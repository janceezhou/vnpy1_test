# encoding: UTF-8

"""
展示如何执行参数优化。
"""

from __future__ import division
from __future__ import print_function


from vnpy.trader.app.ctaStrategy.ctaBacktesting import BacktestingEngine, MINUTE_DB_NAME, OptimizationSetting


if __name__ == '__main__':
    from vnpy.trader.app.ctaStrategy.strategy.strategyTurtle import TurtleStrategy
    
    # 创建回测引擎
    engine = BacktestingEngine()
    
    # 设置引擎的回测模式为K线
    engine.setBacktestingMode(engine.BAR_MODE)

    # 设置回测用的数据起始日期
    engine.setStartDate('20171107')
    engine.setEndDate('20180807')
    
    # 设置产品相关参数
    engine.setSlippage(0)     # 股指1跳
    engine.setRate(1/5000.0)   # 螺纹钢万一
    engine.setSize(5)         # 股指合约大小 
    engine.setPriceTick(5)    # 股指最小价格变动
    engine.setCapital(100000)    # 股指最小价格变动
    engine.setDataSource(engine.CSV_MODE)
    engine.setCsvDataPath(r'd:\RB9999.csv')
    engine.setCsvDateFormat(r'%Y-%m-%d %H:%M:%S')
    
    # 设置使用的历史数据库
    #engine.setDatabase(MINUTE_DB_NAME, 'IF0000')
    
    # 跑优化
    setting = OptimizationSetting()                 # 新建一个优化任务设置对象
    setting.setOptimizeTarget('totalNetPnl')            # 设置优化排序的目标是策略净盈利
    setting.addParameter('S_length', 5, 15, 1)    # 增加第一个优化参数atrLength，起始12，结束20，步进2
    setting.addParameter('maxUnit', 3, 5, 1)        # 增加第二个优化参数atrMa，起始20，结束30，步进5
    #setting.addParameter('rsiLength', 5)            # 增加一个固定数值的参数
    
    # 性能测试环境：I7-3770，主频3.4G, 8核心，内存16G，Windows 7 专业版
    # 测试时还跑着一堆其他的程序，性能仅供参考
    import time    
    start = time.time()
    
    # 运行单进程优化函数，自动输出结果，耗时：359秒
    #engine.runOptimization(AtrRsiStrategy, setting)            
    
    # 多进程优化，耗时：89秒
    engine.runParallelOptimization(TurtleStrategy, setting)
    
    print(u'耗时：%s' %(time.time()-start))