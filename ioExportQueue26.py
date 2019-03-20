#!/usr/bin/python -tt
#
#	  author:		https://github.com/m0nkeyplay
#   license:  use this if it works for you 
#
# 	purpose: 	Queue Up Scan Data for download to import to SC
#     		    This will search one or many scans, depending on the name given for the scan to search
#               Retrieves data from the last completed history scan
#               Gets Critical, High Medium and Scan Information 
#               This can be changed by modifying the report_data variable
#
#	  structure: 	Get the latest history and queue up the nessus file
#				        Write to a file to pick up in a few minutes from IO
#
#   usage:      --scan ScanNameToSearch
#
#   notes:      fill in the following variables as needed per environment
#               log_file        <-- Write down what we did
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
import sys
from datetime import timedelta

args = sys.argv[1:]

#   Check the input data
#   Ways to make a sanity check are appreciated
if len(args) < 4:
  print 'usage --scan ScanNametoSearch (encompass spaces in search in quotes) --type nessus or csv'
  sys.exit(1)

sscan = ''
if args[0] == '--scan':
  sscan = args[1]
  stype = 'nessus'

if args[2] != '--type':
  print 'No --type set.  We will use Nessus.'  
  print 'usage --scan ScanNametoSearch (encompass spaces in search in quotes) --type nessus or csv'
  sys.exit(1)

if args[2] == '--type':
  if args[3] != 'csv' and args[3] != 'nessus':
    print 'Scan output type options are csv and nessus.  Default is nessus.  That is what we will use this time.'
  else:
    stype = args[3]
    print 'Output will be: '+stype

# 	Needed here to get past warning messages when using python 2.6
from requests.packages.urllib3.exceptions import InsecurePlatformWarning
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
from requests.packages.urllib3.exceptions import SNIMissingWarning
requests.packages.urllib3.disable_warnings(SNIMissingWarning)

# 	Need an app and secret key for the API to work
def get_key(keyfile):
  with open(keyfile,'r') as kf:
    line = kf.readline().strip()
    kf.close()
    return line

def file_date(udate):
  cdate = datetime.datetime.fromtimestamp(udate)
  return cdate.strftime('%Y-%m-%d %H:%M:%S')
  
log_time = datetime.datetime.now()
cwd = os.getcwd()
pickUp_file = open(cwd+'', 'w')
log_file = open(cwd+'', 'a')
# Feel free to just put the keys in here
ak = get_key('../.ssh/ak')
sk = get_key('../.ssh/sk')
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
        print 'Scan: '+s_name
        p = requests.post(post_url, proxies=proxies, headers=headers, data=report_data)
        file_data = p.json()
        report_file = str(file_data["file"])
        print 'Run ioExportDownload.py to get the file.'
        print >> pickUp_file, s_name+','+scan_id+','+report_file+','+stype
        print >> log_file, str(log_time)+','+s_name+','+h_id+' queued up'
        break
  else:
    print log_file, str(log_time)+','+s_name+' seems to have an empty history list'

def parse_json(url,scan):
  r = requests.get(url, proxies=proxies, headers=headers)
  data = r.json()
  for d in data["scans"]:
    if scan in d["name"]:
      s_name = d["name"].strip()
      s_id = str(d["id"])
      scan_url = 'https://cloud.tenable.com/scans/'+s_id
      scan_history(scan_url,s_name,s_id)

def main():

  parse_json(check_url,sscan)
  pickUp_file.close()
  log_file.close()
  
if __name__ == '__main__':
  main()
