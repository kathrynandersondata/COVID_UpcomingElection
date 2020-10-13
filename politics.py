from main import * 
from demographics import * 

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

sns.lmplot(data=affiliation_df, x='cases', y='deaths', hue='affiliation')
#plt.show()

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

sns.jointplot(data=affil_mort_df, x='Cases', y='Mortality', hue='Affiliation')
#plt.show()

# PLOTTING POPULATION AND CASES BY PARTY

pop_cases_query=('select demographics.fips, cases, deaths, population, affiliations.affiliation as affiliation'
    ' from demographics ' 
    ' inner join affiliations on affiliations.fips=demographics.fips ' 
    ' where population < 5000000;')
cursor.execute(pop_cases_query)
pop_cases=result(cursor)
pop_cases_df=DataFrame(pop_cases, columns=['Fips','Cases','Deaths','Population','Affiliation'])

sns.lmplot(data=pop_cases_df, x='Population', y='Cases', hue='Affiliation')
#plt.show()

# finding cases/population by party 

cases_per_pop_query=('select affiliations.affiliation as affiliation, sum(cases), sum(deaths), sum(population),  ' 
    ' avg(cases/population) as cases_per_pop from demographics ' 
    ' inner join affiliations on affiliations.fips=demographics.fips ' 
    ' group by affiliation; ')
cursor.execute(cases_per_pop_query)
cases_per_pop=result(cursor)
cases_per_pop_df=DataFrame(cases_per_pop, columns=['Affiliation', 'Total_Cases','Total_Deaths','Total_Population','Avg_Cases_Per_Pop'])
# returns 2.5% cases/population for Democrats, 2.0% cases/population for Republicans 

# PLOTTING NEW CASES OVER TIME BY PARTY

new_cases_party_query=('create temporary table cases_by_party' 
    ' select date, case when dem_votes16>rep_votes16 then "D" else "R" end as affiliation,' 
    ' sum(cases) as total_cases, sum(deaths) as total_deaths' 
    ' from covid_cases' 
    ' join politics on politics.fips=covid_cases.fips' 
    ' group by date, affiliation' 
    ' order by date;')
cursor.execute(new_cases_party_query)
new_cases_party_query2=('select * from cases_by_party;')
cursor.execute(new_cases_party_query2)
new_cases_party=result(cursor)
new_cases_party_df=DataFrame(new_cases_party, columns=['Date','Affiliation','Total_Cases','Total_Deaths'])

# democrat df 
dem_newcases_query=('select * from cases_by_party where affiliation="D";')
cursor.execute(dem_newcases_query)
dem_newcases=result(cursor)
dem_newcases_df=DataFrame(dem_newcases, columns=['Date','Affiliation','Total_Cases','Total_Deaths'])
dem_newcases_df['New_Cases'] = dem_newcases_df.Total_Cases.diff()
dem_newcases_df['New_Deaths'] = dem_newcases_df.Total_Deaths.diff()

# republican df 
rep_newcases_query=('select * from cases_by_party where affiliation="R";')
cursor.execute(rep_newcases_query)
rep_newcases=result(cursor)
rep_newcases_df=DataFrame(rep_newcases, columns=['Date','Affiliation','Total_Cases','Total_Deaths'])
rep_newcases_df['New_Cases'] = rep_newcases_df.Total_Cases.diff()
rep_newcases_df['New_Deaths'] = rep_newcases_df.Total_Deaths.diff()

# combined df 
combined_newcases=DataFrame(dem_newcases_df['Date'], columns=['Date'])
combined_newcases['Dem_Cases'] = dem_newcases_df['New_Cases']
combined_newcases['Dem_Deaths']=dem_newcases_df['New_Deaths']

newcases=combined_newcases.merge(rep_newcases_df, on='Date', how='left')
newcases_df=newcases.drop(columns=['Affiliation','Total_Cases','Total_Deaths'])
newcases_df=newcases_df.rename(columns={'New_Cases':'Rep_Cases', 'New_Deaths':'Rep_Deaths'})

newcases_df['Dem_Cases']=newcases_df['Dem_Cases'].astype(float)
newcases_df['Dem_Deaths']=newcases_df['Dem_Deaths'].astype(float)
newcases_df['Rep_Cases']=newcases_df['Rep_Cases'].astype(float)
newcases_df['Rep_Deaths']=newcases_df['Rep_Deaths'].astype(float)

newcases_df['Perc_Dem_Cases']=newcases_df['Dem_Cases']/(newcases_df['Rep_Cases']+newcases_df['Dem_Cases'])
newcases_df['Perc_Rep_Cases']=newcases_df['Rep_Cases']/(newcases_df['Rep_Cases']+newcases_df['Dem_Cases'])

newcases_df.plot(x="Date", y=["Perc_Dem_Cases", "Perc_Rep_Cases"], kind="line", ylim=[0,1])
if __name__ == "__main__":
    plt.show()

cursor.close()
connection.close() 