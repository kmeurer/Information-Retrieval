import time, sys
import numpy as np
import codecs
import re
import math
import random
import settings as ENV

#  STORES ACCESSORY CLASSES AND FUNCTIONS
def extractStopTerms():
    stopTerms = []
    stopTermFile = codecs.open(ENV.STOP_LIST_SRC, 'rb', 'utf-8')    # specify utf-8 encoding
    lines = stopTermFile.readlines()
    for line in lines:
        stopTerms.append(re.sub('\n', '', line))
    return stopTerms

# SAMPLING FUNCTIONS
# choose w/out replacement and return it
def chooseOneWithoutReplacement(list):
	randIdx = math.floor(len(list) * random.random())
	removedVal = list.pop(int(randIdx))
	return removedVal

# choose one w/ replacement and return it
def chooseOneWithReplacement(list):
	randIdx = math.floor(len(list) * random.random())
	val = list[int(randIdx):int(randIdx) + 1]
	return val

# DICTIONARY FUNCTIONS
# returns true if dictionary is empty, else returns false
def dictIsEmpty(dict):
	for key in dict:
		return False
	return True

# Merges Two dictionaries that use integers as values
def mergeDicts(dict1, dict2):
	newDict = {}
	for key in dict1:
		if key in dict2:
			newDict[key] = dict1[key] + dict2[key]
		else:
			newDict[key] = dict1[key]
	for key in dict2:
		if key in newDict:
			continue
		else:
			newDict[key] = dict2[key]
	return newDict


# MISCELLANEOUS
# Returns whether the string can be converted to a number
def isNumber(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

# Progress bar function -- Some functions inspired by this: http://stackoverflow.com/questions/3160699/python-progress-bar
def update_progress(progress):
    barLength = 20 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Pausing...\r\n"
    if progress >= 1:
        progress = 1
        status = "Processing complete..."
    block = int(round(barLength*progress))
    text = "\rProgress: [{0}] {1}% {2}".format( "#" * block + "-" * (barLength - block), progress * 100, status)
    sys.stdout.write(text)
    sys.stdout.flush()

def convert_num_id_to_trek_id(doc_id):
    # convert to string
    doc_id = str(doc_id)
    return 'FR' + doc_id[0:6] + '-' + doc_id[6:7] + '-' + doc_id[7:]

