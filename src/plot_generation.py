import plotly.graph_objs as go
import pandas as pd

def gen_plt(df_yearly, df_daily, df_yield, df_est, e_total, e_total_norm, e_total_index_dt, metric, currency, symbol, col_dict, e_multiple, year_end):
    # TODO: Improve this function
    trace_base = go.Figure()
    trace_ratio = go.Figure()
    traces = [trace_base, trace_ratio]

    trace_base.add_trace(go.Scatter(
    x=pd.to_datetime(e_total_index_dt),
    y=e_total,
    name="EPS",
    hoverinfo="x+text+name",
    marker=dict(
        color='white',
        size=9,
        line=dict(
            color='grey',
            width=2
        )),
    line=dict(color='grey', width=4),
    fill='tozeroy',
    fillcolor='rgb(55,91,187)'))

    trace_base.add_trace(go.Scatter(
        x=pd.to_datetime(e_total_index_dt),
        y=e_total_norm,
        name="Normal PE",
        hoverinfo="x+text+name",
        marker=dict(
            color='orange',
            size=8),
        line=dict(color='orange', width=3),
        opacity=0.8))

    trace_base.add_trace(go.Scatter(
        x=(df_daily.index),
        y=df_daily["Close"],
        hoverinfo="x+text+name",
        name="Price",
        line_color='white'))

    trace_ratio.add_trace(go.Scatter(
        x=df_daily.index,
        y=df_daily["blended_pe"],
        line=dict(color='SteelBlue', width=1.5),
        name="Earnings"))

    trace_base.layout.title = symbol.upper()
    trace_ratio.layout.title = symbol.upper() + " - PE Plot"
    for x in traces:
        x.layout.template = 'plotly_dark'
        x.layout.plot_bgcolor = 'rgb(35,35,35)'
        x.layout.paper_bgcolor = 'rgb(35,35,35)'
    for x in traces:
        x.layout.height = 575
        x.layout.yaxis.showline = True
        x.layout.xaxis.zerolinecolor = "rgb(255, 255, 255)"
        x.layout.xaxis.gridcolor = "rgb(35,35,35)"
        x.layout.yaxis.zerolinecolor = "rgb(255, 255, 255)"
        x.layout.xaxis.linecolor = "rgb(35,35,35)"
        x.layout.yaxis.linecolor = "rgb(35,35,35)"
        x.layout.yaxis.gridcolor = "rgb(35,35,35)"

    # trace_base.layout.xaxis.mirror=True
    # trace_base.layout.xaxis.ticks='outside'
    #tickmode = 'array',
    #tickvals = pd.to_datetime(e_total_index_dt),
    #ticktext =  xlabel
    trace_base.update_yaxes(title_text=currency)
    trace_base.layout.yaxis.autorange = True
    trace_base.layout.yaxis.rangemode = 'nonnegative'
    trace_ratio.layout.yaxis.range = [5, 40]
    trace_ratio.layout.yaxis.rangemode = 'nonnegative'


    return trace_base, trace_ratio