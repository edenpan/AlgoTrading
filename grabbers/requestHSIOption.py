import urllib2

from http import cookiejar
import time

def get_option():
	orgUrl = 'http://www.hkex.com.hk/Market-Data/Futures-and-Options-Prices/Equity-Index/Hang-Seng-Index-Futures-and-Options?sc_lang=en'
	accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
	user = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
	SecurityPolicy = "frame-ancestors 'self' http://www.hkgem.com http://www.hkex.com.hk http://www.hkexgroup.com http://sc.hkex.com.hk http://sc.hkexnews.hk http://www.hkexnews.hk http://203.78.5.185 http://203.78.5.190; frame-src 'self' http://www.hkgem.com http://www.hkex.com.hk http://www.hkexgroup.com http://sc.hkex.com.hk http://sc.hkexnews.hk http://www.hkexnews.hk http://asia.tools.euroland.com http://203.78.5.185 http://203.78.5.190;"
	cookie = cookiejar.CookieJar()
	handler=urllib2.HTTPCookieProcessor(cookie)
	opener = urllib2.build_opener(handler)
	opener.addheaders = [('User-agent', user),('Accept', accept),("Content-Security-Policy", SecurityPolicy)]
	response = opener.open(orgUrl)
	cont = response.read()
	searchToken = 'Encrypted-Token'
	cont2 = cont[cont.find(searchToken):cont.find(searchToken)+200]
	cont3 = cont2[cont2.find('return') + 8:]
	token = cont3[:cont3.find("\"")]

	month = '062018'
	fr = '14400'
	to = '40000'
	qid = int(time.time() * 1000)
	slash = qid - 1102
	url = "https://www1.hkex.com.hk/hkexwidget/data/getderivativesoption?lang=eng&token={0}&ats=HSI&con={1}&fr={2}&to={3}&type=0&qid={4}&callback=jQuery3110595211137306934_1528993752048&_={5}"
	url = url.format(token,month,fr,to,qid,slash)
	print url
	ref = 'http://www.hkex.com.hk/Market-Data/Futures-and-Options-Prices/Equity-Index/Hang-Seng-Index-Futures-and-Options?sc_lang=en'
	opener.addheaders = [('Referer',ref)]
	response = opener.open(url)
	print response.read()
	
get_option()    
	
