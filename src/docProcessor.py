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
	return []

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

	# split into distinct documents
	docStrArray = re.split('</DOC>', fileStr)
	
	termList = [] # in format [term1, term2, term3, term4]
	postingList = {}

	# for each document, preprocess, writing to memory when the terms list exceeds the memory
	print "\n\nProcessing document included in " + fileSrc
	if ENV.PROGRESS_BAR == True:
		util.updateProgress(0)
	for idx, documentString in enumerate(docStrArray):
		if ENV.PROGRESS_BAR == True:
			util.updateProgress(float(idx) / float(len(docStrArray)))
		# Ignore empty document tokens
		if documentString.isspace() or documentString == "" :
			continue
		# Convert document to class format
		doc = d.Document(re.search('<DOCNO>(.*)</DOCNO>', documentString).group(1), documentString)
		
		doc.convertToLowerCase()
		doc.removeMetadata()
		doc.removeListInfo()
		doc.removeTags()
		
		# Process special tokens
		doc.processSpecialTerms()
		
		# clean up document by eliminating extraneous tokens, except in cases where they fall within brackets {}
		if ENV.INDEX_TYPE == "INVERTED":
			doc.tokenizeDocument()
			doc.cleanTokens()
			doc.removeStopWords()
			docTermDictionary = doc.extractTermInformation()

		elif ENV.INDEX_TYPE == "POSITIONAL":
			print "positional"

		elif ENV.INDEX_TYPE == "STEM":
			print "stem"

		elif ENV.INDEX_TYPE == "PHRASE":
			print "phrase"

		else:
			print "Invalid index type specified in settings."
			
	if ENV.PROGRESS_BAR == True:
		util.updateProgress(1)
	print "\n"

def isValidPhrase(term1, term2):
	if re.search('[\.\,\:\@\#]', term1) and "{" not in term1:
		return False
	else:
		return True

