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
					termIdx = termList.index(term)
					
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
	fileName = ENV.TEMP_FILE_NAME + str(len(indexFiles)) + ".txt"
	indexFile = codecs.open(ENV.INDEX_LOCATION + fileName, 'w', 'utf-8') 	# specify utf-8 encoding
	for triple in tripleList:
		indexFile.write(str(triple[0]) + " " + str(triple[1]) + " " + str(triple[2]) + "\n")

def writeTermListToFile(termList):
	lexFile = codecs.open(ENV.INDEX_LOCATION + "lexicon.txt", 'w', 'utf-8') 	# specify utf-8 encoding
	for idx, term in enumerate(termList):
		lexFile.write(str(idx) + " " + term + "\n")

def mergeTempFiles():
	while len(os.listdir(ENV.INDEX_LOCATION)) > 1:
		indexFiles = os.listdir(ENV.INDEX_LOCATION)
		mergeTripleLists(ENV.INDEX_LOCATION + indexFiles[0], ENV.INDEX_LOCATION + indexFiles[1])

def mergeTripleLists(filePath1, filePath2):
	file1 = codecs.open(filePath1, 'r', 'utf-8')
	file2 = codecs.open(filePath2, 'r', 'utf-8')
	mergeFile = codecs.open(ENV.INDEX_LOCATION + "templist.txt", 'w', 'utf-8')
	line1 = file1.readline()
	line1 = line1.split(" ")
	line2 = file2.readline().split(" ")
	while line1 != [''] and line2 != ['']:
		line1[0] = int(line1[0])
		line2[0] = int(line2[0])
		if line1[0] < line2[0]:
			mergeFile.write(str(line1[0]) + " " + str(line1[1]) + " " + str(line1[2]))
			line1 = file1.readline().split(" ")
		elif line1[0] > line2[0]:
			mergeFile.write(str(line2[0]) + " " + str(line2[1]) + " " + str(line2[2]))
			line2 = file2.readline().split(" ")
		else:
			line1[1] = int(line1[1])
			line2[1] = int(line2[1])
			if line1[1] < line2[1]:
				mergeFile.write(str(line1[0]) + " " + str(line1[1]) + " " + str(line1[2]))
				line1 = file1.readline().split(" ")
			elif line1[1] > line2[1]:
				mergeFile.write(str(line2[0]) + " " + str(line2[1]) + " " + str(line2[2]))
				line2 = file2.readline().split(" ")
			else:
				line1[2] = int(line1[2])
				line2[2] = int(line2[2])
				if line1[2] < line2[2]:
					mergeFile.write(str(line1[0]) + " " + str(line1[1]) + " " + str(line1[2]))
					line1 = file1.readline().split(" ")
				elif line1[2] > line2[2]:
					mergeFile.write(str(line2[0]) + " " + str(line2[1]) + " " + str(line2[2]))
					line2 = file2.readline().split(" ")
				else:
					mergeFile.write(str(line1[0]) + " " + str(line1[1]) + " " + str(line1[2]))
					line1 = file1.readline().split(" ")
	if line1 == ['']:
		while line2 != ['']:
			mergeFile.write(str(line2[0]) + " " + str(line2[1]) + " " + str(line2[2]))
			line2 = file2.readline().split(" ")
	elif line2 == ['']:
		while line1 != ['']:
			mergeFile.write(str(line1[0]) + " " + str(line1[1]) + " " + str(line1[2]))
			line1 = file1.readline().split(" ")
	file1.close()
	file2.close()
	mergeFile.close()
	os.remove(filePath2)
	os.remove(filePath1)
	os.rename(ENV.INDEX_LOCATION + "templist.txt", filePath1)




def isValidPhrase(term1, term2):
	if re.search('[\.\,\:\@\#]', term1) and "{" not in term1:
		return False
	else:
		return True
