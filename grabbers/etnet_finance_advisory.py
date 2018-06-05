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

def get_price(code):
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


if __name__=="__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('code',help = '')
    args = argparser.parse_args()
    
    code = args.code  
    summary_data = get_price(code)
    file_name = code + '_etnet_advisory_' + str(datetime.now())[0:10]

    if len(summary_data)!=1:
        price_data = pd.DataFrame.from_dict(summary_data, orient='index')
        price_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', header=False, index=False)
    else:
        print "No advisory data provided."

