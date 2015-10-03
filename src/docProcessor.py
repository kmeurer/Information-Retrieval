import re
import codecs
import os
import document as d
import utils as util
import settings as ENV
import document as d

def extractDocuments(fileName):
	dataFile = codecs.open(fileSrc, 'rb', 'utf-8') 	# specify utf-8 encoding
	lines = dataFile.readlines() 					# read all lines
	fileStr = ''

	print '\nUnpacking file: ' + fileSrc
	
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

def extractStopTerms():
	stopTerms = []
	stopTermFile = codecs.open(ENV.STOP_LIST_SRC, 'rb', 'utf-8') 	# specify utf-8 encoding
	lines = stopTermFile.readlines()
	for line in lines:
		stopTerms.append(re.sub('\n', '', line))
	return stopTerms

def processDocument(docStr):
	# Ignore empty document tokens
	if docStr.isspace() or docStr == "" :
		return None
	# Convert document to class format
	doc = d.Document(re.search('<DOCNO>(.*)</DOCNO>', docStr).group(1), docStr)
	preprocessDocument(doc)
	# clean up document by eliminating extraneous tokens, except in cases where they fall within brackets {}
	return doc

def preprocessDocument(doc):
	doc.convertToLowerCase()
	doc.removeMetadata()
	doc.removeListInfo()
	doc.removeTags()
	doc.modifyExtraneousCharacters()
	# Process special tokens
	doc.processSpecialTerms()