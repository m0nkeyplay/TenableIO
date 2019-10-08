#!/usr/bin/env python3
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
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-scan", "--scan", required=True, help="Search this specific scan")
ap.add_argument("-o", "--output", required=True, help="Output Type options: csv or nessus")
ap.add_argument("-q", "--queryFor", required=True, help="Query For Options: pluginid, pluginname, hostname, riskfactor, compliancecheck")
ap.add_argument("-d", "--datapoint", required=False, help="Datapoint: example: -q pluginid -d 19506")
ap.add_argument("-f", "--file", required=False, help="get the datapoints from a file -f /path/to/file")
args = vars(ap.parse_args())

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

hello = '''##########################################################################
#                                                                        #
#                              Tenable IO Scan                           #
#                            Search and Download                         #
#                                                                  |     #
#                                                                 /|\~es #
##########################################################################\n'''

holdOnCowboy = '''++++ It looks like the environment isn\'t set up yet.
\nPlease set up the environmental variables first. (put_files, ak, and sk)
Once those are set you should be on your way.'''

intermission ='Requests sent.\nNo errors received.\nExport of results is queued up.\nInitiating download...'

searchError = 'Error: We need either a data point or a file to search through.\n'

status_error_message =  '''We received an error while checking the export status.
This is different than IO still building your request.
Check the error message below at the API website.
https://cloud.tenable.com/api#/resources/scans/export-status'''

#   Variables

outputTypes = ['csv','nessus']

#   Dictionary of API filters to search on
#   Structure - [what are we getting from the user] (tenable calls it,how to search it)
#   Add your own:  https://cloud.tenable.com/api#/resources/scans/export-request

apiFilter = {}
apiFilter['pluginid'] = ('plugin.id','eq')
apiFilter['pluginname'] = ('plugin.name','match')
apiFilter['pluginfamily'] = ('plugin.family','eq')
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
            if query == 'hostname':
                lineStripped = lineStripped.lower()
            searchFor += '"filter.'+str(x)+'.filter":"'+apiFilter[query][0]
            searchFor += '","filter.'+str(x)+'.quality":"'+apiFilter[query][1]
            searchFor += '","filter.'+str(x)+'.value":"'+lineStripped+'",'
        else:
            print('We are currently not searching on '+query+'.  You can make it happen by updating the script, or choose from one of of our predefined query options.')
            exit()
        x += 1
    queryFile.close()
    return searchFor

#   Input Data
sscan = args["scan"].strip()
stype = args["output"].strip()
if stype not in outputTypes:
    print(stype+' is not a supported output type. Please use a supported output type.')
    for x in outputTypes:
      print('     -o '+x)
    exit()

if args["queryFor"] not in apiFilter.keys():
    print('Query not supported.  Please use a supported query.')
    for k in apiFilter:
        print('     -q '+k)
    exit()
else:
    query = args["queryFor"].strip()

# Data point or File
# Remember that dictionary.  We are using it here too.
searchT = ''
try:
  args["datapoint"]
  if query in apiFilter.keys():
      if query == 'hostname':
          lineStripped = args["datapoint"].strip().lower()
      else:
          lineStripped = args["datapoint"].strip()
      searchT = '"filter.0.filter":"'+apiFilter[query][0]+'",'
      searchT += '"filter.0.quality":"'+apiFilter[query][1]+'",'
      searchT += '"filter.0.value":"'+lineStripped+'",'
  else:
      print('!!!! Query error for a single data point.  We should have caught this earlier.')
      exit()
except:
  args["file"]
  if not os.path.isfile(args["file"]):
      print('File is not where we have been told to look.  Exiting.')
      exit() 
  else:
    sFile = args["file"]
    searchT = create_search(sFile,query)    
   
# Some more variables to help this along
timecode = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
cwd = os.getcwd()
workingFile = timecode+'.txt'
#   These need to be uncommented and completed before first run
#put_files = cwd+'/downloads/' # Change or keep
# Fill these in with the path to your files with the keys
# Or just remove the function and put your key in there.  
# Up to you.
#ak = get_key('')
#sk = get_key('')

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