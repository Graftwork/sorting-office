# Going public

A repository stays private by default, which means going public is a deliberate
event, not a setting you flip on a whim. It is also close to irreversible: once
a repository is public, its entire history — including whatever was in it
before anyone thought to check — can be cloned, forked, and indexed by the
time a problem is noticed. Fix what needs fixing first.

This checklist is grafted from Stock ([Stock ADR 0015](decisions/stock-0015-going-public-checklist.md)),
assembled there from Stock's own real pre-publication review. Most items trace
directly to something that was actually missing or actually wrong there, not
anticipated in advance. One is a considered extension of an already-proven
practice rather than something that broke — see the ADR for exactly which is
which.

**This runs once**, immediately before a repository's visibility actually
changes — not on every change the way [`docs/UAT.md`](UAT.md)'s cases do, and
not part of [`docs/RELEASING.md`](RELEASING.md)'s per-version sequence. If a
project stays private for years and only later decides to go public, work this
list fresh at that point rather than trusting whatever was true when the
project was grafted.

## 1. License and copyright

- Confirm a `LICENSE` file exists and states a **deliberate** choice. Silence
  is not neutral — no `LICENSE` means default exclusive copyright, which
  blocks anyone else from legally using or forking what you are about to
  share.
- Confirm the copyright holder is an actual legal person or entity — not a
  project or repo name that is not itself a legal entity. See
  [ADR 0013](decisions/0013-apache-2-0-license-and-copyright.md) for the
  worked reasoning for this project.
- If the license uses a `NOTICE` file (Apache-2.0 and similar), check any
  cross-references inside it actually resolve. Stock's own `NOTICE` shipped
  with a dangling pointer to sections of two other files that didn't mention
  what it claimed — caught only when this project wrote its own `NOTICE` and
  declined to copy the mistake forward; worth re-checking here too now that
  this project's own `NOTICE` has had time to drift.
- Record the decision as an ADR. This is exactly the kind of deliberate
  choice a future reader might otherwise mistake for drift.

## 2. Full-history secret scan

A pre-commit secret scanner only guards commits made after it was installed.
Going public exposes everything before that too — worth checking even though
no leak has ever actually been found here; a scanner's clean track record
going forward says nothing about history it was never watching.

- Scan the **entire** history, not just the working tree:
  `git log --all -p --diff-merges=cc` (plain `-p` skips merge-commit diffs
  by default, so a secret introduced only during a merge's manual conflict
  resolution — and later removed — would produce no output at all; verified
  directly, not assumed), checked against common credential patterns (cloud
  provider keys, private key blocks, common API token shapes) — not just the
  scanner's own baseline.
- Also run the project's own scanner across the current tree
  (`detect-secrets scan --all-files` or equivalent) as a second, narrower
  pass, and confirm any hits are in gitignored/untracked paths, not tracked
  content.

## 3. Cross-repo reference check

Grep the whole repository for links to other repositories — sibling
projects, forks, related work referenced in ADRs, changelogs, or skills:

```bash
grep -rln "github.com/<your-org>/" --include='*.md' .
```

For every match, confirm the linked repository is **already public**, or will
go public in the same window. A link into a repository that stays private
becomes a dead link the moment this one goes public — a 404 or a login
prompt for anyone who clicks through, with no way for them to know why.
Stock's own review found exactly this: six references across `CHANGELOG.md`,
ADRs, and a skill file, all pointing at repositories that were still private
when Stock went public — this project's own README links into
`Graftwork/stock` itself, so that repository going public first (it has) is
what unblocks this check here.

## 4. Stale conditional wording sweep

Grep for words whose truth depends on the repository's current state:
`private`, `internal`, `confidential`, `not yet released`, `unreleased`.
Every hit needs a judgment call, not a reflexive edit:

- Is it still true?
- Was it ever actually the *real* reason for whatever it's justifying — or
  just a convenient-sounding one that happened to also be true at the time?
  Stock's own `docs/CONTRIBUTING.md` had exactly this problem: it attributed
  a workflow to the repository being private, when the actual cause (Claude
  Code session owner-scoping) had nothing to do with visibility at all.

## 5. A final, whole-repository stranger read

Every individual change already gets a "read as a stranger" pass — see
[`docs/UAT.md`](UAT.md) case 2. That happens per diff, though, not across the
whole repository at once. Before flipping visibility, do one more pass over
the repository **as it will actually appear** to a first-time visitor:
`README.md`, every doc, and anything in git history a stranger might
plausibly go looking at (author names, commit messages, anything that reads
as more personal than it needs to).

This is human-judgment work, the same shape as `docs/UAT.md`'s own cases: an
agent can read the repository and report what it saw, but it cannot be the
one to decide the repository is ready. Only a person can.

## 6. Flip visibility — once everything checkable beforehand is settled

Only once items 1–5 are done. The same principle as *Context Is Not Content*
applies here, just at the scale of a whole repository instead of one file:
the window closes at the moment of the flip, not at the moment someone
notices a problem, and there is no undo that reaches whatever was already
cloned, forked, or indexed in between.

This is not, in fact, the last step — see below. It only feels that way
because it's the irreversible one.

## 7. GitHub-side repository settings — now that the repo is public

**Branch protection specifically cannot happen before step 6, on most
plans.** Confirmed both directly (Stock's own private repository refused to
configure it) and against [GitHub's own documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets):
rulesets and branch protection rules are enforced on public repositories on
every plan, but on private repositories only from GitHub Team upward — Free
and Pro accounts can configure nothing on a private repo, full stop. If
you're on Team or Enterprise, this step doesn't have to wait for step 6; on
Free or Pro, it does, same as it did on Stock. So this step necessarily comes
*after* the flip on most accounts, not before it, however much tidier
"settle everything, then flip" would have been. None of it is checkable or
settable by an agent session either way, as of this writing — no tool access
to GitHub's branch-protection API. It's a manual pass, in Settings →
Branches (or the newer Rulesets UI, depending on what your account shows).

- **Require a pull request before merging** on the default branch. Turns
  "changes reach `main` by branch and PR, never a direct commit" from a
  written convention into something GitHub actually enforces.
- **Require the project's CI status check to pass** before merging. The name
  GitHub matches against is the **job name**, not the workflow name — this
  project's workflow is called `CI` (`.github/workflows/ci.yml`), but the job
  inside it is named `check`; searching for `CI` in the "Add checks" box
  won't match anything. Confirmed directly on Stock by inspecting a real PR's
  Checks tab, not assumed; this project's `ci.yml` is grafted from the same
  source and uses the identical job name, but verify against a real PR's
  Checks tab here too rather than trusting the match. A check also only
  becomes selectable once it has run at least once on the repo — not a
  concern here, since several PRs have already run it.
- **Disallow force pushes** to the default branch. This is the one that
  matters most — though precisely: a tag is an independent ref, and
  force-pushing the default branch cannot move, delete, or otherwise affect
  an existing tag, which keeps pointing at the exact same commit regardless.
  The real risk is different: a force-push (even an accidental one) can
  rewrite the default branch's history so a previously-tagged commit is no
  longer an *ancestor* of it, breaking `docs/RELEASING.md`'s "one continuous
  history" model even though the tag itself still resolves correctly. This
  project has cut no tags yet ([`docs/RELEASING.md`](RELEASING.md) — nothing
  has reached 0.1.0), so the immediate risk is lower than it was for Stock,
  but the setting costs nothing to turn on now rather than after the first
  tag exists.
- **Disallow deletion** of the default branch.
- Check whether CI secrets (`CODECOV_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN`) are
  scoped sensibly now that Actions run logs become publicly visible.
- Repo description and topics, if discoverability matters to you.
