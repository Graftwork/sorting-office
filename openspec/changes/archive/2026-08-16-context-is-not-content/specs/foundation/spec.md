## ADDED Requirements

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
