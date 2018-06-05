# author: chenfei
# usage: python hkex_finance.py stock_code
# coding: utf-8
from lxml import html  
import requests
from time import sleep
import json
import argparse
from collections import OrderedDict

import pandas as pd
from datetime import datetime


def get_price(code):
    
    url = "https://www1.hkex.com.hk/hkexwidget/data/getequityquote?sym={0}&token=evLtsLsBNAUVTPxtGqVeG1uj78xAa64jKHCMnMkWcVoo5HkIidDreVmzMKJ%2bZf21&lang=eng&qid=1528175147171&callback=jQuery3110305152158354391_1528175145792&_=1528175145793"
    url = url.format(code)
    ref = 'http://www.hkex.com.hk/Market-Data/Securities-Prices/Equities/Equities-Quote?sym=700&sc_lang=en'
    user = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
    response = requests.get(url,headers={"User-Agent":user, "Referer":ref})
    sleep(4)
    
    cont = response.content
    ad_cont = cont[cont.index('(')+1: -1]
    data = json.loads(ad_cont)

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
    h52 = data['data']['quote']['hi52'].encode('utf-8')
    low52 = data['data']['quote']['lo52'].encode('utf-8')
    
    u_time = data['data']['quote']['updatetime'].encode('utf-8')

    market_data = [price,prev_close,op,to,vol,cap,bid,ask,eps,pe,div,high,low,h52,low52]

    summary_data = OrderedDict()
    headers = ['Nominal Price', 'Prev close', 'Open', 'Turnover', 'Volume', 'Mkt cap', 'Bid','Ask', 'EPS(RMB)', 'P/E ratio', 'Div yield', 'High', 'Low', '52-wk high', '52-wk low']

    up_date = datetime.strptime(u_time[:-6], '%d %b %Y')

    updated_time = str(up_date)[0:10]

    summary_data.update({'Date':updated_time})

    for i in range(0,15,1):
        value = market_data[i]
        if value == '-':
            value = 'N/A'
        summary_data.update({headers[i]:value})
    
    return summary_data


if __name__=="__main__":
    
    argparser = argparse.ArgumentParser()
    argparser.add_argument('code',help = '')
    args = argparser.parse_args()
    
    code = args.code  
    summary_data = get_price(code)
    updated_time = summary_data['Date']

    price_data = pd.DataFrame.from_dict(summary_data, orient='index').T 

    file_name = code + '_hkex_' + updated_time
    price_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', index=False)

