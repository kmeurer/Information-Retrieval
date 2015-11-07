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
def extract_bm25_scores(query, index):
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
        term_df = index.get_df_by_term_id(term_id)
        term_idf = calculate_bm_25_idf(term_df, index.get_collection_size())
        for doc in relevant_posting_entries[term_id]:
            doc_id = doc[0]
            doc_tf = doc[1]
            bm_25_term_weight = calculate_bm_25_entry(term_idf, term_df, q_tid_info_dict[term_id], index.get_document_length(doc_id), index.get_avg_document_length())
            if doc_id in document_weights:
                document_weights[doc_id].append(bm_25_term_weight)
            else:
                document_weights[doc_id] = [bm_25_term_weight]
    final_scores = []
    # for each document, we sum the product of all the weights
    for doc in document_weights:
        final_scores.append([doc, calculate_bm_25(document_weights[doc])])
    final_scores.sort(key=operator.itemgetter(1), reverse=True)
    return final_scores

def calculate_bm_25_idf(df, collection_size):
    return np.log((collection_size - df + .5) / (df + .5))

def calculate_bm_25_entry(idf, dtf, qtf, doc_length, avg_doc_length):
    return idf * ( ( (ENV.BM_25_K1 + 1) * dtf ) / (dtf + ENV.BM_25_K1 * (1 - ENV.BM_25_B + (ENV.BM_25_B * (doc_length / avg_doc_length) ) ) ) ) * ( ( (ENV.BM_25_K1 + 1) * qtf ) / (ENV.BM_25_K1 * qtf) )

def calculate_bm_25(document_weights):
    return np.sum(document_weights)