#!/usr/bin/python3
from faceutil import registerFaces
from predictor import Predictor
from detector import Detector
from lmdbmanager import DataManager

def reg_(file):
	predictor = Predictor("model/sphere20a_20171020.pth")
	detector = Detector("model")
	dm = DataManager({'db':'facedb'})
	dm.connectDB()
	registerFaces(dm,predictor,detector,file)

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('file',type=str,help='csv file')
	args = parser.parse_args()
	reg_(args.file)
