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

p3=sns.lmplot(data=demo_cases_df, x='Population', y='Cases') 
plt.title('Population and Cases', fontsize=12)
plt.suptitle('New York City Has an Exorbitantly High Rate of Cases, Even Given Population', fontsize=8)
plt.xlabel('Population')
plt.ylabel('COVID Cases')
plt.ticklabel_format(style='plain')
p3.fig.set_size_inches(8,8)
if __name__ == "__main__":
    plt.show() # plot 1 

cursor.execute(demo_cases_query) # recreates temp table that matches cases with demo info 
poor_perf_query=('select * from fips_table where cases>250000 and population<2000000;')
cursor.execute(poor_perf_query)
poor_perf=result(cursor) # returns New York City 

cursor.close()
connection.close() 