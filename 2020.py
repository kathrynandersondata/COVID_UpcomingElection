from main import * 
from demographics import * 

connection = mysql.connector.connect(user='root', password='dataadmin',
                              host='localhost', database='covidstocks')
cursor=connection.cursor(buffered=True)

# HOW MANY OF THE LARGEST 100 COUNTIES VOTE DEMOCRATIC?
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
print(result(cursor))


cursor.close()
connection.close() 