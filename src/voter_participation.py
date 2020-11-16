from main import * 
from demographics import * 

connection = mysql.connector.connect(user='root', password='dataadmin',
                              host='localhost', database='covidstocks')
cursor=connection.cursor(buffered=True)

# FINDING VOTING PARTICIPATION RATE BY POLITICAL PARTY 

voter_party_query=('select politics.fips, demographics.state, dem_votes16, rep_votes16, ' 
    ' total_votes16, population, total_votes16/population as vote_rate,'
    ' case when dem_votes16>rep_votes16 then "D" else "R" end as affiliation'
    ' from politics'
    ' inner join demographics on demographics.fips=politics.fips;')
cursor.execute(voter_party_query)
voter_party=result(cursor)
voter_party_df=DataFrame(voter_party,columns=['Fips','State','Dem_Votes','Rep_Votes','Total_Votes','Population','Vote_Rate', 'Affiliation'])

rep_vote_rate=voter_party_df.query("Affiliation == 'R'")['Vote_Rate'].mean() # returns 43.9%
dem_vote_rate=voter_party_df.query("Affiliation == 'D'")['Vote_Rate'].mean() # returns 42.7% 

# SWING STATES: FINDING THE SWING STATES

# finding swing states from 2016 election
swings_query=('select state_abbrev as state, sum(dem_votes16) as dem_votes, sum(rep_votes16) as rep_votes, ' 
' sum(dem_votes16)/(sum(rep_votes16)+sum(rep_votes16)) as perc_dem, ' 
' abs(sum(dem_votes16)-sum(rep_votes16)) as diff, ' 
' abs(sum(dem_votes16)-sum(rep_votes16))/(sum(dem_votes16)+sum(rep_votes16)) as margin ' 
' from politics group by state_abbrev ' 
' order by abs(sum(dem_votes16)-sum(rep_votes16))/(sum(dem_votes16)+sum(rep_votes16)) ' 
' limit 17 ')
cursor.execute(swings_query)
swings=result(cursor)
swings_df=DataFrame(swings, columns=['State','Dem_Votes','Rep_Votes','Perc_Dem','Diff','Margin'])
swings_df=swings_df.drop([1, 4, 10, 14])

# SWING STATES: ANALYZING CASE RATES 

agg_covid_query=('select county, state, max(cases) as cases, max(deaths) as deaths from covid_cases '
    ' group by county, state order by max(cases) desc;')
cursor.execute(agg_covid_query)
agg_covid=result(cursor)
agg_covid_df=DataFrame(agg_covid, columns=['County','State','Cases','Deaths'])

def create_swings(df, col):
    l=[]
    for item in df[col]:
        l.append(item)
    return l
swings_list=create_swings(swings_df, 'State')
states={'AL':'Alabama','AK':'Alaska','AZ':'Arizona', 'AR':'Arkansas','CA':'California',
'CO':'Colorado','CT':'Connecticut','DE':'Delaware','FL':'Florida','GA':'Georgia',
'HI':'Hawaii','ID':'Idaho','IL':'Illinois','IN':'Indiana','IA':'Iowa','KS':'Kansas',
'KY':'Kentucky','LA':'Louisiana','ME':'Maine','MD':'Maryland','MA':'Massachusetts',
'MI':'Michigan','MN':'Minnesota','MS':'Mississippi','MO':'Missouri','MT':'Montana',
'NE':'Nebraska','NV':'Nevada','NH':'New Hampshire','NJ':'New Jersey','NM':'New Mexico',
'NY':'New York','NC':'North Carolina','ND':'North Dakota','OH':'Ohio','OK':'Oklahoma','OR':'Oregon',
'PA':'Pennsylvania','RI':'Rhode Island','SC':'South Carolina','SD':'South Dakota', 'TX':'Texas', 'TN':'Tennessee',
'UT':'Utah','VT':'Vermont','VA':'Virginia','WA':'Washington','WV':'West Virginia',
'WI':'Wisconsin','WY':'Wyoming'}
swings=[states[state] for state in swings_list]
swing_col_query=(f'select county, state, case when state in {tuple(swings)} then "S" else "N" end as swing from covid_cases group by county, state;')
cursor.execute(swing_col_query)
states_swings=result(cursor)
states_swings_df=DataFrame(states_swings, columns=['County', 'State','Status'])

swing_cases_df=agg_covid_df.merge(states_swings_df, on=['County', 'State'], how='left')

# PERCENT OF POPULATION INFECTED OVER TIME 

cases_over_time_query=('select date, state, sum(cases) as cases, sum(deaths) as deaths from covid_cases group by date, state;')
cursor.execute(cases_over_time_query)
cases_over_time=result(cursor)
cases_df=DataFrame(cases_over_time, columns=['Date','State','Cases','Deaths'])
state_status_query=(f'select state, case when state in {tuple(swings)} then "S" else "N" end as swing from covid_cases group by state;')
cursor.execute(state_status_query)
state_status=result(cursor)
states_status_df=DataFrame(state_status, columns=['State','Status'])
cases_state_df=cases_df.merge(states_status_df, on='State', how='left')

pop_query=('select state, sum(population) from demographics group by state;')
cursor.execute(pop_query)
pop=result(cursor)
pop_df=DataFrame(pop, columns=['State','Population'])
cases_pop_df=cases_state_df.merge(pop_df, how='left', on='State')
graph_df=cases_pop_df.groupby(['Date', 'Status'], as_index=False).sum()
graph_df['Cases_Per_Pop']=(graph_df['Cases']/graph_df['Population']*100).astype(float)

if __name__ == "__main__":
    sns.lineplot(x=graph_df['Date'],y=graph_df['Cases_Per_Pop'],style=graph_df['Status'], ci=None)
    plt.suptitle('Percent of Population Infected Over Time for Swing and Non-Swing States', fontsize=12)
    plt.title('In the Months Leading Up to the Election, Swing States Had a Higher Percentage of the Population Infected with COVID', fontsize=8)
    plt.xlabel('Date', fontsize=10)
    plt.ylabel('Percent of Population with COVID (%)')
    plt.show() # plot 1 


# SWING STATES: VOTER PARTICIPATION 

participation_query=('select state, sum(total_votes16) as votes, sum(population) as population, avg(median_age) as avg_age,'
    ' sum(total_votes16)/sum(population) as percent_voters from politics ' 
    ' inner join demographics on demographics.fips=politics.fips ' 
    ' group by state;')
cursor.execute(participation_query)
participation=result(cursor)
participation_df=DataFrame(participation, columns=['State','Votes','Population','Avg_Age','Percent_Voters'])

participation_swings_df=participation_df.merge(swing_cases_df, on='State', how='left')

if __name__ == "__main__":
    sns.scatterplot(data=participation_swings_df,x='Cases',y=participation_swings_df['Percent_Voters']*100,hue='Status')
    plt.title('The Percentage of the Population that Votes is Higher in Swing States', fontsize=8)
    plt.suptitle('Percentage of Population that Votes - Swing and Non-Swing States', fontsize=12)
    plt.xlabel('Cases')
    plt.ylabel('Percent of Total Population that Voted in 2016 Election (%)')
    plt.show() #  plot 2

cursor.close()
connection.close() 