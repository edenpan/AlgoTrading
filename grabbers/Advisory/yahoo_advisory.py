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

    soup = BeautifulSoup(response.content, "lxml")
    script = soup.find("script",text=re.compile("root.App.main")).text
    data = loads(re.search("root.App.main\\s+=\\s+(\\{.*\\})", script).group(1))

    # data.keys()
    # data['context'].keys()
    advisory_data = data['context']['dispatcher']['stores']['QuoteSummaryStore']['financialData']

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

    summary_data = OrderedDict()

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
        print summary_data
        price_data = pd.DataFrame.from_dict(summary_data, orient='index').T       
        HSI_price_data = pd.concat([HSI_price_data, price_data], sort=True)
        
    directory = updated_time
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_name = directory + '/HSI_Advisory_yahoo_' + updated_time

    HSI_price_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A',columns=cols, index=False)

