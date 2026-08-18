## ADDED Requirements

### Requirement: Collection speaks plain IMAP

The postbox is reached over IMAP and nothing else, so the sweeper SHALL NOT
depend on anything specific to a mail provider. Whatever a given provider needs
in order to expose IMAP is deployment configuration. See
[ADR 0009](../../../../docs/decisions/0009-provider-agnostic-collection.md).

#### Scenario: Any IMAP postbox can be swept

- **WHEN** the sweeper is pointed at a different IMAP account by configuration
- **THEN** it collects from it with no change to the code

#### Scenario: Collection can be exercised without a live account

- **WHEN** the sweeper is pointed at a throwaway IMAP server holding fixture mail
- **THEN** a collection duty runs against it end to end

### Requirement: The sweeper relays before it clears

Clearing a message from the postbox is the one irreversible act in the system.
The sweeper SHALL confirm the message is stored in the local mailbox before
removing it from the postbox, and SHALL NOT remove anything it has not confirmed.

#### Scenario: A message is stored before it is cleared

- **WHEN** the sweeper processes a message from a swept folder
- **THEN** the message is written to the local mailbox
- **AND** it is removed from the postbox only after that write is confirmed

#### Scenario: A failed write leaves the message in the postbox

- **WHEN** writing a message to the local mailbox fails
- **THEN** the message is left untouched in the postbox
- **AND** the failure is reported

#### Scenario: Losing the connection mid-run clears nothing unconfirmed

- **WHEN** the connection drops partway through a collection duty
- **THEN** every message already confirmed stored has been cleared
- **AND** no message that was not confirmed stored has been cleared

### Requirement: The sweeper only touches folders it was told to sweep

The sweeper SHALL read only from the configured already-sorted folders, and
SHALL NOT read from or modify any other folder.

#### Scenario: Mail outside the swept folders is untouched

- **WHEN** a collection duty runs
- **THEN** only the configured folders are read
- **AND** the inbox and all other folders are left unchanged

### Requirement: Collection is safe to repeat

A duty may be interrupted, retried, or run twice. The sweeper SHALL NOT store a
second copy of a message it has already collected.

#### Scenario: Re-running a duty does not duplicate messages

- **WHEN** a collection duty runs twice over the same messages
- **THEN** the local mailbox contains exactly one copy of each message

### Requirement: Every collected message carries a postmark

The sweeper SHALL record the time a message was accepted into the local mailbox,
so retention behaviours have a reliable clock that does not depend on headers
supplied by the sender.

#### Scenario: A collected message records when it was accepted

- **WHEN** a message is written to the local mailbox
- **THEN** the time it was accepted is recorded against it

#### Scenario: A misleading sender date does not become the postmark

- **WHEN** a message arrives with a sent date far in the past or the future
- **THEN** the postmark is the time it was accepted, not the sender's date

### Requirement: Dry run is the default

Nothing is deleted until dry run has been explicitly turned off. In dry run the
sweeper SHALL report every action it would take and SHALL change nothing.

#### Scenario: A dry run reports without deleting

- **WHEN** a collection duty runs in dry run
- **THEN** it reports the messages it would relay and clear
- **AND** nothing is written to the local mailbox or removed from the postbox

#### Scenario: Deleting requires dry run to be turned off deliberately

- **WHEN** the sweeper starts with no explicit dry-run setting
- **THEN** it runs in dry run
