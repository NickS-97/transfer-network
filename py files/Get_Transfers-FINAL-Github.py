#!/usr/bin/env python
# coding: utf-8

# In[1]:


## Purpose: Download transfers for the 9 leagues from the football API. Transfers from:
## EPL, MLS, Bundesliga, La Liga, Ligue 1, Liga MX, Liga Nos, Premier Liga, Serie A


# In[2]:


import pandas as pd
import numpy as np
import requests


# ## Set up API Info

# In[3]:


headers = {
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
    'x-rapidapi-key': ""
    }


# In[4]:


## initialize nested dictionary to hold each league, league id, and list of teams
## color will be used for visual purposes. Add later
league_info = {
    'Premier League': {
        'teams': '',
        'code': '',
        'country': '',
        'color': ''
    },
    'MLS': {
        'teams': '',
        'code': '',
        'country': '',
        'color': ''
    },
    'Bundesliga': {
        'teams': '',
        'code': '',
        'country': '',
        'color': ''
    },
    'La Liga': {
        'teams': '',
        'code': '',
        'country': '',
        'color': ''
    },
    'Ligue 1': {
        'teams': '',
        'code': '',
        'country': '',
        'color': ''
    },
    'Liga MX': {
        'teams': '',
        'code': '',
        'country': '',
        'color': ''
    },
    'Liga Nos': { ## also known as Premeira Liga - Portugal
        'teams': '',
        'code': '',
        'country': '',
        'color': ''
    },
    'Premier Liga': {
        'teams': '',
        'code': '',
        'country': '',
        'color': ''
    },
    'Serie A': {
        'teams': '',
        'code': '',
        'country': '',
        'color': ''
    },
    
}


# ## Create functions to get league ids, team ids, and transfers

# In[5]:


## Function 1: Get league ids from country
## Easiest to just print out a list and manuall add the leagues to nested dictionary
def get_leagues(countries):
    
    for country in countries:
        url = "https://api-football-v1.p.rapidapi.com/v2/leagues/country/" + str(country) + '/2020'
        response = requests.request("GET", url, headers=headers)
        obj = response.json()
        leagues = obj['api']['leagues']
        
        print(country)
        
        for league in leagues:
            print(str(league['league_id']) + ' ' + str(league['name'])) 
            
        print('\n')


# In[7]:


## Get leagues from 9 countries of interest
get_leagues(['Mexico', 'England', 'France', 'Germany', 'Portugal', 'USA', 'Russia', 'Spain', 'Italy' ])


# In[8]:


## add top flight league info to dictionary
league_info['Liga MX']['code'] = 2656
league_info['Liga MX']['country'] = 'Mexico'

league_info['MLS']['code'] = 1264
league_info['MLS']['country'] = 'United States'

league_info['Premier League']['code'] = 2790
league_info['Premier League']['country'] = 'England'

league_info['Bundesliga']['code'] = 2755
league_info['Bundesliga']['country'] = 'Germany'

league_info['Ligue 1']['code'] = 2664
league_info['Ligue 1']['country'] = 'France'

league_info['Liga Nos']['code'] = 2826
league_info['Liga Nos']['country'] = 'Portugal'

league_info['Premier Liga']['code'] = 2679
league_info['Premier Liga']['country'] = 'Russia'

league_info['La Liga']['code'] = 2833
league_info['La Liga']['country'] = 'Spain'

league_info['Serie A']['code'] = 2857
league_info['Serie A']['country'] = 'Italy'

league_info


# In[9]:


## Function 2: Get list of teams from league id. Create a dictionary to keep the teams and their ids in
team_dict = {}

def get_teams(league):
    league_id = league_info[league]['code']
    
    url = "https://api-football-v1.p.rapidapi.com/v2/teams/league/" + str(league_id)
    response = requests.request("GET", url, headers=headers)
    obj = response.json()
    
    teams = obj['api']['teams']
    
    ## create a list of team_ids to add to the league_info dict
    team_ids = []
    for team in teams:
        team_ids.append(team['team_id'])
        
        ## add each team and id to team_dict
        team_dict[team['name']]  = team['team_id'] 
        #team_dict[str(team['team_id'])] = team_dict[team['name']]
    
    ## add teams to leagues
    league_info[league]['teams'] = team_ids

    return teams


# In[10]:


for key in league_info.keys():
    get_teams(key)


# In[13]:


## Function 3: Get transfers from team id

def get_transfers(team_ids):
    
    df = pd.DataFrame()
    
    for team_id in team_ids:
        url = "https://api-football-v1.p.rapidapi.com/v2/transfers/team/" + str(team_id)
        response = requests.request("GET", url, headers=headers)
        obj = response.json()
        transfers = obj['api']['transfers']
        df = df.append(transfers)

    return df


# In[14]:


## create dataframe of transfers
transfers = pd.DataFrame()
for key in league_info.keys():
    print(league_info[key]['teams'])
    transfers = transfers.append(get_transfers(league_info[key]['teams']))

## undo nested dictionaries
transfers['team_in_id'] = transfers['team_in'].apply(lambda x: x['team_id'])
transfers['team_in_name'] = transfers['team_in'].apply(lambda x: x['team_name'])
transfers['team_out_id'] = transfers['team_out'].apply(lambda x: x['team_id'])
transfers['team_out_name'] = transfers['team_out'].apply(lambda x: x['team_name'])
transfers = transfers.drop(['team_in', 'team_out'], axis = 1)


# In[15]:


transfers


# In[16]:


## save transfers df to csv
#transfers.to_csv('transfers.csv', index = False)


# In[20]:


## serialize dictionaries as json files and save to use later
import json

with open('league_info.json', 'w') as outfile:
    #json.dump(league_info, outfile, indent = 4)
    
with open('team_dict.json', 'w') as outfile:
    #json.dump(team_dict, outfile, indent = 4)

