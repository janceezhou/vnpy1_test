from vnpy.trader.vtObject import VtBarData, VtTickData

def loadBTCCsv(fileName, dbName, symbol):
    """将BitcoinCharts导出的csv格式的历史tick数据插入到Mongo数据库中"""
    start = time()
    print u'开始读取CSV文件%s中的数据插入到%s的%s中' %(fileName, dbName, symbol)

    # 锁定集合，并创建索引
    client = pymongo.MongoClient(globalSetting['mongoHost'], globalSetting['mongoPort'])
    collection = client[dbName][symbol]
    collection.ensure_index([('datetime', pymongo.ASCENDING)], unique=True)

    # 读取数据和插入到数据库
    reader = csv.reader(open(fileName,"r"))
    for d in reader:
        tick = VtTickData()
        tick.vtSymbol = symbol
        tick.symbol = symbol

        tick.datetime = datetime.strptime(datetime.fromtimestamp(int(d[0])), '%Y-%m-%d %H:%M:%S')
        tick.date = tick.datetime.date().strftime('%Y%m%d')
        tick.time = tick.datetime.time().strftime('%H:%M:%S')

        tick.lastPrice = float(d[1])
        tick.lastVolume = float(d[2])

        flt = {'datetime': tick.datetime}
        collection.update_one(flt, {'$set':tick.__dict__}, upsert=True)
        print('%s \t %s' % (tick.date, tick.time))

    print u'插入完毕，耗时：%s' % (time()-start)   
