# ADR 0016: Going public: what was done, and the ruleset's shape

- **Status:** accepted
- **Date:** 2026-10-15

## Context

[ADR 0014](0014-going-public-checklist-adopted.md) adopted
[`docs/GOING_PUBLIC.md`](../GOING_PUBLIC.md), ran items 1–4, and left items 5–7
open for the owner. [ADR 0015](0015-rebuilt-from-rewritten-history.md) rebuilt
the repository from rewritten history. This ADR closes the checklist and
records the choices in the branch ruleset, which a future reader could
otherwise mistake for drift.

## Decision

**Items 1–4 were re-run on the rebuilt tree** (license and copyright, a full
history secret scan, the cross-repo link check, the wording sweep) and came
back as ADR 0014 recorded them. The history scan covered
`git log --all -p --diff-merges=cc` and found no credential-pattern hits, and
`detect-secrets scan --all-files` found nothing.

**Item 5, the whole-repository read as a stranger,** was done by an agent and
accepted by the owner. It found no personal detail. It found things that read
wrong to a visitor, fixed in the pull request that follows ADR 0015: a UAT case
cited by the wrong number, a stub and an example inherited from Stock that did
not belong here, and a changelog with repeated headings.

One choice came out of it. **Infrastructure the project merely runs on is
described by its role, not its product name** ("the private network", "a cloud
VM"). The components the project chose and weighed keep their names (Dovecot,
n8n). The upstream mail provider stays unnamed
([ADR 0009](0009-provider-agnostic-collection.md)) even though the constraints
it imposes are described in full: the point is discretion about what a name
implies, not secrecy about the design.

**Items 6 and 7** were done by the owner: the repository was made public, then
a ruleset named `sorting-office main` was created on the default branch. It
needed the repository to be public first (the checklist's own reasoning in
item 7). Its shape is deliberate:

- **No deletion and no force push** of the default branch.
- **A pull request is required, with squash as the only merge method.** Zero
  approvals are required, because there is one maintainer and the check on a
  change is the maker/checker split, not a second account.
- **Three checks are required:** `check`, `Session link - commits` and
  `Session link - description`. These are job names, not workflow names.
- **`review` is not required.** The Claude review workflow describes itself as
  advisory, and a required review would block every draft pull request (the job
  is skipped for drafts) and every pull request that edits the workflow itself
  (the gate fails for those by design).
- **No bypass.** The owner is bound by the same rules as everyone else. An
  emergency change still goes through a pull request with green required
  checks. If that proves too strict, adding the owner as a bypass actor is the
  change to make, and it should be recorded here.

## Consequences

- **Enforcement was seen, not assumed.** A throwaway pull request carrying a
  session link in its commit message, committed with `--no-verify`, showed
  `mergeable_state: "blocked"` while `Session link - commits` was red, and its
  merge box offered the owner no bypass.
- **The ruleset is readable without authentication once the repository is
  public:** `GET /repos/Graftwork/sorting-office/rulesets` and
  `/rules/branches/main` return it. `docs/GOING_PUBLIC.md` says an agent session
  cannot check any of this. That holds for a private repository and for
  changing the settings; reading them afterwards works.
- **The coverage upload was confirmed from the job log** once a
  `CODECOV_TOKEN` secret existed: `Token length: 36` and
  `Upload queued for processing complete`, not merely a green step. The step
  continues on error, so a green step alone proves nothing.
- **Pull request descriptions kept the session link in their edit history.**
  The GitHub tool used by cloud coding sessions appends a link to a new pull
  request's body after the agent has written it. Editing it out leaves the
  original in the description's revision history, which is public once the
  repository is. The owner deleted those revisions by hand on the first four
  pull requests. The `Session link - description` workflow cannot prevent this:
  it cleans the body but cannot reach the history. Pull requests are therefore
  opened by the owner from the compare page.
- **The Codecov badge in the README** shows its state only once Codecov has
  processed an upload for a public repository.

## Alternatives considered

- **Require `review` as a fourth check.** Rejected for the two cases above.
  Revisit if the review becomes dependable on every kind of pull request.
- **Add the owner as a bypass actor.** Rejected for now: the rules are meant to
  bind everyone, and nothing has needed an exception.
- **Require an approving review.** Rejected: with one maintainer it would need
  a second account whose only job is to click approve.

Numbers above came from real output: `GET /rulesets/24747810` and
`/rules/branches/main` for the ruleset, the job log of the first `check` run on
`main` after the secret existed for the coverage upload, and the throwaway pull
request's merge state. That the owner could not bypass is the owner's report
from the merge box, not something measured here.
