# Information-Retrieval Project 1: Indexing

### Design Overview
My project is broadly designed as a sequential process, most of which can be explained by looking at the main.py file, the program’s main entry point.  Each document is read in individually, preprocessed, and indexed before the next document is pulled into memory.  As documents are indexed, triple lists are written to files on the disk if the length of the list exceeds the memory constraint.  Once all documents have been read, the remaining triples in memory are written to files, the temporary files are merged, and the large triple list is converted to a single posting list.  Finally, the lexicon is written to memory.  Broadly, this process is composed of four sub processes: file input and parsing, preprocessing, indexing, and file-writing.

### Program Output
Upon completion of the program, each index should have a posting list and a lexicon stored in the index directory.  Upon initializing the program, the index directory is cleared and new lexicons/posting lists are generated.  

### External Libraries Used
Numpy –Used to calculate statistics (i.e. mean df, median df) for the program
NLTK Porter Stemmer – Used to stem terms for the stem index.
Tabulate – Used to display tabular results for the program after it has run.
Bisect (built into python/not external) – Used for insort methods to keep list in sorted order.

### Running the Project
To get started and run my project, there are a few things you need to do:
1.	For everything to run, you’ll have to make sure the dependencies are installed (only numpy, tabulate, and nltk).  To do so, run: pip install –r requirements.txt (note: this command requires pip).  All testing as been completed on python 2.7.8.
2.	Now, open settings.py and make sure that the settings are as you want them.
3.	Run the main file using the following command: python main.py
4.	View your output in the command line or write it to a file by running: python main.py > yourfile.txt.

