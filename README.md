# TenableIO
No reason for different repos for all the IO scripts.  Moving them all here.

Files ending in 26 are written for Python 2.6 Files ending in 3 are written for Python 3  I will get around to moving them all to 3 sooner but right now this is where we are at.

**Scan Owners:**
There is a nasty bug in IO where if a user is deleted, all of their scans go poof!  While this is being worked on getting a list of who owns a scan can help move things around since the GUI doesn't provide an easy way to batch see this.

*usage* `python3 owners3.py`

**Exporting Scan Results:**
To download a nessus or csv file of results from a scan. Gets Critical, High Medium and Scan Information This can be changed by modifying the report_data variable

*usage* `./ioExportQueue26.py --scan 'scan name' --type nessus or csv`

*usage* `./ioExportDownload26.py`

**Searching and Exporting Scan Results - with options and in python3:**
Search for one or a list of plugins in a scan or multiple scans and then download them.  This one came about because people needed specific plugin info on a large scale, quickly.  While ioExportQueue26.py is good to queue up for a nighltly download - this is geared more to a fire drill.

*usage* `python3 ioExportSearchQueue3.py --scan ScanNametoSearch (encompass spaces in search in quotes) --type nessus|csv --p PLUGINID | --f /path/to/file`

Download is the same..  *usage* `python3 ioExportDownload3.py`

**Scan History:**
This script will provide Scan Name, Completion Status, Start Time, End Time for requested scans for requested time frame back.
Data is shown on screen and in a tidy CSV file.

*usage* `./scanHistory26.py --scan ScanNametoSearch (encompass spaces in search in quotes) --days NumberOfDaysBackToGo`
