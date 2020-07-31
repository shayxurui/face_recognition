from src import detector as d
from src.model import PNet, RNet, ONet
from PIL import Image
import cv2
class Detector(object):
    def __init__(self,given):
        self.pnet, self.rnet,self.onet = PNet(),RNet(),ONet()

    def detect(self, image, online=True):
        if not online:
            image = cv2.imread(image)
        image = Image.fromarray(cv2.cvtColor(image,cv2.COLOR_BGR2RGB))
        bboxs, landmarks = d.detect_faces(image,self.pnet,self.rnet,self.onet)

        return landmarks, bboxs
