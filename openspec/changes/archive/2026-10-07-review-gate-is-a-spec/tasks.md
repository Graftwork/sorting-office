## 1. The tests

- [x] 1.1 Add `tests/test_review_gate.py`, carried verbatim from Stock `v0.7.0-rc.1`
- [x] 1.2 Confirm the tests pass against the current `claude-review.yml` and name the rule when they fail

## 2. Verify and archive

- [x] 2.1 Run ruff, pytest and the traceability guard; the guard should read 42/46 claimed with 4 allowed without one
- [x] 2.2 Run `openspec validate --all`
- [x] 2.3 Archive the change so the requirement is written into `openspec/specs/foundation/spec.md`
