## ADDED Requirements

### Requirement: The Counter shows what a run would do

Trust has to be earned before the pipeline is allowed to delete mail unattended.
The Counter SHALL show the outcome of a dry run — what would be collected, what
would be pruned, and why.

#### Scenario: A dry run's outcome can be reviewed

- **WHEN** a duty has run in dry run
- **THEN** the Counter shows the messages it would have collected and pruned

#### Scenario: Each decision shows its reason

- **WHEN** a message is listed as one that would be pruned
- **THEN** the walk and the retention behaviour that decided it are shown

### Requirement: Walk rules can be managed from the Counter

Rules change as new sites are signed up to. The Counter SHALL allow walks and
their address rules to be created, edited, and removed without editing files by
hand.

#### Scenario: A walk rule is added

- **WHEN** a new address rule is added to a walk
- **THEN** later mail to that address is assigned to that walk

#### Scenario: A walk's retention behaviour is changed

- **WHEN** a walk's retention behaviour is changed
- **THEN** the next reconciliation applies the new behaviour

#### Scenario: A rule that would break classification is refused

- **WHEN** a rule is saved that conflicts with an existing rule for the same address
- **THEN** it is refused with an explanation

### Requirement: The Dead Letter Office is triaged from the Counter

Batch triage is the point of the queue, so it SHALL be possible to work through
several waiting addresses in one sitting.

#### Scenario: A waiting address is assigned a walk

- **WHEN** an address in the Dead Letter Office is given a walk at the Counter
- **THEN** that address is triaged and leaves the queue

#### Scenario: The queue shows what is waiting

- **WHEN** the Dead Letter Office is opened at the Counter
- **THEN** the untriaged addresses and their waiting message counts are listed

### Requirement: The Counter is reachable only from the tailnet

The Counter is an interface onto unencrypted mail. It SHALL NOT be exposed to
the public internet.

#### Scenario: The Counter is not served publicly

- **WHEN** the Counter is running
- **THEN** it is reachable only over the private network
