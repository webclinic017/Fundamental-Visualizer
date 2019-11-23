#!/usr/bin/env python
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from webscraper import req_handle
from data_processing import data_processing
import plotly.graph_objs as go
import pandas as pd
import datetime


class storage:
    def __init__(self):
        self.previous_request = []

    def update(self,country,symbol,style):
        print(country,symbol,style)
        data_request = [country,symbol,style]
        print("Request: ",data_request)
        if data_request[:2] != self.previous_request[:2] or self.previous_request == []:
            print("Requesting data...")
            self.df_daily,self.df_yearly,self.df_est,self.currency = req_handle(*data_request)
            self.previous_request = data_request
            print("Data received.")
        print("Processing data...")
        processing_request = [self.df_daily,self.df_yearly,self.df_est,*data_request[1:],self.currency]
        trace1,pe,pe_norm,grw,grw_exp = data_processing(*processing_request)
        print("Data processed.")
        return trace1,pe,pe_norm,grw,grw_exp

strg = storage()
app = dash.Dash('FunViz', external_stylesheets=[dbc.themes.CYBORG])
app.title = "FunViz"


colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div([html.H3('FunViz'),
    html.Div([
        html.Div([
                html.Label('Country: '),
                dcc.Dropdown(
                    id='country-input',
                    options=[
                        {'label': u'USA', 'value': 'USA'},
                        {'label': u'Germany', 'value': 'Germany'},
                        {'label': u'Hongkong', 'value': 'Hongkong'},
                        {'label': u'Japan', 'value': 'Japan'},
                        {'label': u'France', 'value': 'Canada'},
                        {'label': u'UK', 'value': 'UK'},
                        {'label': u'Switzerland', 'value': 'Switzerland'},
                        {'label': u'Australia', 'value': 'Australia'},
                        {'label': u'Korea', 'value': 'Korea'},
                        {'label': u'Netherlands', 'value': 'Netherlands'},
                        {'label': u'Spain', 'value': 'Spain'},
                        {'label': u'Russia', 'value': 'Russia'},
                        {'label': u'Italy', 'value': 'Italy'},
                        {'label': u'Belgium', 'value': 'Belgium'},
                        {'label': u'Mexiko', 'value': 'Mexiko'},
                        {'label': u'Sweden', 'value': 'Sweden'},
                        {'label': u'Norway', 'value': 'Norway'},
                        {'label': u'Finland', 'value': 'Finland'},
                        {'label': u'Denmark', 'value': 'Denmark'},
                    ],
                    value='USA'
                )
            ],style={'width': '30%'}, className="six columns"),

            html.Div([
                html.Label('Style: '),
                dcc.Dropdown(
                    id='style-input',
                    options=[
                        {'label': u'Base', 'value': 'Base'},
                        {'label': u'PE15', 'value': 'PE15'},
                        {'label': u'PEG85', 'value': 'PEG85'},
                        {'label': u'PE-Plot', 'value': 'PE-Plot'},
                        {'label': u'REIT', 'value': 'REIT'},
                    ],
                    value='Base'
                )
            ],style={'width': '30%'}, className="six columns"),
            html.Div([
                html.Label('Ticker: '),
                dcc.Input(id='ticker-input', value='AAPL', type='text'),
                html.Button(id='update-input', type='Update', children='Update')
            ],style={'width': '30%'}, className="six columns"),
        ], className="row"),
        html.Br(),
        html.Div(
            html.Div([
                html.Div([
                    html.Label('PE'),
                    html.Div(id='pe')
                ],style={'width': '20%'}, className="six columns"),

                html.Div([
                    html.Label('Normal PE'),
                    html.Div(id='pe_norm')
                ],style={'width': '20%'}, className="six columns"),

                html.Div([
                    html.Label('Growth Rate'),
                    html.Div(id='grw')
                ],style={'width': '20%'}, className="six columns"),

                html.Div([
                    html.Label('exp. Growth Rate'),
                    html.Div(id='grw_exp',style={"border":"2px black solid"})
                ],style={'width': '20%'}, className="six columns"),
            ], className="row")
        ),
        html.Div(dcc.Graph(id='graph-output'))]
)

@app.callback([
    Output('graph-output', 'figure'),
    Output('pe', 'children'),
    Output('pe_norm', 'children'),
    Output('grw', 'children'),
    Output('grw_exp', 'children')],
    [Input('update-input', 'n_clicks')],
    [State('ticker-input', 'value'),
     State('country-input','value'),
     State('style-input','value')]
    )

def update_graph_output(n_clicks,symbol,country,style):
    figure,pe,pe_norm,grw,grw_exp = strg.update(country,symbol,style)
    print(pe,pe_norm,grw,grw_exp)
    return figure, str(pe), str(pe_norm), str(grw), str(grw_exp)

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    app.run_server(debug=True)

'''
    Output('graph', 'pe':'value'),
    Output('pe_norm', 'pe_norm':'value'),
    Output('grw', 'grw':'value'),
    Output('grw_exp', 'grw_exp':'value')
'''
