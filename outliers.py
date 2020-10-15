from main import *
from demographics import *

connection = mysql.connector.connect(user='root', password='dataadmin',
                              host='localhost', database='covidstocks')
cursor=connection.cursor(buffered=True)

# CLEANING DATA 
cursor.execute(nyc_update_query) # adds NYC fips 
remove_unknown_query=('delete from covid_cases where county="Unknown";')
cursor.execute(remove_unknown_query) # removes unknowns 

# DETERMINING OUTLIERS IN CASES PER POPULATION 

sns.lmplot(data=demo_cases_df, x='Population', y='Cases') 
if __name__ == "__main__":
    plt.show()

cursor.execute(demo_cases_query) # recreates temp table that matches cases with demo info 
poor_perf_query=('select * from fips_table where cases>250000 and population<2000000;')
cursor.execute(poor_perf_query)
poor_perf=result(cursor) # returns New York City 

# DETERMINING OUTLIERS IN MORTALITY RATE 

# find average mortality rate in county --> 2.11%

avg_mort_create=('create temporary table avg_mortality ' 
    ' select fips, county, state, max(cases) as total_cases, max(deaths) as total_deaths, '
    ' max(deaths)/max(cases) as mortality ' 
    ' from covid_cases ' 
    ' group by fips, county, state;') 

cursor.execute(avg_mort_create)

avg_mort_query=('select avg(mortality) from avg_mortality;')
cursor.execute(avg_mort_query)
avg_mort=result(cursor)

# graphing mortality rates 
mort_query=('select * from avg_mortality;')
cursor.execute(mort_query)
mort=result(cursor)

mort_df=DataFrame(mort, columns=['Fips','County','State','Total_Cases','Total_Deaths','Mortality'])
sns.jointplot(data=mort_df, x='Total_Cases', y='Mortality') # no true outliers 
#plt.show()

cursor.close()
connection.close() 