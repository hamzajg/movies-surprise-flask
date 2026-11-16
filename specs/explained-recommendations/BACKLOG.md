# Backlog: explained-recommendations

## US1 — As an API consumer, I want each recommendation to cite similar movies I rated, so that I can trust the pick
- Scenarios: @w1
- Size: M
- Notes: src/explain.py — trainset rating map + reasons_for; unit tests on synthetic maps, no model dump needed.

## US2 — As an API consumer, I want a single endpoint that returns score plus explanations, so that I don't make two calls
- Scenarios: @w2
- Depends: US1
- Size: M
- Notes: POST /explain-recs in server.py reusing _recommendation_params + algo.trainset; test_client tests.
