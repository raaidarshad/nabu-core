from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, Mock
from uuid import uuid4

from sqlmodel import Session

from etl.models import Article
from etl.functions.counts import get_count_data, numerify, get_counts_from_db, get_article_map, \
    counts_to_matrix


def test_numerify():
    target = ["a", "b", "b", "c"]
    indices, index_to_target = numerify(target)
    recreated = [index_to_target[idx] for idx in indices]
    assert target == recreated


def test_get_article_map():
    id1 = uuid4()
    id2 = uuid4()
    fake_articles = [
        Article(**{"id": id1,
                   "url": "https://fake.com",
                   "source_id": uuid4(),
                   "title": "fake title",
                   "published_at": datetime.now(tz=timezone.utc),
                   "parsed_content": "fake raaid content"}),
        Article(**{"id": id2,
                   "url": "https://notreal.com",
                   "source_id": uuid4(),
                   "title": "unreal title",
                   "published_at": datetime.now(tz=timezone.utc) - timedelta(seconds=30),
                   "parsed_content": "unreal raaid content"})
    ]
    mock_db_client = MagicMock(Session)
    a = Mock()
    b = Mock()
    b.all = Mock(return_value=fake_articles)
    a.filter = Mock(return_value=b)
    mock_db_client.query = Mock(return_value=a)

    expected = {id1: fake_articles[0], id2: fake_articles[1]}
    real = get_article_map(datetime.now(tz=timezone.utc) - timedelta(minutes=30), mock_db_client)

    assert real == expected



def test_counts_to_matrix():
    counts = [1, 2, 4, 8]
    rows = [0, 1, 2, 3]
    cols = [0, 1, 2, 3]
    matrix = counts_to_matrix(counts, rows, cols)
    expected = [
        [1, 0, 0, 0],
        [0, 2, 0, 0],
        [0, 0, 4, 0],
        [0, 0, 0, 8]
    ]
    assert matrix.indices.tolist() == cols
    assert matrix.data.tolist() == counts
    assert matrix.shape == (4, 4)

    for idx in rows:
        assert matrix.getrow(idx).todense().tolist()[0] == expected[idx]


def test_get_counts_from_db():
    ...


def test_get_count_data():
    ...
