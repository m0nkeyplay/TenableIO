#!usr/bin/env python3
#
#
# 	author:  	https://github.com/m0nkeyplay/
# 	file Date: 	2019-04-21
#
# 	purpose: 	Queue Up and download scan data from the lastest scan based on scan name
#
#	  structure: 	Get the latest history and queue up the nessus file
#				        Write to a file to pick up in a few minutes from IO
#
#   usage:      -scan ScanNametoSearch -o nessus|csv -q filterQuery -d databpoint | -f /path/to/file
#
#   switchs:    -scan       Search this specific scan
#               -o          Output Type options:  nessus, csv
#               -q          Query Type options:  pluginid, pluginname, hostname, riskfactor, compliancecheck
#               -d or -f    -d for one...   example: -q pluginid -d 19506
#                           -f for file...  -f /path/to/file
#
#   notes:      fill in the following variables as needed per environment
#
#               put_files       <-- Where do you want the exports to download
#                                   default is inside the downloads folder attached to this repo
#               ak              <-- Access Key
#               sk              <-- Secret Key
#               proxies         <-- If you use a proxy, set it here.
#

import requests
import json
import os
import time
import datetime
import shutil
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
hello +='#                              Tenable IO Scan                           #\n'
hello +='#                            Search and Download                         #\n'
hello +='#                                                                        #\n'
hello +='#                                                                        #\n'
hello +='##########################################################################\n'

holdOnCowboy = '++++ It looks like the environment isn\'t set up yet.'
holdOnCowboy +='\nPlease set up the environmental variables first. (put_files, ak, and sk)\n'
holdOnCowboy +='Once those are set you should be on your way.'

intermission ='Requests sent.\nNo errors received.\nExport of results is queued up.\nInitiating download...'

#goodbye ='No errors received.\nExport of results is queued up.\nIn a few minutes run ioExportDownload3.py and you should get the data you need.'

usage = '\n usage% python3 ioSearchDownloadScans.py'
usage += ' -scan ScanNametoSearch -o nessus|csv -q filterQuery -d datapoint | -f /path/to/file\n'
usage += '\nswitchs:\n-scan       Search this specific scan *see below '
usage += '\n-o          Output Type options:  nessus, csv'
usage += '\n-q          Query Type options:  pluginid, pluginname, hostname, riskfactor, compliancecheck'
usage += '\n-d or -f    '
usage += '\n            -d for one...   example: -q pluginid -d 19506'
usage += '\n            -f for file...  example: -q pluginid -f /path/to/file/with/a/list/of/pluginids'
usage+=  '\n            *anything with a space needs to be quoted - double quotes if running on Windows'

searchError = 'Error: We need either a data point or a file to search through.\n'

#   Dictionary of API filters to search on
#   Structure - [what are we getting from the user] (tenable calls it,how to search it)
#   Add your own:  https://cloud.tenable.com/api#/resources/scans/export-request

apiFilter = {}
apiFilter['pluginid'] = ('plugin.id','eq')
apiFilter['pluginname'] = ('plugin.name','match')
apiFilter['hostname'] = ('host.hostname','match')
apiFilter['riskfactor'] = ('plugin.attributes.risk_factor','eq')
apiFilter['compliancecheck'] = ('compliance_description','match')

#   We are creating the search string with the function if we are getting the data from a file
#   Takes the query, matches it to the dictionary item and away we go
def create_search(file,q):
    x = 0
    searchFor = ''
    queryFile = open(sFile,'r')
    for line in queryFile:
        lineStripped = line.strip()
        if query in apiFilter.keys():
            searchFor += '"filter.'+str(x)+'.filter":"'+apiFilter[query][0]+'","filter.'+str(x)+'.quality":"'+apiFilter[query][1]+'","filter.'+str(x)+'.value":"'+lineStripped+'",'
        else:
            print('We are currently not searching on '+query+'.  You can make it happen by updating the script, or choose from one of of our predefined query options.')
            exit()
        x += 1
    queryFile.close()
    return searchFor



#   Check the input data
#   Needs a good sanity check
#   Right now data is required in specific order.  We don't all work that way

args = argv[1:]
if len(args) < 8:
  print('!!!!! We are missing some things here.')
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
  print('!!!!! Output switch is needed -o')
  print(usage)
  exit()

if args[2] == '-o':
  if args[3] != 'csv' and args[3] != 'nessus':
    print('!!!!! Scan output type options are csv and nessus.')
    print(usage)
    exit()
  else:
    stype = args[3].strip()

#   What we are querying.  This will grow
query = ''
if args[4] == '-q':
    if args[5] not in apiFilter.keys():
        print('!!!!! Query not supported.  Please use a supported query.')
        print(usage)
        exit()
    else:
        query = args[5].strip()

# Data point or File
# Remember that dictionary.  We are using it here too.
searchT = ''
if args[6] == '-d':
    if query in apiFilter.keys():
        searchT = '"filter.0.filter":"'+apiFilter[query][0]+'","filter.0.quality":"'+apiFilter[query][1]+'","filter.0.value":"'+args[7].strip()+'",'
    else:
        print('!!!! Query error for a single data point.  We should have caught this earlier.')
        exit()
elif args[6] == '-f':
    sFile = args[7]
    searchT = create_search(sFile,query)
else:
    print(searchError)
    print(usage)
    exit()

# Some more variables to help this along
timecode = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
cwd = os.getcwd()
workingFile = timecode+'.txt'
#   These need to be uncommented and completed before first run
#put_files = cwd+'/downloads/' # Change or keep
#ak = get_key('') # Fill me in
#sk = get_key('') # Fill me in

# Leave this one alone Please
pickUp_file = open(cwd+'/'+workingFile, 'w')

# Environment check
try:
    ak
    sk
    put_files
except:
    print(holdOnCowboy)
    exit()

h_key_data = 'accessKey='+ak+'; secretKey='+sk
check_url = 'https://cloud.tenable.com/scans'

proxies = {}
proxies['https']= ''

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

# 	Status Check
def status_check(scan,file):
  url = 'https://cloud.tenable.com/scans/'+scan+'/export/'+file+'/status'
  r = requests.get(url, proxies=proxies, headers=headers)
  data = r.json()
  if r.status_code == 200:
        if data["status"] == 'loading':
            return 'loading'
        else:
            return 'gtg'
  else:
        print(status_error_message)
        print('Error code: '+str(r.status_code))
        exit()

#	Download the files
def download_report(url,report,con):
  r = requests.get(url, proxies=proxies, headers=headers, stream=True)
  local_filename = put_files+timecode+'-'+report+'.'+con
  with open(local_filename, 'wb') as f:
    shutil.copyfileobj(r.raw, f)
    print('Interweb monkeys are downloading and putting together the pieces of your report.')

def parse_json(url,scan):
  r = requests.get(url, proxies=proxies, headers=headers)
  if r.status_code != 200:
    print('Error - if the code below is 401 - there was a login issue.\nCheck your keys.')
    print(str(r.status_code))
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
print(intermission)
time.sleep(5)
# end queying up the data for export
# begin downloading it

get_files = open(cwd+'/'+workingFile, 'r')

for line in get_files:
    line = line.strip()
    params = line.split(",")
    r_name = params[0].replace(' ','-')
    r_name = r_name.lower()
    scan = params[1]
    file = params[2]
    ftype = params[3]
    download = 'https://cloud.tenable.com/scans/'+scan+'/export/'+file+'/download'
    while True:
         downloadStatus = status_check(scan,file)
         if downloadStatus == 'gtg':
            print('File is ready for download. Calling interweb monkeys to download.\n')
            download_report(download,r_name,ftype)
            break
         else:
            print('The scan is still loading...  We will check again in 10 seconds.\n')
            time.sleep(10)

print('Files are downloaded and pieced together. Pick them up in '+put_files)
# Clean Up
get_files.close()
os.remove(cwd+'/'+workingFile)