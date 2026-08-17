# walks

## Purpose

A walk is a named set of addresses handled together — a postman's delivery round.
This capability decides which walk a message belongs on, using the address it was
delivered to, and says what happens when the address has never been seen before.

The mail domain is a catch-all, so every site gets its own alias and the alias is
the classification signal. New aliases therefore appear the moment one is typed
into a signup form, with nothing to intercept, which is why an unrecognised
address has to be an ordinary outcome rather than an error.

Synced from the `sweeper-and-retention` change ahead of the rest of it: this
capability decides from message metadata alone, so it is finished and tested
while the infrastructure it will eventually run on does not exist yet.

## Requirements

### Requirement: A message is assigned to a walk by the address it was sent to

The domain is a catch-all, so the recipient alias identifies the site that sent
the mail. The system SHALL assign each collected message to exactly one walk
based on the address it was delivered to.

#### Scenario: A known address puts a message on its walk

- **WHEN** a message arrives addressed to an alias with a walk rule
- **THEN** the message is assigned to that walk

#### Scenario: A message is assigned exactly one walk

- **WHEN** a message is assigned to a walk
- **THEN** it belongs to that walk and no other

### Requirement: An unrecognised address is held, never pruned

New addresses appear the moment they are typed into a signup form, with nothing
to intercept. An address with no rule SHALL NOT block collection and SHALL NOT
cause an error; the message SHALL be kept indefinitely until a person decides
otherwise.

#### Scenario: An unknown address does not stop the run

- **WHEN** a message arrives addressed to an alias with no walk rule
- **THEN** the message is collected as normal
- **AND** the duty completes without error

#### Scenario: An unknown address is never pruned by default

- **WHEN** a message is on no walk
- **THEN** no retention behaviour deletes it

#### Scenario: An unknown address is raised for triage

- **WHEN** a message arrives addressed to an alias with no walk rule
- **THEN** the message is put on no walk
- **AND** its address is raised for triage

Recording and queueing the address is the Dead Letter Office's own promise; this
scenario covers only the classification raising it.

### Requirement: Walk rules are matched predictably

Two rules could match the same address. The system SHALL resolve this the same
way every time, and SHALL prefer the more specific rule.

#### Scenario: The most specific matching rule wins

- **WHEN** an address matches both an exact rule and a pattern rule
- **THEN** the exact rule is applied

#### Scenario: Matching an address is case-insensitive

- **WHEN** an address differs from its rule only by letter case
- **THEN** the rule still matches

### Requirement: Reassigning a walk corrects a miss-sort

A message can be classified wrongly. Moving it to a different walk SHALL apply
that walk's retention behaviour from then on.

#### Scenario: A miss-sorted message is moved to the right walk

- **WHEN** a message is reassigned to a different walk
- **THEN** the new walk's retention behaviour governs it
