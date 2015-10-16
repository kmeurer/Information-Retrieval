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
# load queries into memory as query objects
queryData = dp.extractQueryInformation()
queryList = dp.extractQueries(queryData)

# for each query we have extracted
for query in queryList:
	# preprocessEachQuery using the same rules relied upon for documents
	dp.preprocessQuery(query)

	relevantDocs = qp.findRelevantDocuments()
	relevanceRanking = rankDocumentRelevance(relevantDocs)
	# Calculate benchmarks based on our data
	results[query.getId()] = calculateStats(relevanceRanking, annotatedResults)



