#!/usr/bin/python
# Import standard modules

"""
NOTE NEED THESE MODULES TOGETHER WITH SUBMISSION:
xml_parser.py, token_normalization.py, test_driver.py
"""

import sys
import math
import getopt
import pickle
from os import listdir

# Import modules for xml parsing and token normalization
from xml_parser import Document
from token_normalization import normalize_tokens

# Import NLTK modules needed
from nltk.tokenize import word_tokenize

#======================================================================#
# Program Description:
# Indexes the PatSnap corpus into a term frequency inverted index.
# 
# The dictionary and postings list are stored separately on the disk in 
# dictionary.txt and postings.txt respectively.
#
# Additionally, the list of docIDs and their corresponding docLengths will be 
# recorded in the dictionary as auxiliary storage so that it can be used in 
# search.py for normalization of the doc vectors.
#======================================================================#

"""
Executes the program
"""
def exec_indexing():
    construct_inverted_index()

"""
Constructs the {term : (docID, term frequency), ...} mapping and writes to disk
"""
def construct_inverted_index() :
    for file_name in list_of_files:
        # Checks for trailing slash in file name
        if dir_of_docs.endswith("/"):
            file_dir = dir_of_docs + file_name
        else:
            file_dir = dir_of_docs + "/" + file_name
        
        if file_name.endswith(".xml"):
            file_name = file_name[:-4]; # Remove ".xml" in file name
        
        xml_doc = Document(file_name, file_dir)
        zones_to_parse = { "title" : xml_doc.get_title(), "abstr" : xml_doc.get_abstract() }
        
        for zone_type, zone_content in zones_to_parse.iteritems():
            if zone_content is not None:
                normalize_tokens_list = normalize_tokens(word_tokenize(zone_content))
                term_list = set(normalize_tokens_list)
                add_to_dictionary(file_name, normalize_tokens_list, term_list, zone_type, xml_doc)

    write_inverted_index_to_disk()

"""
Adds each term in the term_list to the dictionary structure. Also updates each 
term's term frequency for computing document length.

file_name                docID
normalize_tokens_list    list of normalized tokens of this document (contains 
                         duplicate terms)
term_list                list of normalized terms of this document (no duplicate
                         terms)
zone_type                String representation of the type of zone currently being
                         processed, either "title" or "abstract"
"""
def add_to_dictionary(file_name, normalize_tokens_list, term_list, zone_type, xml_doc):
    term_freq_list = []
    for term in term_list:
        term_zone = term + "." + zone_type
        if not term_docID_map.has_key(term_zone):
            term_docID_map[term_zone] = []
        
        # Term frequencies to be used in computation of doc length
        term_freq = normalize_tokens_list.count(term)
        term_freq_list.append(term_freq)
        
        # Dictionary structure { term_zone : [(docID, term_freq), ...]}
        term_docID_map[term_zone].append((file_name, term_freq))
    update_doc_length_IPC(file_name, term_freq_list, xml_doc)
    
"""
Add doc length to docID_len_IPC_map for computation of weights in search.py.

file_name         docID
term_freq_list    list of term frequencies
"""
def update_doc_length_IPC(file_name, term_freq_list, xml_doc):
    if not docID_len_IPC_map.has_key(file_name):
        docID_len_IPC_map[file_name] = [0, ""]
    docID_len_IPC_map[file_name][0] = compute_doc_length(term_freq_list)
    docID_len_IPC_map[file_name][1] = xml_doc.get_IPC_subclass()

"""
Computes the document vector's magnitude, or the document length.

term_freq_list    List of term frequencies of a document

return            document length
"""
def compute_doc_length(term_freq_list):
    result = 0
    for term_freq in term_freq_list:
        if term_freq == 0:
            term_freq_log_weighting = 0
        else:
            term_freq_log_weighting = 1 + math.log(term_freq, 10)
        result += math.pow(term_freq_log_weighting, 2)
    return math.sqrt(result)

"""
Sets up dictionary and postings data structures to be written to the respective 
files.

The dictionary will be stored in a hash map that maps to a list representing 
the docFreq and pointer of a particular term in the below format.
{ term : [docFreq, value of pointer offset in postings file] }

Also stores the universal set of docIDs and their docLengths for use in 
searching to dictionary.txt

The postings list will be stored as a list of docIDs in a part of the postings 
file on disk specified by a pointer offset value.
"""
def write_inverted_index_to_disk():
    to_dict_file = open(dict_file, "w")
    to_postings_file = open(postings_file, "w")

    dictionary = {}
    dict_terms = term_docID_map.keys(); 
    for term in dict_terms:
        docFreq = len(term_docID_map[term])
        curr_pointer = to_postings_file.tell()
        
        # Dictionary map in the form of { term : [docFreq, pointer in postings file] }
        dictionary[term] = [docFreq, curr_pointer]
        
        # Postings objects of terms written to postings.txt
        postings_docID_list = term_docID_map[term]
        pickle.dump(postings_docID_list, to_postings_file)
    pickle.dump(dictionary, to_dict_file)
    
    # Allocate some dictionary memory to storing the doc length and IPC subclass of each doc
    pickle.dump(docID_len_IPC_map, to_dict_file)
    
    to_dict_file.close()
    to_postings_file.close()

"""
Interprets arguments of this indexing program
"""
def usage():
    print "usage: " + sys.argv[0] + "-i directory-of-documents " \
    "-d dictionary-file -p postings-file"

dir_of_docs = dict_file = postings_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-i':
        dir_of_docs = a
    elif o == '-d':
        dict_file = a
    elif o == '-p':
        postings_file = a
    else:
        assert False, "unhandled option"
if dir_of_docs == None or dict_file == None or postings_file == None:
    usage()
    sys.exit(2)

#=====================================================#
# Execution of Program
#=====================================================#
# Get set of docIDs to process
list_of_files = listdir(dir_of_docs)

term_docID_map = {}
docID_len_IPC_map = {}

# Point of indexing execution
exec_indexing();
