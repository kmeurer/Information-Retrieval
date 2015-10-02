import re
import codecs
import os
import utils as util
import settings as ENV
import document as d

def extractDocuments(fileName):
	documentDict = readDoc(fileName)
	return documentDict

def extractStopTerms():
	stopTerms = []
	stopTermFile = codecs.open(ENV.STOP_LIST_SRC, 'rb', 'utf-8') 	# specify utf-8 encoding
	lines = stopTermFile.readlines()
	for line in lines:
		stopTerms.append(re.sub("\n", "", line))
	return stopTerms

def readDoc(fileSrc):
	dataFile = codecs.open(fileSrc, 'rb', 'utf-8') 	# specify utf-8 encoding
	lines = dataFile.readlines() 					# read all lines
	fileStr = ""

	print "\nUnpacking file: " + fileSrc
	
	if ENV.PROGRESS_BAR == True:
		util.updateProgress(0)
	
	for idx, line in enumerate(lines):
		if ENV.PROGRESS_BAR == True:
			util.updateProgress(float(idx) / float(len(lines)))
		fileStr = fileStr + line
	
	if ENV.PROGRESS_BAR == True:
		util.updateProgress(1)

	# remove new line characters from the file
	fileStr = fileStr.replace('\n', ' ').replace('\r', '')
	
	return fileStr
