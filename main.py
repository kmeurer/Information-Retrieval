import sys
import os
import re
import glob
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
	# idx.mergeTempFiles()

endTime = datetime.datetime.now()
timeSpent = endTime - startTime

print "PROGRAM COMPLETED IN " + str(timeSpent.seconds) + " SECONDS\n\n\n--------------------------\n\n\n"