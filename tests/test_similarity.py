"""Tests for similarity.py — item-item neighbors over ml-latest-small."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from similarity import movie_info, similar_movies, user_rating


def test_similar_movies_returns_ranked_neighbors():
    sims = similar_movies(1, limit=5)  # Toy Story (1995)
    assert len(sims) == 5
    assert all(0 < s['similarity'] <= 1 for s in sims)
    # Sorted descending by similarity.
    assert sims == sorted(sims, key=lambda s: -s['similarity'])
    # The movie itself is never its own neighbor.
    assert all(s['movieId'] != 1 for s in sims)


def test_similar_movies_finds_expected_sequel():
    sims = similar_movies(1, limit=10)
    ids = {s['movieId'] for s in sims}
    assert 3114 in ids  # Toy Story 2 (1999)


def test_similar_movies_unknown_id_is_empty():
    assert similar_movies(999999) == []


def test_movie_info_and_user_rating():
    assert movie_info(1)['title'] == 'Toy Story (1995)'
    assert user_rating(1, 31) == 2.5
    assert user_rating(1, 999999) is None
    assert user_rating(99999, 1) is None
