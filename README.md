# hcdata
A python script to pull holding company data from NPW

This is a script to recreate the bulk data files available on chicagofed.org from a primary source, the NIC Public Website (NPW). A list of ID_RSSDs (financial entities) and MDRMs (data items) are retrieved from NPW and the website of the Board of Governers (BOG) respectively. For a given as-of date, requests are created and submitted for static csv files. These files are then combined with structure attribute data from NPW and written to a bulk csv file.
