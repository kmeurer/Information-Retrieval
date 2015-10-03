import re
import specialTokenHandler as sth

class Document:
	def __init__(self, docId, text):
		self.id = int(re.sub("\D", "", docId)) # stores as number for space efficiency
		self.text = text
		self.tokenizeDocument();

	def addText(self, textStr):
		self.text = self.text + " " + textStr

	def tokenizeDocument(self):
		self.tokens = re.split('\s*', self.text)
	
	def cleanTokens(self):
		for idx, term in enumerate(self.tokens):
			if term.isspace() or term == "":
				continue
			# the {} is used to escape special tokens from efforts to remove punctuation
			if term[0] == '{' and term[len(term) - 1] == '}':
				term = re.sub('[\{\}]', '', term)
				self.tokens[idx] = term
			else:
				term = re.sub('[\^\*\#\@\.\[\]\(\);\"\']', '', term)
				if term.isspace() or term == "":
					continue
				else:
					self.tokens[idx] = term

	def getDocId(self):
		return self.id
	
	def convertToLowerCase(self):
		self.text = self.text.lower()

	def removeTags(self):
		self.text = re.sub('<.*?>', ' ', self.text)

	def removeMetadata(self):
		self.text = re.sub('<DOCNO>(.*)</DOCNO>|<PARENT>(.*)</PARENT>', '', self.text)

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

	def modifyExtraneousCharacters(self):
		self.text = self.text.replace('&sect;', '').replace('&blank;', '').replace('&hypn;', '-')

	def removeStopWords(self, lexicon):
		newTokens = []
		for term in self.tokens:
			if term not in lexicon:
				newTokens.append(term)
		self.tokens = newTokens
