from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import CountVectorizer
from nltk.tokenize import TweetTokenizer
import numpy as np
import pandas as pd
import requests
import json

def word_tokenize(text):
    tokenizer = TweetTokenizer()
    words = tokenizer.tokenize(text)
    words = [word for word in words if word not in '.,']
    return words

class ErrorFeatureTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, gec_api_url, errors_cache = None):
        self.vectorizer = CountVectorizer(token_pattern=r"\S+")
        self.gec_api_url = gec_api_url
        self.errors_cache = errors_cache
    
    def get_feature_names_out(self, feature_names_in_):
        return np.append(self.vectorizer.get_feature_names_out(), ['error_counts', 'error_percent'])
    
    def call_gec_api(self, text :str, url: str):
        res = requests.post(url, json={"text": text})
        res = json.loads(res.text)
        return res["edits"]
    
    def get_errors_texts(self, texts):
        def remove_prefix(error_code):
            return ':'.join(error_code.split(':')[1:])

        errors_texts = []
        for text in texts:
            if self.errors_cache and text in self.errors_cache:
                errors = self.errors_cache[text]
            else:
                errors = self.call_gec_api(text, self.gec_api_url)
            errors_text = ' '.join([remove_prefix(error['code']) for error in errors])
            errors_texts.append(errors_text)
        return errors_texts

    def fit(self, X, y=None):
        errors_texts = self.get_errors_texts(X['text'])
        self.vectorizer.fit(errors_texts)
        return self

    def transform(self, X):
        # Implement the transformation logic here
        errors_texts = self.get_errors_texts(X['text'])
        error_type_counts = self.vectorizer.transform(errors_texts).toarray()
        column_names = self.vectorizer.get_feature_names_out()
        errors_df = pd.DataFrame.from_records(error_type_counts, columns=column_names)
        
        error_counts = error_type_counts.sum(axis=1)
        word_counts = [len(word_tokenize(text)) for text in X['text']]
        errors_df['error_counts'] = error_counts
        errors_df['error_percent'] = error_counts / word_counts
        
        return errors_df
