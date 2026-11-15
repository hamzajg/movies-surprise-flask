# Architecture — movies-surprise-flask

Current-state map. Descriptive, not aspirational; see `docs/adr/` for why.

## System shape

```
client (curl / browser form)
   │  POST /score|/retrieve|/rank|/similar|/explain  JSON
   │  GET /, /api/, /recs (form), /manage_link
   ▼
src/server.py  (Flask, port 12345 — app built at import)
   ├─ Surprise dumps in src/          → model-backed routes
   ├─ src/similarity.py               → /similar, /explain (no model)
   ├─ src/top_n_recommendations.py    → scoring helpers
        │
        ▼
pre-trained dumps: SVD_model, SVD_model_couchDB, KNNBasic_model_couchDB
   │
   ▼ (offline)
src/build.py trains via MovieLens.py + ml-latest-small/ → surprise.dump
```

## Request flows

### Model-backed routes (`/score`, `/retrieve`, `/rank`)

1. `_recommendation_params()` validates `{userId, candidateIds, limit,
   excludeIds?}` → 400 on bad input.
2. `server.py` loads `SVD_model_couchDB` (hardcoded — `source.id` in the
   request is echoed but does not select the dump) and predicts ratings
   over the ml-100k trainset.
3. `/score` returns top-N `{movieId, predicted rating}` filtered by
   candidates/excludes; `/retrieve` and `/rank` return movieIds only.

### Citation routes (`/similar`, `/explain`) — no model

`src/similarity.py` lazily loads `ml-latest-small/ratings.csv` +
`movies.csv` once per process and computes mean-centered cosine
similarity between movies over co-rating users. `/similar` returns
neighbors with titles; `/explain` adds the asking user's rating on each
neighbor (and on the target) — the "why" behind a recommendation without
involving Surprise. See ADR 0002.

### Form routes

`GET /` renders the request form; `POST /recs` returns JSON recs for
form input; `GET /api/?userid=N` returns top-10 recs;
`POST /manage_link` redirects back into the form flow.

## Data

- **Model dumps committed** — inference-only at runtime for model routes;
  `/similar`/`/explain` never touch them.
- `src/ml-latest-small/` — MovieLens latest-small CSVs; used by
  `build.py`, `MovieLens.py`, and `similarity.py`.
- `src/request_test_1.json` — canonical smoke-test payload.

## Entrypoint

- `server.py` — the only served variant. The former `api.py` form
  variant was removed as dead, broken code.

## Deployment

`Dockerfile` (`python:3.13-slim`) installs deps + scikit-surprise, trains
the KNN dump at image build, and starts `server.py` manually — the image
has no entrypoint by design.
