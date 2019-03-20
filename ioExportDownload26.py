#!/usr/bin/python -tt
#
#	  author:		https://github.com/m0nkeyplay
#   license:  use this if it works for you 
#
# 	purpose: 	Download .nessus or .csv reports for import into SC/reporting tool
#     			
#
#	  structure: 	Open get_files
#				        Write the files to disk (put_files)
#               Run after ioExportQueue26.py

#   usage:      run after exports have been queued up for download
#
#   notes:      fill in the following variables as needed per environment
#               log_file        <-- Write down what we did
#               get_files       <-- What files to pick up
#               put_files       <-- Where to put them
#               ak              <-- Access Key
#               sk              <-- Secret Key 
#               proxies         <-- If you use a proxy, set it here.

import requests
import json
import os
import time
import datetime
import sys
import shutil
import subprocess

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
  return cdate.strftime('%Y%m%d%H%M%S%f')

  
cwd = os.getcwd()
# Feel free to just put the keys in here
ak = get_key('../.ssh/ak')
sk = get_key('../.ssh/sk')
h_key_data = 'accessKey='+ak+'; secretKey='+sk
log_time = datetime.datetime.now()
log_file = open(cwd+'', 'a')
get_files = open(cwd+'', 'r')
put_files = cwd+''
check_url = 'https://cloud.tenable.com/scans'

proxies = {}
proxies['https']= ''

headers = {}
headers['content-type']= 'application/json'
headers['x-apikeys']= h_key_data

# 	Status Check
def status_check(scan,file):
  url = 'https://cloud.tenable.com/scans/'+scan+'/export/'+file+'/status'
  r = requests.get(url, proxies=proxies, headers=headers)
  data = r.json()
  print data["status"]
  if data["status"] == 'loading':
    print 'The file is still being built  Please try again later'
    return 'loading'
  else:
    return 'gtg'

#	Download the files
def download_report(url,report,con):
  local_filename = put_files+report+'.'+con
  r = requests.get(url, proxies=proxies, headers=headers, stream=True)
  with open(local_filename, 'wb') as f:
    shutil.copyfileobj(r.raw, f)
    print >> log_file, str(log_time)+','+local_filename+',created'

def main():
#	prepare and download the files
  for line in get_files:
    line = line.strip()
    params = line.split(",")
    r_name = params[0].replace(' ','-')
    r_name = r_name.lower()
    scan = params[1]
    file = params[2]
    ftype = params[3]
    download = 'https://cloud.tenable.com/scans/'+scan+'/export/'+file+'/download'
    if status_check(scan,file) == 'gtg':
      download_report(download,r_name,ftype)

  get_files.close()
  log_file.close()
  
if __name__ == '__main__':
  main()
