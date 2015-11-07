from textobject import TextObject
import re
import settings as ENV

'''
Document object.  Specific information related to documents
'''
class Document(TextObject):
    def __init__(self, docId, text):
        super(Document, self).__init__(text)
        self.id = int(re.sub("\D", "", docId)) # stores as number for space efficiency

    # getDocId: returns the id of the current document
    def getDocId(self):
        return self.id

    def preprocessText(self, stopTerms):
        super(Document, self).preprocessText()
        if ENV.INDEX_TYPE == "PHRASE":
            self.extractValidPhrases(stopTerms)
        # Now that we have our phrase information, we can clean our tokens
        self.cleanTokens()

