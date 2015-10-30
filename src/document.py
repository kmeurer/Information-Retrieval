import re
import specialTokenHandler as sth
import nltk.stem.porter as ps
import settings as ENV

'''
TextObject Class: overarching class that is used as a parent for both Document and Query
'''
class TextObject(object):
	def __init__(self, text):
		self.text = text
		self.tokenizeDocument();
		self.phraseCounts = {}

	# Run the full preprocessing routine
	def preprocessText(self):
		self.convertToLowerCase()
		self.removeMetadata()
		self.removeListInfo()
		self.removeTags()
		self.modifyExtraneousCharacters()
		# Process special tokens
		self.processSpecialTerms()
		self.tokenizeDocument();

	# tokenizeDocument: Splits a document by spaces
	def tokenizeDocument(self):
		self.tokens = re.split('\s*', self.text)

	# Add text function.  Appends text to the document
	def addText(self, textStr):
		self.text = self.text + " " + textStr
		self.tokenizeDocument();

	# convertToLowerCase: Converts the document to lower case
	def convertToLowerCase(self):
		self.text = self.text.lower()
		self.tokenizeDocument();

	# removeStopWords: Removes stop words based on a lexicon of pre-defined stop terms
	def removeStopWords(self, lexicon):
		newTokens = []
		for term in self.tokens:
			if term not in lexicon:
				newTokens.append(term)
		self.tokens = newTokens
		self.text = " ".join(self.tokens)

	# removeListInfo: Removes lists of items from the document (i.e. (1), (2))
	def removeListInfo(self):
		self.text = re.sub('\(\d\)|\(\w\)|subpart\s\w', '', self.text)
		self.tokenizeDocument()

	# modifyExtraneousCharacters: replaces extraneous characters with nothing or regular characters
	def modifyExtraneousCharacters(self):
		self.text = self.text.replace('&sect', '').replace('&blank', '').replace('&hyph', '-').replace('_', " ").replace('&amp', '')
		self.tokenizeDocument()

	# stemTerms: stems all tokens in self.tokens using the nltk porter stemmer
	def stemTerms(self):
		pStem = ps.PorterStemmer()
		for idx, term in enumerate(self.tokens):
			self.tokens[idx] = pStem.stem(term)
		self.text = " ".join(self.tokens)

	# cleanTokens:  Cleans all tokens included in the document by removing punctuation while protecting special tokens
	def cleanTokens(self):
		for idx, term in enumerate(self.tokens):
			term = self.cleanTerm(term)
			if term.isspace() or term == "":
				continue
			self.tokens[idx] = term
		self.text = " ".join(self.tokens)

	# removeMetadata: Removes all metadata in the document by eliminating docno and parent tags + info
	def removeMetadata(self):
		self.text = re.sub('<docno>(.*)</docno>|<parent>(.*)</parent>', '', self.text)

	# removeTags: Removes all tags in the document
	def removeTags(self):
		self.text = re.sub('<.*?>', ' ', self.text)

	# processSpecialTerms:  Defers to the processing function in specialTokenHandler.py to process all special terms
	def processSpecialTerms(self):
		self.text = sth.processSpecialTokens(self.text)

	# extractTermInformation:  Return a dictionary of each term and its term frequency
	def extractTermInformation(self):
		if len(self.tokens) == 0:
			self.tokenizeDocument();
		termCounts = {} # in format {term: count, term2: count2}}
		for term in self.tokens:
			if term in termCounts:
				termCounts[term] += 1
			else:
				termCounts[term] = 1
		return termCounts

	def getPhraseCounts(self):
		return self.phraseCounts

	# extractValidPhrases:  Returns a dictionary of valid bigrams and trigrams in the format "word1_word2"
	def extractValidPhrases(self, stopWords):
		self.phraseCounts = {}
		for idx, term in enumerate(self.tokens):
			if idx == 0 or term.isspace():
				continue
			if idx > 0:
				if self.isValidBigram(self.tokens[idx - 1], term, stopWords):
					phrase = self.cleanTerm(self.tokens[idx - 1]) + "_" + self.cleanTerm(term)
					# self.phrases.append(phrase)
					if phrase in self.phraseCounts:
						self.phraseCounts[phrase] += 1
					else:
						self.phraseCounts[phrase] = 1
			if idx > 1:
				if self.isValidTrigram(self.tokens[idx - 2], self.tokens[idx - 1], term, stopWords):
					phrase = self.cleanTerm(self.tokens[idx - 2]) + "_" + self.cleanTerm(self.tokens[idx - 1]) + "_" + self.cleanTerm(term)
					# self.phrases.append(phrase)
					if phrase in self.phraseCounts:
						self.phraseCounts[phrase] += 1
					else:
						self.phraseCounts[phrase] = 1
		return self.phraseCounts

	# isValidBigram: Determine if a group of terms is a valid bigram. Returns true if valid and false if not
	def isValidBigram(self, term1, term2, stopList):
		if re.search('[\\\.\,\:\@\#\/]', term1) and "{" not in term1:
			return False
		term1 = self.cleanTerm(term1)
		term2 = self.cleanTerm(term2)
		if term1 in stopList or term2 in stopList:
			return False
		else:
			return True

	# isValidTrigram: Determine if a group of terms is a valid trigram. Returns true if valid and false if not
	def isValidTrigram(self, term1, term2, term3, stopList):
		if (re.search('[\\\.\,\:\@\#\/]', term1) and "{" not in term1) or (re.search('[\\\.\,\:\@\#\/]', term2) and "{" not in term2):
			return False
		term1 = self.cleanTerm(term1)
		term2 = self.cleanTerm(term2)
		term3 = self.cleanTerm(term3)
		if term1 in stopList or term2 in stopList or term3 in stopList:
			return False
		else:
			return True

	# cleanTerm:  Cleans an individual term
	def cleanTerm(self, term):
		if term.isspace() or term == "":
			return term
		# the {} is used to escape special tokens from efforts to remove punctuation
		if term[0] == '{' and term[len(term) - 1] == '}':
			term = re.sub('[\{\}]', '', term)
		else:
			# term = re.sub(r'[\^\*#@\.,\[\]\(\);"\'`\:\/]', '', term)
			term = re.sub(r'[^\w\s]', '', term)
		return term

	# extractTermPositionInformation: Returns a dictionary of each term, its term frequency, and its position
	def extractTermPositionInformation(self):
		if len(self.tokens) == 0:
			self.tokenizeDocument();
		termCounts = {} # in format {term: [count, [pos1, pos2, pos3]], term2: [count, [pos1, pos2, pos3]]}}
		for idx, term in enumerate(self.tokens):
			if term in termCounts:
				termCounts[term][0] += 1
				termCounts[term][1].append(idx)
			else:
				termCounts[term] = [1, [idx]]
		return termCounts

'''
Document object.  Specific information related to documents
'''
class Document(TextObject):
	def __init__(self, docId, text):
		super(Document, self).__init__(text)
		self.id = int(re.sub("\D", "", docId)) # stores as number for space efficiency

	# getDocId: returns the id of the current document
	def getDocId(self):
		return self.id

	def preprocessText(self, stopTerms):
		super(Document, self).preprocessText()
		if ENV.INDEX_TYPE == "PHRASE":
			self.extractValidPhrases(stopTerms)
		# Now that we have our phrase information, we can clean our tokens
		self.cleanTokens()

'''
Query Object.  Information specific to queries.  Inherits all properties from TextObject
'''
class Query(TextObject):
	def __init__(self, text):
		super(Query, self).__init__(text)

	def preprocessText(self, stopTerms):
		super(Query, self).preprocessText()
		self.extractValidPhrases(stopTerms)
		# Now that we have our phrase information, we can clean our tokens
		self.cleanTokens()
