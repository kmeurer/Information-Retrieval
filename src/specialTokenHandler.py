import re

def processSpecialTokens(docStr):
	docStr = processDates(docStr)
	docTerms = re.split('\s*', docStr)
	newTerms = []
	# For each term, determine if it is a special term
	for term in docTerms:
		if "." in term:
			if isFinancialValue(term):
				term = processFinancialValue(term)
			elif isFileExtension(term):
				term = processFileExtension(term)
			elif containsDomainName(term):	
				if isEmailAddress(term):
					term = processEmailAddress(term)
				elif isURL(term):
					term = processURL(term)
			elif isIPAddress(term):
				term = processIPAddress(term)
			elif isDigit(term):
				term = processDigit(term)
			elif isDottedTerm(term):
				term = processDottedTerm(term)
		if "-" in term:
			if isAlphabetDigit(term):
				term = processAlphabetDigit(term)
			elif isDigitAlphabet(term):
				term = processDigitAlphabet(term)
			elif isPrefixedTerm(term):
				term = processPrefixedTerm(term)
		newTerms.append(term)
	return " ".join(newTerms)

# UTILITY FUNCTIONS FOR SPECIFIC TOKEN TYPES
# date processing (supported formats: "MMMM dd, YYYY", "MM/DD/YYYY", "MM-DD-YYYY", "MMM-DD-YYYY")
def processDates(docStr):
	return docStr

# dotted term processing (ex: "U.S.A."->"usa", "Ph.D"->"phd", "B.S."->"bs")
def isDottedTerm(docTerm):
	return False

def processDottedTerm(docTerm):
	return docTerm

# financial value processing (ex: $1000->$1000, $1,000->$1000, $15.75->$15.75)
def isFinancialValue(docTerm):
	return False

def processFinancialValue(docTerm):
	return docTerm

# digit processing (ex: 1,000,000->1000000)
def isDigit(docTerm):
	return False

def processDigit(docTerm):
	return docTerm

# processing of alphabet-digits w/ 2 values stored if >3 letters (ex: "F-16"->"f16, "I-20"->i20, "CDC-50"->"cdc50" and "cdc")
def isAlphabetDigit(docTerm):
	return False

def processAlphabetDigit(docTerm):
	return docTerm

# processing of digit-alphabet (ex: "1-hour"->"1hour" and "hour")
def isDigitAlphabet(docTerm):
	return False

def processDigitAlphabet(docTerm):
	return docTerm

# processing of prefixed terms (ex: "pre-processing"->"preprocessing" and "processing", "part-of-speech"->"partofspeech" and "part" and "speech")
def isPrefixedTerm(docTerm):
	return False

def processPrefixedTerm(docTerm):
	return docTerm

# processing of file extensions (ex: "something.pdf"->"pdf" and "something")
def isFileExtension(docTerm):
	return False

def processFileExtension(docTerm):
	return docTerm

def containsDomainName(docTerm):
	return False

# processing of email addresses (ex: "kevin@kevin.com"->"{kevin@kevin.com}")
def isEmailAddress(docTerm):
	return False

def processEmailAddress(docTerm):
	return docTerm

# processing of IP addresses (ex: "73.172.16.182"->"{73.172.16.182}")
def isIPAddress(docTerm):
	return False

def processIPAddress(docTerm):
	return docTerm

# processing of URLs (ex: "georgetown.edu"-> "{georgetown.edu}")
def isURL(docTerm):
	return False

def processURL(docTerm):
	return docTerm
