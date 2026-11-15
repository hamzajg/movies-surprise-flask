# Architecture — movies-surprise-flask

Current-state map. Descriptive, not aspirational; see `docs/adr/` for why.

## System shape

```
client (curl / browser form)
   │  POST /score  JSON   |   GET /  HTML form
   ▼
src/server.py  (Flask, port 12345 — app built at import)
   ├─ loads committed Surprise dumps from src/
   ├─ src/top_n_recommendations.py  scoring helpers
        │
        ▼
pre-trained dumps: SVD_model, SVD_model_couchDB, KNNBasic_model_couchDB
   │
   ▼ (offline)
src/build.py trains via MovieLens.py + ml-latest-small/ → surprise.dump
```

## Request flow (`POST /score`)

1. Request JSON names a `source.id` → `server.py` picks the matching dump.
2. Helpers predict ratings for candidate `movieIds` not yet rated by the
   user.
3. Top-N (default 10) returned as `{movieId, predicted rating}` pairs.

## Data

- **Model dumps committed** — service is inference-only at runtime; no
  training on boot.
- `src/ml-latest-small/` — MovieLens latest-small CSVs used by `build.py`
  and `MovieLens.py` when (re)training.
- `src/request_test_1.json` — canonical smoke-test payload.

## Entrypoint

- `server.py` — the only served variant (JSON `/score` + HTML form).
  The former `api.py` form variant was removed as dead, broken code.

## Deployment

`Dockerfile` (`python:3.13-slim`) installs deps + scikit-surprise, trains
the KNN dump at image build, and starts `server.py` manually — the image
has no entrypoint by design.
