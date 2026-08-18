# ADR 0003: A real local IMAP mailbox, not a bespoke store

- **Status:** accepted
- **Date:** 2026-08-12
- **Carried forward:** written before this repository was rebuilt, and renumbered
  on the way in. The reasoning is unchanged.

## Context

[ADR 0002](0002-two-tier-sweeper.md) puts a local mailbox between the sweeper and
everything else. That mailbox could be a real IMAP server, or it could be an
application-specific store — a database schema shaped around whatever the
pipeline happens to need.

The app-only store looks cheaper at first glance: no server to run, no protocol
to speak, exactly the fields we want.

## Decision

Run a real local mailbox — Dovecot, IMAP only.

Explicitly **not**: no SMTP receiving, no internet exposure, no MX records. It is
a mailbox that only ever gets written to by the sweeper, over the LAN.

## Consequences

- The cost difference is close to zero. The sweeper already speaks IMAP to read
  from the postbox, and `APPEND` is trivial. A bespoke store would mean *inventing* a
  schema rather than reusing one.
- Everything that reads mail already speaks IMAP. Any off-the-shelf client can
  point at the local mailbox — which makes inspection, debugging, and manual
  recovery possible without building anything.
- It is portable. If this project is abandoned, the mail is still in a standard
  format readable by anything. A bespoke schema would strand it.
- RFC 5322 is a far better-tested design than any schema invented in an afternoon,
  and messages arrive in that format anyway — storing them as anything else means
  a lossy conversion on the way in.
- The cost is a Dovecot instance to configure and keep patched. Modest, and it is
  a well-trodden path with abundant documentation.
- IMAP flags (`\Seen`, `\Deleted`) give the retention model somewhere natural to
  read state from, which the keep-until-read behaviour needs anyway.

## Alternatives considered

- **Application-specific database store.** Tempting for the tailored schema, but
  needs a bespoke design, strands the data, and rules out every existing tool.
- **Flat maildir on disk with no server.** Standard format, no daemon — but then
  every reader has to implement its own locking and state handling, which is
  what an IMAP server already does correctly.
