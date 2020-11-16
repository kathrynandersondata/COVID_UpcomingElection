from main import * 
from demographics import * 

connection = mysql.connector.connect(user='root', password='dataadmin',
                              host='localhost', database='covidstocks')
cursor=connection.cursor(buffered=True)

# AGGREGATE STATISTICS 
totals_query='select sum(cases), sum(deaths) from covid_cases where date="2020-11-11"'
cursor.execute(totals_query)
totals=result(cursor)

# RANKS FOR CASES AND DEATHS 
ranks_query=('select county, state, max(cases) as cases, max(deaths) as deaths, ' 
'rank() over (order by max(cases) desc) as rnk ' 
'from covid_cases ' 
'group by county, state ' 
'order by 4 desc ')
cursor.execute(ranks_query)
ranks=result(cursor)
ranks_df=DataFrame(ranks, columns=['County','State','Cases','Deaths','Cases_Rnk'])
print(ranks_df)

# OUTLIERS 
outliers_query=('with cte as ( ' 
' select covid_cases.fips, covid_cases.county, covid_cases.state, max(cases) as cases, max(population) as pop, ' 
'      max(cases)/max(population) as cases_per_pop ' 
'from covid_cases ' 
'join demographics on demographics.fips=covid_cases.fips ' 
'group by fips, county, state), ' 
'cte2 as ( ' 
'select fips, county, state, cases, ntile(100) over (order by cases) as cases_percentile, ' 
'      ntile(100) over (order by cases_per_pop) as cases_perpop_percentile ' 
'from cte) ' 
'select state,count(county) as num_counties, cases_perpop_percentile from cte2 ' 
' where cases_perpop_percentile=1 or cases_perpop_percentile=99 ' 
'group by state, cases_perpop_percentile ' 
'order by cases_perpop_percentile asc, num_counties desc;')
cursor.execute(outliers_query)
outliers=result(cursor)
outliers_df=DataFrame(outliers, columns=['State','Number_of_Counties','Cases_Per_Pop_Perc'])

cursor.close()
connection.close() 