from textobject import TextObject
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
