import mysql.connector
from main import result
from pandas import DataFrame
import seaborn as sns 
import matplotlib.pyplot as plt 

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

# VOTER TURNOUT OR CHANGE OF HEART?
elections_swings_query=('with cte as ( ' 
' select county, state, ' 
' case when candidate="Joe Biden" then total_votes else 0 end as biden, ' 
' case when candidate="Donald Trump" then total_votes else 0 end as trump, ' 
' case when state="Florida" then "FL" when state="Pennsylvania" then "PA" when state="North Carolina" ' 
' then "NC" when state="Georgia" then "GA" when state="Arizona" then "AZ" when state="Nevada" then "NV" ' 
' when state="Maine" then "ME" when state="Michigan" then "MI" when state="Wisconsin" then "WI" ' 
' when state="Colorado" then "CO" when state="Iowa" then "IA" when state="Ohio" then "OH" when state="Texas" ' 
' then "TX" end as state_abbrev ' 
' from politics_2020 ' 
' where state in ("Florida", "Pennsylvania", "North Carolina", "Georgia","Arizona","Nevada", ' 
' "Maine", "Michigan","Wisconsin","Colorado","Iowa","Ohio","Texas")), ' 
' cte2 as ('
' select cte.county, state, sum(biden) as biden, sum(trump) as trump, ' 
'      max(dem_votes16) as hillary, max(rep_votes16) as trump16, ' 
'       case when sum(biden)>sum(trump) then "B" else "T" end as winner20, ' 
'       case when max(dem_votes16)>max(rep_votes16) then "H" else "T" end as winner16, ' 
'       sum(biden)-max(dem_votes16) as dem_diff, sum(trump)-max(rep_votes16) as rep_diff '
'from cte ' 
'join politics on politics.county=cte.county and cte.state_abbrev=politics.state_abbrev ' 
'group by county, state) '
' select * from cte2') 
cursor.execute(elections_swings_query)
elections_swings=result(cursor)
elections_swings_df=DataFrame(elections_swings, columns=['County','State','Biden20','Trump20','Clinton16','Trump16','Win20','Win16','Dem_Diff','Rep_Diff'])

trump_to_biden=len(elections_swings_df[(elections_swings_df['Win16']=='T') & (elections_swings_df['Win20']=='B')]) 
clinton_to_trump=len(elections_swings_df[(elections_swings_df['Win16']=='H') & (elections_swings_df['Win20']=='T')]) 
trump=len(elections_swings_df[(elections_swings_df['Win16']=='T') & (elections_swings_df['Win20']=='T')]) 
dem=len(elections_swings_df[(elections_swings_df['Win16']=='H') & (elections_swings_df['Win20']=='B')]) 
new_dem_votes=elections_swings_df['Dem_Diff'].sum()
new_rep_votes=elections_swings_df['Rep_Diff'].sum()

elections_swings_df['Votes16']=(elections_swings_df['Trump16']+elections_swings_df['Clinton16']).astype(float)
elections_swings_df['Votes20']=(elections_swings_df['Trump20']+elections_swings_df['Biden20']).astype(float)
elections_swings_df['Trump20']=(elections_swings_df['Trump20']).astype(float)
elections_swings_df['Biden20']=(elections_swings_df['Biden20']).astype(float)

clean_elections=elections_swings_df[['State','Biden20','Trump20','Clinton16','Trump16']].groupby(['State'], as_index=False).sum()
barplot_data=clean_elections.melt('State', var_name='Candidate', value_name='Votes')

def election_year(row):
    if row['Candidate']=='Trump16':
        return '2016'
    if row['Candidate']=='Trump20':
        return '2020'
    if row['Candidate']=='Biden20':
        return '2020'
    if row['Candidate']=='Clinton16':
        return '2016'

barplot_data['Election_Year']=barplot_data.apply (lambda row: election_year(row), axis=1)

clean_elections['2020']=abs(clean_elections['Biden20']-clean_elections['Trump20'])
clean_elections['2016']=abs(clean_elections['Clinton16']-clean_elections['Trump16'])
margins_df=clean_elections[['State','2020','2016']]
margins_df=margins_df.melt('State',var_name='Election Year',value_name='Margin')

if __name__ == "__main__":
    sns.barplot(x=barplot_data["State"], y=barplot_data['Votes'], hue=barplot_data['Election_Year'], ci=None)
    plt.suptitle('Voter Turnout for 2020 and 2016 Elections', fontsize=12)
    plt.title('Voter Turnout Was Significantly Higher in the 2020 Election, Especially in Texas, Florida, Arizona, and Georgia', fontsize=8)
    plt.xlabel('State', fontsize=10)
    plt.ylabel('Votes (millions)')
    plt.show() # plot 2 

if __name__ == "__main__":
    sns.barplot(x=margins_df["State"], y=margins_df['Margin'], hue=margins_df['Election Year'], ci=None)
    plt.suptitle('Margins for 2020 and 2016 Elections', fontsize=12)
    plt.title('Arizona, Georgia, and Nevada Ran the Closest Races In 2020, Whereas Michigan and Nevada Were the Closest in 2016', fontsize=8)
    plt.xlabel('State', fontsize=10)
    plt.ylabel('Margin of Votes')
    plt.show() # plot 3

clean_elections['Increase']=clean_elections['Biden20']+clean_elections['Trump20']-clean_elections['Clinton16']-clean_elections['Trump16']
clean_elections.sort_values(by='Increase', ascending=False)

cursor.close()
connection.close() 