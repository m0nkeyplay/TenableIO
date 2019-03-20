# TenableIO
No reason for different repos for all the IO scripts.  Moving them all here.

Files ending in 26 are written for Python 2.6
Files ending in 3 are written for Python 3

Scan Owners:
There is a nasty bug in IO where if a user is deleted, all of their scans go poof!  While this is being worked on getting a list of who owns a scan can help move things around since the GUI doesn't provide an easy way to batch see this.
usage python3 owners3.py

Exporting Scan Results:
To download a nessus or csv file of results from a scan.
usage ./ioExportQueue26.py --scan 'scan name' --type nessus or csv
usage ./ioExportDownload26.py

Scan History:
This script will provide Scan Name, Completion Status, Start Time, End Time for requested scans for requested time frame back.
Data is shown on screen and in a tidy CSV file.
usage ./scanHistory26.py --scan ScanNametoSearch (encompass spaces in search in quotes) --days NumberOfDaysBackToGo
