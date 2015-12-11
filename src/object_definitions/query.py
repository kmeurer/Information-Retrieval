from textobject import TextObject
import numpy as np
import settings as ENV

'''
Query Object.  Information specific to queries.  Inherits all properties from TextObject
'''
class Query(TextObject):
    def __init__(self, text):
        super(Query, self).__init__(text)

    def preprocessText(self, stopTerms):
        super(Query, self).preprocessText()
        self.extractValidPhrases(stopTerms)
        # Now that we have our phrase information, we can clean our tokens
        self.cleanTokens()

    def get_ranked_terms(self):
    	idf_term_list = []
    	for term in self.tokens:
    		# skip terms that aren't in any docs
    		if ENV.primary_index.get_df_by_term(term) is 0:
    			continue
    		idf_term_list.append([np.log(ENV.primary_index.get_collection_size() / ENV.primary_index.get_df_by_term(term)), term])
    	idf_term_list.sort(reverse=True)
    	return [term[1] for term in idf_term_list]