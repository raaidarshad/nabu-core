from datetime import datetime, timedelta, timezone
from uuid import uuid4

from scipy.sparse import csr_matrix

from etl.models import Article
from etl.functions.counts import CountData
from etl.functions.tfidf import SimilarityData, compute_similarities, compute_similarity_data, compute_tfidf, \
    filter_similarities

counts = [10, 11, 12, 13]
rows = [0, 1, 2, 3]
cols = [0, 1, 2, 3]
count_matrix = csr_matrix((counts, (rows, cols)))

tfidfs = [1, 1, 1, 1]
tfidf_matrix = csr_matrix((tfidfs, (rows, cols)))


def test_compute_similarity_data():
    article1 = Article(**{"id": uuid4(),
                          "url": "https://fake.com",
                          "source_id": uuid4(),
                          "title": "fake title",
                          "published_at": datetime.now(tz=timezone.utc),
                          "parsed_content": "fake raaid content"})

    count_data = CountData(
        count_matrix=count_matrix,
        index_to_article_id=[article1.id],
        index_to_term=["term"]
    )

    tfidf_matrix = compute_tfidf(count_data.count_matrix)

    expected = SimilarityData(
        tfidf_matrix=tfidf_matrix,
        similarity_matrix=compute_similarities(tfidf_matrix),
        **count_data.__dict__
    )
    real = compute_similarity_data(count_data)

    assert real.tfidf_matrix.todense().tolist() == expected.tfidf_matrix.todense().tolist()
    assert real.similarity_matrix.todense().tolist() == expected.similarity_matrix.todense().tolist()
    assert real.count_matrix.todense().tolist() == expected.count_matrix.todense().tolist()


def test_compute_tfidf():
    expected = tfidf_matrix
    real = compute_tfidf(count_matrix)

    assert real.todense().tolist() == expected.todense().tolist()


def test_compute_similarities():
    expected = csr_matrix((tfidfs, (rows, cols)))
    real = compute_similarities(tfidf_matrix)

    assert real.todense().tolist() == expected.todense().tolist()


def test_filter_similarities():
    fake = csr_matrix(([1, 0.7, 0.6, 0.3], (rows, cols)))
    # including a zero value instead of omitting it so that the shape is correct
    expected = csr_matrix(([1, 0.7, 0.6, 0], ([0, 1, 2, 3], [0, 1, 2, 3])))
    real = filter_similarities(fake, 0.5)

    assert real.todense().tolist() == expected.todense().tolist()
