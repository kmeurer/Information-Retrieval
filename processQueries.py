# MAIN FILE:  This is the main entry point for query processing, which defers to other files for functionality.
import sys
import os
import codecs
import re
import datetime
import tabulate as tab
import numpy as np
import settings as ENV

sys.path.insert(0, 'src')
import utils as util
from query import queryProcessor as qp
from query import index as i
from indexing import indexing as idx
from object_definitions import document as d

results = {}
stopTerms = util.extractStopTerms()

# we always want to extract phrases for the lexicon
ENV.EXTRACT_PHRASES = True

''' LOAD NECESSARY INDEXES '''
if ENV.QUERY_PROCESSING_METHOD == "STANDARD":
    lexicon_path = ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + "Lexicon.txt"
    doc_list_path = ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + ENV.DOC_FILE_NAME + ".txt"
    posting_list_path = ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + ENV.POSTING_LIST_NAME + ".txt"
    primary_index = i.Index(lexicon_path, posting_list_path, doc_list_path)
# if the index we use is query dependent
elif ENV.QUERY_PROCESSING_METHOD == "CONDITIONAL":
    stemLexicon = il.read_lexicon_to_memory()
else:
    raise ValueError("Please enter a valid value for QUERY_PROCESSING_METHOD.  You entered " + ENV.QUERY_PROCESSING_METHOD + ".")

''' load queries into memory as query objects '''
queryData = qp.extractQueryInformation()
queryTitles = queryData.keys() # gives us each query title
queryScores = {} # stores our similarity scores by query title in format

# for each query we have extracted
for queryText in queryTitles:
    # preprocessEachQuery using the same rules relied upon for documents
    query = qp.preprocess_query(queryText, stopTerms)
    # If we are deferring to a specific index
    if ENV.QUERY_PROCESSING_METHOD == "STANDARD":
        if ENV.QUERY_PROCESSING_INDEX == "INVERTED":
            query.removeStopWords(stopTerms)
            if ENV.SIMILARITY_MEASURE == "BM25":
                queryScores[queryText] = qp.extract_bm25_scores(query, lexicon, doc_list)
            elif ENV.SIMILARITY_MEASURE == "VECTOR":
                queryScores[queryText] = qp.extract_vector_space_scores(query, lexicon, doc_list)
            elif ENV.SIMILARITY_MEASURE == "LANGUAGE":
                queryScores[queryText] = qp.extract_language_model_scores(query, lexicon, doc_list)


#   relevantDocs = qp.findRelevantDocuments()
#   relevanceRanking = rankDocumentRelevance(relevantDocs)
#   # Calculate benchmarks based on our data
#   results[query.getId()] = calculateStats(relevanceRanking, annotatedResults)



