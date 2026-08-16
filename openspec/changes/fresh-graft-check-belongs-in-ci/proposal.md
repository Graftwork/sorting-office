# Backlog stub — not yet designed

A **proposal-only change**: a tracked problem that has not been designed yet.
`openspec validate` will report it invalid ("no deltas found") until it has
deltas; read `openspec status` (`1/4 artifacts`) for progress. See
[Ways of working](../../../WORKFLOW.md#backlog-stubs-are-proposal-only-changes).

## Why

**UAT case 1 — "A fresh graft is green before anyone writes code" — does not
belong in `docs/UAT.md`.**

The file's own admission rule says a case belongs there "when the check needs
human senses or human judgement… If a test could make the call instead, write the
test." Case 1 fails that test. Its `Expect` is *lint clean, suite passes, no edits
needed* — three conditions a machine judges completely, with no residue of
judgement. Compare the cases that do belong:

| Case | What a person actually decides |
| --- | --- |
| 2 — guard output | "could a stranger act on this?" |
| 3 — declared gaps | "does each written reason still hold?" |
| 4 — stranger read | "is this detail sensitive to *me*?" |
| **1 — fresh graft** | **nothing — it is exit codes** |

Leaving it there costs more than tidiness. Every release, a human is asked to
adjudicate something already decided, which trains the reader to skim the file —
and the cases either side of it are exactly the ones that must not be skimmed. A
UAT list padded with mechanical checks is how a UAT list stops being read.

There is a second, quieter cost: because it *looks* like UAT, its result is
recorded as a `Last passed` date rather than as a CI status, so "is the fresh
graft green right now?" is answerable only by reading a hand-maintained date
rather than by looking at the badge.

## What Changes

Not yet designed. The shape is: move the check into CI as its own job, delete
case 1 from `docs/UAT.md`, and renumber the remaining cases.

Open questions:

- **Does it run on every push, or only on release?** It is fast (measured: the
  rehearsal completes in seconds once `uv sync` is warm), which argues for every
  push. But it duplicates most of what the `check` job already does, so the
  marginal value is only in the *tracked-files-only* aspect — it catches a file
  that was never `git add`ed.
- **How does CI express "tracked files only" faithfully?** The local rehearsal
  uses `git ls-files -z | xargs -0 tar cf -`. A CI checkout is already only
  tracked files, so a naive port would test nothing new. The check may need to
  run against a clean re-clone rather than the workspace, or the value may be
  small enough that a plain `git status --porcelain` assertion covers it.
- **Does case 5 (the published tag) move too?** No — it needs a published tag and
  verifies the release rather than the code, so it stays. But whatever CI job is
  built here is most of what case 5 runs, and the two should share a script
  rather than drift apart.
- **What happens to the renumbering?** Case numbers are cited in prose across
  `docs/UAT.md` and `docs/RELEASING.md`. Cite cases by name rather than number
  when this lands, so the next insertion does not break references again — this
  already bit once, when adding case 4 made an existing "case 4" reference point
  at the wrong case.

## Impact

`docs/UAT.md`, `.github/workflows/ci.yml`, possibly a small script shared with
the tag-dependent graftability check (case 5). Docs and CI only, so under
[`docs/RELEASING.md`](../../../docs/RELEASING.md) this would take the direct
route — unless the shared script lands in `scripts/`, which would pull it onto
the full OpenSpec route.
