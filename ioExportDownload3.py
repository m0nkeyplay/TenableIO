# 	author:  	https://github.com/m0nkeyplay/
# 	file Date: 	2019-03-21
#
# 	purpose: 	Download reports queued up from ioExportSearchQueue3.py
#
#
#	structure: 	Open get_files
#				Write the files to disk (put_files)
#               Run after ioExportSearchQueue3.py

#   usage:      run after exports have been queued up for download
#               python3 ioExportSearchQueue3.py
#
#   notes:      fill in the following variables as needed per environment
#
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


# 	Need an app and secret key for the API to work
def get_key(keyfile):
  with open(keyfile,'r') as kf:
    line = kf.readline().strip()
    kf.close()
    return line


cwd = os.getcwd()
ak = get_key('') # Fill me in
sk = get_key('') # Fill me in
h_key_data = 'accessKey='+ak+'; secretKey='+sk
get_files = open(cwd+'/ioExportPickUp.txt', 'r') # Change or keep
put_files = cwd+'/downloads/' # Change or keep
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
  if data["status"] == 'loading':
    print('The file is still being built  Please try again later.')
    return 'loading'
  else:
    return 'gtg'

#	Download the files
def download_report(url,report,con):
  r = requests.get(url, proxies=proxies, headers=headers, stream=True)
  local_filename = put_files+report+'.'+con
  with open(local_filename, 'wb') as f:
    shutil.copyfileobj(r.raw, f)
    print('Data downloading...')



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

print('Files are downloaded. Pick them up in '+put_files)
get_files.close()
