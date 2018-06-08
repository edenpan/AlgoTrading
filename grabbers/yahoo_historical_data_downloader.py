import pandas as pd
import requests
import re
from selenium import webdriver
import time

if __name__=="__main__":
    driver = webdriver.Chrome()
    link = "https://warrants-hk.credit-suisse.com/en/underlying/hsi_e.cgi"
    f = requests.get(link)
    symbolslist = re.findall(r'<td.*?><a.*?>(\d+)(?=</a></td>)', f.text, re.MULTILINE)
    for symbol in symbolslist[:50]:
        xsymbol = symbol[1:]
        url = 'https://finance.yahoo.com/quote/%s.HK/history?p=%s.HK'%(xsymbol,xsymbol)
        driver.get(url)
        driver.find_element_by_xpath("//*[@id='Col1-1-HistoricalDataTable-Proxy']/section/div[1]/div[1]/div[1]/span[2]").click()
        sDate = driver.find_element_by_name("startDate")
        sDate.clear()
        sDate.send_keys("1/1/2015")
        driver.find_element_by_xpath("//*[@id='Col1-1-HistoricalDataTable-Proxy']/section/div[1]/div[1]/div[1]/span[2]/div/div[3]/button[1]").click()
        driver.find_element_by_xpath("//*[@id='Col1-1-HistoricalDataTable-Proxy']/section/div[1]/div[2]/span[2]").click()
        time.sleep(2)
    driver.close()
    