import pandas as pd
import requests
import re
from selenium import webdriver
import time


link = "https://warrants-hk.credit-suisse.com/en/underlying/hsi_e.cgi"
f = requests.get(link)
symbolslist0 = re.findall(r'<td.*?><a.*?>(\d+)(?=</a></td>)', f.text, re.MULTILINE)

flink = 'http://stock360.hkej.com/quotePlus/'

driver = webdriver.Chrome()

df_market = pd.DataFrame(columns=['Symbol','High','Open','Amount','Low','Close','Volume','Beta','PE','EPS','Divident', 
                   'Institute1','Last Advice1','Current Advice1','Last Price1','Current Price1', 
                   'Institute2','Last Advice2','Current Advice2','Last Price2','Current Price2', 
                   'Institute3','Last Advice3','Current Advice3','Last Price3','Current Price3', 
                   'Institute4','Last Advice4','Current Advice4','Last Price4','Current Price4', 
                   'Institute5','Last Advice5','Current Advice5','Last Price5','Current Price5'])  

for symbol in symbolslist[:50]:
    link = flink + symbol
    driver.get(link)
    time.sleep(1)
    #high
    hi = driver.find_element_by_xpath('/html/body/div[6]/div[1]/div[2]/div/div[2]/div[2]/div[2]/table/tbody/tr[2]/td[1]').text
    #open
    op = driver.find_element_by_xpath('/html/body/div[6]/div[1]/div[2]/div/div[2]/div[2]/div[2]/table/tbody/tr[2]/td[2]').text 
    #traded amount
    amt = driver.find_element_by_xpath('/html/body/div[6]/div[1]/div[2]/div/div[2]/div[2]/div[2]/table/tbody/tr[2]/td[3]').text
    #low
    lo = driver.find_element_by_xpath('/html/body/div[6]/div[1]/div[2]/div/div[2]/div[2]/div[2]/table/tbody/tr[4]/td[1]').text
    #close
    cls = driver.find_element_by_xpath('/html/body/div[6]/div[1]/div[2]/div/div[2]/div[2]/div[2]/table/tbody/tr[4]/td[2]').text
    #traded volume
    volm = driver.find_element_by_xpath('/html/body/div[6]/div[1]/div[2]/div/div[2]/div[2]/div[2]/table/tbody/tr[4]/td[3]').text
    #beta
    xbeta = driver.find_element_by_xpath('/html/body/div[6]/div[1]/div[2]/div/div[2]/div[3]/div[3]/p[5]').text
    beta = xbeta[11:len(xbeta)]
    #pe
    xpe = driver.find_element_by_xpath('/html/body/div[6]/div[1]/div[2]/div/div[2]/div[3]/div[3]/p[2]').text
    pe = xpe[11:len(xpe)]
    #eps
    xeps = driver.find_element_by_xpath('/html/body/div[6]/div[1]/div[2]/div/div[2]/div[3]/div[3]/p[1]').text
    eps = xeps[10:len(xeps)]
    #dvd
    xdvd = driver.find_element_by_xpath('/html/body/div[6]/div[1]/div[2]/div/div[2]/div[3]/div[3]/p[4]').text
    dvd = xdvd[7:len(xdvd)]
    #top 5 advices
    advs1 = driver.find_element_by_xpath('/html/body/div[9]/div[2]/div[3]/div[3]/table/tbody/tr[2]').text.split(' ')
    advs2 = driver.find_element_by_xpath('/html/body/div[9]/div[2]/div[3]/div[3]/table/tbody/tr[3]').text.split(' ')
    advs3 = driver.find_element_by_xpath('/html/body/div[9]/div[2]/div[3]/div[3]/table/tbody/tr[4]').text.split(' ')
    advs4 = driver.find_element_by_xpath('/html/body/div[9]/div[2]/div[3]/div[3]/table/tbody/tr[5]').text.split(' ')
    advs5 = driver.find_element_by_xpath('/html/body/div[9]/div[2]/div[3]/div[3]/table/tbody/tr[6]').text.split(' ')
    
    xsymbol = symbol.zfill(5) #fill 0 infront
    data = pd.DataFrame({'Symbol':[xsymbol],'High':[hi],'Open':[op],'Amount':amt,'Low':[lo],'Close':[cls],'Volume':volm,'Beta':[beta],'PE':[pe],'EPS':[eps],'Divident':[dvd], 
                   'Institute1':advs1[0],'Last Advice1':advs1[1],'Current Advice1':advs1[2],'Last Price1':advs1[3],'Current Price1':advs1[4], 
                   'Institute2':advs2[0],'Last Advice2':advs2[1],'Current Advice2':advs2[2],'Last Price2':advs2[3],'Current Price2':advs2[4], 
                   'Institute3':advs3[0],'Last Advice3':advs3[1],'Current Advice3':advs3[2],'Last Price3':advs3[3],'Current Price3':advs3[4], 
                   'Institute4':advs4[0],'Last Advice4':advs4[1],'Current Advice4':advs4[2],'Last Price4':advs4[3],'Current Price4':advs4[4], 
                   'Institute5':advs5[0],'Last Advice5':advs5[1],'Current Advice5':advs5[2],'Last Price5':advs5[3],'Current Price5':advs5[4], 
                  })
    
    df_market = df_market.append(data)
driver.close()

df_market = df_market.set_index('Symbol')
xcolumns = ['High','Open','Amount','Low','Close','Volume','Beta','PE','EPS','Divident', 
                   'Institute1','Last Advice1','Current Advice1','Last Price1','Current Price1', 
                   'Institute2','Last Advice2','Current Advice2','Last Price2','Current Price2', 
                   'Institute3','Last Advice3','Current Advice3','Last Price3','Current Price3', 
                   'Institute4','Last Advice4','Current Advice4','Last Price4','Current Price4', 
                   'Institute5','Last Advice5','Current Advice5','Last Price5','Current Price5']
df_market = df_market.set_index('Symbol')
date = time.strftime("%Y%m%d")
df_market.to_csv(date+'HSI.csv', columns = xcolumns)
