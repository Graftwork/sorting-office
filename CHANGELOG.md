# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
What each version number will mean for this project — and why it is 0.0.0 today
— is set out in [`docs/RELEASING.md`](docs/RELEASING.md).

## [Unreleased]

### Added

- **`.claude/setup.sh`** installs `mise` on a Claude Code cloud session, the
  one thing no command run from inside a session can do for itself. Started
  as Stock's own script, carried over verbatim
  ([`stock-0010`](docs/decisions/stock-0010-cloud-environment-setup-script.md)) —
  but trying it for real, in an actual Custom environment, failed: `mise.run`
  itself downloaded, then its own attempt to fetch the mise binary hit a 403
  from GitHub's release-asset repo-scoping. The script now installs mise via
  its Ubuntu PPA instead, which never touches GitHub
  ([ADR 0010](docs/decisions/0010-mise-via-ppa-not-mise-run.md)). Requires the
  same one-time, per-account manual step Stock's version did — pasting the
  script into a cloud environment's Setup Script field — that nothing
  committed to a repo can complete unassisted. Version pinning was lost in
  the switch and is recorded as an open gap, not silently dropped.

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
  [the resync-in-flight-graft skill](.claude/skills/resync-in-flight-graft/SKILL.md),
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
