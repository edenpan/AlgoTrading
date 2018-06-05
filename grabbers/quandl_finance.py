# coding: utf-8
# author: chenfei
# usage: python quandl_finance.py 00700 2018-05-29 --days 10
import quandl
import argparse
from datetime import datetime
from datetime import timedelta
quandl.ApiConfig.api_key = 'FxbKCf83-WeNae8uyxQg'


def get_price(code, lastdate, horizon = 0):
    
    if horizon == 0:
        begindate = lastdate
    else:
        last_date = datetime.strptime(lastdate,'%Y-%m-%d')
        begindate = str(last_date - timedelta(days = horizon))
    
    stock_code = 'HKEX/' + code
    price_data = quandl.get(stock_code, start_date = begindate, end_date = lastdate)

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
    price_data.insert(0, 'Symbol', args.code)

    file_name = args.code + '_quandl_' + lastdate + '_' + str(horizon)
    price_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A')
    

