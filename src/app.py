#!/usr/bin/env python
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, Event
from webscraper import req_handle
from data_processing import data_processing, killer
import plotly.graph_objs as go
import plotly.express as px

app = dash.Dash()

colors = {
    'background': '#FFFFFF',
    'text': '#7FDBFF'
}

app.layout = html.Div([
    html.Label('Country: '),
    dcc.Dropdown(
        id='country-input',
        options=[
            {'label': u'United States', 'value': 'US'},
            {'label': u'Germany', 'value': 'DE'},
        ],
        value=['US']
    ),

    html.Label('Ticker: '),
    dcc.Input(id='ticker-input', value='AAPL', type='text'),
    html.Button(id='update-input', type='Update', children='Update'),
    html.Div(dcc.Graph(id='graph-output'))

])

@app.callback(
    Output('graph-output', 'figure'),
    [Input('update-input', 'n_clicks')],
    [State('ticker-input', 'value'),
     State('country-input','value')]
    )

def update_graph_output(n_clicks, ticker, country):
    data_request = ["USA","AAPL","Base"]
    df_daily,df_yearly,df_est,currency = req_handle(*data_request)
    processing_request = [df_daily,df_yearly,df_est,*data_request[1:],currency]
    df_yearly,df_daily,df_est,e_total,e_total_norm,e_total_index_dt,style,currency,symbol,col_dict, e_multiple = data_processing(*processing_request)

    #df_daily = dh.get_daily_stock_data(ticker, country)
    #df_date =df_daily['date']
    #df_closing = df_daily['close']

    # Only thing I figured is - I could do this
    trace1 = go.Figure()
    trace1.add_trace(go.Scatter(x=e_total_index_dt, y=e_total, mode='lines', name="AAPL", marker={"size": 3}))
    #trace1.add_trace(go.Scatter(x=df_daily.index, y=df_daily["Close"], mode='lines', name="AAPL", marker={"size": 3})) # fill down to xaxis
    #trace1.add_trace(go.Scatter(x=df_daily.index, y=df_daily["Close"], mode='lines')) # fill to trace0 y
    #trace1 = px.area(y=e_total, x=e_total_index_dt)
    #
    #trace1.add_line(x=df_daily.index, y=df_daily["Close"])
    return {"data": [trace1],
             "layout": go.Layout(title="Wage Rigidity",
                    yaxis={"title": "% of Jobstayers With a Wage Change of Zero", "range": [min(e_total)*0.9, max(e_total)*1.1],
                            "tick0": 0, "dtick": 50},
                    xaxis={"title": "Year",
                            'rangeselector': {'buttons': list([
                                {'count': 1, 'label': '1M', 'step': 'month', 'stepmode': 'backward'},
                                {'count': 6, 'label': '6M', 'step': 'month', 'stepmode': 'backward'},
                                {'step': 'all'}]) }})}
if __name__ == '__main__':
    app.run_server(debug=True)
