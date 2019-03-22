# 	author:  	https://github.com/m0nkeyplay/
# 	file Date: 	2019-03-21
#
# 	purpose: 	Queue Up Scan Data for download based on plugin ids from the lastest scan based on name and plugin id
#
#	structure: 	Get the latest history and queue up the nessus file
#				Write to a file to pick up in a few minutes from IO
#
#   usage:      python3 ioExportSearchQueue3.py --scan ScanNametoSearch (encompass spaces in search in quotes) --type nessus|csv --p PLUGINID | --f /path/to/file
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
def get_key(keyfile):
  with open(keyfile,'r') as kf:
    line = kf.readline().strip()
    kf.close()
    return line

# I don't think we need this - but every time I remove it I find out I needed it
def file_date(udate):
  cdate = datetime.datetime.fromtimestamp(udate)
  return cdate.strftime('%Y-%m-%d %H:%M:%S')

# Repeatable

hello = '##########################################################################\n'
hello +='#                                                                        #\n'
hello +='#                     Tenable IO Plugin Export - Queue Stage             #\n'
hello +='#                     When this is done run ioExportDownload3.py         #\n'
hello +='#                                                                        #\n'
hello +='##########################################################################\n'

goodbye ='No errors. In a few run ioExportDownload3.py and you should get the data you need.'

usage = '****Scan did not run.****\n\nusage% python3 ioExportSearchQueue3.py --scan ScanNametoSearch (encompass spaces in search in quotes) --type nessus|csv --p PLUGINID | --f /path/to/file\n                    ** for some silly reason the quotes must be double quotes if running on Windows'

# We are creating the search string with the function if we are getting the data from a file
def create_search(file):
    x = 0
    searchFor = ''
    pluginFile = open(sFile,'r')
    for plugin in pluginFile:
        line = plugin.strip()
        searchFor += '"filter.'+str(x)+'.filter":"plugin.id","filter.'+str(x)+'.quality":"eq","filter.'+str(x)+'.value":"'+line+'",'
        x += 1
    return searchFor
    pluginFile.close()


#   Check the input data
#   Needs a good sanity check
args = argv[1:]
if len(args) < 6:
  print('We are missing some things here.')
  print(usage)
  exit(1)

#   Working out the data we are going to get
sscan = ''
if args[0] == '--scan':
  sscan = args[1].strip()


if args[2] != '--type':
  print('Type is needed.')
  print(usage)
  exit()

if args[2] == '--type':
  if args[3] != 'csv' and args[3] != 'nessus':
    print('Scan output type options are csv and nessus.')
    print(usage)
    exit()
  else:
    stype = args[3].strip()

# Search for one plugin or a file full
searchT = ''
if args[4] == '--p':
    searchT = '"filter.0.filter":"plugin.id","filter.0.quality":"eq","filter.0.value":"'+args[5].strip()+'",'
elif args[4] == '--f':
    sFile = args[5]
    searchT = create_search(sFile)
else:
    print('We need a plugin or a file of plugins to search for.')
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
proxies['https']= ''

headers = {}
headers['content-type']= 'application/json'
headers['x-apikeys']= h_key_data

#	report filter info so we don't get huuuuuge files
# 	This joke will only be funny in 2018
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

print(hello)
print('We will be looking for "'+sscan+ '" scans.')
print('Output will be: '+stype)
parse_json(check_url,sscan)
pickUp_file.close()
print(goodbye)
