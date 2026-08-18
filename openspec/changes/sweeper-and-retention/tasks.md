Ordered so that each irreversible capability is only reachable after the one
before it has been proven. Nothing deletes mail until section 5 — and after
[ADR 0008](../../../docs/decisions/0008-pruning-moves-to-trash.md), retention
never deletes at all.

Every scenario in `specs/` needs a claiming test before this change is synced to
the main specs — see `CLAUDE.md`.

## 0. Decision logic, buildable without any infrastructure

Both of these decide from message metadata alone, so they can be built and
tested with no mailbox, no mail account and no mini PC.

- [x] 0.1 Assign a message to a walk by recipient address, case-insensitively
- [x] 0.2 Resolve overlapping rules by preferring the most specific
- [x] 0.3 The four retention behaviours as pure decisions over message metadata
- [x] 0.4 Reconciliation returns a plan and changes nothing
- [x] 0.5 Tests claiming the scenarios in `specs/walks/` and `specs/retention/`
- [x] 0.6 Sync those two capabilities into `openspec/specs/`, ahead of the rest

## 1. Infrastructure on the mini PC

- [ ] 1.1 Run whatever the postbox needs for IMAP headless as a systemd service; confirm it survives a reboot
- [ ] 1.2 Stand up Dovecot locally, IMAP only — no SMTP receiving, no MX, no internet exposure
- [ ] 1.3 Confirm both are reachable over the tailnet and not from anywhere else
- [ ] 1.4 Stand up n8n in Docker and confirm it can reach both mailboxes
- [ ] 1.5 Write down how to rebuild all of the above, so the mini PC is not a single point of knowledge

## 1a. A test harness for collection

Collection speaks plain IMAP and names no provider
([ADR 0009](../../../docs/decisions/0009-provider-agnostic-collection.md)), which
makes this possible. It comes before collection is built, not after: this is the
part of the pipeline that can lose mail.

- [ ] 1a.1 Run a throwaway IMAP server in a container, for tests and local runs
- [ ] 1a.2 Fixture mail to seed it with — invented addresses only
- [ ] 1a.3 Point collection at it by configuration alone, with nothing provider-specific in the code
- [ ] 1a.4 Run it in CI, so the relay-before-clear ordering is exercised on every change
- [ ] 1a.5 Decide what the harness cannot prove, and write that down rather than assuming it is covered

## 2. Collection, reporting only

- [ ] 2.1 Connect to the swept folders in the postbox and list what is there
- [ ] 2.2 Assert only the configured folders are ever read
- [ ] 2.3 Add dry run, defaulting on when no setting is given
- [ ] 2.4 Report what a duty would relay and clear, changing nothing
- [ ] 2.5 Tests claiming the dry-run and folder-scope scenarios in `specs/collection/`

## 3. Collection, relaying without clearing

- [ ] 3.1 Write messages into the local mailbox via IMAP APPEND
- [ ] 3.2 Record the postmark at acceptance, ignoring sender-supplied dates
- [ ] 3.3 Key on message identity so a repeated duty cannot store a second copy
- [ ] 3.4 Leave the message in the postbox when a write fails, and report it
- [ ] 3.5 Tests claiming the postmark and repeat-safety scenarios in `specs/collection/`
- [ ] 3.6 Run against real mail and confirm the local mailbox matches the postbox

## 4. Walks and the Dead Letter Office

Rule matching itself is done in section 0; what is left is where the rules live
and the Dead Letter Office around them.

- [x] 4.1 Decide where walk rules live — a database beside the mailbox
      ([ADR 0007](../../../docs/decisions/0007-rules-in-a-database.md))
- [ ] 4.2 Schema and migrations for walk rules and Dead Letter Office entries
- [ ] 4.3 Load rules from the store and feed them to the matcher
- [ ] 4.4 Record unrecognised addresses in the Dead Letter Office, once per address
- [ ] 4.5 Let an unknown address complete a duty without error and without pruning
- [ ] 4.6 Apply a triage decision to mail already collected for that address
- [ ] 4.7 Tests claiming the scenarios in `specs/dead-letter-office/`

## 5. Clearing from the postbox

- [ ] 5.1 Clear a message from the postbox only after its write is confirmed
- [ ] 5.2 Prove an interrupted duty clears nothing unconfirmed
- [ ] 5.3 Tests claiming the relay-before-clear scenarios in `specs/collection/`
- [ ] 5.4 Enable clearing on the live duty, after 3.6 has been reviewed

## 6. Retention against the real mailbox

The behaviours are built in section 0. What is left is reading real state in and
carrying a plan out.

- [ ] 6.1 Read messages and their `\Seen` flags back from the local mailbox
- [ ] 6.2 Read each walk's behaviour and settings from the rule store
- [ ] 6.3 Create the Trash folder if it does not exist, and carry a plan out by
      moving messages into it
- [ ] 6.4 Confirm a message moved to Trash is still readable from a normal client
- [ ] 6.5 Report what would be pruned, and why, at the Counter

## 7. The Counter

- [ ] 7.1 Show the outcome of a dry run — what would be collected and pruned
- [ ] 7.2 Show the walk and behaviour that decided each pruning
- [ ] 7.3 Create, edit and remove walks and their address rules
- [ ] 7.4 Refuse a rule that conflicts with an existing one, with an explanation
- [ ] 7.5 Triage the Dead Letter Office in a batch
- [ ] 7.6 Serve on the tailnet only
- [ ] 7.7 Tests claiming the scenarios in `specs/the-counter/`

## 8. Letting it prune

- [ ] 8.1 Review dry-run reports at the Counter until they are unsurprising
- [ ] 8.2 Let retention carry its plans out
- [ ] 8.3 Schedule the duty and watch the first unattended runs
- [ ] 8.4 Decide when Trash is emptied, and by what — see Open Questions in `design.md`

## 9. Closing the change

- [ ] 9.1 Confirm every scenario has a claiming test and `mise run trace` passes
- [ ] 9.2 Sync the remaining delta specs into `openspec/specs/`
- [ ] 9.3 Record what was learned, including anything that went differently to this plan
- [ ] 9.4 Archive the change
