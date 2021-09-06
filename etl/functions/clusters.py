from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import breadth_first_order

from etl.models import Article


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
    # might need stuff from counts.py
    # CLUSTERS
    clusters = clusterify(filtered)
    index_to_article = {indx: id_to_article[idx] for indx, idx in index_to_id.items()}
    prep_clusters(clusters, index_to_article, tfidfs)
