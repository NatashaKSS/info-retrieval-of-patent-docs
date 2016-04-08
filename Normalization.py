import nltk
import string
from nltk.corpus import stopwords

# Some additional stop words specific to this corpus. The effect of stopping those words is still unclear.

"""
To normalize words by removing stop words.

Returns		the result of normalizing the words (will return None if term is a stopword)
"""

def normalize_remove_stop_words(word):
    word = word.lower()
    stop_word = True
    stops = set(stopwords.words('english'))
    PUNCTUATION = set(string.punctuation)
    
    if word in PUNCTUATION or (stop_word and word in stops):
        return None
    
    return word.lower()
