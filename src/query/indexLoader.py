import re
import codecs

'''
Given a file location, reads a lexicon into memory

Returns
-------
List of lists with the following format:
  [[termid, term, tf]]
'''
def read_lexicon_to_memory(file_location):
	lexicon = codecs.open(file_location, 'rb', 'utf-8')
	lexicon_list = lexicon.readlines()
	for idx, entry in enumerate(lexicon_list):
		 entry = entry.replace('\n', '').split(' ')
		 entry[0] = int(entry[0])
		 entry[2] = int(entry[2])
		 lexicon_list[idx] = entry
	return lexicon_list

'''
Given a file location and a list of termIds, retrieves specified 
term entries from a posting list in the format below

Returns
-------
Dictionary of posting list entries:
  { termId: [[documentID, docFrequency], [documentID, docFrequency]]}
'''
def read_posting_index_to_memory(file_location, term_ids):
	postings = codecs.open(file_location, 'rb', 'utf-8')
	output_dict = {}
	current_line = postings.readline()
	while current_line != '':
		current_line = current_line.replace('\n', '').replace(':', '').split(' ')
		if int(current_line[0]) in term_ids:
			doc_info = current_line[1].split('->')
			for idx, doc in enumerate(doc_info):
				doc = re.sub(r'[\(\)]', '', doc)
				doc = doc.split(', ')
				doc_info[idx] = [int(doc[0]), int(doc[1])]
			output_dict[int(current_line)] = doc_info
	current_line = postings.readline()
	return output_dict


'''
Given a file location, retrieves the document list

Returns
-------
List of document entries:
  [ [docid, doclength] ]
'''
def read_doc_list_to_memory(fileLocation):
	documents = codecs.open(file_location, 'rb', 'utf-8')
	document_list = documents.readlines()
	for idx, entry in enumerate(document_list):
		 entry = entry.replace('\n', '').split(' ')
		 entry[0] = int(entry[0])
		 entry[1] = int(entry[1])
		 document_list[idx] = entry
	return document_list
