#http://www.hkex.com.hk/Market-Data/Futures-and-Options-Prices/Single-Stock/Stock-Options?sc_lang=en#&sttype=options
from pandas.io.json import json_normalize
import pandas as pd
from datetime import datetime
from lxml import html  
import requests
from time import sleep
from collections import OrderedDict
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import timedelta
import numpy as np
import pandas as pd
import quandl
quandl.ApiConfig.api_key = 'FxbKCf83-WeNae8uyxQg'


#get hk option code and their underlying 
def get_code():
    url = "http://www.hkex.com.hk/Market-Data/Futures-and-Options-Prices/Single-Stock/Stock-Options?sc_lang=en#&sttype=options"

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    response = webdriver.Chrome(chrome_options=chrome_options)
    response.get(url)
    sleep(3)
    response.find_element_by_xpath('//*[@id="lhkexw-singlestocklanding"]/section/div[2]/div/div[3]/div[2]/div[1]/span').click()

    l = response.find_elements_by_xpath('//*[@id="lhkexw-singlestocklanding"]/section/div[2]/div/div[3]/div[2]/div[2]/div')
    response.find_elements_by_xpath('//*[@id="lhkexw-singlestocklanding"]/section/div[2]/div/div[3]/div[2]/div[2]/div[{0}]/span'.format(len(l)))[0].click()

    code_list = response.find_elements_by_xpath('//*[@id="mCSB_1_container"]/div/div/table/tbody/tr')

    code=[]
    underlying=[]
    vol=[]
    for i in range(len(code_list)):
        c = code_list[i].find_elements_by_xpath('.//td[1]')[0].text.encode('utf-8')
        u = code_list[i].find_elements_by_xpath('.//td[2]')[0].text.encode('utf-8')
        v = code_list[i].find_elements_by_xpath('.//td[5]')[0].text.encode('utf-8')

        if (i > 0) and (u == underlying[-1]):
            #print float(vol[i-1].replace(",", "")),code[i-1],underlying[i-1]
            if float(v.replace(",", "")) > float(vol[-1].replace(",", "")):
                del code[-1]
                del underlying[-1]
                del vol[-1]
                code.append(c)
                underlying.append(u)
                vol.append(v)
        else:
            code.append(c)
            underlying.append(u)
            vol.append(v)

    return code, underlying  

#get option trading info (at the money, 1 month)
def get_option(code, underlying):

    # url = "http://www.hkex.com.hk/market-data/futures-and-options-prices/single-stock/details?sc_lang=en&product={0}".format(code)

    # chrome_options = Options()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # response = webdriver.Chrome(chrome_options=chrome_options)

    # response.get(url)
    # sleep(3)
    # parser = html.fromstring(response.page_source)

    summary_data = OrderedDict()

    u_time = '2018-06-28'
    expiry = '18-Jun'
    summary_data.update({'Date':u_time})
    summary_data.update({'Stock Code':underlying})
    summary_data.update({'Option Code':code})
    summary_data.update({'Expiry':expiry})
    

    if len(underlying)<5:
            underlying = (5-len(underlying))*'0' + underlying

    mu,upper,down,u_d,net_change,change_per,u_d_2,price = get_BBands(underlying, u_time, 20)
    summary_data.update({'Closing':price})
    summary_data.update({'Net Change':net_change})
    summary_data.update({'Change(%)':change_per})
    
    summary_data.update({'BBands M':round(mu,2)})
    summary_data.update({'BBands U':round(upper,2)})
    summary_data.update({'BBands D':round(down,2)})
    summary_data.update({'U/D(mu)':u_d})
    summary_data.update({'U/D(B)':u_d_2})
     
    return summary_data                           

# get net position up/down, BBands(u,d,m) and up/down
def get_BBands(code, lastdate, period = 20):

    stock_code = 'HKEX/' + code
    price_data = quandl.get(stock_code, start_date = lastdate, end_date = lastdate)
    
    mu = 0
    sigma = 0
    u_d = ''
    u_d_2 = ''
    net_change = 0
    change_per = 0

    last_date = datetime.strptime(lastdate,'%Y-%m-%d')
    
    right = str(last_date)
    left = str(last_date - timedelta(days = period*2))

    price_BB = quandl.get(stock_code, start_date = left , end_date = right)

    data = np.array(list(price_BB[-period:]['Nominal Price']))
    mu = np.mean(data)
    quote = price_BB[-1:]['Nominal Price']
    if float(quote) >= mu:
        u_d = 'up'
    else:
        u_d = 'down'
    

    quote_yes = price_BB[-2:-1]['Nominal Price']
    net_change = round(float(quote)-float(quote_yes),2)
    change_per = round(100*(float(quote)-float(quote_yes))/float(quote_yes),2)
    sigma = np.std(data)

    upper = mu + 2*sigma
    down = mu - 2*sigma  

    if float(quote) >= upper:
        u_d_2 = 'up'
    elif float(quote) <= down:
        u_d_2 = 'down'
    else:
        u_d_2 = '-'

    return mu,upper,down,u_d,net_change,change_per,u_d_2,float(quote)



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
    
    for mem in index:
        ticker = mem.xpath('.//a[contains(@class,"ticker")]//text()')
        temp = str(ticker[0])[:-3]
        s_index.append(temp)
  
    return s_index


if __name__=="__main__":


    code, underlying = get_code()
    index = get_index()

    ol = []
    sl = []
    for c, u in zip(code, underlying):
        if u in index:
            ol.append(c)    
            sl.append(u)

    u_time = '2018-06-28'

    data = pd.DataFrame()
    cols=[]

    for i in range(len(ol)):
        #price = get_price(sl[i])
        summary_data = get_option(ol[i], sl[i])
        if summary_data:
            print summary_data
            cols = summary_data.keys()
            price_data = pd.DataFrame.from_dict(summary_data, orient='index').T       
            data = pd.concat([data, price_data], sort=True)
              
    if not os.path.exists('tech_data/'):
        os.makedirs('tech_data/')

    file_name = 'tech_data' + '/HK_Technical_' + u_time
    data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', columns=cols, index=False)
    data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', columns=cols, index=False)


