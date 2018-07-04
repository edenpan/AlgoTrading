from flask import Flask
import time
import json
from flask import request
from flask import Response
from stockData.symbolInfo import SymbolHSIInfo
from stockData.symbolListInfo import SymbolListInfo
from stockData.symbolHistory import SymbolHistory
app = Flask(__name__)

@app.route('/')
def hello_test():
    return 'hello, test'

@app.route('/time')
def get_time():
    return str(int(time.time() * 1000))

@app.route('/config')
def get_config():
    config = DefConfig()
    s = json.dumps(config.__dict__)
    return setJsonRes(s)
    

@app.route('/search')
def get_searchList():
    symbolList = SymbolListInfo()
    return setJsonRes(symbolList.getSymbollistStr())

@app.route('/symbols')
def get_symbols():
    symbol = request.args.get('symbol')
    symbolList = SymbolListInfo().getSymbollist()
    for symbolInfo  in symbolList:
        if(symbolInfo.get("symbol") == symbol):
            symInfo = SymbolHSIInfo(symbol, symbolInfo.get("full_name"), symbolInfo.get("description"))
    return setJsonRes(json.dumps(symInfo.__dict__))

@app.route('/history')    
def get_history():
    symbol = request.args.get('symbol')
    dateFrom = request.args.get('from')
    dateTo = request.args.get('to')
    resolution = request.args.get('resolution')
    print symbol,dateFrom,dateTo,resolution
    history = SymbolHistory(symbol, dateFrom, dateTo, resolution)
    return setJsonRes(json.dumps(history.getHistory()))

def setJsonRes(jsonCont):
    resp = Response(jsonCont)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp

class DefConfig(object):
    def __init__(self):
        self.supports_search = True
        self.supports_group_request = False
        self.supported_resolutions = ['1', '5', '15', '30', '60', '1D']
        self.supports_marks = False
        self.supports_time = True




