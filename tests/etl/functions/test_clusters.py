from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from scipy.sparse import csr_matrix
from sqlmodel import Session

from etl.models import Article
from etl.functions.clusters import clusterify, load_clusters
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


def test_get_articles_by_id():
    ...


def test_load_clusters():
    mock_db_client = MagicMock(Session)

    clusters = [
        frozenset([0]),
        frozenset([1, 2])
    ]

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
        index_to_article_id=[a1.id, a2.id, a3.id],
        index_to_term=[],
        tfidf_matrix=m,
        similarity_matrix=m
    )

    compute_time = datetime.now(tz=timezone.utc)

    load_clusters(clusters, similarity_data, compute_time, 1, mock_db_client)

    mock_db_client.add_all.assert_called()
    mock_db_client.commit.assert_called()
