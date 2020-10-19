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

if __name__ == "__main__":
    p=sns.PairGrid(demo_cases_df)
    p.map_upper(sns.scatterplot)
    p.map_lower(sns.scatterplot)
    p.map_diag(sns.histplot, kde=True)
    p.fig.set_size_inches(15,8)
    p.fig.suptitle('Various Factor Influences on COVID Cases and Deaths', fontsize=12)
    p.fig.suptitle('Population and Cases Have the Highest Correlation of the Demographic Factors', fontsize=8)
    plt.show() # plot 1 

correl=pearsonr(demo_cases_df.Population, demo_cases_df.Cases) # returns 0.94 

# ANALYZING IF HOW EARLY YOU SAW CASES IMPACTS THE GROWTH OF THE DISEASE

first_date_query = ('select min(date), fips, county, state, sum(cases), sum(deaths) from covid_cases '
    ' group by fips, county, state; ')
cursor.execute(first_date_query)
first_date=result(cursor)
first_date_df=DataFrame(first_date, columns=['Date','Fips','County','State','Cases','Deaths']) 

if __name__ == "__main__":
    p2=sns.displot(data=first_date_df, x='Date', y='Cases', kind='hist')
    plt.title('The Counties That Experienced the Worst COVID Cases Saw Their First Case in Early March and April', fontsize=8)
    plt.suptitle('First Instance of COVID and Effects on Total Cases', fontsize=12)
    plt.ylim(0, 1000000)
    p2.fig.set_size_inches(8,8)
    plt.xlabel('Date of First COVID Case')
    plt.ylabel('Total COVID Cases (in Millions)')
    plt.show() # plot 2 
    
cursor.close()
connection.close() 