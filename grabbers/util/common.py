# -*- coding=utf-8 -*-
# Use for some common funtion

#Get the HSI Index List from Bloomberg

import requests
from lxml import html

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