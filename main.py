import sys
import os
sys.path.insert(0, 'src')

import docProcessor as dp
import utils as util
import settings as ENV
import datetime

startTime = datetime.datetime.now()

docFileNames = []
stopTerms = dp.extractStopTerms()
for filename in os.listdir(ENV.DOCUMENT_SRC):
	documentDictionary = dp.extractDocuments(ENV.DOCUMENT_SRC + filename) # Extract information from our files.

endTime = datetime.datetime.now()
timeSpent = endTime - startTime

print "PROGRAM COMPLETED IN " + str(timeSpent.seconds) + " SECONDS\n\n\n--------------------------\n\n\n"