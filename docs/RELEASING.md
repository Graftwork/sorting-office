# Releasing

[`WORKFLOW.md`](../WORKFLOW.md) is how a change is *run*. This is how a change
gets *out*.

Grafted from Stock's own release process, with the specifics replaced. Stock
releases a foundation that other projects graft from, so its versions are
migration instructions for someone else. This project releases nothing to anyone
— which changes what a version number is *for*, and that is the first section.

## What a version means here

Nothing installs this project, so a version number here is not a package
coordinate. It is a **claim about how much of the promise actually works**, and
it exists so that "are we nearly there?" has an answer that isn't a feeling.

| Version | What is true when it is reached |
| --- | --- |
| **0.0.x** | Decisions recorded, foundation green. Nothing runs end to end. **Here today.** |
| **0.1.0** | One end-to-end run against a real postbox, in dry run, reporting what it *would* do. Nothing has been relayed or cleared. |
| **0.2.0** | Collection relays into the local mailbox and clears the postbox, unattended, with the relay-before-clear ordering proven. |
| **0.3.0** | Retention carries its plans out — mail moves to Trash on a schedule, and the reports at the Counter are unsurprising. |
| **1.0.0** | It has run unattended for a sustained stretch — a month is the working figure — without a surprise, and mail is being pruned without anyone watching it. |

Two things follow from that table:

- **1.0.0 is a long way off, and saying so is the point.** Naming a change "v1"
  before any of it runs claims a maturity that does not exist, and the claim
  outlives the enthusiasm that produced it. Changes are named for what they do.
- **The milestones are about trust, not features.** Every step from 0.1.0 onward
  is "something irreversible became reachable, and was proven first". That is the
  same ordering the task list uses, for the same reason.

Within 0.0.x, patch bumps are not worth the ceremony. The CHANGELOG's
`[Unreleased]` section carries everything until the first milestone is genuinely
reached.

## Which route a change takes

Not every change earns the full ceremony. The test is what it touches.

| The change touches | Route |
| --- | --- |
| `openspec/specs/`, `scripts/`, or `sorting_office/` and its tests | **Full OpenSpec change** — propose, apply, UAT, archive. Main specs are written by archiving, never by hand. |
| Docs, ADRs, CI, `mise.toml`, `.pre-commit-config.yaml`, permissions | **Direct** — branch, commit, PR. The CHANGELOG entry is the record. |

If you are unsure, ask whether the change alters a promise. Promises go through
OpenSpec.

## The sequence

### 1. Branch

```bash
git fetch origin main && git checkout -b <topic> origin/main
```

Never commit to `main` directly. The single exception is the root commit — the
pristine graft — which had no branch to come from.

### 2. Run the change

Per the route table above. If it is a full OpenSpec change, the specs are updated
by `/opsx:archive`, not by editing `openspec/specs/` yourself.

### 3. Get it green

```bash
mise run check          # lint + test, everything CI runs
uvx pre-commit run --all-files
```

### 4. Run UAT — case 4 before the *commit*, the rest before the PR

Work [`docs/UAT.md`](UAT.md) and record what you saw. Case 4 — *the artifacts
read clean to a stranger* — is different from the others: it runs before the
commit, because that is the crossing that matters. Everything after the commit is
a rewrite rather than an edit.

An agent may run the commands and write `Last agent run`. Only a person writes
`Last passed`.

### 5. Write the CHANGELOG entry

Not release notes — the record of what changed and why, for a reader who was not
in the room. Reach a milestone from the table above and the version moves with
it; otherwise it stays in `[Unreleased]`.

### 6. Open the PR

Disclose the coding agent and the model. This is a published requirement of the
`foundation` spec (*AI Authorship Is Disclosed*), declared as a review-policy gap
in `[tool.graftwork.traceability]` precisely because no test can enforce it.

### 7. Merge, and tag if a milestone was reached

```bash
git checkout main && git pull origin main
git tag -a v<X.Y.Z> -m "v<X.Y.Z>"
git push origin v<X.Y.Z>
```

Stock cuts a release candidate first, because its UAT includes cases that need a
published tag to run against — you cannot rehearse grafting from a tag without
one. **This project has no such case**, since nothing grafts from it, so the
candidate step is dropped rather than performed emptily. Add it back the day a
UAT case here genuinely needs a tag.

### 8. Re-sync from Stock when it releases

Stock's CHANGELOG is a list of migrations waiting to happen here. Read it forward
from the `stock-version` recorded in `pyproject.toml`, apply each entry as its own
small PR, and bump the recorded version when they are all in.

This project currently sits on Stock's **stable `v0.3.0`**, having been rebuilt
onto the release candidate `v0.3.0-rc.1` so that the candidate could be tested
by something real before Stock cut the tag. It was — see below — and the move
from `v0.3.0-rc.2` to `v0.3.0` was exactly the no-op this section predicted: a
single-file diff, entirely internal to Stock's own UAT record, that changed
nothing this project inherits.

It already worked once. This project's own graft was the "something real" that
found the bug behind `v0.3.0-rc.2` — Stock's own graft steps said nothing about
`openspec/changes/`, so its backlog stubs travelled across by default. The
re-sync from rc.1 to rc.2 was close to a no-op in substance: a version bump and
a credit line, because the fix itself had already been applied here by hand
before Stock formalized it. The mechanics of *doing* the re-sync mid-flight —
nothing merged yet, one branch carrying all the project's own rewrites — are
their own small piece of process, kept as
[a skill](.claude/skills/stock-resync-in-flight-graft/SKILL.md) rather than
worked out fresh next time. Stock brought the skill back into its own
foundation, renamed with the `stock-` prefix so a later re-sync can tell at a
glance whether `.claude/skills/<name>/` is safe to overwrite
([Stock ADR 0011](decisions/stock-0011-resync-in-flight-graft-skill.md)); this
project's own copy was renamed to match.
