# COVID-19 and the Upcoming Election
I analyzed the correlation between COVID cases and deaths in the United States and the political party affiliation of these hotspots.


## Table of Contents

1. [Data Sources](#data-sources)
2. [Covid Statistics](#covid-statistics)
3. [Thesis 1](#thesis-1-the-political-party-associated-with-a-county-is-strongly-correlated-with-the-extent-of-the-covid-outbreak-in-that-county)
4. [Thesis 2](#thesis-2-the-extent-to-which-covid-has-impacted-swing-states-will-impact-the-way-they-vote-in-the-upcoming-presidential-election)
5. [Smaller Data Explorations](#smaller-data-explorations)

---
## Data Sources: 

In main.py, I use CSV reader to import four unrelated data files from Kaggle.com. 

The table covid_cases reports the aggregate number of cases and deaths for each county in the US each day. This data was downloaded from The New York Times, based on reports from state and local health agencies.

The table politics stores data on the votes by county for each political candidate in the 2016 and 2012 elections. I added a table politics_2020 to store the vote date by county for the 2020 election as of November 12th. Both data sources originated from CNN.

The table demographics tracks information like gender breakdown, population, and median age for each US county. Demographic information is based on the most recent 2014-18 release of the Amercian Community Survey. As such, population data might be slightly outdated.

I cleaned the data in this file as well, adding unique county identifier codes called fips to entries that were missing the code so that I could tie the data together.    

---
## COVID Statistics: 

As of November 11, 2020:

    Total Cases: 10,464,484
    Total Deaths: 240,612

I also wanted to explore outliers: counties that either performed very well or very poorly given population size. Since the distribution of COVID cases is not normal, I calculated the percentile for each county and analyzed the counties in the 1st and 99th percentile. 9 counties in Vermont and 6 in Maine qualified to be in the 1st percentile, whereas 8 in North Dakota and 5 in South Dakota had record-high levels of cases given population size in the 99th percentile. 

---

## Thesis 1: The political party associated with a county is strongly correlated with the extent of the COVID outbreak in that county. 

In politics.py, I explored my first theory: There is a correlation between a county's political affiliation and the extent to which it is devastated by COVID-19. 

I found a strong association between Democratic counties and counties with high instances of COVID. After digging into this further, I noticed that these Democratic counties had very large populations and that Republican counties tended to be less dense. In fact, 87 of the largest 100 counties in the US voted Democrat in the 2020 Election. 

Furthermore, the correlation between population and number of COVID cases for Republican counties was 0.96, compared to 0.88 for Democratic counties, showing that Republican counties experience more cases when accounting for differences in population size. 

I wanted to see if there were any changes to this trend as time went on, specifically as the country began to reopen. I noticed that the gap between Democratic and Republican counties' new cases was narrowing starting right around Memorial Day Weekend, likely in connection with reopenings and the ease of restrictions. Republican new cases even surpassed Democratic new cases in September. Furthermore, Republican and swing state deaths are on the rise, as Democratic state deaths begin to flatten. 

**Graphs:**

<div style="text-align: center">
    <img alt="politics_graph1" src="https://user-images.githubusercontent.com/70925521/99011694-adc9e800-251a-11eb-8e22-9c9bb9a6720a.png"/>
    <img alt="politics_graph2" src="https://user-images.githubusercontent.com/70925521/96490603-0e615000-120f-11eb-90f0-3082010d3403.png" />
    <img alt="politics_graph3" src="https://user-images.githubusercontent.com/70925521/99011715-b4f0f600-251a-11eb-87d6-d00ce8102acc.png" />
    <img alt="politics_graph4" src="https://user-images.githubusercontent.com/70925521/99011720-b7ebe680-251a-11eb-8dc9-1bafb57e7936.png" />

</div>

---

## Thesis 2: The extent to which COVID has impacted swing states will impact the way they vote in the upcoming presidential election.

In voter_participation.py, I identified which states, based on the 2016 presidential election, were swing states. 

I then wanted to see how these states were performing amidst the pandemic. In the weeks leading up to the election, swing states had higher cases for population size than non-swing states. 

In particular, I noticed an uptick in cases (accounting for population size) in ______________. My hypothesis is that health issues will be at the forefront of voter concernsthis year and is likely to persuade voters in these states to vote for a Democratic candidate.

Following the election, I wanted to see if my hypothesis was correct. Did states struggling admist the pandemic vote Democratic? The weighted average percentage of the population infected with COVID (weighted by population size) in these swing states was 3.62% in counties that voted for Biden, as opposed to 3.16% in counties that voted for Trump. 

**Graphs:** 

<div style="text-align: center">
    <img alt="swing_graph1" src="https://user-images.githubusercontent.com/70925521/96514232-5beeb480-1231-11eb-8a5a-d5593f8a8f81.png"/>
    <img alt="swing_graph2" src="https://user-images.githubusercontent.com/70925521/99010513-182d5900-2518-11eb-81a3-569f80b7a4d0.png" />
    <img alt="swing_graph3" src="https://user-images.githubusercontent.com/70925521/96487786-2a62f280-120b-11eb-8341-bd92a35ebeee.png" />

</div>

---

### Smaller Data Explorations:

In demographics.py, I mapped out the trends with COVID cases in relation to population, age, and percentage of the population that was female, finding the highest correlation with population unsurprisingly. 

I also explored the theory that the date of the first case impacted the magnitude of the pandemic in a particular county, with counties who had their first case earlier being more likely to experience a heightened breakout. 

**Graphs:** 

<div style="text-align: center">
    <img alt="dem_graph1" src="https://user-images.githubusercontent.com/70925521/96491002-9f382b80-120f-11eb-9645-e75364cb34cc.png"/>
    <img alt="dem_graph2" src="https://user-images.githubusercontent.com/70925521/96489871-094fd100-120e-11eb-88d8-f84ba8fb77dd.png"/>

</div>

In stockgraph.py, I analyzed the correlation between the stock market and the number of new COVID cases. There was a looser correlation than initially predicted. 

**Graphs:** 

<div style="text-align: center">
    <img alt="stocks_graph1" src="https://user-images.githubusercontent.com/70925521/96514263-6610b300-1231-11eb-8c46-761a479c257c.png"/>

</div>

In mortality.py, I calculated the average and total mortality rates across the country and examined to see if there were any outliers. The counties with the highest mortality rates (greater than 15%) had fewer than 500 total cases, and were the counties with comparatively low populations (22,000 average population compared to nationwide average of 101,000). 

I then looked at counties with high mortality rates and high cases per population, and found Georgia had 6 of these outliers and Texas had 4. Overall, however, the outliers with high cases and mortality rates were a mix of Democratic and Republican counties.  

**Graphs:** 
    
<div style="text-align: center">
    <img alt="stocks_graph1" src="https://user-images.githubusercontent.com/70925521/96489879-0b199480-120e-11eb-8f4f-a9525a7393ed.png"/>

</div>

In outliers.py, I investigated the possibility that some counties had higher populations but lower cases, but unfortunately only found one outlier: New York, which had a high number of cases and deaths, even for its population. 

    


