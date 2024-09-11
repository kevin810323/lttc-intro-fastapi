from sklearn.base import BaseEstimator, TransformerMixin
from nltk.tokenize import sent_tokenize
from nltk.tokenize import TweetTokenizer
import pandas as pd


def word_tokenize(text):
    tokenizer = TweetTokenizer()
    words = tokenizer.tokenize(text)
    words = [word for word in words if word not in '.,']
    return words

class StatisticalFeatureTransformer(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def statisical_features(self, text):
        sents = sent_tokenize(text)
        words = word_tokenize(text)

        sent_count = len(sents)
        word_count = len(words)
        avg_sent_word_count = sum([len(word_tokenize(sent)) for sent in sents]) / sent_count
        avg_word_length = sum([len(word) for word in words]) / word_count
        vocab_size = len(set(words))

        return {
            'word_count': word_count,
            'sentence_count': sent_count,
            'avg_sent_word_count': avg_sent_word_count,
            'avg_word_length': avg_word_length,
            'vocab_size': vocab_size
        }

    def get_feature_names_out(self, feature_names_in_):
        return ['word_count', 'sentence_count', 'avg_sent_word_count', 'avg_word_length', 'vocab_size']

    def fit(self, X, y=None):
        # Implement the fitting logic here
        return self

    def transform(self, X):
        # Implement the transformation logic here
        texts = X['text']
        features = []
        for text in texts:
            features.append(self.statisical_features(text))
        statistical_df = pd.DataFrame.from_records(features)
        return statistical_df
