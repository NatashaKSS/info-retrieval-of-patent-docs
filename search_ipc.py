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
import operator

# Import modules for xml parsing, token normalization and testing
from token_normalization import normalize_tokens
from xml_parser import Query
from test_driver import TestDriver

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
    # Wipe the output file before processing all the queries to ensure previous
    # runs of this program do not merely append the results to the end of the file
    with open(output_file, "w"):
        pass

    # Normalize query list with case-folding, stemming and stop word removal
    normalized_query_list = normalize_tokens(word_tokenize(query.get_description()))
    
    # Term frequencies of query terms for processing    
    query_term_freq_map = compute_query_term_freq_weights(normalized_query_list)
    
    # Remove duplicate query terms to process each term
    # This first round of searching (using the user's input query) holds a weight of 0.75
    # 2nd round of searching should use 0.25 weight
    ranked_results = get_relevant_results(set(normalized_query_list), query_term_freq_map, 0.75)
    
    # Test Driver for debugging purposes
    my_test = TestDriver(ranked_results)
    my_test.process_results()
    
    # NOTE:
    # Query Expansion HEREEEE
    # You can use ranked_scores_top_10 (a global variable) 
    # which contains (docID, tf-idf weight) tuples of the top 10 relevant docs
    
    # TODO: Query Expansion using IPC using top 10 results
    new_query_list = query_expansion_IPC(ranked_results, 120, normalized_query_list)

    
    # Normalize new query list with case-folding, stemming and stop word removal
    normalized_new_query_list = normalize_tokens(new_query_list)
    
    # Remove duplicate query terms to process each term
    # This is the actual final query
    ranked_results = get_relevant_results(set(normalized_new_query_list), query_term_freq_map, 0.25)
    
    
    write_to_output_file(ranked_results)


""" IMPT!!!!
IPC Query expansion: Find the new final query using IPC

initial_results			Results generated from the first round of search
num_terms				Number of new query terms to be generated
old_query				Original normalized query list in the first round of search

Returns:				Weighted new query dictionary
"""
def query_expansion_IPC(initial_results, num_terms, old_query_list):
	 
	# TODO: Get the most frequently occurring IPC_class
	best_IPC_class = get_best_IPC_class(initial_results)#use get top 10
	
	# Get the content for patent in best_IPC_class
	patent_content = get_patent_content(best_IPC_class)
	
	# Get list of words of patent with highest weights
	weighted_new_query_terms = get_new_query_terms(patent_content, old_query_list, num_terms)
	
	# Assign different term frequencies to new and old query terms accordingly
	weighted_query = get_term_frequency(weighted_new_query_terms, old_query_list)
	
	return weighted_query

""" IMPT!!!
Calculating the new combined query's weight by assigning different weights
tf for the old and new query terms
	
new_query_term			list of new query terms
old_query				list of words from the old query

Returns					list of tf of the old and new query terms
"""	
def get_term_frequency(new_query_term, old_query_list):
		
	count_old = Counter(old_query_list)
    new_weights = {}
        
    for term in new_query_term:
        new_weights[term] = 0.5
            
    for term in old_query_list:
        if term in new_query_term:
             new_weights[term] = cal_tf(count_old[term])*1.5
        else:
             new_weights[term] = cal_tf(count_old[term]) *1.0 
    
    return new_weights
	

"""
Using the patent words from the 1st round of search operation, compute the tf of each 
word in the query list
	
patent_content			list of words from the patent description
old_query				list of words from the old query
terms_num				number of new query terms to be generated
	
Returns					list of words from the patent_content with highest weights
"""	
def get_new_query_terms(patent_content, old_query, terms_num):
	count = Counter(patent_content)
	highest_score_terms = get_highest_scores(count, terms_num)
		
	return highest_score_terms
	
	
""" soso
Compute the weights of the words
	
count				dictionary of the new query list words with their 
					frequency in the query
terms_num			number of new query terms to be generated
		
Returns				list of terms with the highest weights
"""
def get_highest_scores(count):
	weights = {}
	for term, num in count.items():
		weight = get_term_weight(PorterStemmer.stem(term), num)
		weights[term] = weight
	highest_scores = [i[0] for i in sorted(weights.items(), key=operator.itemgetter(1), reverse=True)]
	return highest_scores

	
"""
Compute the weights of the words
	
count				dictionary of the new query list words with their 
					frequency in the query
terms_num			number of new query terms to be generated
	
Returns				list of terms with the highest weights
"""	
def get_term_weight(term, num):
	if term in dictionary.keys():
		(tf, postings) = dictionary[term]
			
		idf = math.log10(float(n)/float(tf))
		return compute(num) * idf
	else:
		return 0	

""" IMPT!!!
IPC Query expansion: Finds the most frequently occurring IPC subclass

initial_results		Original results after first round of search

Returns				Best IPC subclass that occurs most frequently in the top 10 docs
"""
def get_best_IPC_class(initial_results):
	IPC_class_list = {}
	
	for doc_ID, score in initial_results:
		ipc_class = get_docID_IPC(doc_ID)	#Q1: is this for getting the ipc class of the documents?
		
		if ipc_class in IPC_class_list.keys():
			IPC_class_list[ipc_class] += 1
		else:
			IPC_class_list[ipc_class] = 1
	
	return max(IPC_class_list.iteritems(), key = operator.itemgetter(1))[0]	
	

"""
Convert a string into a list of tokens
	
string_to_token		the string to be tokenized
	
Returns				list with tokens
"""	
def separate_token(string_to_token):
	token_list = []
	sentences = sent_tokenize(string_to_token)
	for sent in sentences:
		tokens = word_tokenize(sent)
		for token in tokens:
			token_list.append(token)
	return token_list

"""
Computes the term frequency

"""	
def cal_tf(self, count):
	return 1+math.log10(count)	

"""
Searches for results for the specified queries in ranked order.
Also updates the list of top 10 documents that are assumed to be relevant.

list_of_query_terms    List of query terms which are normalized and have no duplicates.
query_term_freq_map    A mapping of log term frequency weights for each query term.
weight                 A fractional weight of choice to give to this tf-idf score.
                       0 < weight <= 1.

return    List of docIDs that relevant to this query, sorted in descending order.
"""
def get_relevant_results(list_of_query_terms, query_term_freq_map, weight):
    global ranked_scores_top_10
    scores = {}
    term_postings = {}
    list_of_query_idf = []
    
    for query_term in list_of_query_terms:
        term_postings["title"] = load_postings_for_term(query_term + ".title")
        term_postings["abstr"] = load_postings_for_term(query_term + ".abstr")
        #term_postings["IPC"] = load_postings_for_term(query_term + ".IPC") # To be used for IPC subclass
        
        query_term_idf = get_idf(query_term, term_postings)
        query_term_weight = query_term_freq_map[query_term] * query_term_idf # tf * idf
        
        # Accumulate list of query idf values for computation of normalized query length
        list_of_query_idf.append(query_term_idf)
        
        # Weighted tf-idf scores (of the various zones, which each have differing weights)
        scores = compute_weighted_score("title", term_postings, query_term_weight, scores)
        scores = compute_weighted_score("abstr", term_postings, query_term_weight, scores)

    # Normalization of docID results vectors
    # TODO: Nat - Check if supposed to use query idf for query vector normalization? Note: Does not affect current results
    scores = normalize_scores(scores, list_of_query_idf, weight)
    
    # Ranks the scores in descending order and removes entries with score = 0
    ranked_scores = get_ranked_scores(scores)
    ranked_scores_top_10 = ranked_scores[:10]
    ranked_docIDs = [score_pair[0] for score_pair in ranked_scores]
    
    print "TOP 50 Ranked scores and positions (position, score):"
    print [(ranked_scores.index(docID_score_pair) + 1, docID_score_pair) for docID_score_pair in ranked_scores][:50]
    print
    
    return ranked_docIDs

"""
Computes the weighted tf-idf score for a docID given in a specific postings 
list.

zone_type            "title", "abstr" section specifiers for the document.
term_postings        Postings list of a query term
query_term_weight    Query term score
scores               Mapping of { docID : current score }
                     
return    New updated mapping of scores for { docID : score }
"""
def compute_weighted_score(zone_type, term_postings, query_term_weight, scores):
    # Term will be ignored if it does not exist in the dictionary in all zones (postings are empty)
    if term_postings[zone_type] is not None:
        for docID_termFreq_pair in term_postings[zone_type]:
            curr_docID = docID_termFreq_pair[0]
            term_freq = docID_termFreq_pair[1]
            
            # Document score weighted against its zone type
            doc_term_weight = get_log_term_freq_weighting(term_freq) * zone_weights[zone_type]
            
            # Dot product of query and doc term weights
            if not scores.has_key(curr_docID):
                scores[curr_docID] = 0
            scores[curr_docID] += query_term_weight * doc_term_weight
    return scores

"""
Ranks the scores of all documents

return    List of (docID, tf-idf weight) tuples ranked against their weights
"""
def get_ranked_scores(scores):
    filtered_scores = {docID : tf_idf for docID, tf_idf in scores.items() if tf_idf != 0}
    ranked_scores = sorted(filtered_scores.items(), key = operator.itemgetter(1), reverse = True)
    return ranked_scores

"""
Computes the idf of a query term.

query_term       Query term in String format
term_postings    Query term's postings across all zone types

return           Inverse doc frequency of a query term.
"""
def get_idf(query_term, term_postings):
    doc_freq = 0

    # Make a big postings list joining each zone-specific postings for query idf computation
    term_postings_all = list(term_postings["title"])
    term_postings_all.extend(term_postings["abstr"])
    
    if term_postings_all is not None:
        combined_term_postings = set([docID_termFreq_pair[0] \
                                      for docID_termFreq_pair in term_postings_all])
        doc_freq = len(combined_term_postings)
    if doc_freq == 0:
        # query term does not occur in ANY doc and should not have weight
        return 0
    else:
        return math.log(float(len_list_of_docIDs) / doc_freq, 10)
  
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
Computes the normalization of tf-idf scores for all result docIDs.

scores               Mapping of { docID : score }
list_of_query_idf    List of idf values for the query vectors
weight               Weight the current search iteration may use. If the current search 
                     iteration is unweighted, specify weight = 1.0.
                     
return    New updated mapping of { docID : score } normalized
"""
def normalize_scores(scores, list_of_query_idf, weight):
    query_norm = get_query_unit_magnitude(list_of_query_idf)
    for docID in scores.keys():
        # Doc length can be obtained from the pickle object loaded from disk from dictionary.txt.
        norm_magnitude = query_norm * get_docID_length(docID)
        scores[docID] = (scores[docID] / norm_magnitude) * weight
    return scores
     
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
    
    # Also load the list of all docIDs, transported from index.txt
    global list_doc_length_IPC
    list_doc_length_IPC = pickle.load(from_dict_file)
    
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
query = Query(query_file_dir) # Loads Query
list_doc_length_IPC = {}
dictionary = load_dictionary()
len_list_of_docIDs = len(list_doc_length_IPC.keys())

# All element values should sum to 1.0
# "abstr" represents "abstract"
zone_weights = { "title" : 0.6, "abstr" : 0.4 }

# Contains tf-idf weighting of query terms used in this search process
scores = {}

# Contains a list of (docID, tf-idf weight) tuples of the top 10 relevant docs
ranked_scores_top_10 = []

# Main execution point after loading dictionary and queries from file-of-queries
exec_search(query)

