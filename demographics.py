from main import *

connection = mysql.connector.connect(user='root', password='dataadmin',
                              host='localhost', database='covidstocks')
cursor=connection.cursor(buffered=True)

# FINDING BLANKS AND ADDING FIPS FOR HIGHER ACCURACY 

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
    ' select demographics.fips, max(cases), max(deaths), max(median_age), '
    ' max(population), max(percent_female) from covid_cases '
    ' join demographics on demographics.fips=covid_cases.fips '
    ' group by covid_cases.fips '
    ' order by max(cases) desc; ')

cursor.execute(demo_cases_query)

demo_cases_data='select * from fips_table; '
cursor.execute(demo_cases_data)

demo_cases=result(cursor)
demo_cases_df=DataFrame(demo_cases, columns=['Fips','Cases','Deaths','Age','Population','Percent_Female'])

cursor.close()
connection.close() 