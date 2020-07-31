from compo.dface.detect import create_mtcnn_net, MtcnnDetector
import cv2
class Detector(object):
    """docstring for DetectManager"""
    def __init__(self,model_path):
        super(Detector, self).__init__()
        Ppath = model_path +"/pnet_epoch.pt"
        Rpath = model_path +"/rnet_epoch.pt"
        Opath = model_path +"/onet_epoch.pt"
        pnet,rnet,onet = create_mtcnn_net(Ppath,Rpath,Opath)
        self.mtcnn_detector = MtcnnDetector(pnet=pnet, rnet=rnet, onet=onet, min_face_size=32)
    def detect(self,raw_image,online=True):
        if not online:
            raw_image = cv2.imread(raw_image)
        bboxs, landmark = self.mtcnn_detector.detect_face(raw_image)
        '''
        lanmark.shape = (1,10) if face exists
        else (0,)
        bboxs.shape = (1,5) if bboxs exists
        '''
        return landmark,bboxs