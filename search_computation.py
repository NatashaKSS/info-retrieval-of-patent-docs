#!/usr/bin/python

# Import standard modules
import math

#======================================================================#
# Program Description:
# Responsible for the search computations in search.py
# Contains methods for tf-idf weight computation and vector normalization.
#======================================================================#
class Search_Compute:
    len_docIDs = 0
    list_doc_length_IPC = {}
    
    def __init__(self, list_of_docID_len, list_doc_length_IPC):
        self.len_docIDs = list_of_docID_len
        self.list_doc_length_IPC = list_doc_length_IPC
    
    def get_docID_length(self, docID):
        return self.list_doc_length_IPC[docID][0]

    def get_docID_IPC(self, docID):
        return self.list_doc_length_IPC[docID][1]
    
    #==================================================================#
    # Computation methods
    #==================================================================#

    """
    Computes the idf of a query term.
    
    query_term       Query term in String format
    term_postings    Query term's postings across all zone types
    
    return           Inverse doc frequency of a query term.
    """
    def get_idf(self, query_term, term_postings):
        doc_freq = 0
    
        # Make a big postings list joining each zone-specific postings for query idf computation
        term_postings_all = self.combine_list(term_postings["title"], term_postings["abstr"])
        
        if term_postings_all is not None:
            combined_term_postings = set([docID_termFreq_pair[0] \
                                          for docID_termFreq_pair in term_postings_all])
            doc_freq = len(combined_term_postings)
        if doc_freq == 0:
            # query term does not occur in ANY doc and should not have weight
            return 0
        else:
            return math.log(float(self.len_docIDs) / doc_freq, 10)
    
    """
    Computes the term frequency log weights of each query term in the input.
    Will compute for duplicated query terms only once.
    
    Precondition: 
    All query terms passed in must be already be normalized.
    Duplicate query terms must not be filtered from the list of query terms.
    
    Arguments:
    old_normalized_list    List of query terms performed at the first search operation
    new_normalized_list    List of query terms performed at the query expansion
                           Specify None if only doing the first search operation
    
    return    A mapping of term frequencies for each query term
    """
    def compute_query_tf_weight(self, old_normalized_list, new_normalized_list):
        query_term_freq_map = {}
        combined_list = list(old_normalized_list)
        
        if not new_normalized_list is None: # Checks if we are doing query expansion now
            combined_list.extend(new_normalized_list)
            for query_term in new_normalized_list:
                if not query_term in old_normalized_list:
                    # This is a completely new query term due to Query Expansion
                    if not query_term_freq_map.has_key(query_term): # Checks for duplicate keys
                        query_term_freq_map[query_term] = \
                            self.get_log_tf_weight(combined_list.count(query_term)) * 0.5
        
        for query_term in old_normalized_list:
            if not query_term_freq_map.has_key(query_term): # Checks for duplicate keys
                if not (new_normalized_list is None) and (query_term in new_normalized_list):
                    # If the term is also in the new query list, it is "more important"
                    weight = 2.0
                else:
                    # If the term was in the original old query list and is not new
                    weight = 1.0
                query_term_freq_map[query_term] = \
                    self.get_log_tf_weight(combined_list.count(query_term)) * weight
        
        return query_term_freq_map
    
    """
    Computes the logarithmic frequency weight of a term.
    
    term_freq    Term frequency in a document.
    
    return       Log term frequency weight.
    """
    def get_log_tf_weight(self, term_freq):
        if term_freq == 0:
            return 0;
        else:
            return 1 + math.log(term_freq, 10)
    
    """
    Computes the normalization of tf-idf scores for all result docIDs.
    
    scores               Mapping of { docID : score }
    list_of_query_idf    List of idf values for the query vectors
                         
    return    New updated mapping of { docID : score } normalized
    """
    def normalize_scores(self, scores, list_of_query_idf):
        query_norm = self.get_query_unit_magnitude(list_of_query_idf)
        for docID in scores.keys():
            # Doc length can be obtained from the pickle object loaded from disk
            if not (self.get_docID_length(docID) == 0):
                norm_magnitude = query_norm * self.get_docID_length(docID)
                scores[docID] = (scores[docID] / norm_magnitude)
        return scores
    
    """
    Computes the magnitude of the query vector for normalization.
    
    list_of_query_idf    List of query term idf values.
    
    return    Magnitude of the query vector.
    """
    def get_query_unit_magnitude(self, list_of_query_idf):
        query_norm = 1;
        for idf_value in list_of_query_idf:
            if not idf_value == 0:
                query_norm *= math.pow(idf_value, 2)
        return math.sqrt(query_norm)
    
    #======================================================================#
    # Auxillary helper functions:
    #======================================================================#
    
    """
    Combines a copy of the contents of a list and appends a copy of the contents 
    of the operand list to it.
    
    list1    Base
    list2    List to append to list1
    
    return    Combined list of list1 and list2
    """ 
    def combine_list(self, list1, list2):
        if not list2 is None:
            combined = list(list1)
            combined.extend(list2)
            return combined
        else:
            return list1

