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
    fastWindow = 5     # 快速均线参数
    slowWindow = 20     # 慢速均线参数
    initDays = 40       # 初始化数据所用的天数
    
    # 策略变量
    fastPositiveVol = EMPTY_FLOAT   # 当前最新的快速EMA
    fastNegativeVol = EMPTY_FLOAT   # 上一根的快速EMA
    
    slowPositiveVol = EMPTY_FLOAT
    slowNegativeVol = EMPTY_FLOAT
    
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
               'slowNegativeVol']  
    
    # 同步列表，保存了需要保存到数据库的变量名称
    syncList = ['pos']

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):
        """Constructor"""
        super(VolStrategy, self).__init__(ctaEngine, setting)
        
        #self.bm = BarGenerator(self.onBar)
        self.bm = BarGenerator(self.onBar, 0, None, 0, None, 1, onDayBar)
        self.am = ArrayManager()
        
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
        
        # 计算快慢均线
        fastMa = am.sma(self.fastWindow, array=True)
        self.fastMa0 = fastMa[-1]
        self.fastMa1 = fastMa[-2]
        
        slowMa = am.sma(self.slowWindow, array=True)
        self.slowMa0 = slowMa[-1]
        self.slowMa1 = slowMa[-2]

        # 判断买卖
        crossOver = self.fastMa0>self.slowMa0 and self.fastMa1<self.slowMa1     # 金叉上穿
        crossBelow = self.fastMa0<self.slowMa0 and self.fastMa1>self.slowMa1    # 死叉下穿
        
        # 金叉和死叉的条件是互斥
        # 所有的委托均以K线收盘价委托（这里有一个实盘中无法成交的风险，考虑添加对模拟市价单类型的支持）
        if crossOver:
            # 如果金叉时手头没有持仓，则直接做多
            if self.pos == 0:
                self.buy(bar.close, 1)
            # 如果有空头持仓，则先平空，再做多
            elif self.pos < 0:
                self.cover(bar.close, 1)
                self.buy(bar.close, 1)
        # 死叉和金叉相反
        elif crossBelow:
            if self.pos == 0:
                #self.short(bar.close, 1)
                pass
            elif self.pos > 0:
                self.sell(bar.close, 1)
                #self.short(bar.close, 1)
                
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
