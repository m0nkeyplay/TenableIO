#!usr/bin/python3
#
# 	author:  	author:  	https://github.com/m0nkeyplay
# 	file Date: 	2019-03-20 
#
# 	purpose: 	Get a list of the scans, scan types, and who is their owner
#               We had to use this when we needed to change the owners of all our scans
#
#
#   usage:      python3 owners3.py
#
#   notes:      fill in the following variables as needed per environment
#               log_file        <-- Where do you want the CSV to go?
#               ak              <-- Access Key
#               sk              <-- Secret Key 
#               proxies         <-- If you use a proxy, set it here.
#

import requests
import json
import os
import sys


# 	Need an app and secret key for the API to work
#   This is getting the key from a file
#   Not neccessary - store your keys as you like
def get_key(keyfile):
  with open(keyfile,'r') as kf:
    line = kf.readline().strip()
    kf.close()
    return line

  
#   Variables - change as needed
cwd = os.getcwd()
log_file = open(cwd+'/results/Owners.csv', 'w')
ak = get_key('includes/ak')
sk = get_key('includes/sk')
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
      s_name = d["name"].strip()
      s_id = str(d["id"])
      s_type = str(d["type"])
      s_owner = d["owner"] 
      print(s_name+' '+s_type+','+s_owner)
      log_file.write(s_name+','+s_type+','+s_owner+'\n')

#   Get to work
log_file.write('Scan Name, Scan Type, Owner\n')
parse_json(check_url)
log_file.close()

