# Stock ADR 0015: A going-public checklist, promoted from Stock's own publication

- **Status:** accepted
- **Date:** 2026-09-14

## Context

Stock itself went public. In the run-up, a review found a real, non-speculative
list of problems, each discovered by actually doing the work rather than
anticipated in advance:

- No `LICENSE` file at all — default exclusive copyright, incompatible with a
  repository whose whole purpose is being forked from.
- `docs/CONTRIBUTING.md` attributed a workflow to the repository being
  private, when the real cause (Claude Code session owner-scoping) had
  nothing to do with visibility — checked directly against the file's own
  "Why this shape" section, not assumed.
- `docs/RELEASING.md` asserted "there are currently no live grafts," which
  quietly stopped being true once `sorting-office` grafted `v0.4.0` for real.
- `NOTICE` cited sections of two other files that didn't actually say what it
  claimed — found only when `sorting-office`'s own real re-sync wrote its own
  `NOTICE` and declined to copy the dangling reference forward.
- Six references across `CHANGELOG.md`, ADRs, and a skill file pointed at
  `Graftwork/sorting-office`, `Graftwork/sorting-office-retired`, and
  `stiffneckjim/comic-book-guy` — all still private at the time this
  repository went public, meaning every one of those links would 404 for a
  visitor who clicked through.
- No way for an agent session to check or set GitHub branch protection, so
  a repository whose entire release model depends on `main`'s history being
  stable had nothing technical enforcing that beyond personal habit — and,
  found only once actually attempted: GitHub refused to let this
  repository configure branch protection while it was still private, so the
  checklist item has to come after the visibility flip, not before it.

Five of these six are exactly that concrete — something that actually went
wrong or was actually missing, found by doing the work. The sixth checklist
item, a full-history secret scan (beyond the working-tree scan the existing
`detect-secrets` pre-commit hook already covers), is not incident-grounded
the same way: no secret was ever actually found in this repository's
history. It earns its place by extending an already-adopted, already-proven
practice to history the hook itself cannot reach, not by having caught
something. Worth stating plainly rather than blurring — a checklist that
claims more rigor than it has earned is exactly the kind of overstatement
this repository's own conventions exist to catch.

Stock's own conventions are explicit that the template grows by promotion
from things that proved themselves in real projects, never by anticipation
(`CLAUDE.md`, "Keep it unspeculative"). A go-public checklist assembled now,
from a real case, is exactly that kind of promotion — the same shape as the
`mise` ADRs, the resync skill, and the `openspec/changes/` graft-step fix,
all of which came from real friction on `sorting-office` rather than being
designed ahead of need.

## Decision

Add [`docs/GOING_PUBLIC.md`](../GOING_PUBLIC.md): a checklist covering
license and copyright, a full-history secret scan, a cross-repo dead-link
check, a sweep for stale conditional wording, a final whole-repository
stranger read, and the GitHub-side settings (branch protection in
particular) that no agent session can currently check on its own.

It is a separate document from `docs/UAT.md` and `docs/RELEASING.md` rather
than folded into either, because it runs on a different cadence: once,
immediately before a repository's visibility changes — not on every change
(`UAT.md`'s cases) and not on every release (`RELEASING.md`'s sequence).

## Consequences

- Every project grafted from this version of Stock inherits a real,
  proven checklist for its own eventual public release, rather than each
  project rediscovering the same gaps independently the way Stock itself
  just did.
- The document names a real, current capability gap (no agent access to
  GitHub branch protection) rather than pretending the checklist can be
  fully automated. That gap may close later; the document should be revised
  when it does, not left describing a limitation that no longer holds.
- This adds a document to maintain. Accepted cost: the alternative is losing
  this list to conversation history, which is precisely the failure mode
  Stock's own "measure, don't derive" and "record deliberate choices"
  conventions exist to prevent.

## Alternatives considered

- **Fold into `docs/RELEASING.md`.** Rejected — different cadence entirely;
  `RELEASING.md` runs every version, this runs once (or rarely, if a project
  stays private for years and only later decides to go public).
- **Fold into `docs/UAT.md`.** Rejected — `UAT.md`'s cases are tied to the
  per-change/per-release loop (run before every PR, before every archive);
  a going-public event doesn't fit that shape, and forcing it in would
  strain the file's own documented "case format."
- **Leave it as an unwritten practice, reconstructed from conversation each
  time a project goes public.** Rejected outright — this is the exact
  tribal-knowledge dependency Stock's own conventions exist to close, and
  the review that produced this checklist would otherwise have to happen
  again, from scratch, on `sorting-office`.
