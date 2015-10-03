import sys
import os
import codecs
import re
import datetime
sys.path.insert(0, 'src')

import docProcessor as dp
import utils as util
import settings as ENV
import indexing as idx
import document as d

startTime = datetime.datetime.now()

termList = []		# able to be stored in memory
tripleList = []		# max length specified by memory constrain specified in settings.py
stopTerms = dp.extractStopTerms()

# Empty our index folder
indexFiles = os.listdir(ENV.INDEX_LOCATION)
for f in indexFiles:
    os.remove(ENV.INDEX_LOCATION + f)

# for each file in the specified directory, extract and index documents
for filename in os.listdir(ENV.DOCUMENT_SRC):
	fileSrc = ENV.DOCUMENT_SRC + filename
	print "\n------------\nProcessing documents included in " + fileSrc + "\n"
	dataFile = codecs.open(fileSrc, 'rb', 'utf-8') 	# specify utf-8 encoding
	currentLine = dataFile.readline()
	count = 1
	while currentLine != '':
		if '<DOC>' in currentLine:
			sys.stdout.write("Processed " + str(count) + " documents...\r")
			count += 1
			docStr = ""
			currentLine = dataFile.readline()
			while '</DOC>' not in currentLine:
				docStr += currentLine
				currentLine = dataFile.readline()
			doc = dp.processDocument(docStr)
			# Pass indexing to our index function, which will triage based on the index specified in settings
			idx.indexDocument(doc, termList, tripleList, stopTerms)
		currentLine = dataFile.readline()

# write remaining triples to a file
idx.writeTriplesToFile(tripleList)
# merge our remaining temporary files
print "\n------------\n\nTemporary Triples Built.  Beginning Merge...\n"
mergeStart = datetime.datetime.now()
idx.mergeTempFiles()
mergeEnd = datetime.datetime.now()
mergeTime = mergeEnd - mergeStart
print "\nMerge Completed in " + str(mergeTime.seconds) + " second(s)."
# write the term list to a file called lexicon.txt
idx.writeTermListToFile(termList)
# convert our triples to a posting list
idx.convertTriplesToPostings(ENV.INDEX_LOCATION + ENV.TRIPLE_LIST_NAME + '.txt', ENV.INDEX_LOCATION + ENV.POSTING_LIST_NAME + '.txt')

endTime = datetime.datetime.now()
totalTime = endTime - startTime
tripleTime = mergeStart - startTime

print '\n------------\n\nPROGRAM COMPLETED IN ' + str(totalTime.seconds) + ' SECONDS\n\n\n--------------------------\n\n\n'
