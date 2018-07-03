主要改动：
1. 所有策略都接收tick数据
2. ctaTemplate合成小时k线和日k线，
3. ctaBacktesting直接从csv读取数据。限价撮合不使用tick的bid和ask数据，而是用lastPrice
