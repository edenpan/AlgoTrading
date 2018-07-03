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
def get_option(code, underlying, price, x):

    # response.find_element_by_xpath('//*[@id="lhkexw-singlestockdetail"]/section/div[3]/div[1]/div[2]/div[1]/div[1]/div/div/div/em').click()

    # x = response.find_elements_by_xpath('//*[@id="lhkexw-singlestockdetail"]/section/div[3]/div[1]/div[2]/div[1]/div[1]/div/div/ul/li[2]')
    # x[0].click()
    url = "http://www.hkex.com.hk/market-data/futures-and-options-prices/single-stock/details?sc_lang=en&product={0}".format(code)

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    response = webdriver.Chrome(chrome_options=chrome_options)

    response.get(url)
    sleep(3)
    parser = html.fromstring(response.page_source)

    summary_data = OrderedDict()

    u_time = str(datetime.now())[0:10]
    summary_data.update({'Date':u_time})
    summary_data.update({'Stock Code':underlying})
    summary_data.update({'Option Code':code})

    # ex = response.find_elements_by_xpath('//*[@id="lhkexw-singlestockdetail"]/section/div[3]/div[1]/div[2]/div[1]/div[1]/div/div/div/span')
    # if len(ex) > 0:
    #     expiry = ex[0].text.encode('utf-8')
    #     summary_data.update({'Expiry':expiry})
    # else:
    #     summary_data.update({'Expiry':'-'})

    summary_data.update({'Closing':price})

    if len(underlying)<4:
            underlying = (4-len(underlying))*'0' + underlying

    mu,upper,down,u_d,net_change,change_per,u_d_2 = get_BBands(underlying, u_time, 20)
    summary_data.update({'Net Change':net_change})
    summary_data.update({'Change(%)':change_per})
    
    summary_data.update({'BBands M':round(mu,2)})
    summary_data.update({'BBands U':round(upper,2)})
    summary_data.update({'BBands D':round(down,2)})
    summary_data.update({'U/D(mu)':u_d})
    summary_data.update({'U/D(B)':u_d_2})

    o_list = parser.xpath('//*[@id="option"]/tbody/tr')

    diff = 9999
    #select at the money
    index = 0
    if price != '-' and len(o_list)>0:
        for i in range(len(o_list)):
            s = o_list[i].xpath('./td[6]')[0].text
            #print s
            #strike = s[0].text
            if abs(float(s) - float(price)) < diff:
                diff = abs(float(s)-float(price))
                index = i

    summary = parser.xpath('//*[@id="option"]/tbody/tr[{0}]/td/text()'.format(index+1))
    c_u_d = ''
    if len(summary) > 0:
        #OI Volume  IV  Bid/Ask Last    Strike  Last    Bid/Ask IV  Volume  OI
        index = x[(x['Option Code'] == code)].index.tolist()[0]
        last_civ = x[index:index+1]['IV(1C)'].tolist()[0]
        # last_piv = x[index:index+1]['P.IV'].tolist()[0]

        if summary[2]!='-' and last_civ!='-' and float(summary[2].rstrip('%')) < float(last_civ.rstrip('%')):
            c_u_d = 'down'
        elif summary[2]!='-' and last_civ!='-' and float(summary[2].rstrip('%')) >= float(last_civ.rstrip('%')):
            c_u_d = 'up'
        else:
            c_u_d = '-'

        # if summary[8]!='-' and summary[2] < last_piv:
        #     p_u_d = 'down'
        # elif summary[8]!='-' and summary[2] >= last_piv
        #     p_u_d = 'up'
        # else:
        #     p_u_d = '-'

        summary_data.update({'IV(1C)':summary[2]})
        summary_data.update({'U/D(1C)':c_u_d})

        #summary_data.update({'IV(1P)':summary[8]})
    else:
        summary_data.clear()
     
    return summary_data                           

# get net position up/down, BBands(u,d,m) and up/down
def get_BBands(code, lastdate, period = 20):

    code = code + '.HK'
    url = "https://finance.yahoo.com/quote/%s/history?p=%s"%(code,code)
    response = requests.get(url)

    parser = html.fromstring(response.text)


    quote = parser.xpath('//table[contains(@data-test,"historical-prices")]/tbody[1]/tr')
    
    mu = 0
    sigma = 0
    u_d = ''
    u_d_2 = ''
    net_change = 0
    change_per = 0

    count=0
    c_price=''
    y_price=''
    BBdata = []

    for d in quote:
        terms = d.xpath('.//td//text()')
        if len(terms) > 5:
            if count == 0:
                c_price = str(terms[5]).strip()
            elif count == 1:
                y_price = str(terms[5]).strip()
            
            count = count + 1
            BBdata.append(float(str(terms[5]).strip()))
            
            if count == period:
                break
        else:
            continue

    data = np.array(BBdata)
    mu = np.mean(data)
    if float(c_price) >= mu:
        u_d = 'up'
    else:
        u_d = 'down'
    

    net_change = round(float(c_price)-float(y_price),2)
    change_per = round(100*(float(c_price)-float(y_price))/float(y_price),2)
    sigma = np.std(data)

    upper = mu + 2*sigma
    down = mu - 2*sigma  

    if float(c_price) >= upper:
        u_d_2 = 'up'
    elif float(c_price) <= down:
        u_d_2 = 'down'
    else:
        u_d_2 = '-'

    # price_data['BBands M'] = mu.values
    # price_data['BBands U'] = up.values
    # price_data['BBands D'] = do.values
    # price_data['UP/DOWN'] = pos.values
    # price_data['NET POS'] = n_c.values
    # price_data['POS(%)'] = c_p.values

    return mu,upper,down,u_d,net_change,change_per,u_d_2


#get underlying price (bloomberg) 
def get_price(code):
    url = "https://www.bloomberg.com/quote/{0}:HK"
    url = url.format(code)
    #print url
    #user = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
    #url = "https://www.bloomberg.com/quote/HSI:IND/members"
    accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    acceptEncoding = 'gzip, deflate, br'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    response = requests.get(url,headers={"User-Agent":user_agent, "Accept":accept, "accept-encoding":acceptEncoding})
    sleep(3)
    parser = html.fromstring(response.text)

    quote = parser.xpath('//section[contains(@class,"snapshotSummary")]//section[contains(@class,"price")]//span[contains(@class,"priceText")]//text()')

    if len(quote) > 0:
        price = str(quote[0]).strip()
    else:
        price = '-'

    return price


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

    u_time = str(datetime.now())[0:10]
    current_date = datetime.strptime(u_time,'%Y-%m-%d')

    count = 1
    last_date = str(current_date - timedelta(days = count))
    while((not os.path.exists('tech_data/HK_Technical_'+ last_date[0:10] + '.csv')) and last_date[0:10]>='2018-06-01'):
        count = count + 1
        #print count
        last_date = str(current_date - timedelta(days = count))

    x = pd.read_csv('tech_data/HK_Technical_'+ last_date[0:10] + '.csv')

    data = pd.DataFrame()
    cols=[]

    for i in range(len(ol)):
        price = get_price(sl[i])
        summary_data = get_option(ol[i], sl[i], price, x)
        if summary_data:
            print summary_data
            cols = summary_data.keys()
            price_data = pd.DataFrame.from_dict(summary_data, orient='index').T       
            data = pd.concat([data, price_data], sort=True)
              
    if not os.path.exists('tech_data/'):
        os.makedirs('tech_data/')

    file_name = 'tech_data' + '/HK_Technical_' + u_time
    data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', columns=cols, index=False)


