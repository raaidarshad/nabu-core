from datetime import datetime

from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfTransformer


# TODO this is a temporary file just to work and write out the business logic, will be moved elsewhere soon


def get_counts(date_threshold: datetime) -> csr_matrix:
    # TODO hits db for relevant articles/counts and puts them in desirable form
    pass


def compute_tfidf(counts: csr_matrix) -> csr_matrix:
    # takes the input count matrix and computes the corresponding tfidf matrix
    return TfidfTransformer().fit_transform(counts)


def compute_similarities(tfidfs: csr_matrix) -> csr_matrix:
    # multiplies the tfidf matrix by its inverse, resulting in a cosine similarity matrix where element (a, b)
    # indicates the similarity between between article a and article b. All values are between 0 and 1. If the tfidfs
    # matrix is an N x M matrix, the output is N x N
    return tfidfs.dot(tfidfs.transpose())


def filter_similarities(similarities: csr_matrix, threshold: float) -> csr_matrix:
    # returns the cosines sparse matrix but only includes elements that are above the specified threshold. Keeps same
    # shape
    return similarities.multiply(similarities >= threshold)


def group_articles(similarities: csr_matrix):
    # TODO given similarities, spit out the groups of articles
    pass
