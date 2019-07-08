This data was scraped using the code from commit `2f2126f01cd83ca98f93132f9843be24cdcb802c`. All data here is clean except the one that is called `uncleanData_6minPopularStream.csv`. That one is there in order for you to observe how analyze.py cleans data. Running it on `Popular_2day12hour_interval5min` shows how special characters are removed as well, but the special characters are rendered in this file since it was done before special characters were replaced.


Since doing the project, I have changed some things. The data files created would be slightly different when using the latest commit. For one, there is a work around for the uncleanliness/errors from the uncleanData example above. But the ability to clean it is still there. 


The following data files are from commit `2f2126f01cd83ca98f93132f9843be24cdcb802c` any others are from the newest scrapers (infoInterval.py and infoStream.py)


Note: the Interval ones that say 2 days 12 hours are not not really 2 days and 12 hours due to some mistake I found afterwards. The Stream one should be fine.

* askreddit_2day12hour_interval5min.csv
* askreddit_2day12hour_stream.csv
* Popular_2day12hour_interval5min.csv
* popular_short_stream2.csv
* ucsc_2day12hour_interval5min.csv 
* ucsc_2day12hour_stream.csv 
* uncleanData_6minPopularStream.csv



_Disclaimer: all this data was scraped using my scripts in the parent folder. I have not screened any for the contents of the titles or posts._