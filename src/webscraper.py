#!/usr/bin/env python
# TODO: Improve README
# TODO: b-shares handler
# TODO: Improve REIT functions add normal multiple

from bs4 import BeautifulSoup
import os
import subprocess
import numpy as np
import re
import json
import datetime
import pandas as pd
import yfinance as yf
import requests

def get_eps(symbol="AAPL", api_token="5eb13d86ab6523.00317139", session=None):
    if session is None:
        session = requests.Session()

    url = "http://eodhistoricaldata.com/api/fundamentals/%s" % symbol

    params = {"api_token": api_token, "filter": "Earnings::Annual"}
    r = session.get(url, params=params)
    df_annual = pd.DataFrame.from_dict(r.json()).T #, skipfooter=1, parse_dates=[0], index_col=0)
    df_annual.index = pd.to_datetime(df_annual.index)
    df_annual=df_annual.iloc[::-1]
    if df_annual.index[-1].month != df_annual.index[-2].month:
        df_annual.drop(df_annual.tail(1).index,inplace=True)

    params = {"api_token": api_token, "filter": "General::CurrencyCode"}
    r = session.get(url, params=params)
    currency = r.text.strip('"')

    params = {"api_token": api_token, "filter": "Financials::Balance_Sheet::yearly"}
    r = session.get(url, params=params)
    df_financials = pd.DataFrame.from_dict(r.json()).T #, skipfooter=1, parse_dates=[0], index_col=0)
    df_financials.index = pd.to_datetime(df_financials.index)
    df_financials.index =df_financials.index + pd.offsets.MonthEnd(0) 
    df_financials =df_financials.iloc[::-1]
    df_financials["ev_delta"] = pd.to_numeric(df_financials["totalLiab"])-pd.to_numeric(df_financials["cash"])-pd.to_numeric(df_financials["shortTermInvestments"])

    params = {"api_token": api_token, "filter": "outstandingShares::annual"}
    r = session.get(url, params=params)
    df_shares = pd.DataFrame.from_dict(r.json()).T
    df_shares = df_shares.iloc[::-1]
    df_shares.index = pd.to_datetime({'year': df_shares["date"],'month': df_financials.index[0].month,'day':df_financials.index[0].day })
    df_shares["shares"] = pd.to_numeric(df_shares["sharesMln"]).apply(lambda x: x*1000000)

    df_annual["ev_delta"] = df_financials["ev_delta"].divide(df_shares["shares"])

    print(df_annual)
    return(df_annual, currency)

def yahoo_data(symbol_yhoo, start, end):
    stock = yf.Ticker(symbol_yhoo)
    try:
        yahoo_currency = stock.info["currency"]
    except Exception as ex:
        yahoo_currency = None
        print("Currency Conversion not supported/necessary.")
        print("Yahoo Error:", ex)
    df_daily = yf.download(symbol_yhoo, start, end)
    if not df_daily.empty:
        print("Received Yahoo Data.")
    return df_daily, yahoo_currency

def morningstar_data_est(symbol_morn):
    df_est_full = pd.read_html(
        r'http://financials.morningstar.com/valuate/annual-estimate-list.action?&t={}'.format(symbol_morn), keep_default_na=False)
    df_est_full = pd.concat(df_est_full)
    df_est = pd.DataFrame([[df_est_full[1][4], df_est_full[1][6]], [df_est_full[4][4], df_est_full[4][6]]], index=[
                          df_est_full[2][0], df_est_full[5][0]], columns=["Median EPS", "Mean EPS"])
    dropNames = df_est[df_est.index.values == "—"].index
    df_est.drop(dropNames, inplace=True)
    df_est.index = pd.to_datetime(df_est.index)
    df_est = df_est.apply(pd.to_numeric, errors='coerce')
    est_currency = df_est_full.iloc[2,1]
    return df_est, est_currency


def gen_symbol(symbol, country):
    symbol = symbol.upper()
    df_exchange = pd.DataFrame(index=["Germany", "Hongkong", "Japan", "France", "Canada", "UK", "Switzerland", "Australia",
                                      "Korea", "Netherlands", "Spain", "Russia", "Italy", "Belgium", "Mexiko", "Sweden", "Norway", "Finland", "Denmark"])
    df_exchange["Morningstar"] = ["XETR:", "XHKG:", "XTKS:", "XPAR:", "XTSE:", "XLON:", "XSWX:", "XASX:",
                                  "XKRX:", "XAMS:", "XMAD:", "MISX:", "XMIL:", "XBRU:", "XMEX:", "XSTO:", "XOSL:", "XHEL:", "XCSE:"]
    df_exchange["eod"] = ["XETR:", "XHKG:", "XTKS:", "XPAR:", "XTSE:", "XLON:", "XSWX:", "XASX:",
                                  "XKRX:", "XAMS:", "XMAD:", "MISX:", "XMIL:", "XBRU:", "XMEX:", "XSTO:", "XOSL:", "XHEL:", "XCSE:"]
    df_exchange["Yahoo"] = [".DE", ".HK", ".T", ".PA", ".TO", ".L", ".SW", ".AX",
                            ".KS", ".AS", ".MC", ".ME", ".MI", ".BR", ".MX", ".ST", ".OL", ".HE", ".CO"]

    if country == "USA":
        symbol_morn = symbol
        symbol_yhoo = symbol_morn
    else:
        symbol_morn = df_exchange.loc[country]["Morningstar"] + symbol
        symbol_yhoo = symbol + df_exchange.loc[country]["Yahoo"]
        if country == "UK" and symbol == "RB":
            symbol_morn = symbol_morn + "."
        if country == "Hongkong" and len(symbol_yhoo) < 7:
            symbol_yhoo = (7-len(symbol_yhoo))*"0" + symbol_yhoo
    print("Symbols: " + symbol_morn + " " + symbol_yhoo)
    return symbol_morn, symbol_yhoo


def currency_conv(df_daily, df_yearly, df_est, yahoo_currency, est_currency, currency, start, end, country):
    #start = end - datetime.timedelta(days=7)
    print(yahoo_currency,currency)
    if yahoo_currency != None and yahoo_currency != currency:
        print("Price data conversion form " +
              yahoo_currency + " to " + currency + ".")
        forex = yf.download(str(yahoo_currency) +
                            str(currency) + "=X", start=start, end=end)
        # df_daily["Close"] = df_daily["Close"].apply(
        #    lambda x: x*forex["Close"].iloc[-1])
        df_daily["Close"] = df_daily["Close"] * forex["Close"]
    if est_currency != None and len(est_currency) > 2 and est_currency != currency:
        print("Estimate data conversion form " +
              est_currency + " to " + currency + ".")
        start = datetime.date.today() - datetime.timedelta(days=7)
        forex = yf.download(str(est_currency) +
                            str(currency) + "=X", start=start, end=end)
        df_est["Median EPS"] = df_est["Median EPS"].apply(
            lambda x: x*forex["Close"].iloc[-1])
    if country == "UK":
        df_daily["Close"] = df_daily["Close"].apply(lambda x: x*(1/100))


def req_handle(country, symbol):
    symbol_morn, symbol_yhoo = gen_symbol(symbol, country)
    df_yearly, morn_currency = get_eps(symbol_morn)
    df_est, est_currency = morningstar_data_est(symbol_morn)

    start = df_yearly.index[0]
    end = datetime.date.today()
    df_daily, yahoo_currency = yahoo_data(symbol_yhoo, start, end)

    currency_conv(df_daily, df_yearly, df_est, yahoo_currency,
                  est_currency, morn_currency, start, end, country)
    return(df_daily, df_yearly, df_est, morn_currency)


if __name__ == "__main__":
    get_eps("googl")
    morningstar_data_est("AAPL")
    #req_handle("USA", "KHC", "Base")
    '''
    if False:
        #from data_processing import data_processing
        processing_request = [df_daily, df_yearly,
                              df_est, "PDD", "Base", morn_currency]
        trace1, pe, pe_norm, grw, grw_exp = data_processing(
            *processing_request)
    '''
