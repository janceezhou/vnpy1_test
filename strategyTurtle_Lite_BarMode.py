# encoding: UTF-8
from vnpy.trader.vtObject import VtBarData
from vnpy.trader.vtConstant import EMPTY_STRING
from vnpy.trader.app.ctaStrategy.ctaTemplate import (CtaTemplate, 
                                                     BarGenerator, 
                                                     ArrayManager)
# 与original turtles的区别：
# 此处capital不变。当总资金亏损10%，original turtles的capital减少20%
# 此处ATR和历史最高最低位使用日K线，每天计算一次，判断交易使用tick数据。original turtles的ATR每周更新一次，历史最高最低位包括当天价格
# 此处unit每天计算一次。original turtles的unit每周更新一次
# 此处使用entry system 1
# 所有unit只要有一单被止损了，则不再另外加仓
# 止损价格不根据实际成交价格计算
# 上一次突破信号是否盈利只是估计值，非实际值

########################################################################
class TurtleStrategy(CtaTemplate):
    className = 'TurtleStrategy'
    author = u'用Python的交易员'

    # 策略参数
    
    S_length=5 #10
    #M_length=20 #20
    #L_length= 55 #55
    
    atrLength = S_length*2          # 计算ATR指标的窗口数   
    initDays = 55                   # 初始化数据所用的天数
    maxUnit = 4                     # 最多持有unit数
    risklevel = 0.01                # 风险因子
    contractSize = 1                # 合约大小
    priceLimitPct = ''                  # 涨跌停板限制
    capital = 6
                          

    # 策略变量
    atrValue = 0                        # 最新的ATR指标数值
    historicHigh_m = 0                  # 20天历史最高价的数值
    historicLow_m = 0                   # 20天历史最低价的数值
    historicHigh_s = 0                  # 10天历史最高价的数值
    historicLow_s = 0                   # 10天历史最低价的数值
    historicHigh_l = 0                  # 20天历史最高价的数值
    historicLow_l = 0                   # 20天历史最低价的数值
    lastTradePrice = 0                  # 上一次成交价格的数值
    lastTradeAtrValue = 0               # 上一次成交时的ATR的数值
    unit = 0                            # 头寸的计量单位
    lastBreakOutPrice = 0               # 上一次突破信号的数值
    lastBreakAtrValue = 0               # 上一次突破时的ATR的数值
    lastBreakLongTrade = False          # 是否有虚拟的上一次突破时的多头头寸
    lastBreakShortTrade = False         # 是否有虚拟的上一次突破时的空头头寸
    lastBreakLosing = False             # 虚拟的上一次突破时的交易是否亏损
    neverTrade = True                   # 是否交易过
    maxTradePrice = 999999              # 为了实现市价单效果，将此价格用在long时的限价单上
    minTradePrice = 0                   # 为了实现市价单效果，将此价格用在short时的限价单上    
    
    orderList = []                      # 保存开仓的委托代码的列表
    stopPriceList = []                  # 保存与开仓的委托代码对应的止损价的列表
    
    
    #testIndex = 0

    # 参数列表，保存了参数的名称
    paramList = ['name',
                 'className',
                 'author',
                 'vtSymbol',
                 'atrLength',
                 'S_length',
                 'maxUnit',
                 'risklevel',
                 'contractSize',
                 'priceLimitPct']    

    # 变量列表，保存了变量的名称
    varList = ['inited',
               'trading',
               'pos',
               'atrValue',
               'historicHigh_m',
               'historicLow_m',
               'historicHigh_s',
               'historicLow_s',
               'historicHigh_l',
               'historicLow_l']  
    
    # 同步列表，保存了需要保存到数据库的变量名称
    syncList = ['pos']

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):
        """Constructor"""
        super(TurtleStrategy, self).__init__(ctaEngine, setting)
        
        #self.M_length=2*self.S_length
        #self.L_length=self.M_length*2+5
        
        # 创建K线合成器对象
        self.bg = BarGenerator(self.onBar, 0, None, 0, None, 1, self.onDayBar) 
        self.am = ArrayManager(2*self.S_length)
        self.am_s = ArrayManager(self.S_length)
        self.am_l = ArrayManager(4*self.S_length+15)
        
        self.orderList = []
        
        # 注意策略类中的可变对象属性（通常是list和dict等），在策略初始化时需要重新创建，
        # 否则会出现多个策略实例之间数据共享的情况，有可能导致潜在的策略逻辑错误风险，
        # 策略类中的这些可变对象属性可以选择不写，全都放在__init__下面，写主要是为了阅读
        # 策略时方便（更多是个编程习惯的选择）        

    #----------------------------------------------------------------------
    def onInit(self):
        """初始化策略（必须由用户继承实现）"""
        self.writeCtaLog(u'%s策略初始化' %self.name)

        # 载入历史数据，并采用回放计算的方式初始化策略数值
        initData = self.loadBar(self.initDays)
        for bar in initData:
            bar.open = 1 / float(bar.open)
            bar.high = 1 / float(bar.high)
            bar.low = 1 / float(bar.low)
            bar.close = 1 / float(bar.close)               
            self.onBar(bar)
    
        #initData = self.loadTick(self.initDays)
        #for tick in initData:
            #self.onTick(tick)    

        self.putEvent()

    #----------------------------------------------------------------------
    def onStart(self):
        """启动策略（必须由用户继承实现）"""
        self.writeCtaLog(u'%s策略启动' %self.name)
        self.putEvent()

    #----------------------------------------------------------------------
    def onStop(self):
        """停止策略（必须由用户继承实现）"""
        self.writeCtaLog(u'%s策略停止' %self.name)
        self.putEvent()

    #----------------------------------------------------------------------
    def onTick(self, tick):
        """收到行情TICK推送（必须由用户继承实现）"""
        tick.lastPrice = 1 / float(tick.lastPrice)
        self.bg.updateTick(tick)

    #----------------------------------------------------------------------
    def onBar(self, bar):
        """收到Bar推送（必须由用户继承实现）"""
        self.bg.updateDayBar(bar)
        
        # 撤销之前发出的尚未成交的委托（包括限价单和停止单）
        self.cancelAll()
        
        # 保存K线数据
        am = self.am
        am_s = self.am_s
        am_l = self.am_l
        
        if not am.inited or not am_s.inited or not am_l.inited:
            return
        
        #print 'date: %s|close: %f|20dayHigh: %f|20dayLow: %f' % (bar.date, bar.close, self.historicHigh_m, self.historicLow_m)

        # 当前无仓位，发送开仓委托，或者计算上一次突破时的虚拟交易

        if self.pos == 0:
            if bar.close > self.historicHigh_m:
                if (self.neverTrade or self.lastBreakLosing or (bar.close > self.historicHigh_l)) and self.unit != 0:
                    print "%s|Buy|LastPrice: %f|historicHigh_m: %f|Unit: %d|PriceUpperLimit: %f|PriceLowerLimit: %f" % (bar.date, bar.close, self.historicHigh_m, self.unit, self.maxTradePrice, self.minTradePrice)
                    #self.orderList.extend(self.buy(self.maxTradePrice, int(self.unit * bar.close), False)) 'DZ:20180908
                    self.orderList.extend(self.buy(self.maxTradePrice, int(self.unit * bar.close), False))
                    self.lastTradePrice = bar.close
                    self.lastTradeAtrValue = self.atrValue
                    self.neverTrade = False
    
            elif bar.close < self.historicLow_m:
                if (self.neverTrade or self.lastBreakLosing or (bar.close < self.historicLow_l)) and self.unit != 0:
                    print "%s|Short|LastPrice: %f|historicLow_m: %f|Unit: %d|PriceUpperLimit: %f|PriceLowerLimit: %f" % (bar.date, bar.close, self.historicLow_m, self.unit, self.maxTradePrice, self.minTradePrice)                 
                    #self.orderList.extend(self.short(self.minTradePrice, int(self.unit * bar.close), False))'DZ:20180908
                    self.orderList.extend(self.short(self.minTradePrice, self.unit * bar.close, False))
                    self.lastTradePrice = bar.close
                    self.lastTradeAtrValue = self.atrValue
                    self.neverTrade = False
    
            # 虚拟交易         
            if not (self.lastBreakLongTrade or self.lastBreakShortTrade):
                if bar.close > self.historicHigh_m:
                    self.lastBreakOutPrice = bar.close
                    self.lastBreakAtrValue = self.atrValue
                    self.lastBreakLongTrade = True
                elif bar.close < self.historicLow_m:
                    self.lastBreakOutPrice = bar.close
                    self.lastBreakAtrValue = self.atrValue
                    self.lastBreakShortTrade = True
    
            elif self.lastBreakLongTrade:
                if bar.close < self.lastBreakOutPrice - 2 * self.lastBreakAtrValue:                
                    self.lastBreakLongTrade = False
                    self.lastBreakLosing = True
                elif bar.close > self.historicHigh_s:
                    self.lastBreakLongTrade = False
                    self.lastBreakLosing = False
    
            elif self.lastBreakShortTrade:
                if bar.close > self.lastBreakOutPrice + 2 * self.lastBreakAtrValue:                
                    self.lastBreakShortTrade = False
                    self.lastBreakLosing = True
                elif bar.close < self.historicLow_s:
                    self.lastBreakShortTrade = False
                    self.lastBreakLosing = False
    
        # 持有多头仓位
        elif self.pos > 0:
            
            addUnit = bar.close > (self.lastTradePrice + len(self.orderList) * self.lastTradeAtrValue / 2)
            underMaxUnit = len(self.orderList) < self.maxUnit
            self.longStop = self.lastTradePrice - (2 - (len(self.orderList) - 1) / 2) * self.lastTradeAtrValue
            # add long position
            if addUnit and underMaxUnit and self.unit != 0:
                print "%s|Buy|LastPrice: %f|BreakPrice: %f|Unit: %d|PriceUpperLimit: %f|PriceLowerLimit: %f" % (bar.date, bar.close, self.lastTradePrice + len(self.orderList) * self.lastTradeAtrValue / 2, self.unit, self.maxTradePrice, self.minTradePrice)             
                #self.orderList.extend(self.buy(self.maxTradePrice, int(self.unit * bar.close), False))'DZ:20180908
                self.orderList.extend(self.buy(self.maxTradePrice, self.unit * bar.close, False))
                
            # stop
            elif bar.close < self.longStop:
                print "%s|Sell|LastPrice: %f|StopPrice: %f|Unit: %d|PriceUpperLimit: %f|PriceLowerLimit: %f" % (bar.date, bar.close, self.longStop, self.unit, self.maxTradePrice, self.minTradePrice)                  
                self.sell(self.minTradePrice, abs(self.pos), False)
                self.orderList = []
                self.lastBreakLosing = True

    
            # exit
            elif bar.close < self.historicLow_s:
                print "%s|Sell|LastPrice: %f|historicLow_s: %f|Unit: %d|PriceUpperLimit: %f|PriceLowerLimit: %f" % (bar.date, bar.close, self.historicLow_s, self.unit, self.maxTradePrice, self.minTradePrice)             
                self.sell(self.minTradePrice, abs(self.pos), False)
                self.orderList = []
                # 近似认为此比交易盈利
                self.lastBreakLosing = False
              
    
        # 持有空头仓位
        elif self.pos < 0:
            
            addUnit = bar.close < (self.lastTradePrice - len(self.orderList) * self.lastTradeAtrValue / 2)
            underMaxUnit = len(self.orderList) < self.maxUnit
            self.shortStop = self.lastTradePrice + (2 - (len(self.orderList) - 1) / 2) * self.lastTradeAtrValue
            
            # add short position
            if addUnit and underMaxUnit and self.unit != 0:
                print "%s|Short|LastPrice: %f|BreakPrice: %f|Unit: %d|PriceUpperLimit: %f|PriceLowerLimit: %f" % (bar.date, bar.close, self.lastTradePrice - len(self.orderList) * self.lastTradeAtrValue / 2, self.unit, self.maxTradePrice, self.minTradePrice)              
                #self.orderList.extend(self.short(self.minTradePrice, int(self.unit * bar.close), False))'DZ:20180908
                self.orderList.extend(self.short(self.minTradePrice, self.unit * bar.close, False))
                
            # stop
            elif bar.close > self.shortStop:
                print "%s|Cover|LastPrice: %f|StopPrice: %f|Unit: %d|PriceUpperLimit: %f|PriceLowerLimit: %f" % (bar.date, bar.close, self.shortStop, self.unit, self.maxTradePrice, self.minTradePrice)                  
                self.cover(self.maxTradePrice, abs(self.pos), False)
                self.orderList = []
                self.lastBreakLosing = True
                
    
            # exit
            elif bar.close > self.historicHigh_s:
                print "%s|Cover|LastPrice: %f|historicHigh_s: %f|Unit: %d|PriceUpperLimit: %f|PriceLowerLimit: %f" % (bar.date, bar.close, self.historicHigh_s, self.unit, self.maxTradePrice, self.minTradePrice)                      
                self.cover(self.maxTradePrice, abs(self.pos), False)
                self.orderList = []
                # 近似认为此比交易盈利
                self.lastBreakLosing = False
                
    
        # 同步数据到数据库o
        self.saveSyncData()        
    
        # 发出状态更新事件
        self.putEvent()            
    
    #----------------------------------------------------------------------        
    def onDayBar(self, bar):
        """收到Bar推送（必须由用户继承实现）"""        
        """收到Bar推送（必须由用户继承实现）"""        
        
        # 保存K线数据
        am = self.am
        am_s = self.am_s
        am_l = self.am_l
        
        am.updateBar(bar)
        am_s.updateBar(bar)
        am_l.updateBar(bar)
        
        if not am.inited or not am_s.inited or not am_l.inited:
            return
        
        # 计算指标数值
        #self.atrValue = am_l.atr(self.atrLength)
        self.atrValue = am_l.atr(self.S_length*2)
        self.historicHigh_m = am.high.max()
        self.historicLow_m = am.low.min()
        self.historicHigh_s = am_s.high.max()
        self.historicLow_s = am_s.low.min()
        self.historicHigh_l = am_l.high.max()
        self.historicLow_l = am_l.low.min()
        
        #if bar.date == '20150412':
            #print 'Yes'
            
        # 只有回测模式下ctaBacktesting里才有capital变量
        # self.unit = int(self.ctaEngine.capital * self.risklevel / self.atrValue / self.contractSize)
        self.unit = int(self.capital * self.risklevel / self.atrValue / self.contractSize) 
        
        if self.priceLimitPct:
            self.maxTradePrice = bar.close * (1 + self.priceLimitPct)
            self.minTradePrice = bar.close * (1 - self.priceLimitPct)
        
    #----------------------------------------------------------------------
    def onOrder(self, order):
        """收到委托变化推送（必须由用户继承实现）"""
        pass

    #----------------------------------------------------------------------
    def onTrade(self, trade):
        pass
        
    #----------------------------------------------------------------------
    def onStopOrder(self, so):
        """停止单推送"""
        pass