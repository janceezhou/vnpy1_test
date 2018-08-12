# encoding: UTF-8

"""
展示如何执行策略回测。
"""


from __future__ import division


from vnpy.trader.app.ctaStrategy.ctaBacktesting import BacktestingEngine, MINUTE_DB_NAME


if __name__ == '__main__':
    from vnpy.trader.app.ctaStrategy.strategy.strategyTurtle import TurtleStrategy
    from vnpy.trader.app.ctaStrategy.strategy.strategyAtrRsi import AtrRsiStrategy
    from vnpy.trader.app.ctaStrategy.strategy.strategyVol import VolStrategy
    
    
    
    # 创建回测引擎
    engine = BacktestingEngine()
    
    # 设置引擎的回测模式为K线
    engine.setBacktestingMode(engine.BAR_MODE)

    # 设置回测用的数据起始日期
    engine.setStartDate('20180207')
    engine.setEndDate('20180807')
    
    # 设置产品相关参数
    engine.setSlippage(0)     # 股指1跳
    engine.setRate(1/5000.0)   # 螺纹钢万一
    engine.setSize(5)         # 股指合约大小 
    engine.setPriceTick(5)    # 股指最小价格变动
    engine.setCapital(100000)    # 股指最小价格变动
    engine.setDataSource(engine.CSV_MODE)
    engine.setCsvDataPath(r'd:\RB1810.csv')
    engine.setCsvDateFormat(r'%Y-%m-%d %H:%M:%S')
    
    # 设置使用的历史数据库
    #engine.setDatabase(MINUTE_DB_NAME, 'IF0000')
    #engine.downloadJQData('RB9999.XSGE', r'd:\RB9999.csv', endDate='2018-08-10')
    #engine.downloadJQData('RB1810.XSGE', r'd:\RB1810.csv', endDate='2018-08-10')
    #XDCE Dalian
    #XSGE Shanghai
    
    # 在引擎中创建策略对象
    d = {}
    engine.initStrategy(TurtleStrategy, d)
    
    # 开始跑回测
    engine.runBacktesting()

    # 显示回测结果
    engine.showBacktestingResult()
    
    engine.showDailyResult()