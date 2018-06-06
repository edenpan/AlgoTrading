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

    summary_data.update({headers[0] : str(price[1]).strip()})
    summary_data.update({headers[1] : str(price[3]).strip()})
    summary_data.update({headers[2] : str(price[5]).strip()})
    summary_data.update({headers[3] : str(price[7]).strip()})
    summary_data.update({headers[4] : str(price[9]).strip()})
    summary_data.update({headers[5] : str(price[11]).strip()})
    summary_data.update({headers[6] : str(price[13]).strip()})
    summary_data.update({headers[7] : str(price[15]).strip()})
    summary_data.update({headers[8] : str(price[17]).strip()})
  
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

