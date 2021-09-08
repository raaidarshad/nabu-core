from etl.functions.counts import get_count_data, numerify, get_counts_from_db, get_article_map, \
    counts_to_matrix


def test_numerify():
    target = ["a", "b", "b", "c"]
    indices, index_to_target = numerify(target)
    recreated = [index_to_target[idx] for idx in indices]
    assert target == recreated


def test_get_article_map():
    ...


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
