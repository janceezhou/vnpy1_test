# encoding: UTF-8

from datetime import datetime

from vnpy.event import Event
from vnpy.trader.vtEvent import EVENT_TICK
from vnpy.trader.vtObject import VtSubscribeReq

EVENT_DEMO_LOG = 'eDemoLog'
EVENT_DEMO_TICK = 'eDemoTick'

def DemoEngine(object):
    
    def __init__(self, mainEngine, eventEngine):
        self.mainEngine = mainEngine
        self.eventEngine = eventEngine
        
        self.symbol = 'rb1806'
        self.priceDict = {}
        
        self.registerEvent()
        
    def subscribeData(self):
        req = VtSubscribeReq()
        req.symbol = self.symbol
        self.mainEngine.subscribeData(req, 'CTP')       
        
    def registerEvent(self):
        self.eventEngine.register(EVENT_TICK, self.processTickEvent)
        
    def processTickEvent(self, event):
        tick = event.dict_['data']
        last = tick.lastPrice
        
        result = ''
        
        if self.priceDict:
            if last >= self.priceDict['ask']:
                result = u'外盘'
            elif last <= self.priceDict['bid']:
                result = u'内盘'
            else:
                result = u'中性'
                
            self.writeLog(u'%s最新Tick的成交价为%s (%s, %s)，交易方向： %s', %(tick,
                                                                          last,
                                                                          self.priceDict['bid'],
                                                                          self.priceDict['ask'],
                                                                          result))
        
        d = {
            'symbol': self.symbol,
            'time': str(datetime.now()),
            'last': last,
            'bid': self.priceDict['bid'],
            'ask': self.priceDict['ask'],
            'result': result
        }
        event = Event(EVENT_DEMO_TICK)
        event.dict_['data']= d
        self.eventEngine.put(event)
        
        self.priceDict['bid'] = tick.bidPrice1
        self.priceDict['ask'] = tick.askPrice1
        
    def writeLog(self, msg):
        event = Event(EVENT_DEMO_LOG)
        event.dict_['data'] = msg
        self.eventEngine.put(event)
