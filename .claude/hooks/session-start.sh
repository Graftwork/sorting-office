#!/bin/bash
set -euo pipefail

# Only run this setup in Claude Code on the web / remote sessions.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

# mise won't run an untrusted config (see CLAUDE.md).
mise trust "$CLAUDE_PROJECT_DIR" >/dev/null 2>&1 || true

# `mise install` resolves the pinned python/uv/node versions via GitHub
# release metadata (api.github.com, mise-versions.jdx.dev). This remote
# session's egress policy scopes GitHub access to this repo only, so those
# lookups are denied and `mise install` — and therefore every `mise run`
# task, which auto-installs all declared tools first — fails here. `uv`
# fetches the same CPython builds through a path the policy allows, so use
# it directly instead. Node isn't affected (mise installs it straight from
# nodejs.org) but is skipped too since nothing in dev setup needs it ahead
# of `npx`, which fetches its own package on first use.
uv python install 3.13

# Python dev dependencies (pytest, ruff, coverage) — pinned in uv.lock.
uv sync
