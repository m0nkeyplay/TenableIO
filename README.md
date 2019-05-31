# TenableIO
Tenable.io has a lot of things that can be done with the API.  https://cloud.tenable.com/api#/overview  It also has a lot of things that can only be done in the API. 

Here we have a collection of scripts to take care of things I need to deal with on a regular basis:  getting data from scans, checking on scan status and finding out who is owning the scans.

There are three ways to search and download scan data:  ``ioDownloadScans.py`` will get you anything that is not info in your scan choice while ``ioSearchDownloadScans.py`` and ``ioInteractiveScanSearch.py`` allow for more granular search parameters in a format you like, switch based for cron based jobs or interactive for need it now fire drills.

Some people don't like to check things that can be automated.  This is why I wrote ``check-stopScans3.py``.  I was tired or forgetting to see if out scans stopped by 7am.  This does it or me, stops them and logs if anything needed to be stopped.

Do you have questions about what's going on with a scan?  With ``owners3.py`` we can see who is the owner of a scan and bug them to find out what it's doing.


Use at will.  Make better at will.  There are variables that need to be set in each file.  Make sure to check that out, otherwise errors abound!

#### May 28, 2019 - Updates to ioInteractiveScanSearch.py and ioSearchDownloadScans.py

Added plugin Family to search options

Created some canned files for searching located in ioFiles/  These are named by the query type then what they are searching on

Files using python 2.6 are noted as ending in 2.6.  All others tested in 3.5+.

#### To do:

Break out keys and specific functions to an include file so we don't need to put the info in each files.

Parse the data from a compliance scan.

Create a report based on workbenches


### Popular scripts in action

Read Me files located in the docs/ directory

> ioInteractiveScanSearch.py

[![asciicast](https://asciinema.org/a/242579.svg)](https://asciinema.org/a/242579)

> ioSearchDownloadScans.py

[![asciicast](https://asciinema.org/a/242426.svg)](https://asciinema.org/a/242426)
