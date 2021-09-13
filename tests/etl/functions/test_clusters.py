from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from scipy.sparse import csr_matrix
from sqlmodel import Session

from etl.models import Article, Cluster
from etl.functions.clusters import clusterify, load_clusters, prep_clusters
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
    a2 = Article(**{"id": uuid4(),
                    "url": "https://fakee.com",
                    "source_id": uuid4(),
                    "title": "fake title",
                    "published_at": datetime.now(tz=timezone.utc),
                    "parsed_content": "fake raaid content"})
    a3 = Article(**{"id": uuid4(),
                    "url": "https://fakeee.com",
                    "source_id": uuid4(),
                    "title": "fake title",
                    "published_at": datetime.now(tz=timezone.utc),
                    "parsed_content": "fake raaid content"})

    similarity_data = SimilarityData(
        count_matrix=m,
        index_to_article={0: a1, 1: a2, 2: a3},
        index_to_term={},
        tfidf_matrix=m,
        similarity_matrix=m
    )

    compute_time = datetime.now(tz=timezone.utc)
    keywords = ["fake", "key", "words"]

    expected = [
        Cluster(keywords=keywords, articles=[a1], computed_at=compute_time, minute_span=1),
        Cluster(keywords=keywords, articles=[a2, a3], computed_at=compute_time, minute_span=1),

    ]
    real = prep_clusters(clusters, similarity_data, compute_time, 1)

    for result in real:
        assert result.minute_span in [e.minute_span for e in expected]
        assert result.computed_at in [e.computed_at for e in expected]
        assert result.keywords in [e.keywords for e in expected]
        assert result.articles in [e.articles for e in expected]


def test_load_clusters():
    mock_db_client = MagicMock(Session)

    clusters = []
    load_clusters(clusters, mock_db_client)
    mock_db_client.add_all.assert_called_with(clusters)
    mock_db_client.commit.assert_called()
