# Information-Retrieval Project 3: Query Reduction / Expansion

### Design Overview
My project’s design is broadly the same as it was in prior iterations, but I have outlined the main changes in the algorithm below. A full outline of the indexing design can be found in Indexing Project Report.pdf and more details on query processing decisions may be found in Query Processing Project 2 Report.pdf, so I will spend no further time on it here.
The “processQueries” script initializes the relevant section of this project, as it includes both query processing and query expansion/reduction. This script runs a sequential process that does the following (new parts are bolded):

1. Extract queries from the file at the path specified by ENV.QUERY_SRC.
2. Load the necessary indexes to memory to be stored as an Index object (contains
posting list, doc list, and lexicon). In the case of standard processing, this is the index specified by ENV.QUERY\_PROCESSING\_INDEX. In the case of Conditional, the file system will load the phrase index and the positional index as well as a backup index specified by ENV.BACKUP\_INDEX. Please note that conditional processing does not support query expansion or reduction.
3. Queries are preprocessed one at a time, using the same preprocessing methods as documents. To ensure consistency, Queries are stored as Query objects that inherit from a parent TextObject class (which documents also inherit from)
4. If ENV.USE\_QUERY\_REDUCTION is set to “True” and ENV.QUERY\_TYPE is set to “NARRATIVE,” the system will employ query reduction. This is done using a document retrieval threshold rather than a strict percentage of the query terms. The document threshold is specified by ENV.QUERY\_THRESHOLD\_DOCS\_RETRIEVED. Terms are added to the query iteratively, and the query is re-ranked until a specified number of docs are retrieved.
5. (if query reduction is not set to true) For each query, relevant docs are ranked in a results dictionary
	a. In the case of “STANDARD” processing, each query is processed according to the specified index using the similarity measure specified by ENV.SIMILARITY\_MEASURE (possible options are BM25, COSINE, and LANGUAGE)
	b. In the case of “CONDITIONAL” processing, queries are sent to the positional index if they have a document frequency above ENV.PHRASE\_MIN\_DF in the phrase index. Otherwise, they are processed by the positional index. If not enough documents have been retrieved after accessing either index, thequery will be matched with documents using the index specified by ENV.BACKUP\_INDEX. These results are added to the others to produce a new ranking.
6. If ENV.USE\_QUERY\_EXPANSION is set to True and ENV.QUERY\_TYPE is set to “TITLE,” the system will use relevance feedback to expand the queries. This works using the queryExpander.py file. It will select the top n documents as specified by ENV.REL\_NUM\_TOP\_DOCS and then select the top m terms as specified by ENV.REL_NUM_TOP_TERMS.
7. Results are written to a file in treceval format at treceval/results with the name assigned according to the settings

In terms of overall design of the query processing, most relevant files are within
src/query, and all files rely on the settings specified in settings.py. queryProcessor.py contains all the logic related to query preprocessing and basic tf.idf extraction. index.py contains the object model for an index stored in memory, and it holds all logic related to accessing items within the index. This abstraction keeps the accessing of index items separate from the query processing task. vectorSpace.py, languageModel.py, and bm25.py each contains its respective similarity calculations. Few files were added for this stage of the project, but queryExpander.py serves as a wrapper for expansion.


### External Libraries Used
Numpy –Used to calculate statistics (i.e. mean df, median df) for the program
NLTK Porter Stemmer – Used to stem terms for the stem index.
Tabulate – Used to display tabular results for the program after it has run.
Bisect (built into python/not external) – Used for insort methods to keep list in sorted order.

### Running the Project
To get started and run my project, there are a few things you need to do:
1.	For everything to run, you’ll have to make sure the dependencies are installed (only numpy, tabulate, and nltk).  To do so, run: pip install –r requirements.txt (note: this command requires pip)
2.	Now, open settings.py and make sure that the settings are as you want them.
3.	If indexes have not yet been generated (there is nothing in the index folder), generate them now by running this command: python buildIndices.py
4.	Now, run the query processing task using the following command: python queryProcessing.py
5.	View your output in the treceval folder under results and run the treceval script to generate the resulting statistics.

Please Note:  In the current state of the project, the only setting you will have to change to test reduction/expansion is the value of QUERY\_TYPE.  If it is set to “NARRATIVE,” it will reduce the query, and if it is set to “TITLE,” it will expand it.  The settings should already have USE\_QUERY\_REDUCTION and USE\_QUERY_EXPANSION set to True.

###Recommended Settings
The following settings reflect the optimal configuration for running the program quickly  and receiving ideal results (this is the current configuration):

####Indexing Settings
DOCUMENT_SRC = './data/BigSample/'
STOP\_LIST\_SRC = './data/stops.txt'
INCLUDE\_DECIMALS = True
REMOVE\_STOP\_WORDS = True
INDEX\_LOCATION = './index/'
TEMP\_FILE\_NAME = 'TempIndex'
TRIPLE\_LIST\_NAME = 'TripleList'
BUILD\_ALL\_INDEXES = True
MIN\_PHRASE\_TF = 2
MEMORY\_MAXIMUM = 100000

####Query Retrieval Settings
QUERY\_PROCESSING\_METHOD = "STANDARD"
SIMILARITY\_MEASURE = "BM25"
BM\_25\_K1 = 1.2
BM\_25\_K2 = 500.0
BM\_25\_B  = .75
QUERY\_PROCESSING\_INDEX = "INVERTED"

####Query Expansion Settings
QUERY\_TYPE = “TITLE”
USE\_QUERY\_EXPANSION = True
QUERY\_EXPANSION\_METHOD = 'RELEVANCE'
REL\_NUM\_TOP\_DOCS = 10
REL\_NUM\_TOP\_TERMS = 5
REL\_SORT\_CRITERIA = 'NIDF'

####Query Reduction Settings (note: mutually exclusive with query expansion)
QUERY\_TYPE = “NARRATIVE”
USE\_QUERY\_REDUCTION = True
QUERY\_THRESHOLD\_DOCS\_RETRIEVED = 50



