from bs4 import BeautifulSoup
import requests
import numpy as np
import re
import json
import matplotlib.pyplot as plt
import pandas as pd

data = []
symbol = 'AAPL'

url1 = 'http://financials.morningstar.com/finan/financials/getFinancePart.html?&callback=xxx&t={}'.format(symbol)
url2 = 'http://financials.morningstar.com/finan/financials/getKeyStatPart.html?&callback=xxx&t={}'.format(symbol)

soup1 = BeautifulSoup(json.loads(re.findall(r'xxx\((.*)\)', requests.get(url1).text)[0])['componentData'], 'lxml')
soup2 = BeautifulSoup(json.loads(re.findall(r'xxx\((.*)\)', requests.get(url2).text)[0])['componentData'], 'lxml')

for i, tr in enumerate(soup1.select('tr')):
    row_data = [td.text for td in tr.select('td, th') if td.text]
    if not row_data:
        continue
    if len(row_data) < 12:
        row_data = ['Year'] + row_data
    for j, td in enumerate(row_data):
        data.append(td)

arr = np.array([data[1:12], data[12:23], data[24:35], data[36:47], data[48:59], data[60:71],  data[72:83], data[84:95], data[96:107], data[108:119], data[120:131], data[132:143], data[144:155], data[156:167], data[168:179],  data[180:191]])
df = pd.DataFrame(arr.T,columns=[data[0],data[23], data[35], data[47], data[59], data[71], data[83], data[95], data[107], data[119], data[131], data[143], data[155], data[167], data[179], data[191]])
df.drop([10], inplace=True)
df['Year'] = pd.to_datetime(df['Year'])
df.columns = df.columns.str.strip()
df.set_index('Year', inplace=True)
#print(df.iloc[ : , 9 ])
#print(df['Shares Mil'])
# gca stands for 'get current axis'
#ax = plt.gca()
column_name=[]
for col in df.columns:
    column_name.append(col)

f1, ax = plt.subplots(figsize = (10,5))
#ax.xaxis_date()
ax.autoscale_view()
plt.plot(df[column_name[4]])
plt.show()
