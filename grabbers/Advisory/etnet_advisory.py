# author: chenfei 
# usage: python etnet_finance_advisory.py 0700
# coding: utf-8
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

def get_advisory(code):
    url = "https://www.etnet.com.hk/www/eng/stocks/realtime/quote_profit.php?code=%s"%(code)
    ref = "https://www.etnet.com.hk/www/eng/stocks/realtime/quote_profit.php?code=%s"%(code)
    response = requests.get(url, headers = {"Referer": ref, "User-Agent": "Mozilla/5.0 \
        (Macintosh; Intel Mac OS X 10_11_6)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"})
    parser = html.fromstring(response.text)

    summary_table = parser.xpath('//div[@class="DivFigureContent"]//div[4]//table[@class="figureTable"]//tr[contains(@class,"Row")]')

    summary_data = OrderedDict()
 
    headers =['Profit Estimation', 'Profit/(Loss)(RMB(MIL))', 'EPS*/(LPS)(RMB(cts))','DPS (RMB(cts))','Broker','Ranking','Target Price*(HKD)','Update Date']
    summary_data.update({"0":headers})

    j = 1
    for table_data in summary_table:
    
        list_data=[]
        for i in range(1,8,1):    
            value = table_data.xpath('./td[%d]/text()'%i)
            if len(value)>0:
                if str(value[0]).strip()=='/--' or str(value[0]).strip()=='--':
                    list_data.append('N/A')
                else:
                    list_data.append(str(value[0]).strip())
            else:
                list_data.append('N/A')
                
        list_data.append(str(table_data.xpath('.//td[9]//text()')[0]).strip())
        
        summary_data.update({str(j):list_data})
        j = j+1

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

    # first_summary_data = get_price(index[0])
    # #cols = first_summary_data.keys()
    # #updated_time = first_summary_data['Date']
    # HSI_price_data = pd.DataFrame.from_dict(first_summary_data, orient='index').T 
    updated_time = str(datetime.now())[0:10]
    directory = updated_time
    if not os.path.exists('etnet/' + directory):
        os.makedirs('etnet/' + directory)
    
    for code in index:
        summary_data = get_advisory(code)
        #print summary_data
        file_name =  'etnet/' + directory + '/' + code + '_Etnet_Advisory_' + updated_time

        if len(summary_data)!=1:
            price_data = pd.DataFrame.from_dict(summary_data, orient='index')
            price_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', header=False, index=False)
        # else:
        #     print "No advisory data provided."
        
    

