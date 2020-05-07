#!/usr/bin/env python
# TODO: function for reverting dataframes after multiplication with e_multiple
# TODO: add decile to yield plot
# TODO: Try if metric==REIT set earnings_col = ocf_col
import pandas as pd
import numpy as np
from plot_generation import gen_plt



def pe_calc(df_daily, df_yearly, e_total_index_dt, e_total, grw, mc_ev, grw_exp, metric, col_dict):
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
    #print(df_daily["blended_ev"])
    df_daily["blended_pe"] = df_daily["Close"]/df_daily["blended_earnings"]
    df_daily["e_yield"] = df_daily["blended_earnings"]/df_daily["Close"]

    #normal_multiple_deprecated = df_daily["e_yield"].mean()
    normal_multiple = df_daily["blended_pe"].agg(lambda x: x[x > 0].median())
    current_pe = df_daily["blended_pe"].iloc[-1]
    if mc_ev:
        pass
        #e_multiple = grw_exp
    else:
        pass
        #e_multiple = grw
    if grw<15:
        e_multiple = 15
    else:
        e_multiple = grw

    if metric == "PE15":
        e_multiple = 15.0
    elif e_multiple != None and not pd.isnull(e_multiple):
        if metric == "Base":
            if e_multiple < 15.0:
                e_multiple = 15.0
        elif metric == "PEG85":
            if e_multiple < 0:
                e_multiple = 8.5
            else:
                e_multiple = e_multiple + 8.5

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

def data_processing(df_daily, df_yearly, df_est, symbol, metric,  mc_ev,currency,):

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
            df_daily, df_yearly, e_total_index_int, e_total, grw, mc_ev, grw_exp, metric, col_dict)
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
    df_daily["blended_ev"] = np.interp(df_daily.index.values.astype(
    'datetime64[D]').astype(int), df_yearly.index.values.astype(
    'datetime64[D]').astype(int), df_yearly["ev_delta"])
    df_daily["price_adj"] = df_daily["Close"] +df_daily["blended_ev"]
    print(df_daily["blended_ev"])
    print(df_daily["Close"])
    if mc_ev:
        df_daily["Close"] = df_daily["price_adj"]
        print("EV")
    print(df_daily["Close"])
    # TODO: gen_plt better not as function?
    try:
        trace_base, trace_ratio = gen_plt(df_yearly, df_daily, df_yield, df_est, e_total, e_total_norm,
                                          e_total_index_dt, metric, currency, symbol, col_dict, e_multiple, year_end)
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

    df_yearly[col_dict["e"]] = df_yearly[col_dict["e"]].apply(
        lambda x: x*(1/e_multiple))
    df_est["Median EPS"] = df_est["Median EPS"]*(1/e_multiple)
    if mc_ev:
        df_daily["Close"] = df_daily["Close"] -df_daily["blended_ev"]

    return trace_base, trace_ratio, current_pe, normal_multiple, grw, grw_exp
    # return(df_yearly,df_daily,df_est,e_total,e_total_norm,e_total_index_dt,metric,currency,symbol,col_dict, e_multiple)
