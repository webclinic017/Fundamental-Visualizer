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


class Storage:
    def __init__(self):
        self.previous_request = []

    def update(self, country, symbol, style):
        print(country, symbol, style)
        data_request = [country, symbol, style]
        print("Request: ", data_request)
        if data_request[:2] != self.previous_request[:2] or self.previous_request == []:
            print("Requesting data...")
            self.df_daily, self.df_yearly, self.df_est, self.currency = req_handle(
                *data_request)
            self.previous_request = data_request
            print("Data received.")
        print("Processing data...")
        processing_request = [self.df_daily, self.df_yearly,
                              self.df_est, *data_request[1:], self.currency]
        trace1, pe, pe_norm, grw, grw_exp = data_processing(
            *processing_request)
        print("Data processed.")
        return trace1, pe, pe_norm, grw, grw_exp


init_fig = figure = {'data': [], 'layout': go.Layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis={
                                                     'showticklabels': False, 'ticks': '', 'showgrid': False, 'zeroline': False}, yaxis={'showticklabels': False, 'ticks': '', 'showgrid': False, 'zeroline': False})}
strg = Storage()
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
app = dash.Dash('FunViz', external_stylesheets=[dbc.themes.DARKLY])
app.title = "FunViz"
# Simple(children=

app.layout = html.Div([dbc.Navbar([
    dbc.Row([
        dbc.Col(html.Img(src=PLOTLY_LOGO, height="90px")),
        dbc.Col([html.H2("FunViz"), html.Div(html.Label(
            "Fundamentals Visualizer"), style={'font-size': 13})]),
        dbc.Col([
            html.Label('Country: '),
            html.Div([dcc.Dropdown(id='country-input',
                                   options=[
                                       {'label': u'USA', 'value': 'USA'},
                                       {'label': u'Germany', 'value': 'Germany'},
                                       {'label': u'Hongkong', 'value': 'Hongkong'},
                                       {'label': u'Japan', 'value': 'Japan'},
                                       {'label': u'France', 'value': 'France'},
                                       {'label': u'UK', 'value': 'UK'},
                                       {'label': u'Switzerland', 'value': 'Switzerland'},
                                       {'label': u'Australia', 'value': 'Australia'},
                                       {'label': u'Korea', 'value': 'Korea'},
                                       {'label': u'Netherlands', 'value': 'Netherlands'},
                                       {'label': u'Spain', 'value': 'Spain'},
                                       {'label': u'Russia', 'value': 'Russia'},
                                       {'label': u'Italy', 'value': 'Italy'},
                                       {'label': u'Belgium', 'value': 'Belgium'},
                                       {'label': u'Sweden', 'value': 'Sweden'},
                                       {'label': u'Norway', 'value': 'Norway'},
                                       {'label': u'Finland', 'value': 'Finland'},
                                       {'label': u'Denmark', 'value': 'Denmark'},
                                   ],
                                   value='USA'
                                   )], style={'color': 'black', 'width': '150px'}),
        ]),
        dbc.Col([
                html.Label('Style: '),
                html.Div([dcc.Dropdown(
                    id='style-input',
                    options=[
                        {'label': u'Base', 'value': 'Base'},
                        {'label': u'PE(15)', 'value': 'PE15'},
                        {'label': u'PEG(8.5)', 'value': 'PEG85'},
                        {'label': u'PE-Plot', 'value': 'PE-Plot'},
                        {'label': u'FFO/OCF', 'value': 'REIT'},
                    ],
                    value='Base'
                )], style={'color': 'black', 'width': '120px'}),
                ]),
        dbc.Col([
                html.Label('Ticker: '),
                html.Div([dbc.Input(id="ticker-input", type="text",
                                    value='AAPL')], style={'width': '80px'}),
                ]),
        dbc.Col([
                dbc.Button("Update", id="update-input", size="lg"),
                ]),
        dbc.Col([
            dbc.Nav([
                dbc.NavItem(dbc.NavLink(
                    "ReadMe", active=True, href="https://github.com/tobigs/FunViz", external_link=True)),
            ], pills=True),
        ]),
        dbc.Col([
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Sponsor", active=True,
                                        href="http://paypal.me/tobigsIO")),
            ], pills=True),
        ]),
    ], justify="end", align="center"),
], className="dash-bootstrap"),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Label('      '),
        ], align="center"),
        dbc.Col([
            dbc.Label('PE'),
            html.Div(dbc.Input(id='pe', type="text"), style={'width': 130})
        ], align="center"),

        dbc.Col([
            dbc.Label('Normal PE'),
            html.Div(dbc.Input(id='pe_norm', type="text"),
                     style={'width': 130})
        ], align="center"),

        dbc.Col([
            dbc.Label('Growth Rate'),
            html.Div(dbc.Input(id='grw', type="text"), style={'width': 130})
        ], align="center"),

        dbc.Col([
            dbc.Label('exp. Growth Rate'),
            html.Div(dbc.Input(id='grw_exp', type="text"),
                     style={'width': 130}),
        ], align="center"),
        dbc.Col([
            dbc.Label('      '),
        ], align="center"),
    ], align="center"),
    html.Div(dbc.Alert(
        "Couldn't find any stocks matching your request or symbol is not supported. Use finance.yahoo.com to check symbol.",
        id="alert",
        dismissable=True,
        fade=True,
        color="warning",
        is_open=False,
    )),
    dcc.Graph(id='graph-output',
              figure={
                  'data': [],
                  'layout': go.Layout(
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      xaxis={
                          'showticklabels': False,
                          'ticks': '',
                          'showgrid': False,
                          'zeroline': False
                      },
                      yaxis={
                          'showticklabels': False,
                          'ticks': '',
                          'showgrid': False,
                          'zeroline': False
                      }
                  )
              }
              )], className="dash-bootstrap"
)


@app.callback([
    Output('graph-output', 'figure'),
    Output('pe', 'value'),
    Output('pe_norm', 'value'),
    Output('grw', 'value'),
    Output('grw_exp', 'value'),
    Output('alert', 'is_open')],
    [Input('update-input', 'n_clicks')],
    [State('ticker-input', 'value'),
     State('country-input', 'value'),
     State('style-input', 'value')]
)
def update_graph_output(n_clicks, symbol, country, style):
    try:
        figure, pe, pe_norm, grw, grw_exp = strg.update(country, symbol, style)
        print("Success.")
        print(pe, pe_norm, grw, grw_exp)
        return figure, str(pe), str(pe_norm), str(grw), str(grw_exp), False
    except Exception as ex:
        print("Failure:", ex)
        return init_fig, None, None, None, None, True
    print("debug-print")
    figure, pe, pe_norm, grw, grw_exp = strg.update(country, symbol, style)
    return figure, str(pe), str(pe_norm), str(grw), str(grw_exp), False


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    app.run_server(debug=True)
