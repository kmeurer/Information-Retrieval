import numpy as np
import utils as util
import settings as ENV
import operator
import queryProcessor as qp

'''
    Given a query and an index object (specified in index.py), return a score list by document

    Returns
    -------
    list of documents and their scores
      [ [documentID, docScore], [documentID, docScore]]
'''
def extract_vector_space_cosine_scores(query, index):
    # get terms and term frequencies from the query in format {term: tf}
    if ENV.QUERY_PROCESSING_INDEX == 'PHRASE':
        q_term_info_dict = query.extractValidPhrases(ENV.STOP_TERMS)
    else:
        q_term_info_dict = query.extractTermInformation()
    q_tid_info_dict = {}
    for term_name in q_term_info_dict:
        tid = index.get_term_id_by_term(term_name)
        if tid != None:
            q_tid_info_dict[tid] = q_term_info_dict[term_name]
    
    # retrieve posting list entries for all term ids in format:
    # { termId: [[doc1, tf], [doc2, tf]]}
    relevant_posting_entries = index.get_posting_entries_by_terms(q_term_info_dict.keys())

    # calculate aggregate query term weight summation (for use in query weight function)
    query_total_summation = 0.0
    for term_id in relevant_posting_entries:
        query_total_summation += np.square(qp.calculate_tf_idf(q_tid_info_dict[term_id], index.get_df_by_term_id(term_id), index.get_collection_size()))
    
    document_weights = {}
    for term_id in relevant_posting_entries:
        term_df = index.get_df_by_term_id(term_id)
        query_term_weight = calculate_term_weight(q_tid_info_dict[term_id], term_df, index.get_collection_size(), query_total_summation)
        for doc in relevant_posting_entries[term_id]:
            doc_id = doc[0]
            doc_tf = doc[1]
            document_term_weight = calculate_term_weight(doc_tf, term_df, index.get_collection_size(), index.get_document_weight_summation(doc_id))
            if doc_id in document_weights:
                document_weights[doc_id].append([query_term_weight, document_term_weight])
            else:
                document_weights[doc_id] = [[query_term_weight, document_term_weight]]
    final_scores = []
    # for each document, we sum the product of all the weights
    for doc in document_weights:
        final_scores.append([doc, calculate_vector_space_cosine(document_weights[doc], index.get_document_weight_summation2(doc))])
    final_scores.sort(key=operator.itemgetter(1), reverse=True)
    return final_scores

'''
Calculates vector space cosine.  Given a list of the following: [queryWeight, documentWeights] for each term
'''
def calculate_vector_space_cosine(qw_dw_list, document_tf_idf_summation):
    numerator_sum = 0.0
    denominator_query_sum = 0.0
    denominator_document_sum = document_tf_idf_summation
    for weight_entry in qw_dw_list:
        numerator_sum += weight_entry[0] * weight_entry[1]
        denominator_query_sum += np.square(weight_entry[0])
    return numerator_sum / np.sqrt(denominator_document_sum * denominator_query_sum)

def calculate_term_weight(tf, df, collection_size, document_tf_idf_summation):
    return qp.calculate_tf_idf(tf, df, collection_size) / document_tf_idf_summation
