# Stock ADR 0002: OpenSpec runs through npx at a pinned version

- **Status:** accepted
- **Date:** 2026-07-25

## Context

OpenSpec is the review layer: plain-English scenarios that non-code review hangs
off. It is distributed on npm as `@fission-ai/openspec`. Stock is otherwise a
Python-first foundation, so pulling in a Node dependency tree is a real cost, and
Node exists in this project for exactly one reason — running this CLI.

Note that the bare `openspec` name on npm is an unrelated 2019 placeholder at
version 0.0.0. The package we want is scoped: `@fission-ai/openspec`.

## Decision

Run OpenSpec via `npx --yes @fission-ai/openspec@<version>`, with the version
pinned in `mise.toml` as `OPENSPEC_VERSION`, and wrapped as `mise run openspec`.

No `package.json`, no `node_modules`, no lockfile in the repo.

## Consequences

- The spec tooling version is explicit and reviewable in one place. A bump is a
  one-line diff, which is exactly the kind of change that belongs in the
  CHANGELOG as a migration step for grafted projects.
- Python tooling stays uncontaminated by a JS dependency tree.
- `npx` caches, so the cost is a one-off download per version per machine.
- The tradeoff: the first OpenSpec command on a cold machine needs network
  access. Acceptable, because spec authoring is an online activity anyway.
- Upgrades are deliberate. Nothing floats to `@latest` behind your back, so the
  scenario format cannot shift under the traceability guard without a commit
  saying so.

## Alternatives considered

- **`npx openspec@latest`.** Unpinned. The scenario format could change under
  the guard with no commit recording it. Rejected outright.
- **Add a `package.json` and install it as a devDependency.** Correct for a Node
  project; here it means a lockfile and `node_modules` for a single CLI.
- **Vendor the CLI.** Removes the network need but makes upgrades manual and
  invisible.
