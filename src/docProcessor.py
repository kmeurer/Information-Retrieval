import re
import codecs
import os
import utils as util
import settings as ENV
import specialTokenHandler as sth

def extractDocuments(fileName):
	documentDict = readDocs(fileName)
	return documentDict


def readDocs(fileSrc):
	dataFile = codecs.open(fileSrc, 'rb', 'utf-8') 	# specify utf-8 encoding
	lines = dataFile.readlines() 					# read all lines
	fileStr = ""
	print "\nUnpacking file: " + fileSrc
	util.updateProgress(0)
	for idx, line in enumerate(lines):
		util.updateProgress(float(idx)/float(len(lines)))
		fileStr = fileStr + line
	util.updateProgress(1)
	fileStr = fileStr.replace('\n', ' ').replace('\r', '')
	docArray = re.split('</DOC>', fileStr)
	docDict = {}
	# for each document, extract free text and tokenize
	print "\n\nProcessing documents included in " + fileSrc
	util.updateProgress(0)
	for idx, doc in enumerate(docArray):
		util.updateProgress(float(idx) / float(len(docArray)))
		# Ignore empty document tokens
		if doc.isspace() or doc == "" :
			continue
		# Convert document to Lower Case
		doc = doc.lower()
		# Extract Document ID
		docId = getDocId(doc)
		doc = removeMetadata(doc)
		doc = removeListInfo(doc)
		doc = removeDocTags(doc)
		# Process special tokens and return the terms list
		docTerms = sth.processSpecialTokens(doc)
		finalTerms = []
		# clean up document by eliminating extraneous tokens, except in cases where they fall within brackets {}
		for idx, term in enumerate(docTerms):
			if term.isspace() or term == "":
				continue
			if term[0] == '{' and term[len(term) - 1] == '}':
				term = re.sub('[\{\}]', '', term)
				finalTerms.append(term)
			else:
				term = re.sub('[\^\*\#\@\.\[\]\(\);]', '', term)
				if term.isspace() or term == "":
					continue
				else:
					finalTerms.append(term)
		docDict[docId] = finalTerms
	util.updateProgress(1)
	print "\n"
	return docDict

def getDocId(doc):
	return re.search('<docno>(.*)</docno>', doc).group(1)

def removeDocTags(doc):
	return re.sub('<.*?>', ' ', doc)

def removeMetadata(doc):
	return re.sub('<docno>(.*)</docno>|<parent>(.*)</parent>', '', doc)

def removeListInfo(doc):
	return re.sub('\(\d\)|\(\w\)|subpart\s\w', '', doc)

def tokenizeDocument(docStr):
	print docStr
