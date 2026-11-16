"""Tests for explain.py — reasons_for citations over synthetic rating maps."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from explain import reasons_for


def test_reasons_only_include_rated_movies():
    # User 1's real latest-small ratings include movie 31 (ghost) etc.; pick
    # ratings we know overlap Toy Story's (movieId 1) neighbor list.
    rated = {31: 4.5, 589: 3.0}
    reasons = reasons_for(rated, 1, limit=5)
    rated_ids = set(rated)
    assert all(r['movieId'] in rated_ids for r in reasons)
    assert all('userRating' in r for r in reasons)


def test_reasons_carry_similarity_and_rating():
    rated = {31: 2.5}
    reasons = reasons_for(rated, 1, limit=10)
    for r in reasons:
        assert 0 < r['similarity'] <= 1
        assert r['userRating'] == rated[r['movieId']]


def test_reasons_sorted_by_similarity_desc():
    rated = dict.fromkeys(range(2, 4000), 4.0)  # rate almost everything
    reasons = reasons_for(rated, 1, limit=10)
    sims = [r['similarity'] for r in reasons]
    assert sims == sorted(sims, reverse=True)


def test_reasons_respects_limit():
    rated = dict.fromkeys(range(2, 4000), 4.0)
    assert len(reasons_for(rated, 1, limit=3)) == 3


def test_no_rated_neighbors_is_empty_not_error():
    assert reasons_for({}, 1) == []
    assert reasons_for({999999: {1: 5.0}}, 1) == []


def test_unknown_movie_is_empty():
    assert reasons_for({1: 5.0}, 999999) == []
