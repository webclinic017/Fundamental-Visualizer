#!/usr/bin/env python
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, Event
from webscraper import req_handle
from data_processing import data_processing, killer
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd

class storage:
    def __init__(self):
        self.previous_request = []

    def update(self,country,symbol,style):
        print(country,symbol,style)
        data_request = [country,symbol,style]
        print("Request: ",data_request)
        print("Request: ",self.previous_request)
        if data_request[:2] != self.previous_request[:2] or self.previous_request == []:
            print("Requesting data...")
            self.df_daily,self.df_yearly,self.df_est,self.currency = req_handle(*data_request)
            self.previous_request = data_request
            print("Data received.")
        print("Processing data...")
        processing_request = [self.df_daily,self.df_yearly,self.df_est,*data_request[1:],self.currency]
        trace1 = data_processing(*processing_request)
        #self.disp_pe["text"] = str(round(pe, 2))
        #self.disp_pe_norm["text"] = str(round(pe_norm, 2))
        #self.disp_grw["text"] = str(round(grw, 2)) + "%"
        #self.disp_grw_exp["text"] = str(round(grw_exp, 2)) + "%"
        print("Data processed.")
        return trace1

str = storage()
app = dash.Dash()

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div([
    html.Label('Country: '),
    dcc.Dropdown(
        id='country-input',
        options=[
            {'label': u'USA', 'value': 'USA'},
            {'label': u'Germany', 'value': 'Germany'},
        ],
        value='USA'
    ),
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
    ),

    html.Label('Ticker: '),
    dcc.Input(id='ticker-input', value='AAPL', type='text'),
    html.Button(id='update-input', type='Update', children='Update'),
    html.Div(dcc.Graph(id='graph-output',
        figure={
            'data': [
            ],
            'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                }
            }
        }))

])

@app.callback(
    Output('graph-output', 'figure'),
    [Input('update-input', 'n_clicks')],
    [State('ticker-input', 'value'),
     State('country-input','value'),
     State('style-input','value')]
    )

def update_graph_output(n_clicks,symbol,country,style):
    trace1 = str.update(country,symbol,style)

    return {'data': trace1,
            'layout': {
                'plot_bgcolor': 'white',
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                }
            }
        }
if __name__ == '__main__':
    app.run_server(debug=True)
