import re
import json
import os
import codecs
import utils as util
import settings as ENV
import bisect
import document as d

def indexDocument(doc, termList, dfList, tripleList, stopTerms):
	if ENV.INDEX_TYPE == "INVERTED":
		doc.cleanTokens()
		if ENV.REMOVE_STOP_WORDS == True:
			doc.removeStopWords(stopTerms)
		docTermDictionary = doc.extractTermInformation() # comes in form of {term: tf}
		for term in docTermDictionary:
			termIdx = addTermToTermList(term, termList, dfList)
			# add it to our existing posting list, in order thanks to bisect
			bisect.insort(tripleList, (termIdx, doc.getDocId(), docTermDictionary[term]))
		if len(tripleList) >= ENV.MEMORY_MAXIMUM or ENV.MEMORY_MAXIMUM == None:
			writeTriplesToFile(tripleList)

	elif ENV.INDEX_TYPE == "POSITIONAL":
		doc.cleanTokens()
		docTermDictionary = doc.extractTermPositionInformation() # in format {term: [count, [pos1, pos2, pos3]], term2: [count, [pos1, pos2, pos3]]}}
		for term in docTermDictionary:
			termIdx = addTermToTermList(term, termList, dfList)
			# add it to our existing posting list, in order thanks to bisect
			bisect.insort(tripleList, (termIdx, doc.getDocId(), docTermDictionary[term][0], docTermDictionary[term][1]))
		if len(tripleList) >= ENV.MEMORY_MAXIMUM or ENV.MEMORY_MAXIMUM == None:
			writeTriplesToFile(tripleList)

	elif ENV.INDEX_TYPE == "STEM":
		doc.cleanTokens()
		if ENV.REMOVE_STOP_WORDS == True:
			doc.removeStopWords(stopTerms)
		# Stem our document terms
		doc.stemTerms()
		docTermDictionary = doc.extractTermInformation() # comes in form of {term: tf}
		for term in docTermDictionary:
			termIdx = addTermToTermList(term, termList, dfList)
			# add it to our existing posting list, in order thanks to bisect
			bisect.insort(tripleList, (termIdx, doc.getDocId(), docTermDictionary[term]))
		if len(tripleList) >= ENV.MEMORY_MAXIMUM or ENV.MEMORY_MAXIMUM == None:
			writeTriplesToFile(tripleList)

	elif ENV.INDEX_TYPE == "PHRASE":
		print "phrase"

	else:
		print "Invalid index type specified in settings."

def addTermToTermList(term, termList, dfList):
	termIdx = None
	# handle insertion into termList
	if term not in termList:
		termList.append(term)
		termIdx = len(termList) - 1
		dfList.append(1)
	else:
		termIdx = termList.index(term)
		dfList[termIdx] += 1
	return termIdx

def writeTriplesToFile(tripleList):
	indexFiles = os.listdir(ENV.INDEX_LOCATION)
	fileName = ENV.TEMP_FILE_NAME + str(len(indexFiles)) + ".txt"
	indexFile = codecs.open(ENV.INDEX_LOCATION + fileName, 'w', 'utf-8') 	# specify utf-8 encoding
	for triple in tripleList:
		if ENV.INDEX_TYPE == "POSITIONAL":
			indexFile.write(str(triple[0]) + " " + str(triple[1]) + " " + str(triple[2]) + " " + str(triple[3]).replace(" ", "") + "\n")
		else:
			indexFile.write(str(triple[0]) + " " + str(triple[1]) + " " + str(triple[2]) + "\n")
	tripleList[:] = []

def writeTermListToFile(termList, dfList):
	lexFile = codecs.open(ENV.INDEX_LOCATION + "lexicon.txt", 'w', 'utf-8') 	# specify utf-8 encoding
	for idx, term in enumerate(termList):
		lexFile.write(str(idx) + " " + term + " " + str(dfList[idx]) + "\n")


def mergeTempFiles():
	while len(os.listdir(ENV.INDEX_LOCATION)) > 1:
		indexFiles = os.listdir(ENV.INDEX_LOCATION)
		mergeTripleLists(ENV.INDEX_LOCATION + indexFiles[0], ENV.INDEX_LOCATION + indexFiles[1])
	os.rename(ENV.INDEX_LOCATION + indexFiles[0], ENV.INDEX_LOCATION + ENV.TRIPLE_LIST_NAME + ".txt")

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
			if ENV.INDEX_TYPE == "POSITIONAL":
				quadrupleWrite(mergeFile, line1)
			else:
				tripleWrite(mergeFile, line1)
			line1 = file1.readline().split(" ")
		elif line1[0] > line2[0]:
			if ENV.INDEX_TYPE == "POSITIONAL":
				quadrupleWrite(mergeFile, line2)
			else:
				tripleWrite(mergeFile, line2)
			line2 = file2.readline().split(" ")
		else:
			line1[1] = int(line1[1])
			line2[1] = int(line2[1])
			if line1[1] < line2[1]:
				if ENV.INDEX_TYPE == "POSITIONAL":
					quadrupleWrite(mergeFile, line1)
				else:
					tripleWrite(mergeFile, line1)
				line1 = file1.readline().split(" ")
			elif line1[1] > line2[1]:
				if ENV.INDEX_TYPE == "POSITIONAL":
					quadrupleWrite(mergeFile, line2)
				else:
					tripleWrite(mergeFile, line2)
				line2 = file2.readline().split(" ")
			else:
				line1[2] = int(line1[2])
				line2[2] = int(line2[2])
				if line1[2] < line2[2]:
					if ENV.INDEX_TYPE == "POSITIONAL":
						quadrupleWrite(mergeFile, line1)
					else:
						tripleWrite(mergeFile, line1)
					line1 = file1.readline().split(" ")
				elif line1[2] > line2[2]:
					if ENV.INDEX_TYPE == "POSITIONAL":
						quadrupleWrite(mergeFile, line2)
					else:
						tripleWrite(mergeFile, line2)
					line2 = file2.readline().split(" ")
				else:
					if ENV.INDEX_TYPE == "POSITIONAL":
						quadrupleWrite(mergeFile, line1)
					else:
						tripleWrite(mergeFile, line1)
					line1 = file1.readline().split(" ")
	if line1 == ['']:
		while line2 != ['']:
			if ENV.INDEX_TYPE == "POSITIONAL":
				quadrupleWrite(mergeFile, line2)
			else:
				tripleWrite(mergeFile, line2)
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

def tripleWrite(fileName, lineArr):
	fileName.write(str(lineArr[0]) + " " + str(lineArr[1]) + " " + str(lineArr[2]))

def quadrupleWrite(fileName, lineArr):
	fileName.write(str(lineArr[0]) + " " + str(lineArr[1]) + " " + str(lineArr[2]) + " " + str(lineArr[3]))	


def convertTriplesToPostings(triplePath, postingPath):
	tripleFile = codecs.open(triplePath, 'r', 'utf-8')
	postingFile = codecs.open(postingPath, 'w', 'utf-8')
	currentLine = tripleFile.readline().replace('\n', '').split(" ")
	currentTerm = currentLine[0]
	if ENV.INDEX_TYPE == "POSITIONAL":
		newLine = currentTerm + ": (" + currentLine[1] + ", " + currentLine[2] + ", " + currentLine[3] + ")"
	else:
		newLine = currentTerm + ": (" + currentLine[1] + ", " + currentLine[2] + ")"
	while currentLine != ['']:
		currentLine = tripleFile.readline().replace('\n', '').split(" ")
		if len(currentLine) < 3:
			continue
		if currentLine[0] != currentTerm:
			postingFile.write(newLine + "\n")
			currentTerm = currentLine[0]
			if ENV.INDEX_TYPE == "POSITIONAL":
				newLine = currentTerm + ": (" + currentLine[1] + ", " + currentLine[2] + ", " + currentLine[3] + ")"
			else:
				newLine = currentTerm + ": (" + currentLine[1] + ", " + currentLine[2] + ")"
		else:
			if ENV.INDEX_TYPE == "POSITIONAL":
				newLine += "->(" + currentLine[1] + ", " + currentLine[2] + ", " + currentLine[3] + ")"
			else:
				newLine += "->(" + currentLine[1] + ", " + currentLine[2] + ")"

def isValidPhrase(term1, term2):
	if re.search('[\.\,\:\@\#]', term1) and "{" not in term1:
		return False
	else:
		return True
