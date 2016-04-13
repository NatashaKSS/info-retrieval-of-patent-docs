#!/usr/bin/python
# Import standard modules

"""
NOTE NEED THESE MODULES TOGETHER WITH SUBMISSION:
xml_parser.py, token_normalization.py, ipc_patent_codes 

BUT NOT (AND PLEASE COMMENT OUT ALL TEST STATEMENTS HERE)
test_driver.py
"""
import sys
import getopt
import pickle
import operator

# Import modules for computation methods, xml parsing, token normalization and testing
from search_computation import Search_Compute
from token_normalization import Normalizer
from ipc_patent_codes import IPC_Patent
from xml_parser import Query
from xml_parser import Document
#from test_driver import TestDriver

# Import NLTK modules needed
from nltk.tokenize import word_tokenize

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
    global scores, ranked_scores_top_10
    # Wipe the output file before processing all the queries to ensure previous
    # runs of this program do not merely append the results to the end of the file
    with open(output_file, "w"):
        pass

    norm = Normalizer()
    normalized_query_list = norm.normalize_tokens(word_tokenize(query.get_description()))
    query_term_freq_map = s_compute.compute_query_tf_weight(normalized_query_list, None)

    # Remove duplicate query terms to process each term and compute relevant docIDs
    ranked_results = get_relevant_results(set(normalized_query_list), query_term_freq_map)
    
    # Query Expansion (Using IPC subclass description)
    new_normalized_query_list = \
        s_compute.combine_list(get_IPC_query_list(norm), get_doc_abstract_query_List(norm))
    combined_query_list = \
        s_compute.combine_list(normalized_query_list, new_normalized_query_list)
    query_term_freq_map = \
        s_compute.compute_query_tf_weight(normalized_query_list, new_normalized_query_list)

    # Query expansion - Computing results
    ranked_results = get_relevant_results(set(combined_query_list), query_term_freq_map)
    
    # Test Driver for debugging purposes
    #my_test = TestDriver(ranked_results)
    #my_test.process_results()
    
    write_to_output_file(ranked_results)

"""
Searches for results for the specified queries in ranked order.
Also updates the list of top 10 documents that are assumed to be relevant.

list_of_query_terms    List of query terms which are normalized and have no duplicates.
query_term_freq_map    A mapping of log term frequency weights for each query term.

return    List of docIDs that relevant to this query, sorted in descending order.
"""
def get_relevant_results(list_of_query_terms, query_term_freq_map):
    global ranked_scores_top_10
    scores = {}
    term_postings = {}
    list_of_query_idf = []
    
    for query_term in list_of_query_terms:
        term_postings["title"] = load_postings_for_term(query_term + ".title")
        term_postings["abstr"] = load_postings_for_term(query_term + ".abstr")
        
        query_term_idf = s_compute.get_idf(query_term, term_postings)
        query_term_weight = query_term_freq_map[query_term] * query_term_idf # tf * idf
        
        # Accumulate list of query idf values for computation of normalized query length
        list_of_query_idf.append(query_term_idf)
        
        # Weighted tf-idf scores (of the various zones, which each have differing weights)
        scores = s_compute.compute_weighted_score("title", term_postings, \
                                                  query_term_weight, scores)
        scores = s_compute.compute_weighted_score("abstr", term_postings, \
                                                  query_term_weight, scores)

    # Normalization of docID results vectors
    # TODO: Nat - Check if supposed to use query idf for query vector normalization? Note: Does not affect current results
    scores = s_compute.normalize_scores(scores, list_of_query_idf)
    
    # Ranks the scores in descending order and removes entries with score = 0
    ranked_scores = get_ranked_scores(scores)
    ranked_scores_top_10 = ranked_scores[:10]
    ranked_docIDs = [score_pair[0] for score_pair in ranked_scores]
    
    #print "TOP 50 Ranked scores and positions (position, score):"
    #print [(ranked_scores.index(docID_score_pair) + 1, docID_score_pair) for docID_score_pair in ranked_scores][:50]
    #print
    
    return ranked_docIDs

"""
Ranks the scores of all documents

return    List of (docID, tf-idf weight) tuples ranked against their weights
"""
def get_ranked_scores(scores):
    filtered_scores = {docID : tf_idf for docID, tf_idf in scores.items() if tf_idf != 0}
    ranked_scores = sorted(filtered_scores.items(), key = operator.itemgetter(1), reverse = True)
    return ranked_scores

#=====================================================#
# Query Expansion functions:
# Using IPC subclass and Top 10 document titles/abstracts
#=====================================================#

"""
IPC Query expansion: Finds the most frequently occurring IPC subclass

pos       Position of the IPC code to be retrieved from the ranked list

return    Best IPC subclass that occurs most frequently in the top 10 docs
"""
def get_best_IPC_code(pos):
    IPC_class_list = {}
    
    for doc_ID, doc_score in ranked_scores_top_10:
        ipc_class = get_docID_IPC(doc_ID)
        
        if ipc_class in IPC_class_list.keys():
            IPC_class_list[ipc_class] += 1
        else:
            IPC_class_list[ipc_class] = 1
    # This only gets the IPC class in the first position
    # best_IPC_code = max(IPC_class_list.iteritems(), key = operator.itemgetter(1))[0]
    best_IPC_code = sorted(IPC_class_list.items(), \
                           key = operator.itemgetter(1), reverse = True)[pos - 1][0]
    
    return best_IPC_code

"""
Gets the normalized list of query tems from the Top 2 IPC descriptions

norm       Normalizer object

return     List of IPC description terms that have been normalized
"""
def get_IPC_query_list(norm):
    ipc_patents = IPC_Patent()
    ipc_patent_description = ipc_patents.get_patent_description(get_best_IPC_code(1))
    ipc_patent_description += " " + ipc_patents.get_patent_description(get_best_IPC_code(2))
    
    normalized = norm.normalize_tokens(word_tokenize(ipc_patent_description))

    return normalized

"""
Obtains the abstract of the top 10 documents and gels them to form a new query list.
Parses the XML document of the top 10 documents from disk.

return    List of document abstract terms that have been normalized
"""
def get_doc_abstract_query_List(norm):
    ranked_top_10_doc_list = map(operator.itemgetter(0), ranked_scores_top_10)
    result_query = ""
    count  = 0 
    synonym_words_list = []
    
    for docID in ranked_top_10_doc_list:
        if dir_of_docs.endswith("/"):
            docID_file_dir = dir_of_docs + docID + ".xml"
        else:
            docID_file_dir = dir_of_docs + "/" + docID + ".xml"
            
        xml_doc = Document(docID, docID_file_dir)
        title = xml_doc.get_title()
        result_query +=  title + " "
        
        # Adds synonyms for the top ranked document's title to new query
        if count < 5:
            title_words = word_tokenize(title)
            for w in title_words:
                synonym_words_list = norm.combine_list(synonym_words_list, norm.get_synonym_list(w))
        
        #if count == 0: # Only get abstract from top document(s)
        #    result_query += xml_doc.get_abstract() + " "
        
        count += 1
        
    result_query_list = word_tokenize(result_query)
    result_query_list = norm.combine_list(result_query_list, synonym_words_list)
    normalized = norm.normalize_tokens(result_query_list)
    return normalized

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
    
    # Also load { docID : [docLength, IPC code] }, transported from index.py
    global list_doc_length_IPC
    list_doc_length_IPC = pickle.load(from_dict_file)
    
    global dir_of_docs
    dir_of_docs = pickle.load(from_dict_file)
    
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
                # No space at the end of the query result line in output file
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
        from_postings_file.seek(dictionary[term][1], 0)
        docID_list = pickle.load(from_postings_file)
    
    from_postings_file.close()
    return docID_list

def get_docID_length(docID):
    return list_doc_length_IPC[docID][0]

def get_docID_IPC(docID):
    return list_doc_length_IPC[docID][1]

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

#=====================================================#
# Execution of Program
#=====================================================#
# Load the dictionary before processing search queries
query = Query(query_file_dir) # Loads Query XML
dir_of_docs = "" # Directory of corpus documents for access
list_doc_length_IPC = {} # { docID : [doc_length, IPC code] } mapping
dictionary = load_dictionary()
len_docIDs = len(list_doc_length_IPC.keys())

# Sets up computation methods
s_compute = Search_Compute(len_docIDs, list_doc_length_IPC)

# Contains tf-idf weighting of query terms used in this search process
scores = {}

# Contains a list of (docID, tf-idf weight) tuples of the top 10 relevant docs
ranked_scores_top_10 = []

# Main execution point after loading dictionary and queries from file-of-queries
exec_search(query)

