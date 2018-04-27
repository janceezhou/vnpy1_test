# encoding: UTF-8

from datetime import datetime

from .demoEngine import EVENT_DEMO_LOG, EVENT_DEMO_TICK

from vnpy.event import Event
from vnpy.trader.uiQt import QtCore, QtWidgets

class DemoWidget(QTWidget.Qwidget):
    
    signalLog = QtCore.Signal(type(Event()))
    signalTick = QtCore.Signal(type(Event()))
    
    def __init__(self, demoEngine, eventEngine, parent=NONE):
        super(DemoWidget, self).__init__(NONE)
        
        self.demoEngine = demoEngine
        self.eventEngine = eventEngine
        
        self.cellDict = {}
       
        self.initUi()
        self.registerEvent()
       
       
    def initUi(self):
        self.setWindowTitle('DemoApp')
        
        self.button = QtWidget.QPushButton(u'订阅行情')
        self.button.clicked.connect(self.demoEngine.subscribeData)
        
        self.logMonitor = QtWidgets.QTextEdit()
        self.logMonitor.setReadOnly(True)
        
        self.tickTable = QtWidgets.QTableWidget()
        self.tickTable.setRowCount(1)
        self.tickTable.setColumnCount(6)
        self.tickTable.setHorizontalHeaderLabels(['symbol', 'time', 'last',
                                                  'bid', 'ask', 'result'])
        cellSymbol = QtWidgets.QTableWidgetItem()
        cellTime = QtWidgets.QTableWidgetItem()
        cellLast = QtWidgets.QTableWidgetItem()
        cellBid = QtWidgets.QTableWidgetItem()
        cellAsk = QtWidgets.QTableWidgetItem()
        cellResult = QtWidgets.QTableWidgetItem()
        
        self.tickTable.setItem(0, 0, cellSymbol)
        self.tickTable.setItem(0, 1, cellTime)
        self.tickTable.setItem(0, 2, cellLast)
        self.tickTable.setItem(0, 3, cellBid)
        self.tickTable.setItem(0, 4, cellAsk)
        self.tickTable.setItem(0, 5, cellResult)
        
        self.cellDict['symbol']= cellSymbol
        self.cellDict['time']= cellTime
        self.cellDict['last']= cellLast
        self.cellDict['bid']= cellBid
        self.cellDict['ask']= cellAsk
        self.cellDict['result']= cellResult
        
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.button)
        hbox.addStretch()
        
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.logMonitor)
        
        self.setLayout(vbox)
    
    def registerEvent(self):
        self.signalLog.connect(self.processLogEvent)
        self.signalTick.connect(self.processTickEvent)
        self.eventEngine.register(EVENT_DEMO_LOG, self.signalLog.emit)
        self.eventEngine.register(EVENT_DEMO_TICK, self.signalTick.emit)
        
    
    def processLogEvent(self, event):
        msg = event.dict_['data']
        t = datetime.now()
        
        msg = str(t) + '   ' + msg
        self.logMonitor.append(msg)
        
        
    def processTickEvent(self, event):
        d = event.dict_['data']
        
        for key, value in d.items():
            self.cellDict[key].setText(str(value)
