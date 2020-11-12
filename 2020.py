from main import * 
from demographics import * 

connection = mysql.connector.connect(user='root', password='dataadmin',
                              host='localhost', database='covidstocks')
cursor=connection.cursor(buffered=True)

# HOW MANY OF THE LARGEST 100 COUNTIES VOTE DEMOCRATIC? --> 87/100
largest_county_query=('with cte as( '
'select demographics.county, demographics.state, population, party '
'from demographics '
'join politics_2020 on politics_2020.state=demographics.state '
'and demographics.county=politics_2020.county '
'where won="True" '
'order by population desc '
'limit 100) '
'select count(*) from cte where party="DEM"')
cursor.execute(largest_county_query)

# DID THE EXTENT OF COVID IMPACT THE WAY VOTERS VOTED IN SWING STATES?

cases_swings2020_query=('with cte as( ' 
' select covid_cases.fips, demographics.county, demographics.state, max(cases) as cases, ' 
' max(population) as population, max(cases)/max(population) as percent_positive ' 
' from covid_cases ' 
' join demographics on demographics.fips=covid_cases.fips ' 
' group by covid_cases.fips, demographics.county, demographics.state ' 
' ), ' 
' cte2 as( ' 
' select fips, cte.county, cte.state, cases, population, ' 
' percent_positive, candidate, party, won ' 
' from cte ' 
' join politics_2020 on politics_2020.county=cte.county ' 
' and politics_2020.state=cte.state ' 
' where won="True" ' 
' and cte.state in ("Florida", "Pennsylvania", "North Carolina", "Georgia","Arizona","Nevada", ' 
' "Maine", "Michigan","Wisconsin","Colorado","Iowa","Ohio","Texas"))'
' select candidate, max(percent_positive) as max, min(percent_positive) as min, ' 
'      avg(percent_positive) as average, sum(cases)/sum(population) as overall_infection_rate ' 
'from cte2 ' 
' group by candidate;')
cursor.execute(cases_swings2020_query)
cases_swings2020=result(cursor)
cases_swings2020_df=DataFrame(cases_swings2020, columns=['Candidate','Max','Min','Average','Weighted Average'])
print(cases_swings2020_df)

cursor.close()
connection.close() 