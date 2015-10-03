# USED TO STORE GLOBAL / ENVIRONMENTAL VARIABLES

# General SETTINGS
PROGRESS_BAR = True

# Source directory for documents to be indexed (always use trailing slash)
DOCUMENT_SRC = './data/BigSample/'
# relative location of stop words
STOP_LIST_SRC = './data/stops.txt'

# INDEX SETTINGS
# Relative path to directory to store index
INDEX_LOCATION = './index/'
TEMP_FILE_NAME = 'tempindex'
TRIPLE_LIST_NAME = 'triplelist'
POSTING_LIST_NAME = 'postinglist'

# Type of Index.  Valid types are: "INVERTED", "POSITIONAL", "STEM", and "PHRASE"
INDEX_TYPE = "INVERTED"
MEMORY_MAXIMUM = 10000

# PRE-PROCESSING SETTINGS
INCLUDE_DECIMALS = True
REMOVE_STOP_WORDS = True

# Prefix, suffix, and domain lists
PREFIX_LIST = ['anti', 'auto', 'co', 'com', 'con', 'contra', 'de', 'dis', 'en', 'ex', 'homo', 'hetero', 'hyper', 'in', 'inter', 'intra', 'mono', 'non', 'micro', 'macro', 'pre', 'post', 're', 'trans', 'tri', 'un', 'uni']
DOMAIN_LIST = ['.com', '.edu', '.org', '.net', '.gov']
FILE_EXTENSION_LIST = ['.pdf', '.html', '.doc', '.docx', '.css', '.ppt', '.py', '.txt', '.csv', '.xml', '.mp3', '.mov', '.avi', '.png', '.jpeg', '.jpg', '.xls', '.exe', '.js']

