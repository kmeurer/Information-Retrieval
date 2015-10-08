import re
import datetime
import utils as util
import settings as ENV

# Takes in a full string and returns a term list of processed terms
def processSpecialTokens(docStr):
	docStr = processDates(docStr)
	docTerms = re.split('\s*', docStr)
	newTerms = []
	
	# For each term, determine if it is a special term
	for term in docTerms:
		if term.isspace() or term == '':
			continue
		if isFinancialValue(term):
			term = processFinancialValue(term)
		elif isDigit(term):
			term = processDigit(term)
		elif "." in term:
			if isFileExtension(term):
				term = processFileExtension(term)
			elif containsDomainName(term):	
				if isEmailAddress(term):
					term = processEmailAddress(term)
				else:
					term = processURL(term)
			elif isIPAddress(term):
				term = processIPAddress(term)
			elif isDottedTerm(term):
				term = processDottedTerm(term)
		if "-" in term:
			if isAlphabetDigit(term):
				term = processAlphabetDigit(term)
			elif isDigitAlphabet(term):
				term = processDigitAlphabet(term)
			elif isPrefixedTerm(term):
				term = processPrefixedTerm(term)
		if isinstance(term, list):
			newTerms = newTerms + term
		else:
			newTerms.append(term)
	return " ".join(newTerms)

# UTILITY FUNCTIONS FOR SPECIFIC TOKEN TYPES
# date processing (supported formats: "MMMM dd, YYYY", "MM/DD/YYYY", "MM-DD-YYYY")
def processDates(docStr):
	# slash date format: 1/24/1994 (we only find these to change 01 -> 1 and make all numbers consistent digits)
	slashDates = re.findall(r'(\d{1,2}\/\d{1,2}\/(?:\d{4}|\d{2}))', docStr)
	for date in slashDates:
		dateArr = date.split("/")
		if len(dateArr[0]) == 2 and dateArr[0][0] == "0":
			dateArr[0] = dateArr[0][1]
		if len(dateArr[1]) == 2 and dateArr[1][0] == "0":
			dateArr[1] = dateArr[1][1]
		if len(dateArr[2]) == 2:
			if (int(dateArr[2]) <= 18):
				dateArr[2] = "20" + dateArr[2]
			else:
				dateArr[2] = "19" + dateArr[2]
		docStr = docStr.replace(date, "/".join(dateArr))

	# full date format: january 24, 1994
	fullDates = re.findall(r'((?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\,\s+\d{4})', docStr)
	for date in fullDates:
		realTime = datetime.datetime.strptime(date, "%B %d, %Y")
		docStr = docStr.replace(date, str(realTime.month) + "/" + str(realTime.day) + "/" + str(realTime.year))

	# dash date format: 1-24-1994
	dashDates = re.findall('(\d{1,2}-\d{1,2}-(?:\d{4}|\d{2}))', docStr)
	for date in dashDates:
		dateArr = date.split("-")
		if len(dateArr[0]) == 2 and dateArr[0][0] == "0":
			dateArr[0] = dateArr[0][1]
		if len(dateArr[1]) == 2 and dateArr[1][0] == "0":
			dateArr[1] = dateArr[1][1]
		if len(dateArr[2]) == 2:
			if (int(dateArr[2]) <= 18):
				dateArr[2] = "20" + dateArr[2]
			else:
				dateArr[2] = "19" + dateArr[2]
		docStr = docStr.replace(date, "/".join(dateArr))
	return docStr

# dotted term processing (ex: "U.S.A."->"usa", "Ph.D"->"phd", "B.S."->"bs")
def isDottedTerm(docTerm):
	if re.match(r'\b\w{1,3}\.\w\.?\b|\b\w\.\w\.\w\.\b|\b\w\.\w\.\w\.\w\.\b', docTerm):
		return True
	return False

def processDottedTerm(docTerm):
	docTerm = re.sub('\.', '', docTerm)
	return docTerm

# financial value processing (ex: $1000->$1000, $1,000->$1000, $15.75->$15.75)
def isFinancialValue(docTerm):
	if "$" in docTerm:
		return True
	return False

def processFinancialValue(docTerm):
	docTerm = re.sub("\$", "", docTerm)
	docTerm = processDigit(docTerm)
	if len(docTerm) == 0:
		return docTerm
	else:
		docTerm = "{$" + docTerm + "}"
	return docTerm

# digit processing (ex: 1,000,000->1000000)
def isDigit(docTerm):
	termCopy = re.sub(",", "", docTerm)
	if util.isNumber(termCopy):
		return True
	return False

def processDigit(docTerm):
	docTerm = re.sub(",", "", docTerm)
	if "." in docTerm:
		if docTerm[len(docTerm) - 1] == ".":
			docTerm = re.sub(".", "", docTerm)
		elif re.match('\d+\.0+', docTerm):
			docTerm = docTerm.split(".")[0]
		elif ENV.INCLUDE_DECIMALS == True:
			docTerm = "{" + docTerm + "}"
		else:
			docTerm = docTerm.split(".")[0]
	return docTerm

# processing of alphabet-digits w/ 2 values stored if >3 letters (ex: "F-16"->"f16, "I-20"->i20, "CDC-50"->"cdc50" and "cdc")
def isAlphabetDigit(docTerm):
	if re.match('\w+-\d+', docTerm):
		return True
	return False

def processAlphabetDigit(docTerm):
	docTerm = docTerm.split("-")
	if (len(docTerm[0]) > 2):
		return [docTerm[0], docTerm[0] + docTerm[1]]
	else:
		return docTerm[0] + docTerm[1]

# processing of digit-alphabet (ex: "1-hour"->"1hour" and "hour")
def isDigitAlphabet(docTerm):
	if re.match(r'\d+-\w+', docTerm):
		return True
	return False

def processDigitAlphabet(docTerm):
	docTerm = docTerm.split("-")
	if (len(docTerm[1]) > 2):
		return [docTerm[0] + docTerm[1], docTerm[1]]
	else:
		return docTerm[0] + docTerm[1]

# processing of prefixed terms (ex: "pre-processing"->"preprocessing" and "processing", "part-of-speech"->"partofspeech" and "part" and "speech")
def isPrefixedTerm(docTerm):
	if re.match(r'\w*-\w*|\w*-\w*-\w*|\w*-\w*-\w*-\w*', docTerm):
		return True
	return False

def processPrefixedTerm(docTerm):
	splitTermList = docTerm.split("-")
	if splitTermList[0] in ENV.PREFIX_LIST:
		returnArr = [splitTermList[0] + splitTermList[1], splitTermList[1]]

		return returnArr
	else:
		splitTermList.append(''.join(splitTermList))

		return splitTermList

# processing of file extensions (ex: "something.pdf"->"pdf" and "something")
def isFileExtension(docTerm):
	for extension in ENV.FILE_EXTENSION_LIST:
		if extension in docTerm:
			return True
	return False

def processFileExtension(docTerm):
	terms = docTerm.split(".")
	return terms

def containsDomainName(docTerm):
	for domain in ENV.DOMAIN_LIST:
		if domain in docTerm:
			return True
	return False

# processing of email addresses (ex: "kevin@kevin.com"->"{kevin@kevin.com}")
def isEmailAddress(docTerm):
	if "@" in docTerm:
		return True
	return False

def processEmailAddress(docTerm):
	return "{" + docTerm + "}"

# processing of IP addresses (ex: "73.172.16.182"->"{73.172.16.182}")
def isIPAddress(docTerm):
	if re.match(r'\b\d{2,3}\.\d{2,3}\.\d{2,3}\.\d{2,3}\b', docTerm):
		return True
	return False

def processIPAddress(docTerm):
	print "IP ADDRESS: " + docTerm
	return "{" + docTerm + "}"

# processing of URLs (ex: "georgetown.edu"-> "{georgetown.edu}")
def processURL(docTerm):
	return "{" + docTerm + "}"
