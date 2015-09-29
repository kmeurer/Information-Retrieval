# USED TO STORE GLOBAL / ENVIRONMENTAL VARIABLES

# General Settings
PROGRESS_BAR = True 							# set whether a progress bar is used to show output.  Should be turned off when writing to files

# Source directory for documents to be indexed (always use trailing slash)
DOCUMENT_SRC = './data/BigSample/'
# relative location of stop words
STOP_LIST_SRC = './data/stops.txt'

# Relative path to directory to store index
INDEX_LOCATION = './index'

# Prefix, suffix, and domain lists
PREFIX_LIST = ['anti', 'auto', 'co', 'com', 'con', 'contra', 'de', 'dis', 'en', 'ex', 'homo', 'hetero', 'hyper', 'in', 'inter', 'intra', 'mono', 'non', 'micro', 'macro', 'pre', 'post', 're', 'trans', 'tri', 'un', 'uni']
DOMAIN_LIST = ['com', 'edu', 'org', 'net', 'gov']

