## ADDED Requirements

### Requirement: Unrecognised addresses collect in the Dead Letter Office

Triage must be something done in a batch when convenient, never a chore attached
to each signup. The system SHALL record every address it has no walk rule for,
and hold it until someone deals with it.

#### Scenario: A new address appears in the Dead Letter Office

- **WHEN** mail arrives addressed to an alias with no walk rule
- **THEN** that address is listed in the Dead Letter Office

#### Scenario: An address is listed once, however much mail it sends

- **WHEN** several messages arrive for the same unrecognised address
- **THEN** the Dead Letter Office lists that address once
- **AND** shows how many messages are waiting on it

#### Scenario: Waiting mail is visible for the decision

- **WHEN** an address in the Dead Letter Office is inspected
- **THEN** the messages received for it can be seen

### Requirement: Assigning a walk clears the address from the Dead Letter Office

Triage means deciding what a walk an address belongs to. Once decided, the
address SHALL stop being unrecognised, and the decision SHALL apply to the mail
already waiting.

#### Scenario: Triaging an address removes it from the queue

- **WHEN** an address in the Dead Letter Office is assigned a walk
- **THEN** it is no longer listed there

#### Scenario: Mail already waiting joins the assigned walk

- **WHEN** an address is assigned a walk
- **THEN** the messages already collected for it are put on that walk

#### Scenario: Later mail is classified without triage

- **WHEN** mail arrives for an address that has been triaged
- **THEN** it is assigned its walk without appearing in the Dead Letter Office

### Requirement: Nothing in the Dead Letter Office is pruned

An untriaged address has no retention behaviour, and guessing one could delete
something that mattered. Mail for an unrecognised address SHALL be kept until its
address is triaged.

#### Scenario: Untriaged mail survives reconciliation

- **WHEN** reconciliation runs while an address is still untriaged
- **THEN** the messages waiting for it are kept
