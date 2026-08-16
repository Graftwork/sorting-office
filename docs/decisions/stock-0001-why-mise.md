# Stock ADR 0001: mise pins the toolchain, devcontainer is the reproducibility layer

- **Status:** accepted
- **Date:** 2026-07-25

## Context

A foundation repo is only worth grafting from if a stamped project behaves the
same on a laptop as it does in CI. The usual answer is a devcontainer, but
requiring one for every experiment is a tax: container rebuild times sit between
having an idea and testing it, and most experiments are abandoned before that
cost pays back.

The competing need is fast-fail. Spinning up a project has to be quick, or the
foundation discourages the very experiments it exists to enable.

## Decision

`mise.toml` pins the toolchain — Python, uv, Node — and is the single source of
truth for versions. It drives three places at once: the local shell, CI (via
`jdx/mise-action`), and the devcontainer (via the mise feature).

The devcontainer ships in the template but is not the default path. It layers on
top of mise rather than duplicating it, so there is no second list of versions to
keep in sync.

## Consequences

- The fast local path is `mise install && uv sync` — seconds, not minutes.
- CI and laptop resolve to identical pinned versions, because both read `mise.toml`.
- The devcontainer earns its keep once a project graduates from experiment to
  something with collaborators or a publishing story. It is there when needed and
  costs nothing when ignored.
- Anyone without mise installed has a slightly worse day; `mise.toml` is readable
  enough that the pinned versions can be installed by hand.

## Alternatives considered

- **Devcontainer only.** Most reproducible, but the rebuild cost lands on every
  throwaway experiment. Rejected as too slow for fast-fail.
- **asdf.** Similar model, but slower, and needs a plugin per tool.
- **No pinning, just `.python-version`.** Covers Python and nothing else; Node
  drift would silently change what the OpenSpec CLI does.
