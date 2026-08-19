#!/bin/bash
# Installs mise for Claude Code cloud sessions, where it is not pre-installed
# and cannot be fetched by any command run from inside a session — see
# docs/decisions/0010-mise-unpinned-via-mise-run.md for the two things this
# repo actually tried and ruled out before landing here, and why.
#
# This file is not executed automatically. Copy its contents into a Custom
# cloud environment's Setup Script field (claude.ai/code environment
# settings) — a one-time, per-account step only a human can do; nothing
# committed to a repo can complete it unassisted.
#
# That environment's network access needs mise.run and mise.jdx.dev — not
# GitHub, if the reasoning below holds. Under Custom, ticking "Also include
# default list of common package managers" and adding both domains is the
# simplest way to get there; Trusted alone does not cover either, since
# neither is on the default allowlist.
#
# Deliberately does NOT pin a mise version. mise's own docs argue against it
# directly: "Pinning mise back is like preventing apt update or brew update
# from refreshing package metadata: it can hide deprecation messages and
# cause bit rot with upstream integrations." A project that wants a floor
# sets `min_version` in mise.toml — a promise mise checks against itself at
# run time — not a specific executable locked in an install script.
#
# That restraint also happens to be what keeps this script off GitHub.
# mise.run's installer only reaches GitHub when the requested version
# doesn't match the version bundled in the copy of the script mise.run is
# currently serving — which is exactly what pinning caused here: a pin that
# matched when it was written went stale the next time mise shipped, and
# the installer silently fell onto a GitHub release-asset download that
# this session's GitHub proxy then 403s (release-asset requests are scoped
# to repositories attached to the session, and jdx/mise isn't one). Leaving
# the version unset makes "requested equals current" true by construction,
# on every run, forever — always mise.jdx.dev for the binary, always the
# checksum baked into that same script copy, never GitHub.
set -euo pipefail

# MISE_INSTALL_PATH: /usr/local/bin is on PATH for every process by default,
# unlike the installer's usual ~/.local/bin — confirmed by direct test, not
# assumed. A cloud session's shell state does not persist between separate
# tool calls, so anything relying on a PATH edit made in ~/.bashrc or
# ~/.profile is invisible to Claude's next command; installing straight to
# an already-searched directory sidesteps that instead of working around it.
curl https://mise.run | MISE_INSTALL_PATH=/usr/local/bin/mise sh
