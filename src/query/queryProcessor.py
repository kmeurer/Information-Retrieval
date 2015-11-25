import re
import codecs
import os
from object_definitions import query as q
import numpy as np
import utils as util
import settings as ENV
import indexLoader as il
import operator
from query import index as i
from query import vectorSpace as vsm
from query import bm25
from query import languageModel as lang
from indexing import indexing as idx
from object_definitions import document as d


# Pull relevant information from query file, including title, num, and description
def extractQueryInformation():
    queries = {}
    queryFile = codecs.open(ENV.QUERY_SRC, 'rb', 'utf-8')   # specify utf-8 encoding
    currentLine = queryFile.readline()
    currentNum = None
    currentTitle = ''
    count = 0
    while currentLine != '':
        if '<num>' in currentLine:
            count += 1
            numLine = currentLine.split('Number: ')
            currentNum = int(re.sub('\s', '', numLine[1]))
        elif '<title>' in currentLine:
            titleLine = currentLine.split('Topic: ')
            title = titleLine[1].replace('\n', '')
            queries[title] = {}
            queries[title]['number'] = currentNum
            currentTitle = title
        elif '<desc>' in currentLine:
            currentLine = queryFile.readline()
            description = ''
            narrative = ''
            while '<narr>' not in currentLine:
                description += currentLine.replace('\n', ' ')
                currentLine = queryFile.readline()
            currentLine = queryFile.readline()
            while '</top>' not in currentLine:
                narrative += currentLine.replace('\n', ' ')
                currentLine = queryFile.readline()
            queries[currentTitle]['description'] = description
            queries[currentTitle]['narrative'] = narrative
        currentLine = queryFile.readline()
    return queries

def preprocess_query(queryString, stopTerms):
    if queryString.isspace() or queryString == '' :
        return None
    # Convert document to class format
    query = q.Query(queryString)
    # Use the same preprocessing strategy here for consistency
    query.preprocessText(stopTerms)
    # clean up document by eliminating extraneous tokens, except in cases where they fall within brackets {}
    return query

def get_relevant_docs(query):
    rankings = None
    # If we are deferring to a specific index
    if ENV.QUERY_PROCESSING_METHOD == 'STANDARD':
        query.removeStopWords(ENV.STOP_TERMS)
        if ENV.QUERY_PROCESSING_INDEX == 'STEM':
            query.stemTerms()
        if ENV.SIMILARITY_MEASURE == 'BM25':
            rankings = bm25.extract_bm25_scores(query, ENV.primary_index)
        elif ENV.SIMILARITY_MEASURE == 'COSINE':
            rankings = vsm.extract_vector_space_cosine_scores(query, ENV.primary_index)
        elif ENV.SIMILARITY_MEASURE == 'LANGUAGE':
            rankings = lang.extract_language_model_scores(query, ENV.primary_index)
        print "Retrieved %s documents." % (len(rankings))
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
                rankings = bm25.extract_bm25_scores(query, ENV.phrase_index)
            elif ENV.SIMILARITY_MEASURE == 'COSINE':
                rankings = vsm.extract_vector_space_cosine_scores(query, ENV.phrase_index)
            elif ENV.SIMILARITY_MEASURE == 'LANGUAGE':
                rankings = lang.extract_language_model_scores(query, ENV.phrase_index)
        else:
            ENV.QUERY_PROCESSING_INDEX = 'POSITIONAL'
            if ENV.SIMILARITY_MEASURE == 'BM25':
                rankings = bm25.extract_bm25_scores(query, ENV.positional_index)
            elif ENV.SIMILARITY_MEASURE == 'COSINE':
                rankings = vsm.extract_vector_space_cosine_scores(query, ENV.positional_index)
            elif ENV.SIMILARITY_MEASURE == 'LANGUAGE':
                rankings = lang.extract_language_model_scores(query, ENV.positional_index)
        # If we haven't retrieved enough docs to say we're done...
        if len(rankings) <= ENV.MIN_DOCS_RETRIEVED:
            query.removeStopWords(ENV.STOP_TERMS)
            # retrieve more documents using the backup index
            print "\nNot enough documents retrieved for the query: %s.  Needed %d and only retrieved %f." % (queryText, int(ENV.MIN_DOCS_RETRIEVED), int(len(rankings)))
            print  "Proceeding to use %s index to find more relevant docs." % (ENV.BACKUP_INDEX.lower())
            ENV.QUERY_PROCESSING_INDEX = ENV.BACKUP_INDEX
            if ENV.BACKUP_INDEX == 'STEM':
                query.stemTerms()
            if ENV.SIMILARITY_MEASURE == 'BM25':
                rankings = bm25.extract_bm25_scores(query, backup_index)
            elif ENV.SIMILARITY_MEASURE == 'COSINE':
                rankings = vsm.extract_vector_space_cosine_scores(query, backup_index)
            elif ENV.SIMILARITY_MEASURE == 'LANGUAGE':
                rankings = lang.extract_language_model_scores(query, backup_index)
        print "\nRetrieved %s documents." % (len(rankings))
    else:
        raise ValueError("Please enter a valid value for QUERY_PROCESSING_METHOD.  You entered " + ENV.QUERY_PROCESSING_METHOD + ".") 
    return rankings

'''
Query Processing methods that are non-specific to one retrieval method
'''
def calculate_tf_idf(tf, df, collection_size):
    return (np.log(tf) + 1) * calculate_idf(df, collection_size)

def calculate_idf(df, collection_size):
    return np.log(collection_size / df)



