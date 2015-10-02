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

for filename in os.listdir(ENV.DOCUMENT_SRC):
	fileText = dp.extractDocuments(ENV.DOCUMENT_SRC + filename) # Extract information from our files.
	# split into distinct documents
	documentStrArray = re.split('</DOC>', fileText)
	idx.indexDocuments(documentStrArray, stopTerms)

endTime = datetime.datetime.now()
timeSpent = endTime - startTime

print "PROGRAM COMPLETED IN " + str(timeSpent.seconds) + " SECONDS\n\n\n--------------------------\n\n\n"