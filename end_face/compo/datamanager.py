#-*- coding: utf-8 -*-
import pymysql
import traceback
import logging
from torch import Tensor
import time
logger = logging.getLogger(__name__)
class DataManager():
    def __init__(self,connector):
        """
        @param connector 需要连接数据库的名称、登录名、密码，字典
        """
        self.connector = connector

    def connectDB(self):#import pymysql
        """
        连接数据库
        @author xcr
        @return connection对象，以在后面操作获得游标
        """
        try:
            self.connection = pymysql.connect(**self.connector)
            self.connection.autocommit(True)
            # c = self.connection.cursor()
            # c.close()
            self.connection.select_db(self.connector['db'])
        except:
            logger.error("connect database failed!\nconnecting information is {}".format(tuple(self.connector.keys())),exc_info=True)
        else:
            logger.info("连接数据库%s成功"%(self.connector['db']))
    def writeRecord(self,table,fieldname,record):   
        """
        把数据库写入数据库对应的表格
        @author xcr
        @param table 表名，字符串类型
        @param record 需要写入的记录，元组类型
        @param fieldname字段名，元组类型
        @return bool是否成功写入
        """
        diffnum=0
        try:
            cursor = self.connection.cursor()#可以改变cursor类型
            #TODO
            #cursor.execute('create table {table} if not exits'.format(table=table))
            tmplate = ("insert into {table} ("+','.join((r'%s',)*len(fieldname))%fieldname+") values(").format(table = table)+','.join(('%s',)*len(record))+')'
            diffnum = cursor.execute(tmplate,record)
        except:
            logger.error("write record in table {} failed!".format(table),exc_info=True)
            self.connection.rollback()
        else:
            logger.debug("写数据库%s成功，写入行数%d"%(self.connector['db'],diffnum))
        finally:
            cursor.close()
        return diffnum == 1
    def writeRecords(self,table,fieldname,records):
        """
        把数据库批量写入数据库对应的表格
        @author xcr
        @param table表名，字符串类型
        @param fieldname字段名，元组类型
        @param records记录列表，字典类型
        @return  成功写入行数
        """
        #records = [tuple(x) for x in records]
        diffnum = 0
        try:
            cursor = self.connection.cursor()#可以改变cursor类型
            #TODO 
            #cursor.execute('create table {table} if not exits'.format(table=table))
            tmplate = ("insert into {table}("+','.join((r'%s',)*len(fieldname))%fieldname+") values(").format(table = table)+','.join(('%s',)*len(records[0]))+')'
            diffnum = cursor.executemany(tmplate,records)
        except:
            logger.error("write records in table {} failed!".format(table),exc_info=True)
            self.connection.rollback()
        else:
            logger.info("写数据库%s成功，写入行数%d"%(self.connector['db'],diffnum))
        finally:
            cursor.close()
        return diffnum
    def readRecordsToMem(self,table,fieldname):
        """
        把数据库的某个表所有所有一次读入内存
        @param fieldname字段名，元组类型
        @return 所有的记录，类型是列表
        """
        try:
            cursor = self.connection.cursor()
            count = cursor.execute(('select ' + ','.join((r'{}',)*len(fieldname)) + ' from {}').format(*fieldname,table))
            ret = cursor.fetchall()
            cursor.close()
        except BrokenPipeError as bpe:
            traceback.print_exc();
            logger.error("尝试重新连接数据库",exc_info=True)
            self.connectDB()
        except Exception as e:
            ret = None
            traceback.print_exc()
            logger.error('read table {} failed, trying to read fieldname {}.'.format(table,fieldname),exc_info=True)
            self.connection.rollback()
            return
        else:
            logger.info("read table {} successfully, totally {} rows are read!".format(table,str(count)))
        if 'feature' in fieldname or (table=='features_t' and '*' in fieldname):
            toc = time.time()
            logger.info("开始加载特征值，将str特征值转化为Tensor")
            idx = fieldname.index('feature') if 'feature' in fieldname else 2
            idx2 = fieldname.index('pid') if 'pid' in fieldname else 1
            id_list=[]
            f_list=[]
            total = len(ret)
            for i,record in enumerate(ret):
                f_list.append(eval(record[idx]))
                id_list.append(record[idx2])
                if i%5000==0:
                    logger.info('目前进度{:.0%}'.format(i/total))
            ret = id_list,Tensor(f_list)
            #ret = [id_list,f_list]
            logger.info("完成%d条特征值的加载，耗时{:.3f}".format(time.time()-toc),count)
        return ret
    def readRecordToMem(self,table,fieldname,where=None):
        """
        把一条记录读入内存
        @param fieldname需要查找的字段名，元组。
        @param table
        @param where是一个三元素元组类型，例如where income>=15，income和>=和15，目前只支持一个条件
        @return 
        """
        try:
            cursor = self.connection.cursor()
            if where is not None:
                logger.debug(('select '+','.join((r'{}',)*len(fieldname))+' from {}').format(*fieldname,table)+" where "+'%s'*len(where)%where)
                count=cursor.execute(('select '+','.join((r'{}',)*len(fieldname))+' from {}').format(*fieldname,table)+" where "+'%s'*len(where)%where)
            else:
                logger.debug('select '+','.join((r'{}',)*len(fieldname))+' from {}').format(*fieldname,table)
                count = cursor.execute(('select '+','.join((r'{}',)*len(fieldname))+' from {}').format(*fieldname,table))
            
            ret = cursor.fetchall()
            cursor.close()
        except:
            ret = None
            logger.error("read table {} failed, trying to read fieldname {}.".format(table,fieldname),exc_info=True)
            self.connection.rollback()
        else:
            logger.info("read table {} successfully, totally {} row(s) are read!".format(table,str(count)))
        if 'feature' in fieldname or (table=='features_t' and '*' in fieldname):
            logger.info("开始加载特征值")
            ret = list()
            idx = fieldname.index('feature') if 'feature' in fieldname else 2
            for i,record in enumerate(ret):
                record = list(record)
                record[idx] = Tensor(eval(record[idx]))
                ret[i] = record
            logger.info("完成%d条特征值的加载",i)
        return ret