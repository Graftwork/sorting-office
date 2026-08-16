# Stock ADR 0004: Tests claim scenarios with a pytest marker

- **Status:** accepted
- **Date:** 2026-07-25

## Context

The point of the foundation is a review layer that can be trusted without reading
the code. Plain-English scenarios only deliver that if there is a mechanical link
between a scenario and the test that keeps its promise. Without a link, specs
drift into aspiration: the scenario says one thing, the suite tests another, and
nothing catches the gap.

Two things can rot independently, and both need catching:

1. A scenario nobody tests — a promise nobody keeps.
2. A test claiming a scenario that no longer exists (renamed, deleted, typo'd) —
   a link that has quietly gone stale while still looking healthy.

## Decision

A test claims a scenario with a marker:

```python
@pytest.mark.spec("foundation/every-scenario-is-claimed-by-a-test")
def test_every_scenario_in_this_repo_is_claimed(): ...
```

Scenario ids are derived from the spec files OpenSpec actually writes —
`openspec/specs/<capability>/spec.md`, headings of the form
`#### Scenario: <title>` — as `<capability>/<slugified-title>`.

`scripts/check_spec_traceability.py` checks both directions and is run three
ways: standalone, as a pre-commit hook, and as a test inside the suite.

## Consequences

- `pytest --strict-markers` means a misspelled *marker* is an error, not a
  silent no-op. A misspelled *scenario id* is caught by the guard's second
  direction. Neither failure mode is silent.
- Claims are found by parsing the syntax tree, so the guard never imports or
  executes test code and stays fast.
- Scenario ids derive from titles, so **renaming a scenario breaks its links on
  purpose**. The guard names both ends of the break and the fix is a one-line
  edit. This is the intended behaviour, not a wart — a rename is exactly when a
  human should confirm the test still covers the promise.
- The guard is itself covered by tests that feed it known-bad input, because a
  guard that cannot fail is not a guard.

## Alternatives considered

- **Docstring convention (`Scenario: <id>` in the test docstring).** Reads nicely
  in plain English, but looser: a typo just fails to link rather than erroring,
  and it cannot be validated by pytest itself.
- **A separate mapping file (scenario id → test path).** Language-agnostic, but a
  third artifact to keep in sync and it drifts the moment a test is renamed.
- **Naming convention on test functions.** Too fragile, and forces unreadable
  test names.
