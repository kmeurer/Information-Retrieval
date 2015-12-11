import settings as ENV

def expand_query(query_text, relevance_rankings, method='RELEVANCE'):
	# get top terms
	top_doc_entries = [doc[0] for doc in relevance_rankings[0:ENV.REL_NUM_TOP_DOCS]]
	if ENV.REL_SORT_CRITERIA is 'NIDF':
		term_ranking = ENV.primary_index.get_n_idf_ranked_list(top_doc_entries)
	elif ENV.REL_SORT_CRITERIA is 'FIDF':
		term_ranking = ENV.primary_index.get_f_idf_ranked_list(top_doc_entries)
	top_term_ids = [term[1] for term in term_ranking]
	added_count = 0
	for tid in top_term_ids:
		if added_count is ENV.REL_NUM_TOP_TERMS:
			break
		term = ENV.primary_index.get_term_by_term_id(tid)
		if term not in query_text:
			query_text += ' %s' % term
			added_count += 1
	return query_text