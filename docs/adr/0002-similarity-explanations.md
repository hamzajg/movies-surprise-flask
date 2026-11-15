# ADR 0002 — Item-item similarity endpoints (`/similar`, `/explain`)

## Status

Accepted — implemented on `feat/recommendation-explain`.

## Context

The service answers "what should user N watch?" (`/score` et al.) but
never "why?" — a recommendation without a citation is a black box, and
the queued Phase-2 candidate was a recommendation agent whose first
requirement was an explanation surface citing similar movies.

## Decision

Two new POST routes backed by `src/similarity.py`, a pure-Python module
over the committed `ml-latest-small/` CSVs:

- **Similarity = mean-centered cosine over co-rating users.** Ratings
  are centered per movie before the dot product, so similarity reflects
  taste pattern rather than raw popularity. Computed lazily, cached for
  the process lifetime — no model dump, no Surprise import, fast enough
  to test without the heavy deps.
- **`POST /similar`** `{movieId|movieIds, limit?}` → neighbors with
  title, genres, similarity score.
- **`POST /explain`** `{movieId|movieIds, userId?, limit?}` → per movie:
  title, the user's rating of it, and neighbors annotated with the
  user's rating on each — the citation ("because you rated Toy Story 2
  4★ and it's 0.39-similar").
- Same validation style as `_recommendation_params` — 400 on bad input;
  new tests cover both success and rejection paths.

## Consequences

- The explanation path has **zero dependency on the Surprise model** —
  it works even where `scikit-surprise` isn't installed, and can't be
  broken by a corrupt dump.
- Each `/similar` query scores the target against every other movie —
  fine at ml-latest-small scale (~9k movies × sparse vectors), but would
  need an index (e.g. sklearn NearestNeighbors) if the dataset grew.
- No LLM agent loop yet: these endpoints are the *tool surface* a future
  agent would call (the orca/al-minhej pattern). Adding one requires an
  LLM provider decision this repo doesn't have — deferred deliberately.
- `source.id` remains cosmetic on the model routes (pre-existing quirk,
  documented in ARCHITECTURE.md, not changed here).
