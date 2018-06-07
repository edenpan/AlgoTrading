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

def get_price(code):
    
    url = "https://www.etnet.com.hk/www/eng/stocks/realtime/quote.php?code=%s"%(code)
    ref = "https://www.etnet.com.hk/www/eng/stocks/realtime/quote.php?code=%s"%(code)
    response = requests.get(url, headers = {"Referer":ref,"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"})
    sleep(1)

    parser = html.fromstring(response.text)

    summary_data = OrderedDict()
    
    u_time = str(datetime.now())[0:10]
    summary_data.update({'Date':u_time})

    #updated_time = parser.xpath('//div[@id="DivContentRight"]/div[@class="DivBoxStyleE shadow"][1]/div[2]/div[@class="remark"]/text()')

    #t = updated_time[0].strip()[-16:-6]
    #up_date = datetime.strptime(t, '%d/%m/%Y')
    #updated_time = str(up_date)[0:10]
    #summary_data.update({'Date':updated_time})

    summary_data.update({'Symbol':code})

    summary_table = parser.xpath('//div[contains(@id,"StkDetailMainBox")]//td[contains(@class,"B")]')
    quote_price = parser.xpath('//div[contains(@id,"StkDetailMainBox")]//td[contains(@class,"A")]//span[contains(@class,"Price")]//text()')

    summary_data.update({'Nominal price':str(quote_price[0].strip())})

    for table_data in summary_table:
        raw_table_key = table_data.xpath('.//text()')
        raw_table_value = table_data.xpath('.//span[contains(@class,"Num")]//text()')
        
        if len(raw_table_value)>0:
            if str(raw_table_value[0]).strip()=='/--' or str(raw_table_value[0]).strip()=='--':
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
    first_summary_data = get_price(index[0])
    cols = first_summary_data.keys()
    updated_time = first_summary_data['Date']
    HSI_price_data = pd.DataFrame.from_dict(first_summary_data, orient='index').T 
    
    for code in index[1:]:
        summary_data = get_price(code)
        price_data = pd.DataFrame.from_dict(summary_data, orient='index').T       
        HSI_price_data = pd.concat([HSI_price_data, price_data], sort=True)
    
    directory = updated_time
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_name = directory + '/HSI_etnet_' + updated_time

    file_name = 'HSI_etnet_' + updated_time
    HSI_price_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', columns=cols, index=False)




