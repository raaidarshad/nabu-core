from unittest.mock import Mock
from uuid import uuid4

from dagster import ModeDefinition, ResourceDefinition, SolidExecutionResult, execute_solid

from etl.common import datetime_to_str, get_current_time
from etl.resources.database_client import mock_database_client
from etl.solids.compute_article_clusters import compute_article_clusters, compute_tfidf, get_term_counts, \
    load_article_clusters, TFIDF
from ptbmodels.models import Article, ArticleCluster, TermCount


def test_get_term_counts():
    expected_term_counts = [
        TermCount(article_id=uuid4(),
                  term=f"term{idx}",
                  count=idx,
                  added_at=get_current_time()
                  ) for idx in range(3)
    ]

    def _test_db_client(_init_context):
        db = mock_database_client()
        t_query = Mock()
        t_query.all = Mock(return_value=expected_term_counts)
        db.exec = Mock(return_value=t_query)
        return db

    result: SolidExecutionResult = execute_solid(
        get_term_counts,
        mode_def=ModeDefinition(name="test",
                                resource_defs={"database_client": ResourceDefinition(_test_db_client)})
    )

    assert result.success
    assert result.output_value() == expected_term_counts


def test_compute_tfidf():
    term_counts = [
        TermCount(article_id=uuid4(),
                  term=f"term{idx}",
                  count=idx,
                  added_at=get_current_time(),
                  article=Article(id=uuid4(),
                                  source_id=idx,
                                  url=f"https://fake.com/article{idx}",
                                  summary=f"summary{idx}",
                                  title=f"title{idx}",
                                  published_at=get_current_time(),
                                  added_at=get_current_time()
                                  )
                  ) for idx in range(3)
    ]

    result: SolidExecutionResult = execute_solid(
        compute_tfidf,
        input_values={"term_counts": term_counts}
    )

    # assert success, shape, types, and presence, otherwise the test code will just re-implement the app code
    assert result.success

    real = result.output_value()
    assert isinstance(real, TFIDF)
    assert real.tfidf.shape == (3, 3)
    assert real.counts.shape == (3, 3)
    assert len(real.index_to_article) == 3
    assert len(real.index_to_term) == 3


def test_compute_article_clusters():
    ...


def test_load_article_clusters():
    article_clusters = [
        ArticleCluster(
            id=uuid4(),
            type=f"type{idx}",
            parameters=idx,
            begin=get_current_time(),
            end=get_current_time(),
            added_at=get_current_time(),
            articles=[Article(id=uuid4(),
                              source_id=jdx,
                              url=f"https://fake.com/article{jdx}",
                              summary=f"summary{jdx}",
                              title=f"title{jdx}",
                              published_at=get_current_time(),
                              added_at=get_current_time()
                              ) for jdx in range(2)]
        ) for idx in range(2)
    ]

    db = mock_database_client()

    def _test_db_client(_init_context):
        db.exec = Mock(return_value=1)
        db.commit = Mock(return_value=1)
        a = Mock()
        a.count = Mock(return_value=1)
        db.query = Mock(return_value=a)
        return db

    result: SolidExecutionResult = execute_solid(
        load_article_clusters,
        mode_def=ModeDefinition(name="test",
                                resource_defs={"database_client": ResourceDefinition(_test_db_client)}),
        input_values={"entities": article_clusters}
    )

    assert result.success
    assert result.output_value() == article_clusters
    # count of rows in mock should be the same, therefore no asset should be materialized
    assert result.materializations_during_compute == []
    assert db.exec.called_once()
    assert db.commit.called_once()
