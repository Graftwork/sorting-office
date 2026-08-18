# retention

## Purpose

How long a message is worth keeping, and what happens when it is not worth
keeping any more. Each walk carries one of four behaviours; this capability
applies them to the mail already held and reports what should go.

Two properties shape everything here. Retention **reconciles** rather than
deciding once at collection time, because read state changes afterwards and newer
messages arrive later. And retention **decides without acting**: it returns a
plan, and something else carries the plan out. Pruning means moving a message to
Trash — deleting is not an outcome this capability can express
([ADR 0008](../../../docs/decisions/0008-pruning-moves-to-trash.md)).

Synced from the `sweeper-and-retention` change ahead of the rest of it: the
behaviours decide from message metadata alone, so they are finished and tested
while the mailbox they will eventually read has not been built.

## Requirements

### Requirement: Pruning moves a message to Trash

Mail loss is the one failure without a cheap undo, so retention SHALL prune by
moving a message to a local Trash folder, and SHALL NOT delete. This applies to
every retention behaviour. See
[ADR 0008](../../../docs/decisions/0008-pruning-moves-to-trash.md).

#### Scenario: A pruned message is moved to Trash rather than deleted

- **WHEN** retention decides a message should be pruned
- **THEN** the message is moved to Trash
- **AND** it remains recoverable

#### Scenario: Retention cannot express a delete

- **WHEN** retention decides what to do with a message
- **THEN** the only outcomes available to it are keeping the message and moving
  it to Trash

### Requirement: A keep-recent walk keeps only the newest messages

For daily headlines and general marketing, only the most recent mail is worth
having. A keep-recent walk SHALL keep the configured number of newest messages —
one unless the walk says otherwise — and prune the rest by arrival order,
whether or not they have been read.

#### Scenario: A new arrival supersedes the previous one

- **WHEN** a message arrives on a keep-recent walk that already holds one
- **THEN** the older message is pruned
- **AND** the newest is kept

#### Scenario: The only message on the walk is kept

- **WHEN** a keep-recent walk holds exactly one message
- **THEN** that message is kept

#### Scenario: An unread message is superseded like any other

- **WHEN** a message on a keep-recent walk is superseded by a newer arrival
- **THEN** it is pruned whether or not it has been read

#### Scenario: A walk can keep more than one

- **WHEN** a keep-recent walk is configured to keep several messages
- **THEN** that many of the newest are kept
- **AND** the rest are pruned

### Requirement: Poste restante keeps a message until it is read

Comics, reviews and commentary are worth keeping while unread and fair game once
opened. A message on a poste restante walk SHALL be kept while unread, and become
eligible for pruning at the next reconciliation once it has been read.

#### Scenario: An unread message is kept

- **WHEN** a message on a poste restante walk has not been read
- **THEN** it is kept, however old it is

#### Scenario: A read message becomes eligible for pruning

- **WHEN** a message on a poste restante walk has been read
- **THEN** it becomes eligible for pruning

### Requirement: A timer walk prunes on age alone

Delivery notifications have a fixed short shelf life whether or not anyone opened
them. A message on a timer walk SHALL be pruned once it is older than the walk's
configured age, regardless of read state. The age is a property of the walk, and
SHALL default to seven days when the walk does not set one.

#### Scenario: A message older than the timer is pruned

- **WHEN** a message on a timer walk is older than the configured age
- **THEN** it is pruned

#### Scenario: An unread message is still pruned by the timer

- **WHEN** a message on a timer walk is older than the configured age and unread
- **THEN** it is pruned

#### Scenario: A message within the timer is kept

- **WHEN** a message on a timer walk is younger than the configured age
- **THEN** it is kept

#### Scenario: A timer walk with no age set uses seven days

- **WHEN** a timer walk does not configure an age
- **THEN** its messages are pruned once they are older than seven days

### Requirement: Keep-indefinitely is never pruned automatically

Purchase confirmations must survive. A message on a keep-indefinitely walk SHALL
NOT be pruned by any automatic behaviour.

#### Scenario: An old read message is still kept

- **WHEN** a message on a keep-indefinitely walk is old and has been read
- **THEN** it is kept

### Requirement: Retention reconciles against current state

Retention is not a decision made once at collection time. Read state changes
after the fact, and newer messages arrive later, so the system SHALL re-evaluate
messages already in the local mailbox against their current state.

#### Scenario: Reading a message later makes it eligible

- **WHEN** a message on a poste restante walk is read after it was collected
- **THEN** the next reconciliation finds it eligible for pruning

#### Scenario: Reconciliation is safe to repeat

- **WHEN** reconciliation runs twice with nothing changing in between
- **THEN** the second run prunes nothing further

### Requirement: Retention decides, it never acts

Retention SHALL return a plan of what it would keep and what it would move to
Trash, and SHALL change nothing itself. Carrying a plan out is a separate,
explicit step. Dry run is therefore not a setting anyone has to remember for
retention: deciding is all the logic can do on its own.

#### Scenario: Reconciliation reports without changing anything

- **WHEN** reconciliation runs
- **THEN** it reports the messages it would prune, and why
- **AND** nothing is moved or deleted

#### Scenario: Every decision carries its reason

- **WHEN** reconciliation decides the fate of a message
- **THEN** the walk and the retention behaviour behind the decision are reported
  with it
