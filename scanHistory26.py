#!/usr/bin/python -tt

# 	author:  	https://github.com/m0nkeyplay
#
# 	purpose: 	Get scan status, start and end time from Tenable.IO
#               Write data to output and a file

import requests
import json
import os
import time
import datetime
import sys
from datetime import timedelta

args = sys.argv[1:]

if len(args) < 4:
  print 'usage ./scanHistory26.py --scan ScanNametoSearch (encompass spaces in search in quotes) --days NumberOfDaysBackToGo'
  sys.exit(1)

sscan = ''
if args[0] == '--scan':
  sscan = args[1]
  sdays = '30'

if args[2] != '--days':
  print 'No --days set.  We will use 30.'  
  print 'usage ./scanHistory26.py --scan ScanNametoSearch (encompass spaces in search in quotes) --days NumberOfDaysBackToGo'

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
  
def file_date_name(udate):
  cdate = datetime.datetime.fromtimestamp(udate)
  return cdate.strftime('%Y%m%d%H%M%S')

cwd = os.getcwd()
log_name = sscan+'-'+file_date_name(time.time())+'.csv'
log_file = open(cwd+'/'+log_name, 'w')
ak = get_key('../.ssh/ak') # use the get key_function or complete it here
sk = get_key('../.ssh/sk') # use the get key_function or complete it here
h_key_data = 'accessKey='+ak+'; secretKey='+sk
check_url = 'https://cloud.tenable.com/scans'

proxies = {}
proxies['https']= ''

headers = {}
headers['content-type']= 'application/json'
headers['x-apikeys']= h_key_data

# See if the scan exists
def check_scan(url,scan):
  rv = ''
  r = requests.get(url, proxies=proxies, headers=headers)
  data = r.json()
  for d in data["scans"]:
    if scan.lower() in d["name"].lower():
      print 'We found it.  We will move along now.'
      print 'Scan Name, Completion Status, Start Time, End Time'
      print >> log_file, 'Scan Name, Completion Status, Start Time, End Time'
      rv = 'gtg'
      return rv
      break

#	Get history and show scans in that period
def scan_history(url,s_name):
  r = requests.get(url, proxies=proxies, headers=headers)
  data = r.json()
  for i, d in enumerate(data["history"]):
    s_start = file_date(d["creation_date"])
    s_end = file_date(d["last_modification_date"])
    s_status = d["status"]
    if datetime.datetime.fromtimestamp(d["creation_date"]) >= datetime.datetime.fromtimestamp(time.time()) - timedelta(days=int(sdays)):
      print s_name+','+s_status+','+s_start+','+s_end
      print >> log_file,s_name+','+s_status+','+s_start+','+s_end
      

#	Get the Scan IDs of the scan
def parse_json(url):
  r = requests.get(url, proxies=proxies, headers=headers)
  data = r.json()
  for d in data["scans"]:
    if sscan.lower() in d["name"].lower():
      s_name = d["name"].strip()
      s_id = str(d["id"])
      s_url = 'https://cloud.tenable.com/scans/'+s_id
      scan_history(s_url,s_name)

def main():
  print 'Searching for '+sscan+' within the past '+sdays+'.  Let\'s see what we find.'
  if check_scan(check_url,sscan) == 'gtg':
    parse_json(check_url)
    log_file.close()
    print ''
    print 'Complete.  Data written to '+cwd+'/'+log_name
  else:
    log_file.close()
    print 'Complete.  No scans with that name found.'
    print 'May want do delete '+cwd+'/'+log_name+ ' since it\'s empty.'
  
if __name__ == '__main__':
  main()
