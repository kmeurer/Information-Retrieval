import re
import codecs
import os
import document as d
import docProcessor as dp
import utils as util
import settings as ENV


def processQuery(queryString, stopTerms):
	if queryString.isspace() or queryString == "" :
		return None
	# Convert document to class format
	query = d.Query(queryString)
	# Use the same preprocessing strategy here for consistency
	query.preprocessText(stopTerms)
	# clean up document by eliminating extraneous tokens, except in cases where they fall within brackets {}
	return query