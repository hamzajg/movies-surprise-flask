# AGENTS.md — movies-surprise-flask

Guidance for AI agents (and humans) working in this repository.

## Project

A Flask service that serves movie recommendations from a pre-trained
[Surprise](https://surpriselib.com/) model dump: `POST /score` returns the
top-N unrated movies with predicted ratings; `GET /` renders a request
form. Trained model dumps are committed so the service starts without
training.
Stack: Python 3.13 (Docker + CI), Flask, scikit-surprise, pandas/numpy,
joblib.

## Commands

Verified 2026-11-13 against CI (`.github/workflows/ci.yml`) and README.

| Task | Command |
|---|---|
| Install deps | `pip install -r requirements.txt && pip install scikit-surprise` |
| Run server | `cd src && python -u server.py` → port **12345** |
| Smoke check | `cd src && python -c "import server"` (builds app at import) |
| Test request | `curl -X POST http://localhost:12345/score -H 'Content-Type: application/json' -d @src/request_test_1.json` |
| Docker | `docker build -t movies-surprise-flask .` then run `sh` → `cd src && python -u server.py` |
| Retrain a model | `cd src && python build.py` (trains + dumps a model) |

Note: `scikit-surprise` is **commented out** in `requirements.txt` (needs a
compiler) — the Dockerfile and CI install it separately; do the same
locally.

## Architecture

- `src/server.py` — the JSON API (`POST /score`, `GET /` form) on port
  12345; **builds the Flask app at import time** and loads model dumps.
- `src/api.py` — a second, form-based variant of `/score`
  (`request.form`, filters by `candidateIds`). Not the served entrypoint.
- `src/top_n_recommendations.py` — top-N helpers shared by both servers.
- `src/build.py` — trains and dumps a model (`surprise.dump`).
- `src/MovieLens.py` — loads `src/ml-latest-small/` (committed dataset).
- `src/templates/` — the request form.
- Model dumps (committed): `SVD_model` (ml-100k), `SVD_model_couchDB`,
  `KNNBasic_model_couchDB`.
- `Dockerfile` + `docker-entrypoint.sh` — `python:3.13-slim` base; build
  step trains the KNN model (takes a couple of minutes); entrypoint is
  intentionally a no-op shell.

### API contract

| Method | Path | Body | Response |
|---|---|---|---|
| POST | `/score` | `{"source": {"id": "<model>"}, "movieIds": [...], "predictedRatings"/`user+`candidateIds` per `request_test_1.json` | top-10 `{movieId, predicted rating}` list |
| GET | `/` | — | HTML request form |

See `src/request_test_1.json` for a ready-made request (user 20,
candidates 1–299 excluding 3,4, limit 15). `api.py`'s form variant uses
`request.form` + `candidateIds` — different input shape, same output idea.

## Conventions

- Model selection is by dump file in `src/`; `source.id` in the request
  picks which dump `server.py` loads. Adding a model = train via
  `build.py`, commit the dump, register it.
- Flask app-at-import pattern — `server.py` has no `if __name__` guard
  requirement for the app object; keep import side-effect-light enough
  for CI's `import server` check.
- Plain Flask, no blueprints/SQLAlchemy — function views + JSON dicts.

## Landmines

- **Default branch is `master`, not `main`.**
- Port is **12345**, not 8000/5000.
- `scikit-surprise` missing from requirements.txt is deliberate — install
  it separately or imports fail.
- Model dumps are binary and committed — regenerating them changes large
  files; only recommit dumps when intentionally retraining.
- `api.py` and `server.py` are two variants of the same endpoint — check
  which one Docker/CI actually exercises (`server.py`) before editing.
- Docker image trains at build time (slow build, ~minutes) — that's
  intentional so the container needs no training step at runtime.
- `CouchDB` in requirements hints at a legacy data source for
  `*_couchDB` models — don't assume CouchDB is needed at runtime.

## Agent rules

- Branch from `master`; name branches `feat/*`, `fix/*`, `chore/*`, `docs/*`.
- Docs-only changes still go through a PR; never commit to `master` directly.
- Verify before claiming: `cd src && python -c "import server"` plus the
  curl smoke against a running server; report the real result.
- Keep changes minimal and consistent with surrounding code. No drive-by
  refactors.
- Update AGENTS.md / docs/ARCHITECTURE.md when you change routes, the
  request/response shape, or the model-dump mechanism.
