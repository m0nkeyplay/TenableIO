#!usr/bin/env python3

# 	author:  	https://github.com/m0nkeyplay/
# 	file Date: 	2019-04-04
#
# 	purpose: 	Queue Up Scan Data for download based on plugins or hostnames from the lastest scan based on scan name
#
#	  structure: 	Get the latest history and queue up the nessus file
#				        Write to a file to pick up in a few minutes from IO
#
#   usage:      -scan ScanNametoSearch -o nessus|csv -q plugin|hostname -d PLUGINID|HOSTNAME | -f /path/to/file
#
#   switchs:    -scan       Search this specific scan
#               -o          Output Type options:  nessus, csv
#               -q          Query Type options:  plugin, hostname
#               -d or -f    -d for one...   example: -q plugin -d 19506
#                           -f for file...  -f /path/to/file              
#
#   notes:      fill in the following variables as needed per environment
#
#               pickUp_file     <-- Where the export data goes to be picked up
#               ak              <-- Access Key
#               sk              <-- Secret Key
#               proxies         <-- If you use a proxy, set it here.
#               report_data     <-- Build the request for the report
#                                   https://cloud.tenable.com/api#/resources/scans/export-request
#

import requests
import json
import os
import time
import datetime
from sys import argv
from datetime import timedelta

# 	Need an app and secret key for the API to work
#   This grabs the key from a file and puts it below
#   Not perfect but better than putting it in the file itself
def get_key(keyfile):
  with open(keyfile,'r') as kf:
    line = kf.readline().strip()
    kf.close()
    return line

# I don't think we need this - but every time I remove it I find out I needed it
def file_date(udate):
  cdate = datetime.datetime.fromtimestamp(udate)
  return cdate.strftime('%Y-%m-%d %H:%M:%S')

#   Chatter

hello = '##########################################################################\n'
hello +='#                                                                        #\n'
hello +='#                     Tenable IO Scan Search - Queue Stage               #\n'
hello +='#                     When this is done run ioExportDownload3.py         #\n'
hello +='#                                                                        #\n'
hello +='##########################################################################\n'

goodbye ='No errors received.\nExport of results is queued up.\nIn a few minutes run ioExportDownload3.py and you should get the data you need.'

usage = '****Scan did not run.****\n\nusage% python3 ioSearchScansQueue3.py' 
usage += ' -scan ScanNametoSearch -o nessus|csv -q plugin|hostname -d PLUGINID|HOSTNAME | -f /path/to/file\n'
usage += '\nswitchs:\n-scan       Search this specific scan (encompass spaces in search in quotes) '
usage += ' ** for some silly reason the quotes must be double quotes if running on Windows'
usage += '\n-o          Output Type options:  nessus, csv'
usage += '\n-q          Query Type options:  plugin, hostname'
usage += '\n-d or -f    '
usage += '\n            -d for one...   example: -q plugin -d 19506'
usage += '\n            -f for file...  -f /path/to/file'     

searchError = 'Error: We need either a data point or a file to search through.\n'

#   We are creating the search string with the function if we are getting the data from a file
#   This will be updated as more search fields are added
def create_search(file,q):
    x = 0
    searchFor = ''
    queryFile = open(sFile,'r')
    for line in queryFile:
        lineStripped = line.strip()
        if query == 'plugin':
            searchFor += '"filter.'+str(x)+'.filter":"plugin.id","filter.'+str(x)+'.quality":"eq","filter.'+str(x)+'.value":"'+lineStripped+'",'
        elif query == 'hostname':
            searchFor += '"filter.'+str(x)+'.filter":"host.hostname","filter.'+str(x)+'.quality":"match","filter.'+str(x)+'.value":"'+lineStripped.lower()+'",'
        else:
            print('The search builder went wrong.')
            exit()
        x += 1
    queryFile.close()
    return searchFor
    


#   Check the input data
#   Needs a good sanity check
#   Right now data is required in specific order.  We don't all work that way

args = argv[1:]
if len(args) < 8:
  print('We are missing some things here.')
  print(usage)
  exit(1)

#   Scan Name 
#   Spaces need to be in quotes
#   Double quotes if run on Windows
sscan = ''
if args[0] == '-scan':
  sscan = args[1].strip()
  
#   Output Type
if args[2] != '-o':
  print('Output switch is needed -o')  
  print(usage)
  exit()

if args[2] == '-o':
  if args[3] != 'csv' and args[3] != 'nessus':
    print('Scan output type options are csv and nessus.')
    print(usage)
    exit()
  else:
    stype = args[3].strip()

#   What we are querying.  This will grow    
query = ''
if args[4] == '-q':
    if args[5] != 'plugin' and args[5] != 'hostname':
        print('Query can be plugin or hostname')
        print(usage)
        exit() 
    else:
        query = args[5].strip()

# Data point or File
searchT = ''    
if args[6] == '-d':
    if query == 'plugin':
        searchT = '"filter.0.filter":"plugin.id","filter.0.quality":"eq","filter.0.value":"'+args[7].strip()+'",'
    elif query == 'hostname':
        lowered = args[7].strip().lower()
        searchT = '"filter.0.filter":"host.hostname","filter.0.quality":"match","filter.0.value":"'+lowered+'",'
    else:
        print('Query error for a single data point')
        exit()
elif args[6] == '-f':
    sFile = args[7]
    searchT = create_search(sFile,query)
else:
    print(searchError)
    print(usage)
    exit()

# Some more variables to help this along
cwd = os.getcwd()
#   where you are writing the data to
pickUp_file = open(cwd+'/ioExportPickUp.txt', 'w') # Change or keep
ak = get_key('') # Fill me in
sk = get_key('') # Fill me in
h_key_data = 'accessKey='+ak+'; secretKey='+sk
check_url = 'https://cloud.tenable.com/scans'

proxies = {}
proxies['https']= '' # fill me in if needed

headers = {}
headers['content-type']= 'application/json'
headers['x-apikeys']= h_key_data

#	report filter info 
report_data = '{'
report_data += searchT      # searchT is created up above
report_data += '"filter.search_type":"or","format":"'+stype+'"}'

#   Set up the scans to queue based on the search criteria
def scan_history(url,s_name,scan_id):
  r = requests.get(url, proxies=proxies, headers=headers)
  data = r.json()
  history_list = []
  for d in data["history"]:
    history_list.append(int(d['history_id']))
  if len(history_list) != 0:
    latest_history = max(history_list)
    for h in data["history"]:
      if  h["status"] == 'completed':
        h_id = str(h["history_id"])
        s_start = file_date(h["creation_date"])
        s_end = file_date(h["last_modification_date"])
        s_status = h["status"]
        post_url = url+'/export?history_id='+h_id
        p = requests.post(post_url, proxies=proxies, headers=headers, data=report_data)
        if p.status_code == 200:
            file_data = p.json()
            report_file = str(file_data["file"])
            pickUp_file.write(s_name+','+scan_id+','+report_file+','+stype+'\n')
            break
        else:
            print('Something went wrong with the request to IO for '+post_url)
            print(p.status_code)
            break

  else:
    print('We should put a log here to say why it did not work...')


def parse_json(url,scan):
  r = requests.get(url, proxies=proxies, headers=headers)
  if r.status_code != 200:
    print('Error - if the code below is 401 - there was a login issue.\nCheck your keys.')
    print(r.status_code())
    exit()

  data = r.json()
  for d in data["scans"]:
    if scan in d["name"]:
      s_name = d["name"].strip()
      s_id = str(d["id"])
      scan_url = 'https://cloud.tenable.com/scans/'+s_id
      scan_history(scan_url,s_name,s_id)

      
# All the above for this...

print(hello)
print('Internet aliens have been dispatched to search "'+sscan+ '" scans for your data.\nOutput will be: '+stype+'\nPlease be patient while they queue up any results...')
parse_json(check_url,sscan)
pickUp_file.close()
print(goodbye)
