# Stock ADR 0005: Untestable scenarios are declared, with a written reason

- **Status:** accepted
- **Date:** 2026-08-16

## Context

[Stock ADR 0004](stock-0004-spec-traceability-guard.md) made every scenario need a claiming
test. Real projects then hit scenarios that genuinely have none: a review policy
("a PR carrying AI-generated code names the model"), a licensing rule, a promise
about something outside the process the suite runs in.

There were three ways that could go, and two of them are bad:

1. **Don't write the scenario.** The spec stops being the whole picture, and the
   promise survives only in someone's memory.
2. **Write a hollow test that asserts nothing.** The guard goes green and the
   coverage number lies. This is the worst option because it looks like the good
   one.
3. **Declare the gap.**

The failure mode we actually care about is not "a scenario has no test" — it is
"a scenario has no test and nobody decided that". Those look identical in a
report that only counts.

## Decision

Untestable scenarios are declared in `pyproject.toml`, and a reason is mandatory:

```toml
[tool.graftwork.traceability]
unclaimed = [
    { scenario = "foundation/...", reason = "review policy; the suite cannot observe a pull request" },
]
```

An entry with no reason does not excuse anything — the scenario is still reported
as unclaimed, *and* the empty declaration is reported too.

The declarations are checked the same way everything else is. The guard reports
three further kinds of rot:

- an entry with no reason,
- an entry naming a scenario that no spec declares (renamed or deleted),
- an entry for a scenario a test now claims (the gap closed; the entry didn't).

It lives in `pyproject.toml` rather than in the guard because the guard is
Stock's code and is overwritten on re-sync. The declarations are the project's,
and belong in a file the project already owns.

## Consequences

- "We can't test this" becomes a sentence someone wrote and a reviewer read,
  rather than a hole that opened on its own.
- The summary line stays honest: `8/9 scenarios claimed by tests, 1 allowed
  without one`. Declared gaps are never counted as claimed.
- Declarations rot like everything else, so they are checked like everything
  else. A stale entry is a finding, not a warning to scroll past.
- Stock ships with exactly one declaration — the AI-authorship review policy — so
  a grafted project inherits a worked example rather than an empty table.
- The cost is a small ceremony on a rare path. That is deliberate: it should be
  slightly more effort to declare a gap than to write the test.

## Alternatives considered

- **A `skip`-style marker on a placeholder test.** Puts the exemption next to the
  code, but a skipped test is invisible in a green run and the reason ends up in
  a string nobody aggregates.
- **A separate `traceability-allowlist.toml`.** One more file to notice. The
  project already owns `pyproject.toml`, and `[tool.graftwork]` was already there
  recording the graft.
- **Reasons optional.** Removes the only part that does any work. An allowlist
  without reasons is just a slower way to lower the bar.
