from datetime import datetime
from uuid import UUID

from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import breadth_first_order
from sqlmodel import Session

from etl.functions.tfidf import SimilarityData
from etl.models import Article, Cluster

RawCluster = frozenset[int]


def compute_cluster_data(similarity_data: SimilarityData,
                         computed_at: datetime,
                         minute_span: int,
                         db_client: Session):
    raw_clusters = clusterify(similarity_data.similarity_matrix)
    raw_clusters = [rc for rc in raw_clusters if len(rc) > 1]
    load_clusters(raw_clusters, similarity_data, computed_at, minute_span, db_client)


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


def extract_keywords(cluster: RawCluster, tfidf: csr_matrix, index_to_term: list[str]) -> list[str]:
    return ["fake", "key", "words"]


def load_clusters(clusters: list[RawCluster],
                  similarity_data: SimilarityData,
                  computed_at: datetime,
                  minute_span: int,
                  db_client: Session):
    prepped = []
    for cluster in clusters:
        keywords = extract_keywords(cluster, similarity_data.tfidf_matrix, similarity_data.index_to_term)
        # if we don't re-cast it as Article, it loses an attribute "_sa_instance_state" that is needed *shrug*
        article_ids = [similarity_data.index_to_article_id[idx] for idx in cluster]
        articles = get_articles_by_id(article_ids, db_client)

        c = Cluster(keywords=keywords,
                    articles=articles,
                    computed_at=computed_at,
                    minute_span=minute_span)
        prepped.append(c)

    old_clusters_to_delete = db_client.query(Cluster).filter(Cluster.minute_span == minute_span).all()
    for old_cluster in old_clusters_to_delete:
        db_client.delete(old_cluster)
    db_client.add_all(prepped)
    db_client.commit()


def get_articles_by_id(ids: list[UUID], db_client: Session) -> list[Article]:
    return db_client.query(Article). \
        filter(Article.id.in_(ids)).all()
