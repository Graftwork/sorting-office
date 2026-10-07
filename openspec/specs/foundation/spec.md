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

### Requirement: Coding Session Links Are Not Disclosed

A commit, pull request, or issue authored with an AI coding agent SHALL name
the coding agent and the model, per *AI Authorship Is Disclosed*, but the text
the agent writes for it SHALL NOT include a link to the private coding session
or conversation that produced it. The agent and the model are the reviewer's
business; which specific conversation produced a change is not — a session
link identifies more than either: an account, sometimes a device, always a
private exchange nobody but its participants agreed to publish.

This governs what the agent writes and what a commit message contains. It does
not reach a link that the platform's own tooling appends to a pull request or
issue body after the agent has written it: no repository instruction can stop
that, so it is removed by editing the body once it is posted.

#### Scenario: A pull request or issue contains no session link

- **WHEN** a coding agent writes the body of a pull request or issue, or a
  comment on one
- **THEN** the text it writes names the coding agent and model but contains no
  link to the session or conversation that produced it

#### Scenario: A commit message containing a coding-session link is refused

- **WHEN** a commit message contains a link to a coding session or
  conversation
- **THEN** the commit is refused and the offending line is reported

### Requirement: A Passing Review Check Means A Review Happened

The automated review check on a pull request SHALL pass only when the review
was actually posted, and SHALL otherwise fail with a reason that names the
cause. A check that reports success while nothing was reviewed is worse than
no check: a reader takes the green tick as a statement that someone looked.

"The review bot" is the account the automated review posts as. Only comments
and reviews it posted since the run started count. A comment by anyone else —
a person, or another workflow's account — cannot make a run that reviewed
nothing look reviewed.

The check SHALL fail when the review bot posted nothing, when the run reports
an error, and when the pull request changes the review workflow itself (the
review skips itself then, so nothing was reviewed). A denied tool call SHALL be
reported but SHALL NOT, by itself, fail the check: exploratory calls are denied
on most runs and differ between them, and a denial that stops the review from
posting already fails the check because nothing was posted.

When the review has nothing to review it says so in a short note, and that note
SHALL be accepted only for a pull request whose changed files are all
Markdown, judged from the list of changed files and never from the note's
wording.

This governs the outcome of the check. It does not govern the quality of the
review, nor whether the review follows its instructions; those are behaviours
of a model and are checked on real runs.

#### Scenario: A review that was posted passes the check

- **WHEN** the review bot has posted a comment or review since the run started
  and the run reports no error
- **THEN** the check passes

#### Scenario: A run that posted nothing fails the check

- **WHEN** the review bot has posted no comment or review since the run started
- **THEN** the check fails, says that nothing was reviewed, and lists any tool
  calls that were denied

#### Scenario: A run that reports an error fails the check

- **WHEN** the run reports an error, whatever the review bot posted
- **THEN** the check fails and says that the run reported an error

#### Scenario: A pull request that edits the review workflow fails the check

- **WHEN** the pull request changes the workflow that runs the review
- **THEN** the check fails and says that the review skipped itself and the
  change must be read by a person

#### Scenario: A denied tool call only warns

- **WHEN** the review bot posted, and one or more tool calls were denied,
  whatever the tool and whatever the denied command's text
- **THEN** the check passes and the denied calls are reported

#### Scenario: A declined review passes only for a Markdown-only pull request

- **WHEN** the review bot's only output is a note that there was nothing to
  review
- **THEN** the check passes if every changed file in the pull request is
  Markdown, and fails if any changed file is not

#### Scenario: Comments by anyone but the review bot do not count

- **WHEN** the only comments on the pull request since the run started are by
  accounts other than the review bot
- **THEN** the check fails as if nothing had been posted
