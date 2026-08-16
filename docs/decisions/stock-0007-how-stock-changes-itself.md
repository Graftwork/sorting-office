# Stock ADR 0007: Stock runs its own change flow, for changes that touch promises

- **Status:** accepted
- **Date:** 2026-08-16

## Context

Stock ships an SDLC. It did not have one of its own.

Measured at v0.1.2: `main` was four commits, linear, with no merge commits; three
tags (`v0.1.0`, `v0.1.1`, `v0.1.2`); zero pull requests ever opened; and no
`openspec/changes/` directory at any point in the history. Every change to the
foundation had been a direct commit to `main`, tagged afterwards.

That left two things unresolved, and both had started to bite.

**The foundation did not practise what it ships.** v0.2.0 added two requirements
to `openspec/specs/foundation/spec.md` by editing the file directly — precisely
what `WORKFLOW.md` tells a grafted project never to do, since main specs are
supposed to be written by archiving a change. A reader who noticed the missing
`changes/` directory could not tell whether that was a deliberate exemption or an
oversight.

**A published requirement had nothing to attach to.** v0.2.0 also added *AI
Authorship Is Disclosed*, a promise about pull requests, to a repository that had
never had one. Not false, but hollow.

The obvious objection to fixing this is ceremony: a proposal, a design, and a
task list to bump a CI action major is absurd, and a process that feels absurd
gets skipped, which is worse than not having one.

## Decision

**Route by what the change touches**, not by size or by who is asking.

| Touches | Route |
| --- | --- |
| `openspec/specs/`, `scripts/`, `tests/` | Full OpenSpec change — propose, apply, UAT, archive |
| Docs, CI, toolchain, permissions | Direct commit on a branch |

The dividing line is whether the change alters a *promise*. The verification
layer is what Stock exists to provide, so changes to it go through the flow Stock
ships. Everything else does not.

**Everything reaches `main` by branch and pull request.** No direct commits to
`main`, regardless of route. The PR discloses the coding agent and the model,
which is what makes the *AI Authorship Is Disclosed* requirement real.

The sequence, the version rules, and the re-sync obligation are written out in
[`docs/RELEASING.md`](../RELEASING.md).

**The rule starts at v0.2.0 and is not applied backwards.** v0.2.0 edited the
foundation spec by hand because it is the change that introduced the rule.
Retrofitting an archived change for it would produce a record of deliberation
that never happened — a fabricated artifact is worse than an honest gap, and this
foundation asks agents to mark the provenance of everything else they assert.

## Consequences

- Stock's `openspec/archive/` becomes a real record of how the foundation
  evolved, which is also the worked example a grafted project learns from.
- A one-line CI fix stays a one-line CI fix. The route table is the thing that
  keeps the process from being skipped wholesale.
- The route table is a judgement call at the margin. "Does it alter a promise?"
  is the tiebreak, and the bias is toward the full route — an unnecessary
  proposal costs an hour, a silent spec edit costs the review layer's
  credibility.
- Branch-and-PR on a foundation repo that is often worked solo means reviewing
  one's own PR. That is still worth it: the PR is where the AI-authorship
  disclosure lives and where the diff becomes reviewable by whoever re-syncs a
  grafted project later.
- v0.2.0 sits on the wrong side of its own rule, permanently and on the record.

## Alternatives considered

- **Dogfood everything.** Maximum consistency, and the archive would be complete.
  Rejected because proposal-design-tasks for a typo fix is the kind of ceremony
  that gets abandoned in month two, taking the useful part with it.
- **Exempt Stock entirely, with an ADR saying so.** Simplest, and honest as far
  as it goes. Rejected because the foundation's credibility rests on the claim
  that this way of working is practical — and declining to use it on the one repo
  whose whole purpose is to demonstrate it is a poor argument for that claim.
- **Keep committing directly to `main`.** Fastest. Rejected because it would have
  required rewriting the *AI Authorship Is Disclosed* requirement to be about
  commit messages, weakening a promise to fit a habit.
