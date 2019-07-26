# TenableIO
Tenable.io has a lot of things that can be done with the API.  https://cloud.tenable.com/api#/overview  It also has a lot of things that can only be done in the API.

These scripts deal with getting data from scans.  We can search and download results from the scans interactively or set up with all the data in switches (for a cron job maybe?)

Use at will.  Make better at will.  There are variables that need to be set in each file.  Make sure to check that out, otherwise errors abound!

> scanNames.py
**This script will pull the scan names you need to run the rest of the scripts.**

*usage* `python scanNames.py 'word in scan name'` for a search  `python scanNames.py` for a full list of scan names

> ioSearchDownloadScans.py

**Search for one or a list of plugins/hostnames/risk factors/compliance checks in a scan or multiple scans and then download them.**  
This one came about because people needed specific plugin/hostname info on a large scale, quickly.  This is geared toward a regular download of scan data.

Query filters are listed below. Add as needed in a dictionary in the script.


1. pluginid
2. pluginname
3. hostname
4. riskfactor
5. compliancecheck  
6. pluginfamily

*usage* `python3 ioSearchDownloadScans.py -scan ScanNametoSearch -o nessus|csv -q filterQuery -d datapoint | -f /path/to/file`

******switchs:******    

               -scan       Search this specific scan
               -o          Output Type options:  nessus, csv
               -q          Query Type options:  pluginid, pluginname, hostname, riskfactor, compliancecheck, pluginfamily
               -d or -f    -d for one...   example: -q pluginid -d 19506
                                           example: -q pluginid -f /path/to/file/with/a/list/of/pluginids              

******notes:******      fill in the following variables as needed per environment

               pickup_file     <-- Where the export data goes to be picked up
               ak              <-- Access Key
               sk              <-- Secret Key
               proxies         <-- If you use a proxy, set it here.


[![asciicast](https://asciinema.org/a/242426.svg)](https://asciinema.org/a/242426)

> ioInteractiveScanSearch.py

Think ioSearchDownloadScans.py but interactive.

Run the scan search, answer some questions and download in one interactive script.  Think when the boss comes and asks how many Macs are running the Critcal version of Chrome?  (pluginid 103649	Google Chrome < 61.0.3163.110 Multiple Vulnerabilities (macOS))


*usage* `python3 ioInteractiveScanSearch.py`

   notes:      fill in the following variables as needed per environment before you get started

               put_Files       <-- Where do you want the exports to downloads
                                   Default is the downloads folder associated with the repo
               ak              <-- Access Key
               sk              <-- Secret Key
               proxies         <-- If you use a proxy, set it here.

[![asciicast](https://asciinema.org/a/242579.svg)](https://asciinema.org/a/242579)

#### Updates

July 2019:

+ added scanNames.py

+ cleaned up errors reporting in scripts

June 2019:

+ Cleaned out unused scripts and documents

+ Added riskfactor file to ioFiles

May 2019:

+ Added plugin Family to search options

+ Created some canned files for searching located in ioFiles/  These are named by the query type then what they are searching on

#### To do:

+ Break out keys and specific functions to an include file so we don't need to put the info in each files.

+ Parse the data from a compliance scan.

+ Create a report based on workbenches
