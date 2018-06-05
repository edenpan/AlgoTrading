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

def get_price(code):
    url = "http://finance.yahoo.com/quote/%s?p=%s"%(code,code)
    response = requests.get(url)
    sleep(4)
    parser = html.fromstring(response.text)

    summary_table = parser.xpath('//div[contains(@data-test,"summary-table")]//tr')
    quote_price = parser.xpath('//div[contains(@data-test,"quote-header")]//div//span[contains(@class,"Trsdu(0.3s) Fw(b)")]//text()')

    summary_data = OrderedDict()
    summary_data.update({'Nominal price':str(quote_price[0])})

    for table_data in summary_table:
        raw_table_key = table_data.xpath('.//td[contains(@class,"C(black)")]//text()')
        raw_table_value = table_data.xpath('.//td[contains(@class,"Ta(end)")]//text()')

        table_key = str(raw_table_key[0]).strip()
        table_value = str(raw_table_value[0]).strip()
        summary_data.update({table_key:table_value})

    price_data = pd.DataFrame(summary_data, index=[str(datetime.now())[0:10]])   
    return price_data

if __name__=="__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('code',help = '')
    args = argparser.parse_args()
    
    code = args.code + '.HK'
    price_data = get_price(code)
        
    file_name = args.code + '_yahoo_' + str(datetime.now())[0:10]
    price_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A')

