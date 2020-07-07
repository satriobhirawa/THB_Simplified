#!/usr/bin/env python
# -*- coding: utf-8 -*-

### Data
import datetime
import os
import pandas as pd
import dash_table
import boto3
from decouple import config

### Graphing
import plotly.graph_objects as go
import plotly.express as px

### Dash
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input

## Set Access_Key and Secret_Key as environment variables
ACCESS_KEY = os.environ['ACCESS_KEY']
SECRET_KEY = os.environ['SECRET_KEY']


#ACCESS_KEY = config('ACCESS_KEY')
#SECRET_KEY = config('SECRET_KEY')

## Read from AWS Dynamodb
client = boto3.resource('dynamodb',
                        aws_access_key_id=ACCESS_KEY,
                        aws_secret_access_key=SECRET_KEY,
                        region_name='eu-central-1')
table = client.Table("bbb_stat")
response = table.scan()
item = response['Items']

dft = pd.DataFrame(data=item)
#########

## Wrangling data from Dataframe df
dft['date_time'] = pd.to_datetime(dft['date_time'], errors='coerce') + datetime.timedelta(hours=2)
dft.sort_values(by=['date_time'], ascending=True, inplace=True)
dft['date_time'] = dft['date_time'].dt.round('15min')
del dft['id']

df = dft.copy(deep=True)
df['month'] = df['date_time'].dt.month
df = df.set_index('month')

dft['date_time'] = pd.DatetimeIndex(dft['date_time']).strftime("%Y-%m-%d %H:%M %a")

#########

table_header = {'listenerCount': 'Zuhörer',
                'meetingCount': 'Meetings',
                'date_time': 'Datum/Uhrzeit',
                'participantCount': 'Teilnehmer',
                'videoCount': 'Video',
                'voiceParticipantCount': 'Sprecher'}

colors = {
    'bg_black': '#818181',
    'text_green': '#1dcf9d',
    'bg_blue': '#365b6b',
    'bg_blue_graph': '#334f65'
}
#########
### DBC Card
### Sum of meeting, listener, participant, and video
card_content_1 = [
    dbc.CardBody(
        [
            html.H5("Meeting", className="card-title"),
            html.P("", className="card-text", ),
            df["meetingCount"].sum(),
        ]
    ),
]

card_content_2 = [
    dbc.CardBody(
        [
            html.H5("Zuhörer", className="card-title"),
            html.P("", className="card-text", ),
            df["listenerCount"].sum(),
        ]
    ),
]

card_content_3 = [
    dbc.CardBody(
        [
            html.H5("Teilnehmer", className="card-title"),
            html.P("", className="card-text", ),
            df["participantCount"].sum(),
        ]
    ),
]

card_content_4 = [
    dbc.CardBody(
        [
            html.H5("Video", className="card-title"),
            html.P("", className="card-text", ),
            df["videoCount"].sum(),
        ]
    ),
]
card_content_5 = [
    dbc.CardBody(
        [
            html.H5("Sprecher", className="card-title"),
            html.P("", className="card-text", ),
            df["voiceParticipantCount"].sum(),
        ]
    ),
]
#########

##### Layout
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
### NOTE remove 3# (comments) below if you want to upload it to the AWS
### please insert THB account secret key between the ''

# app.server.secret_key = ''
# server = app.server
# app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col([dbc.Card(card_content_1, color="info", inverse=True), ]),
            dbc.Col([dbc.Card(card_content_2, color="info", inverse=True), ]),
            dbc.Col([dbc.Card(card_content_3, color="info", inverse=True), ]),
            dbc.Col([dbc.Card(card_content_4, color="info", inverse=True), ]),
            dbc.Col([dbc.Card(card_content_5, color="info", inverse=True), ]),
        ]),

        dbc.Row([], style={'margin-bottom': '10px'}),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id='meeting-history'),
                dcc.Slider(
                    id='date-slider',
                    min=3,
                    max=7,
                    step=None,
                    value=3,
                    marks={3: 'März', 4: 'April', 5: 'Mai', 6: 'Juni',7: 'Juli'}
                )
            ], style={'margin-bottom': '40px'}, md=4),

            dbc.Col([
                dash_table.DataTable(
                    id='datatable-interactivity',
                    columns=[
                        {"name": table_header[i], "id": i, "deletable": True, "selectable": True} for i in dft.columns
                    ],
                    data=dft.to_dict('records'),
                    editable=False,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    # column_selectable="single",
                    row_deletable=False,
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current=0,
                    page_size=10,
                    style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                  'color': 'white'},
                    style_cell={'backgroundColor': 'rgb(50, 50, 50)',
                                'color': 'white'},
                    style_filter={'backgroundColor': 'white', },
                )
            ], md=8),
        ]),

        dbc.Row([], style={'margin-bottom': '20px'}),
        dbc.Row([
            dbc.Col([html.Div(id='datatable-interactivity-container')],
                    style={'width': '20%', 'display': 'block', 'margin-bottom': '20px'},
                    md=12),

        ])
    ])
])


### function update_figure
def update_figure(value):
    dff = df.loc[value]
    fig = px.scatter(dff, x="date_time", y="meetingCount")
    fig.update_layout(yaxis={'title': 'Meeting Count'},
                      title={'text': 'Online Meeting Data'},
                      font={'color': colors['bg_black']},
                      plot_bgcolor='#171717',
                      paper_bgcolor='#171717',
                      hovermode='closest',
                      height=300)
    return fig


### callbacks
@app.callback(
    Output('meeting-history', 'figure'),
    [Input('date-slider', 'value')])
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
    #test
    dfft = dfft.rename({'meetingCount': 'Meetings', 'participantCount': 'Teilnehmer', 'videoCount': 'Video','listenerCount': 'Zuhörer'}, axis=1)
    dfft.sort_values(by=['date_time'], ascending=True, inplace=True)
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
                    "height": 500,
                    "margin": {"t": 10, "l": 10, "r": 10},
                    "color": "crimson",
                    "font": {'color': '#818181'},
                    "plot_bgcolor": '#171717',
                    "paper_bgcolor": '#171717'
                },
            },
        )
        # check if column exists - user may have deleted it
        # If `column.deletable=False`, then you don't
        # need to do this check.
        #test
        #for column in ["meetingCount", "participantCount", "listenerCount"] if column in dfft
        for column in ['Meetings', 'Teilnehmer', 'Video','Zuhörer'] if column in dfft
    ]


@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    [Input('datatable-interactivity', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]


if __name__ == '__main__':
    app.run_server(debug=True)

# remove debug=True if you want to upload the file into AWS
