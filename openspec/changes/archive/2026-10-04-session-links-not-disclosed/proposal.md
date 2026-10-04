## Why

This project's commit history carries private coding-session links. A session
link identifies more than the agent and model do: an account, sometimes a
device, always a private exchange nobody but its participants agreed to
publish. Cloud sessions add a `Claude-Session` trailer to commits by default,
so the links accumulate unless something stops them.

**Measured here** (`git log origin/main --grep='claude.ai/code/session'`, run
at the start of this change): 16 of 17 commits on `main` carry one. That is
the problem this change stops from growing; it does not remove the existing
links.

Stock `v0.6.0-rc.1` ships the fix as a migration entry (its CHANGELOG,
"Coding Session Links Are Not Disclosed"). This change is the part of that
migration that touches `openspec/specs/` and `scripts/`, so it runs as a full
OpenSpec change. The `.claude/settings.json` key, the `session-links` CI
workflow and the session-start hook line are a separate direct-route PR.

## What Changes

- `foundation` gains **Coding Session Links Are Not Disclosed**, alongside
  *AI Authorship Is Disclosed*: name the coding agent and model, never write a
  link to the private session that produced a change.
- A `no-session-link` **commit-msg pre-commit hook**, backed by
  `scripts/check_no_session_link.py` and its tests, refuses a commit message
  containing `claude.ai/code/session` (case-insensitive) and names the line.
- `default_install_hook_types: [pre-commit, commit-msg]` in
  `.pre-commit-config.yaml`, so a plain `pre-commit install` wires up both
  stages.
- A matching house rule in `CLAUDE.md`.
- The scenario about what an agent writes for a pull request or issue is a
  **declared gap** in `[tool.graftwork.traceability]`: the suite cannot observe
  it.

## Scope, stated plainly

The requirement governs what the agent writes and what a commit message
contains. It does not reach a link that the platform's GitHub tool appends to a
pull request body after the agent has written it; that is removed by editing
the body, or by the `session-links` workflow in the companion PR. Neither
touches commits already in history.

## Impact

- New files: `scripts/check_no_session_link.py`, `tests/test_check_no_session_link.py`.
- Changed: `openspec/specs/foundation/spec.md` (by archive), `CLAUDE.md`,
  `.pre-commit-config.yaml`, `pyproject.toml` (one declared gap).
- Both scripts and tests are carried verbatim from Stock `v0.6.0-rc.1`
  (`3ed5e22`), so a later re-sync stays a no-op.
- Existing commits are not changed. A test fixture in
  `tests/test_check_no_session_link.py` spells the link pattern on purpose;
  a future full-history scan for session links will match it, and that is
  expected.
