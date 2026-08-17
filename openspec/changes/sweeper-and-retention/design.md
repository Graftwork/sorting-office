## Context

The architectural decisions are already recorded as ADRs and are not re-argued
here: [where it runs](../../../docs/decisions/0001-where-it-runs.md),
[the two-tier sweeper](../../../docs/decisions/0002-two-tier-sweeper.md),
[a real local mailbox](../../../docs/decisions/0003-real-local-mailbox.md),
[Sieve ruled out](../../../docs/decisions/0004-sieve-ruled-out.md),
[n8n](../../../docs/decisions/0005-n8n-execution-engine.md), and
[postal terminology](../../../docs/decisions/0006-postal-terminology.md).

This document covers what those leave open: how the pieces fit, where state
lives, and how to get from nothing to a pipeline that can be trusted to delete
mail unattended.

Current state is a grafted foundation with no pipeline code. Nothing is running
on the mini PC yet beyond pi-hole.

The binding constraint is that mail loss is the only failure without a cheap
undo. Everything below is shaped around making an irreversible delete hard to
reach by accident.

## Goals / Non-Goals

**Goals:**

- One end-to-end slice: postbox → local mailbox → retention → visible at the Counter.
- Trustworthy enough to run unattended, which means dry run first and a way to
  see what it would do.
- Bespoke logic testable outside n8n, so the traceability guard has tests to
  claim scenarios.
- Cope with a never-seen address without stopping or guessing.

**Non-Goals:**

- Message-level classification for mixed-purpose senders. Address-level rules
  with a conservative fallback are this change; the heuristic version comes later.
- Tracker stripping and reader-mode reformatting. A bad delete is obvious and
  recoverable from Trash; a bad content rewrite mangles silently.
- RSS and chat sources, and any reading UI.
- Facing (normalising to Markdown) beyond what retention needs. The pipeline
  shape leaves room for it; this change does not build it.

## Decisions

**State lives in the mailbox where it can, and beside it where it cannot.**
Read state is an IMAP flag (`\Seen`) — reading it back from the local mailbox is
what makes poste restante work, and it is already correct without us doing
anything. The postmark cannot live in a header we trust, because senders supply
those; it is recorded by us at acceptance. Walk rules and Dead Letter Office
entries are ours and live in a small store beside the mailbox.

*Alternative considered:* keeping all state in our own store, including read
state. Rejected — it would need syncing back from the mailbox, and would go
stale the moment a message is read in any normal client.

**Retention is a reconciliation, not a decision at collection time.** Read state
changes later and newer messages arrive later, so retention re-evaluates what is
already in the mailbox rather than stamping a verdict on arrival. This is what
the proposal means by a loop layered over a pipeline.

*Alternative considered:* computing an expiry at collection time. Simpler, and
cannot express keep-latest-only or keep-until-read at all.

**Idempotence by message identity.** Duties will be interrupted and retried.
Collection keys on the message's own identity so a re-run cannot store a second
copy, and reconciliation is safe to run twice.

**Dry run is the default, not a flag you remember.** Starting with no explicit
setting means dry run. Deleting requires deliberately turning it off. The failure
mode of forgetting is then "nothing happened", not "mail is gone".

**Walk rules and Dead Letter Office entries live in a database, not in the
repo.** This reverses the lean recorded in the original Open Questions below.
The rules are a list of every site the owner has signed up to, and this repo is
public, so committing them publishes that list.
[ADR 0007](../../../docs/decisions/0007-rules-in-a-database.md) has the full
reasoning and the near-miss alternative.

**Pruning moves a message to Trash rather than deleting it.**
[ADR 0008](../../../docs/decisions/0008-pruning-moves-to-trash.md). This changes
the shape of several things below: poste restante can take the simple rule
(read at the next reconciliation makes it fair game) because the recovery is
structural, and retention needs no dry-run flag of its own.

**Collection speaks plain IMAP and names no provider.** The upstream account is
*the postbox*; anything a particular provider needs in order to expose IMAP is
deployment configuration on the mini PC
([ADR 0009](../../../docs/decisions/0009-provider-agnostic-collection.md)). The
practical consequence for this change is a test harness: collection is the part
that can lose mail, and it can now be exercised against a throwaway IMAP server
with fixture mail, locally and in CI, instead of only against a live account.

**Retention computes a plan; carrying it out is a separate step.** A
reconciliation returns what it would keep and what it would move to Trash, and
changes nothing. Dry run therefore is not a setting that has to be remembered —
the logic has no way to act on its own. This is stronger than the "dry run is
the default" note above, and supersedes it for retention specifically;
collection still needs the setting, because collection does act.

**Keep-latest-only becomes keep-recent, with a count.** The behaviour keeps the
newest *n* messages on the walk, defaulting to one. Most newsletters are
all-or-nothing and take the default; some are not — a week of a daily is worth
holding onto and then dumping wholesale, read or not.

*Assumption worth flagging:* "a week's worth" is modelled as a count of
messages, not a duration, so a week of a daily paper is `keep: 7`. A rolling
count is predictable and needs no schedule, but it does mean a pause in
publishing stretches the window in calendar terms. If the intent turns out to be
calendar-based — everything older than Saturday goes, however many arrived — that
is a different behaviour and should be built as one rather than bolted onto this.

*Alternative considered:* never superseding an unread message. Rejected, because
a walk nobody reads then grows without limit, which is the original problem.
Superseding regardless of read state is safe now that superseded mail goes to
Trash.

**A timer walk's age is per-walk, defaulting to seven days.** Delivery
notifications and event reminders do not have the same shelf life, so the knob
will get used; a default means creating a walk does not require picking a number
up front.

**Bespoke logic sits behind a plain interface, not inside n8n nodes.** n8n
schedules and retries; classification and retention decisions are code that can
be called and tested directly. This keeps [ADR 0005](../../../docs/decisions/0005-n8n-execution-engine.md)
genuinely provisional — if n8n proves awkward, the logic moves without a rewrite.

## Risks / Trade-offs

- **A bug deletes wanted mail.** → Write-before-delete ordering, dry run by
  default, and the postbox's Trash as the backstop. Run in dry run against real
  mail until the reports are boring. Collection speaks plain IMAP, so it can also
  be exercised against a throwaway IMAP server before it ever sees real mail.
- **Reaching the postbox may need a headless bridge, which such tools are rarely
  designed for.** → Stand it up and confirm it survives a reboot *before*
  building anything on it. This is the most likely source of early friction, and
  it is now a deployment problem rather than an architectural one
  ([ADR 0009](../../../docs/decisions/0009-provider-agnostic-collection.md)).
- **The mini PC now holds unencrypted mail.** → Accepted consequence of
  [ADR 0002](../../../docs/decisions/0002-two-tier-sweeper.md). Tailnet-only
  access, no internet exposure, no SMTP, no MX.
- **Mixed-purpose addresses get the wrong retention.** → Known and deliberately
  deferred. The conservative fallback means the wrong answer is "kept too long",
  never "deleted too early".
- **The mini PC is a single point of failure.** → The failure mode is mail
  stops being pruned, which is the status quo, not data loss.
- **n8n's licence is fair-code, not OSI open source.** → Fine for personal
  self-hosted use; only bites if this were ever resold as a service.

## Migration Plan

There is nothing to migrate from — the risk is in the first live run, not in a
cutover. Sequenced so that each irreversible capability is only reachable after
the one before it has been proven:

1. Stand up whatever the postbox needs for IMAP, and local Dovecot, on the mini
   PC. Confirm both survive a reboot.
2. Build collection in dry run. Confirm it reports the right messages and writes
   nothing.
3. Turn on relaying, still without clearing. Mail now exists in both places —
   nothing has been lost and nothing deleted.
4. Confirm the local mailbox holds what the postbox holds, then enable clearing.
5. Build walks and retention against the local mailbox, in dry run.
6. Review dry-run reports at the Counter until they are unsurprising, then let
   retention prune.

Rollback at any step is stopping the duty. Up to step 4 nothing has been deleted
at all; after it, the postbox's Trash is the backstop.

## Open Questions

- Does n8n hold up for the collection duty, or does its IMAP handling get in the
  way? This is the question [ADR 0005](../../../docs/decisions/0005-n8n-execution-engine.md)
  is waiting on, and it can only be answered by building the first duty on it.
- When is Trash emptied, and by what? Deliberately unanswered —
  [ADR 0008](../../../docs/decisions/0008-pruning-moves-to-trash.md) leaves
  Trash growing on purpose while the rules are still being tuned. It needs an
  answer before it becomes an archive nobody trusts to be complete.

### Resolved

Kept rather than deleted, because where a question landed is often less
interesting than the fact that it moved.

- **Where do walk rules and Dead Letter Office entries live?** Leaned towards a
  file in the repo for git-reviewability; resolved the other way, to a database,
  once it was clear the rules are personal data and this repo is public.
  [ADR 0007](../../../docs/decisions/0007-rules-in-a-database.md).
- **How is "read" defined for keep-latest-only?** Arrival order alone, and the
  behaviour gained a count: keep the newest *n*, default one. See the Decisions
  above.
- **What is the timer walk's default age, per-walk or global?** Per-walk,
  defaulting to seven days.
- **How soon is a read poste restante message fair game?** At the next
  reconciliation — a question that dissolved once pruning became a move to Trash
  ([ADR 0008](../../../docs/decisions/0008-pruning-moves-to-trash.md)) rather
  than a delete, since the grace period was only ever buying recoverability.
