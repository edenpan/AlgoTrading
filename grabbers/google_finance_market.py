# coding: utf-8
# author: chenfei
# usage: python google_finance_market.py 0700
from lxml import html  
import requests
from time import sleep
import json
import argparse
from collections import OrderedDict
from time import sleep
import pandas as pd
from datetime import datetime


def get_price(code):
   
    url = "https://www.google.com/finance?q=%s"%(code)

    response = requests.get(url,headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"})
    parser = html.fromstring(response.text)
    sleep(4)
    summary_data = OrderedDict()

    u_time = str(datetime.now())[0:10]
    summary_data.update({'Date':u_time})
    summary_data.update({'Symbol':code})
    quote1 = parser.xpath('//div[contains(@id,"entity-summary")]/div/g-card-section/div/g-card-section/div/span[1]//text()')
    summary_data.update({'Nominal price' : str(quote1[0]).strip()})

    price = parser.xpath('//div[contains(@id,"entity-summary")]/div/div[1]/g-card-section[2]/div/div//text()')
    headers = ['Open', 'High', 'Low', 'Mkt cap', 'P/E ratio', 'Div yield', 'Prev close', '52-wk high', '52-wk low']

    for i in range(1,19,2):
        value = str(price[i]).strip()
        if value == '-':
            value = 'N/A'    
    
        summary_data.update({headers[(i-1)/2] : value})

  
    return summary_data


if __name__=="__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('code',help = '')
    args = argparser.parse_args()
    
    code = args.code  
    summary_data = get_price(code)

    price_data = pd.DataFrame.from_dict(summary_data, orient='index').T   
    
    file_name = code + '_google_' + str(datetime.now())[0:10]
    price_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A',index=False)

