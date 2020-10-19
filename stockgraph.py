from main import *

connection = mysql.connector.connect(user='root', password='dataadmin',
                              host='localhost', database='covidstocks')
cursor=connection.cursor(buffered=True)

# FINDING CORRELATION BETWEEN COVID DATA AND STOCK MARKET 

correl_query = ('select covid_cases.date, sum(cases), sum(deaths), avg(stock_data.close) ' 
    ' from covid_cases ' 
    ' left join stock_data' 
    ' on stock_data.date=covid_cases.date ' 
    ' group by date; ') 
cursor.execute(correl_query)
daily_correl=result(cursor)
daily_correl_df=DataFrame(daily_correl, columns=['Date','Cases','Deaths','S&P500'])
daily_correl_df['NewCases']=daily_correl_df['Cases'].astype('float').diff()
daily_correl_df['NewCases'][daily_correl_df['NewCases']<0]=np.NaN

# CREATE COMBO CHART 
fig, ax1 = plt.subplots(figsize=(10,6))
color = 'green'
# cases line graph 
ax1.set_title('COVID-19 Correlation with Stock Market', fontsize=16)
ax1.set_xlabel('Date', fontsize=16)
ax1.set_ylabel('Daily New COVID Cases (green)', fontsize=16)
ax1=sns.lineplot(x='Date', y='NewCases', data = daily_correl_df.dropna(), sort=False, color=color)
ax1.tick_params(axis='y')
ax2 = ax1.twinx() #specify we want to share the same x-axis
color = 'purple'
# S&P line graph 
ax2.set_ylabel('Share of S&P500 ($) (purple)', fontsize=16)
ax2 = sns.lineplot(x='Date', y='S&P500', data = daily_correl_df.dropna(), sort=False, color=color)
ax2.tick_params(axis='y', color=color)
plt.show()


cursor.close()
connection.close() 