import re
import json
import os
import codecs
import utils as util
import settings as ENV
import bisect
import document as d

def buildTempFiles(docStrArray, stopTerms, termL):
	termList = termL 		# in format [term1, term2, term3, term4]
	tripleList = [] 		# in format [(termId(from termList), docId, tf)]

	# for each document, preprocess, writing to memory when the terms list exceeds the memory
	print "\n\nPreprocessing Documents."
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
		
		preprocessDocument(doc)

		# clean up document by eliminating extraneous tokens, except in cases where they fall within brackets {}
		if ENV.INDEX_TYPE == "INVERTED":
			doc.tokenizeDocument()
			doc.cleanTokens()
			doc.removeStopWords(stopTerms)
			docTermDictionary = doc.extractTermInformation() # comes in form of {term: tf}
			for term in docTermDictionary:
				termIdx = None
				# handle insertion into termList
				if term not in termList:
					termList.append(term)
					termIdx = len(termList) - 1
				else:
					termIdx = bisect.bisect_left(termList, term)
				# add it to our existing posting list, in order thanks to bisect
				bisect.insort(tripleList, (termIdx, doc.getDocId(), docTermDictionary[term]))
			if len(tripleList) >= ENV.MEMORY_MAXIMUM:
				writeTriplesToFile(tripleList)
				tripleList = []

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

def preprocessDocument(doc):
	doc.convertToLowerCase()
	doc.removeMetadata()
	doc.removeListInfo()
	doc.removeTags()
	doc.modifyExtraneousCharacters()
	# Process special tokens
	doc.processSpecialTerms()

def writeTriplesToFile(tripleList):
	indexFiles = os.listdir(ENV.INDEX_LOCATION)
	fileName = "tempindex" + str(len(indexFiles)) + ".txt"
	indexFile = codecs.open(ENV.INDEX_LOCATION + fileName, 'w', 'utf-8') 	# specify utf-8 encoding
	for triple in tripleList:
		indexFile.write(str(triple[0]) + " " + str(triple[1]) + " " + str(triple[2]) + "\n")

def writeTermListToFile(termList):
	lexFile = codecs.open(ENV.INDEX_LOCATION + "lexicon.txt", 'w', 'utf-8') 	# specify utf-8 encoding
	for idx, term in enumerate(termList):
		lexFile.write(str(idx) + " " + term)

def mergeTripleFiles():
	return True

def isValidPhrase(term1, term2):
	if re.search('[\.\,\:\@\#]', term1) and "{" not in term1:
		return False
	else:
		return True
