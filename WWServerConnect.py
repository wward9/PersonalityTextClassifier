#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 20:19:48 2017

@author: william
"""

import pandas as pd
import pyodbc
#pyodbc.drivers()


#Create Database connection
server = 'wwcloudserver.database.windows.net'
database = 'WWCloudDatabase'
username = 'WWAdmin'
password = 'WWDBAdmin_3636'
driver= '{ODBC Driver 13 for SQL Server}'
cnxn = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

#Pull all object names
for row in cursor.tables():
    print (row.table_name)

#Run SQL commands here
SQLCommand = """Select *
From ***');"""

#Read SQL command into pandas dataframe
Test = pd.read_sql(sql=SQLCommand, con=cnxn)       

#Close connection
cnxn.close()