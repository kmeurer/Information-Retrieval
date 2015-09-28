import re
import codecs
import os
import utils as util
import settings as ENV

def extractDocuments():
	docFiles = []
	for filename in os.listdir(ENV.DOCUMENT_SRC):
		docFiles.append(filename)
	print docFiles
	readDoc(ENV.DOCUMENT_SRC + docFiles[0])


def readDoc(fileSrc):
	dataFile = codecs.open(fileSrc, 'rb', 'utf-8') 	# specify utf-8 encoding
	lines = dataFile.readlines() 					# read all lines
	fileStr = ""
	print "Unpacking file: " + fileSrc
	util.updateProgress(0)
	for idx, line in enumerate(lines):
		util.updateProgress(float(idx)/float(len(lines)))
		fileStr = fileStr + line
	util.updateProgress(1)
	docArray = re.split("<doc>", fileStr)
	print docArray[0]