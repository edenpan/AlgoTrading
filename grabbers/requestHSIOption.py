import urllib2

from http import cookiejar
import time
import json

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
		self.ats = ['HSI','CKH']

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
		return  conlist

	def getOption(self, code):
		conlist = self.getMonthList(code)
		
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
			print response.read()

	def getAllPrice(self):
		for code in self.ats:
			self.getOption(code)

option = OptionPrice()
option.getAllPrice()
	
