from pandas_datareader import data
import datetime
import mysql.connector
from csv import reader
import yfinance as yf
import seaborn as sns 
from scipy.stats import pearsonr 
from pandas import DataFrame
import pandas 
import matplotlib.pyplot as plt 
import numpy as np 
import csv 
import math 

# DATA SOURCE 1: STOCK PRICES FROM YAHOO 

sp500_list=['^GSPC']

def getStockData (stock_list, start=datetime.datetime(2015,1,1), end=datetime.datetime.now()):
    stockData={}
    for stock in stock_list:
        stockData[stock]=data.DataReader(stock, 'yahoo',start, end)
    return stockData 

sp500 = getStockData(sp500_list) #dict 
sp500_df = data.DataReader(sp500_list, 'yahoo',start=datetime.datetime(2015,1,1), 
                                    end=datetime.datetime.now())['Adj Close']

# DATA SOURCE 2: COVID CASES BY COUNTY (CSV FILE) 
connection = mysql.connector.connect(user='root', password='dataadmin',
                              host='localhost')
cursor=connection.cursor(buffered=True)

cursor.execute('CREATE DATABASE IF NOT EXISTS covidstocks;')

connection = mysql.connector.connect(user='root', password='dataadmin',
                              host='localhost', database='covidstocks')
cursor=connection.cursor(buffered=True)

tables = {}

tables['covid_cases'] = (
    "CREATE TABLE `covid_cases` ("
    "  `date` date NOT NULL,"
    "  `county` text NOT NULL,"
    "  `state` text NOT NULL,"
    "  `fips` text DEFAULT NULL,"
    "  `cases` int NOT NULL,"
    "  `deaths` int NOT NULL"
    ") ENGINE=InnoDB")

def create_covid_cases(dictionary):
    cursor.execute(dictionary['covid_cases'])

'''
create the table: 
create_covid_cases(tables)
'''

def read_csv(filename):
    with open(filename) as file: 
        csv_reader= reader(file)
        data= list(csv_reader)
    return data 

csv_data=read_csv('us-counties.csv')

def bulk_insert(data):
    min_index=0
    max_index=1000
    while max_index < len(data):
        insert_covid_cases(data[min_index:max_index])
        min_index += 1001
        max_index += 1001
    insert_covid_cases(data[min_index:]) #insert the remaining few data points 

def insert_covid_cases (data):
    to_add = ("INSERT INTO covid_cases "
               "(date, county, state, fips, cases, deaths) "
               "VALUES (%s, %s, %s, %s, %s, %s)")
    cursor.executemany(to_add, data)
    connection.commit()

'''
insert data into db: 
bulk_insert(csv_data[1:])
''' 

def result(cursor):
    return [list(row) for row in cursor]

# STORING STOCK DATA TO SAME DB 

tables['stock_data'] = (
    "CREATE TABLE `stock_data` ("
    "  `date` date NOT NULL,"
    "  `close` decimal NOT NULL"
    ") ENGINE=InnoDB")

def create_stock_data(dictionary):
    cursor.execute(dictionary['stock_data'])

'''
creating the stock table:
create_stock_data(tables)
'''

def insert_stock_data(data):
    to_add = ("INSERT INTO stock_data "
                "(date, close) "
                "VALUES (%s, %s)")
    cursor.executemany(to_add, data)
    connection.commit()

data=[]
for index, row in sp500_df.iterrows():
    data.append([index.date(), row[-1]])

'''
# inserting the data 
insert_stock_data(data)
''' 

# DATA SOURCE 3: DEMOGRAPHIC DATA BY COUNTY (CSV FILE)

tables['demographics'] = (
    "CREATE TABLE `demographics` ("
    "  `fips` int,"
     " `county` text,"
    "  `state` text,"
    "  `state_code` text,"
    "  `male` int,"
    "  `female` int,"
    "  `median_age` float,"
    "  `population` int,"
    "  `percent_female` float,"
    "  `latitude` float,"
    "  `longitude` float"
    ") ENGINE=InnoDB")

def create_demographics(dictionary):
    cursor.execute(dictionary['demographics'])

'''
create_demographics(tables)
'''

demo_data=read_csv('county_demographics.csv')

def bulk_insert_demog(data):
    min_index=0
    max_index=1000
    while max_index < len(data):
        insert_demographics(data[min_index:max_index])
        min_index += 1001
        max_index += 1001
    insert_demographics(data[min_index:]) #insert the remaining few data points 

def insert_demographics(data):
    to_add = ("INSERT INTO demographics "
            "(fips, county, state, state_code, male, female, median_age, population, "
            "percent_female, latitude, longitude) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    cursor.executemany(to_add, data)
    connection.commit()

'''
insert data into db: 
bulk_insert_demog(demo_data[1:])
''' 

# DATA SOURCE 4: 2016 AND 2012 ELECTION DATA BY COUNTY (CSV FILE)

tables['politics'] = (
    "CREATE TABLE `politics` ("
    "  `fips` int,"
    "  `dem_votes16` int,"
    "  `rep_votes16` int,"
    "  `total_votes16` int,"
    "  `percent_dem16` float,"
    "  `percent_rep16` float,"
    "  `dif_votes16` int,"
    "  `state_abbrev` char(2),"
    "  `county` text,"
    "  `total_votes12` int,"
    "  `dem_votes12` int,"
    "  `rep_votes12` int,"
    "  `percent_dem12` float,"
    "  `percent_rep12` float,"
    "  `dif_votes12` int,"
    "  `percent_hs` int,"
    "  `percent_uni` int"
    ") ENGINE=InnoDB")

def create_politics(dictionary):
    cursor.execute(dictionary['politics'])

'''
create the table:
create_politics(tables)
''' 

politics_data=read_csv('votes.csv')
def create_clean_politics_data():
    clean_politics_data=[]
    for row in politics_data: # selecting only the columns from the csv that we want 
        clean_politics_data.append(row[2:9]+row[10:12]+row[13:16]+row[18:21]+row[44:46])
    return clean_politics_data 

def bulk_insert_politics(data):
    min_index=0
    max_index=1000
    while max_index < len(data):
        insert_politics(data[min_index:max_index])
        min_index += 1001
        max_index += 1001
    insert_politics(data[min_index:]) #insert the remaining few data points 

def insert_politics(data):
    to_add = ("INSERT INTO politics "
               "(fips, dem_votes16, rep_votes16, total_votes16, percent_dem16, percent_rep16, dif_votes16, state_abbrev, county, "
               " total_votes12, dem_votes12, rep_votes12, percent_dem12, percent_rep12, dif_votes12, percent_hs, percent_uni) "
               " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    cursor.executemany(to_add, data)
    connection.commit()

politics_dataset=create_clean_politics_data()

'''
insert data into db: 
bulk_insert_politics(politics_dataset[1:]) 
''' 

# DATA CLEANSING: FINDING BLANKS AND ADDING FIPS FOR HIGHER ACCURACY 

find_blanks_query=("select distinct(county), state from covid_cases where fips='' and county<>'Unknown'; ")
cursor.execute(find_blanks_query)
find_blanks=list(result(cursor))

find_NYC_query=('select fips, county, state from demographics '
    ' where state="New York" and county like "New York%";')
cursor.execute(find_NYC_query)
find_NYC=list(result(cursor))

find_Jop_query=('select fips, county, state from demographics '
    ' where state="Missouri" and county like "Joplin%";')
cursor.execute(find_Jop_query)
find_Jop=list(result(cursor)) # no match 

find_KCM_query=('select fips, county, state from demographics '
    ' where state="Missouri" and county like "Kansas City%";')
cursor.execute(find_KCM_query)
find_KCM=list(result(cursor))  # no match 

# update the table to add fips to New York City 
nyc_update_query=(f'update covid_cases set fips={find_NYC[0][0]} where county="New York City"')
cursor.execute(nyc_update_query)

# DATA SOURCE 5: 2020 ELECTION DATA BY COUNTY (CSV FILE)

tables['politics_2020'] = (
    "CREATE TABLE `politics_2020` ("
    "  `state` text,"
    "  `county` text,"
    "  `candidate` text,"
    "  `party` text,"
    "  `total_votes` int,"
    "  `won` text"
    ") ENGINE=InnoDB")

def create_politics_2020(dictionary):
    cursor.execute(dictionary['politics_2020'])

'''
create_politics_2020(tables)
'''

politics2020_data=read_csv('president_county_candidate.csv')

def bulk_insert_politics(data):
    min_index=0
    max_index=1000
    while max_index < len(data):
        insert_politics2020(data[min_index:max_index])
        min_index += 1001
        max_index += 1001
    insert_politics2020(data[min_index:]) #insert the remaining few data points 

def insert_politics2020(data):
    to_add = ("INSERT INTO politics_2020 "
               "(state, county, candidate, party, total_votes, won)"
                " VALUES (%s, %s, %s, %s, %s, %s)")
    cursor.executemany(to_add, data)
    connection.commit()

'''
insert data into db: 
bulk_insert_politics(politics2020_data[1:]) 
'''

cursor.close()
connection.close() 