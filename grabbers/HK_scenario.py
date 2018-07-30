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
    sleep(15)
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
def get_option(code, underlying, o_data, u_time, expiry, maturity):

    summary_data = OrderedDict()

    #u_time = str(datetime.now())[0:10]
    summary_data.update({'Date':u_time})
    summary_data.update({'Stock Code':underlying})
    summary_data.update({'Option Code':code})
    
    if len(underlying)<5:
            underlying = (5-len(underlying))*'0' + underlying

    u_d,net_change,change_per,price = get_BBands(underlying, u_time, 20)

    summary_data.update({'Closing':price})
    summary_data.update({'Net Change':net_change})
    summary_data.update({'Change(%)':change_per})
    summary_data.update({'U/D(B)':u_d})

    # summary_data.update({'BBands M':round(mu,2)})
    # summary_data.update({'BBands U':round(upper,2)})
    # summary_data.update({'BBands D':round(down,2)})
    # summary_data.update({'U/D(M)':u_d})
    
    diff_c = 9999
    diff_p = 9999
    #select at/near the money
    index_c = 0
    index_p = 0

    if price > 0:
        for i in range(len(o_data)):
            w = o_data[i].split()
            if len(w) == 12 and w[2] == 'C' and w[0] == expiry:
                c = w[1]
                if abs(float(c) - price) < diff_c:
                    diff_c = abs(float(c) - price)
                    index_c = i
            elif len(w) == 12 and w[2] == 'P' and w[0] == expiry:
                p = w[1]
                if abs(float(p) - price) < diff_p:
                    diff_p = abs(float(p) - price)
                    index_p = i

    # c_u_d = '-'
    # p_u_d = '-'
    if index_p != 0 and index_c != 0:
        
        s_vol = get_s_vol(underlying, u_time, 20)
        IV_1C = o_data[index_c].split()[8]
        IV_1P = o_data[index_p].split()[8]
        Strike = o_data[index_c].split()[1]

        summary_data.update({'Strike':Strike})

        S_C = o_data[index_c].split()[6]
        S_C_C = o_data[index_c].split()[7]
        O_C = o_data[index_c].split()[3]

        S_P = o_data[index_p].split()[6]
        S_P_C = o_data[index_p].split()[7]
        O_P = o_data[index_p].split()[3]

        summary_data.update({'SV':round(s_vol,2)})
        summary_data.update({'IV(%,1C)':IV_1C})
        #summary_data.update({'U/D(1C)':c_u_d})
        summary_data.update({'IV(%,1P)':IV_1P})
        #summary_data.update({'U/D(1P)':p_u_d})

        r = 0.0015
        q = 0.0424
        Expiry = maturity
        T = (Expiry - int(u_time[8:10].lstrip('0')))/365
        #T = 30

        theo_c = price_option(price, float(Strike), r, q, s_vol, T, 0)
        theo_p = price_option(price, float(Strike), r, q, s_vol, T, 1)

        theo_cm30 = price_option(price*0.7, float(Strike), r, q, float(IV_1C)/100, T, 0)
        theo_cm20 = price_option(price*0.8, float(Strike), r, q, float(IV_1C)/100, T, 0)
        theo_cm10 = price_option(price*0.9, float(Strike), r, q, float(IV_1C)/100, T, 0)
        theo_cm5 = price_option(price*0.95, float(Strike), r, q, float(IV_1C)/100, T, 0)
        theo_cm1 = price_option(price*0.99, float(Strike), r, q, float(IV_1C)/100, T, 0)
        theo_c0 = price_option(price, float(Strike), r, q, float(IV_1C)/100, T, 0)
        theo_c1 = price_option(price*1.01, float(Strike), r, q, float(IV_1C)/100, T, 0)
        theo_c5 = price_option(price*1.05, float(Strike), r, q, float(IV_1C)/100, T, 0)
        theo_c10 = price_option(price*1.1, float(Strike), r, q, float(IV_1C)/100, T, 0)
        theo_c20 = price_option(price*1.2, float(Strike), r, q, float(IV_1C)/100, T, 0)
        theo_c30 = price_option(price*1.3, float(Strike), r, q, float(IV_1C)/100, T, 0)

        theo_pm30 = price_option(price*0.7, float(Strike), r, q, float(IV_1P)/100, T, 1)
        theo_pm20 = price_option(price*0.8, float(Strike), r, q, float(IV_1P)/100, T, 1)
        theo_pm10 = price_option(price*0.9, float(Strike), r, q, float(IV_1P)/100, T, 1)
        theo_pm5 = price_option(price*0.95, float(Strike), r, q, float(IV_1P)/100, T, 1)
        theo_pm1 = price_option(price*0.99, float(Strike), r, q, float(IV_1P)/100, T, 1)
        theo_p0 = price_option(price, float(Strike), r, q, float(IV_1P)/100, T, 1)
        theo_p1 = price_option(price*1.01, float(Strike), r, q, float(IV_1P)/100, T, 1)
        theo_p5 = price_option(price*1.05, float(Strike), r, q, float(IV_1P)/100, T, 1)
        theo_p10 = price_option(price*1.1, float(Strike), r, q, float(IV_1P)/100, T, 1)
        theo_p20 = price_option(price*1.2, float(Strike), r, q, float(IV_1P)/100, T, 1)
        theo_p30 = price_option(price*1.3, float(Strike), r, q, float(IV_1P)/100, T, 1)


        summary_data.update({'Open(1C)':O_C})
        summary_data.update({'Settle(1C)':S_C})
        summary_data.update({'Change(1C)':S_C_C})
        summary_data.update({'T-P(S,1C)':round(theo_c,2)})

        summary_data.update({'T-P(-30%C)':round(theo_cm30,2)})
        summary_data.update({'T-P(-20%C)':round(theo_cm20,2)})
        summary_data.update({'T-P(-10%C)':round(theo_cm10,2)})
        summary_data.update({'T-P(-5%C)':round(theo_cm5,2)})
        summary_data.update({'T-P(-1%C)':round(theo_cm1,2)})
        summary_data.update({'T-P(C)':round(theo_c0,2)})
        summary_data.update({'T-P(1%C)':round(theo_c1,2)})
        summary_data.update({'T-P(5%C)':round(theo_c5,2)})
        summary_data.update({'T-P(10%C)':round(theo_c10,2)})
        summary_data.update({'T-P(20%C)':round(theo_c20,2)})
        summary_data.update({'T-P(30%C)':round(theo_c30,2)})

        summary_data.update({'Open(1P)':O_P})
        summary_data.update({'Settle(1P)':S_P})
        summary_data.update({'Change(1P)':S_P_C})
        summary_data.update({'T-P(S,1P)':round(theo_p,2)})

        summary_data.update({'T-P(-30%P)':round(theo_pm30,2)})
        summary_data.update({'T-P(-20%P)':round(theo_pm20,2)})
        summary_data.update({'T-P(-10%P)':round(theo_pm10,2)})
        summary_data.update({'T-P(-5%P)':round(theo_pm5,2)})
        summary_data.update({'T-P(-1%P)':round(theo_pm1,2)})
        summary_data.update({'T-P(P)':round(theo_p0,2)})
        summary_data.update({'T-P(1%P)':round(theo_p1,2)})
        summary_data.update({'T-P(5%P)':round(theo_p5,2)})
        summary_data.update({'T-P(10%P)':round(theo_p10,2)})
        summary_data.update({'T-P(20%P)':round(theo_p20,2)})
        summary_data.update({'T-P(30%P)':round(theo_p30,2)})
    
        #Add delta and vega
        delta_c = get_delta(price, float(Strike), r, q, float(IV_1C)/100, T, 0)
        delta_p = get_delta(price, float(Strike), r, q, float(IV_1P)/100, T, 1)

        vega_c = get_vega(price, float(Strike), r, q, float(IV_1C)/100, T)
        vega_p = get_vega(price, float(Strike), r, q, float(IV_1P)/100, T)

        summary_data.update({'Delta(C)':round(delta_c,2)})
        summary_data.update({'Delta(P)':round(delta_p,2)})
        summary_data.update({'Vega(C)':round(vega_c,2)})
        summary_data.update({'Vega(P)':round(vega_p,2)})


    else:
        summary_data.clear()
     
    return summary_data                           


def get_delta(S, K, r, q, sigma, T, t_o):

    #(price, float(Strike), r, q, float(IV_1C)/100, T, 0)
    if sigma > 0 and T > 0:
        d1 = (math.log(S/K) + (r - q + 0.5*(sigma**2))*T)/(sigma*math.sqrt(T))
        if t_o == 0:

            delta = math.exp(-1*q*T)*norm.cdf(d1)

        else:
            delta = math.exp(-1*q*T)*(norm.cdf(d1)-1)

    else:
        delta = 0

    return delta


def get_vega(S, K, r, q, sigma, T):

    #(price, float(Strike), r, q, float(IV_1C)/100, T, 0)
    
    if sigma > 0 and T > 0:
        d1 = (math.log(S/K) + (r - q + 0.5*(sigma**2))*T)/(sigma*math.sqrt(T))

        vega = (1/100)*S*math.exp(-1*q*T)*math.sqrt(T)*(1/math.sqrt(2*math.pi))*math.exp(-1*d1*d1/2)

    else:
        vega = 0

    return vega


def price_option(S, K, r, q, sigma, T, t_o):
    
    if sigma > 0 and T > 0:
        d1 = (math.log(S/K) + (r - q + 0.5*(sigma**2))*T)/(sigma*math.sqrt(T))
        d2 = d1 - sigma*math.sqrt(T)
        
        if t_o==0:
            C = S*math.exp(-1*q*(T))*norm.cdf(d1) - K*math.exp(-1*r*(T))*norm.cdf(d2)
            return C
        else:
            P = K*math.exp(-1*r*(T))*norm.cdf(-1*d2) - S*math.exp(-1*q*(T))*norm.cdf(-1*d1)
            return P
    else:
        return 0


def get_s_vol(underlying, lastdate, m = 20):

    stock_code = 'HKEX/' + underlying

    last_date = datetime.strptime(lastdate,'%Y-%m-%d')
    
    right = str(last_date)
    left = str(last_date - timedelta(days = m * 3))

    try:
        price_BB = quandl.get(stock_code, start_date = left , end_date = right)
    except:
        sleep(10)
        price_BB = quandl.get(stock_code, start_date = left , end_date = right)


    data = np.array(list(price_BB[-m:]['Nominal Price']))

    X = []
    Xsum = 0
    if len(data)>2:
        for i in range(len(data)-1):
        
            X.append(math.log(data[len(data)-i-1]/data[len(data)-i-2]))

        deltaT = 1/365

        Xsum = sum([ x*x for x in X])


        s_vol = math.sqrt(Xsum * (1/deltaT)/(len(data)-2))

    else:
        s_vol = 0.00

    return s_vol



def get_BBands(code, lastdate, period = 20):

    stock_code = 'HKEX/' + code

    mu = 0
    sigma = 0
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


    if len(price_BB)==1:

        u_d = '-'
  
        quote = price_BB[-1:]['Nominal Price']
        net_change = '-'
        change_per = '-'

    elif len(price_BB)==0: #has option, but stock is still not on list


        u_d = '-'
        quote = 0.00
        net_change = '-'
        change_per = '-'

    else:
        data = np.array(list(price_BB[-period:]['Nominal Price']))
        mu = np.mean(data)

        quote = price_BB[-1:]['Nominal Price']
        quote_yes = price_BB[-2:-1]['Nominal Price']
        net_change = round(float(quote)-float(quote_yes),2)
        change_per = round(100*(float(quote)-float(quote_yes))/float(quote_yes),2)
        
        sigma = np.std(data)
        upper = mu + 2*sigma
        down = mu - 2*sigma  

        if float(quote) >= upper:
            u_d = 'up'
        elif float(quote) <= down:
            u_d = 'down'
        else:
            u_d = '-'



    return u_d,net_change,change_per,float(quote)


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

    expiry_list = [0,0,'MAR19','APR18','MAY18','JUN18','JUL18','AUG18','SEP18','OCT18',0,0]
    maturity_list = [30,30,30, 27,30,28,30, 30,30,30,30,30]
    
    special_list = ['2018-04-30', '2018-05-31', '2018-06-29', '2018-07-31']
    
    time_list_4 = ['2018-04-03','2018-04-04','2018-04-06','2018-04-09','2018-04-10','2018-04-11','2018-04-12','2018-04-13', '2018-04-16', '2018-04-17', '2018-04-18', '2018-04-19', '2018-04-20','2018-04-23','2018-04-24','2018-04-25','2018-04-26','2018-04-27']

    #time_list_5 = ['2018-05-02','2018-05-03','2018-05-04','2018-05-07','2018-05-08','2018-05-09','2018-05-10','2018-05-11', '2018-05-14', '2018-05-15', '2018-05-16', '2018-05-17', '2018-05-18','2018-05-21','2018-05-23','2018-05-24','2018-05-25','2018-05-28', '2018-05-29', '2018-05-30']

    #time_list_6 = ['2018-06-01','2018-06-04','2018-06-05','2018-06-06','2018-06-07','2018-06-08','2018-06-11','2018-06-12','2018-06-13','2018-06-14','2018-06-15','2018-06-19','2018-06-20','2018-06-21','2018-06-22','2018-06-25','2018-06-26','2018-06-27']
    #time_list_7 = ['2018-07-03','2018-07-04','2018-07-05','2018-07-06','2018-07-09','2018-07-10','2018-07-11','2018-07-12','2018-07-13','2018-07-16','2018-07-17','2018-07-18','2018-07-19']
    time_list_7 = ['2018-07-23','2018-07-24','2018-07-25','2018-07-26','2018-07-27',]
    #time_list_7 = ['2018-04-30']
    
    for u_time in time_list_7:
        
        m = int(u_time[5:7].lstrip('0'))
        
        if u_time in special_list:
            expiry = expiry_list[m]

        else:
            expiry = expiry_list[m-1]


        # count = 1
        # last_date = str(current_date - timedelta(days = count))
        # while((not os.path.exists('tech_data/HK_tech_'+ last_date[0:10] + '.csv')) and last_date[0:10]>='2018-01-01'):
        #     count = count + 1
        #     #print count
        #     last_date = str(current_date - timedelta(days = count))

        # x = pd.read_csv('tech_data/HK_tech_'+ last_date[0:10] + '.csv')

        url = "http://www.hkex.com.hk/eng/stat/dmstat/dayrpt/dqe{0}.htm".format(u_time.replace("-", "")[2:])

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        response = webdriver.Chrome(chrome_options=chrome_options)

        response.get(url)
        sleep(10)

        data = pd.DataFrame()
        cols=[]

        for i in range(len(code)):
            try:
                o_data = response.find_element_by_name(code[i])
            except:
                continue

            o_data = o_data.text.encode('utf-8').split('\n')
            summary_data = get_option(code[i], underlying[i], o_data, u_time, expiry, maturity_list[m-1])
            if summary_data:
                print summary_data
                cols = summary_data.keys()
                price_data = pd.DataFrame.from_dict(summary_data, orient='index').T       
                data = pd.concat([data, price_data], sort=True)
                  
        if not os.path.exists('tech_data/'):
            os.makedirs('tech_data/')

        file_name = 'tech_data' + '/HK_tech_' + u_time
        data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', columns=cols, index=False)


