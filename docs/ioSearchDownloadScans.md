> ioSearchDownloadScans.py

**Search for one or a list of plugins/hostnames/risk factors/compliance checks in a scan or multiple scans and then download them.**  
This one came about because people needed specific plugin/hostname info on a large scale, quickly.  More query options will be coming soon.  While ioExportQueue26.py and ioExportScanQueue3.py are good to queue up for a nighltly download - this is geared more to a fire drill.  When done, download the results with the script below.

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
