## Why

Spec-driven development with an agent is a transcription pipeline by design:
conversation → proposal → design → spec → code → commit → published repository.
Every stage is a copy, specs are written to be read by other people, and the
archive is permanent.

That pipeline has no notion of *why* a detail was supplied. A person explaining
their problem gives the agent specifics so it will understand — a name, a
condition, an address, an account, a relationship. The agent, working exactly as
intended, promotes those specifics into a requirement, and the requirement into
code, and the code into a repository. Nothing malfunctioned. The method did what
it is for.

This is not hypothetical. It happened on the first project grafted from Stock,
and the correct remedy turned out to be destroying and rebuilding the repository,
because by the time it was noticed the detail was in git history, and history is
not edited — it is rewritten, which is a different and worse operation.

Two properties make this a foundation-level concern rather than a project-level
one:

- **It is structural.** It follows from the method, not from carelessness. Every
  project grafted from Stock inherits the same pipeline and the same exposure.
- **It is unrecoverable after the fact.** The window is the moment a detail
  crosses from conversation into an artifact. After the commit, the cheapest
  honest remedy is the one that was actually used: start again.

Stock already carries the mechanism for a promise a test cannot keep — declared
gaps, shipped in v0.2.0. This is the case that mechanism exists for.

## What Changes

A new `foundation` requirement, **Context Is Not Content**, establishing that
detail supplied to aid understanding is not thereby material for artifacts.
Requirements are written as categories and rules, not people and instances; a
specific that is genuinely load-bearing is confirmed before it is written down.

Three scenarios, split by what can actually enforce them:

- **Two review-policy scenarios**, declared as gaps in
  `[tool.graftwork.traceability]` with written reasons. No test can read a
  requirement and judge whether "the consultant" is a category or a person.
- **One mechanical scenario** — committed artifacts carry no credentials —
  enforced by a `detect-secrets` pre-commit hook. Machines are good at API keys
  and bad at biography; this covers the half they are good at, and the split is
  stated rather than blurred.

Supporting changes: a UAT case that reads the artifacts as a stranger would, and
a house rule in `CLAUDE.md` binding the agent to abstract by default, say what it
abstracted, and ask before making it concrete.

## Capabilities

### New Capabilities

None. This extends an existing capability.

### Modified Capabilities

- `foundation`: gains the **Context Is Not Content** requirement. Grafted
  projects inherit a new promise, which makes this a minor version bump rather
  than a patch.

## Impact

`openspec/specs/foundation/spec.md`, `pyproject.toml` (two new declared gaps),
`.pre-commit-config.yaml` (the `detect-secrets` hook), `tests/`, `docs/UAT.md`,
`CLAUDE.md`, `WORKFLOW.md`, `CHANGELOG.md`.

Under [`docs/RELEASING.md`](../../../../docs/RELEASING.md) this touches
`openspec/specs/` and `tests/`, so it takes the full OpenSpec route. It is the
first change to do so — v0.2.0 introduced the rule and could not follow it.
