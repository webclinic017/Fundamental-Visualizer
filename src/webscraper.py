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
import subprocess
import numpy as np
import re
import json
import datetime
import pandas as pd
import yfinance as yf
import wget

def yahoo_data(symbol_yhoo,start,end):
    stock = yf.Ticker(symbol_yhoo)
    try:
        yahoo_currency = stock.info["currency"]
    except Exception as ex:
        yahoo_currency = None
        print("Currency Conversion not supported/necessary.")
        print("Yahoo Error:", ex)
    df_daily = yf.download(symbol_yhoo,start,end)
    return df_daily,yahoo_currency

def morningstar_data(symbol_morn):
    #TODO: add handler for no returned data
    #print(symbol_morn)
    mylink = 'http://financials.morningstar.com/finan/financials/getFinancePart.html?&callback=xxx&t={}'.format(symbol_morn)
    #url2 = 'http://financials.morningstar.com/finan/financials/getKeyStatPart.html?&callback=xxx&t={}'.format(symbol_morn)

    subprocess.call(["wget", '-O', 'data.txt', '-S', mylink])

    f = open('data.txt', 'r')
    print(f.read())

    f = open('data.txt', 'r')
    obj=re.findall(r'xxx\((.*)\)', f.read())[0]
    obj = json.loads(obj)['componentData']
    soup1 = BeautifulSoup(obj,'lxml')

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

    print(data)
    x= [data[0],data[12], data[24], data[36], data[48], data[60], data[72], data[84], data[96], data[108], data[120], data[132], data[144], data[156], data[168], data[180]]
    arr = [data[1:12], data[13:24], data[25:36], data[37:48], data[49:60], data[61:72],  data[73:84], data[85:96], data[97:108], data[109:120], data[121:132], data[133:144], data[145:156], data[157:168], data[169:180],  data[181:192]]
    print(x[6])
    index = data[1:12]
    df_yearly = pd.DataFrame(columns=x)
    print(df_yearly)
    i=0
    for col in df_yearly:
        df_yearly[col] = arr[i]
        print(arr[i])
        i=i+1
    print(df_yearly)
    df_yearly.drop([10], inplace=True)
    df_yearly['Year'] = pd.to_datetime(df_yearly['Year'])
    df_yearly.columns = df_yearly.columns.str.strip()
    df_yearly.set_index('Year', inplace=True)
    df_yearly = df_yearly.apply(pd.to_numeric, errors='coerce')
    print(df_yearly)
    earnings_col = [col for col in df_yearly.columns if 'Earn' in col]
    print(df_yearly.index)
    print(df_yearly[earnings_col])
    morn_currency = str(earnings_col)[-5:-2]
    return df_yearly, morn_currency

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
    est_currency = df_est_full.columns[3][:3] #TODO: Improve est_curreny selection
    return df_est, est_currency

def pegc():
    #TODO: implement this
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

def gen_symbol(symbol,country):
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
    return symbol_morn, symbol_yhoo

def currency_conv(df_daily,df_yearly,df_est,yahoo_currency,est_currency,currency,end,country):
    start = end - datetime.timedelta(days=7)
    if yahoo_currency != None and yahoo_currency !=currency:
        print("Price data conversion form " + yahoo_currency + " to " + currency + ".")
        forex = yf.download(str(yahoo_currency) + str(currency) + "=X", start=start, end=end)
        df_daily["Close"] = df_daily["Close"].apply(lambda x: x*forex["Close"].iloc[-1])
    if est_currency != None and len(est_currency)>2 and est_currency != currency:
        print("Estimate data conversion form " + est_currency + " to " + currency + ".")
        start = datetime.date.today() - datetime.timedelta(days=7)
        forex = yf.download(str(est_currency) + str(currency) + "=X", start=start, end=end)
        df_est["Median EPS"] = df_est["Median EPS"].apply(lambda x: x*forex["Close"].iloc[-1])
    if country == "UK":
        df_daily["Close"] = df_daily["Close"].apply(lambda x: x*(1/100))

def req_handle(country,symbol,style):
    symbol_morn, symbol_yhoo = gen_symbol(symbol,country)
    df_yearly, morn_currency = morningstar_data(symbol_morn)
    df_est, est_currency = morningstar_data_est(symbol_morn)

    start = df_yearly.index[0]
    end = datetime.date.today()
    df_daily, yahoo_currency = yahoo_data(symbol_yhoo,start,end)

    currency_conv(df_daily,df_yearly,df_est,yahoo_currency,est_currency,morn_currency,end,country)

    return(df_daily,df_yearly,df_est,morn_currency)
