from PyQt5.QtCore import QThread,pyqtSignal,pyqtSlot
from subprocess import Popen,PIPE
class DetectStatusThread(QThread):
    """docstring for DetectStatusThread"""
    upload_signal = pyqtSignal(dict)
    def __init__(self, slot):
        super(DetectStatusThread, self).__init__()
        self.upload_signal.connect(slot)

    def run(self):
        # detect status and emit upload signal
        # while True:
        #     ret = dict()
        #     # TODO 
        #     self.upload_signal.emit(ret)
        pass