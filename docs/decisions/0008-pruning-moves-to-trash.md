# ADR 0008: Pruning moves a message to Trash, it never deletes

- **Status:** accepted
- **Date:** 2026-08-14
- **Carried forward:** written before this repository was rebuilt, and renumbered
  on the way in. The reasoning is unchanged.

## Context

Mail loss is the one failure in this project without a cheap undo, and retention
is the part that does the losing. Every guard so far has been about *hesitating*
before the irreversible step: dry run by default, write-before-delete ordering,
reviewing reports until they are boring.

Those guards all protect the moment of the delete. None of them help afterwards.
The case that exposed this is poste restante — keep until read. The question was
how soon a read message becomes fair game, and the options came down to "at the
next reconciliation" (clean rule, but opening something by accident in a mail
client is enough to lose it) or "after a grace period" (safer, but adds a knob
and makes "what is on this walk?" harder to answer).

That framing assumed pruning is destructive. It does not have to be. The local
mailbox is a real IMAP server ([ADR 0003](0003-real-local-mailbox.md)), and a
mail store already has the right idea about this: things go to Trash, and Trash
is emptied separately and deliberately.

## Decision

Retention prunes by **moving a message to a local Trash folder**. It never
deletes.

This applies to all four retention behaviours, not just poste restante. The
retention code has no way to express a delete at all — its plan can say *keep* or
*move to Trash*, and that is the whole vocabulary.

Emptying Trash is a separate concern with its own decision, not yet taken, and
deliberately not part of v1.

With this in place, poste restante takes the simple rule: read at the next
reconciliation makes it fair game. The grace period is not needed, because the
recovery it was buying is now structural.

## Consequences

- **An accidental open is recoverable**, as is a wrong walk rule, a wrong
  retention behaviour, and a bug in the reconciliation. The failure mode of
  nearly every retention mistake becomes "it is in Trash", which costs a drag
  back rather than a restore.
- Retention can be trusted to run for real much sooner. Dry-run review is still
  the plan, but the stakes of turning it off drop from irreversible to annoying.
- Disk grows until Trash is emptied. Accepted: text mail is small, the mini PC is
  not short of space, and this buys the safety margin that matters most while the
  rules are still being tuned.
- "Pruned" throughout the specs and the glossary now means *moved to Trash*.
  Anywhere that needs to mean genuinely gone has to say so explicitly.
- The retention layer no longer needs a dry-run flag of its own to be safe. It
  computes a plan and returns it; carrying the plan out is a separate step. Dry
  run stops being a setting to remember and becomes the only thing the logic can
  do by itself.
- There are now two Trashes in the story, doing the same job at different stages:
  the postbox's own Trash is the backstop for the sweeper clearing collected mail
  ([ADR 0002](0002-two-tier-sweeper.md)), and this one is the backstop for
  retention. Neither replaces the other.
- Trash will eventually need an emptying policy, or it becomes an archive that
  nobody trusts to be complete. That is a real follow-up, not a loose end to
  forget.

## Alternatives considered

- **Delete outright, with a grace period before a read message becomes
  eligible.** The alternative that prompted this. It buys a delay rather than an
  undo, needs a duration nobody can pick well, and does nothing for the other
  three behaviours or for a bug.
- **Delete outright and rely on backups.** Restoring one message from a mailbox
  backup is a chore, so in practice it would never be done — the mail is
  effectively gone.
- **Mark with the IMAP `\Deleted` flag and never expunge.** Standard, and the
  message stays in place. Rejected because most clients hide flagged messages,
  which makes recovery invisible exactly when it is needed; a Trash folder is
  somewhere a person can actually look.
