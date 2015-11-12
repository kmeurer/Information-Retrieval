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
from query import vectorSpace as vsm
from query import bm25
from query import languageModel as lang
from indexing import indexing as idx
from object_definitions import document as d


start_time = datetime.datetime.now()

ENV.STOP_TERMS = util.extractStopTerms()

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
    ENV.QUERY_PROCESSING_INDEX = "PHRASE"
    lexicon_path = ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + "Lexicon.txt"
    doc_list_path = ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + ENV.DOC_FILE_NAME + ".txt"
    posting_list_path = ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + ENV.POSTING_LIST_NAME + ".txt"
    phrase_index = i.Index(lexicon_path, posting_list_path, doc_list_path)

    ENV.QUERY_PROCESSING_INDEX = "POSITIONAL"
    lexicon_path = ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + "Lexicon.txt"
    doc_list_path = ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + ENV.DOC_FILE_NAME + ".txt"
    posting_list_path = ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + ENV.POSTING_LIST_NAME + ".txt"
    positional_index = i.Index(lexicon_path, posting_list_path, doc_list_path)

    ENV.QUERY_PROCESSING_INDEX = "STEM"
    lexicon_path = ENV.INDEX_LOCATION + ENV.BACKUP_INDEX.lower() + "Lexicon.txt"
    doc_list_path = ENV.INDEX_LOCATION + ENV.BACKUP_INDEX.lower() + ENV.DOC_FILE_NAME + ".txt"
    posting_list_path = ENV.INDEX_LOCATION + ENV.BACKUP_INDEX.lower() + ENV.POSTING_LIST_NAME + ".txt"
    backup_index = i.Index(lexicon_path, posting_list_path, doc_list_path)
else:
    raise ValueError("Please enter a valid value for QUERY_PROCESSING_METHOD.  You entered %s." % (ENV.QUERY_PROCESSING_METHOD))

''' load queries into memory as query objects '''
queryData = qp.extractQueryInformation()
queryTitles = queryData.keys() # gives us each query title
queryScores = {} # stores our similarity scores by query title in format

print '\n\n---BEGINNING QUERY PROCESSING---'
# for each query we have extracted
for queryText in queryTitles:
    print "\n---\n\nProcessing query: " + queryText
    # preprocessEachQuery using the same rules relied upon for documents
    query = qp.preprocess_query(queryText, ENV.STOP_TERMS)
    # If we are deferring to a specific index
    if ENV.QUERY_PROCESSING_METHOD == 'STANDARD':
        query.removeStopWords(ENV.STOP_TERMS)
        if ENV.QUERY_PROCESSING_INDEX == 'STEM':
            query.stemTerms()
        if ENV.SIMILARITY_MEASURE == 'BM25':
            queryData[queryText]['rankings'] = bm25.extract_bm25_scores(query, primary_index)
        elif ENV.SIMILARITY_MEASURE == 'COSINE':
            queryData[queryText]['rankings'] = vsm.extract_vector_space_cosine_scores(query, primary_index)
        elif ENV.SIMILARITY_MEASURE == 'LANGUAGE':
            queryData[queryText]['rankings'] = lang.extract_language_model_scores(query, primary_index)
        print "Retrieved %s documents." % (len(queryData[queryText]['rankings']))
    elif ENV.QUERY_PROCESSING_METHOD == "CONDITIONAL":
        query_phrases = query.extractValidPhrases(ENV.STOP_TERMS)
        use_phrase = False
        for phrase in query_phrases:
            # if any of our phrases have df above
            if phrase_index.get_df_by_term(phrase) >= ENV.PHRASE_MIN_DF:
                use_phrase = True
        if use_phrase == True:
            ENV.QUERY_PROCESSING_INDEX = 'PHRASE'
            if ENV.SIMILARITY_MEASURE == 'BM25':
                queryData[queryText]['rankings'] = bm25.extract_bm25_scores(query, phrase_index)
            elif ENV.SIMILARITY_MEASURE == 'COSINE':
                queryData[queryText]['rankings'] = vsm.extract_vector_space_cosine_scores(query, phrase_index)
            elif ENV.SIMILARITY_MEASURE == 'LANGUAGE':
                queryData[queryText]['rankings'] = lang.extract_language_model_scores(query, phrase_index)
        else:
            ENV.QUERY_PROCESSING_INDEX = 'POSITIONAL'
            if ENV.SIMILARITY_MEASURE == 'BM25':
                queryData[queryText]['rankings'] = bm25.extract_bm25_scores(query, positional_index)
            elif ENV.SIMILARITY_MEASURE == 'COSINE':
                queryData[queryText]['rankings'] = vsm.extract_vector_space_cosine_scores(query, positional_index)
            elif ENV.SIMILARITY_MEASURE == 'LANGUAGE':
                queryData[queryText]['rankings'] = lang.extract_language_model_scores(query, positional_index)
        # If we haven't retrieved enough docs to say we're done...
        if len(queryData[queryText]['rankings']) <= ENV.MIN_DOCS_RETRIEVED:
            query.removeStopWords(ENV.STOP_TERMS)
            # retrieve more documents using the backup index
            print "\nNot enough documents retrieved for the query: %s.  Needed %d and only retrieved %f." % (queryText, int(ENV.MIN_DOCS_RETRIEVED), int(len(queryData[queryText]['rankings'])))
            print  "Proceeding to use %s index to find more relevant docs." % (ENV.BACKUP_INDEX.lower())
            ENV.QUERY_PROCESSING_INDEX = ENV.BACKUP_INDEX
            if ENV.BACKUP_INDEX == 'STEM':
                query.stemTerms()
            if ENV.SIMILARITY_MEASURE == 'BM25':
                queryData[queryText]['rankings'] = bm25.extract_bm25_scores(query, backup_index)
            elif ENV.SIMILARITY_MEASURE == 'COSINE':
                queryData[queryText]['rankings'] = vsm.extract_vector_space_cosine_scores(query, backup_index)
            elif ENV.SIMILARITY_MEASURE == 'LANGUAGE':
                queryData[queryText]['rankings'] = lang.extract_language_model_scores(query, backup_index)
        print "\nRetrieved %s documents." % (len(queryData[queryText]['rankings']))
    else:
        raise ValueError("Please enter a valid value for QUERY_PROCESSING_METHOD.  You entered " + ENV.QUERY_PROCESSING_METHOD + ".") 

# Write to an evaluation file
if ENV.QUERY_PROCESSING_METHOD == 'STANDARD':
    file_name = '%s%s_%s_%s.txt' % (ENV.TRECEVAL_SRC, ENV.QUERY_PROCESSING_METHOD.lower(), ENV.QUERY_PROCESSING_INDEX.lower(), ENV.SIMILARITY_MEASURE.lower())
else:
    file_name = '%s%s_%s_%s.txt' % (ENV.TRECEVAL_SRC, ENV.QUERY_PROCESSING_METHOD.lower(), ENV.BACKUP_INDEX.lower(), ENV.SIMILARITY_MEASURE.lower())
eval_file = codecs.open(file_name, 'w', 'utf-8')
for qt in queryData:
    for idx, ranked_query in enumerate(queryData[qt]['rankings'][0:100]):
        file_entry = '%d 0 %s %d %f %s\n' % (queryData[qt]['number'], util.convert_num_id_to_trek_id(ranked_query[0]), idx + 1, ranked_query[1], ENV.SIMILARITY_MEASURE)
        eval_file.write(file_entry)

eval_file.close()

print primary_index.get_avg_document_length()

end_time = datetime.datetime.now()

total_time = end_time - start_time
print '\n\nRANKED %s QUERIES IN %d SECONDS.' % (len(queryTitles), total_time.seconds)


