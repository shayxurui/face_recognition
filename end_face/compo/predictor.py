#-*- coding: utf-8 -*-
import numpy as np
import cv2
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.autograd import Variable
torch.backends.cudnn.bencmark = True
from matlab_cp2tform import get_similarity_transform_for_cv2
import net_sphere
import time
import logging
import math
from pj_config import BLUR_THRESHOLD,REF_THRESHOLD
logger = logging.getLogger(__name__)
class Predictor():
    """
    在程序开始实例化，确保网络在程序一开始就载入内存。
    """
    def __init__(self,MODEL_FILE):
        self.net = self._loadNet(MODEL_FILE)
        self.current_face = None

    def _alignment(self,src_img,src_pts):
        ref_pts = [ [30.2946, 51.6963],[65.5318, 51.5014],
            [48.0252, 71.7366],[33.5493, 92.3655],[62.7299, 92.2041] ]
        crop_size = (128, 128)

        s = np.array(src_pts).reshape(5,2).astype(np.float32)
        r = np.array(ref_pts).astype(np.float32)

        tfm = get_similarity_transform_for_cv2(s, r)
        face_img = cv2.warpAffine(src_img, tfm, crop_size)
        return face_img

    def _preprocess(self,img):
        # height = 112
        # width = 96
        # color_img = cv2.imread(img_path)
        # resized_img = cv2.resize(color_img, (width,height))
        # #flip_img = cv2.flip(resized_img, 1)
        # resized_img = (resized_img - 127.5)/128
        # #flip_img = (flip_img - 127.5)/128
        # #return np.transpose(resized_img, (2, 0, 1)), np.transpose(flip_img, (2, 0, 1))
        # return np.transpose(resized_img,(2,0,1))
        return (img.transpose(2,0,1).reshape((1,3,128,128))-127.5)/128

    def _extract_reg(self,image,landmark,online=True):
        '''
        @para online: 
            True: numpy array
            False: pic file

        Return pytorch.Tensor
        '''
        imglist=[]
        landmarks = np.split(landmark,landmark.shape[0],axis=0)
        for _ in landmarks:
            face = self._alignment(image,_)
            imglist.append(self._preprocess(face))

        img = np.vstack(imglist)

        img = Variable(torch.from_numpy(img).float(),volatile=True).cuda()
        output = self.net(img)
        f = output.data
        return f
    def _extract(self,image,landmark,online=True):
        '''
        @para online: 
            True: numpy array
            False: pic file

        Return pytorch.Tensor
        '''
        list2ret=[]
        imglist = []
        landmarks = np.split(landmark,landmark.shape[0],axis=0)
        for _ in landmarks:
            face = self._alignment(image,_)
            #blur = cv2.Laplacian(cv2.cvtColor(face, cv2.COLOR_BGR2GRAY),cv2.CV_64F).var()
            #if  blur > BLUR_THRESHOLD:
            list2ret.append(face)
            imglist.append(self._preprocess(face))
            #imglist.append(self._preprocess(cv2.flip(face,1)))
        
        # for i in range(len(imglist)):
        #     imglist[i] = imglist[i].transpose(2, 0, 1).reshape((1,3,112,96))
        #     imglist[i] = (imglist[i]-127.5)/128.0
        # face = self._alignment(image,landmark)
        # self.current_face = face
        # imglist = [face,cv2.flip(face,1)]
        # for i in range(len(imglist)):
        #     imglist[i] = imglist[i].transpose(2, 0, 1).reshape((1,3,112,96))
        #     imglist[i] = (imglist[i]-127.5)/128.0
        
        img = np.vstack(imglist)

        img = Variable(torch.from_numpy(img).float(),volatile=True).cuda()
        output = self.net(img)
        f = output.data
        return list2ret,f
    def _loadNet(self,MODEL_FILE):
        #net = getattr(net_sphere,'sphere20a')()
        #net.load_state_dict(torch.load(MODEL_FILE))
        net=torch.load(MODEL_FILE).module
        net.cuda()
        net.eval()
        #net.feature = True
        return net
    def predictface(self,records,image,landmark,bboxs):
        toc = time.time()
        imglist,features = self._extract(image,landmark)
        logger.debug("提取特征完成，耗时{:.3f}".format(time.time()-toc))
        toc = time.time()
        # tmp = [i[1].view(1,-1) for i in records]
        # ref = torch.cat(tmp,0).cuda()

        print(type(records[1]))
        print(records[1].size())

        ref = records[1].cuda()
        print(type(ref))

        norms = ref.norm(2,1).view(-1,1)  #(30000,1)
        #result = ref.matmul(features.t())/(norms*features.norm()+1e-5)
        features_norms = features.norm(2,1).view(1,-1)  #(1,N) 
        result = ref.matmul(features.t())/(norms+1e-5)/(features_norms+1e-5)
        max_tup = result.max(0)
        
        ret=[]
        for i,m in enumerate(max_tup[0]):
            if m>REF_THRESHOLD:
                ret.append([bboxs[i],imglist[i],records[0][max_tup[1][i]],math.sqrt(m)])
        logger.debug("特征比对完成，耗时{:.3f}".format(time.time()-toc))

        '''
        if(m<0.65):
            return None
        '''
        return ret
