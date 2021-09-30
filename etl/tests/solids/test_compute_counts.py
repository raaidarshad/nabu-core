from datetime import datetime, timedelta, timezone
from unittest.mock import Mock
from uuid import uuid4

from dagster import ModeDefinition, ResourceDefinition, SolidExecutionResult, execute_solid
from scipy.sparse import csr_matrix

from etl.resources.database_client import mock_database_client
from etl.solids.compute_counts import get_articles, compute_count_matrix, compose_rows, load_counts
from ptbmodels.models import Article, TermCount


fake_articles = [
    Article(**{"id": uuid4(),
               "url": "https://fake.com",
               "source_id": uuid4(),
               "title": "fake title",
               "published_at": datetime.now(tz=timezone.utc),
               "parsed_content": "fake raaid content"}),
    Article(**{"id": uuid4(),
               "url": "https://notreal.com",
               "source_id": uuid4(),
               "title": "unreal title",
               "published_at": datetime.now(tz=timezone.utc) - timedelta(seconds=30),
               "parsed_content": "unreal raaid content"})
]

expected_articles = [Article(**fa.__dict__) for fa in fake_articles]
expected_content = " ".join([fa.parsed_content for fa in fake_articles])
expected_features = sorted(list(set(expected_content.split())))


def test_get_articles():
    def _test_db_client(_init_context):
        db = mock_database_client()
        a = Mock()
        b = Mock()
        c = Mock()
        d = Mock()
        d.all = Mock(return_value=fake_articles)
        c.filter = Mock(return_value=d)
        b.outerjoin = Mock(return_value=c)
        a.filter = Mock(return_value=b)
        db.query = Mock(return_value=a)
        return db

    result: SolidExecutionResult = execute_solid(
        get_articles,
        mode_def=ModeDefinition(name="test_get_articles",
                                resource_defs={"database_client": ResourceDefinition(_test_db_client)}),
        run_config={
            "solids": {
                "get_articles": {
                    "config": {
                        "time_threshold": str(datetime.now(timezone.utc) - timedelta(hours=1))
                    }
                }
            }
        }
    )

    assert result.success
    assert len(result.output_value()) == len(fake_articles)
    for idx, article in enumerate(result.output_value()):
        assert expected_articles[idx] == article


def test_compute_count_matrix():
    result: SolidExecutionResult = execute_solid(
        compute_count_matrix,
        input_values={"articles": expected_articles}
    )

    assert result.success

    features = result.output_value("features")

    # this is a bit tricky because this solid tokenizes, so if we use stop words in the test
    # data, it won't show up here, and it'll also lemmatize certain words so that they aren't
    # the same. I think it is sane to test with no stop words and to just confirm that the
    # expected amount of tokens are present
    assert len(expected_features) == len(features)

    count_matrix = result.output_value("count_matrix")
    assert list(count_matrix.data) == [1, 1, 1, 1, 1, 1]
    assert list(count_matrix.indices) == [1, 2, 0, 2, 0, 3]
    assert list(count_matrix.indptr) == [0, 3, 6]
    assert tuple(count_matrix.shape) == (2, 4)


def test_compose_rows():
    result: SolidExecutionResult = execute_solid(
        compose_rows,
        input_values={
            "articles": expected_articles,
            "features": expected_features,
            "count_matrix": csr_matrix(([1, 1, 1, 1, 1, 1], ([0, 0, 0, 1, 1, 1], [0, 1, 2, 0, 2, 3])), shape=(2, 4))
        }
    )

    assert result.success
    assert len(result.output_value()) == 6
    assert result.output_value() == [
        TermCount(article_id=expected_articles[0].id, term='content', count=1),
        TermCount(article_id=expected_articles[0].id, term='fake', count=1),
        TermCount(article_id=expected_articles[0].id, term='raaid', count=1),
        TermCount(article_id=expected_articles[1].id, term='content', count=1),
        TermCount(article_id=expected_articles[1].id, term='raaid', count=1),
        TermCount(article_id=expected_articles[1].id, term='unreal', count=1),
    ]


def test_load_counts():
    counts = [
        TermCount(article_id=uuid4(), term="president", count=4),
        TermCount(article_id=uuid4(), term="congress", count=2),
        TermCount(article_id=uuid4(), term="environment", count=20),
        TermCount(article_id=uuid4(), term="markets", count=2)
    ]

    db_counts = [TermCount(**count.dict()) for count in counts]

    db_mock = mock_database_client()

    def _test_db_client(_init_context):
        db_mock.add_all = Mock(return_value=1)
        db_mock.commit = Mock(return_value=1)
        t_query = Mock()
        t_query.count = Mock(return_value=1)
        db_mock.query = Mock(return_value=t_query)
        return db_mock

    result: SolidExecutionResult = execute_solid(
        load_counts,
        mode_def=ModeDefinition(name="test_load_counts",
                                resource_defs={"database_client": ResourceDefinition(_test_db_client)}),
        input_values={"counts": counts}
    )

    assert result.success
    assert db_mock.add_all.called_once_with(db_counts)
    assert db_mock.commit.called_once()
