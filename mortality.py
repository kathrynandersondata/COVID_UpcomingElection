from main import *
from demographics import demo_cases_query

connection = mysql.connector.connect(user='root', password='dataadmin',
                              host='localhost', database='covidstocks')
cursor=connection.cursor(buffered=True)

# CLEANING DATA 

cursor.execute(nyc_update_query) # adds NYC fips 
remove_unknown_query=('delete from covid_cases where county="Unknown";')
cursor.execute(remove_unknown_query) # removes unknowns 

# FINDING AVERAGE MORTALITY RATE FOR THE COUNTRY --> 2.11%

avg_mort_create=('create temporary table avg_mortality ' 
    ' select fips, county, state, max(cases) as total_cases, max(deaths) as total_deaths, '
    ' max(deaths)/max(cases) as mortality ' 
    ' from covid_cases ' 
    ' group by fips, county, state;') 

cursor.execute(avg_mort_create)

avg_mort_query=('select avg(mortality) from avg_mortality;')
cursor.execute(avg_mort_query)
avg_mort=result(cursor) 

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

# OUTLIERS: HIGH MORTALITY RATE GIVEN CASES

mort15_query=('select max(total_cases) from avg_mortality where mortality>0.15;')
cursor.execute(mort15_query)
mort15=result(cursor) # returns 431 

mort15_counties=('select avg_mortality.county as county, avg_mortality.state as state, '
    ' mortality, population from avg_mortality '
    ' join demographics on demographics.fips=avg_mortality.fips'
    ' where mortality>0.15;')
cursor.execute(mort15_counties)
mort15_counties=result(cursor)
mort15_counties_df=DataFrame(mort15_counties, columns=['County','State','Mortality','Population'])
avg_pop_mort15=mort15_counties_df['Population'].mean() # returns ~22,000

avg_pop_query=('select avg(population) from demographics;')
cursor.execute(avg_pop_query)
avg_pop=result(cursor) # returns ~101,000

# OUTLIERS: HIGH MORTALITY RATE GIVEN CASES PER POPULATION

cursor.execute(demo_cases_query) #re-creating fips_table temporary table from demographics file
mort_outliers_query=('select fips_table.fips, avg_mortality.county as county, avg_mortality.state as state, '
    ' mortality, cases, deaths, population, cases/population as cases_per_pop from avg_mortality '
    ' join fips_table on fips_table.fips=avg_mortality.fips'
    ' where mortality>0.05'
    ' order by cases_per_pop, mortality desc;')
cursor.execute(mort_outliers_query)
mort_outliers=result(cursor)
mort_outliers_df=DataFrame(mort_outliers, columns=['Fips','County','State','Mortality','Cases','Deaths','Population','Cases_Per_Pop'])
sort_mo_df=mort_outliers_df.sort_values(by=['Cases_Per_Pop','Mortality'], ascending=False)

sns.scatterplot(x=sort_mo_df['Cases_Per_Pop']*100, y=sort_mo_df['Mortality']*100) 
plt.suptitle('Percent of Population with COVID and Mortality Rates', fontsize=12)
plt.title('Many Counties Have Higher than Average Mortality Rates, Even Given Large Population Infection Rates', fontsize=8)
plt.xlabel('Percent of Population with COVID (%)')
plt.ylabel('Mortality Rate (%)')
if __name__ == "__main__":
    plt.show() # plot 2 

avg_cases_per_pop=sort_mo_df['Cases_Per_Pop'].mean() # 1.8% 
avg_mortality=sort_mo_df['Mortality'].mean() # 7.4% 

bad_covid_cases=sort_mo_df[sort_mo_df['Cases_Per_Pop']>avg_cases_per_pop]
bad_covid_mort=bad_covid_cases[bad_covid_cases['Mortality']>avg_mortality]

# STATES THAT CONTAIN OUTLIERS 

bad_covid_mort.groupby(by='State').describe() # Georgia: 6, Texas: 4, New Jersey: 3

# POLITICAL PARTY AFFILIATION OF OUTLIERS 

affil_query=('select fips, case when dem_votes16>rep_votes16 then "D" else "R" end as affiliation '
    ' from politics')
cursor.execute(affil_query)
affils=result(cursor)
affils_df=DataFrame(affils, columns=['Fips','Affiliation'])

mort_affils_df=bad_covid_mort.merge(affils_df, on='Fips', how='left')

sns.scatterplot(x=mort_affils_df['Cases_Per_Pop']*100,y=mort_affils_df['Mortality']*100, hue=mort_affils_df['Affiliation'])
plt.suptitle('High Mortality Counties by Affiliation', fontsize=12)
plt.title('Both Democratic and Republican Counties Are Among the Outliers with High Cases and Mortality Rates', fontsize=8)
plt.xlabel('Percentage of Population with COVID (%)')
plt.ylabel('Mortality Rate (%)')
if __name__ == "__main__":
    plt.show() # plot 3 

cursor.close()
connection.close() 