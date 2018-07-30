# author: chenfei
# usage: python hkex_finance.py 0700
# coding: utf-8
from lxml import html  
import requests
from time import sleep
import json
import argparse
from collections import OrderedDict
import pandas as pd
from datetime import datetime
import os

def get_price(code):
    
    token = getToken(code)
    url = "https://www1.hkex.com.hk/hkexwidget/data/getequityquote?sym={0}&token={1}&lang=eng&qid=1528175147171&callback=jQuery3110305152158354391_1528175145792&_=1528175145793"
    url = url.format(code,token)
    ref = 'http://www.hkex.com.hk/Market-Data/Securities-Prices/Equities/Equities-Quote?sym=700&sc_lang=en'
    user = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
    response = requests.get(url,headers={"User-Agent":user, "Referer":ref})
    
    cont = response.content
    #print cont
    ad_cont = cont[cont.index('(')+1: -1]
    data = json.loads(ad_cont)

    summary_data = OrderedDict()
    headers = ['Nominal Price', 'Prev close', 'Open', 'Turnover', 'Volume', 'Mkt cap', 'Bid','Ask', 'EPS(RMB)', 'P/E ratio', 'Div yield', 'High', 'Low', '52-wk high', '52-wk low']
    u_time = str(datetime.now())[0:10]
    summary_data.update({'Date':u_time})
    summary_data.update({'Symbol':code})

    price = data['data']['quote']['ls'].encode('utf-8')
    prev_close = data['data']['quote']['hc'].encode('utf-8')
    op = data['data']['quote']['op'].encode('utf-8')
    to = data['data']['quote']['am'].encode('utf-8') + data['data']['quote']['am_u'].encode('utf-8')
    vol = data['data']['quote']['vo'].encode('utf-8') + data['data']['quote']['vo_u'].encode('utf-8')
    cap = data['data']['quote']['mkt_cap'].encode('utf-8') + data['data']['quote']['mkt_cap_u'].encode('utf-8')
    bid = data['data']['quote']['bd'].encode('utf-8')
    ask = data['data']['quote']['as'].encode('utf-8')
    eps = data['data']['quote']['eps']
    pe = data['data']['quote']['pe'].encode('utf-8')
    div = data['data']['quote']['div_yield'].encode('utf-8') + "%"

    high = data['data']['quote']['hi'].encode('utf-8')
    low = data['data']['quote']['lo'].encode('utf-8')
    high52 = data['data']['quote']['hi52'].encode('utf-8')
    low52 = data['data']['quote']['lo52'].encode('utf-8')

    market_data = [price,prev_close,op,to,vol,cap,bid,ask,eps,pe,div,high,low,high52,low52]

    for i in range(0,15,1):
        value = market_data[i]
        if value == '-':
            value = 'N/A'
        summary_data.update({headers[i]:value})       
    
    return summary_data


def getToken(code):
    orgUrl = 'http://www.hkex.com.hk/Market-Data/Securities-Prices/Equities/Equities-Quote?sym={0}&sc_lang=en'
    accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    user = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
    orgUrl = orgUrl.format(code)
    res1 = requests.get(orgUrl,headers={"User-Agent":user, "Accept":accept})
    cont = res1.content
    searchToken = 'Encrypted-Token'
    cont2 = cont[cont.find(searchToken):cont.find(searchToken)+200 ]
    cont3 = cont2[cont2.find('return') + 8:]
    token = cont3[:cont3.find("\"")]
    return token

def get_index():

    link = "http://warrants-hk.credit-suisse.com/gb/underlying/hsi_gb.cgi"
    f = requests.get(link)
    s = f.text
    parser = html.fromstring(s)

    index = parser.xpath('//*[@id="mainContent"]/table/tbody/tr')

    s_index = []
    for mem in index:
        ticker = mem.xpath('.//td[1]//text()')
        s_index.append(str(ticker[0])[1:])

    return s_index


if __name__=="__main__":
    
    index = get_index()

    HSI_price_data = pd.DataFrame()
    f_data = get_price(index[0].lstrip('0'))
    cols = f_data.keys()

    for code in index:
        summary_data = get_price(code.lstrip('0'))
        print summary_data
        price_data = pd.DataFrame.from_dict(summary_data, orient='index').T       
        HSI_price_data = pd.concat([HSI_price_data, price_data], sort=True)

    u_time = str(datetime.now())[0:10]
    if not os.path.exists('data/hkex/'):
        os.makedirs('data/hkex/')

    file_name = 'data/hkex' + '/HSI_hkex_' + u_time
    HSI_price_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', columns=cols, index=False)



