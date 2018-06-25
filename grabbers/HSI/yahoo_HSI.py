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


def get_index():

    url = "https://www.bloomberg.com/quote/HSI:IND/members"

    response = requests.get(url)
    s=response.text
    parser = html.fromstring(s)

    index = parser.xpath('//div[@class="index-members"]/div[1]/div[@class="index-members"]/div[@class="security-summary"]')

    s_index = []
    i = 0

    for mem in index:
        ticker = mem.xpath('.//a[contains(@class,"ticker")]//text()')
        temp = str(ticker[0])[:-3]
        if len(temp)<4:
            temp = (4-len(temp))*'0' + temp

        s_index.append(temp)
        i = i + 1

    return s_index


if __name__=="__main__":
    
    index = get_index()

    first_summary_data = get_price(index[0]+'.HK')
    cols = first_summary_data.keys()
    updated_time = first_summary_data['Date']
    HSI_price_data = pd.DataFrame.from_dict(first_summary_data, orient='index').T 
    
    for code in index[1:]:
        code = code + '.HK'
        summary_data = get_price(code)
        price_data = pd.DataFrame.from_dict(summary_data, orient='index').T       
        HSI_price_data = pd.concat([HSI_price_data, price_data], sort=True)

    directory = updated_time
    if not os.path.exists('data/yahoo/'):
        os.makedirs('data/yahoo/')

    file_name = 'data/yahoo' + '/HSI_yahoo_' + updated_time
    HSI_price_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A',columns=cols, index=False)








