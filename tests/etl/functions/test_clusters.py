from datetime import datetime, timezone
from uuid import uuid4

from scipy.sparse import csr_matrix

from etl.models import Article
from etl.functions.clusters import clusterify, prep_clusters
from etl.functions.tfidf import SimilarityData


def test_clusterify():
    vals = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.5, 0.5, 0.6, 0.6]
    rows = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 9, 4, 5]
    cols = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 0, 5, 4]
    similarities = csr_matrix((vals, (rows, cols)), shape=(10, 10))

    real = clusterify(similarities)
    expected = {
        frozenset([0, 9]),
        frozenset([4, 5]),
        frozenset([1]),
        frozenset([2]),
        frozenset([3]),
        frozenset([6]),
        frozenset([7]),
        frozenset([8])
    }

    assert real == expected


def test_extract_keywords():
    ...


def test_prep_clusters():
    clusters = {
        frozenset([0]),
        frozenset([1, 2])
    }

    m = csr_matrix(([1, 1, 1], ([0, 1, 2], [0, 1, 2])))

    a1 = Article(**{"id": uuid4(),
                    "url": "https://fake.com",
                    "source_id": uuid4(),
                    "title": "fake title",
                    "published_at": datetime.now(tz=timezone.utc),
                    "parsed_content": "fake raaid content"})

    similarity_data = SimilarityData(
        count_matrix=m,
        index_to_article={0: a1, 1: a1, 2: a1},
        index_to_term={},
        tfidf_matrix=m,
        similarity_matrix=m
    )

    expected = [
        (["fake", "key", "words"], [a1]),
        (["fake", "key", "words"], [a1, a1])
    ]
    real = prep_clusters(clusters, similarity_data)

    for result in real:
        assert result in expected
