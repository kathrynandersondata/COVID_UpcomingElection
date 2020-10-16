from main import * 
from demographics import demo_cases_query
from voter_participation import * 

connection = mysql.connector.connect(user='root', password='dataadmin',
                              host='localhost', database='covidstocks')
cursor=connection.cursor(buffered=True)

# PLOTTING CASES AND DEATHS WITH POLITICAL PARTY HUE 
cursor.execute(demo_cases_query)

cases_politics_data=('select * from fips_table' 
    ' inner join politics on politics.fips=fips_table.fips;')
cursor.execute(cases_politics_data)
cases_politics=result(cursor)
cases_politics_df=DataFrame(cases_politics, columns=['fips', 'cases', 'deaths', 'age', 'population',
        'percent_female', 'fips', 'dem_votes16', 'rep_votes16', 'total_votes16', 'percent_dem16', 'percent_rep16', 
        'dif_votes16', 'state_abbrev', 'county', 'total_votes12', 'dem_votes12', 'rep_votes12', 
        'percent_dem12', 'percent_rep12', 'dif_votes12', 'percent_hs', 'percent_uni'])

affiliation_create=('create temporary table affiliations ' 
    ' select fips_table.fips, cases, deaths, '
    ' case when dem_votes16>rep_votes16 then "Democrat" else "Republican" end as affiliation ' 
    ' from fips_table '
    ' left join politics on politics.fips=fips_table.fips;')

cursor.execute(affiliation_create)
affiliation_query=('select * from affiliations;')
cursor.execute(affiliation_query)
affiliation=result(cursor)
affiliation_df=DataFrame(affiliation, columns = ['fips','cases','deaths','affiliation'])

p4=sns.scatterplot(data=affiliation_df, x='cases', y='deaths', hue='affiliation')
plt.title('Many Democratic Counties Have Elevated Levels COVID Cases and Deaths', fontsize=8)
plt.suptitle('Cases and Deaths by Affiliation', fontsize=12)
plt.xlabel('Cases')
plt.ylabel('Deaths')
plt.xlim(0,30000)
plt.ylim(0,2000)
if __name__ == "__main__":
    plt.show() # plot 1 

# FINDING CORRELATION BY PARTY 

rep_query=('select * from affiliations where affiliation="Republican";')
cursor.execute(rep_query)
reps=result(cursor)
reps_df=DataFrame(reps,columns = ['fips','cases','deaths','affiliation'])

dem_query=('select * from affiliations where affiliation="Democrat";')
cursor.execute(dem_query)
dems=result(cursor)
dems_df=DataFrame(dems,columns = ['fips','cases','deaths','affiliation'])

rep_correl=np.corrcoef(reps_df.cases,reps_df.deaths) #0.899
dem_correl=np.corrcoef(dems_df.cases, dems_df.deaths) #0.879

# FINDING AVERAGE MORTALITY RATE BY PARTY

affil_mort_query=('create temporary table affil_mortality ' 
    ' select fips, cases, deaths, deaths/cases as mortality, affiliation from affiliations;')
cursor.execute(affil_mort_query)
affil_mort_query2=('select * from affil_mortality;')
cursor.execute(affil_mort_query2)
affil_mort=result(cursor)
affil_mort_df=DataFrame(affil_mort, columns=['Fips', 'Cases','Deaths', 'Mortality','Affiliation'])

rep_mortality=('select avg(mortality) from affil_mortality'
    ' where affiliation="Republican";')
cursor.execute(rep_mortality)
rep_mort=result(cursor) # 2.0%
dem_mortality=('select avg(mortality) from affil_mortality'
    ' where affiliation="Democrat";')
cursor.execute(dem_mortality)
dem_mort=result(cursor) # 3.0%

p5=sns.displot(data=affil_mort_df, x='Cases', y=affil_mort_df['Mortality']*100, hue='Affiliation', kind='kde', fill=True)
plt.suptitle('Many Democratic Counties Have Higher Case Levels, but Many Republican Counties Have Higher Mortality Rates', fontsize=8)
plt.title('Cases and Mortality Rate by Affiliation', fontsize=12)
plt.xlim(0,20000)
plt.ylim(0,10)
plt.xlabel('Cases')
plt.ylabel('Mortality Rate: Deaths Per Cases (%)')
p5.fig.set_size_inches(8,8)
if __name__ == "__main__":
    plt.show() # plot 2 

# PLOTTING POPULATION AND CASES BY PARTY

pop_cases_query=('select demographics.fips, cases, deaths, population, affiliations.affiliation as affiliation'
    ' from demographics ' 
    ' inner join affiliations on affiliations.fips=demographics.fips ' 
    ' where population < 5000000;')
cursor.execute(pop_cases_query)
pop_cases=result(cursor)
pop_cases_df=DataFrame(pop_cases, columns=['Fips','Cases','Deaths','Population','Affiliation'])

p6=sns.lmplot(data=pop_cases_df, x='Population', y='Cases', hue='Affiliation')
plt.suptitle('The Strong Correlation Between Population and Cases Explains the Strong Correlation Between Democratic Affilition and Cases', fontsize=8)
plt.title('Population and Cases by Affiliation', fontsize=12)
plt.xlabel('Population (Millions)')
plt.ylabel('Cases')
p6.fig.set_size_inches(8,8)
if __name__ == "__main__":
    plt.show() # plot 3 

# finding cases/population by party 

cases_per_pop_query=('create temporary table cases_per_pop' 
    ' select affiliations.affiliation as affiliation, sum(cases), sum(deaths), sum(population),  ' 
    ' avg(cases/population) as cases_per_pop from demographics ' 
    ' inner join affiliations on affiliations.fips=demographics.fips ' 
    ' group by affiliation; ')
cursor.execute(cases_per_pop_query)
cases_per_pop_query2=('select * from cases_per_pop;')
cursor.execute(cases_per_pop_query2)
cases_per_pop=result(cursor)
cases_per_pop_df=DataFrame(cases_per_pop, columns=['Affiliation', 'Total_Cases','Total_Deaths','Total_Population','Avg_Cases_Per_Pop'])
# returns 2.5% cases/population for Democrats, 2.0% cases/population for Republicans 

# PLOTTING WEEKLY NEW CASES OVER TIME BY PARTY

temp1_query=('create temporary table temp1'
' select date, case when dem_votes16>rep_votes16 then "D" else "R" end as affiliation,' 
' sum(cases) as total_cases, sum(deaths) as total_deaths' 
' from covid_cases'
' join politics on politics.fips=covid_cases.fips'
' group by date, affiliation' 
' order by date;')
cursor.execute(temp1_query)

temp2_query=('create temporary table temp2'
' select week(date) as week_num, affiliation, sum(total_cases) as total_cases, sum(total_deaths) as total_deaths' 
' from temp1' 
' group by week(date), affiliation;')
cursor.execute(temp2_query)

weekly_cases_query=('select MAKEDATE(2020, week_num*7-1) as date, affiliation, total_cases, total_deaths from temp2;')
cursor.execute(weekly_cases_query)
weekly_cases=result(cursor)
weekly_cases_df=DataFrame(weekly_cases, columns=['Date','Affiliation','Cases','Deaths'])

weekly_reps=weekly_cases_df[weekly_cases_df['Affiliation']=='R']
weekly_dems=weekly_cases_df[weekly_cases_df['Affiliation']=='D']

weekly_reps['NewCases_Reps']=weekly_reps['Cases'].diff().astype(float)
weekly_dems['NewCases_Dems']=weekly_dems['Cases'].diff().astype(float)

weekly_df=weekly_reps.merge(weekly_dems, on='Date', how='left').drop([36])

if __name__ == "__main__":
    weekly_df.plot(x="Date", y=['NewCases_Reps','NewCases_Dems'], kind="line", figsize=(8,5.5))  
    plt.suptitle('Weekly New Cases Over Time by Affiliation', fontsize=12)
    plt.title('Republican New Cases Overtake Democratic New Cases As Reopening Begins Around the Country', fontsize=8)
    plt.xlabel('Date')
    plt.ylabel('Weekly New Cases (Millions)')
    plt.show() # plot 4

# DEATHS AS PERCENTAGE OF POPULATION BY AFFILIATION

deaths_query=('select date, state, sum(cases) as cases, sum(deaths) as deaths,'
    ' case'
        ' when sum(dem_votes16)>sum(rep_votes16) then "D"'
        ' else "R"'
    ' end as affiliation'
    ' from covid_cases'
    ' join politics on politics.fips=covid_cases.fips'
    ' group by date, covid_cases.state' 
    ' order by date;')
cursor.execute(deaths_query)
deaths=result(cursor)
deaths_df=DataFrame(deaths, columns=['Date','State','#Cases','#Deaths','Affiliation'])

deaths_affil_df=deaths_df.merge(swing_cases_df, on='State', how='left').drop(columns=['Cases','Deaths'])
deaths_affil_df['Affil_Status']=deaths_affil_df['Status'][deaths_affil_df['Status']=='S']
deaths_affil_df["Affil_Status"].fillna(deaths_affil_df['Affiliation'], inplace = True) 

state_pop_query=('select state, sum(population) from demographics group by state;')
cursor.execute(state_pop_query)
state_pops=result(cursor)
state_pop_df=DataFrame(state_pops, columns=['State','Population'])

death_pop_df=deaths_affil_df.merge(state_pop_df, on='State', how='left')
death_pop_df['Deaths_Per_Pop']=(death_pop_df['#Deaths']/death_pop_df['Population']*100).astype(float)

if __name__ == "__main__":
    sns.lineplot(data=death_pop_df, x='Date',y='Deaths_Per_Pop', hue='Affil_Status', ci=None)
    plt.title('Republican Deaths on the Rise as Swing State and Democratic Deaths Taper', fontsize=8)
    plt.suptitle('Deaths As A Percentage of Population Over Time by Political Affiliation', fontsize=12)
    plt.xlabel('Date')
    plt.ylabel('Percentage of the Population that Died due to COVID (%)')
    plt.show() # plot 5

cursor.close()
connection.close() 