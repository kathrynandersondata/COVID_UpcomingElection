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

cursor.close()
connection.close() 