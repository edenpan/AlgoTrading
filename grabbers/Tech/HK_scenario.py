#http://www.hkex.com.hk/Market-Data/Futures-and-Options-Prices/Single-Stock/Stock-Options?sc_lang=en#&sttype=options
from __future__ import division
from datetime import datetime 
from time import sleep
from collections import OrderedDict
import os
from lxml import html  
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import timedelta
import numpy as np
import pandas as pd
import math
from scipy.stats import norm
import quandl
quandl.ApiConfig.api_key = 'FxbKCf83-WeNae8uyxQg'
                         


def get_BBands(code, lastdate, period = 20):

    stock_code = 'HKEX/' + code

    mu = 0
    sigma = 0
    net_change = 0
    change_per = 0

    last_date = datetime.strptime(lastdate,'%Y-%m-%d')
    
    right = str(last_date)
    left = str(last_date - timedelta(days = period * 3))

    try:
        price_BB = quandl.get(stock_code, start_date = left , end_date = right)
    except:
        sleep(10)
        price_BB = quandl.get(stock_code, start_date = left , end_date = right)


    if len(price_BB)==1:

        u_d = '-'
  
        quote = price_BB[-1:]['Nominal Price']
        net_change = '-'
        change_per = '-'

    elif len(price_BB)==0: #has option, but stock is still not on list


        u_d = '-'
        quote = 0.00
        net_change = '-'
        change_per = '-'

    else:
        data = np.array(list(price_BB[-period:]['Nominal Price']))
        mu = np.mean(data)

        quote = price_BB[-1:]['Nominal Price']
        quote_yes = price_BB[-2:-1]['Nominal Price']
        net_change = round(float(quote)-float(quote_yes),2)
        change_per = round(100*(float(quote)-float(quote_yes))/float(quote_yes),2)
        
        sigma = np.std(data)
        upper = mu + 2*sigma
        down = mu - 2*sigma  

        if float(quote) >= upper:
            u_d = 'up'
        elif float(quote) <= down:
            u_d = 'down'
        else:
            u_d = '-'



    return u_d,net_change,change_per,float(quote)


def price_portfolio(price_l, buy_call_strike, buy_call_number, r, q, IV_l, T, t_o, scenario):
    #price_portfolio(price_l, buy_call_strike, buy_call_number, r, q, IV_l, T, 0, 1.01)
    portfolio_position = []

    for i in range(len(buy_call_number)):

        iv = float(IV_l[i])/100

        if iv > 0 and T > 0:
            d1 = (math.log(price_l[i]*scenario/buy_call_strike[i]) + (r - q + 0.5*(iv**2))*T)/(iv*math.sqrt(T))
            d2 = d1 - iv*math.sqrt(T)
            
            if t_o==0:
                C = price_l[i]*scenario*math.exp(-1*q*(T))*norm.cdf(d1) - buy_call_strike[i]*math.exp(-1*r*(T))*norm.cdf(d2)
                portfolio_position.append(buy_call_number[i]*C)
            else:
                P = buy_call_strike[i]*math.exp(-1*r*(T))*norm.cdf(-1*d2) - price_l[i]*scenario*math.exp(-1*q*(T))*norm.cdf(-1*d1)
                portfolio_position.append(buy_call_number[i]*P)
        else:
            portfolio_position.append(0)

    position = sum(portfolio_position)

    return position


def compute_scenario(begindate, underlying, buy_call_number, buy_call_list, buy_call_strike, expiry, maturity):
    
    url = "http://www.hkex.com.hk/eng/stat/dmstat/dayrpt/dqe{0}.htm".format(begindate.replace("-", "")[2:])

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    response = webdriver.Chrome(chrome_options=chrome_options)

    response.get(url)
    sleep(10)

    settle_l = []
    IV_l = []
    price_l = []

    for i in range(len(buy_call_list)):
        try:
            o_data = response.find_element_by_name(buy_call_list[i])
        except:
            continue

        if len(underlying[i])<5:
            underlying = (5-len(underlying[i]))*'0' + underlying[i]

        u_d,net_change,change_per,price = get_BBands(underlying, begindate, 20)
        price_l.append(price)

        o_data = o_data.text.encode('utf-8').split('\n')   

        for j in range(len(o_data)):
            w = o_data[j].split()
            if len(w) == 12 and w[2] == 'C' and w[0] == expiry and float(w[1]) == buy_call_strike[i]:
                S_C = w[6]
                IV_1C = w[8]

                settle_l.append(float(S_C))
                IV_l.append(IV_1C)
                break
    
    position_0 = sum([a*b for a,b in zip(buy_call_number,settle_l)])

    r = 0.0015
    q = 0.0424
    Expiry = maturity
    T = (Expiry - int(begindate[8:10].lstrip('0')))/365

    position_1 = price_portfolio(price_l, buy_call_strike, buy_call_number, r, q, IV_l, T, 0, 1.01)
    position_5 = price_portfolio(price_l, buy_call_strike, buy_call_number, r, q, IV_l, T, 0, 1.05)
    position_10 = price_portfolio(price_l, buy_call_strike, buy_call_number, r, q, IV_l, T, 0, 1.1)
    position_20 = price_portfolio(price_l, buy_call_strike, buy_call_number, r, q, IV_l, T, 0, 1.2)
    position_30 = price_portfolio(price_l, buy_call_strike, buy_call_number, r, q, IV_l, T, 0, 1.3)

    position_m1 = price_portfolio(price_l, buy_call_strike, buy_call_number, r, q, IV_l, T, 0, 0.99)
    position_m5 = price_portfolio(price_l, buy_call_strike, buy_call_number, r, q, IV_l, T, 0, 0.95)
    position_m10 = price_portfolio(price_l, buy_call_strike, buy_call_number, r, q, IV_l, T, 0, 0.9)
    position_m20 = price_portfolio(price_l, buy_call_strike, buy_call_number, r, q, IV_l, T, 0, 0.8)
    position_m30 = price_portfolio(price_l, buy_call_strike, buy_call_number, r, q, IV_l, T, 0, 0.7)

    pos_l = [round(position_m30,2),round(position_m20,2),round(position_m10,2),round(position_m5,2),round(position_m1,2),round(position_0,2),round(position_1,2),round(position_5,2),round(position_10,2),round(position_20,2),round(position_30,2)]


    return pos_l


if __name__=="__main__":

    buy_call_number = [1,2,3]
    buy_call_list = ['CKH','CLP','HKG']
    underlying = ['1','2','3']
    buy_call_price = [1.0, 2.0, 3.0]
    buy_call_strike = [82.5, 90, 16]

    buy_call_position = sum([a*b for a,b in zip(buy_call_number,buy_call_price)])
    buy_position = buy_call_position

    dates = ['2018-07-23','2018-07-24','2018-07-25','2018-07-26','2018-07-27',]
    expiry_list = [0,0,'MAR18','APR18','MAY18','JUN18','JUL18','AUG18','SEP18','OCT18',0,0]
    special_list = ['2018-04-30', '2018-05-31', '2018-06-29', '2018-07-31']
    maturity_list = [30,30,30, 27,30,28,30, 30,30,30,30,30]

    pos_l = []

    for begindate in dates:

        m = int(begindate[5:7].lstrip('0'))
            
        if begindate in special_list:
            expiry = expiry_list[m]
        else:
            expiry = expiry_list[m-1]

        maturity = maturity_list[m-1]
        
        pos = compute_scenario(begindate, underlying, buy_call_number, buy_call_list, buy_call_strike, expiry, maturity)

        print pos
        pos_l.append(pos)
    

    b=np.array(pos_l,dtype=float)  
    print b















