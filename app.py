# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
#import libs
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlalchemy
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np

stylesheet = ['./main.css']
#App define
app = dash.Dash(__name__,external_stylesheets=stylesheet)

# creating the sqlalchemy engine connection to the database
engine = sqlalchemy.create_engine("mariadb+mariadbconnector://root:12345678@127.0.0.1:3306/ipl_analysis")

#   5.1. For each team you need to give the stadium name(venue) where that team have won the maximum match?
df = pd.read_sql("select * from matches",engine)
teams = df['winner'].unique()
# print(teams)
teams_option = []
for team in teams:
    if team is None:
        continue
    team_dict = {'label':team,'value':team}
    teams_option.append(team_dict)

team = 'Kolkata Knight Riders'
sql_Statement = "select venue from matches where winner='"+team+"'"
df_venues = pd.read_sql(sql_Statement,engine)

# bar chart for showing data
fig = px.bar(x=df_venues['venue'].value_counts().values, y=df_venues['venue'].value_counts().index,labels={
                     "x": "Number of Matches won",
                     "y": "Venue Name",
                 },title='Matches Won by '+team+' at each venue ', barmode="group")
# to show the venue with max matches won
dict_venues = df_venues['venue'].value_counts().to_dict()
keys_to_values = dict(zip(dict_venues.values(), dict_venues.keys()))
venue_name = keys_to_values[max(keys_to_values.keys())]

# 5.2. For anyone match, you need to show the total runs scored by each batsman in that match and how they dismissed.
match_id = '335982'
sql_query = "select * from ballbyball where id='"+match_id+"'"
each_match_df = pd.read_sql(sql_query,engine)
runs = each_match_df.groupby(['batsman'])['batsman_runs'].sum()
runs.sort_values(ascending=False,inplace=True)

fig2 = px.bar(x=runs.index, y=runs.values,labels={
                     "x": "Batsman",
                     "y": "Runs",
                 },title='Total runs made by each batsman in the match RCB vs KKR', barmode="group")

# to show how each player dismissed
players = each_match_df['batsman'].unique()
players_dismissed_kind = {}
for player in players:
    sql_query = "select dismissal_kind from ballbyball where id='"+match_id+"' and batsman='"+player+"'"
    each_player_df = pd.read_sql(sql_query,engine)
    dismissal_kind = each_player_df['dismissal_kind'].unique()
    if len(dismissal_kind) == 1 and dismissal_kind[0] == 'not_dismissed':
        players_dismissed_kind[player] = 'not_dismissed'
    elif dismissal_kind[0] != 'not_dismissed':
        players_dismissed_kind[player] = dismissal_kind[0]
    elif dismissal_kind[1] != 'not_dismissed':
        players_dismissed_kind[player] = dismissal_kind[1]

fig3 = go.Figure(data=[go.Table(header=dict(values=['Player', 'Dismissed Type']),
                 cells=dict(values=[list(players_dismissed_kind.keys()), list(players_dismissed_kind.values())]))
                     ])
fig3.update_layout(width=1000, height=600)

#5.3. For anyone match, you need to show the total wicktes taken by all bowlers in that match.
wickets = each_match_df.groupby(['bowler'])['is_wicket'].sum()
wickets.columns = ['bowler','total_wickets']
wickets.sort_values(ascending=False,inplace=True)

labels=[X for X in wickets.keys()]

fig4 = px.pie(values=wickets.values, names=labels,labels={
                     "values": "Wickets",
                     "names": "Player",
                 },title='Total wicktes taken by all bowlers in that match')

#5.4. For year 2019, you need to show top 10 batsman(rank them according to their total runs scored).

year = '2019'
sql_query = "select matches.id,matches.date, ballbyball.batsman, ballbyball.batsman_runs from matches natural join ballbyball where matches.date like '"+year+"%'  "
year_df = pd.read_sql(sql_query,engine)
runs = year_df.groupby(['batsman'])['batsman_runs'].sum()
runs.columns = ['batsman','total_runs']
runs.sort_values(ascending=False,inplace=True)
runs = runs.head(10)
fig5 = px.bar(x=runs.index, y=runs.values,labels={
                     "x": "Batsman",
                     "y": "Runs",
                 },title="Top 10 batsmans in the year "+year)

#5.5. For year 2019, you need to show top 10 bowlers(rank them according to their total wickets taken).
sql_query = "select matches.id,matches.date, ballbyball.bowler, ballbyball.is_wicket from matches natural join ballbyball where matches.date like '"+year+"%'  "
year_df = pd.read_sql(sql_query,engine)
wickets = year_df.groupby(['bowler'])['is_wicket'].sum()
wickets.columns = ['bowler','total_wickets']
wickets.sort_values(ascending=False,inplace=True)
wickets = wickets.head(10)

fig6 = px.bar(x=wickets.index, y=wickets.values,labels={
                     "x": "bowler",
                     "y": "total_wickets",
                 },title="Top 10 bowlers in the year "+year)


#5.6. You need to show that does winning toss increases the chance of victory.


df['toss_win_game_win'] = np.where((df.toss_winner == df.winner),'Yes','No')
labels =["Yes",'No']
values = df['toss_win_game_win'].value_counts()
fig7 = px.pie(values=values, names=labels,labels={
                     "values": "Matches",
                     "names": "Matches won when toss won",
                 },title='Winning toss implies winning matches')

#5.7. For any 10 batsman, you need to show, against which bowler he got out most number of time.
ball_df = pd.read_sql("select * from ballbyball",engine)

batsmans = ball_df['batsman'].unique()
ten_batsmans = batsmans[:10]

def each_batsman(batsman,id):
#     batsman = 'RT Ponting'
    sql_query = "select * from ballbyball where batsman ='"+batsman+"'"
    batsman_df = pd.read_sql(sql_query,engine)
    temp_df = batsman_df.groupby('bowler')['is_wicket'].agg('sum').reset_index().sort_values(by='is_wicket', ascending=False).reset_index(drop=True).head(10)
    fig8 = px.bar(x=temp_df['bowler'],y=temp_df['is_wicket'],labels={
                     "x": "bowler",
                     "y": "total_wickets",
                 },title=batsman+" out's by each bowler")
    dict_batsman = temp_df.head(1).value_counts().to_dict()
    name,wicket = list(dict_batsman.keys())[0]
    result = batsman+" has most outs against the bowler "+name
    return dcc.Graph(id='toss-graph'+str(id),figure = fig8),html.Div(id='graph_text'+str(id),children=result)

   


#layout
app.layout = html.Div(children=[
    html.H1(children='IPL DashBoard'),

    html.Div(children='''
        IPL analysis and visualizations
    '''),
    dcc.Dropdown(
        id='iplTeam-dropdown',

        options = teams_option,
        placeholder="Select a Team",
        value='Kolkata Knight Riders'
    ),
    dcc.Graph(
        id='venue-graph'
        ),
    html.Div(id='graph_text',children=team+" won max number of matches at "+venue_name),
    
    dcc.Graph(
        id='matche-graph',
        figure = fig2
        ),
    html.Div(id='gtable_text',children="Dismissal kind of each batsman"),

    dcc.Graph(
        id='matche-table',
        figure = fig3
        ),

        
     dcc.Graph(
        id='boller-graph',
        figure = fig4
        ),
     dcc.Graph(
        id='batyear-graph',
        figure = fig5
        ),
     dcc.Graph(
        id='ballyear-graph',
        figure = fig6
        ),
     dcc.Graph(
        id='toss-graph',
        figure = fig7
        ),
    html.Div(id='text8',children="The number of out's for ten batsmen against each bowler"),

    html.Div([
        each_batsman(ten_batsmans[0],10)[0],
        each_batsman(ten_batsmans[0],10)[1],
        each_batsman(ten_batsmans[1],11)[0],
        each_batsman(ten_batsmans[1],11)[1],

        each_batsman(ten_batsmans[2],12)[0],
        each_batsman(ten_batsmans[2],12)[1],

        each_batsman(ten_batsmans[3],13)[0],
        each_batsman(ten_batsmans[3],13)[1],

        each_batsman(ten_batsmans[4],14)[0],
        each_batsman(ten_batsmans[4],14)[1],

        each_batsman(ten_batsmans[5],15)[0],
        each_batsman(ten_batsmans[5],15)[1],

        each_batsman(ten_batsmans[6],16)[0],
        each_batsman(ten_batsmans[6],16)[1],

        each_batsman(ten_batsmans[7],17)[0],
        each_batsman(ten_batsmans[7],17)[1],


        each_batsman(ten_batsmans[8],18)[0],
        each_batsman(ten_batsmans[8],18)[1],

        each_batsman(ten_batsmans[9],19)[0],
        each_batsman(ten_batsmans[9],19)[1]

    ],className="each_batsman_scroll"),

    
])

@app.callback(
    Output('venue-graph','figure'),
    Output('graph_text', 'children'),
    Input('iplTeam-dropdown', 'value')
)
def update_figure(team):
    sql_Statement = "select venue from matches where winner='"+team+"'"
    df_venues = pd.read_sql(sql_Statement,engine)
    fig = px.bar(x=df_venues['venue'].value_counts().values, y=df_venues['venue'].value_counts().index,labels={
                     "x": "Number of Matches won",
                     "y": "Venue Name",
                 },title='Matches Won by '+team+' at each venue ', barmode="group")
    dict_venues = df_venues['venue'].value_counts().to_dict()
    keys_to_values = dict(zip(dict_venues.values(), dict_venues.keys()))
    venue_name = keys_to_values[max(keys_to_values.keys())]

    return [fig,team+' won max number of matches at '+venue_name]


if __name__ == '__main__':
    app.run_server(debug=True)
