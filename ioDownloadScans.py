#!usr/bin/env python3

#	author:		https://github.com/m0nkeyplay
#   license:    use this if it works for you
#   file Date:  2019-04-23
#
# 	purpose:
#     		    This will download one or many scans, depending on the name given for the scan to search
#               Retrieves data from the last completed history scan
#               Gets Critical, High Medium and Scan Information
#               This can be changed by modifying the report_data variable
#
#	  structure: 	Get the latest history and queue up the nessus file
#				        Write to a file to pick up in a few minutes from IO
#
#   usage:      -scan ScanNameToSearch -type nessus | csv
#
#   notes:      fill in the following variables as needed per environment
#               put_files       <-- Where do you want the exports to download
#                                   default is inside the downloads folder attached to this repo
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
import shutil
from sys import argv
from datetime import timedelta

hello = '##########################################################################\n'
hello +='#                                                                        #\n'
hello +='#                            Tenable IO Scan Dowloads                    #\n'
hello +='#                            Download High, Med, Low                     #\n'
hello +='#                                 & 19506                                #\n'
hello +='#                                                 *this may take a while #\n'
hello +='##########################################################################\n'

scanError = 'Error:  Scan did not run.\n'
usage = 'usage python ioDownloadScans.py -scan ScanNametoSearch (encompass spaces in search in quotes) -type nessus | csv\n'
intermission ='Requests sent.\nNo errors received.\nExport of results is queued up.\nInitiating download...'

args = argv[1:]

#   Check the input data
#   Ways to make a sanity check are appreciated
if len(args) < 4:
  print
  sys.exit(1)

sscan = ''
if args[0] == '-scan':
  sscan = args[1]
  stype = 'nessus'

if args[2] != '-type':
  print(scanError+usage)
  sys.exit(1)

if args[2] == '--type':
  if args[3] != 'csv' and args[3] != 'nessus':
    print('Scan output type options are csv and nessus.\n'+usage)
    exit()
  else:
    stype = args[3]
    print('Output will be: '+stype)


# 	Need an app and secret key for the API to work
#   Read the key from a file
#   Happy to have suggestions on better ways to do this
def get_key(keyfile):
  with open(keyfile,'r') as kf:
    line = kf.readline().strip()
    kf.close()
    return line

def file_date(udate):
  cdate = datetime.datetime.fromtimestamp(udate)
  return cdate.strftime('%Y-%m-%d %H:%M:%S')

log_time = datetime.datetime.now()
timecode = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
cwd = os.getcwd()
workingFile = timecode+'.txt'
pickUp_file = open(cwd+'/'+workingFile, 'w')

######    Uncomment and complete or leave as is
#put_files = cwd+'/downloads/' # Change or keep
#ak = get_key('') # Fill me in
#sk = get_key('') # Fill me in
h_key_data = 'accessKey='+ak+'; secretKey='+sk
check_url = 'https://cloud.tenable.com/scans'

proxies = {}
proxies['https']= ''

headers = {}
headers['content-type']= 'application/json'
headers['x-apikeys']= h_key_data

#	report filter info so we don't get huuuuuge files, but we do get things that need attention
# 	This joke will only be funny in 2018
#   Add/remove filters as needed
report_data = '{'
report_data += '"filter.0.filter":"plugin.id","filter.0.quality":"eq","filter.0.value":"19506"'
report_data += ',"filter.1.filter":"severity","filter.1.quality":"eq","filter.1.value":"Critical"'
report_data += ',"filter.2.filter":"severity","filter.2.quality":"eq","filter.2.value":"High"'
report_data += ',"filter.3.filter":"severity","filter.3.quality":"eq","filter.3.value":"Medium"'
report_data += ',"filter.search_type":"or","format":"'+stype+'"}'

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
        file_data = p.json()
        report_file = str(file_data["file"])
        pickUp_file.write(s_name+','+scan_id+','+report_file+','+stype)
        break
  else:
    print(scanError+usage)
    exit()

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
  data = r.json()
  for d in data["scans"]:
    if scan in d["name"]:
      s_name = d["name"].strip()
      s_id = str(d["id"])
      scan_url = 'https://cloud.tenable.com/scans/'+s_id
      scan_history(scan_url,s_name,s_id)



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
