'''
Description: his creates the web app, or Dash app in general. It runs Dash on a local server. 
This is for the rss solution to the scrolling problem
Author: Tyler J Burns
Date: January 11, 2023
'''

from dash import Dash, dcc, html, dash_table, Input, Output, callback_context, State
import plotly.express as px
import pandas as pd
import json
import re
import numpy as np
from datetime import datetime

# You have to include these two lines if you want it to run in Heroku
app = Dash(__name__)
server = app.server

def search_bar(input, text):
    '''
    Takes a string with or without logical values (AND, OR) as input, runs that on another given string, and returns boolean corresponding to whether the input was in the other string.

    Args:
        input: The search term. 
        text: The text it will be doing the search on.
    Returns:
        boolean value correspoding to whether the input was in the text

    Note: 
        For logic-based search, you can add (all caps) AND or OR. But you can't add both of them. 

    Example:
        search_bar('beer OR wine", "This beer is good") returns True.
        search_bar('beer AND wine", "This beer is good") returns False.
        search_bar('beer AND wine OR cheese', 'This beer is good') returns False, because this function cannot use combos of AND and OR
    '''
    text = text.lower()
    bool_choice = [input.find('AND') != -1, input.find('OR') != -1]
    
    if(sum(bool_choice) == 0):
        result = text.find(input.lower()) != -1
        return(result)
    
    if sum(bool_choice) == 2:
        return(False)
    if bool_choice[0]:
        bool_choice = 'AND'
    elif bool_choice[1]:
        bool_choice = 'OR'

    input = input.split(' ' + bool_choice + ' ')
    input = [i.lower() for i in input]

    if bool_choice  == 'AND':
        result = [all(text.find(i.lower()) != -1 for i in input)]
    elif bool_choice == 'OR':
        result = [any(text.find(i.lower()) != -1 for i in input)]

    return(result[0])

# tmp.csv is the tweet metadata + dimension reduction + clustering script
df = pd.read_csv('data/rss.csv', lineterminator='\n')

# This is for the per-user dropdown menu initialized later in the code
users = list(set(df['source']))
users.append('all_users')

# NULL or NaN gets added to the rows sometimes upstream. Have not figured out why.
df = df[df['title'].notnull()] 
df = df[df['published'].notnull()] 

# NOTE some of the tweets are repeats. We need to get rid of these. 

# We have the url in markdown format, so it only shows up as a hyperlink
df['link'] = ['[Go to story]' + '(' + i + ')' for i in df['link']]

# We get rid of unnecessary columns for downstream processing
df_sub = df[['link', 'source', 'published', 'title']]

# This is the layout of the page. We are using various objects available within Dash. 
fig = px.scatter() # The map
app.layout = html.Div([
    html.A(html.P('We are solving the scrolling problem!'), href="https://tjburns08.github.io/scrolling_problem.html"),
    dcc.Dropdown(users, id='user-dropdown', value = users[0]),
    # dcc.Dropdown(['Today', 'Last 7 days', 'All years'] + list(range(2022, 2006, -1)), id='year-dropdown', value='Last 7 days'),
    dcc.Textarea(
        placeholder='Type keywords separated by AND or OR',
        id = 'user-input',
        value='',
        style={'width': '100%'}
    ),
    html.Button('Submit', id='value-enter'),
    dcc.Graph(
        id='news-map',
        figure=fig
    ),
    html.Plaintext('Info of entry you clicked on.'),
    dash_table.DataTable(data = df_sub.to_dict('records'), style_data={
        'whiteSpace': 'normal',
        'height': 'auto',
    }, id='news-table', fill_width = False, columns=[{'id': x, 'name': x, 'presentation': 'markdown'} if x == 'link' else {'id': x, 'name': x} for x in df_sub.columns]),

    html.Div(html.P(['', html.Br(), ''])),
    html.Plaintext('The total feed'),
    dash_table.DataTable(data = df_sub.to_dict('records'), style_data={
        'whiteSpace': 'normal',
        'height': 'auto',
    }, id='top-table', fill_width = False, columns=[{'id': x, 'name': x, 'presentation': 'markdown'} if x == 'link' else {'id': x, 'name': x} for x in df_sub.columns])

])

# This allows the user to click on a point on the map and get a single entry corresponding to that article
# TODO consider returning the article and its KNN
@app.callback(
    Output('news-table', 'data'),
    Input('news-map', 'clickData'))

def click(clickData):
    if not clickData:
        return
    print(clickData)
    entry = clickData['points'][0]['customdata'][1]
    filtered_df = df_sub[df_sub['title'] == entry]
    filtered_df['title'] = [re.sub('<br>', ' ', i) for i in filtered_df['title']]
    filtered_df['title'] = [i.split('https:')[0] for i in filtered_df['title']]
    return filtered_df.to_dict('records')

# This updates the "top tweets" table every time the year dropdown changes
@app.callback(
    Output('top-table', 'data'),
    Input('value-enter', 'n_clicks'),
    # Input('year-dropdown', 'value'),
    State('user-input', 'value'))

def update_table(n_clicks, input_value):
    
    # TODO do we put the "df" object itself as input to this function?
    # TODO filtered_df = df_sub?
    filtered_df = df # Make local variable. There might be a less ugly way to do this.
    
    if filtered_df.shape[0] == 0:
        return
    
    rel_rows = []
    for i in filtered_df['title']:
        rel_rows.append(search_bar(input_value, i))

    # Re-initialize df_sub given our df has been filtered above
    # TODO to this in a less ugly way please
    filtered_df_sub = filtered_df[['link', 'source', 'published', 'title']]
    filtered_df_sub = filtered_df_sub[rel_rows]
    return filtered_df_sub.to_dict('records')

# This updates the map given the dropdowns and the value entered into the search bar
# TODO change news-map
@app.callback(  
    Output('news-map', 'figure'),
    Input('user-dropdown', 'value'), 
    Input('value-enter', 'n_clicks'),
    State('user-input', 'value'))

def update_plot(source_value, n_clicks, input_value):
    user_context = callback_context.triggered[0]['prop_id'].split('.')[0]
    tmp = df

    # Right now we're getting "none" as source value
    if(source_value != 'all_users'):
        tmp = df[df['source'] == source_value]


    if(source_value == 'all_users'):
        fig = px.scatter(tmp, x = 'umap1', y = 'umap2', hover_data = ['published', 'title'], size_max = 10, title = 'Compare user mode')
    else:
        fig = px.scatter(tmp, x = 'umap1', y = 'umap2', hover_data = ['published', 'title'], size_max = 10, title = 'Context similarity map of tweets')
    

    # DarkSlateGrey
    fig.update_traces(marker=dict(line=dict(width=0.1,
                                        color='DarkSlateGrey')),
                  selector=dict(mode='markers'))

    return(fig)



if __name__ == '__main__':
    app.run_server(debug=True)
