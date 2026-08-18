## Why

Newsletter and marketing mail arrives faster than it gets cleaned up. Existing
filters already sort it into folders, but nothing prunes what lands there, so the
backlog grows every week. Some of it is genuinely wanted, so the answer is
retention rules per message, not a blanket delete.

This change builds the first end-to-end slice: get the mail out of the postbox
into a safe place, decide how long each message is worth keeping, and give a way
to review and correct those decisions before trusting it to run unattended.

## What Changes

- A **sweeper** relays the already-sorted folders in the postbox (Newsletters,
  Marketing) into a local IMAP mailbox and clears them from the postbox. It is
  the only component with postbox credentials, and it speaks plain IMAP
  ([ADR 0009](../../../docs/decisions/0009-provider-agnostic-collection.md)).
- Messages are assigned to a **walk** by recipient address — the catch-all alias
  the mail was sent to is the classification signal.
- Each walk carries one of four **retention behaviours**: keep-recent (the
  newest *n*, one by default), poste restante (keep-until-read), timer, or keep
  indefinitely.
- Addresses with no walk go to the **Dead Letter Office** and are held, never
  pruned, until triaged in batch.
- **The Counter**, an admin UI, exposes walk rules, the Dead Letter Office
  queue, and what a run would do.
- **Pruning moves a message to Trash**, it never deletes
  ([ADR 0008](../../../docs/decisions/0008-pruning-moves-to-trash.md)), so a
  wrong rule or an accidental open costs a drag back rather than a restore.
- **Dry-run is the default** for collection, which does act on the postbox. Retention
  cannot act at all on its own — it returns a plan, and carrying it out is a
  separate step.

Deliberately **not** in this change: message-level classification for
mixed-purpose sender addresses, tracker stripping, reader-mode reformatting, RSS
or chat sources, and any reading UI.

## Capabilities

### New Capabilities

- `collection`: the sweeper — relaying messages from the postbox into the local
  mailbox and clearing them, in an order that cannot lose mail.
- `walks`: assigning a message to a named walk by recipient address, and the
  conservative fallback when no rule matches.
- `retention`: the four retention behaviours, and the reconciliation that applies
  them to messages already in the local mailbox.
- `dead-letter-office`: holding unrecognised addresses safely and queueing them
  for batch triage.
- `the-counter`: the admin UI over walk rules, the Dead Letter Office, and
  dry-run output.

### Modified Capabilities

None. The `foundation` capability is unchanged.

## Impact

- **New infrastructure on the mini PC:** whatever the postbox needs in order to
  expose IMAP, running headless as a systemd service, and a local Dovecot
  instance (IMAP only — no SMTP receiving, no MX records, no internet exposure).
- **New dependency on n8n** (self-hosted, Docker) as the execution engine —
  marked proposed in [ADR 0005](../../../docs/decisions/0005-n8n-execution-engine.md)
  and to be confirmed by building the first collection duty on it.
- **Credentials:** postbox credentials live on the mini PC and are reachable only
  from the tailnet. Which provider they are for is deployment configuration and
  is not recorded in this repo.
- **A rule store on the mini PC**, holding walk rules and Dead Letter Office
  entries. Deliberately not in this repo: the rules name every site signed up to,
  and this repo is public
  ([ADR 0007](../../../docs/decisions/0007-rules-in-a-database.md)).
- **Irreversible operations:** clearing messages from the postbox is the one
  action with no cheap undo. The postbox's own Trash is the backstop, and dry-run
  plus strict write-before-delete ordering are the guards.
- No change to the grafted Stock foundation.
