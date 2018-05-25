%matplotlib inline

from vnpy.trader.app.ctaStrategy.ctaBacktesting import BacktestingEngine, OptimizationSetting, TICK_DB_NAME
from vnpy.trader.app.ctaStrategy.strategy.strategyAtrRsi import AtrRsiStrategy

engine = BacktestingEngine()

engine.setBacktestingMode(engine.TICK_MODE)
engine.setDatabase(TICK_DB_NAME, 'bitstampUSD')
engine.setStartDate('20130101')

engine.setSlippage(0.1)     # 设置滑点为股指1跳
engine.setRate(1/1000)      # 设置手续费千1
engine.setSize(1)           # 设置合约大小 
engine.setPriceTick(0.01)   # 设置最小价格变动   
engine.setCapital(1)        # 设置回测本金

d = {'atrLength': 11}                     # 策略参数配置
engine.initStrategy(AtrRsiStrategy, d)    # 创建策略对象

engine.runBacktesting()          # 运行回测

engine.showDailyResult()

engine.showBacktestingResult()
