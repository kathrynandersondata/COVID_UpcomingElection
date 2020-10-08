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

# DATA SOURCE 2: CSV FILE 
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

#retrieving data from CSV file 
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

# QUERY GENERAL FORMAT 
''' 
RUNNING QUERIES 
query="select count(*) from covid_cases where state='California'; "
cursor.execute(query)
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

# FINDING CORRELATION BETWEEN COVID DATA AND STOCK MARKET 

correl_query = ('select covid_cases.date, sum(cases), sum(deaths), avg(stock_data.close) ' 
    ' from covid_cases ' 
    ' left join stock_data' 
    ' on stock_data.date=covid_cases.date ' 
    ' group by date; ') 

cursor.execute(correl_query)
daily_correl=result(cursor)
daily_correl_df=DataFrame(daily_correl, columns=['Date','Cases','Deaths','S&P500'])
daily_correl_df['NewCases']=daily_correl_df['Cases'].astype('float').diff()
daily_correl_df['NewCases'][daily_correl_df['NewCases']<0]=0

# CREATE COMBO CHART 
fig, ax1 = plt.subplots(figsize=(10,6))
color = 'green'
# cases line graph 
ax1.set_title('COVID-19 Correlation with Stock Market', fontsize=16)
ax1.set_xlabel('Date', fontsize=16)
ax1.set_ylabel('Daily New COVID Cases', fontsize=16)
ax1=sns.lineplot(x='Date', y='NewCases', data = daily_correl_df.dropna(), sort=False, color=color)
ax1.tick_params(axis='y')
ax2 = ax1.twinx() #specify we want to share the same x-axis
color = 'purple'
# S&P line graph 
ax2.set_ylabel('Share of S&P500 ($)', fontsize=16)
ax2 = sns.lineplot(x='Date', y='S&P500', data = daily_correl_df.dropna(), sort=False, color=color)
ax2.tick_params(axis='y', color=color)
#plt.ylim(reversed(plt.ylim()))
#plt.show()

# DATA SOURCE 3 DEMOGRAPHIC DATA 

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

# QUERY WITH CASES AND DEMOGRAPHIC INFO 
demo_cases_query = ('select demographics.fips, max(cases), max(deaths), max(median_age), '
    ' max(population), max(percent_female) from covid_cases '
    ' join demographics on demographics.fips=covid_cases.fips '
    ' group by covid_cases.fips '
    ' order by max(cases) desc; ')

cursor.execute(demo_cases_query)
demo_cases=result(cursor)
demo_cases_df=DataFrame(demo_cases, columns=['Fips','Cases','Deaths','Age','Population','Percent_Female'])

cursor.close()
connection.close() 

'''
Ideas:
1. mask use?
2. demographics
'''