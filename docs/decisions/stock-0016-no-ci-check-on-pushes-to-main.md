# Stock ADR 0016: No CI check for session links on pushes to `main`

- **Status:** accepted
- **Date:** 2026-10-03

## Context

The `session-links` workflow runs on `pull_request` only. A commit that
reaches `main` without a pull request is never scanned. Only a `main` ruleset
requiring pull requests closes that, and Stock cannot enforce one while
private: `gh api repos/Graftwork/stock/rulesets` returned 403 ("Upgrade to
GitHub Pro or make this repository public") on 2026-10-03 (measured). The
maintainer reports the ruleset is disabled for the same reason.
[`docs/GOING_PUBLIC.md`](../GOING_PUBLIC.md) step 7 already covers enabling it.

## Decision

No `push: branches: [main]` trigger. The control for direct pushes is the
ruleset. Until it is enforceable, the only guard is the `no-session-link`
pre-commit hook, which `--no-verify` skips.

## Consequences

- A direct push with a session link is not caught by CI. Accepted: the
  maintainer is the only person who can push to `main`.
- When the ruleset is enforced, add `Session link - commits` and
  `Session link - description` to its required checks.

## Alternatives considered

- **Scan on push to `main`.** Rejected: it runs after the link is in history,
  and `main`'s history is meant to be stable. A red check cannot remove the
  link; only a history rewrite can.
