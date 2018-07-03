from lxml import html  
import requests
from time import sleep
import json
import argparse
from collections import OrderedDict
from time import sleep
import pandas as pd
from datetime import datetime
import os
import sys
sys.path.insert(0,  '../util')
import common

def get_price(code):
    url = "https://www.bloomberg.com/quote/{0}:HK"
    url = url.format(code)
    #user = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"

    response = requests.get(url)
    parser = html.fromstring(response.text)

    summary_data = OrderedDict()

    u_time = str(datetime.now())[0:10]
    summary_data.update({'Date':u_time})
    summary_data.update({'Symbol':code})

    quote = parser.xpath('//section[contains(@class,"snapshotSummary")]//section[contains(@class,"price")]//span[contains(@class,"priceText")]//text()')

    if len(quote) > 0:
        summary_data.update({'Nominal price' : str(quote[0]).strip()})
    else:
        summary_data.update({'Nominal price' : 'N/A'})

    summary1 = parser.xpath('//section[contains(@class,"snapshotOverview")]//section[contains(@class,"snapshotDetails")]//section')      

    for table_data in summary1:
        raw_table_key = table_data.xpath('.//header//text()')
        raw_table_value = table_data.xpath('.//div//text()')

        table_key = str(raw_table_key[0]).strip()
            
        table_value = ''
        for i in range(0,len(raw_table_value)):
            table_value = table_value + str(raw_table_value[i]).strip()

        summary_data.update({table_key:table_value})


    summary2 = parser.xpath('//div[contains(@class,"keyStatistics")]//div[contains(@class,"rowListItemWrap")]')
                      
    for table_data in summary2:
        raw_table_key = table_data.xpath('.//text()')[0]
        raw_table_value = table_data.xpath('.//text()')[1]

        table_key = str(raw_table_key).strip()
            
        if str(raw_table_value).strip()=='--':
            table_value = 'N/A'
        else:
            table_value = str(raw_table_value).strip()
            
        summary_data.update({table_key:table_value})

    return summary_data


if __name__=="__main__":
    
    index = common.get_index()
    HSI_price_data = pd.DataFrame()
    f_data = get_price(index[0].lstrip('0'))
    cols = f_data.keys()

    for code in index:

        summary_data = get_price(code.lstrip('0'))
        print summary_data
        price_data = pd.DataFrame.from_dict(summary_data, orient='index').T       
        HSI_price_data = pd.concat([HSI_price_data, price_data], sort=True)

    u_time = str(datetime.now())[0:10]
    if not os.path.exists('data/bloomberg/'):
        os.makedirs('data/bloomberg/')

    file_name = 'data/bloomberg' + '/HSI_bloomberg_' + u_time
    HSI_price_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', columns=cols, index=False)



