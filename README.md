# COVID-19 and the Upcoming Election

Using four unique datasets from Kaggle.com, I analyzed the association between political party and the number of COVID cases by US county. I also explored the hypothesis that counties experiencing upticks in COVID cases would vote a particular way in swing states by predicting using 2016 election data and comparing results to the 2020 election data. 


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

Total Cases: <strong>10,464,484</strong>
Total Deaths: <strong>240,612</strong>

The counties with the most cases include Los Angeles (CA), New York (NY), Cook (IL), Miami-Dade (FL), Harris (TX), and Maricopa (AZ), each with more than 170,000 cases. These counties are also the ones experiencing the highest death counts, with the notable addition of Wayne (MI), who ranks 6th for deaths even though they are ranked 25th for case counts. 

I also wanted to explore outliers: counties that either performed very well or very poorly given population size. Since the distribution of COVID cases is not normal, I calculated the percentile for each county and analyzed the counties in the 1st and 99th percentile. 9 counties in Vermont and 6 in Maine qualified to be in the 1st percentile, whereas 8 in North Dakota and 5 in South Dakota had record-high levels of cases given population size in the 99th percentile. 

---

## Thesis 1: The political party associated with a county is strongly correlated with the extent of the COVID outbreak in that county. 

In politics.py, I explored my first theory: There is a correlation between a county's political affiliation and the extent to which it is devastated by COVID-19. 

I found a strong association between Democratic counties and counties with high instances of COVID. I noticed the median number of cases for Democratic counties was 2240 cases compared to just 686 cases for Republican ones, and the difference was much more stark when analyzing averages (11,415 versus 1,799). 

After digging into this further, I noticed that these Democratic counties had very large populations and that Republican counties tended to be less dense. In fact, 87 of the largest 100 counties in the US voted Democrat in the 2020 Election, and the average size of a Democratic county is more than 7 times the size of the average Republican county. However, 82% of counties are Republican.

I decided to run a linear regression analysis using SciKit Learn. I started by removing outliers that would skew the regression results, so limited my population size to under 4 million and my case count to under 100,000. I then assessed the correlation between population size and case count for both Democratic and Republican counties. Unsurprisingly, both experienced an incredibly strong correlation, with Republican counties showing a 0.86 correlation and Democratic counties having a 0.82 correlation. This shows that the relationship is stronger in Republican counties between population size and case counts, while there is slightly more variance in Democratic counties. 

The slope of the best-fit line was slightly different among the populations, with Republican counties at 0.033 and Democratic counties at 0.028. Statistically, this means that for every additional 1,000 people in a county, the county will see an increase of 33 and 28 cases, respectively. 

I wanted to see if there were any changes to this trend as time went on, specifically as the country began to reopen. I noticed that the gap between Democratic and Republican counties' new cases was narrowing starting right around Memorial Day Weekend, likely in connection with reopenings and the ease of restrictions. Republican new cases even surpassed Democratic new cases in September. Furthermore, Republican and swing state deaths are on the rise, as Democratic state deaths begin to flatten. 

**Graphs:**

<div style="text-align: center">
    <img alt="politics_graph1" src="https://user-images.githubusercontent.com/70925521/99011694-adc9e800-251a-11eb-8e22-9c9bb9a6720a.png"/>
    <img alt="politics_graph2" src="https://user-images.githubusercontent.com/70925521/99114098-4b2a2800-25be-11eb-8994-63969170034f.png" />
    <img alt="politics_graph3" src="https://user-images.githubusercontent.com/70925521/99011715-b4f0f600-251a-11eb-87d6-d00ce8102acc.png" />
    <img alt="politics_graph4" src="https://user-images.githubusercontent.com/70925521/99011720-b7ebe680-251a-11eb-8dc9-1bafb57e7936.png" />

</div>

---

## Thesis 2: The extent to which COVID has impacted swing states will impact the way they vote in the upcoming presidential election.

In voter_participation.py, I identified which states, based on the 2016 presidential election, were swing states. 

I then wanted to see how these states were performing amidst the pandemic. In the weeks leading up to the election, swing states had higher cases for population size than non-swing states. In addition, every swing state was experiencing major increases in cases, with the notable exception of Maine. 

In particular, I noticed an uptick in cases (accounting for population size) in Iowa, Wisconsin, and Florida. My hypothesis was that health issues would be at the forefront of voter concerns this year and was likely to persuade voters in these states to vote for a Democratic candidate.

Following the election, I wanted to see if my hypothesis was correct. Did states struggling admist the pandemic vote Democratic? 

The third plot shows that 8 of the 13 swing states cast their votes for Biden. 

On a county level, the weighted average percentage of the population infected with COVID (weighted by population size) in these swing states was 3.62% in counties that voted for Biden, as opposed to 3.16% in counties that voted for Trump. As a whole, counties in swing states that experienced higher levels voted for Biden, but there were a few exceptions to that rule. 

On a nationwide level for all states, the difference between infection rates was more pronounced and the the highest parties were <i>reversed</i>: Republican counties had a higher infection rate of 3.75% while Democrat ones had 2.91%. However, this is less significant since COVID case rates are less likely to predict outcomes for states who are historically strong Democratic or Republican counties. 

So what ensured the win for Biden: county conversion or increased voter turnout in Hillary's 2016 counties? Out of the 1100 counties in swing states this year, only 19 switched their vote from Republican to Democrat, and 12 switched from Democrat to Republican. However, votes for Democrats increased by 6.5 million, compared to only 5.5 million for the Republicans. Voter turnout reached record high levels across the nation as well, with 16.2 million more citizens casting votes for Biden than Clinton and 11.8 million more votes for Trump. 

**Graphs:** 

<div style="text-align: center">
    <img alt="swing_graph2" src="https://user-images.githubusercontent.com/70925521/99010513-182d5900-2518-11eb-81a3-569f80b7a4d0.png" />
    <img alt="swing_graph3" src="https://user-images.githubusercontent.com/70925521/99027784-0d84bb00-253c-11eb-8616-f0a3e049ad8d.png" />
    <img alt="barplot" src="https://user-images.githubusercontent.com/70925521/99127969-9866c380-25d7-11eb-93c3-b3d3ac012698.png" />

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


    


