import re
import codecs
import os
from object_definitions import query as q
import numpy as np
import utils as util
import settings as ENV
import operator

'''
    Given a query and an index object (specified in index.py), return a score list by document

    Returns
    -------
    list of documents and their scores
      [ [documentID, docScore], [documentID, docScore]]
'''
def extract_language_model_scores(query, index):
    # Make sure our u value is set correctly according to the settings
    if ENV.USE_AVG_DOC_LENGTH_FOR_LANG_U == True:
        ENV.LANG_U = index.get_avg_document_length()
    # get terms and term frequencies from the query in format {term: tf}
    q_term_info_dict = query.extractTermInformation()
    q_tid_info_dict = {}
    for term_name in q_term_info_dict:
        tid = index.get_term_id_by_term(term_name)
        if tid != None:
            q_tid_info_dict[tid] = q_term_info_dict[term_name]
    
    # retrieve posting list entries for all term ids in format:
    # { termId: [[doc1, tf], [doc2, tf]]}
    relevant_posting_entries = index.get_posting_entries_by_terms(q_term_info_dict.keys())
    
    document_weights = {}
    for term_id in relevant_posting_entries:
        collection_term_frequency = 0
        # run through the term's docs once to get the collection term frequency
        for doc_entry in relevant_posting_entries[term_id]:
            collection_term_frequency += doc_entry[1]
        # run through the term's docs once more to actually calculate our values
        for doc in relevant_posting_entries[term_id]:
            doc_id = doc[0]
            doc_tf = doc[1]
            dirichlet_entry = calculate_dirichlet_entry(doc_tf, collection_term_frequency, index.get_collection_length(), index.get_document_length(doc_id))
            if doc_id in document_weights:
                document_weights[doc_id].append(dirichlet_entry)
            else:
                document_weights[doc_id] = [dirichlet_entry]
    final_scores = []
    # for each document, we sum the product of all the weights
    for doc in document_weights:
        final_scores.append([doc, calculate_query_likelihood(document_weights[doc])])
    final_scores.sort(key=operator.itemgetter(1), reverse=True)
    return final_scores

def calculate_dirichlet_entry(dtf, ctf, collection_length, doc_length):
    return (dtf + (ENV.LANG_U * (ctf / collection_length)) ) / (doc_length + ENV.LANG_U)

def calculate_query_likelihood(dirichlet_entries):
    return np.sum(dirichlet_entries)

