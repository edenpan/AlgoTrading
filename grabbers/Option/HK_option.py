#http://www.hkex.com.hk/Market-Data/Futures-and-Options-Prices/Single-Stock/Stock-Options?sc_lang=en#&sttype=options

import urllib2
from http import cookiejar
import time
import json
import argparse
from pandas.io.json import json_normalize
import pandas as pd
from datetime import datetime
from lxml import html  
import requests
from time import sleep
from collections import OrderedDict
import os

def get_price(code):
    
        token = get_stock_Token(code)
        url = "https://www1.hkex.com.hk/hkexwidget/data/getequityquote?sym={0}&token={1}&lang=eng&qid=1528175147171&callback=jQuery3110305152158354391_1528175145792&_=1528175145793"
        url = url.format(code,token)
        ref = 'http://www.hkex.com.hk/Market-Data/Securities-Prices/Equities/Equities-Quote?sym=700&sc_lang=en'
        user = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
        response = requests.get(url,headers={"User-Agent":user, "Referer":ref})
        
        cont = response.content
        #print cont
        ad_cont = cont[cont.index('(')+1: -1]
        data = json.loads(ad_cont)

        price = data['data']['quote']['ls'].encode('utf-8')

        return price

def get_stock_Token(code):
        orgUrl = 'http://www.hkex.com.hk/Market-Data/Securities-Prices/Equities/Equities-Quote?sym={0}&sc_lang=en'
        accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
        user = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
        orgUrl = orgUrl.format(code)
        res1 = requests.get(orgUrl,headers={"User-Agent":user, "Accept":accept})
        cont = res1.content
        searchToken = 'Encrypted-Token'
        cont2 = cont[cont.find(searchToken):cont.find(searchToken)+200 ]
        cont3 = cont2[cont2.find('return') + 8:]
        token = cont3[:cont3.find("\"")]
        return token


class OptionPrice:
    
    def __init__(self):
        self.cookie = cookiejar.CookieJar()
        self.handler=urllib2.HTTPCookieProcessor(self.cookie)
        self.opener = urllib2.build_opener(self.handler)
        accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
        user = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
        SecurityPolicy = "frame-ancestors 'self' http://www.hkgem.com http://www.hkex.com.hk http://www.hkexgroup.com http://sc.hkex.com.hk http://sc.hkexnews.hk http://www.hkexnews.hk http://203.78.5.185 http://203.78.5.190; frame-src 'self' http://www.hkgem.com http://www.hkex.com.hk http://www.hkexgroup.com http://sc.hkex.com.hk http://sc.hkexnews.hk http://www.hkexnews.hk http://asia.tools.euroland.com http://203.78.5.185 http://203.78.5.190;"
        self.opener.addheaders = [('User-agent', user),('Accept', accept),("Content-Security-Policy", SecurityPolicy)]
        self.getToken()
        self.ats = []
        self.underlying = []
        self.price = []




    def getToken(self):
        orgUrl = 'http://www.hkex.com.hk/Market-Data/Futures-and-Options-Prices/Equity-Index/Hang-Seng-Index-Futures-and-Options?sc_lang=en'
        response = self.opener.open(orgUrl)
        cont = response.read()
        searchToken = 'Encrypted-Token'
        cont2 = cont[cont.find(searchToken):cont.find(searchToken)+200]
        cont3 = cont2[cont2.find('return') + 8:]
        self.token = cont3[:cont3.find("\"")]

    def getMonthList(self, code):
        url = 'https://www1.hkex.com.hk/hkexwidget/data/getoptioncontractlist?lang=eng&token={0}&ats={1}&qid={2}&callback=jQuery31109370303295785578_1529140424891&_={3}'
        qid = int(time.time() * 1000)
        slash = qid - 1102
        url = url.format(self.token,code,qid,slash)
        ref = 'http://www.hkex.com.hk/Market-Data/Futures-and-Options-Prices/Equity-Index/Hang-Seng-Index-Futures-and-Options?sc_lang=en'
        self.opener.addheaders = [('Referer',ref)]
        response = self.opener.open(url)
        rangeStr = response.read()
        rangeStr = rangeStr[41:-1]
        text = json.loads(rangeStr)
        conlist = text.get("data").get("conlist")
        return conlist

    def getOption(self, code):
        conlist = self.getMonthList(code)
        c = 0
        for con in conlist:
            month = con.get('id')
            qid = int(time.time() * 1000)
            slash = qid - 1102
            rangeurl = "https://www1.hkex.com.hk/hkexwidget/data/getderivativesoption?lang=eng&token={0}&ats={1}&con={2}&fr=null&to=null&type=0&qid={3}&callback=jQuery3110595211137306934_1528993752048&_={4}"
            rangeurl = rangeurl.format(self.token,code,month,qid,slash)
            response = self.opener.open(rangeurl)
            rangeStr = response.read()
            rangeStr = rangeStr[40:-1]
            text = json.loads(rangeStr)

            maxStr =  str(text.get('data').get("max")).translate(None, ',')
            maxStr = "%d" % float(maxStr)
            minStr =  str(text.get('data').get("min")).translate(None, ',')
            minStr = "%d" % float(minStr)
            url = "https://www1.hkex.com.hk/hkexwidget/data/getderivativesoption?lang=eng&token={0}&ats={1}&con={2}&fr={3}&to={4}&type=0&qid={5}&callback=jQuery3110595211137306934_1528993752048&_={6}"
            url = url.format(self.token,code,month,minStr, maxStr,qid,slash)
            
            response = self.opener.open(url)
            s = response.read()
            if c == 0:
                s = s[s.index('(')+1: -1]
                data = json.loads(s)
                u_time = str(datetime.now())[0:10]
                option_data = json_normalize(data['data']['optionlist'])
                option_data.insert(loc=0, column='Date', value=u_time)
                option_data.insert(loc=1, column='Underlying', value=self.underlying[0])
                option_data = option_data.replace('', '-', regex=True)

                eod_price = float(self.price[0])
                diff = abs(eod_price - float(option_data[0:1]['strike']))
                #min(myList, key=lambda x:abs(x-eod_price))
                index = 0

                for ind, row in option_data.iterrows():
                    if abs(eod_price - float(row['strike'])) < diff:
                        diff = abs(eod_price - float(row['strike']))
                        index = index + 1

                option_data = option_data[index:index+1]
                #option_data = option_data.insert(1, 'Underlying', self.underlying[0])
                file_name =  code + '_' + u_time
                option_data.to_csv(file_name + '.csv', sep=',', na_rep='-', index=False)    
                break   
            c = c + 1        
        
    def getAllPrice(self):
        for code in self.ats:
            self.getOption(code)


if __name__=="__main__":
    
    argparser = argparse.ArgumentParser()
    argparser.add_argument('code',help = '')
    argparser.add_argument('underlying',help = '')
    args = argparser.parse_args()

    code = args.code
    EOD_price = get_price(args.underlying.lstrip('0'))

    option = OptionPrice()
    option.ats.append(code)
    option.price.append(EOD_price)
    option.underlying.append(args.underlying)

    option.getAllPrice()



