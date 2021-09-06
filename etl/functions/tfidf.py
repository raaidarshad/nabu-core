from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfTransformer


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


def main():
    # MIGHT NEED STUFF FROM counts.py
    # TF IDF
    tfidfs = compute_tfidf(sparse_counts)
    # now it is a csr_matrix with the same col/row indices but the values are tfidf, so same shape diff vals
    similarities = compute_similarities(tfidfs)
    # was N x M, now N x N where value at (i, j) shows the similarity between article i and j
    filtered = filter_similarities(similarities, 0.45)
    # removes values from the sparse matrix that are below the similarity value
