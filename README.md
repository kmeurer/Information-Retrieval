# Information-Retrieval Project 2: Query Extraction

### Design Overview
My project is broadly designed in two large parts.  The first, indexing, is initialized by running the buildIndices.py script.  This will draw on files in src/index specifically to build the indices.  A full outline of this design can be found in Indexing Project Report.pdf, so I will spend no further time on it here.

The second part, query processing, is initialized by the processQueries.py script.  This script runs a sequential process that does the following:

1. Extract queries from the file at the path specified by ENV.QUERY_SRC.
2. Load the necessary indexes to memory to be stored as an Index object (contains posting list, doc list, and lexicon).  In the case of standard processing, this is the index specified by ENV.QUERY_PROCESSING_INDEX.  In the case of Conditional, the file system will load the phrase index and the positional index.
3. Queries are preprocessed one at a time, using the same preprocessing methods as documents.  To ensure consistency, Queries are stored as Query objects that inherit from a parent TextObject class (which documents also inherit from)
4. For each query, relevant docs are ranked in a results dictionary
	a. In the case of standard processing, each query is processed according to the specified index using the similarity measure specified by ENV.SIMILARITY_MEASURE (possible options are BM25, COSINE, and LANGUAGE)
	b. In the case of conditional processing, queries are sent to the positional index if they have a document frequency above ENV.PHRASE_MIN_DF in the phrase index.  Otherwise, they are processed by the positional index.  If not enough documents have been retrieved after accessing either index, the query will be matched with documents using the index specified in ENV.BACKUP_INDEX.  These results are added to the others to produce a new ranking.
5. Results are written to a file in treceval format at treceval/results with the name processingapproach_indextype_similaritymeasure.txt

In terms of overall design of the query processing, most relevant files are within src/query, and all files rely on the settings specified in settings.py.  queryProcessor.py contains all the logic related to query preprocessing and basic tf.idf extraction.  index.py contains the object model for an index stored in memory, and it holds all logic related to accessing items within the index.  This abstraction keeps the accessing of index items separate from the query processing task.  Finally, vectorSpace.py, languageModel.py, and bm25.py each contains their respective similarity calculations.

### Program Output
Upon completion of the program, each index should have a posting list and a lexicon stored in the index directory.  Upon initializing the program, the index directory is cleared and new lexicons/posting lists are generated.  

### External Libraries Used
Numpy –Used to calculate statistics (i.e. mean df, median df) for the program
NLTK Porter Stemmer – Used to stem terms for the stem index.
Tabulate – Used to display tabular results for the program after it has run.
Bisect (built into python/not external) – Used for insort methods to keep list in sorted order.

### Running the Project
To get started and run my project, there are a few things you need to do:
1.	For everything to run, you’ll have to make sure the dependencies are installed (only numpy, tabulate, and nltk).  To do so, run: pip install –r requirements.txt (note: this command requires pip).  All testing has been completed on python 2.7.8.
2.	Now, open settings.py and make sure that the settings are as you want them.
3.	Run the main file using the following command: python main.py
4.	View your output in the command line or write it to a file by running: python main.py > yourfile.txt.

