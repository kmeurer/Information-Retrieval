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
    if ENV.QUERY_PROCESSING_METHOD == 'STANDARD':
        query.removeStopWords(stopTerms)
        if ENV.QUERY_PROCESSING_INDEX == 'STEM':
            query.stemTerms()
        if ENV.SIMILARITY_MEASURE == 'BM25':
            queryData[queryText] = qp.extract_bm25_scores(query, lexicon, doc_list)
        elif ENV.SIMILARITY_MEASURE == 'VECTOR':
            queryData[queryText]['rankings'] = qp.extract_vector_space_scores(query, primary_index)
        elif ENV.SIMILARITY_MEASURE == 'LANGUAGE':
            queryData[queryText] = qp.extract_language_model_scores(query, lexicon, doc_list)

# Write to an evaluation file
eval_file = codecs.open(ENV.TRECEVAL_SRC + ENV.QUERY_PROCESSING_INDEX.lower() + ENV.SIMILARITY_MEASURE.lower() + '.txt', 'w', 'utf-8')
for qt in queryData:
    for idx, ranked_query in enumerate(queryData[qt]['rankings'][0:100]):
        eval_file.write(str(queryData[qt]['number']) + ' 0 ' + util.convert_num_id_to_trek_id(ranked_query[0]) + ' ' + str(idx + 1) + ' ' + ENV.SIMILARITY_MEASURE.lower() + '\n')

eval_file.close()



#   relevantDocs = qp.findRelevantDocuments()
#   relevanceRanking = rankDocumentRelevance(relevantDocs)
#   # Calculate benchmarks based on our data
#   results[query.getId()] = calculateStats(relevanceRanking, annotatedResults)



