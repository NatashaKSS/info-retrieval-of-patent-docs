#!/usr/bin/python
# Import standard modules
import math
import operator

# Import NLTK modules needed
import nltk
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize

# Import collection modules needed
from collections import Counter
#======================================================================#
# Program Description:
# Expands query using PRF and IPC based on the top k ranked documents
# retrieved from the first round of querying
#  
# Result of query expansion will be used for the second round of querying
#
# Additionally, optimal weights will be assigned according to the expanded
# query's term's importance.
#
#======================================================================#

class QueryExpansion:

	def __init__(self, dictionary, positions, postings, n):
		self.n = n
		self.dictionary = dictionary
		self.positions = positions
		self.postings = postings
	
	""" IMPT : pseudo relevance feed back
	Find new query terms from the top previously retrieved documents 
	
	old_query			original query list from the first search
	terms_num			number of query terms that is to be generated
	initial_results		top ranked documents (1st round) to retrieve the
						new query terms
				
	Returns				words with the highest weight from the previously 
						retrieved documents
	"""	
	def expand_old_query(self, terms_num, old_query, initial_results):
		document_content = self.get_content(initial_results)
		new_query_terms = self.get_new_query_terms(document_content, old_query,terms_num)
		weighted_query = self.get_term_frequency(new_query_term, old_query)
		
		return weighted_query
	
	""" IMPT: pseudo relevance
	Gets a list with all the content from title and abstract of retrieved
	documents
	
	initial_results		top ranked documents
	
	Returns				list with all the words of the top ranked documents
	"""
	def get_content(self, initial_results):
		document_content = ''
		
		#Get list of content
		for doc_name, score in initial_results:
			document_content+= #get title 
			document_content+= #get abstract
				
		return separate_token(document_content)
	
	"""
	Convert a string into a list of tokens
	
	string_to_token		the string to be tokenized
	
	Returns				list with tokens
	"""	
	def separate_token(self, string_to_token):
		token_list = []
		sentences = sent_tokenize(string_to_token)
		for sent in sentences:
			tokens = word_tokenize(sent)
			for token in tokens:
				token_list.append(token)
		return token_list
	
	"""
	Using the words from the 1st round of retrieved documents, compute the 
	tf of each word in the query list
	
	document_content		list of words from the document
	old_query				list of words from the old query
	terms_num				number of new query terms to be generated
	
	Returns					tf of 
	"""	
	def get_new_query_terms(self, document_content, old_query, terms_num):
		count = Counter(document_content)
		highest_score_terms = self.get_highest_scores(count, terms_num)
		
		return highest_score_terms
	
	"""
	Calculating the new combined query's weight by assigning different weights
	tf for the old and new query terms
	
	new_query_term			list of new query terms
	old_query				list of words from the old query

	Returns					list of tf of the old and new query terms
	"""	
	def get_term_frequency(self, new_query_term, old_query):
		
		count_old = Counter(old_query)
        new_weights = {}
        
        for term in new_query_term:
            new_weights[term] = 0.5
            
        for term in old_query:
            if term in new_query_term:
                new_weights[term] = self.cal_tf(count_old[term])*1.5
            else:
                new_weights[term] = self.cal_tf(count_old[term])
        
        return new_weights
	
	
	"""
	Compute the weights of the words
	
	count			dictionary of the new query list words with their 
					frequency in the query
	terms_num		number of new query terms to be generated
	
	Returns			list of terms with the highest weights
	"""
	def get_highest_scores(self, count, terms_num):
		weights = {}
		for term, num in count.items():
			weight = self.get_term_weight(PorterStemmer.stem(term), num)
			weights[term] = weight
		highest_scores = [i[0] for i in sorted(weights.items(), key=operator.itemgetter(1), reverse=True)][:terms_num]
		return highest_scores
		
	def get_term_weight(self, term, num):
		if term in self.dictionary.keys():
			(tf, postings) = self.dictionary[term]
			
			idf = math.log10(float(self.n)/float(tf))
			return compute(num) * idf
		else:
			return 0
	"""
	Find new query terms using IPC
	
	
	"""
	def IPC_query(self, old_query, terms_num, initial_results, patent_num):
	
	
	
	"""
	Computes the term frequency

	"""	
	def cal_tf(self, count):
		return 1+math.log10(count)