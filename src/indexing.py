import re
import codecs
import utils as util
import settings as ENV
import bisect
import document as d
import tripleBuilder as tb

# indexDocument: Takes a single document and the global variables for storage and, based on the current index, adds terms to the triples list
def indexDocument(doc, termList, dfList, tripleList, stopTerms):
	# Depending on the index type, process in slightly different ways
	if ENV.INDEX_TYPE == "INVERTED":
		doc.cleanTokens()	# clean all tokens
		if ENV.REMOVE_STOP_WORDS == True:
			doc.removeStopWords(stopTerms)
		docTermDictionary = doc.extractTermInformation() # comes in form of {term: tf}
		# for every term included in the document...
		for term in docTermDictionary:
			termIdx = addTermToTermList(term, termList, dfList)
			# add it to our existing posting list, in order thanks to bisect
			bisect.insort(tripleList, (termIdx, doc.getDocId(), docTermDictionary[term]))
		if len(tripleList) >= ENV.MEMORY_MAXIMUM or ENV.MEMORY_MAXIMUM == None:
			tb.writeTriplesToFile(tripleList)

	elif ENV.INDEX_TYPE == "POSITIONAL":
		doc.cleanTokens()
		docTermDictionary = doc.extractTermPositionInformation() # in format {term: [count, [pos1, pos2, pos3]], term2: [count, [pos1, pos2, pos3]]}}
		# for every term and its position included in the document...
		for term in docTermDictionary:
			termIdx = addTermToTermList(term, termList, dfList)
			# add it to our existing posting list, in order thanks to bisect
			bisect.insort(tripleList, (termIdx, doc.getDocId(), docTermDictionary[term][0], docTermDictionary[term][1]))
		if len(tripleList) >= ENV.MEMORY_MAXIMUM or ENV.MEMORY_MAXIMUM == None:
			tb.writeTriplesToFile(tripleList)

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
		if len(tripleList) >= ENV.MEMORY_MAXIMUM:
			tb.writeTriplesToFile(tripleList)

	elif ENV.INDEX_TYPE == "PHRASE":
		phraseTermDictionary  = doc.extractValidPhrases(stopTerms)
		for phrase in phraseTermDictionary:
			termIdx = addPhraseToTermList(phrase, phraseTermDictionary[phrase], termList, dfList)
			# add it to our existing posting list, in order thanks to bisect
			if termIdx != None:
				bisect.insort(tripleList, (termIdx, doc.getDocId(), phraseTermDictionary[phrase]))
		if len(tripleList) >= ENV.MEMORY_MAXIMUM or ENV.MEMORY_MAXIMUM == None:
			tb.writeTriplesToFile(tripleList)
	else:
		print "Invalid index type specified in settings."

# addPhraseToTermList: Given a phrase, its frequency, and the global term list, append the term or add to its doc frequency
def addPhraseToTermList(phrase, phraseFreq, termList, dfList):
	termIdx = None  # return the index of the term (its ID)
	# handle insertion into termList
	# only add terms with a sufficient term frequency...
	if phraseFreq <= ENV.MIN_PHRASE_TF:
		return termIdx
	if phrase not in termList:
		termList.append(phrase)
		termIdx = len(termList) - 1
		dfList.append(1)
	else:
		termIdx = termList.index(phrase)
		dfList[termIdx] += 1
	return termIdx

# addTermToTermList: Given a term, add it to the lexicon
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

# writeTermListToFile: Write the term list to a file in the format "id term df"
def writeTermListToFile(termList, dfList):
	lexFile = codecs.open(ENV.INDEX_LOCATION + ENV.INDEX_TYPE.lower() + "Lexicon.txt", 'w', 'utf-8') 	# specify utf-8 encoding
	for idx, term in enumerate(termList):
		lexFile.write(str(idx) + " " + term + " " + str(dfList[idx]) + "\n")


