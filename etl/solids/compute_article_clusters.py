import enum
from collections import defaultdict
from dataclasses import dataclass
from itertools import groupby
import json

from dagster import AssetMaterialization, Enum, EnumValue, Field, Output, solid
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import breadth_first_order
from sklearn.base import BaseEstimator, ClusterMixin
from sklearn.cluster import AgglomerativeClustering, DBSCAN, OPTICS
from sklearn.feature_extraction.text import TfidfTransformer
from sqlmodel import Session

from etl.common import Context, DagsterTime, get_rows_factory, str_to_datetime, truncate_table_factory
from ptbmodels.models import Article, ArticleCluster, ArticleClusterKeyword, TermCount


# intermediate models
@dataclass
class TFIDF:
    tfidf: csr_matrix
    counts: csr_matrix
    index_to_article: list[Article]
    index_to_term: list[str]


class PTB1Cluster:
    def __init__(self, threshold: float, labels: np.array):
        self.threshold = threshold
        self.labels = labels
        self.cluster_count = len(set(labels))


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

        self.labels_ = np.array(self._encode_to_int(clusters))
        return self

    @staticmethod
    def _encode_to_int(seq):
        cmap = {item: idx for idx, item in enumerate(set(seq))}
        return [cmap[item] for item in seq]


class PTB1Arbitration(enum.Enum):
    COARSE = "COARSE"
    FINE = "FINE"


class PTB1(ClusterMixin, BaseEstimator):
    def __init__(self, start: float = 0.2, stop: float = 0.6, steps: int = 40,
                 arbitration: PTB1Arbitration = PTB1Arbitration.COARSE,
                 drop_bottom: bool = True):
        self.start = start
        self.stop = stop
        self.steps = steps
        self.arbitration = arbitration
        self.drop_bottom = drop_bottom

    def fit(self, X, y=None, sample_weight=None):
        # use PTB0 for every threshold between (inclusive) start and stop with the specified number of steps
        clusters = [PTB1Cluster(threshold, PTB0(threshold).fit(X).labels_) for threshold in
                    np.linspace(self.start, self.stop, self.steps)]
        # group by the number of clusters, so list of (cluster count, PTB1Cluster)
        grouped = [(cluster_count, list(clusters)) for cluster_count, clusters in
                   groupby(clusters, key=lambda t: t.cluster_count)]

        # drop the bottom term because it will likely be a max, but not the one we are interested in
        # don't drop it if there is only one group!
        if self.drop_bottom and len(grouped) != 1:
            grouped = grouped[1:]

        # find which group (so which cluster_count) spans the largest number of steps. that will be our target output
        if self.arbitration == PTB1Arbitration.COARSE:
            # find the lowest (coarsest) max
            target_group = max(grouped, key=lambda t: len(t[1]))
        else:
            # find the highest (finest) max
            target_group = max(reversed(grouped), key=lambda t: len(t[1]))

        self.labels_ = target_group[1][0].labels
        self.threshold_ = target_group[1][0].threshold
        self.cluster_count_ = target_group[1][0].cluster_count

        return self


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
                    [EnumValue("Agglomerative"),
                     EnumValue("DBSCAN"),
                     EnumValue("OPTICS"),
                     EnumValue("PTB0"),
                     EnumValue("PTB1")
                     ])

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
        "PTB0": PTB0,
        "PTB1": PTB1
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
            articles=[tfidf.index_to_article[idx] for idx in rows],
            keywords=extract_keywords(rows, tfidf)
        ) for _, rows in clusters_and_rows
    ]


def extract_keywords(article_indices: list[int], tfidf: TFIDF, limit: int = 10) -> list[ArticleClusterKeyword]:
    # pull out only the relevant rows (articles)
    target_rows = tfidf.tfidf[article_indices, :]
    # take the mean of every column (term)
    word_weights = target_rows.mean(axis=0)
    # convert to list so it is easier to work with
    word_weights = word_weights.tolist()[0]
    # create dict to track indices while sorting
    idx_weight = [(idx, weight) for idx, weight in enumerate(word_weights)]
    # sort by weight desc
    sorted_idx_weight = sorted(idx_weight, key=lambda item: item[1], reverse=True)
    # grab the first N term indices
    keywords = sorted_idx_weight[:limit]
    # use index_to_term to convert to the right terms
    return [
        ArticleClusterKeyword(
            # article_cluster_id="",
            term=tfidf.index_to_term[idx],
            weight=weight
        ) for idx, weight in keywords
    ]


def _get_indices(seq):
    tally = defaultdict(list)
    for idx, item in enumerate(seq):
        tally[item].append(idx)
    return ((key, locs) for key, locs in tally.items() if len(locs) > 1)


@solid(required_resource_keys={"database_client"},
       config_schema={"runtime": DagsterTime,
                      "cluster_range": Field(config=dict, default_value={"days": 1}, is_required=False)})
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
                tags={"runtime": context.solid_config["runtime"],
                      "cluster_range": json.dumps(context.solid_config["cluster_range"])}
            )
        yield Output(entities)
    else:
        context.log.info("No entities to add")
        yield Output(entities)


truncate_term_count = truncate_table_factory("truncate_term_count", TermCount)
