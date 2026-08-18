# ADR 0009: Collection is IMAP-agnostic, and no provider is named in this repo

- **Status:** accepted
- **Date:** 2026-08-16
- **Carried forward:** written before this repository was rebuilt, and renumbered
  on the way in. The reasoning is unchanged; the note on history at the end has
  been rewritten, because the rebuild answered the question it left open.

## Context

The design was written against one specific mail provider. That provider's name
appeared throughout — in the ADRs, the README, the v1 change, and the collection
spec — and in places the design leaned on provider-specific machinery: a local
bridge process to get IMAP at all, and that provider's Sieve implementation.

Two problems with that, one of them practical and one about what this repo is
for.

**It is untestable.** Collection is the part of the pipeline that most needs a
test harness — it is the part that can lose mail — and there is no way to stand
up a specific provider's account in a container. A test harness has to be an
IMAP server we can run, throw away, and run again. If collection is written
against one provider's quirks rather than against IMAP, that harness proves
nothing.

**It is not appropriate for a public example.** This repo is a case study meant
to be shared. Naming the owner's mail provider says something about the owner
rather than about the design, and it makes a general pipeline read as a
single-provider tool. The same argument as
[ADR 0007](0007-rules-in-a-database.md), applied to a different kind of detail:
the interesting part is the mechanism, not whose account it runs against.

## Decision

Collection speaks IMAP and nothing else. No provider is named anywhere in this
repository.

The upstream account that collection empties is **the postbox** — the term is in
the [glossary](../glossary.md) alongside the rest of the vocabulary. Anything a
particular provider needs in order to expose IMAP — a local bridge process,
an app password, a non-standard port — is deployment configuration, not
architecture, and it lives on the mini PC with the credentials.

Applies to the other decisions too: ADRs 0001, 0002, 0003, 0004 and 0008 had the
provider's name replaced when they were written, and each says so. Their
reasoning is unchanged and none of the decisions moved — this ADR is the record
that the edit happened, so the change of direction is visible rather than
silently tidied away.

## Consequences

- **A real test harness becomes possible**: a throwaway IMAP server in a
  container, with fixture mail, run locally and in CI. Collection and the
  write-before-clear ordering can then be tested for real, which is the one part
  of this project where a bug loses something. This is the biggest gain and it is
  the reason to do it now rather than at publication time.
- The pipeline stays honest about what it depends on. Anything that turns out not
  to work over plain IMAP is a finding to record, not a quirk to code around.
- Switching providers, or collecting from a second postbox, stops being a rewrite.
  Not a goal, but it falls out for free.
- The provider-specific risk noted in the v1 design — a bridge that is
  GUI-oriented and awkward to run headless — does not disappear. It moves from
  being an architectural concern to being a deployment note on the mini PC, where
  it belongs.
- A reader of this repo cannot tell which provider it runs against. That is the
  point, and it does cost something: the concrete detail that made
  [ADR 0004](0004-sieve-ruled-out.md) vivid is now stated more abstractly.

## Alternatives considered

- **Leave it, and scrub before publishing.** Cheapest now, and it is the option
  that quietly never happens — the scrub competes with whatever else is urgent
  the week the repo goes public, and by then the name is in a year of commits.
  Doing it now also unlocks the test harness, which is worth having regardless of
  whether this is ever published.
- **Keep the provider named in the ADRs as history, and generalise only the
  forward-looking docs.** Faithful to the usual rule that an ADR is a record and
  not a living document, and the option that was seriously weighed. Rejected
  because the ADRs are the part of this repo most likely to be read by someone
  else, so leaving the name there defeats the purpose while making the repo
  inconsistent with itself. Recording the edit in this ADR keeps the history
  honest without keeping the name.
- **An abstraction layer over several mail backends.** Not this. Being
  IMAP-agnostic means writing to the protocol, not building a plugin system for
  providers nobody has asked for.

## Note on history

The version of this decision written before the rebuild ended with an open
question: the provider's name and one real address pattern were in that
repository's git history, where editing files cannot reach them, and the choice
between accepting that history and rewriting it was left to whoever pressed the
button.

It was answered by rebuilding. This repository's history begins at a clean graft,
so there is nothing here to rewrite — which is the expensive way to learn that
the control belongs at the crossing into a file, not at review. That lesson is
now a published requirement of the foundation rather than a paragraph in an ADR.
