"""Item-item similarity over the committed MovieLens dataset.

The recommender (`server.py`) answers "what should this user watch?" but not
"why?". This module answers the citation half: which movies are similar to a
given one, and how the asking user rated those neighbors. Pure Python over
`ml-latest-small/ratings.csv` + `movies.csv` — no Surprise dependency, so it
loads fast and is unit-testable without the model dumps.

Lazy + cached: the CSVs are parsed once per process on first use.
"""

import csv
import math
import os
from collections import defaultdict

_DATA_DIR = os.path.join(os.path.dirname(__file__), "ml-latest-small")
_RATINGS_CSV = os.path.join(_DATA_DIR, "ratings.csv")
_MOVIES_CSV = os.path.join(_DATA_DIR, "movies.csv")

# Module-level caches — the dataset is committed and immutable at runtime.
_movies = None          # movieId -> {"title": str, "genres": str}
_user_ratings = None    # userId -> {movieId -> rating}
_item_vector = None     # movieId -> {userId -> rating}  (item-centered)
_item_norm = None       # movieId -> L2 norm of its rating vector


def _load_movies():
    global _movies
    if _movies is None:
        _movies = {}
        with open(_MOVIES_CSV, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                _movies[int(row["movieId"])] = {
                    "title": row["title"],
                    "genres": row["genres"],
                }
    return _movies


def _load_ratings():
    """Build both directions of the rating matrix in one pass."""
    global _user_ratings, _item_vector, _item_norm
    if _user_ratings is not None:
        return
    movies = _load_movies()
    _user_ratings = defaultdict(dict)
    _item_vector = defaultdict(dict)
    with open(_RATINGS_CSV, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            uid, mid, rating = int(row["userId"]), int(row["movieId"]), float(row["rating"])
            _user_ratings[uid][mid] = rating
            _item_vector[mid][uid] = rating
    # Center each item's ratings on its mean so similarity reflects taste
    # pattern, not raw popularity.
    _item_norm = {}
    for mid, vec in _item_vector.items():
        mean = sum(vec.values()) / len(vec)
        _item_norm[mid] = math.sqrt(sum((r - mean) ** 2 for r in vec.values()))


def movie_info(movie_id):
    """Title/genres for a movieId, or None if unknown."""
    _load_ratings()
    return _movies.get(movie_id)


def user_rating(user_id, movie_id):
    """The user's rating for a movie, or None if unrated/unknown."""
    _load_ratings()
    return _user_ratings.get(user_id, {}).get(movie_id)


def _cosine(item_a, item_b):
    """Pearson-style cosine over co-rated users (mean-centered vectors)."""
    vec_a, vec_b = _item_vector[item_a], _item_vector[item_b]
    if item_a == item_b or not vec_a or not vec_b:
        return 0.0
    mean_a = sum(vec_a.values()) / len(vec_a)
    mean_b = sum(vec_b.values()) / len(vec_b)
    dot = 0.0
    for uid, ra in vec_a.items():
        rb = vec_b.get(uid)
        if rb is not None:
            dot += (ra - mean_a) * (rb - mean_b)
    if dot == 0.0:
        return 0.0
    return dot / (_item_norm[item_a] * _item_norm[item_b])


def similar_movies(movie_id, limit=5):
    """Top-`limit` movies most similar to `movie_id`, cosine over co-raters.

    Returns [{"movieId", "title", "genres", "similarity"}] sorted desc.
    Empty list for unknown movieIds.
    """
    _load_ratings()
    if movie_id not in _item_vector:
        return []
    scored = []
    for other_id in _item_vector:
        if other_id == movie_id:
            continue
        sim = _cosine(movie_id, other_id)
        if sim > 0:
            info = _movies.get(other_id, {})
            scored.append({
                "movieId": other_id,
                "title": info.get("title"),
                "genres": info.get("genres"),
                "similarity": round(sim, 4),
            })
    scored.sort(key=lambda m: (-m["similarity"], m["movieId"]))
    return scored[:limit]
