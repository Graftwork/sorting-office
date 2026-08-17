# ADR 0002: Only a small, low-privilege sweeper touches the postbox

- **Status:** accepted
- **Date:** 2026-08-12
- **Carried forward:** written before this repository was rebuilt, and renumbered
  on the way in. The reasoning is unchanged; the mail provider it originally
  named has been replaced by *the postbox*, per
  [ADR 0009](0009-provider-agnostic-collection.md).

## Context

This pipeline necessarily holds standing access to unencrypted email content —
that is what it is for. The blast radius of a bug, a bad dependency, or a
compromised component is therefore the primary design constraint, ahead of
elegance or convenience.

The naive shape is one process that connects to the postbox, classifies messages,
applies retention rules, and serves an admin UI. That means the component with
the most logic, the most dependencies, and the most attack surface is also the
one holding credentials to the primary mail account.

## Decision

Split into two tiers.

**Tier 1 — the sweeper.** Small, low-privilege, deliberately dumb. It knows only
which folders the mail client's existing filters already sort into (Newsletters,
Marketing). It relays their contents into the local mailbox and clears them from
the postbox. No classification, no retention logic, no UI.

**Tier 2 — everything else.** Classification, retention rules, the Dead Letter
Office, and the Counter all run against the **local** mailbox over plain IMAP.
No postbox credentials, no provider-specific access, no encryption complexity.

## Consequences

- The only code with postbox access is small enough to read in one sitting and
  changes rarely. The code that changes constantly has no path to the postbox at
  all.
- Tier 2 can be iterated on, restarted, and broken freely without risking the
  primary account.
- Tier 2 development and testing need no postbox connection — a local mailbox with
  sample messages is a complete test environment. This is a significant
  day-to-day benefit, not just a security one.
- The cost is a copy: mail exists in the local mailbox as well as the postbox, so
  the mini PC now holds unencrypted mail and needs to be treated accordingly.
- Deleting from the postbox after relaying is the step that can lose mail. It must
  be strictly ordered — confirmed write to the local mailbox *before* removal from
  the postbox — and must be exercised in dry-run mode first.

## Alternatives considered

- **One process doing everything.** Simpler to build, and puts maximum logic next
  to maximum privilege. Rejected on blast radius.
- **Classify in place on the postbox, never copy.** Avoids the duplicate, but
  means the complex logic holds postbox credentials, and makes every iteration a
  live experiment against real mail.
