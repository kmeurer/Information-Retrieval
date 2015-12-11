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
from query import queryReducer as q_red
from query import queryExpander as q_exp
from indexing import indexing as idx
from object_definitions import document as d
from object_definitions.query import Query

start_time = datetime.datetime.now()

ENV.STOP_TERMS = util.extractStopTerms()

# we always want to extract phrases for the lexicon
ENV.EXTRACT_PHRASES = True

''' LOAD NECESSARY INDEXES '''
if ENV.QUERY_PROCESSING_METHOD == "STANDARD":
    lexicon_path = ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + "Lexicon.txt"
    doc_list_path = ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + ENV.DOC_FILE_NAME + ".txt"
    posting_list_path = ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + ENV.POSTING_LIST_NAME + ".txt"
    ENV.primary_index = i.Index(lexicon_path, posting_list_path, doc_list_path)
# if the index we use is query dependent
elif ENV.QUERY_PROCESSING_METHOD == "CONDITIONAL":
    ENV.QUERY_PROCESSING_INDEX = "PHRASE"
    lexicon_path = ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + "Lexicon.txt"
    doc_list_path = ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + ENV.DOC_FILE_NAME + ".txt"
    posting_list_path = ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + ENV.POSTING_LIST_NAME + ".txt"
    ENV.phrase_index = i.Index(lexicon_path, posting_list_path, doc_list_path)

    ENV.QUERY_PROCESSING_INDEX = "POSITIONAL"
    lexicon_path = ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + "Lexicon.txt"
    doc_list_path = ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + ENV.DOC_FILE_NAME + ".txt"
    posting_list_path = ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + ENV.POSTING_LIST_NAME + ".txt"
    ENV.positional_index = i.Index(lexicon_path, posting_list_path, doc_list_path)

    ENV.QUERY_PROCESSING_INDEX = "STEM"
    lexicon_path = ENV.INDEX_LOCATION + ENV.BACKUP_INDEX.lower() + "Lexicon.txt"
    doc_list_path = ENV.INDEX_LOCATION + ENV.BACKUP_INDEX.lower() + ENV.DOC_FILE_NAME + ".txt"
    posting_list_path = ENV.INDEX_LOCATION + ENV.BACKUP_INDEX.lower() + ENV.POSTING_LIST_NAME + ".txt"
    ENV.backup_index = i.Index(lexicon_path, posting_list_path, doc_list_path)
else:
    raise ValueError("Please enter a valid value for QUERY_PROCESSING_METHOD.  You entered %s." % (ENV.QUERY_PROCESSING_METHOD))

''' QUERY LOADING '''
query_data = qp.extractQueryInformation()
query_scores = {} # stores our similarity scores by query
if ENV.QUERY_TYPE is "TITLE":
    queries = query_data.keys() # gives us each query title
    query_scores = query_data
elif ENV.QUERY_TYPE is "NARRATIVE":
    query_titles = query_data.keys()
    queries = []
    # change our keys so that the narrative (the query) becomes the key and the title becomes a value
    for q in query_data:
        queries.append(query_data[q]['narrative'])
        query_scores[query_data[q]['narrative']] = {}
        for key in query_data[q]:
            if key is 'narrative':
                continue
            query_scores[query_data[q]['narrative']][key] = query_data[q][key]
        query_scores[query_data[q]['narrative']]['title'] = q
else:
    raise ValueError("Please enter a valid value for QUERY_TYPE.  You entered %s." % (ENV.QUERY_TYPE))
    
''' OPTIONAL QUERY REDUCTION '''
if ENV.USE_QUERY_REDUCTION is True and ENV.QUERY_TYPE is 'NARRATIVE':
    print "\n---\n\nReducing query using Query thresholding: "
    for idx, query_text in enumerate(queries):
        query = qp.preprocess_query(query_text, ENV.STOP_TERMS)
        top_terms = query.get_ranked_terms()
        expanding_query = Query(top_terms[0])
        for term in top_terms:
            rel_docs = qp.get_relevant_docs(expanding_query)
            if len(rel_docs) > ENV.QUERY_THRESHOLD_DOCS_RETRIEVED:
                print '\nReduced initial query to \"%s\".  Stopped processing as %d docs were retrieved.\n_________\n' % (expanding_query.text, len(rel_docs))
                queries[idx] = query.text
                if query_text in query_scores:
                    query_scores[queries[idx]] = query_scores.pop(query_text)
                query_scores[queries[idx]]['rankings'] = rel_docs  
                break
            elif term not in expanding_query.text:
                expanding_query.addText(term)
            else:
                continue        
else:
    ''' QUERY PRIMARY PROCESSING '''
    print '\n\n---BEGINNING QUERY PROCESSING---'
    # for each query we have extracted
    for idx, query_text in enumerate(queries):
        print "\n---\n\nProcessing query: " + query_text
        # preprocess each query using the same rules relied upon for documents
        query = qp.preprocess_query(query_text, ENV.STOP_TERMS)
        queries[idx] = query.text
        if query_text in query_scores:
            query_scores[queries[idx]] = query_scores.pop(query_text)
        query_scores[queries[idx]]['rankings'] = qp.get_relevant_docs(query)    

''' OPTIONAL QUERY EXPANSION '''
if ENV.QUERY_TYPE is 'TITLE' and ENV.USE_QUERY_EXPANSION == True:
    if ENV.QUERY_EXPANSION_METHOD == 'RELEVANCE':
        print "\n---\n\nExpanding query using relevance feedback: "
        for idx, query_text in enumerate(queries):
            queries[idx] = q_exp.expand_query(query_text, query_scores[query_text]['rankings'])
            query_scores[queries[idx]] = query_scores.pop(query_text)
            print "Expanded \"%s\" to \"%s\"" % (query_text, queries[idx])
    elif ENV.QUERY_EXPANSION_METHOD == 'THESAURI':
        print "\n---\n\nExpanding query using thesaurus: "
        for idx, query_text in enumerate(queries):
            queries[idx] = q_exp.expand_query(query_text, query_scores[query_text]['rankings'], 'THESAURI')
            query_scores[queries[idx]] = query_scores.pop(query_text)
            print "Expanded \"%s\" to \"%s\"" % (query_text, queries[idx])
    else:
        raise ValueError("Please enter a valid value for QUERY_EXPANSION_METHOD.  You entered " + ENV.QUERY_EXPANSION_METHOD + ".") 
    ''' rerank docs '''
    for queryText in queries:
        print "\n---\n\nProcessing query: " + queryText
        # preprocessEachQuery using the same rules relied upon for documents
        query = qp.preprocess_query(queryText, ENV.STOP_TERMS)
        query_scores[queryText]['rankings'] = qp.get_relevant_docs(query)

''' EVAL FILE WRITE '''
if ENV.QUERY_PROCESSING_METHOD == 'STANDARD':
    file_name = '%s%s_%s_%s.txt' % (ENV.TRECEVAL_SRC, ENV.QUERY_PROCESSING_METHOD.lower(), ENV.QUERY_PROCESSING_INDEX.lower(), ENV.SIMILARITY_MEASURE.lower())
else:
    file_name = '%s%s_%s_%s.txt' % (ENV.TRECEVAL_SRC, ENV.QUERY_PROCESSING_METHOD.lower(), ENV.BACKUP_INDEX.lower(), ENV.SIMILARITY_MEASURE.lower())
eval_file = codecs.open(file_name, 'w', 'utf-8')
for qt in query_scores:
    for idx, ranked_query in enumerate(query_scores[qt]['rankings'][0:100]):
        file_entry = '%d 0 %s %d %f %s\n' % (query_scores[qt]['number'], util.convert_num_id_to_trek_id(ranked_query[0]), idx + 1, ranked_query[1], ENV.SIMILARITY_MEASURE)
        eval_file.write(file_entry)

eval_file.close()

end_time = datetime.datetime.now()

total_time = end_time - start_time
print '\n\nRANKED %s QUERIES IN %d SECONDS.' % (len(queries), total_time.seconds)

