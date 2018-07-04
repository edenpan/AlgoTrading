# coding: utf-8
# author: chenfei
# usage: python quandl_finance.py 00700 2018-05-29 --days 10
import quandl
import argparse
from datetime import datetime
from datetime import timedelta
import numpy as np
import pandas as pd
quandl.ApiConfig.api_key = 'FxbKCf83-WeNae8uyxQg'

# get net position up/down, BBands(u,d,m) and up/down
def get_price(code, lastdate, horizon = 0, period = 20):
    
    if horizon == 0:
        begindate = lastdate
    else:
        last_date = datetime.strptime(lastdate,'%Y-%m-%d')
        begindate = str(last_date - timedelta(days = horizon*2))
    stock_code = 'HKEX/' + code
    price_temp = quandl.get(stock_code, start_date = begindate, end_date = lastdate)
    price_data = price_temp[-horizon-1:]
    
    mu = []
    sigma = []
    u_d = []
    net_change = []
    change_per = []
    last_date = datetime.strptime(lastdate,'%Y-%m-%d')
    for i in range(0, horizon + 1):
        right = str(last_date - timedelta(days = i))
        left = str(last_date - timedelta(days = i) - timedelta(days = period*2))

        price_temp = quandl.get(stock_code, start_date = left , end_date = right)

        data = np.array(list(price_temp[-period:]['Nominal Price']))
        mu.append(np.mean(data))
        quote = price_temp[-1:]['Nominal Price']
        if float(quote) >= np.mean(data):
            u_d.append('up')
        else:
            u_d.append('down')
        
        quote_yes = price_temp[-2:-1]['Nominal Price']
        net_change.append(float(quote)-float(quote_yes))
        change_per.append(round(100*(float(quote)-float(quote_yes))/float(quote_yes),2))
        sigma.append(np.std(data))

    mu.reverse()
    u_d.reverse()
    sigma.reverse()
    net_change.reverse()
    change_per.reverse()
    w = [c*2 for c in sigma]
    upper = [x + y for x, y in zip(mu, w)]
    down = [x - y for x, y in zip(mu, w)]   
        
    mu = pd.Series(mu)
    up = pd.Series(upper)
    do = pd.Series(down)
    pos = pd.Series(u_d)
    n_c =  pd.Series(net_change)
    c_p = pd.Series(change_per)

    price_data['BBands M'] = mu.values
    price_data['BBands U'] = up.values
    price_data['BBands D'] = do.values
    price_data['UP/DOWN'] = pos.values
    price_data['NET POS'] = n_c.values
    price_data['POS(%)'] = c_p.values

    return price_data


if __name__=="__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('code',help = '')
    argparser.add_argument('lastdate',help = '')
    argparser.add_argument('--days',help = '',type=int)
    
    args = argparser.parse_args()
    
    code = '0' + args.code
    lastdate = args.lastdate
    
    if args.days:
        horizon = args.days
        price_data = get_price(code, lastdate, horizon)
    else:
        price_data = get_price(code, lastdate)
        
    price_data = price_data.drop('Lot Size', axis=1, inplace=False)
    price_data = price_data.drop('Net Change', axis=1, inplace=False)
    price_data = price_data.drop('Change (%)', axis=1, inplace=False)
    price_data.insert(0, 'Symbol', args.code)

    file_name = args.code + '_quandl_BBands_' + lastdate + '_' + str(horizon)
    price_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A')
    

