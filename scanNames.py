# 	author:  	https://github.com/m0nkeyplay/
# 	file Date: 	2019-07-24
#
# 	purpose: 	get Scan names 
#
#   notes:      fill in the following variables as needed per environment
#               ak              <-- Access Key
#               sk              <-- Secret Key 
#               proxies         <-- If you use a proxy, set it here.
#
#   usage:  python3 scanNames.py   or python3 scanNames.py "scan Name" to search for only scans with something in their name

import requests
import json
import os
import sys

args = sys.argv[1:]
scanCheck = ''

# 	Need an app and secret key for the API to work
def get_key(keyfile):
  with open(keyfile,'r') as kf:
    line = kf.readline().strip()
    kf.close()
    return line

cwd = os.getcwd()
#   Uncomment and then...
#   Place a file in a folder and link to it for each of you keys
#   Or rip out the function part and just put the key in here 
#   Your call
#ak = get_key('')
#sk = get_key('')

# Environment check
try:
    ak
    sk
except:
    print("Please input your access and secret keys")
    exit()

h_key_data = 'accessKey='+ak+'; secretKey='+sk
check_url = 'https://cloud.tenable.com/scans'
proxies = {}
proxies['https']= ''
proxies['http']= ''

headers = {}
headers['content-type']= 'application/json'
headers['x-apikeys']= h_key_data

#   Check to see if we are searching for a scan or just dumping the data
if args:
  if args[0]:
    print('Looking for: '+args[0])
    scanCheck = args[0]
else:
  print('Gathering all the scans')
           
def get_scans(url):
  r = requests.get(url, proxies=proxies, headers=headers)
  data = r.json()
  for d in data["scans"]:
      if scanCheck:
          if scanCheck in d["name"]:
              print(d["name"])
      else:
        print(d["name"])

get_scans(check_url)

