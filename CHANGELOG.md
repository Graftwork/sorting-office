# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
What each version number will mean for this project — and why it is 0.0.0 today
— is set out in [`docs/RELEASING.md`](docs/RELEASING.md).

## [Unreleased]

### Added

- **Re-synced to Stock `v0.4.0`.** A minor, additive release — nothing here
  broke by staying on `v0.3.0` — applied as a mechanical batch since `main`
  was already settled (unlike the `v0.3.0-rc.1` → `rc.2` resync, this one
  didn't need the in-flight-graft skill). `stock-version` in `pyproject.toml`
  now reads `0.4.0`. Brought over:
  - [`stock-0009`](docs/decisions/stock-0009-not-a-template-repo.md),
    [`stock-0011`](docs/decisions/stock-0011-resync-in-flight-graft-skill.md),
    and [`stock-0013`](docs/decisions/stock-0013-defer-to-tool-defaults-over-suppressions.md)
    — the three Stock ADRs added since `v0.3.0` that this project didn't
    already have a copy of.
  - `.claude/skills/resync-in-flight-graft/` renamed to
    `.claude/skills/stock-resync-in-flight-graft/`, matching Stock's own
    formalization of the skill this project wrote (`stock-0011`) — the
    prefix lets a future resync tell at a glance which `.claude/skills/`
    entries are Stock's (safe to overwrite) versus this project's own.
  - `WORKFLOW.md`'s "Branch names match the route" expanded from this
    project's original two prefixes (`feature/`, `chore/`) to Stock's fuller
    set (`feature/`, `bugfix/`, `chore/`, `docs/`, `ci/`, `refactor/`,
    `test/`, explicitly not `release/`/`hotfix/`) — Stock generalized this
    from this project's own convention; adopting the fuller version back is
    documentation catching up, not a behavior change.
  - A new `CLAUDE.md` house rule, "Default to a tool's own defaults over a
    suppression" (`stock-0013`).
  - `jdx/mise-action@v4` in `.github/workflows/ci.yml` now sets
    `minimum_release_age: 7d`, guarding against a brand-new mise release
    shipping assets that 404 for the first few days — the bug Stock hit and
    fixed this way.

  Not brought over here: Stock's own `LICENSE`/`NOTICE`/`stock-0014` — that
  decision was made independently for this project in the entry below.
- **`LICENSE` and `NOTICE`** — Apache License 2.0, copyright held by James
  Rennison individually rather than by "Graftwork" (a repo name, not a legal
  entity). See [ADR 0013](docs/decisions/0013-apache-2-0-license-and-copyright.md).
  Found missing during the pre-publication review ahead of making the
  repository public: with no `LICENSE`, default exclusive copyright applied,
  which is incompatible with a repository meant to be shared. Mirrors
  [Stock ADR 0014](docs/decisions/stock-0014-license-and-copyright.md), which
  hit the identical gap for the identical reason and settled the same
  question for Stock itself; that ADR is explicit the decision doesn't
  extend here, so it was confirmed independently with the owner rather than
  assumed.
- **`.claude/setup.sh`** installs `mise` on a Claude Code cloud session, the
  one thing no command run from inside a session can do for itself. Started
  as Stock's own script, carried over verbatim
  ([`stock-0010`](docs/decisions/stock-0010-cloud-environment-setup-script.md)),
  pinned to a specific version — but trying it for real, in an actual Custom
  environment, failed: `mise.run` downloaded, then its own attempt to fetch
  the pinned mise binary hit a 403. Reading the installer explained why: the
  pin matched when it was written and went stale by the time it ran, and a
  non-matching version routes through a GitHub release asset, which a cloud
  session's proxy blocks. The script now installs mise **unpinned**, which
  mise's own docs recommend regardless of this problem, and which also keeps
  the installer off GitHub permanently rather than until the next stale pin
  ([ADR 0010](docs/decisions/0010-mise-unpinned-via-mise-run.md); an
  intermediate attempt via mise's Ubuntu PPA is recorded there too, tried and
  reverted once the real cause turned out to be the pin, not `mise.run`
  itself). Same one-time, per-account manual step as Stock's version —
  pasting the script into a cloud environment's Setup Script field — that
  nothing committed to a repo can complete unassisted.

### Changed

- **`stock-version` corrected from `0.3.0-rc.2` to `0.3.0`.** Stock cut the
  stable tag one commit after the candidate this project was already
  synced to — a single-file diff, internal to Stock's own UAT record, that
  changes nothing here. Confirmed by diffing the two tags directly rather
  than assumed from the version numbers alone.
- Grafted from [Graftwork Stock](https://github.com/Graftwork/stock)
  v0.3.0-rc.1 — pinned toolchain, OpenSpec review layer, spec traceability guard
  with declared gaps, UAT as a human gate, release process, CI, and pre-commit
  including `detect-secrets`. The graft is the root commit and is byte-identical
  to the tag. The version is recorded in `pyproject.toml` under
  `[tool.graftwork]`, which is where a later re-sync starts reading Stock's
  CHANGELOG from.
- The decisions this project had already reached, carried forward as ADRs
  0001–0009 and the glossary: where it runs, the two-tier sweeper, a real local
  mailbox, server-side Sieve ruled out, n8n as the execution engine, postal
  terminology, walk rules in a database, pruning as a move to Trash, and
  IMAP-agnostic collection.
- `docs/UAT.md` and `docs/RELEASING.md` rewritten for this project, replacing
  Stock's own cases and release sequence while keeping both formats.

### Changed

- **Re-synced to Stock `v0.3.0-rc.2`.** Stock's own fix for exactly the bug
  this project found by hand during the original graft: the graft steps said
  nothing about `openspec/changes/`, so Stock's backlog stubs and archived
  changes travelled across by default. This project had already removed them
  before Stock's fix existed; the re-sync is a credit and a version bump, not
  new work — `stock-version` in `pyproject.toml` now reads `0.3.0-rc.2`, with
  a `resynced` date alongside `grafted` so the two stay distinguishable.
  `main` was updated first, by applying Stock's own diff directly and
  checking the result was tree-identical to the `v0.3.0-rc.2` tag, the same
  verification the original graft used; the project branch then merged that
  and resolved conflicts by keeping this project's own rewritten docs, since
  none of Stock's specific text in this diff was about anything but Stock's
  own release process. First real use of
  [the resync-in-flight-graft skill](.claude/skills/stock-resync-in-flight-graft/SKILL.md)
  (renamed with the `stock-` prefix when Stock brought it back into its own
  foundation — see the `[Unreleased]` entry below),
  written from doing this once so the next Stock update doesn't start from
  nothing.

### Notes

- **This repository was rebuilt.** An earlier version of it was retired because
  personal detail supplied as context while scoping the work had been written
  into a spec, then into code, then pushed — and git history is rewritten rather
  than edited. Nothing was imported from it: the decisions above were rewritten
  into a clean graft, and the one ADR whose text carried a real address pattern
  was rewritten from scratch rather than copied and patched.
- The ADRs are renumbered from that earlier repository and start again at 0001.
  Stock's own ADRs are prefixed `stock-` since v0.3.0, so the two series no
  longer collide.
