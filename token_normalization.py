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

class Normalizer():
    stemmer = PorterStemmer()
    
    """
    Some additional words we deem to be redundant which are specific to this corpus.
    Criteria for choosing these words:
        1.) Have little semantic meaning in the context of this corpus
        2.) If they were present in a +ve document or a -ve document, they would not have provided 
            a significant amount of 'judgement' on its relevance
    
    Not included: 
    Didn't agree with "treatment", "flow", "separ", "batteri"...etc
    
    Up for debate:
    "wash" (Note: this word does not emcompass terms like "washer", "backwash", "dishwash", etc.)
    "water" (May be too semantically meaningless)
    """
    censored_words = ["method", "includ", "use", "provid", "system", "one", "compris", \
                      "process", "invent", "contain", "remov", "least", "form", "system", "devic", \
                      "apparatu", "also", "gener", "treat", "present", "liquid", "first", "relat" \
                      "may", "materi", "organ", "second", "wherein", "allow", "perform", "therebi"\
                      "remove", "caus", "herein", "mechan"]
    
    def __init__(self):
        self.stop_words_NLTK_default = map(self.stemmer.stem, stopwords.words('english'))
        self.punctuations_default = string.punctuation
        
    """
    Normalizes tokens through case-folding and stemming using Porter's Stemmer.
    
    tokens_list    List of unnormalized tokens
    
    return         List of normalized tokens
    """
    def normalize_tokens(self, tokens_list):
        normalized_token_list = []
        
        for token in tokens_list:
            token = token.lower()
            if "-"in token:
                # We treat hyphenated tokens as separate tokens
                token_pair = token.split("-")
                for tok in token_pair:
                    if not self.is_redundant_word(tok):
                        normalized_token_list.append(self.stemmer.stem(tok))
            else:
                if not self.is_redundant_word(token):
                    normalized_token_list.append(self.stemmer.stem(token))
        return normalized_token_list
    
    """
    Determines if a word is a stop word from the NLTK library.
    
    word      The word to test in String format. Does not matter if in capital letters or not.
    
    return    True if the word is a stop word, false otherwise.
    """
    def is_redundant_word(self, word):
        word = self.stemmer.stem(word.lower())
        
        return (word in self.punctuations_default) or \
            (word in self.stop_words_NLTK_default) or \
            (word in self.censored_words)
