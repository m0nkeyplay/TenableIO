# 	author:  	https://github.com/m0nkeyplay/
# 	file Date: 	2019-03-27
#
# 	purpose: 	Check scan status and stop them if needed
#				Set up a cron job to check and stop 
#               https://cloud.tenable.com/api#/resources/scans/stop
# 
#   usage:      python3 check-stopScans3.py --scan "Scan Name"   
#               *enclose scan name in quotes if name has spaces
#
#   variables:
#               ak              <-- Access Key
#               sk              <-- Secret Key 
#               proxies         <-- If you use a proxy, set it here
#               log_file        <-- Set the log file here
#				

import requests
import json
import os
import time
import datetime
import sys
from sys import argv

hello = '##########################################################################\n'
hello +='#2019                                                                    #\n'
hello +='#                     Tenable IO Scan Check/Stop                         #\n'
hello +='#                                                                        #\n'
hello +='#                                                                     ~es#\n'
hello +='##########################################################################\n'

usage = '****Scan did not run.****\n\nusage% python3 check-stopScans3.py --scan "Scan Name"\n'
usage += '*enclose scan name in quotes if name has spaces'

args = argv[1:]
if len(args) != 2:
  print('We are missing some things here.')
  print(usage)
  exit()

scanToStop = ''
if args[0] == '--scan':
  scanToStop = args[1].strip()

# 	Get the key if it's not in this file.  It shouldn't be in this file, but hey - that's up to you.
def get_key(keyfile):
  with open(keyfile,'r') as kf:
    line = kf.readline().strip()
    kf.close()
    return line
	
def clean_date(udate):
  cdate = datetime.datetime.fromtimestamp(udate)
  return cdate.strftime('%Y-%m-%d %H:%M:%S')

def file_date(udate):
  cdate = datetime.datetime.fromtimestamp(udate)
  return cdate.strftime('%Y-%m-%d %H:%M:%S')
  
cwd = os.getcwd()
log_file = open(cwd+'/', 'a')


ak = get_key('')    # path to file in function or replace with key
sk = get_key('')    # path to file in function or replace with key
h_key_data = 'accessKey='+ak+'; secretKey='+sk
check_url = 'https://cloud.tenable.com/scans'

proxies = {}
proxies['https']= ''

headers = {}
headers['content-type']= 'application/json'
headers['x-apikeys']= h_key_data

def parse_json(url):
  r = requests.get(url, proxies=proxies, headers=headers)
  data = r.json()
    
  for d in data["scans"]:
    if scanToStop in d["name"] and d["status"] == "running":
      s_name = d["name"]
      s_status = d["status"]
      s_id = str(d["id"])
      stop_url = 'https://cloud.tenable.com/scans/'+s_id+'/stop'	  
      requests.post(stop_url, proxies=proxies, headers=headers)     
      log_file.write(file_date(time.time())+' '+s_name+' was still running and needed to be stopped.')

# Do the work
print(hello)
parse_json(check_url)
log_file.close()

