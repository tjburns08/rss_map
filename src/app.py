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
users.insert(0, 'all_users')

# NULL or NaN gets added to the rows sometimes upstream. Have not figured out why.
df = df[df['title'].notnull()] 
df = df[df['published'].notnull()] 

# We have the url in markdown format, so it only shows up as a hyperlink
df['link'] = ['[Go to story]' + '(' + i + ')' for i in df['link']]

# We get rid of unnecessary columns for downstream processing
df_sub = df[['link', 'source', 'published', 'title', 'sentiment']]

# This is the layout of the page. We are using various objects available within Dash. 
fig = px.scatter() # The map
app.layout = html.Div([
    html.A(html.P('We are solving the scrolling problem!'), href="https://tjburns08.github.io/scrolling_problem.html"),
    dcc.Dropdown(users, id='user-dropdown', value = users[0]),
    dcc.Input(
        type='text',
        placeholder='Type keywords separated by AND or OR',
        id='user-input',
        value='',
        style={'width': '100%'},
        debounce=True
    ),

    html.Button('Submit', id='value-enter'),
    html.Div(style={'height': '20px'}), # Checkbox is too close to the search button
    dcc.Checklist(
        options=[
            {'label': 'Color by sentiment', 'value': 'sentiment'}
        ],
        id='color-by-sentiment',
        value=[]
    ),
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
    html.Div(id='row-count'),
    dash_table.DataTable(data=df_sub.head(10).to_dict('records'),
                     style_data={
                         'whiteSpace': 'normal',
                         'height': 'auto',
                     },
                     id='top-table',
                     fill_width=False,
                     columns=[{'id': x, 'name': x, 'presentation': 'markdown'} if x == 'link' else {'id': x, 'name': x} for x in df_sub.columns],
                     page_size=10,  # Show 10 rows per page
                     sort_action='native',  # Enable sorting
                     page_action='native',  # Enable pagination
                     filter_action='native',  # Enable searching
                     ),
    dcc.Store(id='filtered-data')
])

# This allows the user to click on a point on the map and get a single entry corresponding to that article
# TODO consider returning the article and its KNN
@app.callback(
    Output('news-table', 'data'),
    Input('news-map', 'clickData'))

def click(clickData):
    if not clickData:
        return
    entry = clickData['points'][0]['customdata'][1]
    filtered_df = df_sub[df_sub['title'] == entry]
    filtered_df['title'] = [re.sub('<br>', ' ', i) for i in filtered_df['title']]
    filtered_df['title'] = [i.split('https:')[0] for i in filtered_df['title']]
    return filtered_df.to_dict('records')

# This updates the "top tweets" table every time the year dropdown changes
@app.callback(
    Output('top-table', 'data'),
    Input('filtered-data', 'data'),
    Input('user-dropdown', 'value'))
def update_table(filtered_data, source_value):
    if not filtered_data:
        return

    filtered_df = pd.DataFrame(filtered_data)

    if source_value != 'all_users':
        filtered_df = filtered_df[filtered_df['source'] == source_value]

    return filtered_df.to_dict('records')


# This updates the map given the dropdowns and the value entered into the search bar
# TODO change news-map
@app.callback(
    Output('filtered-data', 'data'),
    Output('news-map', 'figure'),
    Input('user-dropdown', 'value'),
    Input('value-enter', 'n_clicks'),
    Input('color-by-sentiment', 'value'),
    State('user-input', 'value'))
def update_plot(source_value, n_clicks, color_by_sentiment, input_value):
    user_context = callback_context.triggered[0]['prop_id'].split('.')[0]
    tmp = df

    color_scale = {
        'negative': '#EF553B',
        'neutral': '#636EFA',
        'positive': '#00CC96'
    }

    color_column = 'sentiment' if 'sentiment' in color_by_sentiment else 'source'

    if source_value != 'all_users':
        tmp = df[df['source'] == source_value]

    if source_value == 'all_users':
        fig = px.scatter(tmp, x='umap1', y='umap2', hover_data=['published', 'title', 'sentiment'], size_max=10, color=color_column, color_discrete_map=color_scale, title='Compare user mode', template='plotly_dark')
    else:
        fig = px.scatter(tmp, x='umap1', y='umap2', hover_data=['published', 'title', 'sentiment'], size_max=10, color=color_column, color_discrete_map=color_scale, title='Context similarity map of tweets', template='plotly_dark')

    fig.update_traces(marker=dict(line=dict(width=0.1, color='DarkSlateGrey')), selector=dict(mode='markers'))

    if input_value:  # Check if input_value is not empty
        rel_rows = [search_bar(input_value, title) for title in tmp['title']]
        tmp = tmp[rel_rows]

        if source_value == 'all_users':
            fig = px.scatter(tmp, x='umap1', y='umap2', hover_data=['published', 'title', 'sentiment'], size_max=10, color=color_column, color_discrete_map=color_scale, title='Compare user mode', template='plotly_dark')
        else:
            fig = px.scatter(tmp, x='umap1', y='umap2', hover_data=['published', 'title', 'sentiment'], size_max=10, color=color_column, color_discrete_map=color_scale, title='Context similarity map of tweets', template='plotly_dark')

        fig.update_traces(marker=dict(line=dict(width=0.1, color='DarkSlateGrey')), selector=dict(mode='markers'))

    # Set the range_x and range_y to the default coordinates
    default_x_range = [df['umap1'].min(), df['umap1'].max()]
    default_y_range = [df['umap2'].min(), df['umap2'].max()]

    fig.update_xaxes(range=default_x_range)
    fig.update_yaxes(range=default_y_range)

    # Store the filtered DataFrame in the dcc.Store component
    filtered_data = tmp[['link', 'source', 'published', 'title', 'sentiment']].to_dict('records')

    return filtered_data, fig


@app.callback(
    Output('row-count', 'children'),
    Input('top-table', 'derived_virtual_data')  
)
def update_row_count(data):
    if data is None:
        row_count = 0
    else:
        row_count = len(data)
    return f"Total rows: {row_count}"


if __name__ == '__main__':
    app.run_server(debug=True)
