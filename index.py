#!/usr/bin/python
# Import standard modules
import sys
import math
import getopt
from os import listdir
import pickle

# Import modules for XML parsing
from xml_parser import Document

# Import NLTK modules needed
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

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

term_docID_map = {}
docLength_map = {}

"""
Executes the program
"""
def exec_indexing():
    construct_inverted_index()

"""
Constructs the (term, (docID, term frequency)) mapping and writes to disk
"""
def construct_inverted_index() :
    # Iterates through a sorted list of all files, each file with a unique
    # filename, i.e. docID. Ensures postings docIDs will also be in sorted
    # order when appended to term-docID mapping.
    for file_name in list_of_files:
        # Checks for trailing slash in case
        if dir_of_docs.endswith("/"):
            file_dir = dir_of_docs + file_name
            file_text = open(file_dir, "r").read()
        else:
            file_dir = dir_of_docs + "/" + file_name
            file_text = open(file_dir, "r").read()
        
        if file_name.endswith(".xml"):
            file_name = file_name[:-4]; # Remove ".xml" in file name
        
        # Test XML parsing of doc
        xml_doc = Document(file_name, file_dir)
        #print xml_doc.get_title()
        #print xml_doc.get_abstract()
        #print xml_doc.get_IPC_subclass()
        #xml_doc.print_xml_format()
        #print "----------------------------------------"
        
        words_list = word_tokenize(file_text)
        normalize_tokens_list = normalize_tokens(words_list)
        term_list = set(normalize_tokens_list)
        
        # add patent_docID to the current term_docID_map
        term_freq_list = []
        for term in term_list:
            if not term_docID_map.has_key(term):
                term_docID_map[term] = []
            
            # Term frequencies to be used in computation of doc length
            term_freq = normalize_tokens_list.count(term)
            term_freq_list.append(term_freq)
            term_docID_map[term].append((file_name, term_freq))
        
        # add doc length to docLength_map for computation of weights in search.py
        if not docLength_map.has_key(file_name):
            docLength_map[file_name] = 0
        docLength_map[file_name] = compute_doc_length(term_freq_list)
        
    # print term_docID_map # For debugging purposes
    write_inverted_index_to_disk()

"""
Computes the document vector's magnitude, or the document length.

term_freq_list    List of term frequencies of a document

return            Document length
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
Normalizes tokens through case-folding and stemming using Porter's Stemmer.

tokens_list    List of unnormalized tokens

return         List of normalized tokens
"""
def normalize_tokens(tokens_list):
    stemmer = PorterStemmer()
    normalized_token_list = []
    
    for token in tokens_list:
        normalized_token_list.append(stemmer.stem(token.lower()))
    
    return normalized_token_list
   
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
        
        # Dictionary map in the form of:
        # { term : [docFreq, value of pointer offset in postings file] }
        dictionary[term] = [docFreq, curr_pointer]
        
        # Postings objects of sorted terms written to postings.txt, individually
        # for search phase retrieval
        postings_docID_list = term_docID_map[term]
        #print postings_docID_list
        pickle.dump(postings_docID_list, to_postings_file)
    pickle.dump(dictionary, to_dict_file)
    
    # Allocate some dictionary memory to storing the universal set of docIDs
    # for search.py
    pickle.dump(list_of_files, to_dict_file)
    
    # Allocate some dictionary memory to storing the doc length of each doc
    pickle.dump(docLength_map, to_dict_file)
    
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
"""
Get set of docIDs to process
"""
list_of_files = listdir(dir_of_docs)

""" 
Point of indexing execution
""" 
exec_indexing();
