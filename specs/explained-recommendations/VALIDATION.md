# Validation — explained-recommendations

## Traceability

| AC | Criterion | Scenarios | Wave(s) | Test evidence |
|----|-----------|-----------|---------|---------------|
| 1 | Each recommended movie carries up to `explainLimit` reasons… | Explained recs cite rated neighbors, No rated neighbors is not an error, Reasons use model-user ratings | 1 | (weak) test_explain.py, test_explain_recs.py |
| 2 | Reasons never include movies the user did not rate, and… | Explained recs cite rated neighbors, No rated neighbors is not an error, Reasons use model-user ratings | 1 | (weak) test_explain.py, test_explain_recs.py |
| 3 | The response preserves the /score contract (`movieIds`… | Response keeps score contract, Validation matches score | 2 | (weak) test_explain_recs.py |
| 4 | Bad input is rejected exactly like /score (400s) | Response keeps score contract, Validation matches score | 2 | (weak) test_explain_recs.py |
| 5 | A recommendation with no rated neighbors returns `reasons… | Explained recs cite rated neighbors, No rated neighbors is not an error, Reasons use model-user ratings | 1 | (weak) test_explain.py, test_explain_recs.py |

## Scenario coverage

- Scenarios: 5 total, 0 with detected test evidence, 5 with weak (token-match) evidence only, 0 without
- ~ `Explained recs cite rated neighbors` (@w1)
- ~ `Reasons use model-user ratings` (@w1)
- ~ `No rated neighbors is not an error` (@w1)
- ~ `Response keeps score contract` (@w2)
- ~ `Validation matches score` (@w2)

## Demo script (manual walkthrough)

1. **Explained recs cite rated neighbors** — run the app, perform the scenario, observe the outcome.
2. **Response keeps score contract** — run the app, perform the scenario, observe the outcome.

## Gaps

- none — spec is fully traced

Note: 'no evidence' means neither the scenario name nor a
token match was found in test files — verify by hand before
treating it as a real gap. '~' marks weak token-match evidence.

## Outcome follow-up

Optional; this is a post-release learning record, not a finish gate.
- Status: not yet measured
- Owner and review date: (record when known)
- Signal and observed result: (record after release; do not invent)
- Learning or next action: (record after review)