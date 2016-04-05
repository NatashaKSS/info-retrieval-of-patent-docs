#!/usr/bin/python
# Import standard modules
import sys
import math
import getopt
import pickle
import operator

# Import modules for XML parsing
from xml_parser import Query

# Import modules for testing
from test_driver import TestDriver

# Import NLTK modules needed
from nltk import word_tokenize
from nltk.stem import PorterStemmer

#======================================================================#
# Program Description:
# Searches for all relevant PatSnap patents with reference to an XML 
# formatted search query.
# 
# The result of the query will be written to the specified output file, 
# containing all relevant document IDs.
#======================================================================#

"""
Main execution point of program
Executes the search operation on the given queries in file-of-queries

query    Query object parsed at start of program.
"""
def exec_search(query):
    # Wipe the output file before processing all the queries to ensure previous
    # runs of this program do not merely append the results to the end of the file
    with open(output_file, "w"):
        pass

    """
    TODO
    Only tries to work with the title of query...for now...
    """
    #print "Title:", query.get_title()
    #print "Description:", query.get_description()
    
    # Normalize query list with case-folding and stemming
    normalized_query_list = normalize_tokens(query.get_title())

    # Term frequencies of query terms for processing    
    query_term_freq_map = compute_query_term_freq_weights(normalized_query_list)
    
    # Remove duplicate query terms to process each term
    # This first round of searching (using the user's input query) holds a weight of 0.75
    ranked_results = get_top_results(set(normalized_query_list), query_term_freq_map, 0.75)
    
    my_test = TestDriver(ranked_results)
    my_test.process_results()
    
    # NOTE:
    # Query Expansion HEREEEE
    # You can use list_top_10_docIDs (a global variable) 
    # which contains (docID, tf-idf weight) tuples of the top 10 relevant docs
    
    
    write_to_output_file(ranked_results)

"""
Searches for results for the specified queries in ranked order.
Also updates the list of top 10 documents that are assumed to be relevant.

list_of_query_terms    List of query terms which are normalized and have no duplicates.
query_term_freq_map    A mapping of log term frequency weights for each query term.
weight                 A fractional weight of choice to give to this tf-idf score.
                       0 < weight <= 1.

return    List of docIDs that relevant to this query, sorted in descending order.
"""
def get_top_results(list_of_query_terms, query_term_freq_map, weight):
    global scores
    global list_top_10_docIDs
    list_of_query_idf = []

    for query_term in list_of_query_terms:
        term_postings = load_postings_for_term(query_term)
        query_term_freq_weight = query_term_freq_map[query_term]
        query_term_idf = get_idf(term_postings, len(list_of_docIDs))
        
        # Accumulate list of query idf values for computation of normalized query length
        list_of_query_idf.append(query_term_idf)
        query_term_weight = query_term_freq_weight * query_term_idf # tf * idf
        
        # Term will be ignored if it does not exist in the dictionary (postings is empty list)
        if term_postings:
            for docID_termFreq_pair in term_postings:
                curr_docID = docID_termFreq_pair[0]
                doc_term_weight = get_log_term_freq_weighting(docID_termFreq_pair[1])
                
                # Dot product of query and doc term weights
                if not scores.has_key(curr_docID):
                    scores[curr_docID] = 0
                scores[curr_docID] += weight * query_term_weight * doc_term_weight

    # Normalization
    query_norm = get_query_unit_magnitude(list_of_query_idf)
    for docID in scores.keys():
        # Doc length can be obtained from the pickle object loaded from disk from dictionary.txt.
        norm_magnitude = query_norm * list_of_doc_lengths[str(docID)]
        scores[docID] = scores[docID] / norm_magnitude
    
    # Ranks the scores in descending order
    filtered_scores = {docID:tf_idf for docID,tf_idf in scores.items() if tf_idf != 0}
    ranked_scores = sorted(filtered_scores.items(), key = operator.itemgetter(1), reverse = True)
    list_top_10_docIDs = ranked_scores[:10]
    
    return [score_pair[0] for score_pair in ranked_scores]

"""
Computes the magnitude of the query vector for normalization.

list_of_query_idf    List of query term idf values.

return    Magnitude of the query vector.
"""
def get_query_unit_magnitude(list_of_query_idf):
    query_norm = 1;
    for idf_value in list_of_query_idf:
        if not idf_value == 0:
            query_norm *= math.pow(idf_value, 2)
    return math.sqrt(query_norm)

"""
Computes the term frequency log weights of each query term in the input.
Will compute duplicated query terms only once.

normalized_query_list    List of query terms which have been stemmed and case-
                         folded. Duplicate query terms are not filtered.

return    A mapping of term frequencies for each query term
"""
def compute_query_term_freq_weights(normalized_query_list):
    query_term_freq_map = {}
    for query_term in normalized_query_list:
        if not query_term_freq_map.has_key(query_term):
            query_term_freq_map[query_term] = \
                get_log_term_freq_weighting(normalized_query_list.count(query_term))
    return query_term_freq_map

"""
Computes the logarithmic frequency weight of a term

term_freq    Term frequency in a document.

return       Log term frequency weight.
"""
def get_log_term_freq_weighting(term_freq):
    if term_freq == 0:
        return 0;
    else:
        return 1 + math.log(term_freq, 10)

"""
Computes the idf of a query term.

term_postings    postings of a query term
N                Total number of documents in corpus.

return           Inverse doc frequency of a query term.
"""
def get_idf(term_postings, N):
    doc_freq = len(term_postings)
    if doc_freq == 0:
        # query term does not occur in ANY document and should not be regarded as weight
        return 0
    else: 
        return math.log(N / doc_freq, 10)

"""
Tokenizes and normalizes the query from a String format to a list of case-folded 
and stemmed query tokens.

query_text    Unnormalized query in String format

return        List of normalized tokens
"""
def normalize_tokens(query_text):
    stemmer = PorterStemmer()
    tokens_list = word_tokenize(query_text)
    normalized_token_list = []
    
    for token in tokens_list:
        normalized_token_list.append(stemmer.stem(token.lower()))
    
    return normalized_token_list
   
#=====================================================#
# Pre-processing functions:
# Loading the file-of-queries, loading the dictionary, loading a term's postings
# list and writing to output.
#=====================================================#

"""
Loads dictionary at startup from dictionary.txt.
This also loads the universal set of docIDs to be used in computing boolean queries.

return    dictionary map in the specified form of
          { term : [docFreq, value of pointer offset in postings file] }
"""
def load_dictionary():
    from_dict_file= open(dict_file, "r")
    dictionary_loaded = pickle.load(from_dict_file)
    
    # Loads the list of all docIDs used in our corpus, since it 
    # was transported from index.txt.
    global list_of_docIDs
    global list_of_doc_lengths
    list_of_docIDs = pickle.load(from_dict_file)
    list_of_doc_lengths = pickle.load(from_dict_file)
    
    from_dict_file.close()
    return dictionary_loaded

"""
Writes a list of docIDs to the output file located on disk
"""
def write_to_output_file(result_docIDs_list):
    with open(output_file, "a") as to_output_file:
        for docID in result_docIDs_list:
            to_output_file.write(str(docID))
            if not docID == result_docIDs_list[-1]:
                # No space will be written to the end of the query result line in 
                # the output file
                to_output_file.write(" ")
        to_output_file.write("\n")
     
"""
Returns the list of docIDs belonging to this term. If the query term is 
not found in the dictionary, an empty list will be returned

term      the term to be retrieved in String form

return    List of docIDs if term exists in dictionary
          Empty list if term does not exist in dictionary
"""
def load_postings_for_term(term):
    from_postings_file = open(postings_file, "r")
    docID_list = []
    
    if term in dictionary.keys():
        # A seek to the exact location of the pickle object representing 
        # this term's list of docIDs
        from_postings_file.seek(dictionary[term][1], 0)
        docID_list = pickle.load(from_postings_file)
    
    from_postings_file.close()
    return docID_list

"""
Interprets arguments of this search program
"""
def usage():
    print "error1"
    print "usage: " + sys.argv[0] + "-d dictionary-file -p postings-file " \
          "-q query_file_dir -o output-file-of-results"
    
dict_file = postings_file = query_file_dir = output_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError, err:
    print "error1"
    usage()
    sys.exit(2)
for out, a in opts:
    if out == '-d':
        dict_file = a
    elif out == '-p':
        postings_file = a
    elif out == '-q':
        query_file_dir = a
    elif out == '-o':
        output_file = a
    else:
        assert False, "unhandled option"
if dict_file == None or postings_file == None or query_file_dir == None or output_file == None:
    print "error1"
    usage()
    sys.exit(2)

"""
Test cases for the processQuery function
A String of valid query inputs should be used
The results of the test will be print to standard output on the console.

It is recommended to only perform a few tests at a time to obtain 
reasonably human-readable outputs.
"""
def test_query():
    print "test_query"
    
#=====================================================#
# Execution of Program
#=====================================================#
"""
Load the dictionary before processing search queries
"""
query = Query(query_file_dir) # Loads Query
list_of_docIDs = []
list_of_doc_lengths = []
dictionary = load_dictionary()

# Contains tf-idf weighting of query terms used in this search process
scores = {}

# Contains a list of (docID, tf-idf weight) tuples of the top 10 relevant docs
list_top_10_docIDs = []

"""
Main execution point after loading dictionary and queries from file-of-queries
"""
exec_search(query)

