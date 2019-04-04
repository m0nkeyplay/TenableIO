# TenableIO
Tenable.io has a lot of things that can be done with the API.  https://cloud.tenable.com/api#/overview  

It also has a lot of things that can only be done in the API.  Here's my contribution to what I have been able to do with it that helps us out. 

Use at will.  Make better at will.  There are variables that need to be set in each file.  Make sure to check that out, otherwise errors abound!

Files ending in 26 are written for Python 2.6 Files ending in 3 are written for Python 3  I will get around to moving them all to 3 sooner but right now this is where we are at.

## Scripts and what they do

**Scan Owners:**
There is a nasty bug in IO where if a user is deleted, all of their scans go poof!  While this is being worked on getting a list of who owns a scan can help move things around since the GUI doesn't provide an easy way to batch see this.

> owners3.py

*usage* `python3 owners3.py`

----

**Searching and Exporting Scan Results - with options and in python3:**
Search for one or a list of plugins/hostnames in a scan or multiple scans and then download them.  This one came about because people needed specific plugin/hostname info on a large scale, quickly.  More query options will be coming soon.  While ioExportQueue26.py is good to queue up for a nighltly download (and will be replaced by a python3 soon)- this is geared more to a fire drill.

> ioSearchScansQueue3.py

*usage* `python3 ioSearchScansQueue3 -scan ScanNametoSearch -o nessus|csv -q plugin|hostname -d PLUGINID|HOSTNAME | -f /path/to/file`

******switchs:******    

               -scan       Search this specific scan 
               -o          Output Type options:  nessus, csv
               -q          Query Type options:  plugin, hostname
               -d or -f    -d for one...   example: -q plugin -d 19506
                           -f for file...  -f /path/to/file              

******notes:******      fill in the following variables as needed per environment

               pickUp_file     <-- Where the export data goes to be picked up
               ak              <-- Access Key
               sk              <-- Secret Key
               proxies         <-- If you use a proxy, set it here.
               report_data     <-- Build the request for the report


> ioExportDownload3.py

**Download the search results**  *usage* `python3 ioExportDownload3.py`

----

**Just Exporting Scan Results:**
To download a nessus or csv file of results from a scan. Gets Critical, High Medium and Scan Information This can be changed by modifying the report_data variable.  This is good for a batch job to get data where the search script is good for ~~firedrill~~ pinpointing data.
> ioExportQueue26.py

> ioExportDownload26.py

*usage* `./ioExportQueue26.py --scan 'scan name' --type nessus or csv`

*usage* `./ioExportDownload26.py`

Python3:

> ioExportScanQueue3.py

> ioExportDownload3.py

*usage* `python ioExportScanQueue3.py --scan 'scan name' --type nessus or csv`

*usage* `python3 ioExportDownload3.py`

----

**Scan History:**
This script will provide Scan Name, Completion Status, Start Time, End Time for requested scans for requested time frame back.
Data is shown on screen and in a tidy CSV file.

> scanHistory26.py

*usage* `./scanHistory26.py --scan ScanNametoSearch (encompass spaces in search in quotes) --days NumberOfDaysBackToGo`

-----
**Stop long scans:**
This script is good to run as a task.  If scans can't run into business hours and you don't want to get up and look to see if they are running - add this as a cron job and it will check for you, stop as needed and log that it did it. 

> check-stopScans3.py

*usage* `python3 check-stopScans3.py --scan "Scan Name" (encompass spaces in search in quotes)`
