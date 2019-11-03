#!/usr/bin/env python
#TODO: GUI
#TODO: Classes and functions
#TODO: Country Seletion for non-US Stocks
#TODO: normal_multiple + blended PE
from bs4 import BeautifulSoup
import requests
import numpy as np
import re
import json
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import pandas_datareader.data as web
from PIL import Image

print("Enter US Stock Symbol or type 'n':")
s = input()
if s == "n":
    print("Enter Morningstar-Symbol:")
    symbol_morn = input()
    print("Enter Yahoo-Symbol:")
    symbol_yhoo = input()
else:
    symbol_morn = s
    symbol_yhoo = symbol_morn

df_est = pd.read_html(r'http://financials.morningstar.com/valuate/annual-estimate-list.action?&t={}'.format(symbol_morn),keep_default_na=False)
df_est = pd.concat(df_est)
df3 = pd.DataFrame([[df_est[1][4],df_est[1][6]],[df_est[4][4],df_est[4][6]]],index=[df_est[2][0],df_est[5][0]],columns=["Median EPS","Mean EPS"])
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

url1 = 'http://financials.morningstar.com/finan/financials/getFinancePart.html?&callback=xxx&t={}'.format(symbol_morn)
url2 = 'http://financials.morningstar.com/finan/financials/getKeyStatPart.html?&callback=xxx&t={}'.format(symbol_morn)

soup1 = BeautifulSoup(json.loads(re.findall(r'xxx\((.*)\)', requests.get(url1).text)[0])['componentData'], 'lxml')
soup2 = BeautifulSoup(json.loads(re.findall(r'xxx\((.*)\)', requests.get(url2).text)[0])['componentData'], 'lxml')

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
df_price = web.DataReader(symbol_yhoo,'yahoo',start,end)
test = np.array(df.index.values)#,df3.index.values)
for x in df3.index.values:
    if not pd.isnull(x):
        test = np.append(test, x)
test2 = np.append(df[column_name[5]].values,df3["Median EPS"].values)
test2 = test2[~np.isnan(test2)]
cut = (len(test)-len(test2))
currency = str(df.columns[13])[-3:]
xlabel = []

multiple = (test2[-1]/df[column_name[5]][cut]) #**(1.0/(len(test2)-1.0))-1.0

if multiple < 0:
    print("Growth Rate: " + str(-100*((abs(multiple))**(1.0/(len(test2)-1.0))-1.0)) + "%")
    multiple = 15
else:
    multiple = (multiple**(1.0/(len(test2)-1.0))-1.0)*100
    print("Growth Rate: " + str(multiple) + "%")

print("Choose Multiple(base/peg/peg85/pegc):")

s = input()
if s == "base":
    multiple = 15.0
elif s == "peg":
    if multiple < 15.0:
        multiple = 15.0
elif s == "peg85":
    if multiple <0:
        multiple = 8.5
    else:
        multiple = multiple + 8.5
elif s == "pegc":
    i = 0
    print("Growth Rate", "Year")
    for x in range(1, len(test2)):
        gnumbers = ((test2[x] - test2[x-1]) / test2[x-1] * 100)
        if test2[x-1] < 0:
            print(-gnumbers, i, test2[x-1], test2[x])
        else:
            print(gnumbers, i, test2[x-1], test2[x])
        i=i+1
    print("Type Year to start multiple calculation:")
    s = int(input())
    multiple = ((test2[-1]/test2.item(s))) #**(1.0/(len(test2)-s))-1.0)*100.0
    if multiple < 0:
        print("Growth Rate: " + str(print(-100*((abs(multiple))**(1.0/(len(test2)-s))-1.0))) + "%")
        multiple = 15
    else:
        multiple = 100*(multiple**(1.0/(len(test2)-s))-1.0)
        print(multiple)
        if multiple < 15:
            multiple = 15
            print("Growth Rate < 15%")
        else:
            print("Growth Rate: " + str(multiple) + "%")

normal_multiple = 16.0
test3= test2 * normal_multiple
df[column_name[5]] = df[column_name[5]].apply(lambda x: x*multiple)
df3["Median EPS"] = df3["Median EPS"]*multiple
df[column_name[6]] = df[column_name[6]].apply(lambda x: x*multiple)

test2 = np.append(df[column_name[5]].values,df3["Median EPS"].values)
test2 = test2[~np.isnan(test2)]
test = test[(len(test)-len(test2)):]

for x in df.index:
    if not pd.isnull(x):
        xlabel.append(x.strftime('%m/%y'))
for x in df3.index:
    if not pd.isnull(x):
        xlabel.append(x.strftime('%m/%y'))

plt.style.use('dark_background')
f1, ax = plt.subplots(figsize = (8,5))
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
plt.xticks(test,xlabel[cut:])
plt.fill_between(test, test2, color = "blue")
plt.plot(test,test3, color="orange", marker="o")
plt.plot(test, test2, color="grey", linewidth=3, marker="^")
plt.plot(df.index, df[column_name[6]], color="yellow", marker="o")
plt.plot(df_price.index, df_price["Close"], color="white")
plt.ylim(0,None)
plt.xlim(df.index[cut],test[-1]) #df3.index[len(df3.index)-1])
ax.xaxis.grid(color='white', linewidth=0.25, alpha=0.95)
plt.savefig('Graphs/plot.png')
image = Image.open(r'Graphs/plot.png')
image.show()
'''
'''
