#-*- coding: utf-8 -*-
import cv2
from pj_config import camera_device_id
class CameraManager():
    def __init__(self):
        super().__init__()
        self.cam = cv2.VideoCapture(camera_device_id)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
    def getframe(self):
        ret,frame = self.cam.read()
        if ret:
            return frame