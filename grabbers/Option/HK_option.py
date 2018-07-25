#http://www.hkex.com.hk/Market-Data/Futures-and-Options-Prices/Single-Stock/Stock-Options?sc_lang=en#&sttype=options
from __future__ import division
from datetime import datetime 
from time import sleep
from collections import OrderedDict
import os
from lxml import html  
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import timedelta
import numpy as np
import pandas as pd
import math
from scipy.stats import norm
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
    sleep(5)
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

#get option trading info (1 month)
def get_option(code, underlying, o_data, u_time, expiry, data):

    summary_data = OrderedDict()

    #u_time = str(datetime.now())[0:10]
    
    #JUL18    44.00 C     m 0.00      0.00      0.00     23.40      -1.25   53          0           0            0
    if len(underlying)<5:
    	underlying = (5-len(underlying))*'0' + underlying

	price = get_price(underlying, u_time)

    for i in range(len(o_data)):
        w = o_data[i].split()

        if len(w) == 12 and w[2] == 'C' and w[0] == expiry:       	

            summary_data.update({'Date':u_time})
            summary_data.update({'Stock Code':underlying})
            summary_data.update({'Option Code':code})
            summary_data.update({'Closing':price})

            summary_data.update({'Expiry':w[0]})
            summary_data.update({'Strike':w[1]})
            summary_data.update({'Type':w[2]})
            summary_data.update({'Open':w[3]})

            summary_data.update({'High':w[4]})
            summary_data.update({'Low':w[5]})
            summary_data.update({'Settlement Price':w[6]})
            summary_data.update({'Change':w[7]})

            summary_data.update({'IV(%)':w[8]})
            summary_data.update({'Volume':w[9]})
            summary_data.update({'Open Interest':w[10]})
            summary_data.update({'Change OI':w[11]})


            price_data = pd.DataFrame.from_dict(summary_data, orient='index').T       
            data = pd.concat([data, price_data], sort=True)
            print data
            #summary_data.clear()

        elif len(w) == 12 and w[2] == 'P' and w[0] == expiry:

            summary_data.update({'Date':u_time})
            summary_data.update({'Stock Code':underlying})
            summary_data.update({'Option Code':code})
            summary_data.update({'Closing':price})

            summary_data.update({'Expiry':w[0]})
            summary_data.update({'Strike':w[1]})
            summary_data.update({'Type':w[2]})
            summary_data.update({'Open':w[3]})

            summary_data.update({'High':w[4]})
            summary_data.update({'Low':w[5]})
            summary_data.update({'Settlement Price':w[6]})
            summary_data.update({'Change':w[7]})

            summary_data.update({'IV(%)':w[8]})
            summary_data.update({'Volume':w[9]})
            summary_data.update({'Open Interest':w[10]})
            summary_data.update({'Change OI':w[11]})


            price_data = pd.DataFrame.from_dict(summary_data, orient='index').T       
            data = pd.concat([data, price_data], sort=True)
            print data
            #summary_data.clear()

    return data                         


def get_price(code, lastdate):

    stock_code = 'HKEX/' + code

    price_BB = quandl.get(stock_code, start_date = lastdate , end_date = lastdate)

    quote = price_BB[-1:]['Nominal Price']
    s='-'

    if len(quote)>0:

        return float(quote)
    else:
        return s


if __name__=="__main__":


    code, underlying = get_code()

    #to get historical raw option data, hard code
    #time_list_5 = ['2018-04-30','2018-05-21','2018-05-21','2018-05-21','2018-05-21','2018-05-21','2018-05-21','2018-05-21','2018-05-21','2018-05-21','2018-05-21','2018-05-21','2018-05-21','2018-05-21','2018-05-21', '2018-05-23', '2018-05-24', '2018-05-25', '2018-05-28', '2018-05-29', '2018-05-30']
    #expiry_5 = ['2018-05-31']
    #u_time_list = ['2018-06-01']

    
    #u_time = str(datetime.now())[0:10]
    expiry_list = [0,0,'MAR19',0,'MAY18','JUN18','JUL18','AUG18','SEP18','OCT18',0,0]
    #for u_time in u_time_list:
    special_list = ['2018-05-31', '2018-06-29', '2018-07-31']

    #current_date = datetime.strptime(u_time,'%Y-%m-%d')

    #last_date = str(current_date - timedelta(days = 1))
    #u_time = last_date[0:10]    

    #time_list_7 = ['2018-06-29','2018-07-03','2018-07-04','2018-07-05','2018-07-06','2018-07-09','2018-07-10','2018-07-11','2018-07-12','2018-07-13']
    
    time_list_7 = ['2018-07-12']
    for u_time in time_list_7:
        
        url = "http://www.hkex.com.hk/eng/stat/dmstat/dayrpt/dqe{0}.htm".format(u_time.replace("-", "")[2:])

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        response = webdriver.Chrome(chrome_options=chrome_options)

        response.get(url)
        sleep(2)

        data = pd.DataFrame()
        cols=['Date','Stock Code','Option Code','Closing','Expiry','Strike','Type','Open','High','Low','Settlement Price','Change', 'IV(%)','Volume','Open Interest','Change OI']

        if not os.path.exists('data/'+ u_time):
            os.makedirs('data/'+ u_time)

        for i in range(len(code)):
            m = int(u_time[5:7].lstrip('0'))
            if m in special_list:
                expiry = expiry_list[m]
            else:
                expiry = expiry_list[m-1]

            try:
                o_data = response.find_element_by_name(code[i])
            except:
                continue

            o_data = o_data.text.encode('utf-8').split('\n')
            summary_data = get_option(code[i], underlying[i], o_data, u_time, expiry, data) 
            if not summary_data.empty:
                file_name = 'data/' + u_time + '/HK_option_1m_'+ code[i] + '_' + u_time
                summary_data.to_csv(file_name + '.csv', sep=',', columns=cols, index=False)    














