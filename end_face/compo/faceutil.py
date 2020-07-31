#-*- coding: utf-8 -*-
import csv,os,os.path
import logging
import numpy as np
import time
logger = logging.getLogger(__name__)
def registerFaces(dm,predictor,detector,filename):#import csv,
    """
    批量读入图片和对应的信息
    @author xcr
    @param dm DataManager类型
    @param predictor FaceManager类型
    @param detector DetectManager类型
    @param filename csv文件路径，csv文件的格式是pid,pname,sex,height,weight,origin,ptype,note,path
    @return void
    """
    #TODO：写一个自动生成csv文件的系统
    dirName = os.path.dirname(filename)
    fail_list=[]
    warning_list = []
    with open(filename,'r',encoding='utf-8') as csvFile:
        reader = csv.reader(csvFile)
        #header
        fieldname = next(reader)
        features_t = []
        information_t = []
        idx=0
        for row in reader:
            if not row:
                continue
            imagename = row.pop()
            try:
                image,landmark = detector.detect(os.path.join(dirName,imagename),online=False)
            except:
                logger.error("可能打开图片失败，图片下标为%d"%(idx),exc_info=True)
                fail_list.append(imagename)
                continue
            if landmark.shape[0]>1:
                landmark = np.split(landmark,[1],axis=0)[0]
                warning_list.append(imagename)
            if landmark.shape[0] == 1:
                idx+=1
                print(idx)
                try:
                    features = predictor._extract_reg(image,landmark,online=True)
                    #print(features.shape)
                    # pickle
                    features = features.cpu().numpy().tolist()[0]
                    # mysql
                    # features = str(features.cpu().numpy().tolist()[0])
                except:
                    logger.error("注册时提取特征出错，出错照片编号为%d"%(idx),exc_info=True)
                else:
                    features_t.append((row[0],features))
                    information_t.append(row)
            else:
                fail_list.append(imagename)
        logger.info("提取特征过程已经完成，准备将%d条数据写入数据库"%len(features_t))
        logger.info("提取特征识别失败的图片有%s"%str(fail_list))
        if not features_t:
            logger.warning("没有成功提取的特征，无需写数据库。")
            return
        fieldname.pop()
        info_fieldname = tuple(fieldname)
        fea_fieldname = (fieldname[0],'feature',)
        dm.writeRecords('information_t',info_fieldname,information_t)
        dm.writeRecords('features_t',fea_fieldname,features_t)
def recognizeFace(predictor,detector,records,image):
    """
    通过pycaffe api使用训练好的人脸识别模型实现识别功能，返回结果。
    @param predictor FaceManager类型
    @param dm DetectManager类型
    @param records features表的数据，通过datautil方法获得
    @param image row image in numpy array
    @return 返回识别的id列表(包括id,相似度,bbox)
    """
    infos = []
    toc=time.time()
    landmark,bboxs = detector.detect(image,online=True)
    # logger.debug("检测完成，landmark为%s"%str(landmark))
    logger.info('检测完成，{}'.format(time.time()-toc))
    if  landmark.shape[0]==0:
        return infos
    try:
        infos = predictor.predictface(records,image,landmark,bboxs)
    except:
        logger.error("识别人脸错误",exc_info=True)
    return infos