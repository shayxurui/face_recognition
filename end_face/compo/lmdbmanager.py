import os.path
import pickle
from torch import Tensor
class DataManager():
    def __init__(self, connector):
        self.connector = connector

    def connectDB(self):
        self.dbfile=self.connector['db']+'.pkl'
        if os.path.exists(self.dbfile):
            with open(self.dbfile, 'rb') as f:
                self.all_tables = pickle.load(f)
        else:
            self.all_tables = {'information_t':{},'features_t':[]}

    def readRecordsToMem(self,table,fieldname):
        if table=='information_t':
            return self.all_tables[table]
        elif table=='features_t':
            tmp = list(zip(*(self.all_tables[table])))
            return tmp[0],Tensor(tmp[1]).cuda()

    def readRecordToMem(self,table,fieldname,where=None):
        return [self.all_tables[table][where[2]]]

    def writeRecords(self,table,fieldname,records):
        if table=="information_t":
            self.__write_information(records)
        elif table=="features_t":
            self.__write_features(records)

    def __write_information(self,records):
        self.all_tables['information_t'].update(dict(tuple(map(lambda x:(x[0],x),records))))
        with open(self.dbfile, 'wb') as f:
            pickle.dump(self.all_tables, f)

    def __write_features(self,records):
        self.all_tables['features_t'].extend(records)
        with open(self.dbfile, 'wb') as f:
            pickle.dump(self.all_tables, f)
