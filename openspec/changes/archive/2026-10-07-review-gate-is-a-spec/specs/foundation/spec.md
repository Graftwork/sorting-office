## ADDED Requirements

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
