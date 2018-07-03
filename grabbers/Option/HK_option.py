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

#get hk option code and their underlying 
def get_code():
    url = "http://www.hkex.com.hk/Market-Data/Futures-and-Options-Prices/Single-Stock/Stock-Options?sc_lang=en#&sttype=options"

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    response = webdriver.Chrome(chrome_options=chrome_options)
    response.get(url)
    sleep(4)
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
def get_option(code, underlying, price):

    # response.find_element_by_xpath('//*[@id="lhkexw-singlestockdetail"]/section/div[3]/div[1]/div[2]/div[1]/div[1]/div/div/div/em').click()

    # x = response.find_elements_by_xpath('//*[@id="lhkexw-singlestockdetail"]/section/div[3]/div[1]/div[2]/div[1]/div[1]/div/div/ul/li[2]')
    # x[0].click()
    url = "http://www.hkex.com.hk/market-data/futures-and-options-prices/single-stock/details?sc_lang=en&product={0}".format(code)

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    response = webdriver.Chrome(chrome_options=chrome_options)

    response.get(url)
    sleep(4)
    parser = html.fromstring(response.page_source)

    summary_data = OrderedDict()

    u_time = str(datetime.now())[0:10]
    summary_data.update({'Date':u_time})
    summary_data.update({'Code':code})

    ex = response.find_elements_by_xpath('//*[@id="lhkexw-singlestockdetail"]/section/div[3]/div[1]/div[2]/div[1]/div[1]/div/div/div/span')
    if len(ex) > 0:
        expiry = ex[0].text.encode('utf-8')
        summary_data.update({'Expiry':expiry})
    else:
        summary_data.update({'Expiry':'-'})

    summary_data.update({'Undelying':underlying})
    summary_data.update({'Closing':price})


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
    if len(summary) > 0:
        #OI Volume  IV  Bid/Ask Last    Strike  Last    Bid/Ask IV  Volume  OI
        summary_data.update({'C.OI':summary[0]})
        summary_data.update({'C.VOL':summary[1]})
        summary_data.update({'C.IV':summary[2]})
        summary_data.update({'C.B/A':summary[3]})
        summary_data.update({'C.LAST':summary[4]})
        summary_data.update({'Strike':summary[5]})
        summary_data.update({'P.LAST':summary[6]})
        summary_data.update({'P.B/A':summary[7]})
        summary_data.update({'P.IV':summary[8]})
        summary_data.update({'P.VOL':summary[9]})
        summary_data.update({'P.OI':summary[10]})
    else:
        summary_data.clear()     
        

    return summary_data                           


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
    # print code
    # print underlying
    # print index

    # sleep(3)
    ol = []
    sl = []
    for c, u in zip(code, underlying):
        if u in index:
            ol.append(c)    
            sl.append(u)
    # print ol 
    # print sl
    # sleep(30)
    Option_data = pd.DataFrame()
    cols=[]

    for i in range(len(ol)):

        price = get_price(sl[i])
        summary_data = get_option(ol[i], sl[i], price)
        if summary_data:
            print summary_data
            cols = summary_data.keys()
            price_data = pd.DataFrame.from_dict(summary_data, orient='index').T       
            Option_data = pd.concat([Option_data, price_data], sort=True)
    
    u_time = str(datetime.now())[0:10]           
    if not os.path.exists('data/'):
        os.makedirs('data/')

    file_name = 'data' + '/HK_Option_' + u_time
    Option_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', columns=cols, index=False)


