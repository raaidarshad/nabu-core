from scipy.sparse import csr_matrix

from etl.functions.clusters import clusterify, prep_clusters


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


def test_prep_clusters():
    ...
