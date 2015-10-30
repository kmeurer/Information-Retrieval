import re
import codecs
import os
import document as d
import utils as util
import settings as ENV
import document as d

def extractStopTerms():
	stopTerms = []
	stopTermFile = codecs.open(ENV.STOP_LIST_SRC, 'rb', 'utf-8') 	# specify utf-8 encoding
	lines = stopTermFile.readlines()
	for line in lines:
		stopTerms.append(re.sub('\n', '', line))
	return stopTerms

# Pull relevant information from query file, including title, num, and description
def extractQueryInformation():
	queries = {}
	queryFile = codecs.open(ENV.QUERY_SRC, 'rb', 'utf-8') 	# specify utf-8 encoding
	currentLine = queryFile.readline()
	currentNum = None
	currentTitle = ''
	while currentLine != '':
		if '<num>' in currentLine:
			numLine = currentLine.split('Number: ')
			currentNum = int(re.sub("\s", "", numLine[1]))
		elif '<title>' in currentLine:
			titleLine = currentLine.split('Topic: ')
			title = titleLine[1].replace('\n', '')
			queries[title] = {}
			queries[title]["number"] = currentNum
			currentTitle = title
		elif '<desc>' in currentLine:
			currentLine = queryFile.readline()
			description = ''
			while '<narr>' not in currentLine:
				description += currentLine.replace('\n', ' ')
				currentLine = queryFile.readline()
			queries[currentTitle]["description"] = description
		currentLine = queryFile.readline()
	return queries

def writeDocListToFile(docList):
	print "running"
	fileName = ENV.INDEX_TYPE.lower() + ENV.DOC_FILE_NAME + ".txt"
	docFile = codecs.open(ENV.INDEX_LOCATION + fileName, 'w', 'utf-8') 	# specify utf-8 encoding
	for doc in docList:
		docFile.write(str(doc[0]) + " " + str(doc[1]) + "\n")

def processDocument(docStr, stopTerms):
	# Ignore empty document tokens
	if docStr.isspace() or docStr == "" :
		return None
	# Convert document to class format
	doc = d.Document(re.search('<DOCNO>(.*)</DOCNO>', docStr).group(1), docStr)
	doc.preprocessText(stopTerms)
	# clean up document by eliminating extraneous tokens, except in cases where they fall within brackets {}
	return doc