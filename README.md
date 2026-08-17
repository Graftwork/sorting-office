# Graftwork Stock

[![CI](https://github.com/Graftwork/stock/actions/workflows/ci.yml/badge.svg)](https://github.com/Graftwork/stock/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/Graftwork/stock/branch/main/graph/badge.svg)](https://codecov.io/gh/Graftwork/stock)

The rootstock for new projects — a versioned foundation you graft new work onto,
so every project starts from a proven, consistent base and can be re-synced as
the foundation improves.

**Version 0.3.0.** See [CHANGELOG.md](CHANGELOG.md) for what changes between
versions, which doubles as the migration list for already-grafted projects.

## What you get

A project that is green from commit one — lint, tests, coverage, and CI all pass
on a fresh stamp with zero edits — so the first real commit is the idea, not the
plumbing.

| Piece | What it's for |
| --- | --- |
| [`mise.toml`](mise.toml) | Pinned toolchain (Python, uv, Node) — same versions on a laptop and in CI |
| [`pyproject.toml`](pyproject.toml) | uv-managed deps, ruff, pytest, coverage |
| [`openspec/`](openspec/) | Plain-English scenarios — the review layer |
| [`scripts/check_spec_traceability.py`](scripts/check_spec_traceability.py) | The guard: every scenario is claimed by a test |
| [`WORKFLOW.md`](WORKFLOW.md) | How changes are run — the loop, the conventions, the tool's rough edges |
| [`docs/UAT.md`](docs/UAT.md) | The checks that need human senses, and when they run |
| [`docs/RELEASING.md`](docs/RELEASING.md) | Branch to tag to re-sync — how a change gets out |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | Lint + test + coverage upload |
| [`.pre-commit-config.yaml`](.pre-commit-config.yaml) | The same checks, before the commit lands |
| [`.devcontainer/`](.devcontainer/) | Reproducibility layer, for when a project graduates |
| [`docs/decisions/`](docs/decisions/) | ADRs — which choices were deliberate. Stock's carry a `stock-` prefix; yours start at 0001 |
| [`CLAUDE.md`](CLAUDE.md) | Commands, conventions, house rules for Claude Code |

## Getting started

```bash
mise trust          # once per clone — mise won't run an untrusted config
mise install && uv sync
mise run check
```

## The verification layer

This is the part that matters. A spec scenario is written in plain English:

```markdown
#### Scenario: A refund returns the full amount
- **WHEN** a customer requests a refund
- **THEN** the full amount is returned
```

and a test claims it by id:

```python
@pytest.mark.spec("billing/a-refund-returns-the-full-amount")
def test_refund_returns_full_amount(): ...
```

`mise run trace` then checks **both directions** — a scenario with no test, or a
test claiming a scenario that doesn't exist — and prints what's missing in plain
English:

```
Scenarios with no test claiming them:
  billing/a-refund-returns-the-full-amount
    "A refund returns the full amount" under "Refunds"
    openspec/specs/billing/spec.md:12
    fix: add @pytest.mark.spec("billing/a-refund-returns-the-full-amount") to a test

0/1 scenarios claimed by tests
```

It runs three ways — standalone, as a pre-commit hook, and as a test in the suite
— so the link between what was promised and what is checked can't quietly rot.
The guard is itself tested against known-bad input, because a guard that can't
fail isn't a guard. See [Stock ADR 0004](docs/decisions/stock-0004-spec-traceability-guard.md).

Some promises genuinely can't be kept by a test — a review policy, something the
suite can't observe. Those are declared, with the reason written down:

```toml
[tool.graftwork.traceability]
unclaimed = [
    { scenario = "foundation/...", reason = "review policy; the suite cannot observe a pull request" },
]
```

The reason is mandatory, and the declarations are checked the same way everything
else is — an entry with no reason, one naming a scenario that no longer exists,
or one for a gap a test has since closed all turn the guard red. The distinction
that matters isn't "tested or not", it's **"decided or not"**. See
[Stock ADR 0005](docs/decisions/stock-0005-declared-gaps-in-traceability.md).

## Working this way

The guard is the part a machine can check. [`WORKFLOW.md`](WORKFLOW.md) is the
part it can't: when to open a change and when to explore instead, why backlog
items are proposal-only changes, why you copy the reasoning out of an abandoned
change before deleting it, and where OpenSpec's sharp edges are. It's short, and
everything in it changed an outcome on a real project.

[`docs/UAT.md`](docs/UAT.md) holds the checks that need a person — each with a
`Last passed` date, run before the PR and before the archive, because the archive
is one-way. An agent can run the commands and report what it saw; it can't mark
the case passed. See [Stock ADR 0006](docs/decisions/stock-0006-uat-is-a-human-gate.md).

[`docs/RELEASING.md`](docs/RELEASING.md) is how a change gets *out* — branch, the
route it takes, the version decision, tag, and the re-sync PRs it owes every
grafted project. Stock changes that touch specs or the guard run through the same
OpenSpec flow Stock ships; docs and CI fixes go direct. See
[Stock ADR 0007](docs/decisions/stock-0007-how-stock-changes-itself.md).

## Turning on the coverage badge

Coverage runs from day one, but the hosted badge needs one step: add a
`CODECOV_TOKEN` secret to the repo and it goes live on the next push. Until then
CI stays green and the real number is in the CI log — the upload is deliberately
non-blocking so a fresh stamp is never red. See
[Stock ADR 0003](docs/decisions/stock-0003-coverage-reporting.md).

## Grafting a project from Stock

Clone Stock at a tag, drop its history, and point the remote at the new repo:

```bash
git clone --branch v0.3.0 --depth 1 git@github.com:Graftwork/stock.git <project>
rm -rf <project>/.git
git -C <project> init -b main
git -C <project> remote add origin <new-repo-url>
```

Then:

1. **Keep `openspec/specs/foundation/`.** It is Stock's own spec, and its
   promises stay true of the grafted project — the suite asserts at least one
   scenario exists, so removing it turns a fresh stamp red. Your capabilities go
   alongside it.
2. **Remove `openspec/changes/`.** Its backlog stubs and archived changes are
   Stock's own working state, not yours — carrying them across means
   `openspec list` shows Stock's TODOs as if they belonged to your project, and
   `CLAUDE.md`'s "don't open a second change over the same ground" rule then
   treats a stale Stock stub as ground you've already covered. `rm -rf
   openspec/changes` is enough; `openspec new change` recreates the directory
   (and `archive/`) the first time you use it.
3. **Keep `WORKFLOW.md` and `docs/decisions/`.** The ways of working and the
   foundation's rationale travel with the graft. Stock's ADRs are the
   `stock-NNNN-*.md` files — leave them named as they are and never renumber
   them; **your own ADRs start at `0001`**, so the two sequences can't collide
   and a re-sync never rewrites your history
   ([Stock ADR 0008](docs/decisions/stock-0008-adr-numbering.md)). Keep
   `docs/RELEASING.md` too, and replace its specifics — most projects can drop
   the re-sync step and keep the rest.
4. Rewrite `README.md`, `CHANGELOG.md`, and the "what this repo is" section of
   `CLAUDE.md` for the new project. Replace Stock's cases in `docs/UAT.md` with
   the project's own — keep the file and the case format.
5. Set `name` and `description` in `pyproject.toml`, and record the graft:

   ```toml
   [tool.graftwork]
   stock-version = "0.3.0"
   grafted = "YYYY-MM-DD"
   ```

6. Run `mise trust && mise install && uv sync && mise run check` — it should be
   green before you write a line of your own code.

To re-sync later, read this CHANGELOG forward from the recorded `stock-version`,
apply each entry as its own small PR, then bump the recorded version.
