#!/usr/bin/env python
# TODO: function for reverting dataframes after multiplication with e_multiple
# TODO: add decile to yield plot
# TODO: Modularize gen_plt, pe_calc
# TODO: add handler for irregular forcasting data (2018,2019,2021)
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
            year_end_vals.append(df_daily["Close"][-1])

        df_yield = pd.DataFrame(index=df_daily.index[:delta])

        df_yield["blended_ocf"] = np.interp(df_yield.index.values.astype(
            'datetime64[D]').astype(int), df_yearly.index.values.astype(
            'datetime64[D]').astype(int), df_yearly[col_dict["ocf"]])
        df_yield["blended_fcf"] = np.interp(df_yield.index.values.astype(
            'datetime64[D]').astype(int), df_yearly.index.values.astype(
            'datetime64[D]').astype(int), df_yearly[col_dict["fcf"]])
        df_yield["blended_div"] = np.interp(df_yield.index.values.astype(
            'datetime64[D]').astype(int), df_yearly.index.values.astype(
            'datetime64[D]').astype(int), df_yearly[col_dict["div"]])

        df_yield["ocf_yield"] = df_yield["blended_ocf"] / \
            df_daily["Close"][:delta]
        df_yield["fcf_yield"] = df_yield["blended_fcf"] / \
            df_daily["Close"][:delta]
        df_yield["div_yield"] = df_yield["blended_div"] / \
            df_daily["Close"][:delta]

    except Exception as ex:
        df_yield = pd.DataFrame()
        print("df_yield end generation failed: " + str(ex))

    df_daily["blended_earnings"] = np.interp(df_daily.index.values.astype(
        'datetime64[D]').astype(int), e_total_index_dt, e_total)
    df_daily["blended_pe"] = df_daily["Close"]/df_daily["blended_earnings"]
    df_daily["e_yield"] = df_daily["blended_earnings"]/df_daily["Close"]

    #normal_multiple_deprecated = df_daily["e_yield"].mean()
    normal_multiple = df_daily["blended_pe"].agg(lambda x: x[x > 0].median())
    normal_multiple_ocf = (1/df_yield["ocf_yield"]).agg(
        lambda x: x[x > 0].median())
    if style == "REIT":
        current_pe = (1/(df_yield["ocf_yield"].iloc[-1]))
    else:
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
        elif style == "REIT":
            if e_multiple < 15:
                e_multiple = 15
    else:
        e_multiple = 15

    return e_multiple, normal_multiple, normal_multiple_ocf, current_pe, df_yield, year_end_vals


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
    try:
        #cut = (len(e_total_index_dt)-len(e_total))
        #xlabel = gen_xlabel(df_yearly, df_est)
        ranger = {"x": [], "y": []}
        hvrtxt = {"div": [], "eps": [], "pe_norm": [],
                  "ocf": [], "price": [], "pe": [], "ocf_norm": []}
        for x in df_daily["Close"]:
            hvrtxt["price"].append(round(x, 2))
        for x in df_daily["e_yield"]:
            hvrtxt["pe"].append(round(x, 2))
        for x in df_yearly[col_dict["div"]]:
            hvrtxt["div"].append(x)
        print("Created Hovertext.")
    except Exception as ex:
        print("Failed to generate Hovertext: " + str(ex))
    try:
        for i, x in enumerate(e_total):
            hvrtxt["eps"].append(
                "EPS: " + str(round(x/e_multiple, 2)) + "<br>Price @ PE=G: " + str(round(x, 2)) + "<br>Difference: " + str(round(((x/year_end[i])-1)*100, 2)) + "%")
        for i, x in enumerate(e_total_norm):
            hvrtxt["pe_norm"].append(
                "Price @ Normal Multiple: " + str(round(x, 2)) + "<br>Difference: " + str(round(((x/year_end[i])-1)*100, 2)) + "%")
    except Exception as ex:
        print("Hovertext w/ year_end failed: " + str(ex))
        for i, x in enumerate(e_total):
            hvrtxt["eps"].append(
                "EPS: " + str(round(x/e_multiple, 2)) + "<br>Price @ PE=G: " + str(round(x, 2)))
        for x in e_total_norm:
            hvrtxt["pe_norm"].append(
                "Price @ Normal Multiple: " + str(round(x, 2)))

    if style == "REIT":
        #TODO: Improve naming
        df_yearly[col_dict["div"]] = df_yearly[col_dict["div"]].apply(
            lambda x: x*e_multiple)
        df_yearly[col_dict["ocf"]] = df_yearly[col_dict["ocf"]].apply(
            lambda x: x*e_multiple)
        try:
            if 10 > len(df_yearly[col_dict["ocf"]]):
                print(year_end)
                year_end = year_end[(10-len(df_yearly[col_dict["ocf"]])):]
                print(year_end)
            for i, x in enumerate(df_yearly[col_dict["ocf"]]):
                hvrtxt["ocf"].append(
                    "OCF: " + str(round(x/e_multiple, 2)) + "<br>Price @ PE=G: " + str(round(x, 2)) + "<br>Difference: " + str(round(((x/year_end[i])-1)*100, 2)) + "%")
            for i, x in enumerate(df_yearly["ocf_norm"]):
                hvrtxt["ocf_norm"].append(
                    "Price @ Normal Multiple: " + str(round(x, 2)) + "<br>Difference: " + str(round(((x/year_end[i])-1)*100, 2)) + "%")
        except Exception as ex:
            print("OCF Hovertext w/ year_end failed: " + str(ex))
        ranger["x"].append(df_yearly.index.min())
        ranger["x"].append(df_yearly.index.max())
        ranger["y"].append(df_yearly[col_dict["ocf"]].min())
        ranger["y"].append(df_yearly[col_dict["ocf"]].max())
        trace_base.add_trace(go.Scatter(
            x=df_yearly.index,
            y=df_yearly[col_dict["ocf"]],
            name="OCF",
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
        trace_base.add_trace(go.Scatter(
            x=df_yearly.index,
            y=df_yearly["ocf_norm"],
            name="Normal P/OCF",
            hoverinfo="x+text+name",
            hovertext=hvrtxt["ocf_norm"],
            marker=dict(
                color='orange',
                size=8),
            line=dict(color='orange', width=3),
            opacity=0.8))
        trace_base.add_trace(go.Scatter(
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
        trace_base.add_trace(go.Scatter(
            x=df_daily.index,
            y=df_daily["Close"],
            hoverinfo="x+text+name",
            hovertext=hvrtxt["price"],
            name="Price",
            line_color='white'))
        trace_base.layout.xaxis.range = [ranger["x"][0], df_daily.index.max()]
        df_yearly[col_dict["div"]] = df_yearly[col_dict["div"]].apply(
            lambda x: x*(1/e_multiple))
        df_yearly[col_dict["ocf"]] = df_yearly[col_dict["ocf"]].apply(
            lambda x: x*(1/e_multiple))
    else:
        trace_base.add_trace(go.Scatter(
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
        try:
            for x in df_yearly[col_dict["ocf"]]:
                hvrtxt["ocf"].append(round(x, 2))
            df_yearly[col_dict["ocf"]] = df_yearly[col_dict["ocf"]].apply(
                lambda x: x*e_multiple)
            df_yearly[col_dict["fcf"]] = df_yearly[col_dict["fcf"]].apply(
                lambda x: x*e_multiple)
            trace_base.add_trace(go.Scatter(
                x=df_yearly.index,
                y=df_yearly[col_dict["ocf"]],
                name="OCF",
                hoverinfo="x+text+name",
                hovertext=hvrtxt["ocf"],
                line=dict(color='crimson', width=2),
                marker=dict(
                    color='white',
                    size=9,
                    line=dict(
                        color='crimson',
                        width=2
                    )),
                fill='tozeroy',
                fillcolor='rgba(174, 200, 240, 0.3)',
                visible='legendonly', opacity=0.8))
            #'rgba(99, 125, 165, 1)'
            trace_base.add_trace(go.Scatter(
                x=df_yearly.index,
                y=df_yearly[col_dict["fcf"]],
                name="FCF",
                line=dict(color='limegreen', width=2),
                marker=dict(
                    color='white',
                    size=9,
                    line=dict(
                        color='limegreen',
                        width=2
                    )),
                fill='tozeroy',
                fillcolor='rgba(174, 200, 240, 0.3)',
                visible='legendonly', opacity=0.8))
            df_yearly[col_dict["ocf"]] = df_yearly[col_dict["ocf"]].apply(
                lambda x: x*(1/e_multiple))
            df_yearly[col_dict["fcf"]] = df_yearly[col_dict["fcf"]].apply(
                lambda x: x*(1/e_multiple))
        except Exception as ex:
            print("OCF plot failed: " + str(ex))
        trace_base.add_trace(go.Scatter(
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
        try:
            df_yearly[col_dict["div"]] = df_yearly[col_dict["div"]].apply(
                lambda x: x*e_multiple)
            trace_base.add_trace(go.Scatter(
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
            df_yearly[col_dict["div"]] = df_yearly[col_dict["div"]].apply(
                lambda x: x*(1/e_multiple))
        except Exception as ex:
            print(ex)
        trace_base.add_trace(go.Scatter(
            x=(df_daily.index),
            y=df_daily["Close"],
            hoverinfo="x+text+name",
            hovertext=hvrtxt["price"],
            name="Price",
            line_color='white'))
        print("Added data to plot.")
        try:
            ranger["x"].append(pd.to_datetime(e_total_index_dt.min()))
            ranger["x"].append(pd.to_datetime(e_total_index_dt.max()))
            ranger["y"].append((e_total.min()))
            ranger["y"].append((e_total.max()))
            trace_base.layout.xaxis.range = [ranger["x"][0], ranger["x"][1]]
        except Exception as ex:
            print("Couldn't set x Limits.")
    try:
        ranger["x"].append(df_daily.index.min())
        ranger["x"].append(df_daily.index.max())
        ranger["y"].append(df_daily["e_yield"].min())
        ranger["y"].append(df_daily["e_yield"].max())
        trace_ratio.add_trace(go.Scatter(
            x=df_daily.index,
            y=df_daily["e_yield"],
            line=dict(color='SteelBlue', width=1.5),
            name="Earnings"))
        trace_ratio.add_trace(go.Scatter(
            x=df_yield.index,
            y=df_yield["ocf_yield"],
            line=dict(color='rgba(220, 20, 60,0.8)', width=1.5),
            name="OCF", visible='legendonly',)),
        trace_ratio.add_trace(go.Scatter(
            x=df_yield.index,
            y=df_yield["fcf_yield"],
            line=dict(color='rgba(50, 205, 50, 0.8)', width=1.5),
            visible='legendonly',
            name="FCF"))
        trace_ratio.add_trace(go.Scatter(
            x=df_yield.index,
            y=df_yield["div_yield"],
            line=dict(color='rgba(255, 255, 0,0.8)', width=1.5),
            name="Dividend")),
        maxvar = 1.0
        minvar = 0.0
        extrema_list = []
        for x in df_yield.loc[:, 'div_yield':].columns:
            if 1 > df_yield[x].max() >= 0:
                extrema_list.append(df_yield[x].max())
            if 1 > df_yield[x].min() >= 0:
                extrema_list.append(df_yield[x].min())
        extrema_list.append(df_daily["e_yield"].max())
        extrema_list.append(df_daily["e_yield"].min())
        if max(extrema_list) < maxvar:
            maxvar = max(extrema_list)
        if min(extrema_list) > minvar:
            minvar = min(extrema_list)-0.001
        trace_ratio.update_yaxes(title_text="Yield")
        print(minvar, maxvar)
        trace_ratio.layout.yaxis.range = [minvar, maxvar]
    except Exception as ex:
        print("Ratio-Plot failed: " + str(ex))

    df_yearly[col_dict["e"]] = df_yearly[col_dict["e"]].apply(
        lambda x: x*(1/e_multiple))
    df_est["Median EPS"] = df_est["Median EPS"]*(1/e_multiple)
    df_yearly[col_dict["ocf"]] = df_yearly[col_dict["ocf"]] * \
        df_yearly[col_dict["shrs"]]

    #TODO: Put in layout
    for x in traces:
        x.layout.template = 'plotly_dark'
        x.layout.plot_bgcolor = 'rgb(35,35,35)'
        x.layout.paper_bgcolor = 'rgb(35,35,35)'
    # trace_base.layout.xaxis=dict(showgrid=False)
    # trace_base.layout.yaxis=dict(showgrid=False)
    try:
        trace_base.layout.xaxis.nticks = len(e_total_index_dt)
        trace_base.layout.xaxis.tick0 = pd.to_datetime(e_total_index_dt[0])
    except Exception as ex:
        print("Couldn't modify ticks: " + str(ex))

    trace_base.layout.title = symbol.upper()
    trace_ratio.layout.title = symbol.upper() + " - Yield Graph"
    for x in traces:
        x.layout.height = 575
        x.layout.yaxis.showline = True
        x.layout.xaxis.zerolinecolor = "rgb(35,35,35)"
        x.layout.xaxis.gridcolor = "rgb(35,35,35)"
        x.layout.yaxis.zerolinecolor = "rgb(35,35,35)"
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
    trace_base.layout.yaxis.zerolinecolor = "rgb(250,250,250)"

    trace_ratio.layout.yaxis.tickformat = ',.1%'
    trace_ratio.update_yaxes(hoverformat=",.2%")

    return trace_base, trace_ratio


def data_processing(df_daily, df_yearly, df_est, symbol, style, currency, exp_switch):

    earnings_col = df_yearly.filter(like='Earn').columns[0]
    fcf_col = df_yearly.filter(like='Free Cash Flow Per').columns[0]
    ocf_col = df_yearly.filter(like='Operating Cash Fl').columns[0]
    dividend_col = df_yearly.filter(like='Divid').columns[0]
    shares_col = df_yearly.filter(like='Shares').columns[0]
    col_dict = {"e": earnings_col, "ocf": ocf_col,
                "div": dividend_col, "shrs": shares_col, "fcf": fcf_col}

    # ocf/share
    df_yearly[col_dict["ocf"]] = df_yearly[col_dict["ocf"]] / \
        df_yearly[col_dict["shrs"]]

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
        if style == "REIT":
             grw, grw_exp = grw_calc(df_yearly[col_dict["ocf"]])
        else:
            grw, grw_exp = grw_calc(e_total)
    except Exception as ex:
        grw, grw_exp = [0, 0]
        print("Growth Calc failed: " + str(ex))
    try:
        e_multiple, normal_multiple, normal_multiple_ocf, current_pe, df_yield, year_end = pe_calc(
            df_daily, df_yearly, e_total_index_int, e_total, grw, exp_switch, grw_exp, style, col_dict)
    except Exception as ex:
        e_multiple, normal_multiple, normal_multiple_ocf, current_pe, df_yield, year_end = [
            15, None, None, None, None, None]
        print("PE Calc failed: " + str(ex))

    df_yearly[col_dict["e"]] = df_yearly[col_dict["e"]].apply(
        lambda x: x*e_multiple)
    df_est["Median EPS"] = df_est["Median EPS"]*e_multiple

    if style == "REIT":
        print(normal_multiple_ocf)
        df_yearly["ocf_norm"] = df_yearly[col_dict["ocf"]].apply(
            lambda x: x*normal_multiple_ocf)

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
    # str(round(current_pe, 2)), str(round(normal_multiple, 2)), (str(round(grw, 2)) + " %"), (str(round(grw_exp, 2)) + " %"

    if style == "REIT":
        return trace_base, trace_ratio, current_pe, str(round(normal_multiple_ocf, 2)), grw, grw_exp
    else:
        return trace_base, trace_ratio, current_pe, normal_multiple, grw, grw_exp
    # return(df_yearly,df_daily,df_est,e_total,e_total_norm,e_total_index_dt,style,currency,symbol,col_dict, e_multiple)
