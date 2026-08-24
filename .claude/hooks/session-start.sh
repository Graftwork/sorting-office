#!/bin/bash
set -euo pipefail

# Only run this setup in Claude Code on the web / remote sessions.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

# mise won't run an untrusted config (see CLAUDE.md).
mise trust "$CLAUDE_PROJECT_DIR" >/dev/null 2>&1 || true

# `mise install` (and every `mise run` task) can't fetch the pinned
# python/uv here — see ADR 0011 for why and what was ruled out.
uv python install 3.13

# Python dev dependencies (pytest, ruff, coverage) — pinned in uv.lock.
uv sync
