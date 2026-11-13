# ADR 0001 — Initial architecture

Date: 2026-11-13 (baseline recorded retroactively)
Status: accepted (describes what is built)

## Context

A small Flask service exposing Surprise-model movie recommendations. It
must start instantly (no training at runtime) and stay trivially deployable
via Docker.

## Decisions

1. **Pre-trained dumps committed; inference-only runtime.** `SVD_model`,
   `SVD_model_couchDB`, `KNNBasic_model_couchDB` live in `src/`; `server.py`
   loads them at import. Rationale: zero startup cost, no training infra,
   reproducible outputs.
2. **Flask function views, no framework extras.** No blueprints, ORM, or
   auth — JSON in, JSON out on port 12345. Rationale: KISS for a demo-grade
   service.
3. **`scikit-surprise` excluded from requirements.txt.** It needs a C
   compiler, so the Dockerfile and CI install it as a separate step;
   `requirements.txt` stays pip-light. Rationale: documented trade-off —
   local installs must add it by hand.
4. **Two endpoint variants kept (`server.py` JSON + `api.py` form).** The
   HTML form uses `request.form` + `candidateIds`; the JSON API uses
   `request.get_json`. Rationale: the form predates the JSON API; merging
   them is possible but was deferred — flagged here so it's a known
   duplication, not an accident.
5. **Training is an offline script (`build.py`).** Models are produced by
   running `build.py` against `MovieLens.py`/`ml-latest-small`, then
   committing the dump. Rationale: separates the slow training path from
   the fast serving path.
6. **Docker trains at build time.** The image build runs the KNN training
   (minutes) so runtime needs nothing. Rationale: keeps `docker run` a
   single command; build-time cost accepted.

## Consequences

_dump files are binary artifacts in git — retraining produces large diffs;
only recommit intentionally._
- `api.py`/`server.py` duplication means fixes may need applying twice —
  or a consolidation PR.
- No auth/rate-limiting — LAN/demo scope only.
