# coding: utf-8
# author: chenfei 
# usage: python etnet_finance_HSI.py
from lxml import html  
import requests
import argparse
from time import sleep
from collections import OrderedDict
import pandas as pd
from datetime import datetime
import os
import sys


def get_price(code):
    
    url = "https://www.etnet.com.hk/www/eng/stocks/realtime/quote.php?code=%s"%(code)
    ref = "https://www.etnet.com.hk/www/eng/stocks/realtime/quote.php?code=%s"%(code)
    response = requests.get(url, headers = {"Referer":ref,"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"})

    parser = html.fromstring(response.text)

    summary_data = OrderedDict()
    
    u_time = str(datetime.now())[0:10]
    summary_data.update({'Date':u_time})
    summary_data.update({'Symbol':code})

    summary_table = parser.xpath('//div[contains(@id,"StkDetailMainBox")]//td[contains(@class,"B")]')
    quote = parser.xpath('//div[contains(@id,"StkDetailMainBox")]//td[contains(@class,"A")]//span[contains(@class,"Price")]//text()')
    
    if len(quote) > 0:
        summary_data.update({'Nominal price' : str(quote[0].strip())})
    else:
        summary_data.update({'Nominal price' : 'N/A'})

    for table_data in summary_table:
        raw_table_key = table_data.xpath('.//text()')
        raw_table_value = table_data.xpath('.//span[contains(@class,"Num")]//text()')
        
        if len(raw_table_value)>0:
            if raw_table_value[0] == u'\xa0':
                table_value = 'N/A'
            elif str(raw_table_value[0]).strip()=='/--' or str(raw_table_value[0]).strip()=='--':
                table_value = 'N/A'
            else:
                table_value = str(raw_table_value[0]).strip()
        else:
            table_value = 'N/A'

        table_key = str(raw_table_key[0]).strip()
        
        summary_data.update({table_key:table_value})

    for i in range(1,60,2):
        raw_table_key = parser.xpath('//div[contains(@id,"StkList")]//li[%d]//text()'%i)
        raw_table_value = parser.xpath('//div[contains(@id,"StkList")]//li[%d]//text()'%(i+1))

        if len(raw_table_value)>0:
            if str(raw_table_value[0]).strip()=='/--' or str(raw_table_value[0]).strip()=='--':
                table_value = 'N/A'
            else:
                table_value = str(raw_table_value[0]).strip()
        else:
            table_value = 'N/A'

        table_key = str(raw_table_key[0]).strip()
        
        summary_data.update({table_key:table_value})

    del summary_data['Currency']
    del summary_data['Eligible for CAS']
    del summary_data['Eligible for VCM']        
    del summary_data['BoardLot']
    del summary_data['Listing Date']
    del summary_data['Listing Price'] 
 
    return summary_data

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
    f_data = get_price(index[0])
    cols = f_data.keys()
    
    for code in index:
        summary_data = get_price(code)
        print summary_data
        price_data = pd.DataFrame.from_dict(summary_data, orient='index').T       
        HSI_price_data = pd.concat([HSI_price_data, price_data], sort=True)

    u_time = str(datetime.now())[0:10]
    if not os.path.exists('data/etnet/'):
        os.makedirs('data/etnet/')

    file_name = 'data/etnet' + '/HSI_etnet_' + u_time
    HSI_price_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', columns=cols, index=False)







