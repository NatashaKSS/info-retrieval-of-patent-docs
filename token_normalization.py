#!/usr/bin/python
# Import standard modules
import string

# Import NLTK modules needed
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

#======================================================================#
# Program Description:
# Normalizes a list of tokens.
# Applies stemming, case-folding and removal of stop words (specified 
# by NLTK library).
#======================================================================#

"""
Normalizes tokens through case-folding and stemming using Porter's Stemmer.

tokens_list    List of unnormalized tokens

return         List of normalized tokens
"""
def normalize_tokens(tokens_list):
    stemmer = PorterStemmer()
    normalized_token_list = []
    
    for token in tokens_list:
        token = token.lower()
        if not is_stop_word(token):
            normalized_token_list.append(stemmer.stem(token))
    
    return normalized_token_list

"""
Determines if a word is a stop word from the NLTK library.

word      The word to test in String format. Does not matter if in capital letters or not.

return    True if the word is a stop word, false otherwise.
"""
# Some additional stop words specific to this corpus. The effect of stopping those words is still unclear.
# ... add here ...?
def is_stop_word(word):
    word = word.lower()
    stops = set(stopwords.words('english'))
    punct = set(string.punctuation)
    
    return (word in punct) or (word in stops)
