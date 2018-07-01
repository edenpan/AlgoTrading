# APIs Description

## Services

name	|	Description
------------- | -------------
time	| provide server time
config | the chart basic config
symbols | current support symbols
history | trading data
search	| return search result


## Get

###/time

	GET 	/time
	1530001150613


### /search

	GET 	/search
	[{"symbol":"0939","full_name":"China Construction Bank","description":"China Construction Bank-China Construction Bank","exchange":"","ticker":"0939","type":"stock"},
	{"symbol":"0005","full_name":"HSBC Holdings plc","description":"HSBC Holdings plc-HSBC Holdings plc","exchange":"","ticker":"0005","type":"stock"}]

### /config

	GET /config
	{
	  "supports_search": true,
	  "supports_group_request": false,
	  "supported_resolutions": [
	    "1",
	    "5",
	    "15",
	    "30",
	    "60",
	    "1D",
	    "1W",
	    "1M"
	  ],
	  "supports_marks": false,
	  "supports_time": true
	}
	
### /symbols?symbol=<symbol>	

	GET /symbols?symbol=<symbol>	
	
	{
	  "name": "0700",
	  "full_name": "Tencent Holdings Limited",
	  "ticker": "0700",
	  "description": "0700-Tencent Holdings Limited",
	  "type": "stock",
	  "session": "0930-1200,1300-1600",
	  "exchange": "香港证券交易所",
	  "listed_exchange": "香港证券交易所",
	  "timezone": "Asia/Hong_Kong",
	  "pricescale": 100,
	  "minmov": 1,
	  "has_intraday": true,
	  "supported_resolutions": [
	    "1",
	    "5",
	    "15",
	    "30",
	    "60",
	    "1D",
	    "1W",
	    "1M"
	  ],
	  "has_daily": true,
	  "has_weekly_and_monthly": true,
	  "has_no_volume": false,
	  "sector": "Tencent Holdings Limited",
	  "industry": "0700",
	  "currency_code": "HKD"
	}
	
### /history?symbol=0700

	GET /history?symbol=0700
		{
	  "s": "ok",
	  "t": [
	    1528335000000,
	    1528335060000,
	    1528335120000,
	    1528335180000,
	  ],
	  "c": [
	    429.4,
	    429.2,
	    429.8,
	    430
	  ],
	  "o": [
	    431.2,
	    429.8,
	    429.2,
	    429.8
	  ],
	  "l": [
	    429.4,
	    429,
	    429,
	    429.6
	  ],
	  "h": [
	    431.6,
	    431,
	    430,
	    430.6
	  ],
	  "v": [
	    219700,
	    779000,
	    186900,
	    499600
	   ]
	}	
	
### /search

	GET /search

	[
	  {
	    "symbol": "0939",
	    "full_name": "China Construction Bank",
	    "description": "China Construction Bank-China Construction Bank",
	    "exchange": "",
	    "ticker": "0939",
	    "type": "stock"
	  },
	  {
	    "symbol": "0005",
	    "full_name": "HSBC Holdings plc",
	    "description": "HSBC Holdings plc-HSBC Holdings plc",
	    "exchange": "",
	    "ticker": "0005",
	    "type": "stock"
	  }
	  ...
	]	
		
	


