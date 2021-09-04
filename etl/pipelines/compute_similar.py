from datetime import datetime
from uuid import UUID

from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import breadth_first_order
from sklearn.feature_extraction.text import TfidfTransformer
from sqlalchemy.orm import Session

from etl.models import Article, Count


# TODO this is a temporary file just to work and write out the business logic, will be moved elsewhere soon
def numerify(target: list) -> tuple[list, dict]:
    deduped = list(set(target))
    target_to_index = {t: idx for idx, t in enumerate(deduped)}
    index_to_target = {v: k for k, v in target_to_index.items()}
    return [target_to_index[t] for t in target], index_to_target


def get_counts(datetime_threshold: datetime, db_client: Session) -> tuple[list, list, list]:
    db_counts: list[Count] = db_client.query(Count). \
        join(Article.id). \
        filter(Article.published_at >= datetime_threshold).all()

    counts, ids, terms = zip(*[(dbc.count, dbc.article_id, dbc.term) for dbc in db_counts])
    return counts, ids, terms


def get_article_map(datetime_threshold: datetime, db_client: Session) -> dict[UUID, Article]:
    db_articles: list[Article] = db_client.query(Article).\
        filter(Article.published_at >= datetime_threshold).all()

    return {dba.id: Article(**dba.__dict__) for dba in db_articles}


def counts_to_matrix(counts: list[int], rows: list[int], cols: list[int]) -> csr_matrix:
    return csr_matrix((counts, (rows, cols)))


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


def clusterify(similarities: csr_matrix) -> set[frozenset[int]]:
    return {frozenset(breadth_first_order(similarities, idx, directed=False, return_predecessors=False)) for idx in
            range(similarities.shape[0])}


def prep_clusters(clusters: set[frozenset[int]], index_to_article: dict, tfidf: csr_matrix) -> dict[int, list[Article]]:
    # each cluster is a list of articles by index
    # convert to list of a article ids
    # grab the article content for those ids
    prepped = {}
    for idx, article_num_ids in enumerate(clusters):
        articles = [index_to_article[article_num_id] for article_num_id in article_num_ids]
        # get the rows of this clusters articles from the tfidf matrix and get the mean tfidf value for each term
        # target_rows = tfidf[article_num_ids, :].mean(axis=0).tolist()[0]
        # sort the resulting list from highest to lowest, take the first N elements as keyword indices
        # target_rows.sort(reverse=True)[:5]

        prepped[idx] = articles

    return prepped


def main():
    threshold = datetime.now()
    counts, ids, terms = get_counts(threshold, "")
    id_to_article = get_article_map(threshold, "")
    index_article_ids, index_to_id = numerify(ids)
    index_terms, index_to_term = numerify(terms)
    sparse_counts = counts_to_matrix(counts=counts, rows=index_article_ids, cols=index_terms)
    tfidfs = compute_tfidf(sparse_counts)
    similarities = compute_similarities(tfidfs)
    filtered = filter_similarities(similarities, 0.45)
    clusters = clusterify(filtered)
    index_to_article = {indx: id_to_article[idx] for indx, idx in index_to_id.items()}
    prep_clusters(clusters, index_to_article, tfidfs)
