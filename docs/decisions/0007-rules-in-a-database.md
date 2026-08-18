# ADR 0007: Walk rules and the Dead Letter Office live in a database, not in the repo

- **Status:** accepted
- **Date:** 2026-08-14
- **Carried forward:** written before this repository was rebuilt, and renumbered
  on the way in. The reasoning is unchanged — and the rebuild is the strongest
  evidence for it that could exist.

## Context

Walk rules map a recipient alias to a walk; the Dead Letter Office holds the
aliases that have no rule yet. Both need to live somewhere.

The first design of this work left this open, and leaned the other way to where
it ended up: *"A file is reviewable
in git, which suits a case study; a database suits editing from the Counter.
Likely a file first."* The reasoning was that a rule change would show up as a
diff — visible, reviewable, revertable — and that this repo is a case study in
working with Claude Code, so making the decision trail legible is worth real
weight.

That argument had a hole in it. **The rules are personal data.** The
classification key is the catch-all alias each site was given, so the rule set is
a list of every service signed up to, and the Dead Letter Office is the same list
for everything not yet triaged. This repo is public and meant to be shared as an
example of how a Product Owner can work with these tools. Committing the rules
would publish that list.

The workarounds are all worse than the problem: redact before committing (a
manual step, and one slip is permanent in git history), keep a private fork
(two repos to reconcile), or commit fictional rules and keep the real ones
elsewhere (at which point the file in git is decoration, not the source of
truth).

## Decision

Walk rules and Dead Letter Office entries live in a small database beside the
local mailbox on the mini PC. The repository holds the schema, the migrations,
and fixtures — never real rules.

The invented addresses used in tests and examples stay obviously invented, so
nobody has to judge whether a given address is real.

## Consequences

- The repo can stay public without leaking a list of the owner's accounts. The
  case study can show the whole mechanism using fixture rules, which is the part
  worth showing anyway.
- Rule history stops being visible in git — the original reason to prefer a file.
  If an audit trail turns out to matter, it belongs in the database as a change
  log the Counter can display, not in commits. Deferred until there is evidence
  it is wanted.
- The rules now live only on the mini PC, so they are only as durable as its
  backups. Losing them does not lose mail — untriaged mail is held, never pruned
  ([ADR 0008](0008-pruning-moves-to-trash.md) makes even a wrong rule
  recoverable) — but it does mean redoing triage.
- Editing from the Counter gets easier, which was the original argument *for* a
  database. It is a genuine benefit and it was not the deciding one.
- Tests for classification and retention take rules as arguments rather than
  reading a store, so the pure logic stays testable with no database at all.

## Alternatives considered

- **A YAML file committed to the repo.** The original lean. Rejected: it
  publishes the alias list, and every mitigation turns the file into either a
  manual chore or a decoration.
- **A YAML file outside the repo, gitignored.** Keeps the format simple with no
  schema to maintain, and keeps the personal data out of git. Genuinely close,
  and rejected on second-order grounds: it keeps none of the git-reviewability
  that was the only reason to prefer a file, while the Dead Letter Office is
  churn — addresses appear, get triaged, disappear — and the Counter will be
  writing to it concurrently with a running duty. That is a transaction, and
  hand-rolling one over a text file to avoid a schema is a poor trade.
- **Rules in the mailbox itself**, as IMAP folder names or keywords. Puts
  everything in one place, but overloads a mail store with configuration and
  makes a rule change a mail operation. Rejected as too clever.
