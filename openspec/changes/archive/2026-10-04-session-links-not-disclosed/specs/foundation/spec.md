## ADDED Requirements

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
