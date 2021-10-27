from collections import defaultdict
from dataclasses import dataclass

from dagster import AssetMaterialization, Enum, EnumValue, Field, Output, solid
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import breadth_first_order
from sklearn.base import BaseEstimator, ClusterMixin
from sklearn.cluster import AgglomerativeClustering, DBSCAN, OPTICS
from sklearn.feature_extraction.text import TfidfTransformer
from sqlmodel import Session

from etl.common import Context, DagsterTime, get_rows_factory, str_to_datetime
from ptbmodels.models import Article, ArticleCluster, TermCount


# intermediate models
@dataclass
class TFIDF:
    tfidf: csr_matrix
    counts: csr_matrix
    index_to_article: list[Article]
    index_to_term: list[str]


# custom clustering models
class PTB0(ClusterMixin, BaseEstimator):
    def __init__(self, threshold=0.4, min_cluster_size=None):
        self.threshold = threshold
        self.min_cluster_size = min_cluster_size

    def fit(self, X, y=None, sample_weight=None):
        # convert to sparse
        X = csr_matrix(X)
        # dot product of X with its transpose to get a cosine-similarity matrix,
        # where the value at [i, j] tells you the cosine similarity between
        # article i and article j
        similarities = X.dot(X.transpose())
        # filter to articles above a certain threshold of similarity
        filtered = similarities.multiply(similarities >= self.threshold)
        clusters = [
            frozenset(breadth_first_order(filtered, idx, directed=False, return_predecessors=False)) for idx in
            range(filtered.shape[0])]

        self.labels_ = self._encode_to_int(clusters)
        return self

    @staticmethod
    def _encode_to_int(seq):
        cmap = {item: idx for idx, item in enumerate(set(seq))}
        return [cmap[item] for item in seq]


get_term_counts = get_rows_factory("get_term_counts", TermCount)


@solid
def compute_tfidf(context: Context, term_counts: list[TermCount]) -> TFIDF:
    # recreate count matrix and keep track of index_to_id and index_to_term
    counts, articles, terms = zip(*[(tc.count, tc.article, tc.term) for tc in term_counts])
    index_articles, index_to_article = _numerify(articles)
    index_terms, index_to_term = _numerify(terms)
    sparse_counts = csr_matrix((counts, (index_articles, index_terms)))

    # create tfidf matrix
    tfidf = TfidfTransformer().fit_transform(sparse_counts)

    context.log.info(f"Size of the matrix is [{sparse_counts.shape[0]}, {sparse_counts.shape[1]}]")
    # create intermediate object
    return TFIDF(
        tfidf=tfidf,
        counts=sparse_counts,
        index_to_article=index_to_article,
        index_to_term=index_to_term
    )


def _numerify(target: list) -> tuple[list, list]:
    deduped = list(set(target))
    target_to_index = {t: idx for idx, t in enumerate(deduped)}
    return [target_to_index[t] for t in target], deduped


ClusterDenum = Enum("ClusterDenum",
                    [EnumValue("Agglomerative"), EnumValue("DBSCAN"), EnumValue("OPTICS"), EnumValue("PTB0")])

ClusterDenumConfig = Field(
    config=ClusterDenum,
    default_value="Agglomerative",
    is_required=False
)


@solid(config_schema={"runtime": DagsterTime,
                      "cluster_type": ClusterDenumConfig,
                      "cluster_parameters": Field(config=dict, default_value={}, is_required=False),
                      "begin": DagsterTime,
                      "end": DagsterTime})
def cluster_articles(context: Context, tfidf: TFIDF) -> list[ArticleCluster]:
    cluster_type: str = context.solid_config["cluster_type"]
    cluster_parameters: dict = context.solid_config["cluster_parameters"]

    # get correct class based on input
    cluster_method = {
        "Agglomerative": AgglomerativeClustering,
        "DBSCAN": DBSCAN,
        "OPTICS": OPTICS,
        "PTB0": PTB0
    }[cluster_type]

    # compute clusters given the specified cluster type and parameters
    clustering = cluster_method(**cluster_parameters).fit(tfidf.tfidf.toarray())
    # transform [0 0 1 1] to [(0, [0, 1]), (1, [2, 3])] so we know which row
    # indices are in the same cluster, allowing us to reference the correct
    # articles when adding the ArticleCluster to the DB
    clusters_and_rows = _get_indices(clustering.labels_)

    return [
        ArticleCluster(
            type=cluster_type,
            parameters=cluster_parameters,
            begin=str_to_datetime(context.solid_config["begin"]),
            end=str_to_datetime(context.solid_config["end"]),
            added_at=str_to_datetime(context.solid_config["runtime"]),
            articles=[tfidf.index_to_article[idx] for idx in rows]
        ) for _, rows in clusters_and_rows
    ]


def _get_indices(seq):
    tally = defaultdict(list)
    for idx, item in enumerate(seq):
        tally[item].append(idx)
    return ((key, locs) for key, locs in tally.items() if len(locs) > 1)


@solid(required_resource_keys={"database_client"}, config_schema={"runtime": DagsterTime})
def load_article_clusters(context: Context, entities: list[ArticleCluster]):
    db_client: Session = context.resources.database_client

    if entities:
        context.log.info(f"Attempting to add {len(entities)} rows to the {ArticleCluster.__name__} table")
        count_before = db_client.query(ArticleCluster).count()
        db_client.add_all(entities)
        db_client.commit()
        count_after = db_client.query(ArticleCluster).count()
        added = count_after - count_before
        context.log.info(f"Added {added} rows to the {ArticleCluster.__name__} table")

        if added > 0:
            yield AssetMaterialization(
                asset_key=f"{ArticleCluster.__tablename__}_table",
                description=f"New rows added to {ArticleCluster.__tablename__} table",
                tags={"runtime": context.solid_config["runtime"]}
            )
        yield Output(entities)
    else:
        context.log.info("No entities to add")
        yield Output(entities)
