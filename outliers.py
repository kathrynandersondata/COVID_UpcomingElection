from main import *
from demographics import *

connection = mysql.connector.connect(user='root', password='dataadmin',
                              host='localhost', database='covidstocks')
cursor=connection.cursor(buffered=True)

# CLEANING DATA 
cursor.execute(nyc_update_query) # adds NYC fips 
remove_unknown_query=('delete from covid_cases where county="Unknown";')
cursor.execute(remove_unknown_query) # removes unknowns 

# DETERMINING OUTLIERS IN CASES PER POPULATION 

sns.lmplot(data=demo_cases_df, x='Population', y='Cases') 
if __name__ == "__main__":
    plt.show()

cursor.execute(demo_cases_query) # recreates temp table that matches cases with demo info 
poor_perf_query=('select * from fips_table where cases>250000 and population<2000000;')
cursor.execute(poor_perf_query)
poor_perf=result(cursor) # returns New York City 

cursor.close()
connection.close() 