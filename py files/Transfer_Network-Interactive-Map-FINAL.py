#!/usr/bin/env python
# coding: utf-8

# In[1]:


## Purpose: Create a network for transfers in the top 9 leagues
## Visualize network 


# In[2]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json 
import math
import networkx as nx
import re


# In[3]:


## import plotly and dash packages
import plotly.graph_objects as go
import dash 
import dash_core_components as dcc
import dash_html_components as html


# In[5]:


pd.__version__


# In[6]:


np.__version__


# In[7]:


json.__version__


# In[8]:


nx.__version__


# In[9]:


re.__version__


# In[10]:


go.__version__


# In[11]:


dash.__version__


# In[13]:


import plotly


# In[14]:


plotly.__version__


# In[4]:


## Tutorials referenced
# https://plotly.com/python/network-graphs/


# In[5]:


## read in transfers dataframe and necessary dictionaries
transfers = pd.read_csv('transfers.csv')

## league info
f = open('league_info.json')
leagues = json.load(f)
f.close()

## team and team codes
f = open('team_dict.json')
teams = json.load(f)
f.close()

## import all_teams json - this holds all coordinates for every team
f = open('all_teams.json')
all_teams = json.load(f)
f.close()


# In[6]:


transfers.head()


# ## Clean transfers df

# In[7]:


## there is some missing data
transfers.info()


# In[8]:


## I was going to clean and use the transfer fee for node size, but there are too many missing values
## so I am just going to drop it
transfers['type'].tail(10)


# In[9]:


## also drop ids - not needed (ones I need are in a dict)
to_drop = ['lastUpdate', 'type',  'team_in_id', 'team_out_id']
transfers = transfers.drop(to_drop, axis = 1)
transfers.head()


# In[10]:


## look at rows with missing player names
transfers.loc[transfers['player_name'].isnull() == True, :]


# In[11]:


## change missing players from null to missing
transfers.loc[transfers['player_name'].isnull() == True, 'player_name'] = 'Missing'


# In[12]:


## deal with missing team names. replace missing with 'Released'
transfers.loc[transfers['team_in_name'].isnull() == True, 'team_in_name'] = 'Released'
transfers.loc[transfers['team_out_name'].isnull() == True, 'team_out_name'] = 'Released'


# In[13]:


## there is no longer missing data
transfers.info()


# ## Create new features

# In[14]:


## change transfer dates to datetime
transfers['transfer_date'] = pd.to_datetime(transfers['transfer_date'])

## grab year, month, day from transfer_date
transfers['year'] = transfers['transfer_date'].apply(lambda x: x.year)
transfers['month'] = transfers['transfer_date'].apply(lambda x: x.month)
transfers['day'] = transfers['transfer_date'].apply(lambda x: x.day)

transfers.head()


# In[15]:


## graph will only have years 2010-2019
transfers = transfers.loc[(transfers['year'] >= 2010) & (transfers['year'] <=2019), :]


# In[16]:


## create edges within dataframe - these will come in handy later
def create_edges(row):
    return (row['team_in_name'], row['team_out_name'])

transfers['edge'] = transfers.apply(lambda row: create_edges(row), axis = 1)
transfers.head()


# In[17]:


transfers.shape


# ## Add colors to league dict

# In[18]:


## add official color for each league from sportsfancovers.com
leagues['Premier League']['color'] = '#3d195b' # purple
leagues['MLS']['color'] = '#001f5b' # blue
leagues['Bundesliga']['color'] = '#d20515' # red
leagues['La Liga']['color'] = '#ee8707' #orange
leagues['Ligue 1']['color'] = '#dae025' #yellow
leagues['Liga Nos']['color'] = '#d3c084' #gold - from portugese national team
leagues['Premier Liga']['color'] = 'black' 
leagues['Serie A']['color'] = '#008fd7' # light blue
leagues['Liga MX']['color'] = '#c1d82f'


# ## Define functions to get node colors

# In[19]:


## Define functions to get node colors for graph

def get_colors(graph):
    cmap = []
    
    global leagues
    global teams
    
    for node in graph.nodes():
        ## get team id from team name
        if node in teams:
            team_id = teams[node]
            
            ## check if node in teams list by looping through all teams in all leagues
            for league in leagues:
                if team_id in leagues[league]['teams']:
                    ## add color to cmap list
                    cmap.append(leagues[league]['color'])
        
        elif node == 'Released':
            cmap.append('green') 
        
        else:
            cmap.append('gray') ## these are teams that are not in our 9 leagues
            
    return cmap


# In[20]:


## create function that will check if team is in edge. This will be used for filtering on the graph
def contains_team(row, team):
    if team in row:
        return True
    else:
        return False


# ## Define Function to Create Graph

# In[21]:


def create_graph(team = None, player = None, year = [None, None], df = transfers):
     ## if team or player is not none, filter
    if team != None:
        df['team_search'] = df['edge'].apply(lambda row: contains_team(row, team))
        df = df.loc[df['team_search'] == True, :]
    if player != None:
        df = df.loc[df['player_name'] == player, :]
    if year[0] != None:
        year_min = year[0]
        year_max = year[1]
        df = df.loc[(df['year'] >= year_min) & (df['year'] <= year_max), :]
#     else:
#         df = transfers.head(1000) ## REMEMBER THIS IS JUST SHOWING 1000
#         #df = transfers
    
    ## create graph
    g = nx.from_pandas_edgelist(df, source = 'team_in_name', target = 'team_out_name', create_using = nx.DiGraph)
    
    return g


# ## Convert Coordinates for all teams

# In[22]:


## define function to convert coordinates from DMS to degrees
def convert_coordinates(lat, lon):
    deg, minutes, seconds, drop, direction = re.split('[°\'"]', lat)
    lat_new = (float(deg) + float(minutes)/60 + float(seconds)/(60*60)) * (-1 if direction.strip() in ['W', 'S'] else 1)
    
    deg, minutes, seconds, drop, direction = re.split('[°\'"]', lon)
    lon_new = (float(deg) + float(minutes)/60 + float(seconds)/(60*60)) * (-1 if direction.strip() in ['W', 'S'] else 1)
    
    all_teams[team]['lat'] = lat_new
    all_teams[team]['lng'] = lon_new


# In[23]:


## call function to convert the coordinates of every team from DMS to degrees
exceptions =  []
for team in all_teams:
    try:
        convert_coordinates(all_teams[team]['lat'], all_teams[team]['lng'])
    except:
        exceptions.append(team)
        pass
exceptions


# ## Handle teams that are out of place

# In[24]:


## Some teams are out of place on the map - fix the coordinates for these
misplaced = ['Juventus', 'Leon', 'Santa Clara', 'Maritimo', 'Belenenses', 'Tenerife', 'Las Palmas', 'Guadeloupe', 'Camacha', 'Minnesota Stars FC']
for name in misplaced:
    for team in all_teams:
        if all_teams[team]['name'] == name:
            print(name + " " + team)


# In[25]:


## Brazilian Juventus
all_teams['10019']['name'] = 'Clube Atletico Juventus'

## Leon - Mexico
all_teams['2289']['lat'] = 21.1250
all_teams['2289']['lng'] = -101.6869

## Belenenses - Portugal
all_teams['221']['lat'] = 38.7088
all_teams['221']['lng'] = -9.2627

## Wexford Youths - 10907
all_teams['10907']['lat'] = 52.3848
all_teams['10907']['lng'] = -6.5006

## Lillestrom - 10894
all_teams['10894']['lat'] = 59.9560
all_teams['10894']['lng'] = 11.0504

## all other teams appear to be correct


# In[26]:


## this is checking to make sure all the nodes are 
# passed = []
# for node in g.nodes():
#     for team in all_teams:
#         if node == all_teams[team]['name']:
#             print(all_teams[team]['lng'], all_teams[team]['lat'])
#             g.nodes[node]['pos'] = list([all_teams[team]['lng'], all_teams[team]['lat']])
    


# ## Define Functions to Create Figure

# In[27]:


def get_title(team = None, player = None, year = [None, None]):
    
    ## get year portion for title
    if year[0] != year[1]:
        year_title = str(year[0]) + "-" + str(year[1])
    else: 
        year_title = str(year[0])
     
    ## get remainder of title. Player portion takes precedent over team
    if player != None:
        title = "Transfers for " + player + ": " + year_title 
    elif team != None:
        title = "Transfers in and out of " + str(team) + ": "  + year_title
    else:
        title = "Transfers in and out of Top 9 Leagues for " + year_title
        
    return title


# In[28]:


def create_fig(G, title, map_type):
    
    ## get layout of nodes
    
    ## if visual is world map - get coordinates
    if map_type == 'world-map':
        ## get layout - coordinates
        for node in G.nodes():
            for team in all_teams:
                if node == all_teams[team]['name']:
                    G.nodes[node]['pos'] = list([all_teams[team]['lng'], all_teams[team]['lat']])
        ## This puts nodes not in all_teams (i.e. "Released") at coordinates (0,0) - way of error handling
        for node in G.nodes():
            try:
                x = G.nodes[node]['pos']
            except:
                if node == 'Minnesota Stars FC':
                    G.nodes[node]['pos'] = [45.1608, -93.2349]
                else:
                    G.nodes[node]['pos'] = [0,0]
    
    ## if visual is networkx - get spring layout points
    else:
        pos = nx.spring_layout(G)
        for node in G.nodes():
            G.nodes[node]['pos'] = list(pos[node])
      
    ## get edges (transfers) and nodes (teams) as scatter traces
    edge_x = []
    edge_y = []

    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
    
    if map_type == 'world-map':
        edge_trace = go.Scattergeo(lon = edge_x, lat = edge_y, mode = 'lines',
                           line = dict(width = 0.5, color = 'black'),
                           hoverinfo = None,
                            opacity = 0.35)
    else:
        edge_trace = go.Scatter(x = edge_x, y = edge_y,
                           line = dict(width = 0.5, color = 'black'),
                           hoverinfo = None,
                            opacity = 0.35)

    #edge_trace.line.width = edge_widths

    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)
        node_text.append(node) # on hover will display team
    
    node_colors = get_colors(G) ## get node colors
    
    if map_type == 'world-map':
        node_trace = go.Scattergeo( 
        lon = node_x, lat = node_y, 
        mode = 'markers', 
        hoverinfo = 'text',
        marker = dict(
            color = node_colors,
            showscale = False
            ))
    else:
        node_trace = go.Scatter(
            x = node_x, y = node_y, 
            mode = 'markers', 
            hoverinfo = 'text',
            marker = dict(
                color = node_colors,
                showscale = False
                ))
        
    node_trace.text = node_text

    ## scale node size by number of connections
    node_sizes = []

    for node, adjacencies in enumerate(G.adjacency()):
        node_sizes.append(len(adjacencies[1]))
        
    a = 10 # min node size after scaling
    b = 20 # max node size after scaling
    node_sizes_scaled = []

    min_nodes = min(node_sizes)
    max_nodes = max(node_sizes)
    
    node_sizes_scaled = [(((b-a) * (x - min_nodes))/(max_nodes - min_nodes)) + a for x in node_sizes]

    node_trace.marker.size = node_sizes_scaled
    
    ## create figure
    fig = go.Figure(data = [edge_trace, node_trace],
               layout = go.Layout(
                   title = title,
                   showlegend = False,
                   hovermode = 'closest',
                   xaxis = dict(showgrid = False, zeroline = False, showticklabels = False),
                   yaxis = dict(showgrid = False, zeroline = False, showticklabels = False),
                   margin = dict(b = 20, l = 5, r = 5, t = 40)))
    
    return fig


# ## Define functions for player and team dropdowns

# In[29]:


## def get team dropdown - this will change when filtered for player or year 

def get_team_dd(player = None, year = [None, None], df = transfers):
    ## filter df
    if player != None:
        df = df.loc[df['player_name'] == player, :]
    if year[0] != None:
        year_min = year[0]
        year_max = year[1]
        df = df.loc[(df['year'] >= year_min) & (df['year'] <= year_max), :]
    ## get list of unique teams in the filtered df
    team_list = df['team_in_name'].append(df['team_out_name'])
    teams_unique = team_list.unique()
    team_dd = []
    for team in teams_unique:
        options =  {}
        options['label'] = team
        options['value'] = team
        team_dd.append(options)
    team_dd = sorted(team_dd, key = lambda i: i['label'])
    return team_dd


# In[30]:


## def function to get the player dropdown list - this will change when filtered for team or year

def get_player_dd(team = None, year = [None, None], df = transfers):
    ## filter df
    if team != None:
        df['team_search'] = df['edge'].apply(lambda row: contains_team(row, team))
        df = df.loc[df['team_search'] == True, :]
    if year[0] != None:
        year_min = year[0]
        year_max = year[1]
        df = df.loc[(df['year'] >= year_min) & (df['year'] <= year_max), :]
        
    ## get list of unique players
    players_unique = df['player_name'].unique()
    player_dd = []
    
    for player in players_unique:
        options = {}
        options['label'] = player
        options['value'] = player
        player_dd.append(options)
    
    player_dd = sorted(player_dd, key = lambda i: i['label'])
    return player_dd


# ## Put graph on dash

# In[ ]:


app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1(
      children = 'The Transfer Network', 
        style = {
            'textAlign': 'Center'
        }
    ),
    html.Div(
        children = 'A visualization of the global movement of soccer players',
        style = {
            'textAlign': 'center'
        }
    ),
    
    html.Div([
        dcc.Dropdown(
            id = 'player-dropdown',
            #options = player_options,
            value = None,
            placeholder = "Start typing to select a player"
        ),
      
        html.Div(id = 'pd-output-container') 
    ]),
    html.Div([
        dcc.Dropdown(
            id = 'team-dropdown',
            #options = team_options,
            value = None,
            placeholder = "Start typing to select a team"
        ),
        html.Div(id = 'td-output-container')
    ]),
    html.Div(
        children = 'Select year(s) of interest. (A player will not show up in dropdown unless they were transferred within the range of years)'
    ),
    html.Div([
        dcc.RangeSlider(
        id = 'year-range-slider',
        min = transfers['year'].min(),
        max = transfers['year'].max(),
        value = [2010, 2010],
        marks = {str(year): str(year) for year in transfers['year'].unique()},
        step = None),
        html.Div(id = 'output-container-range-slider')
    ]),
    html.Div(
        children = 'Show visual as:'
    ),
    html.Div([
        dcc.RadioItems(
        id = 'radio-type-selector', 
        options = [
            {'label': 'NetworkX Graph', 'value': 'nx-graph'},
            {'label': 'World Map', 'value': 'world-map'}
        ],
        value = 'world-map'
        )
    ]),
    html.Div([
        dcc.Graph(id = 'transfers-network')
    ]),
    html.Footer(
        children = 'No legend? Due to the way I created node colors and how plotly legends function, I was unable to add a legend to match leagues and colors.'
    ),
    html.Label(
        ['View source code on my ', html.A('Github', href = 'https://github.com/')]
    )
])


## Update graph 
@app.callback(
    dash.dependencies.Output('transfers-network', 'figure'),
    [dash.dependencies.Input('team-dropdown', 'value'),
    dash.dependencies.Input('player-dropdown', 'value'),
    dash.dependencies.Input('year-range-slider', 'value'),
    dash.dependencies.Input('radio-type-selector', 'value')])
def update_fig(team_value, player_value, year_value, radio_value):
    g = create_graph(team = team_value, player = player_value, year = year_value)
    title = get_title(team = team_value, player = player_value, year = year_value)
    fig = create_fig(g, title, map_type = radio_value)
    return fig

@app.callback(
    dash.dependencies.Output('player-dropdown', 'options'),
    [dash.dependencies.Input('team-dropdown', 'value'),
    dash.dependencies.Input('year-range-slider', 'value')])
def update_player_dd(team_value, year_value):
    player_dd = get_player_dd(team = team_value, year = year_value)
    return player_dd

@app.callback(
    dash.dependencies.Output('team-dropdown', 'options'),
    [dash.dependencies.Input('player-dropdown', 'value'),
    dash.dependencies.Input('year-range-slider', 'value')])
def update_team_dd(player_value, year_value):
    team_dd = get_team_dd(player = player_value, year = year_value)
    return team_dd


if __name__ == '__main__':
    app.run_server(debug = False)


# In[ ]:




