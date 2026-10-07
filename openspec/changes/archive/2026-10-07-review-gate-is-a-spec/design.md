## Context

Stock carries this as the change `review-gate-is-a-spec`. Its tests extract the
`id: gate` step from the workflow and run it. This project's
`claude-review.yml` is byte-identical to the tag's (merged in #27), so the same
tests apply unchanged.

## Decisions

Kept as Stock made them, because a grafted project that diverges makes every
later re-sync a merge:

- **Run the real script, extracted from the YAML**, by slicing the `run: |`
  block by indentation. A copy of the logic would pass whatever the workflow
  does. PyYAML is not a dependency, so the extractor does not parse the YAML;
  it asserts it found exactly one `id: gate` step with a non-empty script, so a
  reformatted workflow fails loudly instead of testing nothing.
- **A fake `gh` on `PATH`** answers by endpoint from JSON the test supplies and
  applies `--jq` with the real `jq`.
- **`bash` and `jq` are required, not skipped.** A skipped test is a promise
  nobody is checking (Stock ADR 0013).
- **Claimed, not declared as gaps.** The seven scenarios are claimed by tests.

## Settled here: this project runs Stock's review workflow

Stock leaves open what a graft without `claude-review.yml` should do. This
project runs it, so the requirement and the tests apply as they are and the
question does not arise.

## Premises checked here, not taken from Stock

- **The tests need the new gate.** In a scratch worktree, the tag's tests gave
  24 passed against the gate from #27, and 6 failed against the previous
  (v0.6.0) gate: the "posted nothing" cases and the "denied tool call only
  warns" cases. That is why #27 had to merge before this change.
- **`bash` and `jq`** are present in this session (`jq-1.7`).

## Risks

- A refactor of the gate can break the tests, because they read it out of the
  workflow. Accepted: that coupling is what makes them test the real thing.
- The stubs can drift from the real API's field names. Mitigation: the live
  runs, and this project's own review runs on every PR.
- The tests compare ISO timestamps as fixed strings, so they do not exercise
  clock or time-zone behaviour.
