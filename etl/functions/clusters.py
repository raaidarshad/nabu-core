from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import breadth_first_order

from etl.models import Article

RawCluster = frozenset[int]

def clusterify(similarities: csr_matrix) -> set[RawCluster]:
    # okay SO for each row, the BFO operation looks through the matrix to find all "connected" rows, where connected
    # means there is a non-zero value to another row. So if row 0 has a value in column 4, those two should be connected
    # We then wrap that in a frozenset so that we can eliminate repeated rows if necessary, and so that we can compare
    # between sets (can't do that with normal sets). Since we iterate over all the rows, we WILL get duplicate
    # frozensets so we have the whole thing in a set comprehension, not a list comprehension, to automatically get the
    # unique frozensets (we also use frozensets because they are hashable and therefore allowed in a set).

    # All to say, this should provide us every group of connected rows with no duplicates. Huzzah!
    return {frozenset(breadth_first_order(similarities, idx, directed=False, return_predecessors=False)) for idx in
            range(similarities.shape[0])}


def extract_keywords(cluster: RawCluster, tfidf: csr_matrix, index_to_term: dict[int, str]) -> set[str]:
    ...


def prep_clusters(clusters: set[RawCluster], index_to_article: dict[int, Article], tfidf: csr_matrix) -> dict[int, list[Article]]:
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
