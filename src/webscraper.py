#!/usr/bin/env python
#TODO: Clean this mess (Classes and functions)
#TODO: Labels
#TODO: Improve README, add how to use
#TODO: Fix pegc calc
#TODO: Store data and request other graph, same symbol
#TODO: b-shares handler
#TODO: improve column selection
#TODO: BUGFIX DDD,KHC,PCG,PDD
#TODO: Improve REIT functions
from bs4 import BeautifulSoup
import requests
import numpy as np
import re
import json
import matplotlib.pyplot as plt
import datetime
import pandas as pd
import yfinance as yf
import sys
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

def killer():
    plt.close("all")

def yahoo_data(symbol_yhoo,start,end):
    stock = yf.Ticker(symbol_yhoo)
    try:
        yahoo_currency = stock.info["currency"]
    except Exception as ex:
        yahoo_currency = None
        print(ex)
    df_daily = yf.download(symbol_yhoo,start,end)
    return df_daily,yahoo_currency

def morningstar_data(symbol_morn):
    url1 = 'http://financials.morningstar.com/finan/financials/getFinancePart.html?&callback=xxx&t={}'.format(symbol_morn)
    #url2 = 'http://financials.morningstar.com/finan/financials/getKeyStatPart.html?&callback=xxx&t={}'.format(symbol_morn)
    soup1 = BeautifulSoup(json.loads(re.findall(r'xxx\((.*)\)', requests.get(url1).text)[0])['componentData'], 'lxml')
    #soup2 = BeautifulSoup(json.loads(re.findall(r'xxx\((.*)\)', requests.get(url2).text)[0])['componentData'], 'lxml')

    data = []
    for i, tr in enumerate(soup1.select('tr')):
        row_data = [td.text for td in tr.select('td, th') if td.text]
        if not row_data:
            continue
        if len(row_data) < 12:
            row_data = ['Year'] + row_data
        for j, td in enumerate(row_data):
            data.append(td)

    for index, x in enumerate(data,0):
        data[index] = str(x).replace(',','')


    arr = np.array([data[1:12], data[12:23], data[24:35], data[36:47], data[48:59], data[60:71],  data[72:83], data[84:95], data[96:107], data[108:119], data[120:131], data[132:143], data[144:155], data[156:167], data[168:179],  data[180:191]])
    df_yearly = pd.DataFrame(arr.T,columns=[data[0],data[23], data[35], data[47], data[59], data[71], data[83], data[95], data[107], data[119], data[131], data[143], data[155], data[167], data[179], data[191]])
    df_yearly.drop([10], inplace=True)
    df_yearly['Year'] = pd.to_datetime(df_yearly['Year'])
    df_yearly.columns = df_yearly.columns.str.strip()
    df_yearly.set_index('Year', inplace=True)
    df_yearly = df_yearly.apply(pd.to_numeric, errors='coerce')
    return df_yearly

def morningstar_data_est(symbol_morn):
    df_est_full = pd.read_html(r'http://financials.morningstar.com/valuate/annual-estimate-list.action?&t={}'.format(symbol_morn),keep_default_na=False)
    df_est_full = pd.concat(df_est_full)

    df_est = pd.DataFrame([[df_est_full[1][4],df_est_full[1][6]],[df_est_full[4][4],df_est_full[4][6]]],index=[df_est_full[2][0],df_est_full[5][0]],columns=["Median EPS","Mean EPS"])
    dropNames = df_est[ df_est.index.values == "—" ].index
    df_est.drop(dropNames , inplace=True)
    df_est.index = pd.to_datetime(df_est.index)
    df_est = df_est.apply(pd.to_numeric, errors='coerce')

    est_time = df_est_full[2][0] + "-" + df_est_full[5][0]
    df_est_full[0][2] = est_time
    df_est_full[1][2] = df_est_full[1][2] + " " + df_est_full[2][0]
    df_est_full[2][2] = df_est_full[2][2] + " " + df_est_full[2][0]
    df_est_full[4][2] = df_est_full[4][2] + " " + df_est_full[5][0]
    df_est_full[5][2] = df_est_full[5][2] + " " + df_est_full[5][0]
    df_est_full[0].replace('', np.nan, inplace=True)
    df_est_full.dropna(axis=0, how='any', inplace=True)
    header = df_est_full.iloc[0]
    df_est_full = df_est_full[1:]
    df_est_full.rename(columns = header, inplace=True)
    df_est_full.set_index(est_time, inplace=True)
    print(df_est_full)
    est_currency = df_est_full.columns[3][:3] #TODO: Improve ecurreny selection
    return df_est, est_currency

def pegc():
    '''
    elif style == "PEGC":
        i = 0
        print("Growth Rate", "Year")
        for x in range(1, len(e_total)):
            gnumbers = ((e_total[x] - e_total[x-1]) / e_total[x-1] * 100)
            if e_total[x-1] < 0:
                print(-gnumbers, i, e_total[x-1], e_total[x])
            else:
                print(gnumbers, i, e_total[x-1], e_total[x])
            i=i+1
        s = int(input("Type Year to start multiple calculation:"))
        multiple = ((e_total[-1]/e_total.item(s))) #**(1.0/(len(e_total)-s))-1.0)*100.0
        if multiple < 0:
            print("Growth Rate: " + str(print(-100*((abs(multiple))**(1.0/(len(e_total)-s))-1.0))) + "%")
            multiple = 15
        else:
            multiple = 100*(multiple**(1.0/(len(e_total)-s))-1.0)
            print(multiple)
            if multiple < 15:
                multiple = 15
                print("Growth Rate < 15%")
            else:
                print("Growth Rate: " + str(multiple) + "%")
    '''

def gen_plt(symbol_yhoo, currency):
    plt.style.use('dark_background')
    fig1, ax = plt.subplots(figsize = (8,5))
    ax.set_title(symbol_yhoo)
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
    return fig1, ax

def req_handle(symbol,country,style):
    killer()

    df_exchange = pd.DataFrame(index=["Germany","Hongkong","Japan","France","Canada","UK","Switzerland", "Australia","Korea","Netherlands","Spain","Russia","Italy","Belgium","Mexiko","Sweden","Norway","Finland","Denmark"])
    df_exchange["Morningstar"] = ["XETR:","XHKG:","XTKS:","XPAR:","XTSE:","XLON:","XSWX:","XASX:","XKRX:","XAMS:","XMAD:","MISX:","XMIL:","XBRU:","XMEX:","XSTO:","XOSL:","XHEL:","XCSE:"]
    df_exchange["Yahoo"] = [".DE",".HK",".T",".PA",".TO",".L",".SW",".AX",".KS",".AS",".MC",".ME",".MI",".BR",".MX",".ST",".OL",".HE",".CO"]

    if country == "USA":
        symbol_morn = symbol
        symbol_yhoo = symbol_morn
    else:
        symbol_morn = df_exchange.loc[country]["Morningstar"] + symbol
        symbol_yhoo = symbol + df_exchange.loc[country]["Yahoo"]
        if country == "UK" and symbol == "RB":
            symbol_morn = symbol_morn + "."
        if country == "Hongkong" and len(symbol_yhoo)<7:
            symbol_yhoo = (7-len(symbol_yhoo))*"0" + symbol_yhoo

    df_yearly = morningstar_data(symbol_morn)
    df_est, est_currency = morningstar_data_est(symbol_morn)

    start = df_yearly.index[0]
    end = datetime.date.today()

    df_daily, yahoo_currency = yahoo_data(symbol_yhoo,start,end)

    column_name=[]
    for col in df_yearly.columns:
        column_name.append(col)

    currency = str([col for col in df_yearly.columns if 'Earn' in col])[-5:-2]
    if yahoo_currency != None and yahoo_currency !=currency:
        print("Price data conversion form " + yahoo_currency + " to " + currency + ".")
        start2 = datetime.date.today() - datetime.timedelta(days=7)
        forex = yf.download(str(yahoo_currency) + str(currency) + "=X", start=start2, end=end)
        df_daily["Close"] = df_daily["Close"].apply(lambda x: x*forex["Close"].iloc[-1])
    if est_currency != None and len(est_currency)>2 and est_currency != currency:
        print("Estimate data conversion form " + est_currency + " to " + currency + ".")
        start2 = datetime.date.today() - datetime.timedelta(days=7)
        forex = yf.download(str(est_currency) + str(currency) + "=X", start=start2, end=end)
        df_est["Median EPS"] = df_est["Median EPS"].apply(lambda x: x*forex["Close"].iloc[-1])
    if country == "UK":
        df_daily["Close"] = df_daily["Close"].apply(lambda x: x*(1/100))

    price = np.array(df_yearly.index.values)
    for x in df_est.index.values:
        if not pd.isnull(x):
            price = np.append(price, x)
    e_total = np.append(pd.to_numeric(df_yearly[column_name[5]].values, errors='coerce'),pd.to_numeric(df_est["Median EPS"].values, errors='coerce'))#TODO:remove duplicate
    thecutter = ~np.isnan(e_total)
    e_total = e_total[thecutter]

    cut = (len(price)-len(e_total))

    e_total_index = np.append(df_yearly.index.values.astype('datetime64[D]').astype(int),df_est.index.values.astype('datetime64[D]').astype(int))
    e_total_index = e_total_index[thecutter]

    df_daily["blended_earnings"] = np.interp(df_daily.index.values.astype('datetime64[D]').astype(int) , e_total_index, e_total)
    df_daily["blended_pe"] = df_daily["Close"]/df_daily["blended_earnings"]

    normal_multiple = df_daily["blended_pe"].agg(lambda x: x[x>0].median())
    #normal_multiple_deprecated = df_daily["blended_pe"].mean()
    current_pe = df_daily["blended_pe"].iloc[-1]
    for i, item in enumerate(e_total):
        if item>0:
            grw_start = i
            grw_status = True
            break
    if e_total[-1]<0:
        grw_status = False

    if grw_status:
        num_years = len(e_total)-grw_start-1
        if num_years == 1:
            print("Short Earnings Growth History.")
            grw_fut = (((e_total[-1]/e_total[-2])**(1/1))-1)*100 #TODO: improve grw_fut
        else:
            grw_fut = (((e_total[-1]/e_total[-3])**(1/2))-1)*100 #TODO: improve grw_fut
        grw = (((e_total[-1]/e_total[i])**(1/num_years))-1)*100 #(start/end)^(1/periods)-1
    else:
        grw = 0
        grw_fut = 0
    multiple = grw_fut

    if style == "PE15":
        multiple = 15.0
    elif style == "Base":
        if multiple < 15.0:
            multiple = 15.0
    elif style == "PEG85":
        if multiple <0:
            multiple = 8.5
        else:
            multiple = multiple + 8.5

    e_total_norm= e_total * normal_multiple
    df_yearly[column_name[5]] = df_yearly[column_name[5]].apply(lambda x: x*multiple)
    df_est["Median EPS"] = df_est["Median EPS"]*multiple
    e_total = np.append(pd.to_numeric(df_yearly[column_name[5]].values, errors='coerce'),pd.to_numeric(df_est["Median EPS"].values, errors='coerce'))
    e_total = e_total[~np.isnan(e_total)]
    price = price[(len(price)-len(e_total)):]
    xlabel = []
    for x in df_yearly.index:
        if not pd.isnull(x):
            xlabel.append(x.strftime('%m/%y'))
    for x in df_est.index:
        if not pd.isnull(x):
            xlabel.append(x.strftime('%m/%y'))

    fig1, ax = gen_plt(symbol_yhoo, currency)

    if style == "REIT":
        ax.set_ylabel("OCF")
        df_yearly[column_name[6]] = df_yearly[column_name[6]].apply(lambda x: x*15)
        df_yearly[column_name[10]] = df_yearly[column_name[10]]/df_yearly[column_name[8]]
        df_yearly[column_name[10]] = df_yearly[column_name[10]].apply(lambda x: x*15)
        plt.fill_between(df_yearly.index, df_yearly[column_name[10]], color = "blue")
        plt.plot(df_daily.index, df_daily["Close"], color="white")
        plt.plot(df_yearly.index, df_yearly[column_name[10]], color="grey", linewidth=3, marker="^")
        plt.plot(df_yearly.index, df_yearly[column_name[6]], color="yellow", marker="o")
        cutvar = xlabel[cut:]
        plt.xticks(price[:-1],cutvar[:-1])
        plt.ylim(0,None)
        plt.xlim(df_yearly.index[cut],price[-2])
        ax.xaxis.grid(color='white', linewidth=0.25, alpha=0.95)
    elif style == "PE-Plot":
        plt.plot(df_daily["blended_pe"],color="orange")
        if df_daily["blended_pe"].max() > 100.0 and df_daily["blended_pe"].min() < 0.0:
            plt.ylim(0,100)
        elif df_daily["blended_pe"].min() < 0.0:
            plt.ylim(0,None)
        elif df_daily["blended_pe"].max() > 100.0:
            plt.ylim(0,100)
        ax.set_ylabel("PE")
        cutvar = xlabel[cut:]
        plt.xticks(price[:-1],cutvar[:-1])
        plt.xlim(df_yearly.index[cut],price[-2])
    else:
        df_yearly[column_name[6]] = df_yearly[column_name[6]].apply(lambda x: x*multiple)
        plt.fill_between(price, e_total, color = "blue")
        plt.xticks(price,xlabel[cut:])
        plt.plot(price, e_total_norm, color="orange", marker="o")
        plt.plot(price, e_total, color="grey", linewidth=3, marker="^")
        plt.plot(df_yearly.index, df_yearly[column_name[6]], color="yellow", marker="o")
        plt.plot(df_daily.index, df_daily["Close"], color="white")
        plt.ylim(0,None)
        plt.xlim(df_yearly.index[cut],price[-1]) #df_est.index[len(df_est.index)-1])
        ax.xaxis.grid(color='white', linewidth=0.25, alpha=0.95)

    plt.savefig('graphs/plot_base.png')
    plt.clf()
    plt.cla()
    return(current_pe,normal_multiple,grw, grw_fut)
