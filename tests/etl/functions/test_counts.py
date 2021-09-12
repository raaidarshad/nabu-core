from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, Mock
from uuid import uuid4

from scipy.sparse import csr_matrix
from sqlmodel import Session

from etl.models import Article, TermCount
from etl.functions.counts import CountData, get_count_data, numerify, get_counts_from_db, get_id_to_article, \
    counts_to_matrix

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

fake_counts = [
    TermCount(article_id=id1, term='content', count=1),
    TermCount(article_id=id2, term='fake', count=2)
]


def test_numerify():
    target = ["a", "b", "b", "c"]
    indices, index_to_target = numerify(target)
    recreated = [index_to_target[idx] for idx in indices]
    assert target == recreated


def test_get_article_map():
    mock_db_client = MagicMock(Session)
    a = Mock()
    b = Mock()
    b.all = Mock(return_value=fake_articles)
    a.filter = Mock(return_value=b)
    mock_db_client.query = Mock(return_value=a)

    expected = {id1: fake_articles[0], id2: fake_articles[1]}
    real = get_id_to_article(datetime.now(tz=timezone.utc) - timedelta(minutes=30), mock_db_client)

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
    mock_db_client = MagicMock(Session)
    a = Mock()
    b = Mock()
    c = Mock()
    c.all = Mock(return_value=fake_counts)
    b.filter = Mock(return_value=c)
    a.join = Mock(return_value=b)
    mock_db_client.query = Mock(return_value=a)

    # zip is weird
    x, y, z = zip(*[(dbc.count, dbc.article_id, dbc.term) for dbc in fake_counts])
    expected = (x, y, z)
    real = get_counts_from_db(datetime.now(tz=timezone.utc), mock_db_client)

    assert real == expected


def test_get_count_data():
    mock_db_client = MagicMock(Session)
    a = Mock()
    b = Mock()
    b.all = Mock(return_value=fake_articles)
    a.filter = Mock(return_value=b)

    c = Mock()
    d = Mock()
    d.all = Mock(return_value=fake_counts)
    c.filter = Mock(return_value=d)
    a.join = Mock(return_value=c)
    mock_db_client.query = Mock(return_value=a)

    real = get_count_data(datetime.now(tz=timezone.utc), mock_db_client)

    counts, ids, terms = zip(*[(dbc.count, dbc.article_id, dbc.term) for dbc in fake_counts])
    index_ids, index_to_id = numerify(ids)
    index_terms, index_to_term = numerify(terms)
    article_map = {id1: fake_articles[0], id2: fake_articles[1]}
    index_to_article = {index: article_map[idx] for index, idx in index_to_id.items()}

    expected = CountData(
        count_matrix=csr_matrix((counts, (index_ids, index_terms))),
        index_to_article=index_to_article,
        index_to_term=index_to_term
    )

    assert real.count_matrix.todense().tolist() == expected.count_matrix.todense().tolist()
    assert real.index_to_article == expected.index_to_article
    assert real.index_to_term == expected.index_to_term
