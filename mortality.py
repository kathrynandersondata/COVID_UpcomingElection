from main import *

connection = mysql.connector.connect(user='root', password='dataadmin',
                              host='localhost', database='covidstocks')
cursor=connection.cursor(buffered=True)

# DETERMINING OVERALL MORTALITY RATE 


cursor.close()
connection.close() 