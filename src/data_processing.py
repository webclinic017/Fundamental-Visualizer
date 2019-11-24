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

def gen_plt(df_yearly,df_daily,df_est,e_total,e_total_norm,e_total_index_dt,style,currency,symbol,col_dict,e_multiple):
    #TODO: Improve this function
    cut = (len(e_total_index_dt)-len(e_total))
    xlabel = gen_xlabel(df_yearly,df_est)
    trace1 = go.Figure()
    trace1.layout.title= symbol.upper()
    ranger={"x":[],"y":[]}
    hvrtxt = {"div":[],"eps":[],"pe_norm":[],"ocf":[],"price":[],"pe":[]}
    for x in df_daily["Close"]:
        hvrtxt["price"].append(round(x,2))
    for x in df_daily["blended_pe"]:
        hvrtxt["pe"].append(round(x,2))
    for x in  df_yearly[col_dict["div"]]:
        hvrtxt["div"].append(x)
    for x in e_total:
        hvrtxt["eps"].append(round(x/e_multiple,2))
    for x in e_total_norm:
        hvrtxt["pe_norm"].append("Price @ Normal Multiple: " + str(round(x,2)))
    if style == "REIT":
        df_yearly[col_dict["div"]] = df_yearly[col_dict["div"]].apply(lambda x: x*15)
        df_yearly[col_dict["ocf"]] = df_yearly[col_dict["ocf"]]/df_yearly[col_dict["shrs"]]
        for x in df_yearly[col_dict["ocf"]]:
            hvrtxt["ocf"].append(round(x,2))
        df_yearly[col_dict["ocf"]] = df_yearly[col_dict["ocf"]].apply(lambda x: x*15)
        ranger["x"].append(df_yearly.index.min())
        ranger["x"].append(df_yearly.index.max())
        ranger["y"].append(df_yearly[col_dict["ocf"]].min())
        ranger["y"].append(df_yearly[col_dict["ocf"]].max())
        trace1.add_trace(go.Scatter(
                        x=df_yearly.index,
                        y=df_yearly[col_dict["ocf"]],
                        name="OCF/FFO",
                        hoverinfo="x+text+name",
                        hovertext=hvrtxt["ocf"],
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
        trace1.add_trace(go.Scatter(
                        x=df_yearly.index,
                        y=df_yearly[col_dict["div"]],
                        name="Dividend",
                        hoverinfo="x+text+name",
                        hovertext=hvrtxt["div"],
                        marker=dict(
                            color='yellow',
                            size=8),
                        line=dict(color='yellow', width=3),
                        opacity=0.8))
        trace1.add_trace(go.Scatter(
                        x=df_daily.index,
                        y=df_daily["Close"],
                        hoverinfo="x+text+name",
                        hovertext=hvrtxt["price"],
                        name="Price",
                        line_color='white'))
        trace1.layout.xaxis.range = [ranger["x"][0],df_daily.index.max()]
        df_yearly[col_dict["div"]] = df_yearly[col_dict["div"]].apply(lambda x: x*(1/15))
        df_yearly[col_dict["ocf"]] = df_yearly[col_dict["ocf"]].apply(lambda x: x*(1/15))
        df_yearly[col_dict["ocf"]] = df_yearly[col_dict["ocf"]]*df_yearly[col_dict["shrs"]]

    elif style == "PE-Plot":
        ranger["x"].append(df_daily.index.min())
        ranger["x"].append(df_daily.index.max())
        ranger["y"].append(df_daily["blended_pe"].min())
        ranger["y"].append(df_daily["blended_pe"].max())
        trace1.add_trace(go.Scatter(
                        x=df_daily.index,
                        y=df_daily["blended_pe"],
                        hoverinfo="x+text+name",
                        hovertext=hvrtxt["pe"],
                        line_color='orange',
                        name="PE"))
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
                        hoverinfo="x+text+name",
                        hovertext=hvrtxt["eps"],
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

        trace1.add_trace(go.Scatter(
                        x=pd.to_datetime(e_total_index_dt),
                        y=e_total_norm,
                        name="Normal PE",
                        hoverinfo="x+text+name",
                        hovertext=hvrtxt["pe_norm"],
                        marker=dict(
                            color='orange',
                            size=8),
                        line=dict(color='orange', width=3),
                        opacity=0.8))
        trace1.add_trace(go.Scatter(
                        x=pd.to_datetime(df_yearly.index),
                        y=df_yearly[col_dict["div"]],
                        name="Dividend",
                        hoverinfo="x+text+name",
                        hovertext=hvrtxt["div"],
                        marker=dict(
                            color='yellow',
                            size=8),
                        line=dict(color='yellow', width=3),
                        opacity=0.8))
        trace1.add_trace(go.Scatter(
                        x=(df_daily.index),
                        y=df_daily["Close"],
                        hoverinfo="x+text+name",
                        hovertext=hvrtxt["price"],
                        name="Price",
                        line_color='white'))
        df_yearly[col_dict["div"]] = df_yearly[col_dict["div"]].apply(lambda x: x*(1/e_multiple))
        trace1.layout.xaxis.range = [ranger["x"][0],ranger["x"][1]]

    df_yearly[col_dict["e"]] = df_yearly[col_dict["e"]].apply(lambda x: x*(1/e_multiple))
    df_est["Median EPS"] = df_est["Median EPS"]*(1/e_multiple)

    #TODO: Put in layout
    trace1.layout.template = 'plotly_dark'
    trace1.layout.plot_bgcolor= 'rgb(35,35,35)'
    trace1.layout.paper_bgcolor='rgb(35,35,35)'
    #trace1.layout.xaxis=dict(showgrid=False)
    #trace1.layout.yaxis=dict(showgrid=False)
    trace1.layout.xaxis.nticks = len(e_total_index_dt)
    trace1.layout.xaxis.tick0 = pd.to_datetime(e_total_index_dt[0])
    trace1.layout.height=575
    if style == "PE-Plot":
        trace1.update_yaxes(title_text="PE");
    else:
        trace1.update_yaxes(title_text=currency)
    trace1.layout.yaxis.autorange= True
    trace1.layout.yaxis.rangemode= 'nonnegative'
    #trace1.layout.xaxis.mirror=True
    #trace1.layout.xaxis.ticks='outside'
    trace1.layout.yaxis.showline=True
    trace1.layout.xaxis.zerolinecolor = "rgb(255, 255, 255)"
    trace1.layout.xaxis.gridcolor = "rgb(35,35,35)"
    trace1.layout.yaxis.zerolinecolor = "rgb(255, 255, 255)"
    trace1.layout.xaxis.linecolor = "rgb(255, 255, 255)"
    trace1.layout.yaxis.linecolor = "rgb(35,35,35)"
    trace1.layout.yaxis.gridcolor = "rgb(35,35,35)"
    #tickmode = 'array',
    #tickvals = pd.to_datetime(e_total_index_dt),
    #ticktext =  xlabel

    return trace1,ranger

def data_processing(df_daily ,df_yearly, df_est, symbol, style, currency):
    earnings_col = df_yearly.filter(like='Earn').columns[0]
    ocf_col = df_yearly.filter(like='Operating Cash').columns[0]
    dividend_col = df_yearly.filter(like='Divid').columns[0]
    shares_col = df_yearly.filter(like='Shares').columns[0]
    col_dict = {"e" :earnings_col,"ocf": ocf_col,"div": dividend_col,"shrs": shares_col}
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

            #self.disp_pe["text"] = str(round(pe, 2))
        #self.disp_pe_norm["text"] = str(round(pe_norm, 2))
        #self.disp_grw["text"] = str(round(grw, 2)) + " %"
        #self.disp_grw_exp["text"] = str(round(grw_exp, 2)) + " %"

    #TODO: gen_plt better not as function?
    trace1,range = gen_plt(df_yearly,df_daily,df_est,e_total,e_total_norm,e_total_index_dt,style,currency,symbol,col_dict, e_multiple)

    return trace1, str(round(current_pe, 2)), str(round(normal_multiple, 2)), (str(round(grw, 2))+ " %"), (str(round(grw_exp, 2))+ " %")
    #return(df_yearly,df_daily,df_est,e_total,e_total_norm,e_total_index_dt,style,currency,symbol,col_dict, e_multiple)
