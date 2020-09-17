# transfer-network
Visualization of the global movement of soccer players using plotly and dash.
The purpose of this project was to learn how to use dash and plotly, and get some experience with the networkx package, which I was introduced to in a Coursera course. 
This was actually going to be part 2 in a 2 part project using the Football-API. The first part was an attempt at creating a machine learning model to predict market values. Unfortunately, the model did not turn out how I intended.
I made this project my main focus. While I was not able to add all the features I had planned, I am happy with the result, considering it was my first attempt using some of these packages. 

Breakdown of work:

"Get_Transfers"
The first notebook in this project is "Get_Transfers." In this notebook I made calls to the API to first get the leagues in a specific country.  I was interested in 9 leagues specifically: Premier League, MLS, Bundesliga, La Liga, Ligue 1, Liga MX, Liga Nos, Premier Liga, and Serie A. I then called the API to get all the teams (by team code) for these leagues for the 2020-21 season. 
I then created a function that allowed me to loop through all these teams and get team (club) transfers, both in and out. This gave me a dataframe consisting of players, the date of their transfer, the club from, and the club to. Players show up multiple times indicating multiple tranfers. The total dataframe contained roughly 60k rows.

An important note: every instance in the dataframe involves a club from one of the 9 leagues specified, but can also include a club from another league or country. For example, Man City could buy a player from Brazil, which would show up in the dataframe. However, because the Brazilian league was not one of the 9 leagues I searched, transfers within the Brazilian league are not included in the dataset. 

"Get_all_teams"
In this notebook I create a list of all the unique teams in the dataset. There are over 2500. I then call the Football-API for each club to get the club's venue, address, city, and country. Some clubs had all this information, some had none. I then used another API for geocoding. I passed in the location data to return coordinates for the club in DMS format. I used multiple try/except calls to handle the clubs that were missing specific location info. 
I ran out of API calls for the geocoding api, and so had to save the list of teams that were passed and I reran them the next day.

"Interactive-Map"
This is the final notebook for the project. In this notebook I start by cleaning the data, and I decided the project would only look at transfers between 2010 and 2019. There was still about 50k instances in the dataframe. 
Throughout the notebook I create multiple functions to make the plotly/dash graph interactive, and that allow for filtering the data. The functions include matching location data from the dictionary to the teams in the dataframe. I could have done this project without using networkx, but that is something I am trying to learn more about, so I made it a main point of this project. However, I did not utilize any of its analysis capabilities to look at most important nodes - perhaps a future version. 

Limitations
Because of the way I created the nodes in the graph, I was unable to add a legend to specify the colors for each league. Additionally, I found it difficult to allow the user to click on a team for more information. 


Future Work
If I return to this project in the future I would like to add player names to edges, so that users could see which player was transferred from team A to team B. I would also like to allow the user to click on a node and see a df of all the players linked to that team.

If you have any feedback or comments on my code/project, please reach out.