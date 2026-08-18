#!/bin/bash
# Installs mise for Claude Code cloud sessions, where it is not pre-installed
# and cannot be fetched by any command run from inside a session — see
# docs/decisions/0010-mise-via-ppa-not-mise-run.md for what was tried,
# reproduced failing for real, and why this is the fix instead.
#
# This file is not executed automatically. Copy its contents into a Custom
# (or Trusted — see below) cloud environment's Setup Script field
# (claude.ai/code environment settings) — a one-time, per-account step only a
# human can do; nothing committed to a repo can complete it unassisted.
#
# Uses Ubuntu's mise PPA, not the curl-from-mise.run installer Stock ADR 0010
# originally shipped. That installer downloads the actual binary from a
# GitHub release asset, and this session's own test of it (not a guess)
# failed there with a 403: the cloud session's GitHub proxy restricts
# release-asset requests to repositories attached to the session, and
# jdx/mise is not one. The PPA route never touches GitHub, so it does not
# hit that wall — launchpad.net and ppa.launchpad.net are already on a
# Trusted environment's default allowlist, so this may not even need Custom
# network access at all. Try Trusted first; only reach for Custom if it
# still fails to reach Launchpad.
set -euo pipefail

# Scripts run as root already (confirmed by Anthropic's own docs), so no
# sudo — a minimal image is not guaranteed to have it configured, and it is
# an unnecessary dependency when the script is already running as root.
apt-get update
apt-get install -y software-properties-common
add-apt-repository -y ppa:jdxcode/mise
apt-get update
apt-get install -y mise

# Unlike the mise.run route, this does not pin a specific mise version —
# apt installs whatever the PPA currently carries. Pinning via
# `apt-get install -y mise=<version>` is possible in principle, but the
# PPA's actual version-string format (Launchpad revision suffixes and all)
# was not checked, and guessing wrong would fail the install outright rather
# than degrade gracefully. Left unpinned deliberately, flagged as a known
# gap rather than a silent one — worth revisiting once someone has the PPA's
# real version strings in front of them to pin against.
