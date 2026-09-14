# Stock ADR 0012: `uv` installs Python directly; `mise run` doesn't work on Claude Code web

- **Status:** accepted
- **Date:** 2026-08-24

## Context

[Stock ADR 0010](stock-0010-cloud-environment-setup-script.md) gets `mise`
itself onto a Claude Code cloud session. That doesn't make `mise install`
work: `mise.toml` also pins `python = "3.13"` and `uv = "0.11.16"`, and
resolving either needs GitHub release metadata —
`api.github.com/repos/astral-sh/uv/releases` for uv, a
`python-build-standalone` release for Python. A cloud session's GitHub
access is scoped to the repositories attached to it, and neither of those
repos is ever a grafted project's own. Found grafting [sorting-office](
https://github.com/Graftwork/sorting-office), measured directly:

```
$ mise install
mise WARN  Remote versions cannot be fetched for astral-sh/uv: HTTP status client error (403 Forbidden) for url (https://api.github.com/repos/astral-sh/uv/releases?per_page=100)
github response: {"message":"GitHub access to this repository is not enabled for this session. ..."}
...
mise ERROR Failed to install tools: aqua:astral-sh/uv@0.11.16, core:python@3.13
core:python@3.13: error sending request: client error (Connect): tunnel error: unsuccessful
```

This isn't only `mise install`'s problem: every `mise run <task>`
auto-installs all of a project's declared tools first, regardless of what
the task itself needs — confirmed by running a task that only shells out to
`npx`, and watching it fail on the same python/uv error before `npx` ever
ran. So `mise run check`/`test`/`lint`/`trace`/`openspec` are all broken
here, not only the tools each happens to touch.

The mechanism, traced directly rather than left at the symptom:

- `curl https://api.github.com/repos/astral-sh/uv/releases?per_page=5` → the
  same 403.
- `uv python install 3.13.7`, forcing a real download → succeeded, 30.8MiB
  in 5.28s.
- `RUST_LOG=uv=debug uv python install 3.12.11` traced the exact URL:
  `https://github.com/astral-sh/python-build-standalone/releases/download/20250902/cpython-3.12.11%2B20250902-x86_64-unknown-linux-gnu-install_only_stripped.tar.gz`
  — a GitHub URL, the same host the blocked API calls hit.
- `curl -sSI` on that URL: a **302 redirect to
  `release-assets.githubusercontent.com`**, a separate, reachable host. A
  direct `releases/download/<tag>/<file>` link resolves through that
  redirect; `api.github.com` and the release-listing pages do not.

The boundary isn't "uv uses a different provider" (checked and ruled out —
uv's Python builds are GitHub releases too, same as mise's); it's *which
shape of GitHub request* the session's proxy allows. A request that already
knows its download URL redirects through a CDN host outside the
restriction. A request that has to ask GitHub's API what's available
first — what `mise install` always does — does not. `uv python install
<version>` never asks.

**Unmeasured:** `mise`'s own `core:python` backend fails with a
connection/tunnel error, not a clean 403 — a different failure mode — and
`mise` isn't installed in this environment to trace further. The exact host
it targets, and why it fails at the connection level rather than the API's
403, is open for whenever a session has `mise` on `PATH` to check.

## Decision

Ship [`.claude/hooks/session-start.sh`](../../.claude/hooks/session-start.sh)
as a `SessionStart` hook, not a Setup Script — it needs the repository
already checked out, which happens after any Setup Script runs. Gated on
`CLAUDE_CODE_REMOTE=true` so it's a no-op locally and in CI:

```bash
python_version="$(grep -m1 '^python = ' mise.toml | sed -E 's/^python = "(.*)"$/\1/')"
uv python install "$python_version"
uv sync
```

The Python version is read from `mise.toml` rather than hardcoded, since a
grafted project can move that pin. `uv sync` installs the pinned dev
dependencies from `uv.lock`. Registered in `.claude/settings.json`'s
`hooks.SessionStart`, so it runs automatically once committed — no manual
per-account step, unlike [Stock ADR 0010](stock-0010-cloud-environment-setup-script.md)'s
Setup Script.

`CLAUDE.md` and `README.md` both point here and say to use `uv run`/`npx`
directly instead of `mise run lint`/`test`/`trace` in this environment.

## Consequences

- **The pinned `uv` version isn't what actually runs** in a cloud
  session — whatever `uv` the image ships. `uv self update` hits the same
  blocked API path as `mise install`, so nothing inside a session can move
  it. Worth re-checking if `uv sync` ever behaves differently only here.
- **`mise run <task>` doesn't verify anything in this environment.** Use
  `uv run …`/`npx …` directly — why this is a committed hook and an ADR,
  not just something someone has to already know.
- Scoped to cloud sessions only, via `CLAUDE_CODE_REMOTE`. Local and CI runs
  never execute the hook's body.
- No manual step needed, unlike [Stock ADR 0010](stock-0010-cloud-environment-setup-script.md) —
  a `SessionStart` hook is a git object.

## Alternatives considered

- **Widen the session's GitHub access** to include `astral-sh/uv` and the
  Python build repo. Rejected — that's a per-session security boundary, not
  a domain allowlist; widening it would mean trusting arbitrary third-party
  release assets in every session for every grafted project.
- **Loosen `mise.toml`'s pins** (e.g. `python = "system"`). Rejected without
  trying it — the pins are shared by every environment a project runs in;
  loosening them for one sandbox's network policy weakens reproducibility
  everywhere else.
- **Disable mise's auto-install-on-run** via
  `MISE_TASK_RUN_AUTO_INSTALL`/`task.run_auto_install`. Would fix `mise run`
  but leaves `mise install` broken and still needs the network exception
  this ADR avoids opening. Revisit only if a future task needs `mise run`'s
  own dependency graph.
