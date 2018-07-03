# coding: utf-8
# author: chenfei
# usage: python yahoo_finance_market.py 0700
from lxml import html  
import requests
from time import sleep
import argparse
from collections import OrderedDict
import pandas as pd
from datetime import datetime
import os
import sys
sys.path.insert(0,  '../util')
import common

def get_price(code):
    url = "http://finance.yahoo.com/quote/%s?p=%s"%(code,code)
    response = requests.get(url)
    #sleep(1)
    parser = html.fromstring(response.text)

    summary_table = parser.xpath('//div[contains(@data-test,"summary-table")]//tr')
    quote = parser.xpath('//div[contains(@data-test,"quote-header")]//div//span[contains(@class,"Trsdu(0.3s) Fw(b)")]//text()')

    summary_data = OrderedDict()

    u_time = str(datetime.now())[0:10]
    summary_data.update({'Date':u_time})
    summary_data.update({'Symbol':code[0:4]})

    if len(quote) > 0:
        summary_data.update({'Nominal price' : str(quote[0]).strip()})
    else:
        summary_data.update({'Nominal price' : 'N/A'})

    for table_data in summary_table:
        raw_table_key = table_data.xpath('.//td[contains(@class,"C(black)")]//text()')
        raw_table_value = table_data.xpath('.//td[contains(@class,"Ta(end)")]//text()')

        table_key = str(raw_table_key[0]).strip()
        if raw_table_value[0] == u'\u221e':
            table_value = 'N/A'
        else:
            table_value = str(raw_table_value[0]).strip()

        summary_data.update({table_key:table_value})


    return summary_data


if __name__=="__main__":
    
    index = common.get_index()
    
    HSI_price_data = pd.DataFrame()
    f_data = get_price(index[0] + '.HK')
    cols = f_data.keys()

    for code in index:
        code = code + '.HK'
        summary_data = get_price(code)
        print summary_data
        price_data = pd.DataFrame.from_dict(summary_data, orient='index').T       
        HSI_price_data = pd.concat([HSI_price_data, price_data], sort=True)

    u_time = str(datetime.now())[0:10]
    if not os.path.exists('data/yahoo/'):
        os.makedirs('data/yahoo/')

    file_name = 'data/yahoo' + '/HSI_yahoo_' + u_time
    HSI_price_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', columns=cols, index=False)








