from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from scipy.sparse import csr_matrix
from sqlmodel import Session

from etl.models import Article, TermCount


class CountData(BaseModel):
    count_matrix: csr_matrix
    index_to_article_id: list[UUID]
    index_to_term: list[str]

    class Config:
        arbitrary_types_allowed = True


def get_count_data(datetime_threshold: datetime, db_client: Session) -> CountData:
    # get csr_matrix, add article_map (id to article dict), add index to id/term dicts
    counts, ids, terms = get_counts_from_db(datetime_threshold, db_client)
    index_article_ids, index_to_id = numerify(ids)
    index_terms, index_to_term = numerify(terms)
    sparse_counts = counts_to_matrix(counts=counts, rows=index_article_ids, cols=index_terms)
    return CountData(count_matrix=sparse_counts,
                     index_to_article_id=index_to_id,
                     index_to_term=index_to_term)


def get_count_matrix(datetime_threshold: datetime, db_client: Session) -> csr_matrix:
    count_data = get_count_data(datetime_threshold, db_client)
    return count_data.count_matrix


def numerify(target: list) -> tuple[list, list]:
    deduped = list(set(target))
    target_to_index = {t: idx for idx, t in enumerate(deduped)}
    return [target_to_index[t] for t in target], deduped


# TODO will want more than just datetime filter at some point
def get_counts_from_db(datetime_threshold: datetime, db_client: Session) -> tuple[list, list, list]:
    db_counts: list[TermCount] = db_client.query(TermCount). \
        join(Article, Article.id == TermCount.article_id). \
        filter(Article.published_at >= datetime_threshold).all()

    counts, ids, terms = zip(*[(dbc.count, dbc.article_id, dbc.term) for dbc in db_counts])
    return counts, ids, terms


def counts_to_matrix(counts: list[int], rows: list[int], cols: list[int]) -> csr_matrix:
    return csr_matrix((counts, (rows, cols)))
