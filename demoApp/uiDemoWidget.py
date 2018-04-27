# encoding: UTF-8

from datetime import datetime

from .demoEngine import EVENT_DEMO_LOG

from vnpy.event import Event
from vnpy.trader.uiQt import QtCore, QtWidgets

class DemoWidget(QTWidget.Qwidget):
    
    signalLog = QtCore.Signal(type(Event()))
    
    def __init__(self, demoEngine, eventEngine, parent=NONE):
        super(DemoWidget, self).__init__(NONE)
        
        self.demoEngine = demoEngine
        self.eventEngine = eventEngine
       
        self.initUi()
        self.registerEvent()
       
       
    def initUi(self):
        self.setWindowTitle('DemoApp')
        
        self.button = QtWidget.QPushButton(u'订阅行情')
        self.button.clicked.connect(self.demoEngine.subscribeData)
        
        self.logMonitor = QtZidgets.QTextEdit()
        self.logMonitor.setReadOnly(True)
        
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.button)
        hbox.addStretch()
        
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.logMonitor)
        
        self.setLayout(vbox)
    
    def registerEvent(self):
        self.signalLog.connect(self.processLogEvent)
        self.eventEngine.register(EVENT_DEMO_LOG, self.signalLog.emit())
        
    
    def processLogEvent(self, event):
        msg = event.dict_['data']
        t = datetime.now()
        
        msg = str(t) + '   ' + msg
        self.logMonitor.append(msg)
        