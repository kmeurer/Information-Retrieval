# MAIN FILE:  This is the main entry point for the project, which defers to other files for functionality.

import sys
import os
import codecs
import re
import datetime
import tabulate as tab
import numpy as np

sys.path.insert(0, 'src')
import docProcessor as dp
import utils as util
import settings as ENV
import indexing as idx
import document as d
import tripleBuilder as tb

termList = []
dfList = []
tripleList = []
stopTerms = dp.extractStopTerms()
if ENV.BUILD_ALL_INDEXES == True:
	indexTypes = ["INVERTED", "POSITIONAL", "STEM", "PHRASE"]
else:
	indexTypes = [ENV.INDEX_TYPE]

runStats = {}
timeStats = {}


# Empty our index folder
indexFiles = os.listdir(ENV.INDEX_LOCATION)
for f in indexFiles:
    os.remove(ENV.INDEX_LOCATION + f)

# For every index type we wish to create...
for idxType in indexTypes:
	startTime = datetime.datetime.now()	# record start time
	ENV.INDEX_TYPE = idxType
	print "\n------------\nBuilding " + idxType.lower() + " index:"
	termList[:] = []		# able to be stored in memory
	dfList[:] = []			# companion to term list of df
	tripleList[:] = []		# max length specified by memory constrain specified in settings.py

	totalDocCount = 0 # for counting processed documents
	# for each file in the specified directory, extract and index documents
	for filename in os.listdir(ENV.DOCUMENT_SRC):
		fileSrc = ENV.DOCUMENT_SRC + filename # set the file source
		print "\n------------\nProcessing documents included in " + fileSrc + "\n"
		dataFile = codecs.open(fileSrc, 'rb', 'utf-8') 	# open our data file
		currentLine = dataFile.readline()
		count = 1
		# while there is still information left in the file...
		while currentLine != '':
			# test if we have found a document
			if '<DOC>' in currentLine:
				sys.stdout.write("Processed " + str(count) + " documents...\r")
				count += 1
				totalDocCount += 1
				docStr = ""
				currentLine = dataFile.readline()
				# terminate when we reach the closing tag
				while '</DOC>' not in currentLine:
					docStr += currentLine
					currentLine = dataFile.readline()
				# MAIN ENTRY POINT FOR PREPROCESSING
				doc = dp.processDocument(docStr)
				# MAIN ENTRY POINT FOR INDEXING
				idx.indexDocument(doc, termList, dfList, tripleList, stopTerms)
			currentLine = dataFile.readline()

	# write remaining triples to a file
	tb.writeTriplesToFile(tripleList)
	print "\n------------\n\nTemporary Triples Built.  Beginning Merge...\n"
	mergeStart = datetime.datetime.now()
	# merge our remaining temporary files
	tb.mergeTempFiles()
	# convert our triples to a posting list
	tb.convertTriplesToPostings(ENV.INDEX_LOCATION + ENV.INDEX_TYPE.lower() + ENV.TRIPLE_LIST_NAME + '.txt', ENV.INDEX_LOCATION + ENV.INDEX_TYPE.lower() + ENV.POSTING_LIST_NAME + '.txt')
	mergeEnd = datetime.datetime.now()
	mergeTime = mergeEnd - mergeStart
	print "\nMerge Completed in " + str(mergeTime.seconds) + " second(s)."
	# delete triple list unless keep triples list is set to true
	if ENV.KEEP_TRIPLES_LIST != True:
		os.remove(ENV.INDEX_LOCATION + ENV.INDEX_TYPE.lower() + ENV.TRIPLE_LIST_NAME + '.txt')
	# write the term list to a file called lexicon.txt
	idx.writeTermListToFile(termList, dfList)

	endTime = datetime.datetime.now()
	totalTime = endTime - startTime
	tripleTime = mergeStart - startTime

	if ENV.MEMORY_MAXIMUM:
		print "\n------------\n\nRuntime for memory constraint of " + str(ENV.MEMORY_MAXIMUM) + " triples:"
	else:
		print "\n------------\n\nRuntine with no memory maximum."

	print tab.tabulate([[str(tripleTime.seconds) + " seconds", str(mergeTime.seconds) + " seconds", str(totalTime.seconds) + " seconds"]], ["Time to build triples", "Time to merge files.", "Total Time"], tablefmt="fancy_grid")
	print "\nLexicon and Posting List Statistics for " + ENV.INDEX_TYPE.lower() + " index."
	print tab.tabulate([[ENV.INDEX_TYPE.lower(), str(len(termList)), os.path.getsize(ENV.INDEX_LOCATION + ENV.INDEX_TYPE.lower() + "lexicon.txt") + os.path.getsize(ENV.INDEX_LOCATION + ENV.INDEX_TYPE.lower() + "postinglist.txt"), np.max(dfList), np.min(dfList), np.mean(dfList), np.median(dfList)]],["Index Type", "Lexicon (#of terms)", "Index size Lexicon+PL(byte)", "Max df", "Min df", "Mean df", "Median df"], tablefmt="fancy_grid")
	
	runStats[ENV.INDEX_TYPE] = [ENV.INDEX_TYPE.lower(), str(len(termList)), os.path.getsize(ENV.INDEX_LOCATION + ENV.INDEX_TYPE.lower() + "lexicon.txt") + os.path.getsize(ENV.INDEX_LOCATION + ENV.INDEX_TYPE.lower() + "postinglist.txt"), np.max(dfList), np.min(dfList), np.mean(dfList), np.median(dfList)]
	timeStats[ENV.INDEX_TYPE] = [ENV.INDEX_TYPE.lower(), str(tripleTime.seconds) + " seconds", str(mergeTime.seconds) + " seconds", str(totalTime.seconds) + " seconds"]
	
	print "Indexed " + str(totalDocCount) + " documents"

# Generate statistics for runtime and document frequencies
runTimes = []
for type in timeStats:
	runTimes.append(timeStats[type])
dfStats = []
for type in runStats:
	dfStats.append(runStats[type])

print "\n------------\n\nTotal runtime stats by index.  All results for a memory maximum of " + str(ENV.MEMORY_MAXIMUM) + "."
print tab.tabulate(runTimes, ["Index Type", "Time to build triples", "Time to merge files.", "Total Time"], tablefmt="fancy_grid")
print "Total Document Frequency (df) stats across indexes generated.  Memory Maximum: " + str(ENV.MEMORY_MAXIMUM) + "."
print tab.tabulate(dfStats,["Index Type", "Lexicon (#of terms)", "Index size Lexicon+PL(byte)", "Max df", "Min df", "Mean df", "Median df"], tablefmt="fancy_grid")
