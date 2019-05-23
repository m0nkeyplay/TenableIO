#!usr/bin/env python3
#
#
# 	author:  	https://github.com/m0nkeyplay/
# 	file Date: 	2019-04-21
#
#   notes:      fill in the following variables as needed per environment
#
#               put_files       <-- Where do you want the exports to downloads
#                                   Default is the downloads folder associated with the repo
#               ak              <-- Access Key
#               sk              <-- Secret Key
#               proxies         <-- If you use a proxy, set it here.
#
#   updates:    +random file for queuing added so things can be done more than one time
#               also added the timecode to the results so they don't overwrite when using this more often and files 
#               stil in downloads folder
#               +lowered the case for hostnames, since IO lowers them and search seems to be case sensitive

import requests
import json
import os
import time
import datetime
import shutil
from sys import argv
from datetime import timedelta

#   Chatter

hello = '##########################################################################\n'
hello +='#                                                                        #\n'
hello +='#                     Tenable IO Interactive Scan Search                 #\n'
hello +='#                     1. Answer some questions                           #\n'
hello +='#                     2. Get a report                                    #\n'
hello +='#                                                                        #\n'
hello +='##########################################################################\n'

holdOnCowboy = '++++ It looks like the environment isn\'t set up yet.'
holdOnCowboy +='\nPlease set up the environmental variables first. (put_files, ak, and sk)\n'
holdOnCowboy +='Once those are set you should be on your way.'

intermission ='Requests sent.\nNo errors received.\nExport of results is queued up.\nInitiating download...'

queryExtra = 'You can make it happen by updating the script, or choose from one of of our predefined query options.'

status_error_message =  'We received an error while checking the export status.\n'
status_error_message += 'This is different than IO still building your request.\n'
status_error_message += 'Check the error message below at the API website.\n'
status_error_message += 'https://cloud.tenable.com/api#/resources/scans/export-status'

#   Dictionary of API filters to search on
#   Structure - [what are we getting from the user] (tenable calls it,how to search it)
#   Add your own:  https://cloud.tenable.com/api#/resources/scans/export-request

apiFilter = {}
apiFilter['pluginid'] = ('plugin.id','eq')
apiFilter['pluginname'] = ('plugin.name','match')
apiFilter['hostname'] = ('host.hostname','match')
apiFilter['riskfactor'] = ('plugin.attributes.risk_factor','eq')
apiFilter['compliancecheck'] = ('compliance_description','match')

#   This grabs the key from a file and puts it below
#   Not perfect but better than putting it in the file itself
def get_key(keyfile):
  with open(keyfile,'r') as kf:
    line = kf.readline().strip()
    kf.close()
    return line

# used to write unique files
def file_date(udate):
    cdate = datetime.datetime.fromtimestamp(udate)
    return cdate.strftime('%Y-%m-%d %H:%M:%S')

# Important Variables
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

##### Functions

# Search String
def create_search(file,q):
    x = 0
    searchFor = ''
    queryFile = open(sFile,'r')
    for line in queryFile:
        lineStripped = line.strip()
        if query in apiFilter.keys():
            if query == 'hostname':
                lineStripped = lineStripped.lower()
            searchFor += '"filter.'+str(x)+'.filter":"'+apiFilter[query][0]+'","filter.'
            searchFor += str(x)+'.quality":"'+apiFilter[query][1]+'","filter.'
            searchFor += str(x)+'.value":"'+lineStripped+'",'
        else:
            print('We are currently not searching on '+query+'. '+queryExtra)
            exit()
        x += 1
    queryFile.close()
    return searchFor

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
            pickUp_file.write(s_name+','+scan_id+','+report_file+','+outputType+'\n')
            break
        else:
            print('The request to IO failed and reported the following error:')
            print(p.status_code)
            break
  else:
    print('There was no history to get data from.')

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

#   Wrapper for queuing up the data
def parse_json(url,scan):
  r = requests.get(url, proxies=proxies, headers=headers)
  if r.status_code != 200:
    print('Error - IO Error Code Below:')
    print(str(r.status_code))
    exit()
  data = r.json()
  for d in data["scans"]:
    if scan in d["name"]:
      s_name = d["name"].strip()
      s_id = str(d["id"])
      scan_url = 'https://cloud.tenable.com/scans/'+s_id
      scan_history(scan_url,s_name,s_id)

#     Menus for Interactive
def outputMenu():
    print('Output Type Options:')
    print(' csv')
    print(' nessus')


def filterMenu():
    print('Filter Type Options:')
    for k, v in apiFilter.items():
        print('  '+k)

def queryMenu():
    print('Query Type:')
    print('  datapoint')
    print('  file')

# Interactive Conversation to move things along
print(hello)

sscan = input('Scan to search: ')
sscan = sscan.strip()

oType = True
while oType:
    outputMenu()
    choice = input('Please choose an output type: ')
    if choice == 'csv' or choice == 'nessus':
        outputType = choice
        break
    else:
        print('---Options are csv or nessus---')

filterType = True
while filterType:
    filterMenu()
    choice = input('Please choose a filter type: ')
    if choice in apiFilter.keys():
        query = choice
        break
    else:
        print('--Filter not supported.\nWe are currently not searching on '+choice+'. '+queryExtra)

qType = True
while qType:
    queryMenu()
    choice = input('Please choose a data query type: ')
    if choice == 'datapoint' or choice == 'file':
        oneOrMany = choice
        break
    else:
        print('--Options are datapoint or file--')

dts = oneOrMany
# data to search
searchT = ''
if dts == 'datapoint':
    criteria = input('Great. What is your datapoint: ')
    if query in apiFilter.keys():
        if query == 'hostname':
            criteria = criteria.lower()
        searchT = '"filter.0.filter":"'+apiFilter[query][0]+'","filter.0.quality":"'
        searchT += apiFilter[query][1]+'","filter.0.value":"'+criteria.strip()+'",'
elif dts == 'file':
    criteria = input('Great. /path/to/file: ')
    sFile = criteria.strip()
    searchT = create_search(sFile,query)
else:
    print('We mucked up - Dying before doing harm')
    exit()

#	report filter info
report_data = '{'
report_data += searchT      # searchT is created up above
report_data += '"filter.search_type":"or","format":"'+outputType+'"}'

print('Internet aliens have been dispatched to search "'+sscan+ '" scans for your data.')
print('Output will be: '+outputType+'\nPlease be patient while they queue up any results...')
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
