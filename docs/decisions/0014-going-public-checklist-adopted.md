# ADR 0014: Adopt Stock's going-public checklist, and run it before publication

- **Status:** accepted
- **Date:** 2026-09-15

## Context

`Graftwork/stock` went public and, in the run-up, assembled a real checklist
from its own pre-publication review — [`docs/GOING_PUBLIC.md`](../GOING_PUBLIC.md)
and [Stock ADR 0015](stock-0015-going-public-checklist.md). This project is
heading toward the same event, for the same presentation-driven reason Stock
was, so the checklist applies directly rather than by analogy.

Bringing it in now, ahead of any tagged Stock release, follows the pattern
already set by the mise fixes and the resync skill: a real finding on this
project fed Stock's process before Stock formalized it, and this is the
reverse direction — a real finding on Stock, fed back here, before Stock has
cut a release to resync against normally. `docs/RELEASING.md` step 8 still
applies once Stock tags a release; this is the one-off exception the
situation calls for, not a new standing practice.

**Applying the checklist here surfaced two independent problems**, neither of
which is about going public directly:

- **`stock-0012` and `stock-0014` were missing from `docs/decisions/`.**
  Both existed in Stock at the exact `v0.4.0` tag this project's `stock-version`
  already claims to be synced to — the earlier resync ([#9](https://github.com/Graftwork/sorting-office/pull/9))
  copied `stock-0009`, `stock-0011`, and `stock-0013` but missed these two.
  `stock-0012` is Stock's own record of the `uv`-not-`mise-run` fix this
  project found independently (already covered here by its own
  [ADR 0011](0011-uv-not-mise-run-on-claude-code-web.md)); `stock-0014` is
  Stock's license decision, deliberately not binding here (see
  [ADR 0013](0013-apache-2-0-license-and-copyright.md)) but, on the same
  logic that keeps `stock-0009` here despite "not a template repo" not being
  this project's decision to make either, still part of the historical
  record that travels with the graft as a block. Fixed in the same change as
  this ADR, since both are `docs/decisions/` housekeeping either way.
- **Nothing else the checklist's mechanical items check (full-history secret
  scan, cross-repo reference check, stale conditional wording sweep) found
  anything.** Recorded so a future reader can tell the checklist was actually
  run, not skipped — see Consequences.

## Decision

- Add [`docs/GOING_PUBLIC.md`](../GOING_PUBLIC.md), adapted from Stock's:
  cross-references point at this project's own `docs/UAT.md` case 2 and
  ADR 0013 rather than Stock's, and the CI job-name gotcha in section 7 is
  confirmed against this project's own `ci.yml` rather than assumed to
  match Stock's.
- Add [`stock-0012`](stock-0012-uv-not-mise-run-on-claude-code-web.md),
  [`stock-0014`](stock-0014-license-and-copyright.md), and
  [`stock-0015`](stock-0015-going-public-checklist.md) verbatim, closing the
  gap against the `v0.4.0` tag this project already claims and bringing in
  the new one.
- Ran checklist items 1–4 now (results below); items 5–7 are left open per
  house rules — a human stranger-read and the GitHub-side settings are not
  something an agent session can close.

## Consequences

Checklist items 1–4, run 2026-09-15:

1. **License and copyright** — `LICENSE`/`NOTICE` present, copyright holder
   is a real person, cross-references in `NOTICE` checked directly and
   resolve (this project's own, written after finding Stock's didn't).
   Decision recorded as [ADR 0013](0013-apache-2-0-license-and-copyright.md).
2. **Full-history secret scan** — `git log --all -p --diff-merges=cc`
   against common credential patterns: no hits beyond commit SHAs and badge
   URLs incidentally matching the length heuristic. `detect-secrets`
   confirmed clean across the current tree (via the pre-commit environment;
   a fresh `uvx detect-secrets` invocation hit a transient PyPI timeout
   unrelated to any finding).
3. **Cross-repo reference check** — every `github.com/` reference in this
   repository's docs resolves to `Graftwork/sorting-office` (self),
   `Graftwork/stock` (public), or upstream open-source tooling (`jdx/mise`,
   `astral-sh`). No dead links.
4. **Stale conditional wording sweep** — every `private`/`internal` hit is
   about the mini PC's Tailscale-only network model (genuinely still true;
   only the repository's visibility is changing, not the postbox's) or is
   Stock's own historical text, not a stale claim about this repository.

Items 5 (whole-repository stranger read) and 6–7 (flip visibility; GitHub
branch protection) are **not** closed by this ADR — left open in
`docs/UAT.md`-equivalent fashion, for the owner.

## Alternatives considered

Wait for Stock to tag a release and pull this in as a normal versioned
resync. Rejected for the same reason the mid-flight resync skill exists:
the situation (about to publish, the checklist is exactly on point, Stock
hasn't tagged yet) is real and immediate, and waiting for ceremony that
doesn't change the content would just delay a publication-blocking check
for no benefit.
