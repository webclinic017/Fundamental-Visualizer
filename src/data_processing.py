#!/usr/bin/env python
# TODO: function for reverting dataframes after multiplication with e_multiple
# TODO: add decile to yield plot
# TODO: Try if style==REIT set earnings_col = ocf_col
import pandas as pd
import numpy as np
import plotly.graph_objs as go


def pe_calc(df_daily, df_yearly, e_total_index_dt, e_total, grw, exp_switch, grw_exp, style, col_dict):
    e_multiple = 15
    delta = None
    year_end = []
    year_end_vals = []
    year_end_var = None
    try:
        for i, x in enumerate(df_daily.index):
            if x.month == df_yearly.index[-1].month:
                year_var = x.year
                if year_var != year_end_var:
                    year_end_var = year_var
                    year_end.append(x)
                if x.year == df_yearly.index[-1].year:
                    delta = i+1
                    break

        for x in year_end:
            temp_var = df_daily["Close"].loc[df_daily.index == x]
            year_end_vals.append(temp_var.values[0])

        # Required because of forecasting data
        while len(year_end_vals) < 12:
            year_end_vals.append(year_end_vals[-1])

        df_yield = pd.DataFrame(index=df_daily.index[:delta])

    except Exception as ex:
        df_yield = pd.DataFrame()
        print("df_yield end generation failed: " + str(ex))

    df_daily["blended_earnings"] = np.interp(df_daily.index.values.astype(
        'datetime64[D]').astype(int), e_total_index_dt, e_total)
    df_daily["blended_pe"] = df_daily["Close"]/df_daily["blended_earnings"]
    df_daily["e_yield"] = df_daily["blended_earnings"]/df_daily["Close"]

    #normal_multiple_deprecated = df_daily["e_yield"].mean()
    normal_multiple = df_daily["blended_pe"].agg(lambda x: x[x > 0].median())
    current_pe = df_daily["blended_pe"].iloc[-1]
    if exp_switch:
        e_multiple = grw_exp
    else:
        e_multiple = grw

    if style == "PE15":
        e_multiple = 15.0
    elif e_multiple != None and not pd.isnull(e_multiple):
        if style == "Base":
            if e_multiple < 15.0:
                e_multiple = 15.0
        elif style == "PEG85":
            if e_multiple < 0:
                e_multiple = 8.5
            else:
                e_multiple = e_multiple + 8.5
    else:
        e_multiple = 15

    return e_multiple, normal_multiple, current_pe, df_yield, year_end_vals


def grw_calc(e_total):
    grw = 0
    grw_exp = 0
    for i, item in enumerate(e_total):
        if item > 0:
            grw_start = i
            grw_status = True
            break
    if e_total[-1] < 0:
        grw_status = False
        print("No Earnings, not a suitable Ticker.")

    if grw_status:
        num_years = len(e_total)-grw_start-1
        if num_years == 1:
            print("Short Earnings Growth History.")
            # TODO: improve grw_exp
            grw_exp = (((e_total[-1]/e_total[-2])**(1/1))-1)*100
        else:
            # TODO: improve grw_exp
            if e_total[-3] < 0:
                grw_exp = (((e_total[-1]/e_total[-2])**(1/1))-1)*100
            else:
                grw_exp = (((e_total[-1]/e_total[-3])**(1/2))-1)*100
        if num_years == 0:
            grw = None
            grw_exp = None
        else:
            grw = (((e_total[-1]/e_total[i])**(1/num_years))-1) * \
                100  # (start/end)^(1/periods)-1
    else:
        grw = 0
        grw_exp = 0
    return grw, grw_exp


def gen_xlabel(df_yearly, df_est):
    # TODO: Implement solution with e_total_index_dt
    xlabel = []
    for x in df_yearly.index:
        if not pd.isnull(x):
            xlabel.append(x.strftime('%m/%y'))
    for x in df_est.index:
        if not pd.isnull(x):
            xlabel.append(x.strftime('%m/%y'))

    return xlabel


def likely_deprecated(df_est):
    for x in df_est.index.values:
        if not pd.isnull(x):
            pass
        else:
            pass
            #print("**DEBUG-PRINT** pd.isnull(for x in df_est.index.values) == True")


def gen_plt(df_yearly, df_daily, df_yield, df_est, e_total, e_total_norm, e_total_index_dt, style, currency, symbol, col_dict, e_multiple, year_end):
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

    trace_base.layout.title = symbol.upper()
    trace_ratio.layout.title = symbol.upper() + " - Yield Graph"
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
    trace_ratio.layout.yaxis.tickformat = ',.0%'
    trace_ratio.update_yaxes(hoverformat=",.2%")

    return trace_base, trace_ratio


def data_processing(df_daily, df_yearly, df_est, symbol, style, currency, exp_switch):

    col_dict = {"e": "epsActual"}

    # TODO: implement col_dict in data_processing
    e_total = np.append(pd.to_numeric(df_yearly[col_dict["e"]].values, errors='coerce'), pd.to_numeric(
        df_est["Median EPS"].values, errors='coerce'))
    e_total_index_int = np.append(df_yearly.index.values.astype('datetime64[D]').astype(
        int), df_est.index.values.astype('datetime64[D]').astype(int))
    e_total_index_dt = np.append(df_yearly.index.values, df_est.index.values)

    nan_cut = ~np.isnan(e_total)
    e_total = e_total[nan_cut]
    len_cut = len(e_total_index_dt)-len(e_total)
    # TODO: Improve cutting
    if len_cut > 0:
        print(df_est["Median EPS"])
        est_empty = False
        for x in pd.isnull(df_est["Median EPS"]):
            if x == True:
                est_empty = True
        print("Testing if estimates are empty, result: ", est_empty)
        if est_empty:
            e_total_index_dt = e_total_index_dt[:-len_cut]
            e_total_index_int = e_total_index_int[:-len_cut]
            print("Cutting back to front.")
        else:
            e_total_index_dt = e_total_index_dt[len_cut:]
            e_total_index_int = e_total_index_int[len_cut:]
            print("Cutting front to back.")

    # TODO: check and then remove this
    likely_deprecated(df_est)

    try:
        grw, grw_exp = grw_calc(e_total)
    except Exception as ex:
        grw, grw_exp = [0, 0]
        print("Growth Calc failed: " + str(ex))
    try:
        e_multiple, normal_multiple, current_pe, df_yield, year_end = pe_calc(
            df_daily, df_yearly, e_total_index_int, e_total, grw, exp_switch, grw_exp, style, col_dict)
    except Exception as ex:
        e_multiple, normal_multiple, current_pe, df_yield, year_end = [
            15, None, None, None, None]
        print("PE Calc failed: " + str(ex))

    df_yearly[col_dict["e"]] = df_yearly[col_dict["e"]].apply(
        lambda x: x*e_multiple)
    df_est["Median EPS"] = df_est["Median EPS"]*e_multiple

    e_total_norm = e_total * normal_multiple
    e_total = e_total * e_multiple
    e_total = e_total[~np.isnan(e_total)]  # TODO: check for redundancy
    e_total_index_dt = e_total_index_dt[(len(e_total_index_dt)-len(e_total)):]

    #self.disp_pe["text"] = str(round(pe, 2))
    #self.disp_pe_norm["text"] = str(round(pe_norm, 2))
    #self.disp_grw["text"] = str(round(grw, 2)) + " %"
    #self.disp_grw_exp["text"] = str(round(grw_exp, 2)) + " %"

    # TODO: gen_plt better not as function?
    try:
        trace_base, trace_ratio = gen_plt(df_yearly, df_daily, df_yield, df_est, e_total, e_total_norm,
                                          e_total_index_dt, style, currency, symbol, col_dict, e_multiple, year_end)
    except Exception as ex:
        print("Plot generation failed:" + str(ex))

    try:
        round_lst = [current_pe, normal_multiple, grw, grw_exp]
        for i, x in enumerate(round_lst):
            if x != None:
                round_lst[i] = str(round(x, 2))
        current_pe, normal_multiple, grw, grw_exp = round_lst
    except Exception as ex:
        print("Exception: " + str(ex))

    try:
        grw, grw_exp = grw + " %", grw_exp + " %"
    except Exception as ex:
        print("Probably no earnings: " + str(ex))
    print(current_pe, normal_multiple, grw, grw_exp)
    # str(round(current_pe, 2)), str(round(normal_multiple, 2)), (str(round(grw, 2)) + " %"), (str(round(grw_exp, 2)) + " %"

    return trace_base, trace_ratio, current_pe, normal_multiple, grw, grw_exp
    # return(df_yearly,df_daily,df_est,e_total,e_total_norm,e_total_index_dt,style,currency,symbol,col_dict, e_multiple)
