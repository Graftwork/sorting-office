#!/bin/bash
# Installs mise for Claude Code cloud sessions, where it is not pre-installed
# and cannot be fetched by any command run from inside a session — see
# docs/decisions/stock-0010-cloud-environment-setup-script.md for what was
# tried and ruled out, and why this has to be a setup script.
#
# This file is not executed automatically. Copy its contents into a Custom
# cloud environment's Setup Script field (claude.ai/code environment
# settings) — a one-time, per-account step only a human can do; nothing
# committed to a repo can complete it unassisted.
#
# That environment's network access must also reach mise.run and GitHub.
# Under Custom, ticking "Also include default list of common package
# managers" and adding mise.run is the simplest way to get both — Trusted
# alone does not cover mise.run, since it is not on the default allowlist.
set -euo pipefail

# MISE_INSTALL_PATH: /usr/local/bin is on PATH for every process by default,
# unlike the installer's usual ~/.local/bin — confirmed by direct test, not
# assumed. A cloud session's shell state does not persist between separate
# tool calls, so anything relying on a PATH edit made in ~/.bashrc or
# ~/.profile is invisible to Claude's next command; installing straight to
# an already-searched directory sidesteps that instead of working around it.
#
# MISE_VERSION: pinned, consistent with mise.toml pinning everything mise
# itself manages. Bump deliberately, the same way mise.toml's own pins move.
#
# Both variables must sit before `sh`, not before `curl` — in a pipeline,
# `VAR=val cmd1 | cmd2` only sets VAR for cmd1. The install script runs as
# the `sh` process and reads its own environment, so that is where the
# variables have to be.
curl https://mise.run | MISE_INSTALL_PATH=/usr/local/bin/mise MISE_VERSION=2026.8.8 sh
