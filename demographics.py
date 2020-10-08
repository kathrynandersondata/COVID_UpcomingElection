from main import *

connection = mysql.connector.connect(user='root', password='dataadmin',
                              host='localhost', database='covidstocks')
cursor=connection.cursor(buffered=True)

# DATA CLEANSING: FINDING BLANKS AND ADDING FIPS FOR HIGHER ACCURACY 

find_blanks_query=("select  distinct(county), state from covid_cases where fips='' and county<>'Unknown'; ")
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
nyc_update_query=(f'update covid_cases set fips={find_NYC[0][0]} where county="New York City";')
cursor.execute(nyc_update_query)

# CREATING JOINT TABLE WITH CASES AND DEMOGRAPHICS DATA 
demo_cases_query = ('create temporary table fips_table '
    ' select demographics.fips as fips, max(cases) as cases, max(deaths) as deaths, max(median_age) as age, '
    ' max(population) as population, max(percent_female) as percent_female from covid_cases '
    ' join demographics on demographics.fips=covid_cases.fips '
    ' group by covid_cases.fips '
    ' order by max(cases) desc; ')

cursor.execute(demo_cases_query)

demo_cases_data='select * from fips_table; '
cursor.execute(demo_cases_data)

demo_cases=result(cursor)
demo_cases_df=DataFrame(demo_cases, columns=['Fips','Cases','Deaths','Age','Population','Percent_Female'])

# CREATING SCATTERPLOTS TO FIND CORRELATION BETWEEN CASES/DEATHS AND VARIOUS DEMOGRAPHIC FACTORS 
'''
CASES VS DEATHS WITH HUE FOR FACTORS 
sns.scatterplot(data=demo_cases_df, x='Cases', y='Deaths',hue='Population',size='Population')
sns.scatterplot(data=demo_cases_df, x='Cases', y='Deaths',hue='Percent_Female',size='Percent_Female')
sns.scatterplot(data=demo_cases_df, x='Cases', y='Deaths',hue='Age',size='Age')
plt.show()
'''
''' 
CASES OR DEATHS VS FACTORS 
#sns.lmplot(data=demo_cases_df, x='Population', y='Cases')
#sns.lmplot(data=demo_cases_df, x='Population', y='Deaths')
#sns.lmplot(data=demo_cases_df, x='Age', y='Cases') # no strong correlation
#sns.lmplot(data=demo_cases_df, x='Age', y='Deaths') # no strong correlation
#sns.lmplot(data=demo_cases_df, x='Percent_Female', y='Cases')
# sns.lmplot(data=demo_cases_df, x='Percent_Female', y='Deaths')
plt.show()
''' 
correl=pearsonr(demo_cases_df.Population, demo_cases_df.Cases)

''' 
def find_greatest_correl(df, factors, stats):
    output={}
    for factor in factors:
        for stat in stats:
            output[[factor, stat]]=pearsonr(df[factor], df[stat])
    return output

factor_list=['Population','Age','Percent_Female']
stats_list=['Cases','Deaths']
print(find_greatest_correl(demo_cases_df, factor_list, stats_list))
''' 
# ANALYZING IF HOW EARLY YOU SAW CASES IMPACTS THE GROWTH OF THE DISEASE

first_date_query = ('select min(date), fips, county, state, sum(cases), sum(deaths) from covid_cases '
    ' group by fips, county, state; ')
   
cursor.execute(first_date_query)

first_date=result(cursor)
first_date_df=DataFrame(first_date, columns=['Date','Fips','County','State','Cases','Deaths']) 

sns.scatterplot(data=first_date_df, x='Date', y='Cases')
#plt.show()


cursor.close()
connection.close() 