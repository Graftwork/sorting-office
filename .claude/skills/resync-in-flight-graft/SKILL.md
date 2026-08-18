---
name: resync-in-flight-graft
description: Bring a project grafted from Graftwork Stock up to a newer Stock tag while the project's own first work is still mid-flight — nothing merged to a settled main yet, everything living on one branch. Use when Stock has moved (a new rc or a new release) and the grafted project needs to pick it up without a mechanical merge mangling docs the project has already rewritten for its own identity.
license: MIT
compatibility: Requires the graft to follow the rolling-main pattern below; a git remote for Stock reachable to diff and fetch tags from.
metadata:
  author: graftwork
  version: "1.0"
  provenance: "Written after the first real case: sorting-office picking up stock v0.3.0-rc.1 -> v0.3.0-rc.2 before its first PR had even merged."
---

Bring a grafted project's `main` and in-progress work up to a newer Stock tag,
without a raw `git merge` mangling files the project has already rewritten.

## When this applies

A normal re-sync — read Stock's CHANGELOG forward from the recorded
`stock-version`, apply each entry as its own small PR — assumes the grafted
project already has a settled history: at least one release behind it, `main`
representing something real that other work branches from cleanly.

This skill is for the gap before that exists: the project has grafted, started
its own first work, and none of it is merged yet. There is no settled `main` to
branch a normal re-sync PR from — the project's entire identity (rewritten
README, CHANGELOG, docs/RELEASING.md, its own ADRs) lives on one branch, and
`main` is still just the graft.

**Precondition this skill assumes:** `main` is kept as a rolling, verifiable
mirror of *the current Stock tag* — nothing project-specific has been committed
to it. If a project's `main` doesn't follow that pattern (something has already
been merged to it), this skill doesn't apply as written; use the normal
CHANGELOG-forward re-sync instead.

## Why a raw merge doesn't work here

`git merge` reasons about lines, not intent. A file the project has wholesale
rewritten — its own README replacing Stock's generic one, say — shares almost no
text with Stock's edited version of that same file, even though both are
"about the README." The merge algorithm sees a modify/modify conflict on nearly
every line and hands you a wall of conflict markers with no more insight in
them than the two files already had apart. Resolving that by reading marker by
marker is slower and less clear than just reading the upstream diff once and
deciding, file by file, what's still relevant.

So this skill splits the problem in two, by file, rather than treating the
whole update as one merge:

- **Files the project hasn't touched yet** (still byte-identical to what the
  graft produced) — a straight patch applies cleanly, because there's nothing
  to conflict with. Verifiable, not just probable: the result's tree hash can
  be checked against the new tag's tree hash directly.
- **Files the project has already rewritten for its own identity** — don't
  merge them. Read what changed upstream, in full, and decide by hand what (if
  anything) is still relevant to a project that has already diverged.

## Steps

### 1. Diff the two tags

```bash
git fetch origin --tags
git diff <old-tag> <new-tag> --stat
git diff <old-tag> <new-tag>
```

Read the whole diff before deciding anything. Categorize each changed file:

- **About Stock itself** — Stock's own release process, its own ADR
  numbering, anything describing how Stock manages *its* downstream grafts.
  This almost never needs applying to a grafted project; it describes Stock
  managing itself, not something the grafted project inherits. Worth noting in
  the resync record that it was read and consciously not carried over, and
  why — that's a real judgement call, not nothing.
- **A fix for something the grafted project can act on.** Check whether the
  project already worked around it by hand before the fix landed upstream —
  this is common precisely because a real graft attempt is often what
  surfaces the bug in the first place. If so, there's nothing left to apply,
  only something to credit.
- **Something genuinely new to bring in.** Rare for a small point release, but
  possible — treat it the same as any other re-sync entry: read it, apply the
  substance by hand to whichever files it affects.

### 2. Update `main`

For the files still untouched by the project (check with
`git log main -- <file>` — if the only commit touching it is the graft itself,
it qualifies):

```bash
git checkout main && git pull
git diff <old-tag> <new-tag> -- <untouched-files> > /tmp/stock.patch
git apply --check /tmp/stock.patch   # confirm it applies cleanly first
git apply /tmp/stock.patch
git add -A && git commit -m "chore: re-graft to Stock <new-tag>"
```

Verify, don't assume:

```bash
git rev-parse HEAD^{tree}
git rev-parse <new-tag>^{tree}
```

These must match exactly. If they don't, something on `main` has diverged that
this skill's precondition assumed hadn't — stop and re-check rather than force
it through. Push `main`.

### 3. Bring the work branch up to date

```bash
git checkout <work-branch>
git merge main --no-commit --no-ff
```

Expect conflicts exactly on the files identified as "already rewritten" in
step 1. For each:

```bash
git checkout --ours <file>
```

This discards Stock's specific text for that file and keeps the project's own
— correct whenever step 1 already established the upstream content there
doesn't apply. Then apply by hand whatever step 1 found was still relevant:
typically a version-string bump and a CHANGELOG entry crediting the fix.

**Bump version strings by judgement, not by search-and-replace.** Grep for the
old string and read every hit:

```bash
grep -rn "<old-tag>" --include="*.md" --include="*.toml" .
```

Some are permanent statements about the past ("this project was grafted from
`<old-tag>`" — true forever, don't touch) and some track current state
("this project currently sits on `<old-tag>`" — this one moves). Getting this
backwards either erases real history or leaves a stale claim standing; a
project's own `docs/RELEASING.md` usually already states this distinction for
its own release process, and the same judgement applies here.

Stage everything, including files that auto-merged without conflict — a clean
auto-merge is still worth a second look if it touched something version- or
identity-bearing.

### 4. Verify and record

Run the project's full check suite and traceability guard. Run the "does this
read clean to a stranger" UAT case, if the project has one, before committing
— a merge commit crosses the same boundary any other commit does. Write the
CHANGELOG entry for the resync itself: what moved, what was already handled by
hand, what was consciously not carried over and why. Commit, push.

## What this looks like when it's mostly bookkeeping

Often the actual content to apply is small — a version bump and a sentence of
credit — even though the mechanical process (diff, patch, verify, merge,
resolve, re-verify) is not. That's fine and worth saying plainly in the
CHANGELOG entry rather than padding the record to look more substantial than
it was. The value of doing it properly is the same either way: `main` stays a
provably accurate mirror of the tag it claims to represent, and the work
branch picks up exactly what's relevant to it without losing anything it had
already figured out for itself.
