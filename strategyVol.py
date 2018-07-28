# encoding: UTF-8

from __future__ import division

from vnpy.trader.vtConstant import EMPTY_STRING, EMPTY_FLOAT
from vnpy.trader.app.ctaStrategy.ctaTemplate import (CtaTemplate, 
                                                     BarGenerator,
                                                     ArrayManager)


########################################################################
class VolStrategy(CtaTemplate):
    """双指数均线策略Demo"""
    className = 'VolStrategy'
    author = u'Daomin'
    
    # 策略参数
    fastWindow = 5     # 快速波动率参数
    slowWindow = 20     # 慢速波动率参数
    initDays = 30       # 初始化数据所用的天数
    maxTradePrice = 999999              # 为了实现市价单效果，将此价格用在long时的限价单上
    minTradePrice = 0                   # 为了实现市价单效果，将此价格用在short时的限价单上
    maxPos = 2
    trailingPrcnt = -0.3
    stopLossDays = 20
    
    # 策略变量
    fastPositiveVol = EMPTY_FLOAT   
    fastNegativeVol = EMPTY_FLOAT   
    
    slowPositiveVol = EMPTY_FLOAT
    slowNegativeVol = EMPTY_FLOAT
    
    pnlList = [0 for i in range(stopLossDays)]
    drawDown = EMPTY_FLOAT
    
    
    # 参数列表，保存了参数的名称
    paramList = ['name',
                 'className',
                 'author',
                 'vtSymbol',
                 'fastWindow',
                 'slowWindow']    
    
    # 变量列表，保存了变量的名称
    varList = ['inited',
               'trading',
               'pos',
               'fastPositiveVol',
               'fastNegativeVol',
               'slowPositiveVol',
               'slowNegativeVol',
               'maxDD']  
    
    # 同步列表，保存了需要保存到数据库的变量名称
    syncList = ['pos']

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):
        """Constructor"""
        super(VolStrategy, self).__init__(ctaEngine, setting)
        
        #self.bm = BarGenerator(self.onBar)
        self.bm = BarGenerator(self.onBar, 0, None, 0, None, 1, self.onDayBar)
        self.am = ArrayManager(self.initDays)
        
        self.pnlList = [0 for i in range(self.stopLossDays)]

        # 注意策略类中的可变对象属性（通常是list和dict等），在策略初始化时需要重新创建，
        # 否则会出现多个策略实例之间数据共享的情况，有可能导致潜在的策略逻辑错误风险，
        # 策略类中的这些可变对象属性可以选择不写，全都放在__init__下面，写主要是为了阅读
        # 策略时方便（更多是个编程习惯的选择）
        
    #----------------------------------------------------------------------
    def onInit(self):
        """初始化策略（必须由用户继承实现）"""
        self.writeCtaLog(u'双EMA演示策略初始化')
        
        #initData = self.loadBar(self.initDays)
        #for bar in initData:
            #self.onBar(bar)
        
        initData = self.loadTick(self.initDays)
        for tick in initData:
            self.onTick(tick)            
        
        self.putEvent()
        
    #----------------------------------------------------------------------
    def onStart(self):
        """启动策略（必须由用户继承实现）"""
        self.writeCtaLog(u'双EMA演示策略启动')
        self.putEvent()
    
    #----------------------------------------------------------------------
    def onStop(self):
        """停止策略（必须由用户继承实现）"""
        self.writeCtaLog(u'双EMA演示策略停止')
        self.putEvent()
        
    #----------------------------------------------------------------------
    def onTick(self, tick):
        """收到行情TICK推送（必须由用户继承实现）"""
        self.bm.updateTick(tick)
        
    #----------------------------------------------------------------------    
    def onBar(self, bar):
        """收到Bar推送（必须由用户继承实现）"""
        self.bm.updateDayBar(bar)        
    #----------------------------------------------------------------------
    def onDayBar(self, bar):
        """收到Bar推送（必须由用户继承实现）"""
        am = self.am        
        am.updateBar(bar)
        if not am.inited:
            return
        # 计算前一天的pnl并存入pnlList
        self.pnlList[0:self.stopLossDays-1] = self.pnlList[1:self.stopLossDays]
        self.pnlList[-1] = self.pnlList[-2] + self.pos * (am.close[-1] - am.close[-2])
        
        # 计算drawdown
        self.drawDown = self.pnlList[-1] - max(self.pnlList)

        if max(self.pnlList) == 0 or self.drawDown / max(bar.close*2, max(self.pnlList)) > self.trailingPrcnt:
            
            # 计算快慢
            self.fastPositiveVol = am.simpleVolatility(self.fastWindow, onlyPositive=True, onlyNegative=False, array=True)
            self.fastNegativeVol = am.simpleVolatility(self.fastWindow, onlyPositive=False, onlyNegative=True, array=True)
            
            self.slowPositiveVol = am.simpleVolatility(self.slowWindow, onlyPositive=True, onlyNegative=False, array=True)
            self.slowNegativeVol = am.simpleVolatility(self.slowWindow, onlyPositive=False, onlyNegative=True, array=True)  
            
            # 判断买卖
            fastCross = self.fastPositiveVol > self.fastNegativeVol # 短期上行波动率大于下行波动率
            slowCross = self.slowPositiveVol > self.slowNegativeVol # 长期上行波动率大于下行波动率
            
            fastSignal = 0.5 if fastCross else -0.5
            slowSignal = 0.5 if slowCross else -0.5
            signal = fastSignal + slowSignal
            
        else:
            signal =0
        
        print "%s|%f|%f|%f|%f|%f|%f|%d" % (bar.date, bar.close, self.slowPositiveVol, self.slowNegativeVol, self.fastPositiveVol, self.fastNegativeVol, signal, self.pnlList[-1])
        
        if signal > 0:
            # 如果手头没有持仓，则直接做多
            if self.pos == 0:
                self.buy(self.maxTradePrice, self.maxPos, False)
            # 如果有空头持仓，则先平空，再做多
            elif self.pos < 0:
                self.cover(self.maxTradePrice, self.maxPos, False)
                self.buy(self.maxTradePrice, self.maxPos, False)

        elif signal < 0:
            if self.pos == 0:
                self.short(self.minTradePrice, self.maxPos, False)
            elif self.pos > 0:
                self.sell(self.minTradePrice, self.maxPos, False)
                self.short(self.minTradePrice, self.maxPos, False)
                
        elif signal == 0:
            if self.pos > 0:
                self.sell(self.minTradePrice, self.maxPos, False)
            elif self.pos < 0:
                self.cover(self.maxTradePrice, self.maxPos, False)
                
        # 发出状态更新事件
        self.putEvent()
        
    #----------------------------------------------------------------------
    def onOrder(self, order):
        """收到委托变化推送（必须由用户继承实现）"""
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        pass
    
    #----------------------------------------------------------------------
    def onTrade(self, trade):
        """收到成交推送（必须由用户继承实现）"""
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        pass
    
    #----------------------------------------------------------------------
    def onStopOrder(self, so):
        """停止单推送"""
        pass    