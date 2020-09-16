#!/usr/bin/env python
# coding: utf-8

# In[1]:


## Purpose: Get location info for all teams in the transfers dataset. Collecting this data was not the original plan, but instead
## of changing the get_teams() function and teams_dict(), for the sake of not messing up my code I will create a new function and dictionary.
## It is not ideal and leads to having the same data multiple times, but it is the easiest thing to do for now.


# In[2]:


import pandas as pd
import numpy as np
import requests


# In[3]:


## read in transfers df
df = pd.read_csv('transfers.csv')
df.head()


# In[4]:


## get a series of all unique team ids. Need to change these from floats to int and then str
team_ids = df['team_in_id'].append(df['team_out_id'])
teams_unique = team_ids.unique()
teams_unique = teams_unique.astype(int)
teams_unique = teams_unique.astype(str)
teams_unique = list(teams_unique)


# ## Define function to get team info from id

# In[5]:


headers = {
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
    'x-rapidapi-key': ""
    }


# In[6]:


df.info()


# In[7]:


## reminder that null ids are considered 'released'
df.loc[df['team_in_id'].isnull() == True, :]


# In[8]:


all_teams = {}

def get_team_info(team_id):
    team = {}
    url = "https://api-football-v1.p.rapidapi.com/v2/teams/team/" + str(team_id)
    response = requests.request("GET", url, headers = headers)
    
    obj = response.json()
    info = obj['api']['teams'][0]
    
    name = info['name']
    country = info['country']
    venue = info['venue_name']
    address = info['venue_address']
    city = info['venue_city']
    
    team = {
        'name': name,
        'country': country,
        'city': city,
        'venue': venue,
        'address': address
    }
    
    return team


# In[9]:


## COMMENT OUT TO NOT RERUN

# ## get info for all teams
# passed = []
# for team in teams_unique:
#     try:
#         info = get_team_info(team)
#         all_teams[team] = info
#     except:
#         passed.append(team)
#         pass
    
# all_teams


# ## Define function to get lat and lng from address, city, country

# In[11]:


##opencage api info

geocode_key = ''
url = "https://opencage-geocoder.p.rapidapi.com/geocode/v1/json"
headers = {
    'x-rapidapi-host': "opencage-geocoder.p.rapidapi.com",
    'x-rapidapi-key': ""
    }


# In[42]:


def get_coordinates(team):
    try:
        search = all_teams[team]['address'] + ", " + all_teams[team]['city'] + ", " + all_teams[team]['country']
        querystring = {"language":"en","key":geocode_key,"q":search}
    
        response = requests.request("GET", url, headers=headers, params=querystring)
        obj = response.json()
        result = obj['results'][0] ## take first result
        lat = result['annotations']['DMS']['lat']
        lng = result['annotations']['DMS']['lng']

        all_teams[team]['lat'] = lat
        all_teams[team]['lng'] = lng
    except:
        try:
            search = all_teams[team]['venue']
            querystring = {"language":"en","key":geocode_key,"q":search}

            response = requests.request("GET", url, headers=headers, params=querystring)
            obj = response.json()
            result = obj['results'][0] ## take first result
            lat = result['annotations']['DMS']['lat']
            lng = result['annotations']['DMS']['lng']

            all_teams[team]['lat'] = lat
            all_teams[team]['lng'] = lng
        except:
            try: 
                search = all_teams[team]['venue'] + ", " + all_teams[team]['country']
                querystring = {"language":"en","key":geocode_key,"q":search}

                response = requests.request("GET", url, headers=headers, params=querystring)
                obj = response.json()
                result = obj['results'][0] ## take first result
                lat = result['annotations']['DMS']['lat']
                lng = result['annotations']['DMS']['lng']

                all_teams[team]['lat'] = lat
                all_teams[team]['lng'] = lng
            except:
                try:
                    search = all_teams[team]['city']
                    querystring = {"language":"en","key":geocode_key,"q":search}

                    response = requests.request("GET", url, headers=headers, params=querystring)
                    obj = response.json()
                    result = obj['results'][0] ## take first result
                    lat = result['annotations']['DMS']['lat']
                    lng = result['annotations']['DMS']['lng']

                    all_teams[team]['lat'] = lat
                    all_teams[team]['lng'] = lng
                except:
                    try:
                        search = all_teams[team]['country']
                        querystring = {"language":"en","key":geocode_key,"q":search}

                        response = requests.request("GET", url, headers=headers, params=querystring)
                        obj = response.json()
                        result = obj['results'][0] ## take first result
                        lat = result['annotations']['DMS']['lat']
                        lng = result['annotations']['DMS']['lng']

                        all_teams[team]['lat'] = lat
                        all_teams[team]['lng'] = lng
                    except:
                        passed2.append(team)
                        pass


# In[ ]:


## get coordinates for all teams

## COMMENT OUT AS THIS HAS ALREADY RUN
# passed2 = []
# for team in all_teams:
#     get_coordinates(team)


# In[ ]:


#passed2


# In[ ]:


#len(passed2)


# In[ ]:


## save all passed2 teams to run again tomorrow
## save all_teams as json

# import json
# with open('all_teams.json', 'w') as outfile:
#     json.dump(all_teams, outfile, indent = 4)
    
# with open('passed_on_coordinates.txt', 'w') as outfile:
#     outfile.write(str(passed2))


# ## Read in the teams that were passed and rerun the function - they were passed due to api limits

# In[13]:


import ast

## read to list of teams to rerun in as a nested file
rerun_nested = []
with open("passed_on_coordinates.txt", "r") as f:
    rerun_nested.append(ast.literal_eval(f.read()))
    
f.close()

rerun = rerun_nested[0]


# In[15]:


import json
## read in all_teams file that has been saved
f = open('all_teams.json')
all_teams = json.load(f)
f.close()


# In[18]:


## loop through file and call the function. Use passed2 again for teams that are passed on
passed2 = []
# for team in rerun:
#     get_coordinates(team)


# In[ ]:


rerun2 = passed2


# In[47]:


passed2 = []
for team in rerun2:
    get_coordinates(team)


# In[48]:


passed2


# In[51]:


## there are now only two teams without coordinates - save the rest to all_teams file
with open('all_teams.json', 'w') as outfile:
#     json.dump(all_teams, outfile, indent = 4)

