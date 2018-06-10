# encoding: UTF-8

"""
导入BitcoinCharts导出的CSV历史数据到MongoDB中
"""

from vnpy.trader.app.ctaStrategy.ctaBase import TICK_DB_NAME
from vnpy.trader.app.ctaStrategy.ctaHistoryData import loadBTCCsv


if __name__ == '__main__':
    loadBTCCsv('bitstampUSD.csv', TICK_DB_NAME, 'bitstampUSD')