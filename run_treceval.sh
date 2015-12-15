#!
# empty directory contents
rm -rf /Users/kevinmeurer/Projects/InformationRetrieval/treceval/eval/*
# iterate through files and send eval output to output directory
for f in $( ls /Users/kevinmeurer/Projects/InformationRetrieval/treceval/results ); do
	/Users/kevinmeurer/Projects/InformationRetrieval/treceval/trec_eval.8.1/trec_eval -q -a /Users/kevinmeurer/Projects/InformationRetrieval/treceval/qrel.txt /Users/kevinmeurer/Projects/InformationRetrieval/treceval/results/$f > /Users/kevinmeurer/Projects/InformationRetrieval/treceval/eval/$f\_eval.txt
done