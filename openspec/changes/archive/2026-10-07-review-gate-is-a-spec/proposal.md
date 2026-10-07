## Why

The automated review check promises something specific: a green tick means a
review was actually posted. The final step of `.github/workflows/claude-review.yml`
(adopted in the v0.6.0 re-sync, tidied in v0.7.0) keeps that promise, but the
promise exists only as shell inside a workflow file and the comments around
it. `foundation` does not mention it, the traceability guard cannot see it, and
no test runs the step, so a refactor can delete a rule without any check
noticing.

That matters here because this project saw the original failure first-hand: the
review ran on every PR and reported `success` while posting nothing. This
change writes the promise down as a requirement and makes tests claim it.

Stock `v0.7.0-rc.1` (commit `7fccde9`) ships exactly this as a migration entry
(its CHANGELOG, "A Passing Review Check Means A Review Happened"). This change
is the part of that migration that touches `openspec/specs/` and `tests/`, so
it runs as a full OpenSpec change; the workflow and `ci.yml` changes were
separate direct-route PRs (#27, #28), merged first because the tests assume the
new gate.

## What Changes

- **ADDED** `foundation` → *A Passing Review Check Means A Review Happened*, with
  seven scenarios: a posted review passes; nothing posted fails; a run that
  reports an error fails; a pull request that edits the review workflow fails;
  a denied tool call only warns; a declined review passes only for a
  Markdown-only pull request; comments by anyone but the review bot do not
  count. The text is Stock's, unchanged.
- **`tests/test_review_gate.py`**, carried verbatim from the tag. It reads the
  gate step out of `.github/workflows/claude-review.yml`, runs it with `bash`
  against a fake `gh`, and claims all seven scenarios.

Not changed: the workflow, the gate's behaviour, and the four existing declared
gaps.

## Impact

- `openspec/specs/foundation/spec.md`: one requirement, seven scenarios, added
  by archiving. The guard should go from `35/39` to `42/46` with the same 4
  declared gaps (derived: 35 and 39 measured on `main` today, plus 7 claimed).
- `tests/test_review_gate.py`: new. Needs `bash` and `jq`; both are present in
  the cloud session used to write this (measured: `jq-1.7`), and on
  `ubuntu-latest` (recalled, not checked for the current image; the first CI
  run on this change is the check).
- No change to `.github/workflows/`, `scripts/` or dependencies.

## Not covered, and said so in the spec

Whether the live review follows its prompt (the "No reviewable changes" note,
reviewing again after a push) is model and plugin behaviour, checked on real
runs, not by the suite. On this project's #26 the review declined correctly and
the gate failed it because `pyproject.toml` is not Markdown: Stock records the
same limit in its CHANGELOG.
