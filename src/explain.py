"""Explanation citations for recommendations.

`similarity.py` answers "which movies are like this one" over
ml-latest-small; this module answers "which of those did THIS user
rate?". Ratings come from the fitted algorithm's own `trainset` —
ml-100k user space, which is *not* the same population as the
latest-small `user_rating` table (see
specs/explained-recommendations/SPEC.md → Decisions).
"""

from similarity import similar_movies

# Candidates scanned per movie before the user-rating filter. The cosine
# pass is O(#items) anyway; a generous pool keeps reasons available for
# users with sparse overlap.
_NEIGHBOR_POOL = 50


def user_rating_map(trainset):
    """{userId: {movieId: rating}} from a fitted Surprise Trainset."""
    out = {}
    for uid, mid, rating, _est in trainset.raw_ratings():
        out.setdefault(uid, {})[mid] = rating
    return out


def reasons_for(user_ratings, movie_id, limit=3):
    """Top similar movies `user_ratings` actually rated.

    `user_ratings` is one user's {movieId: rating} dict (see
    user_rating_map). Returns citation dicts sorted by similarity desc:
    {movieId, title, genres, similarity, userRating}. An empty list —
    never an error — when the user rated none of the neighbors.
    """
    rated = user_ratings or {}
    reasons = []
    for s in similar_movies(movie_id, limit=_NEIGHBOR_POOL):
        user_rating = rated.get(s["movieId"])
        if user_rating is None:
            continue
        reasons.append({**s, "userRating": user_rating})
        if len(reasons) >= limit:
            break
    return reasons
