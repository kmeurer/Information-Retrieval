import re
import codecs
import os
from object_definitions import query as q
import utils as util
import settings as ENV


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

def preprocess_query(queryString, stopTerms):
	if queryString.isspace() or queryString == "" :
		return None
	# Convert document to class format
	query = q.Query(queryString)
	# Use the same preprocessing strategy here for consistency
	query.preprocessText(stopTerms)
	# clean up document by eliminating extraneous tokens, except in cases where they fall within brackets {}
	return query

def extract_bm25_scores(query):
	return None

def extract_vector_space_scores(query):
	return None

def extract_language_model_scores(query):
	return None