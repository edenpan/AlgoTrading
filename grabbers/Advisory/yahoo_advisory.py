from lxml import html  
import requests
from time import sleep
import argparse
from collections import OrderedDict
import pandas as pd
from datetime import datetime
import re
from bs4 import BeautifulSoup
from json import loads
import os

def get_price(code):
 
    url = "http://finance.yahoo.com/quote/%s?p=%s"%(code,code)
    response = requests.get(url)
    sleep(4)
    soup = BeautifulSoup(response.content, "lxml")
    script = soup.find("script",text=re.compile("root.App.main")).text
    data = loads(re.search("root.App.main\\s+=\\s+(\\{.*\\})", script).group(1))
    summary_data = OrderedDict()
    # data.keys()
    # data['context'].keys()
    advisory_data = data['context']['dispatcher']['stores']['QuoteSummaryStore']['financialData']
    if advisory_data:
        if advisory_data['currentPrice']:
            cur_price = advisory_data['currentPrice']['fmt'].encode('utf-8')
        else:
            cur_price = "-"

        if advisory_data['targetMeanPrice']:
            avr_target = advisory_data['targetMeanPrice']['fmt'].encode('utf-8')
        else:
            avr_target = "-"
            
        if advisory_data['targetHighPrice']:
            high_target = advisory_data['targetHighPrice']['fmt'].encode('utf-8')
        else:
            high_target = "-"
            
        if advisory_data['targetLowPrice']:
            low_target = advisory_data['targetLowPrice']['fmt'].encode('utf-8')
        else:
            low_target = "-"
            
        if advisory_data['recommendationMean']:
            rating = advisory_data['recommendationMean']['fmt'].encode('utf-8')
        else:
            rating = "-"    
            
        if advisory_data['recommendationKey']:
            advise = advisory_data['recommendationKey'].encode('utf-8')
        else:
            advise = "-"

        # ROE = advisory_data['returnOnEquity']['fmt'].encode('utf-8')
        # GrossMargin = advisory_data['grossMargins']['fmt'].encode('utf-8')
        # NPM = advisory_data['profitMargins']['fmt'].encode('utf-8')

        

        u_time = str(datetime.now())[0:10]
        summary_data.update({'Date':u_time})
        summary_data.update({'Symbol':code[0:4]})

        summary_data.update({'Advisory':advise})
        summary_data.update({'Rating(1-5)':rating})

        summary_data.update({'Current price':cur_price})

        summary_data.update({'Average Target price':avr_target})
        summary_data.update({'Low Target Price':low_target})
        summary_data.update({'High Target Price':high_target})

        # summary_data.update({'ROE':ROE})
        # summary_data.update({'GrossMargin':GrossMargin})
        # summary_data.update({'NPM':NPM})
    else:
        summary_data.clear()

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
    f_data = get_price(index[0] + '.HK')
    cols = f_data.keys() 
    
    for code in index:
        code = code + '.HK'
        summary_data = get_price(code)
        if summary_data:
            print summary_data
            price_data = pd.DataFrame.from_dict(summary_data, orient='index').T       
            HSI_price_data = pd.concat([HSI_price_data, price_data], sort=True)
    
    u_time = str(datetime.now())[0:10]    
    if not os.path.exists('yahoo/'):
        os.makedirs('yahoo/')

    file_name = 'yahoo/HSI_Advisory_Yahoo_' + u_time

    HSI_price_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', columns=cols, index=False)

