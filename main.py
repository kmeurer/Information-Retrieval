import sys
import os
import re
sys.path.insert(0, 'src')

import docProcessor as dp
import utils as util
import settings as ENV
import datetime
import indexing as idx

startTime = datetime.datetime.now()

docFileNames = []
stopTerms = dp.extractStopTerms()
termList = []
indexFiles = os.listdir(ENV.INDEX_LOCATION)
for f in indexFiles:
    os.remove(ENV.INDEX_LOCATION + f)

for filename in os.listdir(ENV.DOCUMENT_SRC):
	fileText = dp.extractDocuments(ENV.DOCUMENT_SRC + filename) # Extract information from our files.
	# split into distinct documents
	documentStrArray = re.split('</DOC>', fileText)
	idx.buildTempFiles(documentStrArray, stopTerms, termList)

idx.mergeTempFiles()
idx.writeTermListToFile(termList)
idx.convertTriplesToPostings(ENV.INDEX_LOCATION + ENV.TRIPLE_LIST_NAME + '.txt', ENV.INDEX_LOCATION + ENV.POSTING_LIST_NAME + '.txt')

endTime = datetime.datetime.now()
timeSpent = endTime - startTime

print 'PROGRAM COMPLETED IN ' + str(timeSpent.seconds) + ' SECONDS\n\n\n--------------------------\n\n\n'