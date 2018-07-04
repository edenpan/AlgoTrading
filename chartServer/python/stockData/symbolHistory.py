# coding: utf-8
import sys
import requests
import json
from dateutil import parser
import time

class SymbolHistory():
	def __init__(self, symbolName, fromDate, toDate, resolution):
		self.symbolName = symbolName
		self.fromDate = fromDate
		self.toDate = toDate
		self.resolution = getResolution(resolution).get('p')
		# self.url = 'http://127.0.0.1:8888/history/%s?resolution=%s&starttime=%s&endtime=%s'%(self.symbolName, self.resolution, self.fromDate, self.toDate)
		self.url = 'http://18.182.12.142:8888/history/%s?resolution=%s&starttime=%s&endtime=%s'%(self.symbolName, self.resolution, self.fromDate, self.toDate)
	
	def getHistory(self):
		response = requests.get(self.url)
		print self.url
		history = response.text
		historyList = json.loads(history)
		t =[]
		c = []
		o = []
		l = []
		h = []
		v = []
		result = {}
		if(0 == len(historyList)):
			result["s"] = "no_data"
		else :			
			for tick in historyList:
				c.append(tick.get('adjusted_close'))
				o.append(tick.get('open'))
				h.append(tick.get('high'))
				l.append(tick.get('low'))
				v.append(tick.get('volume'))
				# print time.mktime(parser.parse(tick.get('date')))
				inttime = int(time.mktime(parser.parse(tick.get('date')).timetuple()))
				t.append(inttime)
			
			result["s"] = "ok"
			result["t"] = t
			result["v"] = v
			result["c"] = c
			result["l"] = l
			result["h"] = h
			result["o"] = o
		return result





# get the resolution period.
# day / hour / 30minutes / 15minutes / 5minutes / minute
def getResolution(x):
	return {
		'1':{'p':'minute'},
		'5':{'p':'5minutes'},
		'15':{'p':'15minutes'},
		'30':{'p':'30minutes'},
		'60':{'p':'hour'},
		'D':{'p':'day'},
		'1D':{'p':'day'},
	}.get(x)

# history = SymbolHistory('700', '946684800', '1529971200','1D')
# history.getHistory()

