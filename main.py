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
import numpy as np
import document as d
import tabulate as tb

startTime = datetime.datetime.now()

termList = []		# able to be stored in memory
dfList = []			# companion to term list of df
tripleList = []		# max length specified by memory constrain specified in settings.py
stopTerms = dp.extractStopTerms()

# Empty our index folder
indexFiles = os.listdir(ENV.INDEX_LOCATION)
for f in indexFiles:
    os.remove(ENV.INDEX_LOCATION + f)

# for each file in the specified directory, extract and index documents
totalDocCount = 0
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
			totalDocCount += 1
			docStr = ""
			currentLine = dataFile.readline()
			while '</DOC>' not in currentLine:
				docStr += currentLine
				currentLine = dataFile.readline()
			doc = dp.processDocument(docStr)
			# Pass indexing to our index function, which will triage based on the index specified in settings
			idx.indexDocument(doc, termList, dfList, tripleList, stopTerms)
		currentLine = dataFile.readline()

# write remaining triples to a file
idx.writeTriplesToFile(tripleList)
# merge our remaining temporary files
print "\n------------\n\nTemporary Triples Built.  Beginning Merge...\n"
mergeStart = datetime.datetime.now()
idx.mergeTempFiles()
# convert our triples to a posting list
idx.convertTriplesToPostings(ENV.INDEX_LOCATION + ENV.TRIPLE_LIST_NAME + '.txt', ENV.INDEX_LOCATION + ENV.POSTING_LIST_NAME + '.txt')
mergeEnd = datetime.datetime.now()
mergeTime = mergeEnd - mergeStart
print "\nMerge Completed in " + str(mergeTime.seconds) + " second(s)."
# write the term list to a file called lexicon.txt
idx.writeTermListToFile(termList, dfList)

endTime = datetime.datetime.now()
totalTime = endTime - startTime
tripleTime = mergeStart - startTime

if ENV.MEMORY_MAXIMUM:
	print "\n------------\n\nRuntime for memory constraint of " + str(ENV.MEMORY_MAXIMUM) + " triples:"
else:
	print "\n------------\n\nRuntine with no memory maximum."

print tb.tabulate([[str(tripleTime.seconds) + " seconds", str(mergeTime.seconds) + " seconds", str(totalTime.seconds) + " seconds"]], ["Time to build triples", "Time to merge files.", "Total Time"], tablefmt="fancy_grid")

print "\nLexicon and Posting List Statistics for " + ENV.INDEX_TYPE.lower() + " index."
print tb.tabulate([[ENV.INDEX_TYPE.lower(), str(len(termList)), os.path.getsize(ENV.INDEX_LOCATION + "lexicon.txt") + os.path.getsize(ENV.INDEX_LOCATION + "postinglist.txt"), np.max(dfList), np.min(dfList), np.mean(dfList), np.median(dfList)]],["Index Type", "Lexicon (#of terms)", "Index size Lexicon+PL(byte)", "Max df", "Min df", "Mean df", "Median df"], tablefmt="fancy_grid")

print "Indexed " + str(totalDocCount) + " documents"
