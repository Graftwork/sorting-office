# Stock ADR 0011: Ship the in-flight-graft resync skill; leave the general case a backlog item

- **Status:** accepted
- **Date:** 2026-08-18

## Context

Grafting is one direction of a two-way relationship Stock was meant to have
with the projects built on it: lessons flow from real projects back into
Stock (the mechanism this whole foundation already runs on — `WORKFLOW.md`,
`CLAUDE.md`'s house rules, and most of this repo's ADRs exist because a real
graft found something), and Stock's own improvements are meant to flow back
out, "intelligently," into projects that already exist.

The second direction never got built past `docs/RELEASING.md` step 10 — read
Stock's CHANGELOG forward from a project's recorded `stock-version`, apply
each entry as its own small PR. That step's own text admits the gap: *"nothing
tracks whether a migration has landed."* When this was last discussed, the
call was to leave it there rather than design a general "intelligently pull
changes into an existing project" mechanism speculatively — Stock's own
convention is to grow "by promotion from things that proved themselves in real
projects, never by anticipation," and at the time there was no real re-sync
event to design against, only fresh grafts.

There now is one. `sorting-office` grafted from `v0.3.0-rc.1`, started real
work, and Stock moved to `v0.3.0-rc.2` before any of that work had merged to a
settled `main`. That is a narrower, more specific situation than the general
case `RELEASING.md` step 10 was written for: there is no settled history to
branch a normal re-sync PR from, and the project's entire identity — rewritten
README, its own ADRs, its own `docs/RELEASING.md` — lives on one unmerged
branch. A raw `git merge` from Stock's updated tag would try to reconcile that
against files the project has already wholesale rewritten, and fail the way
merges of same-topic-different-text files always fail: a wall of line-level
conflicts with no more signal in them than reading each file once would give.

`sorting-office` wrote a skill for exactly this situation and merged it —
[`resync-in-flight-graft`](https://github.com/Graftwork/sorting-office/blob/main/.claude/skills/resync-in-flight-graft/SKILL.md).
It splits the update by file rather than attempting one merge: untouched files
get a straight patch, verified by comparing tree hashes directly rather than
trusting the patch succeeded; already-rewritten files are read in full and
decided on by hand, `git checkout --ours` keeping the project's version once
that's decided. It correctly does not attempt the general, already-settled,
already-diverged case — its own precondition section says so and points back
to step 10 for that situation.

## Decision

Ship the skill in Stock, as
[`.claude/skills/stock-resync-in-flight-graft/SKILL.md`](../../.claude/skills/stock-resync-in-flight-graft/SKILL.md)
— renamed with the `stock-` prefix, content otherwise unchanged. It travels
via graft the same way the vendored `openspec-*` skills already do.

**The general case stays a backlog item, deliberately, not by oversight.**
This skill proved itself on one real project in one real, narrow situation. The
"already-settled, already-diverged, read-the-whole-CHANGELOG" case discussed
earlier is still unproven — building it now would be exactly the anticipation
Stock's own conventions warn against, just with better evidence sitting one
step closer than before. Some of this skill's techniques — diffing tag to tag
rather than trusting prose, verifying with tree hashes rather than assuming a
patch applied cleanly, splitting files by touched/untouched before deciding
how to treat them — look like they would generalize. That is a lead for
whoever designs the general case next, not a decision made here.

## Why the `stock-` prefix, not `graftwork-`

Skills don't have the collision problem ADRs do — `docs/decisions/` is one
flat, sequentially-numbered directory shared between Stock's own ADRs and a
project's own, which is why [Stock ADR 0008](stock-0008-adr-numbering.md) had
to exist at all. `.claude/skills/<name>/` doesn't share a namespace that way;
an ordinary kebab-case name collision is possible but not structurally
guaranteed the way sequential numbers were.

The prefix is still worth carrying, for a different, real reason: **resync
safety.** If this skill improves later and a grafted project re-syncs, the
project needs to tell at a glance whether `.claude/skills/<name>/` is Stock's
(safe to overwrite on resync) or the project's own (must not be silently
clobbered) — the same problem the ADR prefix solves, one level down. Given
that, matching the ADR convention already established (`stock-`, not a second,
different prefix for a different asset type) is more consistent than
introducing `graftwork-` for skills specifically. `graftwork-` was the name
first proposed; `stock-` is what shipped, for consistency with the one prefix
convention this repo already has.

## Consequences

- A project that grafts, starts real work, and finds Stock has moved before
  anything has merged gets a proven, mechanical way to catch up, instead of
  reinventing this — as `sorting-office` did — under time pressure.
- The general re-sync case is still undesigned. Anyone picking it up next has
  one more real data point than existed when it was last discussed, and a
  concrete technique (diff-and-categorize-by-file, verify-with-tree-hashes)
  worth trying to extend rather than starting from nothing.
- The skill's own precondition is easy to violate silently — a project that
  has, even once, committed something project-specific to `main` before
  re-syncing no longer qualifies, and the skill says so but cannot enforce it.

## Alternatives considered

- **Design the general resync mechanism now, using this as the seed.**
  Rejected for the reason above — one proven narrow case is not evidence for
  the general one, and building past what's proven is the anticipation this
  repo's own conventions exist to prevent.
- **Leave the skill in `sorting-office` only, don't bring it back.** Rejected
  — the situation it solves (Stock moves before a fresh graft's first work
  merges) is a property of *how Stock ships*, not of `sorting-office`
  specifically. Every project grafted close to a Stock release is exposed to
  it the same way `.claude/setup.sh` (Stock ADR 0010) addressed a gap every
  project inherits from Stock's own choices, not one project's particular
  circumstance.
- **`graftwork-` prefix, as first proposed.** Reconsidered above — `stock-`
  matches the one provenance-prefix convention this repo already has, rather
  than adding a second one for no functional difference.
