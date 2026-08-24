# ADR 0011: `uv` installs Python directly; `mise run` doesn't work on Claude Code web

- **Status:** accepted
- **Date:** 2026-08-19

## Context

[ADR 0010](0010-mise-unpinned-via-mise-run.md) got the `mise` binary itself
onto a Claude Code cloud session, via a one-time Setup Script paste. That
does not make `mise install` work: `mise.toml` also pins `python = "3.13"`
and `uv = "0.11.16"`, and resolving either needs GitHub release metadata —
`api.github.com/repos/astral-sh/uv/releases` for uv, and (after
`mise-versions.jdx.dev`, itself blocked, is exhausted as a mirror) a
python-build-standalone GitHub release for Python. A Claude Code on the web
session's GitHub access is scoped to the one repository it's attached to
(`graftwork/sorting-office`), so both lookups are denied — measured directly:

```
$ mise install
mise WARN  Remote versions cannot be fetched for astral-sh/uv: HTTP status client error (403 Forbidden) for url (https://api.github.com/repos/astral-sh/uv/releases?per_page=100)
github response: {"message":"GitHub access to this repository is not enabled for this session. ..."}
...
mise ERROR Failed to install tools: aqua:astral-sh/uv@0.11.16, core:python@3.13
core:python@3.13: error sending request: client error (Connect): tunnel error: unsuccessful
```

This isn't only `mise install`'s problem. Every `mise run <task>`
auto-installs all of a project's declared tools before running the task it
was actually asked for, regardless of whether that task needs them —
confirmed by running `mise run openspec -- --version`, a task that only
shells out to `npx`, and watching it fail on the same python/uv error before
`npx` ever runs. So `mise run check`/`test`/`lint`/`trace`/`openspec` are all
broken in this environment, not only the tools each happens to touch.

`uv` itself is unaffected: `uv python install 3.13` reaches the same CPython
builds through a path the policy allows, and succeeds in a few seconds.
`uv self update` does hit the same wall — it also queries
`api.github.com/repos/astral-sh/uv` — so the `uv` already on the image
(0.8.17 when this was written) can't be moved to the pinned 0.11.16 from
inside a session.

## Decision

`.claude/hooks/session-start.sh` — a `SessionStart` hook, not a Setup
Script; it needs the repository already checked out, which happens after a
Setup Script runs — does:

```bash
uv python install 3.13
uv sync
```

instead of `mise install`. This gets a working venv with the right
interpreter and the pinned dev dependencies (`uv.lock` still governs those
exactly), using whatever `uv` binary the image already provides.

Lint and test commands inside a Claude Code web session use `uv run ruff
check .`, `uv run pytest`, `uv run python scripts/check_spec_traceability.py`
directly — not `mise run lint`/`mise run test`/`mise run trace` — since
those tasks are exactly the ones broken by this. Local development and CI
are untouched: both reach GitHub without restriction and keep using `mise
run` as documented.

## Consequences

- **The pinned `uv` version (0.11.16) isn't what actually runs** in a Claude
  Code web session — it runs whatever `uv` the image ships (0.8.17 when this
  was written). Confirmed compatible for this repo's purposes (`uv sync`,
  `uv run`), but a real version gap, worth re-checking if a future `uv sync`
  ever behaves differently only in this environment.
- **`mise run <task>` is not "how you verify it" in this environment.**
  Anyone driving this repo from Claude Code on the web needs to reach for
  `uv run …` / `npx …` directly instead — which is why this is an ADR and
  not just a comment in the hook script.
- Scoped to Claude Code web sessions only. Nothing here changes `mise.toml`,
  so the pins stay exact everywhere else.

## Alternatives considered

- **Ask for the session's GitHub access to include `astral-sh/uv` and the
  Python build repo.** That scoping is a per-session security boundary, not
  an environment domain allowlist like the one ADR 0010 used for
  `mise.run`/`mise.jdx.dev` — there's no setup-script equivalent for
  widening it, and doing so would mean trusting arbitrary third-party
  repositories' release assets inside every session for this project, a much
  bigger door to open than the problem needs.
- **Loosen `mise.toml`'s pins** (e.g. `python = "system"`) so mise doesn't
  need to fetch a specific build at all. Rejected without trying it: the
  pins are shared by every environment this project runs in, and loosening
  them to fix one sandbox's network policy would weaken reproducibility
  everywhere else for a problem that's local to this one environment.
- **Wait for mise to skip the auto-install-on-run behaviour.** Checked
  `mise settings ls` for anything resembling it; no such setting exists in
  2026.8.8.
