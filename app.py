#!/usr/bin/env python
# -*- coding: utf-8 -*-

### Data
import pandas as pd
import pickle
import dash_table
import boto3
from boto3.dynamodb.conditions import Key, Attr

### Graphing
import plotly.graph_objects as go
import plotly.express as px

### Dash
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input

## Access_Key and Secret_Key account THB
## Please insert access and secret key of thb account (for dynamodb)
## between ''
ACCESS_KEY = ''
SECRET_KEY = ''

## Read from AWS Dynamodb
##client = boto3.resource ('dynamodb')
client = boto3.resource('dynamodb',aws_access_key_id= ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
table = client.Table("bbb_stat")
response = table.scan()
item=response['Items']
# first dataframe df
df = pd.DataFrame(data=item)
# second dataframe dft
dft = pd.DataFrame(data=item)
#########

## Wrangling data from Dataframe df
df['date_time'] = pd.to_datetime(df['date_time'],errors='coerce')
df['month'] = df['date_time'].dt.month
df = df.set_index('month')
#########

### Colors
colors = {
    'bg_black' : '#818181',
    'text_green' : '#1dcf9d',
    'bg_blue' : '#365b6b',
    'bg_blue_graph' : '#334f65'
}
#########



### DBC Card
### Sum of meeting, listener, participant, and video
card_content_1 = [
    
    dbc.CardBody(
        [
            html.H5("Meeting", className="card-title"),
            html.P("",className="card-text",),
            df["meetingCount"].sum(),
        ]
    ),
]

card_content_2 = [
    
    dbc.CardBody(
        [
            html.H5("Listener", className="card-title"),
            html.P("",className="card-text",),
            df["listenerCount"].sum(),
        ]
    ),
]

card_content_3 = [
    
    dbc.CardBody(
        [
            html.H5("Participant", className="card-title"),
            html.P("",className="card-text",),
            df["participantCount"].sum(),
        ]
    ),
]

card_content_4 = [
    
    dbc.CardBody(
        [
            html.H5("Video", className="card-title"),
            html.P("",className="card-text",),
            df["videoCount"].sum(),
        ]
    ),
]
#########


##### Layout

app = dash.Dash(__name__,external_stylesheets = [dbc.themes.SOLAR])
### NOTE remove 3# (comments) below if you want to upload it to the AWS
### please insert THB account secret key between the ''

#app.server.secret_key = ''
#server = app.server
#app.config.suppress_callback_exceptions = True

app.layout = html.Div([
        dbc.Container([
           

            dbc.Row([
                
                dbc.Col([
                    dbc.Card(card_content_1, color="info", inverse=True),
                    dbc.Card(card_content_3, color="info", inverse=True)
                ],md=2),

                dbc.Col([                   
                    dbc.Card(card_content_2, color="info", inverse=True),
                    dbc.Card(card_content_4, color="info", inverse=True)
                ],md=2),
                dbc.Col([

                   dash_table.DataTable(
                    id='datatable-interactivity',
                    columns=[
                        {"name": i, "id": i, "deletable": False, "selectable": True} for i in dft.columns
                    ],
                    data=dft.to_dict('records'),
                    editable=False,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    column_selectable="single",
                    row_deletable=False,
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current= 0,
                    page_size= 10,
                    style_header={'backgroundColor': 'rgb(30, 30, 30)','color':'white'},
                    style_cell={'backgroundColor': 'rgb(50, 50, 50)',
                                'color': 'white'})
                ],md=8),
            ]),

            dbc.Row([

                
            ],style={'margin-bottom': '40px'}),

            dbc.Row([

                dbc.Col([
                    dcc.Graph(id='meeting-history'),

                    
                    dcc.Slider(
                        id='date-slider',
                        min=3,
                        max=6,
                        step=None,
                        value=3,
                        marks={3:'März', 4:'April', 5:'Mai', 6:'Juni'}
                    )
                ],style={'margin-bottom': '40px'},md=4),

                dbc.Col([
                    html.Div(id='datatable-interactivity-container')
                ],style={'width': '20%', 'display': 'block', 'margin-bottom': '20px'},md=8),              
            ]),

            dbc.Row([
                
            ],style={'margin-bottom': '40px'}),            
            
        ])
    ])

### function update_figure
def update_figure(value):
    dff = df.loc[value]
    
    fig = px.scatter(dff, x="date_time", y="meetingCount")

    fig.update_layout(yaxis={'title':'Meeting Count'},
                      title={'text':'Online Meeting Data'},
                      font = {'color' : colors['bg_black']},
                      plot_bgcolor = '#171717',
                      paper_bgcolor = '#171717',
                      hovermode = 'closest',
                      height=300)
    return fig
########################################

### callbacks
@app.callback(
    Output('meeting-history','figure'),
    [Input('date-slider','value')])
def update_graph(value):
    graph = update_figure(value)
    return graph

@app.callback(
    Output('datatable-interactivity-container', "children"),
    [Input('datatable-interactivity', "derived_virtual_data"),
     Input('datatable-interactivity', "derived_virtual_selected_rows")])
def update_graphs(rows, derived_virtual_selected_rows):

    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dfft = dft if rows is None else pd.DataFrame(rows)

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dfft))]
    
    return [
        dcc.Graph(
            id=column,
            figure={
                "data": [
                    {
                        "x": dfft["date_time"],
                        "y": dfft[column],
                        "type": "bar",
                        "marker": {"color": colors},
                    }
                ],
                "layout": {
                    "xaxis": {"automargin": True},
                    "yaxis": {
                        "automargin": True,
                        "title": {"text": column}
                    },
                    "height": 250,
                    "margin": {"t": 10, "l": 10, "r": 10},
                    "color":"crimson",
                    "font":{'color':'#818181'},
                    "plot_bgcolor" : '#171717',
                    "paper_bgcolor" : '#171717'
                },
            },
        )
        # check if column exists - user may have deleted it
        # If `column.deletable=False`, then you don't
        # need to do this check.
        for column in ["meetingCount", "participantCount", "listenerCount"] if column in dfft
    ]

@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    [Input('datatable-interactivity', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]

if __name__ == '__main__':
    app.run_server(debug=True)

#remove debug=True if you want to upload the file into AWS