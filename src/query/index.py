import re
import codecs
import settings as ENV
import utils as util
import queryProcessor as qp
import numpy as np

class Index(object):
    def __init__(self, lexicon_file_location, posting_list_file_location, doc_list_file_location):
        print "\nLOADING INDEX..."
        # extract doc list
        self.doc_list_location = doc_list_file_location
        self.doc_list = self._read_doc_list_to_memory(doc_list_file_location)
        # extract posting list
        self.posting_list_file_location = posting_list_file_location
        if ENV.EXTRACT_FULL_POSTING_LIST == True:
            self.posting_list = self._read_full_postings_to_memory(posting_list_file_location)
        # extract lexicon
        self.lexicon_file_location = lexicon_file_location
        self.lexicon = self._read_lexicon_to_memory(lexicon_file_location)
        self._lexicon_compressed = [term_entry[1] for term_entry in self.lexicon]
        
        if ENV.SIMILARITY_MEASURE == "VECTOR":
           self._extract_document_summations()

    
    # Given a list of termIds, retrieves specified term entries from the posting list
    # Returns: Dictionary of posting list entries: { termId: [[documentID, docFrequency], [documentID, docFrequency]]}
    def get_posting_entries(self, term_ids):
        if ENV.EXTRACT_FULL_POSTING_LIST == True:
            entries = {}
            for term in term_ids:
                entries[term] = self.get_posting_entry(term)
            return entries
        else:
            return self.read_posting_entries_to_memory(self.posting_list_file_location, term_ids)

    # Given a list of terms, retrieves specified term entries from the posting list
    # Returns: Dictionary of posting list entries: { termId: [[documentID, docFrequency], [documentID, docFrequency]]}
    def get_posting_entries_by_terms(self, term_list):
        results = {}
        for term in term_list:
            tid = self.get_term_id_by_term(term)
            if tid != None:
                results[tid] = self.get_posting_entry(tid)
        return results

    # Given a single id, retrieves document part of posting list
    # Returns: List of posting list entries: [[documentID, docFrequency], [documentID, docFrequency]]
    def get_posting_entry(self, term_id):
        return self.posting_list[term_id]

    # Given a term as a string, retrieves posting entry if it exists, none if not
    # Returns: List of posting list entries: [[documentID, docFrequency], [documentID, docFrequency]]
    def get_posting_entry_by_term(self, term):
        return self.get_posting_entry(self.get_term_id_by_term(term))

    # Given a term as a string, retrieves term id, none if not in lexicon
    # Returns: number or None
    def get_term_id_by_term(self, term):
        if term in self._lexicon_compressed:
            return self._lexicon_compressed.index(term)
        else:
            return None

    def get_df_by_term_id(self, term_id):
        return self.lexicon[term_id][2]

    def get_document_weight_summation(self, doc_id):
        return self.doc_list[doc_id]['sum_weight']

    def get_document_length(self, doc_id):
        return self.doc_list[doc_id]['length']

    def get_avg_document_length(self):
        return self.avg_doc_length

    def get_collection_size(self):
        return len(self.doc_list.keys())

    '''
    Given a file location and a list of termIds, retrieves specified 
    term entries from a posting list in the format below.  Useful for memory-constrained projects

    Returns
    -------
    Dictionary of posting list entries:
      { termId: [[documentID, docFrequency], [documentID, docFrequency]]}
    '''
    def read_posting_entries_to_memory(self, file_location, term_ids):
        postings = codecs.open(file_location, 'rb', 'utf-8')
        output_dict = {}
        current_line = postings.readline()
        while current_line != '':
            current_line = current_line.replace('\n', '').split(': ')
            if int(current_line[0]) in term_ids:
                doc_info = current_line[1].split('->')
                for idx, doc in enumerate(doc_info):
                    doc = re.sub(r'[\(\)]', '', doc)
                    doc = doc.split(', ')
                    doc_info[idx] = [int(doc[0]), int(doc[1])]
                output_dict[int(current_line[0])] = doc_info
            current_line = postings.readline()
        return output_dict

    '''
    Given a file location, reads a lexicon into memory

    Returns
    -------
    List of lists with the following format:
      [[termid, term, tf]]
    '''
    def _read_lexicon_to_memory(cls, file_location):
        print "\nReading lexicon to memory..."
        lexicon = codecs.open(file_location, 'rb', 'utf-8')
        lexicon_list = lexicon.readlines()
        if ENV.PROGRESS_BAR == True:    
            util.update_progress(0)
        for idx, entry in enumerate(lexicon_list):
            if ENV.PROGRESS_BAR == True:
                util.update_progress(float(idx) / float(len(lexicon_list)))
            entry = entry.replace('\n', '').split(' ')
            entry[0] = int(entry[0])
            entry[2] = int(entry[2])
            lexicon_list[idx] = entry
        if ENV.PROGRESS_BAR == True:
            util.update_progress(1)
        lexicon.close()
        return lexicon_list

    '''
    Given a file location, retrieves entire posting list and stores in memory

    Returns
    -------
    Dictionary of posting list entries:
      { termId: [[documentID, docFrequency], [documentID, docFrequency]]}
    '''
    def _read_full_postings_to_memory(cls, file_location):
        print "\nReading posting list to memory..."
        postings = codecs.open(file_location, 'rb', 'utf-8')
        posting_list = {}
        posting_lines = postings.readlines()
        if ENV.PROGRESS_BAR == True:
            util.update_progress(0)
        for idx, line in enumerate(posting_lines):
            if ENV.PROGRESS_BAR == True:
                util.update_progress(float(idx) / float(len(posting_lines)))
            line = line.replace('\n', '').split(': ')
            doc_info = line[1].split('->')
            for idx, doc in enumerate(doc_info):
                doc = re.sub(r'[\(\)]', '', doc)
                doc = doc.split(', ')
                doc_info[idx] = [int(doc[0]), int(doc[1])]
            posting_list[int(line[0])] = doc_info
        if ENV.PROGRESS_BAR == True:
            util.update_progress(1)
        postings.close()
        return posting_list

    '''
    Given a file location, retrieves the document list

    Returns
    -------
    List of document entries:
      [ [docid, doclength] ]
    '''
    def _read_doc_list_to_memory(cls, file_location):
        print "\nExtracting Document List..."
        doc_lengths = []
        documents = codecs.open(file_location, 'rb', 'utf-8')
        document_list = documents.readlines()
        doc_dict = {}
        if ENV.PROGRESS_BAR == True:
            util.update_progress(0)
        for idx, entry in enumerate(document_list):
            if ENV.PROGRESS_BAR == True:
                util.update_progress(float(idx) / float(len(document_list)))
            entry = entry.replace('\n', '').split(' ')
            entry[0] = int(entry[0])
            entry[1] = int(entry[1])
            document_list[idx] = entry
            doc_dict[entry[0]] = {'length': entry[1]}
            doc_lengths.append(entry[1])
        if ENV.PROGRESS_BAR == True:
            util.update_progress(1)
        cls.avg_doc_length = np.mean(doc_lengths)
        return doc_dict

    '''
    Used in VSM Cosine only, this function will extract the document weight, squared, for all terms in the doc_info
    the value is used as a proxy for document length

    Returns
    -------
    Nothing.  Updates self.doc_list
    '''
    def _extract_document_summations(cls):
        print "\nExtracting document summations for use in Vector Space Model..."
        if ENV.PROGRESS_BAR == True:
            util.update_progress(0)
        for idx, term in enumerate(cls.posting_list):
            if ENV.PROGRESS_BAR == True:
                util.update_progress(float(idx) / float(len(cls.posting_list)))
            docs = cls.posting_list[term]
            for doc in docs:
                addition = qp.calculate_tf_idf(doc[1], cls.get_df_by_term_id(term), len(cls.doc_list.keys()))
                addition_squared = np.square(addition)
                if 'sum_weight' in cls.doc_list[doc[0]]:
                    cls.doc_list[doc[0]]['sum_weight'] += addition_squared
                else:
                    cls.doc_list[doc[0]]['sum_weight'] = addition_squared
        if ENV.PROGRESS_BAR == True:
            util.update_progress(1)

