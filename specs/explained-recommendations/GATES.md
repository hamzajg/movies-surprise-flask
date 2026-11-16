# Gates: explained-recommendations

## G1 — Endpoint contract recorded
- Before: plan
- Type: decision
- Owner: agent
- Resolver: agent
- Blocking: yes
- Check: file:specs/explained-recommendations/SPEC.md
- Why: /explain-recs shape (body reuse + explainLimit + explanations payload) must be frozen before waves.

## G2 — Test suite green
- Before: validate
- Type: quality
- Owner: agent
- Resolver: agent
- Blocking: yes
- Check: command:PYTHONPATH=src python -m pytest tests/ -q
- Why: validation requires mechanical evidence, not claims.
