import nltk
import string
from nltk.corpus import stopwords



# Some additional stop words specific to this corpus. The effect of stopping those words is still unclear.
stops |= {'mechanism', 'technology', 'technique', 'using', 'means', 'apparatus', 'method', 'system', 'perform', 'include'}

"""
To normalize words by removing stop words.

Returns		the result of normalizing the words (will return None if term is a stopword)
"""

def normalize(word):

	stop_word = TRUE
	stops = set(stopwords.words('english'))
	PUNCTUATION = set(string.punctuation)

    if word in PUNCTUATION or (stop_words and word in stops):
        return None

    return word