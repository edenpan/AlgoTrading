# coding: utf-8
# chenfei 
# usage: python etnet_finance_market.py 0700
from lxml import html  
import requests
import argparse
from time import sleep
from collections import OrderedDict
import pandas as pd
from datetime import datetime

def get_price(code):
    
    url = "https://www.etnet.com.hk/www/eng/stocks/realtime/quote.php?code=%s"%(code)
    ref = "https://www.etnet.com.hk/www/eng/stocks/realtime/quote.php?code=%s"%(code)
    response = requests.get(url, headers = {"Referer":ref,"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"})
    sleep(4)

    parser = html.fromstring(response.text)

    summary_data = OrderedDict()

    updated_time = parser.xpath('//div[@id="DivContentRight"]/div[@class="DivBoxStyleE shadow"][1]/div[2]/div[@class="remark"]/text()')

    t = updated_time[0].strip()[-16:-6]
  
    up_date = datetime.strptime(t, '%d/%m/%Y')

    updated_time = str(up_date)[0:10]

    summary_data.update({'Date':updated_time})
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

    
    summary_data.pop('Currency')
    summary_data.pop('Eligible for CAS')
    summary_data.pop('Eligible for VCM')        
    summary_data.pop('BoardLot') 
    summary_data.pop('Listing Date') 
    summary_data.pop('Listing Price') 
 
    return summary_data


if __name__=="__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('code',help = '')
    args = argparser.parse_args()
    
    code = args.code  
    summary_data = get_price(code)

    updated_time = summary_data['Date']

    price_data = pd.DataFrame.from_dict(summary_data, orient='index').T 
        
    file_name = code + '_etnet_' + updated_time
    price_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A',index=False)







