#!/usr/bin/python
# Import standard modules
import string

# Import NLTK modules needed
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from perceptron import PerceptronTagger
#from nltk.tag.perceptron import PerceptronTagger

#======================================================================#
# Program Description:
# Normalizes a list of tokens.
# Applies stemming, case-folding and removal of stop words (specified 
# by NLTK library). Can also retrieve a word's synonyms.
#======================================================================#

class Normalizer():
    stemmer = PorterStemmer()
    tagger = PerceptronTagger() # For part-of-speech tagging
    
    """
    Some additional words we deem to be redundant which are specific to this corpus.
    Criteria for choosing these words:
        1.) Have little semantic meaning in the context of this corpus
        2.) If they were present in a +ve document or a -ve document, they would not have provided 
            a significant amount of 'judgement' on its relevance
    
    Not included: 
    Didn't agree with "treatment", "flow", "separ", "system", "remove", "gener", "batteri"...etc
    """
    # Note: A smaller set from the words in the above list
    censored_words = ["method", "process", "includ", "use", "provid", "compris", "device", \
                      "apparatu", "mechan", "also", "treat", \
                      "relat", "may", "wherein", "allow", \
                      "therebi", "caus", "herein"]
    
    def __init__(self):
        self.stop_words_NLTK_default = set(map(self.stemmer.stem, stopwords.words('english')))
        self.punctuations_default = string.punctuation
        
    """
    Normalizes tokens through case-folding and stemming using Porter's Stemmer.
    
    tokens_list    List of unnormalized tokens
    return         List of normalized tokens
    """
    def normalize_tokens(self, tokens_list):
        normalized_token_list = []
        tokens_list_POS = self.tagger.tag(tokens_list)
        
        for token, part_of_speech in tokens_list_POS:
            token = token.lower()
            if part_of_speech == "NN": # Only nouns will be processed
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
    Determines if a word is a redundant word based on the below categories:
    - Is a punctuation point
    - Is a stop word
    - Is in our list of words deemed to be semantically insignificant
    - Begins with a backslash
    
    word      The word to test in String format. Does not matter if in capital 
              letters or not. This word will be stemmed and lowercased.
    return    True if the word is a redundant word, false otherwise.
    """
    def is_redundant_word(self, word):
        word = self.stemmer.stem(word.lower())
        
        return (word in self.punctuations_default) or \
            (word in self.stop_words_NLTK_default) or \
            (word in self.censored_words) or\
            (word.startswith("\\"))
    
    """
    Gets a list of synonyms of a word if they exist in NLTK wordnet.
    
    word      Word to get synonyms for
    return    List of synonyms for word
    """
    def get_synonym_list(self, word):
        word = word.lower()
        synonym_list = []
        for i, lemma_list in enumerate(wordnet.synsets(word)):
            synonym_list = self.combine_list(synonym_list, lemma_list.lemma_names())
        return synonym_list
    
    """
    [DEPRECATED] PERFORMANCE ISSUES and LACK OF SIGNIFICANT RESULTS
    Determines if a word is a noun.
    
    word      Word to check
    return    True if this word is a noun, False otherwise 
    """
    """
    def is_noun(self, word):
        if (word == "") or (word is None):
            return False
        else:
            POS_symbol = self.tagger.tag([word])[0]
            return POS_symbol[1] == "NN"
    """
        
    #======================================================================#
    # Auxillary helper functions:
    #======================================================================#
    
    """
    Makes a copy of list1 and appends the contents of list2 to it
    
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


