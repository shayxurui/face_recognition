import init_path
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton,QFileDialog,QLabel,QProgressBar,QFrame,QMainWindow,QStackedWidget 
from PyQt5.QtGui import QPainter,QImage,QFont,QPixmap,QColor,QPalette,QMouseEvent,QBrush
from PyQt5.QtCore import QRect,pyqtSignal,QTimer,QThreadPool,QThread,QRectF,Qt
import cv2
import os.path,os
from camera import CameraManager
#from reactor import Reactor
import faceutil as F
from person import Person
from iomanager import IOManager
from pj_config import model_path,MODELFILE,CONNECTOR,res_path
import strings as S
import time
import logging
from detectstatus import DetectStatusThread
from rec_ui import UI,LabelButton
from history_ui import HistoryUI
logger = logging.getLogger(__name__)


'''
TODO LIST
IO manager
dst

'''



class MainWindow(QMainWindow):
    WIDTH,HEIGHT = 400,700 #窗体大小
    font = ("Roman times",QFont.Bold)
    status = 0 # 0->rec 1->history
    def __init__(self):
        super().__init__()

        self.initUI()
        

    def initUI(self):
        
        self.setFixedSize(self.WIDTH,self.HEIGHT)
        self.setWindowTitle(S.S_WINDOW_TITLE)
        pal = QPalette()
        pal.setColor(QPalette.Background,QColor(57,48,75))
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        status_pos_y,info_pos_y,button_pos_y = 50,100,625
        
        self.initBar() 
        self.sw = QStackedWidget(self)
        self.sw.setGeometry(0,0,self.WIDTH,self.HEIGHT)
        self.rec_ui = UI(self.sw,status_pos_y)
        self.rec_ui.history_signal.connect(self.historyUpdate)
        self.history_ui = HistoryUI(self.sw,status_pos_y)
        self.history_ui.info_update_signal.connect(self.infoUpdate)
        self.sw.addWidget(self.rec_ui)
        self.sw.addWidget(self.history_ui)
        self.initButton(button_pos_y)
        
        #self.initSlot()
        self.show()

    def initBar(self): #需要每分钟更新
        self.bar_timer = QTimer(self)
        self.bar_timer.timeout.connect(self.updateBar)
        self.bar_timer.start(1000)

        self.time_label = QLabel(self)
        self.time_label.setGeometry(170,10,self.WIDTH,self.HEIGHT)

        self.bluetooth_label = LabelButton(self,'bluetooth.png',300,5,20,'rgb(57,48,75)')

        self.charge_bar = None



    def initButton(self,button_pos_y):
        self.button_background = QLabel(self)
        self.button_background.setGeometry(0,button_pos_y,self.WIDTH,self.HEIGHT)
        self.button_background.setStyleSheet('background-color:rgb(151,151,151);')
        
        
        self.start_button = LabelButton(self,'start.png',75,button_pos_y+5)
        self.lookup_button = LabelButton(self,'lookup.png',250,button_pos_y+5)
        self.start_button.clicked.connect(self.runRec)
        self.lookup_button.clicked.connect(self.runHis)
    

    def updateBar(self):
        str_time = time.strftime("%H:%M",time.localtime())
        self.updateLabel(self.time_label,str_time,10)

    def updateLabel(self,label,text,size):
        label.setText(text)
        label.setFont(QFont(*self.fontHelper(size)))
        label.adjustSize()
        pal = QPalette()
        pal.setColor(QPalette.WindowText,QColor(255,255,255))
        label.setPalette(pal)

    def fontHelper(self,size):
        font_name,font_weight = self.font
        return font_name,size,font_weight

    def loadFinish(self,info):
        self.updateLabel(self.label_current_state,info,15)
        self.updateLabel(self.label_current_state,'系统空闲',20)
        self.update()

    
    def infoUpdate(self,history):
        self.status = 0
        self.rec_ui.infoUpdate(history)
        self.sw.setCurrentIndex(0)
    


    def frameHelper(self,file):
        if isinstance(file,str):
            file = cv2.imread(os.path.join('.','resources',file))
        image = cv2.cvtColor(file,cv2.COLOR_BGR2RGB)
        return QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)

    def runRec(self):
        if not self.status:
            self.rec_ui.runRec()
        else:
            self.status = 0
            self.sw.setCurrentIndex(0)
        # TODO timer cancel
        # connect slot and signal
        # history page

    def runHis(self):
        if self.rec_ui.rec_running:
            self.runRec()
        self.status = 1
        self.rec_ui.lookupStart()
        #self.history_ui.history = self.history
        self.sw.setCurrentIndex(1)
    
    def historyUpdate(self,history):
        self.history_ui.setHistory(history)

    '''
    def saveRecord(self,l):
        self.io.start('save',l)
    '''

if __name__ == '__main__':
    
    app = QApplication(sys.argv)

    ui = MainWindow()
    
    sys.exit(app.exec_())