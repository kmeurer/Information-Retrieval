# USED TO STORE GLOBAL / ENVIRONMENTAL VARIABLES

# GENERAL SETTINGS
PROGRESS_BAR = True

# FUNCTIONAL SETTINGS
# Source directory for documents to be indexed (always use trailing slash)
DOCUMENT_SRC = './data/BigSample/'
# relative location of stop words
STOP_LIST_SRC = './data/stops.txt'

# PRE-PROCESSING SETTINGS
# Whether or not to include decimals in tokens or simply round
INCLUDE_DECIMALS = True
# Whether or not to remove stop words in preprocessing (Note: the positional index never removes stop words)
REMOVE_STOP_WORDS = True
# Prefix, suffix, and domain lists
PREFIX_LIST = ['anti', 'auto', 'co', 'com', 'con', 'contra', 'de', 'dis', 'en', 'ex', 'homo', 'hetero', 'hyper', 'in', 'inter', 'intra', 'mono', 'non', 'micro', 'macro', 'pre', 'post', 're', 'trans', 'tri', 'un', 'uni']
DOMAIN_LIST = ['.com', '.edu', '.org', '.net', '.gov']
FILE_EXTENSION_LIST = ['.pdf', '.html', '.doc', '.docx', '.css', '.ppt', '.py', '.txt', '.csv', '.xml', '.mp3', '.mov', '.avi', '.png', '.jpeg', '.jpg', '.xls', '.exe', '.js']


# INDEXING SETTINGS
# Relative path to index directory (always use trailing slash)
INDEX_LOCATION = './index/'
# base name for temp files
TEMP_FILE_NAME = 'TempIndex'
# base name for triple list files
TRIPLE_LIST_NAME = 'TripleList'
# base name for posting list files
POSTING_LIST_NAME = 'PostingList'
# Build all indexes option.  If set to True, will build each index type
BUILD_ALL_INDEXES = True
# Type of Index.  Valid types are: "INVERTED", "POSITIONAL", "STEM", and "PHRASE"
INDEX_TYPE = "PHRASE"
# Determines whether the triples list is stored in memory after it has been converted to the posting list.
KEEP_TRIPLES_LIST = False
# (optional) Set a minimum term frequency for the phrase index (as phrases that occur just once per document aren't phrases)
MIN_PHRASE_TF = 2
# Maximum memory for triple list, measured in number of triples (for unlimited memory, set this to a massive number)
MEMORY_MAXIMUM = 100000