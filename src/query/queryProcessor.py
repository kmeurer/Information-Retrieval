import re
import codecs
import os
from object_definitions import query as q
import numpy as np
import utils as util
import settings as ENV
import indexLoader as il


# Pull relevant information from query file, including title, num, and description
def extractQueryInformation():
    queries = {}
    queryFile = codecs.open(ENV.QUERY_SRC, 'rb', 'utf-8')   # specify utf-8 encoding
    currentLine = queryFile.readline()
    currentNum = None
    currentTitle = ''
    while currentLine != '':
        if '<num>' in currentLine:
            numLine = currentLine.split('Number: ')
            currentNum = int(re.sub("\s", "", numLine[1]))
        elif '<title>' in currentLine:
            titleLine = currentLine.split('Topic: ')
            title = titleLine[1].replace('\n', '')
            queries[title] = {}
            queries[title]["number"] = currentNum
            currentTitle = title
        elif '<desc>' in currentLine:
            currentLine = queryFile.readline()
            description = ''
            while '<narr>' not in currentLine:
                description += currentLine.replace('\n', ' ')
                currentLine = queryFile.readline()
            queries[currentTitle]["description"] = description
        currentLine = queryFile.readline()
    return queries

def preprocess_query(queryString, stopTerms):
    if queryString.isspace() or queryString == "" :
        return None
    # Convert document to class format
    query = q.Query(queryString)
    # Use the same preprocessing strategy here for consistency
    query.preprocessText(stopTerms)
    # clean up document by eliminating extraneous tokens, except in cases where they fall within brackets {}
    return query

def extract_bm25_scores(query, lexicon, doc_list):
    term_info = query.extractTermInformation()
    lexicon_compressed = [item[1] for item in lexicon]
    term_ids = []
    # find term id for each term
    for term in term_info:
        term_id = lexicon_compressed.index(term)
    # retrieve posting list entries for all term ids
    posting_entries = il.read_posting_entries_to_memory(ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + ENV.POSTING_LIST_NAME + ".txt", term_ids)
    print posting_entries
    return None

def extract_vector_space_scores(query, lexicon, doc_list):
    term_info = query.extractTermInformation()
    lexicon_compressed = [item[1] for item in lexicon]
    term_ids = []
    # find term id for each term
    for term in term_info:
        if term in lexicon_compressed:
            term_ids.append([lexicon_compressed.index(term), term_info[term]])
        else:
            continue
    
    # retrieve posting list entries for all term ids in format:
    # { termId: [[doc1, tf], [doc2, tf]]}
    print term_ids
    relevant_posting_entries = il.read_posting_entries_to_memory(ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + ENV.POSTING_LIST_NAME + ".txt", [tid[0] for tid in term_ids])
    
    # info stored by document in the format:
    # { docID: [ [queryWeight1, termWeight1], [queryWeight2, termWeight2] ] }
    relevance_info = {}
    for i, term_info in enumerate(term_ids):
        term_lexicon_index = term_info[0]
        query_tf = term_info[1]
        term_df = lexicon[term_lexicon_index][2]
        # get the document info for each document that contains the term
        for doc in relevant_posting_entries[term_info[0]]:
            document_tf = doc[1]
            # print doc
            # print document_tf
            added_relevance_info = [calculate_term_weight(query_tf, term_df, len(doc_list)), calculate_term_weight(document_tf, term_df, len(doc_list))]
            if doc[0] in relevance_info:
                relevance_info[doc[0]].append(added_relevance_info)
            else:
                relevance_info[doc[0]] = [ added_relevance_info ]
    finalScores = []
    for docId in relevance_info:
        docScore = calculate_vector_space_cosine(relevance_info[docId])
        # print docScore
        finalScores.append([docId, docScore])
    # print finalScores
    return finalScores

def extract_language_model_scores(query, lexicon, doc_list):
    # term_info = query.extractTermInformation()
    # lexicon_compressed = [item[1] for item in lexicon]
    # term_ids = []
    # # find term id for each term
    # for term in term_info:
    #     term_id = lexicon_compressed.index(term)
    # # retrieve posting list entries for all term ids in format
    # posting_entries = il.read_posting_entries_to_memory(ENV.INDEX_LOCATION + ENV.QUERY_PROCESSING_INDEX.lower() + ENV.POSTING_LIST_NAME + ".txt", term_ids)
    return None

'''
Calculates term weights for 
'''
def calculate_term_weight(tf, df, collection_size):
    return (np.log(tf) + 1) * calculate_idf(df, collection_size)

def calculate_idf(df, collection_size):
    return np.log(collection_size / df)

'''
Calculates vector space cosine.  Given a list of the following: [queryWeight, documentWeights] for each term
'''
def calculate_vector_space_cosine(qw_dw_list):
    numerator_sum = 0.0
    denominator_query_sum = 0.0
    denominator_document_sum = 0.0
    for weight_entry in qw_dw_list:
        numerator_sum += weight_entry[0] * weight_entry[1]
        denominator_document_sum += np.square(weight_entry[1])
        denominator_query_sum += np.square(weight_entry[0])
    print numerator_sum
    print np.sqrt(denominator_document_sum) * np.sqrt(denominator_query_sum)
    return numerator_sum / np.sqrt(denominator_document_sum * denominator_query_sum)

