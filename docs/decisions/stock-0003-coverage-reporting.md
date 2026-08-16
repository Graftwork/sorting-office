# Stock ADR 0003: Codecov from day one, but never blocking a fresh stamp

- **Status:** accepted
- **Date:** 2026-07-25

## Context

Coverage is part of the transparency layer, not a vanity metric: it is one of the
surfaces that shows whether the verification layer is real. So it should be
visible in the README from the start.

This collides with the harder rule that a freshly stamped project is green on
commit one with zero edits. Codecov on a **private** repo needs a `CODECOV_TOKEN`
secret, and a new stamp has no secrets configured. A required upload step would
mean every new project starts red — precisely the plumbing-before-ideas problem
the foundation exists to remove.

## Decision

Keep the Codecov upload in CI from day one, but make it non-blocking:
`fail_ci_if_error: false` plus `continue-on-error: true`.

Coverage itself is always produced locally and in CI — `pytest` writes
`coverage.xml` and a terminal summary regardless. Only the *upload* is best-effort.

## Consequences

- A fresh stamp is genuinely green with no secrets and no edits.
- Activation is one step: add `CODECOV_TOKEN` to the repo secrets and the badge
  goes live on the next push. No workflow edit needed.
- The cost is honest: until the token exists, the badge in the README shows
  "unknown". The real coverage number is still in the CI log and in
  `coverage.xml`, so nothing is actually hidden — it is just not hosted yet.
- A silently failing upload will not turn CI red. That is the intended trade: CI
  red should mean the code is wrong, not that a third-party service was down.

## Alternatives considered

- **Codecov as a required step.** Every new private repo starts red until the
  token is added. Rejected — it breaks the core promise.
- **Self-contained SVG badge committed by CI.** No account needed and works
  offline, but no PR comments or trend history, and a bot commit on every push.
  Worth revisiting if Codecov's hosted value stops justifying the setup step.
