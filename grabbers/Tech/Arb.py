import pandas as pd
import numpy as np
from datetime import datetime 
from datetime import timedelta
import os

def arbitrage(begin, end, number = 5):
	
	Pnl = []
	special_list = ['2018-04-27', '2018-05-30', '2018-06-28', '2018-07-30']

	while begin != end:

		if begin not in special_list:
			data = pd.read_csv('tech_data/HK_tech_' + begin + '.csv')

			#choose most 10 mispricing call options
			settle_c = np.array(data['Settle(1C)'].tolist())
			t_p_c =  np.array(data['T-P(S,1C)'].tolist())
			
			diff = settle_c - t_p_c

			sort_index = np.argsort(diff)

			buy_call_index = sort_index[0:number]
			short_call_index = sort_index[-1*number:]

			call_portfolio = {}
			buy_calls = [] 
			short_calls = []

			buy_settles = []
			short_settles = []

			#construct call portfolio
			for i in range(number):
			    buy_calls.append(data[buy_call_index[i]:buy_call_index[i]+1]['Option Code'].tolist()[0])
			    short_calls.append(data[short_call_index[i]:short_call_index[i]+1]['Option Code'].tolist()[0])

				#buy_settles.append(data[buy_call_index[i]:buy_call_index[i]+1]['Settle(1C)'].tolist()[0])
				#short_settles.append(data[short_call_index[i]:short_call_index[i]+1]['Settle(1C)'].tolist()[0])

			call_portfolio['1'] = buy_calls
			call_portfolio['-1'] = short_calls
			#call



			current_date = datetime.strptime(begin,'%Y-%m-%d')
			
			count = 1
			next_date = str(current_date + timedelta(days = count))
			while((not os.path.exists('tech_data/HK_tech_'+ next_date[0:10] + '.csv')) and next_date[0:10]<='2018-10-01'):
				count = count + 1
		    	#print count
				next_date = str(current_date + timedelta(days = count))

			data_next = pd.read_csv('tech_data/HK_tech_'+ next_date[0:10] + '.csv')

			#PNL for buy
			pnl_buy = 0
			pnl_short = 0

			for i in range(len(call_portfolio['1'])):
			    index = data_next[(data_next['Option Code'] == call_portfolio['1'][i])].index.tolist()[0]
			    #if i == 0:
			    #	b_position = 500 * float(data_next[index:index+1]['Change(1C)'].tolist()[0])
			    #elif i == 1:

			    #b_position = float(data_next[index:index+1]['Open(1C)'].tolist()[0]) - (float(data_next[index:index+1]['Settle(1C)'].tolist()[0]) - float(data_next[index:index+1]['Change(1C)'].tolist()[0]))
			    b_position = float(data_next[index:index+1]['Settle(1C)'].tolist()[0]) - float(data_next[index:index+1]['Open(1C)'].tolist()[0])
			    pnl_buy = pnl_buy + b_position
			    
			for i in range(len(call_portfolio['-1'])):
			    index = data_next[(data_next['Option Code'] == call_portfolio['-1'][i])].index.tolist()[0]
			    #s_position = float(data_next[index:index+1]['Change(1C)'].tolist()[0])
			    #s_position = float(data_next[index:index+1]['Open(1C)'].tolist()[0]) - (float(data_next[index:index+1]['Settle(1C)'].tolist()[0]) - float(data_next[index:index+1]['Change(1C)'].tolist()[0]))
			    s_position = float(data_next[index:index+1]['Settle(1C)'].tolist()[0]) - float(data_next[index:index+1]['Open(1C)'].tolist()[0])
			    pnl_short = pnl_short - s_position

			pnl = pnl_short + pnl_buy
			
			Pnl.append(round(pnl,2))

			begin = next_date[0:10]
		
		else:

			count = 1
			current_date = datetime.strptime(begin,'%Y-%m-%d')
			next_date = str(current_date + timedelta(days = count))
			while((not os.path.exists('tech_data/HK_tech_'+ next_date[0:10] + '.csv')) and next_date[0:10]<='2018-10-01'):
				count = count + 1
		   	
				next_date = str(current_date + timedelta(days = count))

			begin = next_date[0:10]

	return Pnl


if __name__=="__main__":

	begin = '2018-05-02'
	end = '2018-07-20'

	#5:c - c(-27), c - o(-15), o - c(-11), only buy(-4), only short(-7)
	#1:c - c(-7.44), c - o(-18.2), o - c(10.76), only buy(-4), only short(-7)
	

	result = arbitrage(begin, end, 1)
	print result, sum(result)












