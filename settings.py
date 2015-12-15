# USED TO STORE GLOBAL / ENVIRONMENTAL VARIABLES

'''GENERAL SETTINGS'''
PROGRESS_BAR = True
STOP_TERMS = []

'''FUNCTIONAL SETTINGS'''
# Source directory for documents to be indexed (always use trailing slash)
DOCUMENT_SRC = './data/BigSample/'
# File location for queries to be tested
QUERY_SRC = './data/QueryFile/queryfile.txt'
# File location to write treceval files
TRECEVAL_SRC = './treceval/results/'
# relative location of stop words
STOP_LIST_SRC = './data/stops.txt'

'''PRE-PROCESSING SETTINGS'''
# Whether or not to include decimals in tokens or simply round
INCLUDE_DECIMALS = True
# Whether or not to remove stop words in preprocessing (Note: the positional index never removes stop words)
REMOVE_STOP_WORDS = True
# Whether or not to extract phrases
EXTRACT_PHRASES = False
# Prefix, suffix, and domain lists
PREFIX_LIST = ['anti', 'auto', 'co', 'com', 'con', 'contra', 'de', 'dis', 'en', 'ex', 'homo', 'hetero', 'hyper', 'in', 'inter', 'intra', 'mono', 'non', 'micro', 'macro', 'pre', 'post', 're', 'trans', 'tri', 'un', 'uni']
DOMAIN_LIST = ['.com', '.edu', '.org', '.net', '.gov']
FILE_EXTENSION_LIST = ['.pdf', '.html', '.doc', '.docx', '.css', '.ppt', '.py', '.txt', '.csv', '.xml', '.mp3', '.mov', '.avi', '.png', '.jpeg', '.jpg', '.xls', '.exe', '.js']

'''INDEXING SETTINGS'''
# Relative path to index directory (always use trailing slash)
INDEX_LOCATION = './index/'
# base name for temp files
TEMP_FILE_NAME = 'TempIndex'
# base name for triple list files
TRIPLE_LIST_NAME = 'TripleList'
# base name for posting list files
POSTING_LIST_NAME = 'PostingList'
# Document list name
DOC_FILE_NAME = 'DocList'
# Build all indexes option.  If set to True, will build each index type
BUILD_ALL_INDEXES = True
# Type of Index.  Valid types are: "INVERTED", "POSITIONAL", "STEM", and "PHRASE"
INDEX_TYPE = "INVERTED"
# Determines whether the triples list is stored in memory after it has been converted to the posting list.
KEEP_TRIPLES_LIST = False
# (optional) Set a minimum term frequency for the phrase index 
# (as phrases that occur just once per document aren't phrases)
MIN_PHRASE_TF = 2
# Maximum memory for triple list, measured in number of 
# triples (for unlimited memory, set this to a massive number)
MEMORY_MAXIMUM = 100000

'''QUERY PROCESSING SETTINGS: GENERAL'''
# Method of Query processing.  Allowed Values: "STANDARD" or "CONDITIONAL"
# Standard: Sends all queries to the index specified by QUERY_PROCESSING_INDEX
# Conditional: Sends some queries to phrase index and others to positional index
# Note: Query reduction and expansion not supported using conditional processing
QUERY_PROCESSING_METHOD = "STANDARD"
# Relevance Ranking Option. Valid types are: "BM25", "COSINE", "LANGUAGE"
SIMILARITY_MEASURE = "BM25"
# Query-Type: Determines whether the system uses "TITLE" 
# or "NARRATIVE" as the query
# Note: Query expansion only works with "TITLE" and query reduction only works with "NARRATIVE"
QUERY_TYPE = "TITLE" 
# BM25 TUNING PARAMETERS: ONLY USED if SIMILARITY_MEASURE = "BM25"
BM_25_K1 = 1.2
BM_25_K2 = 500.0
BM_25_B  = .75
# DIRICHLET TUNING PARAMETERS: ONLY USED IF SIMILARITY_MEASURE = "LANGUAGE"
LANG_U = 1.0
# Overrides LANG_U if set to true
USE_AVG_DOC_LENGTH_FOR_LANG_U = False

'''QUERY EXPANSION SETTINGS'''
# Determine whether to use query expansion on the queries. 
# Will only be used if QUERY_TYPE is "TITLE"
USE_QUERY_EXPANSION = True
# Determines what type of query expansion method to use. Acceptable values are 'RELEVANCE'
QUERY_EXPANSION_METHOD = 'RELEVANCE'
# parameters for RELEVANCE ranking
REL_NUM_TOP_DOCS = 10
REL_NUM_TOP_TERMS = 5
REL_SORT_CRITERIA = 'NIDF' # value can be 'NIDF' or 'FIDF'

'''QUERY REDUCTION SETTINGS'''
# Determine whether to use query reduction on the queries.  Will only be used if QUERY_TYPE is 
# "NARRATIVE". Defaults to query threshold method
USE_QUERY_REDUCTION = True
QUERY_THRESHOLD_DOCS_RETRIEVED = 100

'''QUERY PROCESSING SETTINGS: STANDARD METHOD'''
# Index to be used if standard is specified.  Options possible are "INVERTED" or "STEM"
QUERY_PROCESSING_INDEX = "INVERTED"

'''QUERY PROCESSING SETTINGS: CONDITIONAL METHOD'''
# PHRASE MIN DF: Minimum document frequency for a phrase for it to be sent to the phrase index
PHRASE_MIN_DF = 2
# MIN DOCS RETRIEVED:  Minimum number of documents retrieved to terminate and stop retrieving docs.
# If this number is not met, then the method will use the backup index
MIN_DOCS_RETRIEVED = 30
# BACKUP INDEX:  Acceptable values are "INVERTED" or "STEM"
BACKUP_INDEX = "INVERTED"


