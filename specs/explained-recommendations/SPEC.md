# Spec: explained-recommendations

> Spec-driven development artifact. This file is the contract: implementation
> is done when every acceptance criterion maps to a scenario in
> `EXAMPLES.feature` and every scenario has a passing check.

## Problem

`POST /score` returns a ranked list of predicted ratings but no "why" — a
user cannot tell whether a pick matches their taste or is noise. The repo
already ships the citation half (`/similar`, `/explain` over
`ml-latest-small`) but nothing connects those neighbors to the SVD
recommendations, and the obvious shortcut — `similarity.user_rating` — is
wrong here: it reads the *latest-small* user table, whose user ids are a
different population than the ml-100k users the model knows. The correct
rating source is the fitted algorithm's own `trainset`.

## Users

- API consumers integrating the recommender who need explainable output
  ("because you rated X highly and it's similar").

## Outcome hypothesis

- Expected user outcome: every recommendation can be defended with 1–3
  concrete citations instead of a bare score.
- Opportunity evidence: the product already exposes `/similar` + `/explain`
  for item-item citations (PR #13); this connects them to the recs.
- Signal: `POST /explain-recs` returns non-empty `reasons` for the
  majority of recommendations on the bundled request fixture.
- Follow-up owner/date: repo owner, at next release review.

## Scope (in)

- `src/explain.py` — rating-map builder over a Surprise `Trainset`
  (`raw_ratings`) + `reasons_for(user_ratings, movie_id, limit)` that
  reuses `similarity.similar_movies`/`movie_info` and keeps only neighbors
  the user actually rated.
- `POST /explain-recs` — same request body as `/score` plus optional
  integer `explainLimit` (default 3); response keeps `movieIds` +
  `predictedRatings` and adds `explanations` per movie with `reasons`.
- Unit tests for `explain.py` on synthetic rating maps; endpoint tests via
  Flask `test_client` (validation 400s + one happy path).

## Scope (out)

- Changing `/score`, `/retrieve`, `/rank` responses or semantics.
- Persisting sessions/watchlists, auth, multiple models, pagination.
- Fixing `similarity.user_rating`'s user-space mismatch for `/explain`
  (documented; `/explain-recs` deliberately does not use it).

## Acceptance criteria

| # | Criterion | Scenario(s) |
|---|-----------|-------------|
| 1 | Each recommended movie carries up to `explainLimit` reasons citing similar movies the user rated | Explained recs cite rated neighbors |
| 2 | Reasons never include movies the user did not rate, and user ids come from the model's trainset (ml-100k space) | Reasons use model-user ratings |
| 3 | The response preserves the /score contract (`movieIds`, `predictedRatings`) and adds `explanations` | Response keeps score contract |
| 4 | Bad input is rejected exactly like /score (400s) | Validation matches score |
| 5 | A recommendation with no rated neighbors returns `reasons: []`, not an error | No rated neighbors is not an error |

## Decisions

- **Rating source = `algo.trainset`**, not `similarity.user_rating`:
  latest-small and ml-100k are different user populations; only the
  trainset knows the model's users. (Recorded here; revisit if a shared
  user mapping ever lands.)
- **New endpoint, not a flag on /score**: keeps the cheap path cheap —
  explanations cost similarity lookups per rec; callers opt in.
- **Reasons ranked by item-item similarity**, filtered to user-rated —
  simplest defensible ordering; no learned explanation model (KISS).
