from bs4 import BeautifulSoup
import requests
import re
import json
import pandas as pd

url1 = 'http://financials.morningstar.com/finan/financials/getFinancePart.html?&callback=xxx&t=XETR:BAS'
url2 = 'http://financials.morningstar.com/finan/financials/getKeyStatPart.html?&callback=xxx&t=XETR:BAS'

soup1 = BeautifulSoup(json.loads(re.findall(r'xxx\((.*)\)', requests.get(url1).text)[0])['componentData'], 'lxml')
soup2 = BeautifulSoup(json.loads(re.findall(r'xxx\((.*)\)', requests.get(url2).text)[0])['componentData'], 'lxml')

def print_table(soup):
    for i, tr in enumerate(soup.select('tr')):
        row_data = [td.text for td in tr.select('td, th') if td.text]
        if not row_data:
            continue
        if len(row_data) < 12:
            row_data = ['X'] + row_data
        for j, td in enumerate(row_data):
            if j==0:
                print('{: >30}'.format(td), end='|')
            else:
                print('{: ^12}'.format(td), end='|')
        print()


df = pd.read_json(print_table(soup1))
print(df)
#print()
#print_table(soup2)
