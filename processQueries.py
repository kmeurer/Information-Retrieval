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
    lexicon_path = ENV.INDEX_LOCATION + "phrase" + "Lexicon.txt"
    doc_list_path = ENV.INDEX_LOCATION + "phrase" + ENV.DOC_FILE_NAME + ".txt"
    posting_list_path = ENV.INDEX_LOCATION + "phrase" + ENV.POSTING_LIST_NAME + ".txt"
    phrase_index = i.Index(lexicon_path, posting_list_path, doc_list_path)

    lexicon_path = ENV.INDEX_LOCATION + "positional" + "Lexicon.txt"
    doc_list_path = ENV.INDEX_LOCATION + "positional" + ENV.DOC_FILE_NAME + ".txt"
    posting_list_path = ENV.INDEX_LOCATION + "positional" + ENV.POSTING_LIST_NAME + ".txt"
    positional_index = i.Index(lexicon_path, posting_list_path, doc_list_path)
else:
    raise ValueError("Please enter a valid value for QUERY_PROCESSING_METHOD.  You entered " + ENV.QUERY_PROCESSING_METHOD + ".")

''' load queries into memory as query objects '''
queryData = qp.extractQueryInformation()
queryTitles = queryData.keys() # gives us each query title
queryScores = {} # stores our similarity scores by query title in format

# for each query we have extracted
for queryText in queryTitles:
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
    elif ENV.QUERY_PROCESSING_METHOD == "CONDITIONAL":
        query_phrases = query.extractValidPhrases(ENV.STOP_TERMS)
        use_phrase = False
        for phrase in query_phrases:
            # if any of our phrases have df above
            if phrase_index.get_df_by_term(phrase) >= ENV.PHRASE_MIN_DF:
                use_phrase = True
        if use_phrase == True:
            ENV.QUERY_PROCESSING_INDEX = 'PHRASE'
            query.removeStopWords(ENV.STOP_TERMS)
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
    else:
        raise ValueError("Please enter a valid value for QUERY_PROCESSING_METHOD.  You entered " + ENV.QUERY_PROCESSING_METHOD + ".") 

# Write to an evaluation file
if ENV.QUERY_PROCESSING_METHOD == 'STANDARD':
    file_name = ENV.TRECEVAL_SRC + ENV.QUERY_PROCESSING_METHOD.lower() + '_' + ENV.QUERY_PROCESSING_INDEX.lower() + '_' +ENV.SIMILARITY_MEASURE.lower() + '.txt'
else:
    file_name = ENV.TRECEVAL_SRC + ENV.QUERY_PROCESSING_METHOD.lower() + '_' + ENV.SIMILARITY_MEASURE.lower() + '.txt'
eval_file = codecs.open(file_name, 'w', 'utf-8')
for qt in queryData:
    for idx, ranked_query in enumerate(queryData[qt]['rankings'][0:100]):
        eval_file.write(str(queryData[qt]['number']) + ' 0 ' + util.convert_num_id_to_trek_id(ranked_query[0]) + ' ' + str(idx + 1) + ' ' + str(ranked_query[1]) + ' ' + ENV.SIMILARITY_MEASURE + '\n')

eval_file.close()

end_time = datetime.datetime.now()

total_time = end_time - start_time
print '\n\nRANKED ' + str(len(queryTitles)) + ' QUERIES IN ' + str(total_time.seconds) + ' SECONDS.'


