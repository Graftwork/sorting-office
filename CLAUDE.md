# CLAUDE.md

Guidance for Claude Code working in this repository.

## What this repo is

Graftwork Stock is a foundation ("rootstock") repo. Projects are grafted from it
and re-synced as it improves. Changes here propagate outward to real projects, so
the bar for adding something is higher than in a normal repo — see Conventions.

## Commands

```bash
mise trust            # once per clone — mise won't run an untrusted config
mise install          # install the pinned toolchain
uv sync               # install Python dev dependencies
mise run check        # everything CI runs (lint + test)
mise run test         # pytest with coverage
mise run lint         # ruff check + format check
mise run format       # auto-fix and format
mise run trace        # spec traceability guard on its own
mise run openspec -- list   # the pinned OpenSpec CLI
uvx pre-commit run --all-files
```

## Architecture

There is deliberately no `src/`. Stock carries the verification layer and nothing
speculative; a grafted project adds its own package alongside.

- `openspec/specs/<capability>/spec.md` — plain-English scenarios, the review layer
- `scripts/check_spec_traceability.py` — the guard linking scenarios to tests
- `tests/` — the suite, including tests of the guard itself
- `WORKFLOW.md` — how changes are run: the loop, the conventions, OpenSpec's rough edges
- `docs/UAT.md` — the checks that need human senses, and when they run
- `docs/RELEASING.md` — how a change to Stock itself gets out: route, version, tag, re-sync
- `docs/decisions/` — ADRs recording deliberate choices
- `mise.toml` — pinned toolchain and task entry points

## Conventions

**The spec traceability contract.** Every scenario in `openspec/specs/` must be
claimed by at least one test:

```python
@pytest.mark.spec("<capability>/<slugified-scenario-title>")
def test_something(): ...
```

When you add a scenario, add the claiming test in the same change. When you
rename a scenario, its id changes and the guard will flag the broken link —
update the marker deliberately rather than routing around the guard.

A scenario that genuinely cannot be tested — a review policy, something the suite
cannot observe — is declared in `pyproject.toml` under
`[tool.graftwork.traceability]` with a written reason. The reason is mandatory
and the declarations are checked too: no reason, a scenario that no longer
exists, or a gap a test has since closed all fail the guard. See
[Stock ADR 0005](docs/decisions/stock-0005-declared-gaps-in-traceability.md).

**Never weaken the guard to make it pass.** If the guard fails, either the test
is missing or the spec is wrong. Both are real findings. Declaring a gap is not a
way to make a failure go away — it is a claim, in writing, that no test could
have kept this promise.

**Keep it unspeculative.** No `src/` ceremony, no publishing pipeline, no
monorepo layout until a real project needs one. The template grows by promotion
from things that proved themselves in real projects, never by anticipation. If
you are tempted to add something "for later", don't.

**Record deliberate choices.** Anything a future reader might mistake for drift
gets an ADR in `docs/decisions/`.

**Every change here is a migration for grafted projects.** Log it in
`CHANGELOG.md` so "migrate project Y to Stock vX" is a reviewable batch of small
PRs rather than an archaeology exercise.

**Changes to Stock take one of two routes.** Anything touching
`openspec/specs/`, `scripts/`, or `tests/` runs as a full OpenSpec change — the
specs are written by archiving, never edited by hand. Docs, CI, toolchain and
permission changes go direct. Either way it reaches `main` by branch and PR,
never a direct commit. The full sequence is in
[`docs/RELEASING.md`](docs/RELEASING.md); the reasoning is
[Stock ADR 0007](docs/decisions/stock-0007-how-stock-changes-itself.md).

## House rules

The long form, with the reasoning, is in [`WORKFLOW.md`](WORKFLOW.md). These are
the ones that bind you while you work.

**Context is not content.** Detail someone gives you so you understand their
problem is not thereby material for the artifacts. Write requirements as
categories and rules — a named correspondent, not their name; a retention
period, not whose records. When a specific genuinely has to appear for the
requirement to mean anything, say which specific and confirm it before writing
it down. Say what you abstracted, so the choice is visible and can be reversed.
The window is the crossing from conversation into a file that will be committed;
after the commit the cheapest honest remedy is rebuilding the repository.

**Measure, don't derive — and say which you did.** Every number a decision rests
on is *measured* (name the command that produced it), *derived* (show the
derivation), or *recalled* (say so; treat it as unverified). A confidently stated
wrong number is the failure a reviewer is least equipped to catch by reading. If
a document's numbers all came from real output, say so in a line of its own.

**Test the premise before you spec it.** If a change rests on an assumption you
could cheaply check — what an API really returns, what a library really does —
check it first. Specification effort spent on an unvalidated premise is the work
most likely to be thrown away.

**In-flight artifacts are editable; nothing is locked before archive.** If a task
turns out to be wrong, correct the task text in place rather than silently
implementing something else. Report which artifacts you edited and why in your
completion summary.

**Don't open a second change over the same ground.** Before `openspec new
change`, check whether an existing change or backlog stub already covers it — a
stub usually carries research a fresh change would re-derive, or worse, re-derive
differently. Announce which change you're using and how to override.

**Ask on genuine forks, decide on everything else.** A question is worth asking
when the answers lead to different code. Ask it with context, a recommendation,
and a realistic preview of each option. Everything else you decide — then flag
the one judgement call you were least sure about, and offer to change it.

**The user's field experience is evidence, not preference.** It is ground truth
you cannot observe. When a correction changes your recommendation, say so plainly
rather than absorbing it silently.

**Don't close a gate that needs human senses.** Run the [`docs/UAT.md`](docs/UAT.md)
commands and report what you saw; leave the case open. Naming one task as
unfinished is the correct outcome, not a shortfall.

**Disclose AI authorship in pull requests** — the coding agent and the model.

## Notes

- OpenSpec is `@fission-ai/openspec`, pinned via `OPENSPEC_VERSION` in `mise.toml`.
  The bare `openspec` npm package is an unrelated placeholder — do not use it.
- `.claude/settings.local.json` is machine-local and gitignored; the shared
  allowlist is `.claude/settings.json`.
