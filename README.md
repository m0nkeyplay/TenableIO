# TenableIO
Tenable.io has a lot of things that can be done with the API.  https://cloud.tenable.com/api#/overview  

It also has a lot of things that can only be done in the API.  Here's my contribution to what I have been able to do with it that helps us out.

Use at will.  Make better at will.  There are variables that need to be set in each file.  Make sure to check that out, otherwise errors abound!

## May 28, 2019 - Updates to ioInteractiveScanSearch.py and ioSearchDownloadScans.py

Added plugin Family to search options

Created some canned files for searching located in ioFiles/  These are named by the query type then what they are searching on

Files using python 2.6 are noted as ending in 2.6.  All others tested in 3.5+.

## To do:

Break out keys and specific functions to an include file so we don't need to put the info in each files.

Parse the data from a compliance scan.


### Popular scripts in action

Read Me files located in the docs/ directory

> ioInteractiveScanSearch.py

[![asciicast](https://asciinema.org/a/242579.svg)](https://asciinema.org/a/242579)

> ioSearchDownloadScans.py

[![asciicast](https://asciinema.org/a/242426.svg)](https://asciinema.org/a/242426)
