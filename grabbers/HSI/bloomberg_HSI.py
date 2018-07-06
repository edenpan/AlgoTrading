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
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_price(code):
    url = "https://www.bloomberg.com/quote/{0}:HK"
    url = url.format(code)
    #print url
    #user = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
    #url = "https://www.bloomberg.com/quote/HSI:IND/members"
    accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    acceptEncoding = 'gzip, deflate, br'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    #cookie = 'non_public_ab=shi_chang; bbAbVisits=; bdfpc=004.9334377194.1527909092345; _ga=GA1.2.890971448.1527909093; __ssds=2; agent_id=2bab95b4-9ace-4251-88eb-7b39c1630bcc; session_id=0936afe4-4267-43ef-b212-eceb4921fd82; session_key=8f442f49be56ce352af9a884e917562fe463b8d8; _pxvid=a3b7b410-6612-11e8-a4be-dd089fc261a9; __ssuzjsr2=a9be0cd8e; __uzmaj2=5fd66d03-6b6d-44ea-9434-acb7e2ccaa986863; __uzmbj2=1527909087; trc_cookie_storage=taboola%2520global%253Auser-id%3Df2d509e5-3460-4913-86fb-c256cd1fbb59-tuct20b9031; __gads=ID=eff743b88f144083:T=1527909089:S=ALNI_Mb_2aqCdomDEgDMCDXzHojlCnM3AA; __tbc=%7Bjzx%7Dt_3qvTkEkvt3AGEeiiNNgAb2dtoeOsJW62OddwPPSXN5ka3DYpaS56p9O-GwqQWYNC4S60HJCdBtNRHEr2y5-IiW2Aar-S8P1JoADyfhP1BUK52iG_ODk-5HCi94fA_zjylU0Z664w9lha1BgkmqDg; optimizelyEndUserId=oeu1528784177256r0.46434719714597095; optimizelySegments=%7B%224375847448%22%3A%22false%22%2C%224391854435%22%3A%22direct%22%2C%224373366517%22%3A%22none%22%2C%224384716416%22%3A%22gc%22%7D; optimizelyBuckets=%7B%7D; __pat=-14400000; __ncuid=6cf71a27-090e-41c0-8651-1c081d52e423; bb_geo_info={"country":"HK","region":"Asia"}|1530708226529; _user_newsletters=[]; _gid=GA1.2.746693131.1530614195; _user-status=anonymous; notice_behavior=none; BUSINESS_AP=J27; _parsely_visitor={%22id%22:%22b7ab9454-3860-4063-b066-cfa7257575ed%22%2C%22session_count%22:4%2C%22last_session_ts%22:1530614216350}; bbAbVisits=; RT="sl=1&ss=1530618098925&tt=5257&obo=0&bcn=%2F%2F36fb61b5.akstat.io%2F&sh=1530618104193%3D1%3A0%3A5257&dm=www.bloomberg.com&si=5b48649d-be2d-4119-9188-7f7c42781253&ld=1530618104194&r=https%3A%2F%2Fwww.bloomberg.com%2Fquote%2F700%3AHK&ul=1530618116238&hd=1530618116526"; __pvi=%7B%22id%22%3A%22v-2018-07-03-22-15-53-930-4kB6lx90LAMGQDXM-264a99050712acd1c09c1cf06b4ee53a%22%2C%22domain%22%3A%22.bloomberg.com%22%2C%22time%22%3A1530627353930%7D; xbc=%7Bjzx%7DfjMbYP8Kb5QJED4WTTXJ3Kg6LqNjt_JBhybaNY_c4aC6Ed9kGcJy91-J1YblD9R1gJ9LS9Sy1HXQLd7TxyfSEm0izLTWxHhPelBE39HmJ7azQn2lWR9hRNAElPQIW8DvMFr4HQFDvOOjz0uAFwbCumUyrv6fLOvQJxGIrum730-yA4ADOHaWjWW0UqdICNDJLxqx-SbRMYCZ7hHghBkwfl0af_Ml6mwk0ELzOLHV_89zoDR4l-QKyIGtfdI2lbcIJQzKVaNsD37xrO846O_Zc_qPpn7FZYjaMqwXmMBHyOCK5h4cJOc-35lHDLZZlK-ojxliva24opGVSsQ_d3MBQO9LcJ0E-j0_uXFMnd_npNHMo6TP1pLbxLMD98UudBhya3iilkZ3D2GG1Pczjo3pfMdPsB5RVBOHQOS5qVz727E; MARKETS_AP=J16; SRV=JPX02; __uzma=c133fa65-1d20-306e-5c17-c20ea529db25; __uzmb=1530708142; __uzmc=808101033018; __uzmd=1530708142; _dc_gtm_UA-11413116-1=1; _uetsid=_uet8d57adac; _user-ip=123.203.89.172; __uzmcj2=8245626865227; __uzmdj2=1530708144; _px3=902220f468a4a0832a4067309cf098d49f4775c6cf0ef9e26a609e62122e5caf:L/d3MoBpDS7aDMbH4UxLSTtVdfv5MIOArdLPQvVLhMH1/j6prAJLCH+CRWegLtDsSU9IvhWM04AZU6LFFPxFOA==:1000:F2h1x0Axjw6dcARzyxIstBHjpa1CoAqv0dIWiEYE+Lg4Rs7C5axT/xiR2cWGouvJ4yO4XV9SL09EHxJE5SwtVMh+RZFyPch/RrFUfDemOmUkvX8AehC9rDd1//0g+6U1UOq8+D76RwEkMTNbvefeqJqQx5C4HulgoQm77JIMOVk=; _tb_sess_r=; _tb_t_ppg=https%3A//www.bloomberg.com/quote/700%3AHK'
    response = requests.get(url, headers={"User-Agent":user_agent, "Accept":accept, "accept-encoding":acceptEncoding})
    sleep(5)
    #response = requests.get(url)
    parser = html.fromstring(response.text)

    # chrome_options = Options()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # response = webdriver.Chrome()
    # response.get(url)
    # sleep(3)
    # parser = html.fromstring(response.page_source)

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

def get_index():

    url = "https://www.bloomberg.com/quote/HSI:IND/members"
    accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    acceptEncoding = 'gzip, deflate, br'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    response = requests.get(url,headers={"User-Agent":user_agent, "Accept":accept, "accept-encoding":acceptEncoding})
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
    #print index
    #sleep(6)
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



