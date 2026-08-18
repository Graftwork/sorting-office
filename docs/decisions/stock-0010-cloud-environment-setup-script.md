# Stock ADR 0010: A committed setup script for Claude Code cloud sessions

- **Status:** accepted
- **Date:** 2026-08-17

## Context

[Stock ADR 0001](stock-0001-why-mise.md) standardizes the toolchain on `mise`.
Claude Code cloud sessions don't have it, and — measured from inside a live
session, not recalled — nothing a session can run gets it there:

- `mise` is absent from the documented pre-installed toolchain
  (Python/Node/Ruby/PHP/Java/Rust; no version manager), confirmed against
  <https://code.claude.com/docs/en/cloud-environments#installed-tools>.
- `curl https://mise.run | sh` fails — `mise.run` is not on a Trusted
  environment's default allowlist. Reproduced independently in two different
  sessions: `curl: (56) CONNECT tunnel failed, response 403`.
- `uv tool install mise` fails — mise isn't published on PyPI. Reproduced
  independently in both sessions with the identical error.
- A direct GitHub release-asset download fails too, for a different reason:
  the cloud session's GitHub proxy restricts release-asset requests to
  repositories attached to the session, and `jdx/mise` isn't one.

This isn't project-specific. It follows mechanically from Stock's own choice
to standardize on mise, so every project grafted from Stock inherits it the
first time someone drives it from Claude Code on the web rather than a
laptop — which is exactly how it was found, driving [sorting-office](
https://github.com/Graftwork/sorting-office).

**The docs name the setup script as the intended mechanism for exactly this
case**, confirmed verbatim: *"Use a setup script to provision the VM itself:
toolchains and CLI tools that aren't pre-installed. Use a SessionStart hook
for project setup that should run everywhere, cloud and local, like `npm
install`."* A SessionStart hook is committed to the repo
(`.claude/settings.json`) and reruns every session assuming the toolchain
already exists. A setup script runs once per environment, as root, before
Claude Code launches — but it lives in the cloud environment's own
configuration in the claude.ai/code UI, which is **not a git object**.
Nothing committed to any repo can complete this unassisted; a human has to
create or edit an environment once and paste a script in.

## Decision

Ship [`.claude/setup.sh`](../../.claude/setup.sh) as the script to paste into
a Custom environment's Setup Script field, and this ADR as where the reasoning
and the manual step live. `README.md`/`CLAUDE.md` point here rather than
restating it.

The script installs mise to `/usr/local/bin`, pinned to a specific version,
using variables mise's own installer documents (`MISE_INSTALL_PATH`,
`MISE_VERSION`). Both choices were checked, not copied from the first thing
that looked plausible:

- **`/usr/local/bin`, not the installer's default `~/.local/bin`.** Verified
  directly: a value written to `~/.bashrc` in one Bash tool call is invisible
  to the next — "shell state does not persist between commands" isn't
  incidental, it's exactly the property that breaks a PATH edit made that
  way. `/usr/local/bin` is already on `PATH` for every call, confirmed by
  writing an executable there and finding it from a separate call with no
  PATH or rc edit at all.
- **Pinned, not floating.** Consistent with `mise.toml` pinning everything
  mise itself manages — the binary that enforces those pins shouldn't be the
  one unpinned thing in the chain.
- **The env vars sit before `sh`, not before `curl`.** In a pipeline,
  `VAR=val cmd1 | cmd2` sets `VAR` only for `cmd1`. The install script runs
  as the `sh` process and reads its own environment, so the variables have to
  be placed there — a fix that would otherwise look correct while silently
  not applying.

**What this does not do.** The script installs `mise` itself only — it does
not also run `mise trust && mise install`. Whether a setup script runs before
or after the repository is cloned isn't confirmed anywhere in the docs this
was checked against, and `mise install` needs `mise.toml` on disk to mean
anything. Rather than assume an ordering, the script does the one thing that
is independent of it, and everything downstream happens the normal way, once
`mise` exists on `PATH`.

**What could not be verified.** `curl https://mise.run` returns 403 in every
session available to check this from — the actual install, past that point,
was never observed to complete. Everything about *why* it fails and what the
fix has to look like is measured; whether the fixed script runs clean end to
end once the domain is allowlisted is not, and is worth confirming the first
time someone actually adds `mise.run` to a Custom environment.

## Consequences

- A grafted project stops rediscovering this from scratch. The fix and the
  reasoning travel with the graft, the same way `mise.toml` itself does.
- The manual step doesn't go away, and no amount of repo automation removes
  it — worth saying plainly rather than implying the script alone fixes
  this. Someone still has to create a Custom environment, set its network
  access, and paste the script in, once per account.
- The pinned version will drift from mise's actual latest release over time.
  That's the same trade-off `mise.toml` already accepts for Python, uv, and
  Node, for the same reason: reproducibility over always-latest.

## Related, not addressed here

Investigating this also surfaced that pulling Docker images inside a cloud
session fails against `production.cloudfront.docker.com`, while the docs'
Trusted allowlist names `production.cloudflare.docker.com` — a different
host. That's a discrepancy in Anthropic's own docs or allowlist, not a
consequence of any decision Stock has made, so it doesn't belong in this ADR
or get a workaround here. Worth reporting to Anthropic directly if it's still
reproducing.

## Alternatives considered

- **A `SessionStart` hook instead.** Ruled out by the docs' own stated
  distinction: hooks assume the toolchain exists, they don't install one, and
  they rerun every session rather than provisioning once.
- **Document the manual `curl`/`uv`/GitHub attempts as "just do this
  yourself."** Rejected — all three are dead ends, verified independently
  twice, not workarounds someone is failing to find.
- **Fold the Docker/CloudFront finding into this ADR.** Rejected — different
  root cause, different owner. Bundling it in would make this ADR harder to
  act on for the one thing it actually fixes.
