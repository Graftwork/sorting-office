# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
What each version number will mean for this project — and why it is 0.0.0 today
— is set out in [`docs/RELEASING.md`](docs/RELEASING.md).

## [Unreleased]

### Added

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
