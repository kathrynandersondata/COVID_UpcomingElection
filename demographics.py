from main import *

connection = mysql.connector.connect(user='root', password='dataadmin',
                              host='localhost', database='covidstocks')
cursor=connection.cursor(buffered=True)

# CREATING JOINT TABLE WITH CASES AND DEMOGRAPHICS DATA 
demo_cases_query = ('create temporary table fips_table '
    ' select demographics.fips as fips, max(cases) as cases, max(deaths) as deaths, max(median_age) as age, '
    ' max(population) as population, max(percent_female) as percent_female from covid_cases '
    ' join demographics on demographics.fips=covid_cases.fips '
    ' group by covid_cases.fips '
    ' order by max(cases) desc; ')
cursor.execute(demo_cases_query)
demo_cases_data='select cases, deaths, age, population, percent_female from fips_table; '
cursor.execute(demo_cases_data)
demo_cases=result(cursor)
demo_cases_df=DataFrame(demo_cases, columns=['Cases','Deaths','Age','Population','Percent_Female'])

# CREATING SCATTERPLOTS TO FIND CORRELATION BETWEEN CASES/DEATHS AND VARIOUS DEMOGRAPHIC FACTORS 

p=sns.PairGrid(demo_cases_df)
p.map_upper(sns.scatterplot)
p.map_lower(sns.scatterplot)
p.map_diag(sns.histplot, kde=True)
p.fig.set_size_inches(15,8)
p.fig.suptitle('Various Factor Influences on COVID Cases and Deaths')
if __name__ == "__main__":
    plt.show()

correl=pearsonr(demo_cases_df.Population, demo_cases_df.Cases) # returns 0.94 

# ANALYZING IF HOW EARLY YOU SAW CASES IMPACTS THE GROWTH OF THE DISEASE

first_date_query = ('select min(date), fips, county, state, sum(cases), sum(deaths) from covid_cases '
    ' group by fips, county, state; ')
cursor.execute(first_date_query)
first_date=result(cursor)
first_date_df=DataFrame(first_date, columns=['Date','Fips','County','State','Cases','Deaths']) 

p2=sns.displot(data=first_date_df, x='Date', y='Cases', kind='hist')
plt.title('First Instance of COVID and Effects on Total Cases')
plt.ylim(0, 1000000)
p2.fig.set_size_inches(7,7)
if __name__ == "__main__":
    plt.show()
    
cursor.close()
connection.close() 