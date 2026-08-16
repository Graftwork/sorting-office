# foundation

## Purpose

The guarantees Graftwork Stock makes to a project grafted from it. These are the
promises of the foundation itself, not of any project built on top — a stamped
project keeps this spec, adds its own capabilities alongside it, and can check at
any time that the foundation still holds.
## Requirements
### Requirement: Green From Commit One

A freshly stamped project SHALL pass its checks with no edits, so the first real
commit is the idea rather than the plumbing.

#### Scenario: A freshly stamped project passes its test suite

- **WHEN** a project is stamped from Stock and its test suite is run
- **THEN** the suite passes without any source edits

### Requirement: Spec Traceability

Every scenario written in a spec SHALL be claimed by at least one test, and every
claim a test makes SHALL name a scenario that exists. This is the contract
between the plain-English review layer and the code layer: a scenario nobody
tests is a promise nobody keeps, and a test claiming a scenario that does not
exist is a link that has quietly rotted.

#### Scenario: Every scenario is claimed by a test

- **WHEN** the traceability guard runs against the specs and the tests
- **THEN** it reports no unclaimed scenarios

#### Scenario: An unclaimed scenario is reported

- **WHEN** a spec contains a scenario that no test claims
- **THEN** the guard names that scenario and fails

#### Scenario: A claim naming an unknown scenario is reported

- **WHEN** a test claims a scenario id that appears in no spec
- **THEN** the guard names that claim and fails

### Requirement: Declared Gaps

Some promises cannot be kept by a test — a review policy, or a promise about
something the suite cannot observe. Such a scenario SHALL be declared with a
written reason rather than quietly tolerated, and the declaration itself SHALL
be checked, so that "we cannot test this" is a statement someone made on the
record and not a hole that opened on its own.

#### Scenario: A declared gap is not reported as unclaimed

- **WHEN** a scenario no test claims is declared with a written reason
- **THEN** the guard accepts it and reports it as allowed rather than missing

#### Scenario: A declared gap with no reason is reported

- **WHEN** a scenario is declared as untestable but no reason is written down
- **THEN** the guard rejects the declaration and fails

#### Scenario: A declared gap naming an unknown scenario is reported

- **WHEN** a declaration names a scenario id that appears in no spec
- **THEN** the guard names that declaration and fails

#### Scenario: A declared gap that a test now claims is reported

- **WHEN** a scenario is declared as untestable and a test also claims it
- **THEN** the guard names the stale declaration and fails

### Requirement: AI Authorship Is Disclosed

A pull request carrying AI-generated code SHALL name the coding agent and the
model that wrote it. Grafted projects are built this way by design, and a
reviewer reading a diff is owed the same context as the person who prompted it.

#### Scenario: A pull request carrying AI-generated code names the agent and model

- **WHEN** a pull request containing AI-generated code is opened for review
- **THEN** its description names the coding agent and the model used

### Requirement: Context Is Not Content

Detail a person supplies so that the agent understands a problem SHALL NOT be
copied into an artifact merely because it was supplied. Requirements SHALL be
written as categories and rules rather than as people and instances, and where a
specific is genuinely load-bearing it SHALL be confirmed before it is written
down.

The window is the moment a detail crosses from conversation into a file that will
be committed. After that it is in history, and history is not edited but
rewritten — so this is a promise that must be kept before the commit, not audited
after it.

#### Scenario: Personal detail supplied as context stays out of the artifacts

- **WHEN** someone supplies personal or identifying detail while explaining what
  they need
- **THEN** the artifacts state the requirement in general terms, and the detail
  appears in none of them

#### Scenario: A load-bearing specific is confirmed before it is written down

- **WHEN** a specific detail genuinely has to appear in an artifact for the
  requirement to mean anything
- **THEN** it is named as a specific and confirmed with the person who supplied
  it before it is committed

#### Scenario: A commit carrying a credential is refused

- **WHEN** a change staged for commit contains a credential or other
  high-entropy secret
- **THEN** the commit is refused and the location of the secret is reported
