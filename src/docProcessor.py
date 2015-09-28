import re
import codecs
import os
import utils as util
import settings as ENV

def extractDocuments():
	docFiles = []
	for filename in os.listdir(ENV.DOCUMENT_SRC):
		docFiles.append(filename)
	readDocs(ENV.DOCUMENT_SRC + docFiles[0])


def readDocs(fileSrc):
	dataFile = codecs.open(fileSrc, 'rb', 'utf-8') 	# specify utf-8 encoding
	lines = dataFile.readlines() 					# read all lines
	fileStr = ""
	print "Unpacking file: " + fileSrc
	util.updateProgress(0)
	for idx, line in enumerate(lines):
		util.updateProgress(float(idx)/float(len(lines)))
		fileStr = fileStr + line
	util.updateProgress(1)
	# print fileStr
	fileStr = fileStr.replace('\n', '').replace('\r', '')
	docArray = re.split('</DOC>', fileStr)
	docDict = {}
	for doc in docArray:
		if doc == '':
			continue
		docId = re.search('<DOCNO>(.*)</DOCNO>', doc).group(1)
		doc = re.sub('<DOCNO>(.*)</DOCNO>|<PARENT>(.*)</PARENT>|\(\d\)|\(\w\)', '', doc)
		doc = re.sub('<.*?>', '', doc)
		print doc

def tokenizeDocument(docStr):
	print docStr
