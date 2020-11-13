from main import * 
from demographics import demo_cases_query
from voter_participation import * 
from sklearn.linear_model import LinearRegression

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

# AVERAGE POPULATION SIZE BY PARTY 
average_pops_query=('select party, avg(pop) as average_pop ' 
' from (select d.county, d.state, population as pop, party ' 
' from politics_2020 p ' 
' join demographics d on d.county=p.county and d.state=p.state ' 
' where won="True") t1 ' 
' group by party ')
cursor.execute(average_pops_query)
average_pops=result(cursor)

# NUMBER OF COUNTIES BY PARTY  
num_counties_query=('select party, avg(pop) as average_pop, count(county) '
' from (select d.county, d.state, population as pop, party' 
' from politics_2020 p ' 
' join demographics d on d.county=p.county and d.state=p.state ' 
' where won="True") t1 ' 
' group by party ')
cursor.execute(num_counties_query)
num_counties=result(cursor)

# FINDING CORRELATION OF CASES AND DEATHS BY PARTY 

rep_query=('select affiliations.fips, cases, deaths, affiliation, population from affiliations '
' join demographics on demographics.fips=affiliations.fips '
'where affiliation="Republican";')
cursor.execute(rep_query)
reps=result(cursor)
reps_df=DataFrame(reps,columns = ['fips','cases','deaths','affiliation', 'population'])

dem_query=('select affiliations.fips, cases, deaths, affiliation, population from affiliations'
' join demographics on demographics.fips=affiliations.fips ' 
'where affiliation="Democrat";')
cursor.execute(dem_query)
dems=result(cursor)
dems_df=DataFrame(dems,columns = ['fips','cases','deaths','affiliation', 'population'])

rep_correl=np.corrcoef(reps_df.cases,reps_df.deaths) #0.90
dem_correl=np.corrcoef(dems_df.cases, dems_df.deaths) #0.88

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

rep_correl2=np.corrcoef(reps_df.population,reps_df.cases) #0.96
dem_correl2=np.corrcoef(dems_df.population, dems_df.cases) #0.88 

# LUNEAR REGRESSION TEST ON POPULATION AND CASES BY PARTY 

clean_reps_df=reps_df[(reps_df['population']<4000000) & (reps_df['cases']<100000)]
clean_dems_df=dems_df[(dems_df['population']<4000000) & (dems_df['cases']<100000)]

clean_df=pop_cases_df[(pop_cases_df['Population']<4000000) & (pop_cases_df['Cases']<100000)]

new_plot=sns.lmplot(data=clean_df, x='Population', y='Cases', hue='Affiliation')
plt.suptitle('The Strong Correlation Between Population and Cases Explains the Strong Correlation Between Democratic Affilition and Cases', fontsize=8)
plt.title('Population and Cases by Affiliation', fontsize=12)
plt.xlabel('Population (Millions)')
plt.ylabel('Cases')
new_plot.fig.set_size_inches(8,8)
if __name__ == "__main__":
    plt.show() # plot 3 

reps_x=clean_reps_df['population'].values.reshape((-1, 1))
reps_y=clean_reps_df['cases']
dems_x=clean_dems_df['population'].values.reshape((-1, 1))
dems_y=clean_dems_df['cases']

reps_model=LinearRegression().fit(reps_x, reps_y)
dems_model=LinearRegression().fit(dems_x, dems_y)

reps_rsq=reps_model.score(reps_x,reps_y)
reps_intercept=reps_model.intercept_ 
reps_slope=reps_model.coef_ 

dems_rsq=dems_model.score(dems_x,dems_y)
dems_intercept=dems_model.intercept_ 
dems_slope=dems_model.coef_ 

print(reps_rsq,reps_slope,dems_rsq,dems_slope)

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

# PLOTTING DAILY NEW CASES OVER TIME BY PARTY

daily_cases_query=('with cte as( '
'select date, covid_cases.county, covid_cases.state, ' 
'case when dem_votes16>rep_votes16 then "D" else "R" end as affiliation, ' 
'cases, lag(cases,1) over (partition by covid_cases.fips order by date) as cases_yesterday ' 
'from covid_cases ' 
'join politics on politics.fips=covid_cases.fips ' 
'order by date desc) '
' select date, affiliation, sum(cases) as total_cases, sum(cases_yesterday) as yesterday_cases, ' 
' sum(cases)-sum(cases_yesterday) as new_cases ' 
' from cte ' 
' group by date, affiliation ')
cursor.execute(daily_cases_query)
daily_cases=result(cursor)
daily_cases_df=DataFrame(daily_cases, columns=['Date','Affiliation','Cases','Yesterday_Cases','New_Cases'])

daily_reps=daily_cases_df[daily_cases_df['Affiliation']=='R']
daily_dems=daily_cases_df[daily_cases_df['Affiliation']=='D']

daily_reps['NewCases_Reps']=daily_reps['New_Cases'].astype(float)
daily_dems['NewCases_Dems']=daily_dems['New_Cases'].astype(float)

daily_df=daily_reps.merge(daily_dems, on='Date', how='left')

if __name__ == "__main__":
    daily_df.plot(x="Date", y=['NewCases_Dems','NewCases_Reps'], kind="line", figsize=(8,5.5))  
    plt.suptitle('Daily New Cases Over Time by Affiliation', fontsize=12)
    plt.title('Republican New Cases Overtake Democratic New Cases As Reopening Begins Around the Country', fontsize=8)
    plt.xlabel('Date')
    plt.ylabel('Daily New Cases')
    plt.show() # plot 3.5 


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
' select week(date) as week_num, affiliation, max(total_cases) as total_cases, max(total_deaths) as total_deaths' 
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
    plt.ylabel('Weekly New Cases')
    plt.xlim('2020-02-01','2020-11-06')
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
    plt.title('Republican and Swing State Deaths on the Rise as Democratic Deaths Taper', fontsize=8)
    plt.suptitle('Deaths As A Percentage of Population Over Time by Political Affiliation', fontsize=12)
    plt.xlabel('Date')
    plt.ylabel('Percentage of the Population that Died due to COVID (%)')
    plt.show() # plot 5

cursor.close()
connection.close() 