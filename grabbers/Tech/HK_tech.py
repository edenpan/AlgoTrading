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

#get option trading info (at the money, 1 month)
def get_option(code, underlying, data, u_time, x):

    summary_data = OrderedDict()

    #u_time = str(datetime.now())[0:10]
    summary_data.update({'Date':u_time})
    summary_data.update({'Stock Code':underlying})
    summary_data.update({'Option Code':code})
    
    if len(underlying)<5:
            underlying = (5-len(underlying))*'0' + underlying

    mu,upper,down,u_d,net_change,change_per,u_d_2,price = get_BBands(underlying, u_time, 20)

    summary_data.update({'Closing':price})
    summary_data.update({'Net Change':net_change})
    summary_data.update({'Change(%)':change_per})
    
    summary_data.update({'BBands M':round(mu,2)})
    summary_data.update({'BBands U':round(upper,2)})
    summary_data.update({'BBands D':round(down,2)})
    summary_data.update({'U/D(M)':u_d})
    summary_data.update({'U/D(B)':u_d_2})

    diff_c = 9999
    diff_p = 9999
    #select at the money
    index_c = 0
    index_p = 0

    for i in range(len(data)):
        w = data[i].split()
        if len(w) == 12 and w[2] == 'C' and w[0] == 'JUL18':
            c = w[1]
            if abs(float(c) - price) < diff_c:
                diff_c = abs(float(c) - price)
                index_c = i
        elif len(w) == 12 and w[2] == 'P' and w[0] == 'JUL18':
            p = w[1]
            if abs(float(p) - price) < diff_p:
                diff_p = abs(float(p) - price)
                index_p = i

    c_u_d = '-'
    p_u_d = '-'

    IV_1C = data[index_c].split()[8]
    IV_1P = data[index_p].split()[8]
    Strike = data[index_c].split()[1]

    index = x[(x['Option Code'] == code)].index.tolist()[0]
    last_civ = x[index:index+1]['IV(1C)'].tolist()[0]
    last_piv = x[index:index+1]['IV(1P)'].tolist()[0]

    if float(IV_1C) < float(last_civ):
        c_u_d = 'down'
    elif float(IV_1C) > float(last_civ):
        c_u_d = 'up'


    if float(IV_1P) < float(last_piv):
        p_u_d = 'down'
    elif float(IV_1P) > float(last_piv):
        p_u_d = 'up'


    S_C = data[index_c].split()[6]
    S_C_C = data[index_c].split()[7]

    S_P = data[index_p].split()[6]
    S_P_C = data[index_p].split()[7]

    summary_data.update({'IV(1C)':IV_1C})
    summary_data.update({'U/D(1C)':c_u_d})
    summary_data.update({'IV(1P)':IV_1P})
    summary_data.update({'U/D(1P)':p_u_d})


    r = 0.0015
    q = 0.0424
    Expiry = 30
    T = (Expiry - int(u_time[8:10].lstrip('0')))/365

    percent = 0.01
    price_delta = float(price)*percent

    if T > 0 and IV_1C != '0':
        c_delta = get_delta(price, float(Strike), r, q, float(IV_1C)/100, T, 0)
        C_prediction_u = round((float(S_C) + c_delta*price_delta),2)
        C_prediction_d = float(S_C)
    else:
        C_prediction_u = '-'
        C_prediction_d = '-'

    if T > 0 and IV_1P != '0':
        p_delta = get_delta(price, float(Strike), r, q, float(IV_1P)/100, T, 1)
        P_prediction_d = float(S_P)
        P_prediction_u = round((float(S_P) - p_delta*price_delta),2)
    else:
        P_prediction_u = '-'
        P_prediction_d = '-'

        
    summary_data.update({'Strike':Strike})
    summary_data.update({'Settle(1C)':S_C})
    summary_data.update({'Change(1C)':S_C_C})
    summary_data.update({'Prediction(1C)':C_prediction_u})
    summary_data.update({'Settle(1P)':S_P})
    summary_data.update({'Change(1P)':S_P_C})
    summary_data.update({'Prediction(1P)':P_prediction_u})

     
    return summary_data                           


def get_delta(S, K, r, q, sigma, T, t_o):

    d1 = (math.log(S/K) + (r - q + 0.5*(sigma**2))*T)/(sigma*math.sqrt(T))
    if t_o == 0:

        delta = math.exp(-1*q*T)*norm.cdf(d1)

    else:
        delta = math.exp(-1*q*T)*(norm.cdf(d1)-1)

    return delta


def get_BBands(code, lastdate, period = 20):

    stock_code = 'HKEX/' + code

    mu = 0
    sigma = 0
    u_d = '-'
    u_d_2 = '-'
    net_change = 0
    change_per = 0

    last_date = datetime.strptime(lastdate,'%Y-%m-%d')
    
    right = str(last_date)
    left = str(last_date - timedelta(days = period * 3))

    try:
        price_BB = quandl.get(stock_code, start_date = left , end_date = right)
    except:
        sleep(10)
        price_BB = quandl.get(stock_code, start_date = left , end_date = right)

    data = np.array(list(price_BB[-period:]['Nominal Price']))
    mu = np.mean(data)
    quote = price_BB[-1:]['Nominal Price']
    if float(quote) > mu:
        u_d = 'up'
    elif float(quote) < mu:
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


    return mu,upper,down,u_d,net_change,change_per,u_d_2,float(quote)


# get net position up/down, BBands(u,d,m) and up/down
# def get_BBands(code, lastdate, period = 20):

#     code = code + '.HK'
#     url = "https://finance.yahoo.com/quote/%s/history?p=%s"%(code,code)
#     response = requests.get(url)

#     parser = html.fromstring(response.text)


#     quote = parser.xpath('//table[contains(@data-test,"historical-prices")]/tbody[1]/tr')
    
#     mu = 0
#     sigma = 0
#     u_d = ''
#     u_d_2 = ''
#     net_change = 0
#     change_per = 0

#     count=0
#     c_price=''
#     y_price=''
#     BBdata = []

#     for d in quote:
#         terms = d.xpath('.//td//text()')
#         if len(terms) > 5:
#             if count == 0:
#                 c_price = str(terms[5]).strip()
#             elif count == 1:
#                 y_price = str(terms[5]).strip()
            
#             count = count + 1
#             BBdata.append(float(str(terms[5]).strip()))
            
#             if count == period:
#                 break
#         else:
#             continue

#     data = np.array(BBdata)
#     mu = np.mean(data)
#     if float(c_price) >= mu:
#         u_d = 'up'
#     else:
#         u_d = 'down'
    

#     net_change = round(float(c_price)-float(y_price),2)
#     change_per = round(100*(float(c_price)-float(y_price))/float(y_price),2)
#     sigma = np.std(data)

#     upper = mu + 2*sigma
#     down = mu - 2*sigma  

#     if float(c_price) >= upper:
#         u_d_2 = 'up'
#     elif float(c_price) <= down:
#         u_d_2 = 'down'
#     else:
#         u_d_2 = '-'


#     return mu,upper,down,u_d,net_change,change_per,u_d_2,c_price


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

    u_time = '2018-07-06'
    current_date = datetime.strptime(u_time,'%Y-%m-%d')

    count = 1
    last_date = str(current_date - timedelta(days = count))
    while((not os.path.exists('tech_data/HK_tech_'+ last_date[0:10] + '.csv')) and last_date[0:10]>='2018-06-01'):
        count = count + 1
        #print count
        last_date = str(current_date - timedelta(days = count))

    x = pd.read_csv('tech_data/HK_tech_'+ last_date[0:10] + '.csv')

    url = "http://www.hkex.com.hk/eng/stat/dmstat/dayrpt/dqe{0}.htm".format(u_time.replace("-", "")[2:])

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    response = webdriver.Chrome(chrome_options=chrome_options)

    response.get(url)
    sleep(5)

    data = pd.DataFrame()
    cols=[]

    for i in range(len(ol)):
        #price = get_price(sl[i])
        #try:
        o_data = response.find_element_by_name(ol[i])
        # except:
        #     sleep(10)
        #     o_data = response.find_element_by_name(ol[i])

        o_data = o_data.text.encode('utf-8').split('\n')
        summary_data = get_option(ol[i], sl[i], o_data, u_time, x)
        if summary_data:
            print summary_data
            cols = summary_data.keys()
            price_data = pd.DataFrame.from_dict(summary_data, orient='index').T       
            data = pd.concat([data, price_data], sort=True)
              
    if not os.path.exists('tech_data/'):
        os.makedirs('tech_data/')

    file_name = 'tech_data' + '/HK_tech_' + u_time
    data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', columns=cols, index=False)


