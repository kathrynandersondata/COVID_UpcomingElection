from main import *
from demographics import demo_cases_query

connection = mysql.connector.connect(user='root', password='dataadmin',
                              host='localhost', database='covidstocks')
cursor=connection.cursor(buffered=True)

# CLEANING DATA 

cursor.execute(nyc_update_query) # adds NYC fips 
remove_unknown_query=('delete from covid_cases where county="Unknown";')
cursor.execute(remove_unknown_query) # removes unknowns 

# FINDING AVERAGE AND TOTAL MORTALITY RATES FOR THE COUNTRY --> 1.9% average, 2.3% country-wide rate 

avg_mort_create=('create temporary table avg_mortality ' 
    ' select fips, county, state, max(cases) as total_cases, max(deaths) as total_deaths, '
    ' max(deaths)/max(cases) as mortality ' 
    ' from covid_cases ' 
    ' group by fips, county, state;') 

cursor.execute(avg_mort_create)

avg_mort_query=('select avg(mortality) from avg_mortality;')
cursor.execute(avg_mort_query)
avg_mort=result(cursor) # 1.9%

total_mort_query=('select sum(total_deaths)/sum(total_cases) as mortality from avg_mortality;')
cursor.execute(total_mort_query)
total_mort=result(cursor) # 2.3% 

# GRAPHING MORTALITY RATES 

mort_query=('select * from avg_mortality;')
cursor.execute(mort_query)
mort=result(cursor)

mort_df=DataFrame(mort, columns=['Fips','County','State','Total_Cases','Total_Deaths','Mortality'])
sns.scatterplot(data=mort_df, x='Total_Cases', y=mort_df['Mortality']*100) 
plt.suptitle('Cases and Mortality Rates', fontsize=12)
plt.title('A Handful of Counties Have Excessively High Mortality Rates for the Amount of COVID Cases', fontsize=8)
plt.xlabel('Total Cases')
plt.ylabel('Mortality Rate (%)')
if __name__ == "__main__":
    plt.show() # plot 1 

cursor.close()
connection.close() 