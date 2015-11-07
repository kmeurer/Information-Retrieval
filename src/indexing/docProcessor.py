import re
import codecs
import os
import utils as util
from object_definitions import document as d
import settings as ENV

def writeDocListToFile(docList):
    print "running"
    fileName = ENV.INDEX_TYPE.lower() + ENV.DOC_FILE_NAME + ".txt"
    docFile = codecs.open(ENV.INDEX_LOCATION + fileName, 'w', 'utf-8')  # specify utf-8 encoding
    for doc in docList:
        docFile.write(str(doc[0]) + " " + str(doc[1]) + "\n")

def processDocument(docStr, stopTerms):
    # Ignore empty document tokens
    if docStr.isspace() or docStr == "" :
        return None
    # Convert document to class format
    doc = d.Document(re.search('<DOCNO>(.*)</DOCNO>', docStr).group(1), docStr)
    doc.preprocessText(stopTerms)
    # clean up document by eliminating extraneous tokens, except in cases where they fall within brackets {}
    return doc