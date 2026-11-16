# Waves — explained-recommendations

Each wave IS an iteration: a time-boxed, independently shippable
increment — one branch, one PR, green tests, demoable outcome.
Do not start wave N+1 until wave N merges.

## Wave 1 — iteration 1

Scenarios proven by this wave:
- Explained recs cite rated neighbors
- Reasons use model-user ratings
- No rated neighbors is not an error

| Item | Title | Size | Deps | Notes |
|------|-------|------|------|-------|
| US1 | As an API consumer, I want each recommendation to cite similar movies I rated, so that I can trust the pick | M | — | src/explain.py — trainset rating map + reasons_for; unit tests on synthetic maps, no model dump needed. |

## Wave 2 — iteration 2

Scenarios proven by this wave:
- Response keeps score contract
- Validation matches score

| Item | Title | Size | Deps | Notes |
|------|-------|------|------|-------|
| US2 | As an API consumer, I want a single endpoint that returns score plus explanations, so that I don't make two calls | M | US1 | POST /explain-recs in server.py reusing _recommendation_params + algo.trainset; test_client tests. |
