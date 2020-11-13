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

# SWING STATES CASES AND AFFILIATION

cases_swings_time_query=('with cte as( ' 
' select date, covid_cases.state, sum(cases) as cases, sum(deaths) as deaths, ' 
' sum(population) as pop, sum(cases)/sum(population)*100 as cases_perc, ' 
' case when covid_cases.state in ' 
' ("Florida", "Pennsylvania", "North Carolina", "Georgia","Arizona","Nevada", "Maine", "Michigan","Wisconsin","Colorado","Iowa","Ohio","Texas") ' 
' then "S" else "N" end as affiliation ' 
' from covid_cases ' 
' join demographics on demographics.fips=covid_cases.fips ' 
' group by date, state ' 
' order by date desc, cases_perc desc), ' 
' cte2 as ( ' 
' select state, candidate, ' 
' case when candidate="Joe Biden" then sum(total_votes) else 0 end as biden, ' 
' case when candidate="Donald Trump" then sum(total_votes) else 0 end as trump ' 
' from politics_2020 ' 
' group by state, candidate ' 
' having candidate="Joe Biden" or candidate="Donald Trump"), ' 
' cte3 as( ' 
' select state, sum(biden) as biden, sum(trump) as trump ' 
' from cte2' 
' group by state ' 
')'
' select date, cte.state, cases, deaths, pop, cases_perc, ' 
' case when biden>trump then "D" else "R" end as party ' 
' from cte ' 
' join cte3 on cte3.state=cte.state ' 
' where affiliation="S" ' 
' order by date desc')
cursor.execute(cases_swings_time_query)
cases_swings_time=result(cursor)
cases_swings_time_df=DataFrame(cases_swings_time, columns=['Date','State','Cases','Deaths','Pop','Cases_Perc','Party'])

if __name__ == "__main__":
    sns.lineplot(data=cases_swings_time_df, x='Date',y='Cases_Perc', hue='Party', style='State',ci=None)
    plt.suptitle('Cases As Percent of the Population Over Time in Swing States', fontsize=12)
    plt.title('All Swing States Experienced an Uptick in Cases Ahead of the Election, with the Majority Voting for Biden', fontsize=8)
    plt.xlabel('Date', fontsize=10)
    plt.ylabel('Cases as a Percent of the Population (%)')
    plt.show() # plot 1

cursor.close()
connection.close() 