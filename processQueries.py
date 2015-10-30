# MAIN FILE:  This is the main entry point for query processing, which defers to other files for functionality.

import sys
import os
import codecs
import re
import datetime
import tabulate as tab
import numpy as np

sys.path.insert(0, 'src')
import docProcessor as dp
import queryProcessor as qp
import utils as util
import settings as ENV
import indexing as idx
import document as d
import tripleBuilder as tb


results = {}
stopTerms = dp.extractStopTerms()

ENV.EXTRACT_PHRASES = True

# load queries into memory as query objects
queryData = dp.extractQueryInformation()
queryTitles = queryData.keys() # gives us each query title

# for each query we have extracted
for query in queryTitles:
# 	# preprocessEachQuery using the same rules relied upon for documents
	query = qp.processQuery(query, stopTerms)
	print query.text


# 	relevantDocs = qp.findRelevantDocuments()
# 	relevanceRanking = rankDocumentRelevance(relevantDocs)
# 	# Calculate benchmarks based on our data
# 	results[query.getId()] = calculateStats(relevanceRanking, annotatedResults)



