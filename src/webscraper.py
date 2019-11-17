#!/usr/bin/env python
#TODO: Classes and functions
#TODO: Labels
#TODO: Fix pegc calc
#TODO: Store data and request other graph, same symbol
#TODO: b-shares handler
#TODO: handler estimates-curreny != data-currency (MOWI)
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

def req_handle(symbol,country,style):
    killer()
    df = pd.DataFrame(index=["Germany","Hongkong","Japan","France","Canada","UK","Switzerland", "Australia","Korea","Netherlands","Spain","Russia","Italy","Belgium","Mexiko","Sweden","Norway","Finland","Denmark"])
    df["Morningstar"] = ["XETR:","XHKG:","XTKS:","XPAR:","XTSE:","XLON:","XSWX:","XASX:","XKRX:","XAMS:","XMAD:","MISX:","XMIL:","XBRU:","XMEX:","XSTO:","XOSL:","XHEL:","XCSE:"]
    df["Yahoo"] = [".DE",".HK",".T",".PA",".TO",".L",".SW",".AX",".KS",".AS",".MC",".ME",".MI",".BR",".MX",".ST",".OL",".HE",".CO"]
    if country == "USA":
        symbol_morn = symbol
        symbol_yhoo = symbol_morn
    else:
        symbol_morn = df.loc[country]["Morningstar"] + symbol
        symbol_yhoo = symbol + df.loc[country]["Yahoo"]
        if country == "UK" and symbol == "RB":
            symbol_morn = symbol_morn + "."
        if country == "Hongkong" and len(symbol_yhoo)<7:
            symbol_yhoo = (7-len(symbol_yhoo))*"0" + symbol_yhoo

    df_est = pd.read_html(r'http://financials.morningstar.com/valuate/annual-estimate-list.action?&t={}'.format(symbol_morn),keep_default_na=False)
    df_est = pd.concat(df_est)
    df3 = pd.DataFrame([[df_est[1][4],df_est[1][6]],[df_est[4][4],df_est[4][6]]],index=[df_est[2][0],df_est[5][0]],columns=["Median EPS","Mean EPS"])
    dropNames = df3[ df3.index.values == "—" ].index
    df3.drop(dropNames , inplace=True)
    df3.index = pd.to_datetime(df3.index)
    df3 = df3.apply(pd.to_numeric, errors='coerce')
    est_time = df_est[2][0] + "-" + df_est[5][0]
    df_est[0][2] = est_time
    df_est[1][2] = df_est[1][2] + " " + df_est[2][0]
    df_est[2][2] = df_est[2][2] + " " + df_est[2][0]
    df_est[4][2] = df_est[4][2] + " " + df_est[5][0]
    df_est[5][2] = df_est[5][2] + " " + df_est[5][0]
    df_est[0].replace('', np.nan, inplace=True)
    df_est.dropna(axis=0, how='any', inplace=True)
    header = df_est.iloc[0]
    df_est = df_est[1:]
    df_est.rename(columns = header, inplace=True)
    df_est.set_index(est_time, inplace=True)
    ecurrency = df_est.columns[3][:3]

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
    df = pd.DataFrame(arr.T,columns=[data[0],data[23], data[35], data[47], data[59], data[71], data[83], data[95], data[107], data[119], data[131], data[143], data[155], data[167], data[179], data[191]])
    df.drop([10], inplace=True)
    df['Year'] = pd.to_datetime(df['Year'])
    df.columns = df.columns.str.strip()
    df.set_index('Year', inplace=True)
    df = df.apply(pd.to_numeric, errors='coerce')

    column_name=[]
    for col in df.columns:
        column_name.append(col)

    start = df.index[0]
    end = datetime.date.today()
    stock = yf.Ticker(symbol_yhoo)
    try:
        ycurrency = stock.info["currency"]
    except Exception as ex:
        ycurrency = None
        print(ex)
    df_daily = yf.download(symbol_yhoo,start,end)
    currency = str([col for col in df.columns if 'Earn' in col])[-5:-2]
    if ycurrency != None and ycurrency !=currency:
        print(currency,ycurrency)
        start2 = datetime.date.today() - datetime.timedelta(days=7)
        forex = yf.download(str(ycurrency) + str(currency) + "=X", start=start2, end=end)
        df_daily["Close"] = df_daily["Close"].apply(lambda x: x*forex["Close"].iloc[-1])
    if ecurrency != None and ecurrency != currency:
        start2 = datetime.date.today() - datetime.timedelta(days=7)
        forex = yf.download(str(ecurrency) + str(currency) + "=X", start=start2, end=end)
        df3["Median EPS"] = df3["Median EPS"].apply(lambda x: x*forex["Close"].iloc[-1])
    if country == "UK":
        df_daily["Close"] = df_daily["Close"].apply(lambda x: x*(1/100))

    price = np.array(df.index.values) #,df3.index.values)
    for x in df3.index.values:
        if not pd.isnull(x):
            price = np.append(price, x)
    e_total = np.append(pd.to_numeric(df[column_name[5]].values, errors='coerce'),pd.to_numeric(df3["Median EPS"].values, errors='coerce'))#TODO:remove duplicate
    thecutter = ~np.isnan(e_total)
    e_total = e_total[thecutter]

    cut = (len(price)-len(e_total))
    currency = str([col for col in df.columns if 'Earn' in col])[-5:-2]
    if ycurrency != None and ycurrency !=currency:
        print(currency,ycurrency)
        start2 = datetime.date.today() - datetime.timedelta(days=7)
        forex = yf.download(str(ycurrency) + str(currency) + "=X", start=start2, end=end)
        df_daily["Close"] = df_daily["Close"].apply(lambda x: x*forex["Close"].iloc[-1])
    if country == "UK":
        df_daily["Close"] = df_daily["Close"].apply(lambda x: x*(1/100))
    xlabel = []

    e_total_index = np.append(df.index.values.astype('datetime64[D]').astype(int),df3.index.values.astype('datetime64[D]').astype(int))
    e_total_index = e_total_index[thecutter]

    df_daily["blended_earnings"] = np.interp(df_daily.index.values.astype('datetime64[D]').astype(int) , e_total_index, e_total)
    df_daily["blended_pe"] = df_daily["Close"]/df_daily["blended_earnings"]
    normal_multiple = df_daily["blended_pe"].mean()
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
        grw = (((e_total[-1]/e_total[i])**(1/num_years))-1)*100 #(start/end)^(1/periods)-1
        grw_fut = (((e_total[-1]/e_total[-3])**(1/3))-1)*100 #TODO: improve grw_fut
    else:
        grw = 0
        grw_fut = 0
    multiple = grw_fut

    if style == "Base":
        multiple = 15.0
    elif style == "PEG":
        if multiple < 15.0:
            multiple = 15.0
    elif style == "PEG85":
        if multiple <0:
            multiple = 8.5
        else:
            multiple = multiple + 8.5
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
    e_total_norm= e_total * normal_multiple
    df[column_name[5]] = df[column_name[5]].apply(lambda x: x*multiple)
    df3["Median EPS"] = df3["Median EPS"]*multiple
    df[column_name[6]] = df[column_name[6]].apply(lambda x: x*multiple)
    e_total = np.append(pd.to_numeric(df[column_name[5]].values, errors='coerce'),pd.to_numeric(df3["Median EPS"].values, errors='coerce'))
    e_total = e_total[~np.isnan(e_total)]
    price = price[(len(price)-len(e_total)):]

    for x in df.index:
        if not pd.isnull(x):
            xlabel.append(x.strftime('%m/%y'))
    for x in df3.index:
        if not pd.isnull(x):
            xlabel.append(x.strftime('%m/%y'))

    fig1, ax = gen_plt(symbol_yhoo, currency)
    plt.fill_between(price, e_total, color = "blue")
    plt.xticks(price,xlabel[cut:])
    plt.plot(price, e_total_norm, color="orange", marker="o")
    plt.plot(price, e_total, color="grey", linewidth=3, marker="^")
    plt.plot(df.index, df[column_name[6]], color="yellow", marker="o")
    plt.plot(df_daily.index, df_daily["Close"], color="white")
    plt.ylim(0,None)
    plt.xlim(df.index[cut],price[-1]) #df3.index[len(df3.index)-1])
    ax.xaxis.grid(color='white', linewidth=0.25, alpha=0.95)
    plt.savefig('graphs/plot_base.png')
    plt.clf()
    plt.cla()
    return(current_pe,normal_multiple,grw, grw_fut)
    '''
    f1, ax = gen_plt(symbol_yhoo, currency)
    plt.xticks(price,xlabel[cut:])
    plt.plot(df_daily["blended_pe"])
    plt.show()
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

def killer():
    plt.close("all")

'''
if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(ex)
        e = sys.exc_info()[0]
        print(e)
    finally:
        e = sys.exc_info()[0]
        if e != None:
            print(e)
            input("Press Enter to close ...")
'''
