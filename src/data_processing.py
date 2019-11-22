#!/usr/bin/env python
#TODO: function for reverting dataframes after multiplication with e_multiple
import pandas as pd
import numpy as np
import plotly.graph_objs as go

def pe_calc(df_daily, e_total_index_dt, e_total, grw_exp, style):
    df_daily["blended_earnings"] = np.interp(df_daily.index.values.astype('datetime64[D]').astype(int) , e_total_index_dt, e_total)
    df_daily["blended_pe"] = df_daily["Close"]/df_daily["blended_earnings"]

    #normal_multiple_deprecated = df_daily["blended_pe"].mean()
    normal_multiple = df_daily["blended_pe"].agg(lambda x: x[x>0].median())
    current_pe = df_daily["blended_pe"].iloc[-1]
    e_multiple = grw_exp

    if style == "PE15":
        e_multiple = 15.0
    elif style == "Base":
        if e_multiple < 15.0:
            e_multiple = 15.0
    elif style == "PEG85":
        if e_multiple <0:
            e_multiple = 8.5
        else:
            e_multiple = e_multiple + 8.5

    return e_multiple, normal_multiple, current_pe

def grw_calc(e_total):
    for i, item in enumerate(e_total):
        if item>0:
            grw_start = i
            grw_status = True
            break
    if e_total[-1]<0:
        grw_status = False
        print("No Earnings, not a suitable Ticker.")

    if grw_status:
        num_years = len(e_total)-grw_start-1
        if num_years == 1:
            print("Short Earnings Growth History.")
            grw_exp = (((e_total[-1]/e_total[-2])**(1/1))-1)*100 #TODO: improve grw_exp
        else:
            grw_exp = (((e_total[-1]/e_total[-3])**(1/2))-1)*100 #TODO: improve grw_exp
        grw = (((e_total[-1]/e_total[i])**(1/num_years))-1)*100 #(start/end)^(1/periods)-1
    else:
        grw = 0
        grw_exp = 0
    return grw, grw_exp

def gen_xlabel(df_yearly,df_est):
    #TODO: Implement solution with e_total_index_dt
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

def base_plt(symbol, currency):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize = (8,5))
    ax.set_title(symbol)
    ax.set_ylabel(currency)
    #ax.spines["top"].set_visible(False)
    #ax.spines["right"].set_visible(False)
    #ax.spines["bottom"].set_visible(False)
    #ax.spines["left"].set_visible(False)
    #ax.get_xaxis().tick_bottom()
    #ax.get_yaxis().tick_left()
    #ax.set_axisbelow(True)
    #ax.yaxis.grid(color='gray', linewidth=0.25)
    ax.xaxis.grid(color='white', linewidth=0.25, alpha=0.9)
    return fig, ax

def gen_plt(df_yearly,df_daily,df_est,e_total,e_total_norm,e_total_index_dt,style,currency,symbol,col_dict,e_multiple):
    #TODO: Improve this function
    cut = (len(e_total_index_dt)-len(e_total))
    fig, ax = base_plt(symbol, currency)
    xlabel = gen_xlabel(df_yearly,df_est)
    trace1 = go.Figure()
    ranger={"x":[],"y":[]}
    if style == "REIT":
        df_yearly[col_dict["div"]] = df_yearly[col_dict["div"]].apply(lambda x: x*15)
        df_yearly[col_dict["ofc"]] = df_yearly[col_dict["ofc"]]/df_yearly[col_dict["shrs"]]
        df_yearly[col_dict["ofc"]] = df_yearly[col_dict["ofc"]].apply(lambda x: x*15)
        ranger["x"].append(df_yearly.index.min())
        ranger["x"].append(df_yearly.index.max())
        ranger["y"].append(df_yearly[col_dict["ofc"]].min())
        ranger["y"].append(df_yearly[col_dict["ofc"]].max())
        trace1.add_trace(go.Scatter(
                        x=df_yearly.index,
                        y=df_yearly[col_dict["ofc"]],
                        name="OCF/FFO",
                        line_color='blue',
                        fill='tozeroy'))
        trace1.add_trace(go.Scatter(
                        x=df_daily.index,
                        y=df_daily["Close"],
                        name="Price",
                        line_color='white',
                        opacity=0.8))
        trace1.add_trace(go.Scatter(
                        x=df_yearly.index,
                        y=df_yearly[col_dict["div"]],
                        name="Dividend",
                        line_color='yellow',
                        opacity=0.8))
        df_yearly[col_dict["div"]] = df_yearly[col_dict["div"]].apply(lambda x: x*(1/15))
        df_yearly[col_dict["ofc"]] = df_yearly[col_dict["ofc"]].apply(lambda x: x*(1/15))
        df_yearly[col_dict["ofc"]] = df_yearly[col_dict["ofc"]]*df_yearly[col_dict["shrs"]]

    elif style == "PE-Plot":
        ranger["x"].append(df_daily.index.min())
        ranger["x"].append(df_daily.index.max())
        ranger["y"].append(df_daily["blended_pe"].min())
        ranger["y"].append(df_daily["blended_pe"].max())
        trace1.add_trace(go.Scatter(
                        x=df_daily.index,
                        y=df_daily["blended_pe"],
                        name="PE",
                        line_color='orange'))
    else:
        ranger["x"].append(pd.to_datetime(e_total_index_dt.min()))
        ranger["x"].append(pd.to_datetime(e_total_index_dt.max()))
        ranger["y"].append((e_total.min()))
        ranger["y"].append((e_total.max()))
        df_yearly[col_dict["div"]] = df_yearly[col_dict["div"]].apply(lambda x: x*e_multiple)
        trace1.add_trace(go.Scatter(
                        x=pd.to_datetime(e_total_index_dt),
                        y=e_total,
                        name="EPS",
                        line_color='blue',
                        fill='tozeroy'))
        trace1.add_trace(go.Scatter(
                        x=(df_daily.index),
                        y=df_daily["Close"],
                        name="Price",
                        line_color='white',
                        opacity=0.8))
        trace1.add_trace(go.Scatter(
                        x=pd.to_datetime(e_total_index_dt),
                        y=e_total_norm,
                        name="Normal PE",
                        line_color='orange',
                        opacity=0.8))
        trace1.add_trace(go.Scatter(
                        x=pd.to_datetime(df_yearly.index),
                        y=df_yearly[col_dict["div"]],
                        name="Dividend",
                        line_color='yellow',
                        opacity=0.8))
        df_yearly[col_dict["div"]] = df_yearly[col_dict["div"]].apply(lambda x: x*(1/e_multiple))

    df_yearly[col_dict["e"]] = df_yearly[col_dict["e"]].apply(lambda x: x*(1/e_multiple))
    df_est["Median EPS"] = df_est["Median EPS"]*(1/e_multiple)
    trace1.layout.template = 'plotly_dark'
    return trace1,ranger

def data_processing(df_daily ,df_yearly, df_est, symbol, style, currency):
    earnings_col = df_yearly.filter(like='Earn').columns[0]
    ocf_col = df_yearly.filter(like='Operating Cash').columns[0]
    dividend_col = df_yearly.filter(like='Divid').columns[0]
    shares_col = df_yearly.filter(like='Shares').columns[0]
    col_dict = {"e" :earnings_col,"ofc": ocf_col,"div": dividend_col,"shrs": shares_col}
    #TODO: implement col_dict in data_processing

    e_total = np.append(pd.to_numeric(df_yearly[col_dict["e"]].values, errors='coerce'),pd.to_numeric(df_est["Median EPS"].values, errors='coerce'))
    e_total_index_int = np.append(df_yearly.index.values.astype('datetime64[D]').astype(int),df_est.index.values.astype('datetime64[D]').astype(int))
    e_total_index_dt = np.append(df_yearly.index.values,df_est.index.values)

    nan_cut = ~np.isnan(e_total)
    e_total = e_total[nan_cut]
    len_cut = len(e_total_index_dt)-len(e_total)
    if len_cut >0:
        e_total_index_dt = e_total_index_dt[:-len_cut]
        e_total_index_int = e_total_index_int[:-len_cut]

    #TODO: check and then remove this
    likely_deprecated(df_est)

    grw, grw_exp = grw_calc(e_total)
    e_multiple, normal_multiple, current_pe = pe_calc(df_daily, e_total_index_int, e_total, grw_exp, style)

    df_yearly[col_dict["e"]] = df_yearly[col_dict["e"]].apply(lambda x: x*e_multiple)
    df_est["Median EPS"] = df_est["Median EPS"]*e_multiple

    e_total_norm= e_total * normal_multiple
    e_total = e_total * e_multiple
    e_total = e_total[~np.isnan(e_total)] #TODO: check for redundancy
    e_total_index_dt = e_total_index_dt[(len(e_total_index_dt)-len(e_total)):]

    #TODO: gen_plt better not as function?
    trace1,range = gen_plt(df_yearly,df_daily,df_est,e_total,e_total_norm,e_total_index_dt,style,currency,symbol,col_dict, e_multiple)
    return trace1,range
    #return(df_yearly,df_daily,df_est,e_total,e_total_norm,e_total_index_dt,style,currency,symbol,col_dict, e_multiple)
