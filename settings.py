# USED TO STORE GLOBAL / ENVIRONMENTAL VARIABLES

# GENERAL SETTINGS
PROGRESS_BAR = True

# FUNCTIONAL SETTINGS
# Source directory for documents to be indexed (always use trailing slash)
DOCUMENT_SRC = './data/BigSample/'
# relative location of stop words
STOP_LIST_SRC = './data/stops.txt'

# PRE-PROCESSING SETTINGS
# Whether or not to include decimals
INCLUDE_DECIMALS = True
REMOVE_STOP_WORDS = True
# Prefix, suffix, and domain lists
PREFIX_LIST = ['anti', 'auto', 'co', 'com', 'con', 'contra', 'de', 'dis', 'en', 'ex', 'homo', 'hetero', 'hyper', 'in', 'inter', 'intra', 'mono', 'non', 'micro', 'macro', 'pre', 'post', 're', 'trans', 'tri', 'un', 'uni']
DOMAIN_LIST = ['.com', '.edu', '.org', '.net', '.gov']
FILE_EXTENSION_LIST = ['.pdf', '.html', '.doc', '.docx', '.css', '.ppt', '.py', '.txt', '.csv', '.xml', '.mp3', '.mov', '.avi', '.png', '.jpeg', '.jpg', '.xls', '.exe', '.js']


# INDEXING SETTINGS
# Relative path to index directory
INDEX_LOCATION = './index/'
# base name for temp files
TEMP_FILE_NAME = 'tempindex'
# base name for triple list files
TRIPLE_LIST_NAME = 'triplelist'
# base name for posting list files
POSTING_LIST_NAME = 'postinglist'
# Type of Index.  Valid types are: "INVERTED", "POSITIONAL", "STEM", and "PHRASE"
INDEX_TYPE = "INVERTED"
# Maximum memory for triple list, measured in number of triples
MEMORY_MAXIMUM = 10000