# Stock ADR 0009: Stock is not a GitHub template repository

- **Status:** accepted
- **Date:** 2026-08-17

## Context

Grafting from Stock means cloning it at a tag, dropping the history, and pointing
the remote at a new repository — four commands in
[the README](../../README.md#grafting-a-project-from-stock). GitHub offers a
one-click alternative: mark the repository as a template, and "Use this template"
creates a new repository from it.

The attraction is real. The person running this project works from the GitHub UI
rather than a terminal, and a button beats four commands.

**What a template actually copies** (checked against GitHub's documentation, not
recalled):

- the **default branch** only, or optionally all branches — files and directory
  structure, never full history
- the new repository starts with **a single commit**
- **tags and releases are not copied**, and there is no way to create a
  repository from a tag

That last point is the whole decision. A template snapshots a *branch*. Stock's
contract is built on *tags*:

| Stock relies on | A template provides |
| --- | --- |
| `git clone --branch v0.3.0` | whatever `main` is at that moment |
| `stock-version` recorded at graft time | no released version to record |
| CHANGELOG re-sync read forward from that version | no honest starting point |
| A UAT case verifying the published tag is graftable | nothing about the button |

This is not hypothetical. At the time of writing, `main` carries
`version = "0.3.0"` while the only tag for that work is `v0.3.0-rc.1` — the
stable release does not exist yet. A template graft would faithfully record
`stock-version = "0.3.0"` for a version that had never been released, and
nothing would go red. That is exactly the quiet corruption of the re-sync path
described in the `version-string-consistency` backlog stub.

The second problem compounds the first: **"Use this template" is a prominent
button and the README is prose.** It would become the discoverable path, and the
wrong one — particularly for agent sessions, which reliably take the cheapest
route offered.

The apparent benefit also turns out to be smaller than it looks. Grafting is not
done by hand here; an agent session does it, and agent sessions have a terminal
even when the person directing them does not. The UI gap that genuinely mattered
was *tagging*, and that is solved through the Releases page.

## Decision

Stock is **not** marked as a GitHub template repository. Grafting is by
clone-at-a-tag, as the README describes.

## Consequences

- Every graft starts from a named release, so `stock-version` records something
  real and the re-sync path has an honest starting point.
- There is no one-click route. That cost is accepted, and it is smaller than it
  appears because the clone is executed by an agent session rather than by hand.
- Someone will eventually notice the unused setting and be tempted to switch it
  on as an obvious improvement. That is what this ADR is for.
- If the project ever gains people who graft without an agent session, this
  decision should be revisited rather than assumed — the balance genuinely
  changes.

## Revisit when

A template becomes safe once `main` can no longer claim to be a release it is
not. The cheap way is a `-dev` suffix: immediately after tagging `vX.Y.Z`, bump
`main` to `vX.Y+1.0-dev`. Then a template graft records
`stock-version = "0.4.0-dev"`, which is self-evidently not a release, and the
graft instructions can say so plainly — *if your recorded version ends in `-dev`,
you grafted from an unreleased `main`; re-sync to the next tag before building
anything real.*

With that convention in place, a template is a legitimate second route rather
than a trap, and this ADR should be superseded rather than quietly ignored.

## Alternatives considered

- **Template from a `release` branch kept at the last released commit.** Would
  work, but "Use this template" takes the *default* branch, so `release` would
  have to become the default — which complicates every pull request to serve a
  convenience button.
- **Template plus a manual post-graft version check.** Puts the correctness
  burden on the step most likely to be skipped, on the path chosen precisely
  because it looked easier.
- **Mark it a template and accept branch-based grafts.** Honest only if the
  tag-based re-sync contract is abandoned too, which is most of what Stock is
  for.
