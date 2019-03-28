# TenableIO
Tenable.io has a lot of things that can be done with the API.  https://cloud.tenable.com/api#/overview  

It also has a lot of things that can only be done in the API.  Here's my contribution to what I have been able to do with it that helps us out. 

Use at will.  Make better at will.

Files ending in 26 are written for Python 2.6 Files ending in 3 are written for Python 3  I will get around to moving them all to 3 sooner but right now this is where we are at.

## Scripts and what they do

**Scan Owners:**
There is a nasty bug in IO where if a user is deleted, all of their scans go poof!  While this is being worked on getting a list of who owns a scan can help move things around since the GUI doesn't provide an easy way to batch see this.

> owners3.py

*usage* `python3 owners3.py`

----

**Exporting Scan Results:**
To download a nessus or csv file of results from a scan. Gets Critical, High Medium and Scan Information This can be changed by modifying the report_data variable
> ioExportQueue26.py

> ioExportDownload26.py


*usage* `./ioExportQueue26.py --scan 'scan name' --type nessus or csv`

*usage* `./ioExportDownload26.py`

----

**Searching and Exporting Scan Results - with options and in python3:**
Search for one or a list of plugins in a scan or multiple scans and then download them.  This one came about because people needed specific plugin info on a large scale, quickly.  While ioExportQueue26.py is good to queue up for a nighltly download - this is geared more to a fire drill.

> ioSearchPluginQueue3.py

> ioExportDownload3.py

**Search plugins**  
*usage* `python3 ioSearchPluginQueue3.py --scan ScanNametoSearch (encompass spaces in search in quotes) --type nessus|csv --p PLUGINID | --f /path/to/file`

**Search description field** *(coming soon)*

Download is the same for each  *usage* `python3 ioExportDownload3.py`

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
