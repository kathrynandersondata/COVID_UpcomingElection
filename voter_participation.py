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
swing16_query=('select state_abbrev as state, sum(dem_votes16) as dem_votes, sum(rep_votes16) as rep_votes, ' 
    ' sum(dem_votes16)/(sum(rep_votes16)+sum(rep_votes16)) as perc_dem from politics ' 
    ' group by state_abbrev ' 
    ' order by abs(sum(dem_votes16)-sum(rep_votes16))' 
    ' limit 10;')
cursor.execute(swing16_query)
swings16=result(cursor)
swings16_df=DataFrame(swings16, columns=['State','Dem_Votes','Rep_Votes','Perc_Dem'])

# finding swing states from 2012 election 
swing12_query=('select state_abbrev as state, sum(dem_votes12) as dem_votes, sum(rep_votes12) as rep_votes, ' 
    ' sum(dem_votes12)/(sum(rep_votes12)+sum(rep_votes12)) as perc_dem from politics ' 
    ' group by state_abbrev ' 
    ' order by abs(sum(dem_votes12)-sum(rep_votes12))' 
    ' limit 10;')
cursor.execute(swing12_query)
swings12=result(cursor)
swings12_df=DataFrame(swings12, columns=['State','Dem_Votes','Rep_Votes','Perc_Dem'])

# merging swing state data from each election to one DF 
swings_df=swings16_df.merge(swings12_df, on='State', how='outer')

# SWING STATES: ANALYZING CASE RATES 

# Scatterplot of swing states vs total states

agg_covid_query=('select state, sum(cases) as cases, sum(deaths) as deaths from covid_cases '
    ' group by state order by sum(cases) desc;')
cursor.execute(agg_covid_query)
agg_covid=result(cursor)
agg_covid_df=DataFrame(agg_covid, columns=['State','Cases','Deaths'])

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
'PA':'Pennsylvania','RI':'Rhode Island','SC':'South Carolina','SD':'South Dakota', 'TN':'Tennessee',
'UT':'Utah','VT':'Vermont','VA':'Virginia','WA':'Washington','WV':'West Virginia',
'WI':'Wisconsin','WY':'Wyoming'}
swings=[states[state] for state in swings_list]
swing_col_query=(f'select state, case when state in {tuple(swings)} then "S" else "N" end as swing from covid_cases group by state;')
cursor.execute(swing_col_query)
states_swings=result(cursor)
states_swings_df=DataFrame(states_swings, columns=['State','Status'])

swing_cases_df=agg_covid_df.merge(states_swings_df, on='State', how='left')

sns.jointplot(x=swing_cases_df['Cases'].astype(float), y=swing_cases_df['Deaths'].astype(float), hue=swing_cases_df['Status'])
plt.title('Cases and Deaths for Swing and Non-Swing States')
if __name__ == "__main__":
    plt.show() # plot 1 

impacted_states=(swing_cases_df.sort_values(by=['Deaths', 'Status'])) # returns PA, MI, FL

# Time series of swing states cases versus national

cases_over_time_query=('select date, state, sum(cases) as cases, sum(deaths) as deaths from covid_cases group by date, state;')
cursor.execute(cases_over_time_query)
cases_over_time=result(cursor)
cases_df=DataFrame(cases_over_time, columns=['Date','State','Cases','Deaths'])
cases_state_df=cases_df.merge(states_swings_df, on='State', how='left')

pop_query=('select state, sum(population) from demographics group by state;')
cursor.execute(pop_query)
pop=result(cursor)
pop_df=DataFrame(pop, columns=['State','Population'])
cases_pop_df=cases_state_df.merge(pop_df, how='left', on='State')
cases_pop_df['Cases_Per_Pop']=cases_pop_df['Cases']/cases_pop_df['Population']

sns.lineplot(data=cases_state_df, x='Date',y='Cases',style='Status', ci=None)
plt.title('Cases Over Time for Swing and Non-Swing States')
if __name__ == "__main__":
    plt.show() # plot 2 

sns.lineplot(data=cases_pop_df, x='Date',y='Cases_Per_Pop',style='Status', ci=None)
plt.title('Percent of Population Infected Over Time for Swing and Non-Swing States')
if __name__ == "__main__":
    plt.show() # plot 3 

# SWING STATES: VOTER PARTICIPATION 

participation_query=('select state, sum(total_votes16) as votes, sum(population) as population, avg(median_age) as avg_age,'
    ' sum(total_votes16)/sum(population) as percent_voters from politics ' 
    ' inner join demographics on demographics.fips=politics.fips ' 
    ' group by state;')
cursor.execute(participation_query)
participation=result(cursor)
participation_df=DataFrame(participation, columns=['State','Votes','Population','Avg_Age','Percent_Voters'])

participation_swings_df=participation_df.merge(swing_cases_df, on='State', how='left')

sns.displot(data=participation_swings_df,x='Cases',y='Percent_Voters',hue='Status')
plt.title('Percentage of Population that Votes - Swing and Non-Swing States')
if __name__ == "__main__":
    plt.show() # Swing states have higher percentages of voters

cursor.close()
connection.close() 