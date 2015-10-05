import re
import specialTokenHandler as sth
import nltk.stem.porter as ps

class Document:
	def __init__(self, docId, text):
		self.id = int(re.sub("\D", "", docId)) # stores as number for space efficiency
		self.text = text
		self.tokenizeDocument();
		self.phrases = []

	def addText(self, textStr):
		self.text = self.text + " " + textStr

	def tokenizeDocument(self):
		self.tokens = re.split('\s*', self.text)
	
	def cleanTokens(self):
		for idx, term in enumerate(self.tokens):
			term = self.cleanTerm(term)
			if term.isspace() or term == "":
				continue
			self.tokens[idx] = term

	def cleanTerm(self, term):
		if term.isspace() or term == "":
			return term
		# the {} is used to escape special tokens from efforts to remove punctuation
		if term[0] == '{' and term[len(term) - 1] == '}':
			term = re.sub('[\{\}]', '', term)
		else:
			term = re.sub('[\^\*#@\.,\[\]\(\);"\'`\:\/]', '', term)
		return term

	def getDocId(self):
		return self.id
	
	def convertToLowerCase(self):
		self.text = self.text.lower()

	def removeTags(self):
		self.text = re.sub('<.*?>', ' ', self.text)

	def removeMetadata(self):
		self.text = re.sub('<docno>(.*)</docno>|<parent>(.*)</parent>', '', self.text)

	def removeListInfo(self):
		self.text = re.sub('\(\d\)|\(\w\)|subpart\s\w', '', self.text)

	def processSpecialTerms(self):
		self.text = sth.processSpecialTokens(self.text)

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

	def extractValidPhrases(self, stopWords):
		self.phrases[:] = []
		phraseCounts = {}
		for idx, term in enumerate(self.tokens):
			if idx == 0 or term.isspace():
				continue
			if idx > 0:
				if self.isValidBigram(self.tokens[idx - 1], term, stopWords):
					phrase = self.cleanTerm(self.tokens[idx - 1]) + "_" + self.cleanTerm(term)
					self.phrases.append(phrase)
					if phrase in phraseCounts:
						phraseCounts[phrase] += 1
					else:
						phraseCounts[phrase] = 1
			if idx > 1:
				if self.isValidTrigram(self.tokens[idx - 2], self.tokens[idx - 1], term, stopWords):
					phrase = self.cleanTerm(self.tokens[idx - 2]) + "_" + self.cleanTerm(self.tokens[idx - 1]) + "_" + self.cleanTerm(term)
					self.phrases.append(phrase)
					if phrase in phraseCounts:
						phraseCounts[phrase] += 1
					else:
						phraseCounts[phrase] = 1
		return phraseCounts

	def isValidBigram(self, term1, term2, stopList):
		if re.search('[\\\.\,\:\@\#\/]', term1) and "{" not in term1:
			return False
		term1 = self.cleanTerm(term1)
		term2 = self.cleanTerm(term2)
		if term1 in stopList or term2 in stopList:
			return False
		else:
			return True

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

	def modifyExtraneousCharacters(self):
		self.text = self.text.replace('&sect', '').replace('&blank', '').replace('&hyph', '-').replace('_', " ").replace('&amp', '')

	def stemTerms(self):
		pStem = ps.PorterStemmer()
		for idx, term in enumerate(self.tokens):
			self.tokens[idx] = pStem.stem(term)

	def removeStopWords(self, lexicon):
		newTokens = []
		for term in self.tokens:
			if term not in lexicon:
				newTokens.append(term)
		self.tokens = newTokens
