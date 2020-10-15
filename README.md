This project analyzes the correlation between COVID cases and deaths in the United States and the political party affiliation of these hotspots. 

 Data Sources: 

    In main.py, I use CSV reader to import three unrelated data files from Kaggle.com. 
    
    I created a table called covid_cases that reports the number of aggregate cases and deaths for each county in the US each day. 
    
    The table politics stores data on the votes by county for each political candidate in the 2016 and 2012 elections. 
    
    The table demographics tracks information like gender breakdown, population, and median age for each US county. 
    
    I cleaned the data in this file as well, adding unique county identifier codes called fips to entries that were missing the code so that I could tie the data together.    

Thesis 1: The political party associated with a county is strongly correlated with the extent of the COVID outbreak in that county. 

    In politics.py, I explored my first theory: There is a correlation between a county's political affiliation and the extent to which it is devastated by COVID-19. I found a strong correlation amongst Democratic counties and counties with high instances of COVID. After digging into this further, I noticed that these Democratic counties had very large populations and that Republican counties tended to be less dense.

    I wanted to see if there were any changes to this trend as time went on, specifically as the country began to reopen. I noticed that the gap between Democratic and Republican counties' cases was narrowing starting right around Memorial Day Weekend, likely in connection with reopenings and the ease of restrictions. 

    Graphs: 

        1. 

Thesis 2: The extent to which COVID has impacted swing states will impact the way they vote in the upcoming presidential election.

    In voter_participation.py, I identified which states, based on the 2016 presidential election, were swing states. 
    
    I then wanted to see how these states were performing amidst the pandemic. I noticed three states in particular had a disproportionately high number of deaths: Pennsylvania, Michigan, and Florida. My hypothesis is that health issues will be at the forefront this year and is likely to persuade voters to vote for a Democratic candidate. 

    Graphs: 
    
        1. Cases and Deaths for Swing and Non-Swing States

        2. Cases Over Time for Swing and Non-Swing States

        3. Percent of Population Infected Over Time for Swing and Non-Swing States

Smaller Data Explorations:

    In demographics.py, I mapped out the trends with COVID cases in relation to population, age, and percentage of the population that was female, finding the highest correlation with population unsurprisingly. 
    
        Graphs: 
        
            1. Various Factor Influences on COVID Cases and Deaths

            2. First Instance of COVID and Effects on Total Cases

    In stockgraph.py, I analyzed the correlation between the stock market and the number of new COVID cases. 

        Graphs: 

            1. COVID-19 Correlation with Stock Market
    
    In mortality.py, I crunched some numbers regarding mortality rates. 

        Graphs: 
        
            1. 
    
    In outliers.py, I investigated the possibility that some counties had higher populations but lower cases, but unfortunately only found one outlier: New York, which had a high number of cases and deaths, even for its population. 

        Graphs: 

            1. 
    


