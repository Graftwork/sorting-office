# Changelog

Every entry here is a migration step for projects already grafted from Stock.
Read from the version a project recorded at graft time forward, and apply each
entry as its own small PR.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html),
where a **major** bump means a grafted project needs manual intervention to
re-sync, and a **minor** bump means the migration is additive.

## [0.3.0] — 2026-08-16

**Context is not content.** Learned the expensive way: the first project grafted
from Stock was torn down and rebuilt because personal detail supplied while
scoping the work had been written into a spec, then into code, then pushed. By
the time it was noticed it was in git history, and history is not edited but
rewritten — so rebuilding was the cheapest honest remedy.

This is structural, not careless. Spec-driven development with an agent is a
transcription pipeline by design — conversation to proposal to spec to code to
commit — and the pipeline has no notion of *why* a detail was supplied. Every
project grafted from Stock inherits the same exposure, which is what makes it a
foundation concern.

The migration is additive: a new promise and one new pre-commit hook. A grafted
project that adopts neither stays green.

### Added

- **`foundation` requirement: Context Is Not Content.** Detail supplied so the
  agent understands a problem is not thereby material for artifacts. Requirements
  are written as categories and rules — a named correspondent, not their name; a
  retention period, not whose records. A specific that genuinely is the
  requirement gets confirmed before it is written down.
- **A `detect-secrets` pre-commit hook** (`Yelp/detect-secrets`, pinned
  `v1.5.0`), covering the half of that promise a machine can keep. Verified both
  ways: clean across the repository, and failing on a planted credential. No
  baseline file — Stock has no false positives to suppress, and a project adds
  one the day it gets its first.
- **Two declared gaps** in `[tool.graftwork.traceability]` for the half a machine
  cannot keep. No test can read a requirement and judge whether "the consultant"
  is a category or a person. The split is stated rather than blurred, because a
  green hook reading as "checked" is exactly the false assurance to avoid here.
- **UAT case 4** — read the artifacts as a stranger would. The only case that
  must run **before the commit** rather than before the PR, for the reason above.
- **House rule in `CLAUDE.md`** and the long-form convention in `WORKFLOW.md`,
  including the pipeline diagram showing where the window closes.
- **Three more of OpenSpec's rough edges**, all hit while making this change:
  nothing may reference a scenario id until the change is archived (there is no
  `sync` command to write main specs early, so the archive has to be ordered
  *ahead* of any claiming test or declared gap); `archive` moves a change one
  directory deeper without rewriting its relative links, silently breaking every
  `../../../` reference in its artifacts; and `validate --change <name>` prints
  `error: unknown option` while exiting 0.

### Changed

- **UAT `Last passed` dates are batched** into the next real change rather than
  each earning its own PR. A one-line date change costing a full pull request is
  friction that gets a rule quietly ignored; an exemption is a hole that widens.
  This release is the first use of it.
- **`docs/UAT.md` cases now carry two dates, not one.** `Last agent run` records
  that the commands were executed and what came back; `Last passed` records that
  a person looked and accepted. Only a person writes the second.

  This corrects a real defect in v0.2.0: every `Last passed` date in that release
  was written by the agent that had just run the commands itself. Everything was
  green and nothing had been reviewed — the exact failure UAT exists to prevent,
  shipped inside the file that forbids it. All `Last passed` dates are reset to
  `never` pending a human read.

- **Release candidates.** `docs/RELEASING.md` gains a step: after merge, cut
  `vX.Y.Z-rc.N` and run the tag-dependent UAT cases against *that*, before the
  stable tag exists. This closes a circle the v0.2.0 process could not: those
  cases need a real, cloneable tag, so they could only run after the release was
  already made — and a stable tag that turns out to be wrong cannot be moved,
  because someone may already have grafted from it. A candidate is real enough to
  clone and carries no promise, so a failure costs an `-rc.2` rather than a bad
  release. Cases previously marked *post-release* are now marked *needs a
  published tag*, since they no longer happen after the release.
- **A backlog stub** at `openspec/changes/fresh-graft-check-belongs-in-ci/`. UAT
  case 1 is fully machine-judgeable — its `Expect` is three exit codes — and by
  `docs/UAT.md`'s own admission rule it should be a CI job. A UAT list padded
  with mechanical checks trains the reader to skim, and the cases either side of
  it are the ones that must not be skimmed.

### Notes

- **This is the first change to take the full OpenSpec route** that
  [Stock ADR 0007](docs/decisions/stock-0007-how-stock-changes-itself.md)
  established — propose, design, delta specs, tasks, apply, archive. v0.2.0
  introduced the rule and could not follow it. The main spec here was written by
  `openspec archive`, not by hand.
- `gitleaks` was tested and rejected: its pre-commit hook declares
  `language: golang`, and Stock's toolchain pins Python, uv and Node but no Go.
  Adding a language runtime for one hook is disproportionate; the Docker variant
  trades it for a Docker dependency. `detect-secrets` declares `language: python`,
  which pre-commit provisions itself.
- The task list was edited mid-flight. Its first draft put the claiming test and
  the declared gaps before the archive step, which cannot work — see the rough
  edge above. The correction is recorded in the archived change rather than
  quietly applied.

## [0.2.0] — 2026-08-16

The ways of working, promoted from a real project. Everything here changed an
outcome on a real project — a parametric model generator run this way for its
whole life — rather than being added because it sounded sensible.

The migration is additive: nothing existing changes behaviour, and a grafted
project that adopts none of it stays green.

### Added

- **`WORKFLOW.md`** — how changes are actually run. The loop, the recipe table
  (situation → action), and the conventions OpenSpec cannot enforce for you:
  backlog stubs as proposal-only changes, transcribing learnings forward when a
  change is abandoned, small scope justified by abandonment cost rather than
  velocity, `MODIFIED` meaning the *entire* requirement, deprecation as a
  first-class `REMOVED` delta, and proving the untouched path is untouched. Ends
  with OpenSpec's rough edges written down, so nobody assumes they have
  misunderstood the tool.
- **Declared gaps in the traceability guard.** A scenario that genuinely cannot
  be tested is declared in `pyproject.toml` with a mandatory written reason:

  ```toml
  [tool.graftwork.traceability]
  unclaimed = [
      { scenario = "foundation/...", reason = "review policy; the suite cannot observe a pull request" },
  ]
  ```

  The declarations are checked like everything else — an entry with no reason, one
  naming a scenario that no spec declares, and one for a gap a test has since
  closed all fail the guard. The distinction that matters is not "tested or not"
  but "decided or not".
  ([Stock ADR 0005](docs/decisions/stock-0005-declared-gaps-in-traceability.md))
- **`docs/UAT.md`** — numbered cases with `Command` / `Expect` / `Last passed`,
  run before the PR and before the archive. An agent may run the commands and
  report what it saw; it may not mark a case passed. Ships with four real cases
  for Stock itself rather than an empty template, one of them marked
  *post-release* because it verifies the published tag and so genuinely cannot
  run before the release exists.
  ([Stock ADR 0006](docs/decisions/stock-0006-uat-is-a-human-gate.md))
- **House rules in `CLAUDE.md`** — the agent-facing half. Measure rather than
  derive and mark which you did; test an empirical premise before specifying on
  top of it; in-flight artifacts are editable and edits get reported; don't open
  a second change over ground an existing one covers; ask on genuine forks and
  decide on everything else; treat the user's field experience as evidence and
  say when it moves your recommendation; don't close a gate that needs human
  senses.
- **Two new `foundation` requirements** — *Declared Gaps* (four scenarios, all
  claimed by tests) and *AI Authorship Is Disclosed* (one scenario, declared as a
  review policy, which is what gives Stock a worked example of the new mechanism
  in its own repo).
- **`docs/RELEASING.md`** — how a change gets *out*, which Stock had never
  written down. The route table (spec/guard changes run as full OpenSpec changes;
  docs and CI go direct), the version decision, tag-after-merge, and the re-sync
  PRs each release owes every grafted project. A grafted project should keep the
  file and replace the specifics.
  ([Stock ADR 0007](docs/decisions/stock-0007-how-stock-changes-itself.md))
- **Project context and artifact rules in `openspec/config.yaml`**, which was
  previously entirely commented out. The `proposal` rules ask for a
  `## Background` section carrying reasoning forward from a superseded change,
  and for the provenance of load-bearing numbers; the `tasks` rule asks for a UAT
  step ordered before archive. Rules are the supported customisation hook — the
  artifact templates themselves are regenerated and would lose an edit.
- **A worked backlog stub** at
  `openspec/changes/version-string-consistency/` — proposal-only, no deltas,
  demonstrating the convention and tracking a real problem: the version string
  appears in 13 places across 6 files, only 5 of which may be bumped at a
  release. It will report as invalid under `openspec validate` until designed,
  which is the documented cost of the pattern.

### Changed

- `check()` in `scripts/check_spec_traceability.py` takes an `allowed` argument.
  It defaults to reading `pyproject.toml`, so existing callers keep working;
  pass `allowed=[]` to check specs on their own. `Report` gains `unexplained`,
  `orphaned`, and `redundant` alongside `unclaimed` and `unknown`, and the
  summary line accounts for declared gaps: `8/9 scenarios claimed by tests, 1
  allowed without one`.
- **Stock's ADRs are renamed `stock-NNNN-<slug>.md`**, titled `# Stock ADR NNNN:`
  and cited in prose as "Stock ADR 0004". A grafted project now numbers its own
  ADRs from `0001` and never renumbers them — the two sequences share a directory
  and cannot collide.

  This replaces the old advice that a project's ADRs "start at the next free
  number", which could not work: a project stamped when Stock had four ADRs
  started at 0005, and this release adds Stock's own 0005, 0006 and 0007. The
  collision was measured on a real graft — three colliding filenames and 45
  cross-references across 11 files that a renumber would have to rewrite by hand,
  recurring at every future release that adds an ADR. Since nothing outside Stock
  cites Stock's ADR filenames, moving Stock's files instead costs almost nothing.
  ([Stock ADR 0008](docs/decisions/stock-0008-adr-numbering.md))

  **Re-syncers:** if you grafted before v0.2.0 and numbered your own ADRs from
  0005, you do *not* need to renumber. Take the renamed `stock-*` files, keep
  yours exactly as they are, and update any of your own prose that cited Stock's
  ADRs by their old bare numbers.
- Graft steps in `README.md` now say to keep `WORKFLOW.md` and to replace Stock's
  UAT cases rather than the file.
- The ADR template carries a comment explaining the two numbering sequences, so
  the convention is visible at the moment someone copies it.
- **Stock no longer commits to `main` directly.** Up to v0.1.2 every release was
  a direct commit — `main` is a linear run with no merge commits and the repo had
  never had a pull request. From v0.2.0 changes reach `main` by branch and PR,
  which is also what makes the new *AI Authorship Is Disclosed* requirement
  something Stock itself can keep. This is a process change, not a code change;
  grafted projects are free to ignore it.

### Notes

- The vendored `.claude/skills/openspec-*` files are deliberately untouched. The
  "don't open a duplicate change" guardrail belongs in one of them by rights, but
  those files are generated by `@fission-ai/openspec` and would lose the edit on
  the next regeneration. `CLAUDE.md` is loaded every session and carries it
  instead.
- **v0.2.0 sits on the wrong side of its own rule.** It edits
  `openspec/specs/foundation/spec.md` directly, which Stock ADR 0007 forbids from
  v0.2.0 onward — it is the change that introduced the rule and could not have
  followed it. Retrofitting an archived change would fabricate a record of
  deliberation that never happened. The gap is deliberate and stays on the
  record; everything after this follows the route table.
- The auto-marked fast/slow test split is documented in `WORKFLOW.md` as a
  pattern, not shipped as code. Stock has no slow tests, and a `slow` marker with
  nothing to mark is exactly the "added for later" the conventions forbid. It
  should be promoted the first time a grafted project earns it.

## [0.1.2] — 2026-08-13

Permission allowlist tightened. Grafted projects should apply this to their own
`.claude/settings.json`.

### Fixed

- **The allowlist granted arbitrary code execution.** `Bash(uv run:*)` permitted
  `uv run python -c '<anything>'`, and `Bash(mise run:*)` permitted any task
  `mise.toml` happens to define. Both are removed and replaced by the specific
  commands actually used — `uv run pytest`, `uv run ruff check .`,
  `mise run check`, and so on. Because this file is copied into every grafted
  project, the over-broad version propagated outward, which is what makes it
  worth a release of its own.

### Added

- Narrow read-only allowlist entries derived from real usage across sessions:
  the `mise run` tasks, `uv run pytest`, ruff's check-only forms, the
  traceability guard, `uvx pre-commit run --all-files`, `uv sync --locked`, and
  the read-only OpenSpec subcommands.

### Notes

- `Bash(uvx pre-commit:*)` and `Bash(npx --yes @fission-ai/openspec@1.6.0:*)`
  are deliberately kept. Both are scoped to a single named tool rather than to
  an interpreter, and narrowing OpenSpec further would mean a prompt on every
  `new change` and `archive` — a real cost for no real gain.
- Entries such as `Bash(git status:*)` are redundant, since Claude Code already
  treats read-only git and gh subcommands as safe. They are harmless and left
  alone.

## [0.1.1] — 2026-08-12

Fixes found by the first real graft.
No code changed, so re-syncing is documentation-only.

### Fixed

- **The graft instructions produced a red stamp.** They said to drop
  `openspec/specs/`, but the suite asserts at least one scenario exists, so a
  project following them would fail on its first run — the exact opposite of the
  promise. The `foundation` spec now explicitly travels with the graft, which is
  what its own Purpose section always said.
- `mise trust` was missing from the getting-started steps. mise refuses to run an
  untrusted config, so a fresh clone stopped at the first command.
- CI pinned stale action majors (`checkout@v5`, `mise-action@v2`,
  `codecov-action@v5`); now `v7`, `v4`, and `v7`.

### Added

- **`[tool.graftwork]` in `pyproject.toml`** — records `stock-version` and the
  graft date. Previously "record the version you grafted from" named no location,
  so a re-sync had nowhere to look. This is now the starting point for reading
  the CHANGELOG forward.
- Concrete clone-and-detach commands for grafting, rather than "copy the
  foundation across".

## [0.1.0] — 2026-07-25

The initial foundation.

### Added

- **Pinned toolchain** via `mise.toml` — Python 3.13, uv 0.11.16, Node 26.
  Drives the local shell, CI, and the devcontainer from one source of truth.
  ([Stock ADR 0001](docs/decisions/stock-0001-why-mise.md))
- **Python project config** in `pyproject.toml` — uv dependency groups, ruff
  (lint + format), pytest with coverage and `--strict-markers`.
- **OpenSpec** initialised via the pinned `@fission-ai/openspec@1.6.0`, with
  Claude Code skills and `/opsx:*` commands.
  ([Stock ADR 0002](docs/decisions/stock-0002-why-openspec-via-npx.md))
- **Spec traceability guard** (`scripts/check_spec_traceability.py`) — checks
  that every scenario is claimed by a test and that every claim names a real
  scenario. Runs standalone, as a pre-commit hook, and inside the test suite.
  ([Stock ADR 0004](docs/decisions/stock-0004-spec-traceability-guard.md))
- **`foundation` spec** — Stock's own promises, written as scenarios and claimed
  by tests, so the foundation is verified by the same mechanism it provides.
- **CI** (`.github/workflows/ci.yml`) — lint, test, and a non-blocking Codecov
  upload so a fresh stamp is green before any secret exists.
  ([Stock ADR 0003](docs/decisions/stock-0003-coverage-reporting.md))
- **pre-commit config** — whitespace/YAML/TOML hygiene, ruff, and the
  traceability guard.
- **Devcontainer** layered on mise, for when a project graduates from experiment.
- **`CLAUDE.md`** — commands, conventions, architecture.
- **`.claude/settings.json`** — shared permission allowlist.
- **ADRs** in `docs/decisions/`, with a template.

[0.3.0]: https://github.com/Graftwork/stock/releases/tag/v0.3.0
[0.2.0]: https://github.com/Graftwork/stock/releases/tag/v0.2.0
[0.1.2]: https://github.com/Graftwork/stock/releases/tag/v0.1.2
[0.1.1]: https://github.com/Graftwork/stock/releases/tag/v0.1.1
[0.1.0]: https://github.com/Graftwork/stock/releases/tag/v0.1.0
