# Ways of working

OpenSpec gives you primitives — a change, its artifacts, an archive. It does not
give you judgement about when to open one, when to abandon one, or what to carry
forward when you do. This file is that judgement, written down.

Everything here earned its place on a real project. Nothing is here because it
sounded sensible.

## The loop

```
/opsx:explore   →   /opsx:propose   →   /opsx:apply   →   UAT   →   /opsx:archive
  think out loud      proposal,           work the        eyeball    specs updated,
  no artifacts        design, tasks       task list       the output change filed
```

The steps are not phase-locked. You can explore in the middle of applying, and
you can edit a change's artifacts at any point before archive. What you cannot do
is skip UAT, because the archive is one-way.

## Recipes

| Situation | Action |
| --- | --- |
| You don't know what you want yet | `/opsx:explore`. No artifacts, no commitment, nothing to abandon. |
| You know what you want | `/opsx:propose`. |
| You want to note work you haven't designed yet | Keep a **proposal-only change** as a backlog stub. Accept that it will not pass strict validation until it has deltas. |
| You learned something mid-flight that changes scope | Edit the in-flight change's artifacts directly. Nothing is locked before archive. |
| A change turns out to be wrong | Abandon it — but transcribe the *why* into whatever replaces it first. |
| Something you're about to spec rests on an untested assumption | Test the assumption first. See [Validate before you specify](#validate-before-you-specify). |
| New work contradicts a published requirement | That is an argument *for* a real change, not against one. Write the delta. |
| You're walking back shipped behaviour | A new change with a `REMOVED` delta carrying a **Reason** and a **Migration**. |
| A change already covers the ground you're about to propose | Continue that one. Do not open a second. |
| Implementation is done and the tests pass | Run the [UAT](docs/UAT.md) cases, *then* open the PR, *then* archive. |

## Conventions

### Context is not content

To brief an agent well you have to tell it things. Why this matters, who it is
for, what went wrong last time. That is the right way to work — an agent
reasoning without context produces plausible, useless requirements.

But this method is a transcription pipeline. It is built to turn what you said
into something written, reviewable, and permanent:

```
conversation  →  proposal  →  design  →  spec  →  code  →  commit  →  remote
    ^                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^           ^
 said to explain       the window — every one of these is a copy    │
 the problem                                                 past here the only
                                                             honest remedy is to
                                                             rebuild the repo
```

Nothing has to malfunction for a detail offered as background to end up in a
published requirement. The pipeline has no notion of *why* you said something.

So the rule: **detail supplied to aid understanding is not thereby material for
the artifacts.** Requirements name categories and rules — a named correspondent
rather than their name, a retention period rather than whose records. Where a
specific genuinely is the requirement, it gets named as a specific and confirmed
before it is written down. The agent says what it abstracted, so the judgement is
visible rather than silent.

Two things follow that are easy to get wrong:

- **The control sits at the crossing, not at review.** A check before the PR is
  already too late if a commit was made an hour earlier. Git history is not
  edited, it is rewritten — a different and worse operation.
- **The machine half is the small half.** The `detect-secrets` pre-commit hook
  catches credentials, and that is worth having. It cannot tell whether "the
  consultant" is a category or a person. Do not read a green hook as "checked" —
  the rest is a review policy, declared as a gap in `pyproject.toml` precisely
  because no test can keep it.

This was learned the expensive way: the first project grafted from Stock was torn
down and rebuilt because personal context given while scoping had been written
into a spec, then into code, then pushed.

### Small changes, because abandonment is the cheap part

The usual arguments for small scope are velocity and review burden. Neither is
the real one here. When an agent can produce a complete implementation in an
hour, the binding constraint becomes **how much work you are willing to throw
away when it turns out to be wrong**. Small changes are cheap to abandon, and
that is what makes course-correction painless.

### Backlog stubs are proposal-only changes

A problem you have noticed but not designed needs somewhere to live that isn't an
issue tracker nobody reads. In OpenSpec the only primitive is a change, so the
convention is a change with a `proposal.md` and nothing else.

**The cost, stated plainly: `openspec validate` will call it invalid for as long
as it stays a stub.** There is no "intentionally incomplete" state — validation is
binary. Measured against the stub in this repo:

```
$ openspec validate version-string-consistency          # exit 1
Change 'version-string-consistency' has issues
✗ [ERROR] file: Change must have at least one delta. No deltas found.

$ openspec status --change version-string-consistency   # exit 0
Progress: 1/4 artifacts complete
[x] proposal
[ ] design
[ ] specs
[-] tasks (blocked by: design, specs)
```

So read `status` for progress, and treat `validate` as a completeness measure
rather than a health check. Do not wire `validate` into CI unless you have
decided that stubs are banned.

Stubs pay for themselves when they carry research. A stub that already holds the
measurements and the dead ends gives `/opsx:propose` something to build on
instead of starting cold.

### Transcribe learnings forward

OpenSpec does not model relationships between changes. Supersedes, replaces,
depends-on are prose, not data — you cannot query "what replaced X". **The tool
will silently lose your reasoning unless you carry it by hand.**

So when you abandon or supersede a change, copy the *why* into its replacement,
in the imperative, addressed to whoever tries next:

> Do not attempt a straightforward box-subtraction implementation again without
> first working out how to keep the mating profile intact — that is precisely
> what went wrong last time.

A paragraph like that is worth more than the branch you deleted.

The stock OpenSpec proposal template has no slot for this — it is `## Why`,
`## What Changes`, `## Capabilities`, `## Impact`. Rather than fork the template,
Stock adds a proposal rule in `openspec/config.yaml` telling the agent to write a
`## Background` section carrying the reasoning forward whenever a change replaces
an abandoned one. Rules are the supported hook; an edited template would be
overwritten the next time OpenSpec regenerates.

### Validate before you specify

When a change rests on an assumption you could cheaply test — does that API
really return that? does the library actually do this? will anyone click it? —
test it **before** writing the spec, not after.

Specification effort spent on an unvalidated premise is the work most likely to
be thrown away. A proposal is cheap to abandon; an experiment is cheaper still,
and if it works you write the deltas with real numbers instead of provisional
ones.

### A spec contradiction is a signal

When new work contradicts a published requirement, that is the strongest
available argument that it deserves a real change rather than a quiet flag or a
preset. Ship it without noticing, and the spec is left actively false — worse
than silent, because someone will trust it.

### `MODIFIED` means the *entire* updated requirement

A `MODIFIED` delta must restate the whole requirement, not the part that changed.
Partial content silently loses the rest at archive time. This is an easy trap and
the loss is quiet.

### Deprecation is first-class

Walking back shipped behaviour is a new change with a `REMOVED` delta carrying a
**Reason** and a **Migration**. The original stays in `archive/` as honest
history. "We did this, then we knew better" is a feature of the record, not an
embarrassment to tidy away.

### UAT is a gate, and it comes before the PR

For anything a test cannot fully judge — generated files, rendered output, UI,
anything physical — the change's verification tasks must include regenerating the
artifacts and looking at them, **ordered before the archive step and before any
PR**.

The ordering has to be explicit because the natural instinct is to finish the
checklist and open the PR. An unordered UAT step gets done after the PR is up,
which is the wrong moment to discover the concept was wrong.

**An agent cannot close a gate that requires human senses.** Reporting 34/35 with
the eyeball task named and left open is correct. Reporting 35/35 is not.

Cases live in [`docs/UAT.md`](docs/UAT.md), each with a `Last passed` date — the
date is what stops UAT from going quietly stale.

### Branch names match the route

[Two routes](CLAUDE.md#conventions), two prefixes — the branch says which one
before you open the PR:

- `feature/<change-name>` — the OpenSpec route. Reuse the change's own directory
  name (`openspec/changes/<change-name>/`) as the slug, so the branch, the change,
  and the PR all name the same thing without a second slug to keep in sync. Covers
  new capability and bug fixes alike — OpenSpec doesn't distinguish the two at the
  change level, so neither does the branch.
- `chore/<slug>` — the direct route: docs, ADRs, CI, toolchain, permissions.

Claude Code on the web derives its own `claude/<slug>-<hash>` branch per session,
which is neither. Rename onto the matching prefix (`git branch -m`) before opening
the PR.

### Prove you didn't break the existing thing

For any additive change, include a task that *proves* the untouched path is
untouched. Extract the pre-change sources with `git show HEAD:<file>` into a temp
directory, run them against the same environment, and compare hashes:

```bash
mkdir -p /tmp/before && git show HEAD:path/to/module.py > /tmp/before/module.py
# regenerate with both, then:
sha256sum before.out after.out
```

Non-destructive — no stashing, no worktree. "Identical hashes" is a result a
reviewer can act on. "I don't think I changed anything" is not.

### Keep the fast loop fast, without relying on memory

The moment a project grows a slow subset — integration tests, browser drivers,
real geometry, model inference — the inner loop starts costing minutes and people
quietly stop running it.

Split it, but do not split it by asking everyone to remember a marker. Mark it
from something the test already declares. Requesting an expensive fixture is the
signal:

```python
# conftest.py
SLOW_FIXTURES = {"rendered_model", "browser"}


def pytest_collection_modifyitems(items):
    for item in items:
        if SLOW_FIXTURES & set(getattr(item, "fixturenames", ())):
            item.add_marker("slow")
```

Then `pytest -m "not slow"` is the loop and the full suite is CI. A test that
starts using the expensive fixture gets marked the moment it does, which is the
point — a convention nobody has to maintain is the only kind that survives.

Stock does not ship this, because Stock has no slow tests and a marker with
nothing to mark is exactly the speculation these conventions forbid. Add it the
day the suite earns it.

## Who does what

### The product owner

- **Supplies the ground truth the agent cannot observe.** Field experience —
  "we've been cutting these in OrcaSlicer for months and it's been fine" — is
  data the agent does not have and cannot derive. It outranks the agent's
  theory.
- **Answers the genuine forks.** Decisions that lead to different code.
- **Decides what to throw away.** Scaling a change down is the PO's call.

### The agent

- **Asks on genuine forks, decides on everything else.** A PO's attention is the
  scarce resource. A question should come with context, a recommendation, and a
  realistic preview of each option, so answering takes seconds. Everything else
  gets decided — with the one judgement call you were least sure about flagged,
  and an offer to change it.
- **Marks the provenance of load-bearing numbers.** Every number that a decision
  rests on is *measured* (name the command that produced it), *derived* (show the
  derivation), or *recalled* (treat as unverified). A PO cannot check an agent's
  arithmetic, but they can ask "did you measure that?" — a question that is cheap
  to ask and expensive to fake. If a document's numbers all came from real
  output, say so in a line of its own.
- **Says plainly when a correction changes the recommendation.** Absorbing a
  correction silently hides the fact that the answer moved.
- **Reports which artifacts it edited mid-flight, and why.** Correcting a wrong
  task in place is right. Doing it silently is not.
- **Does not close a gate that needs human senses.**
- **Discloses AI authorship in the PR** — the coding agent and the model used.

## OpenSpec's rough edges

Knowing these stops you assuming you have misunderstood something.

- **Archive is one-way.** There is no unarchive. This is why UAT precedes it.
- **There is no issue, draft, or spike primitive.** A change is the only unit, so
  backlog items are proposal-only changes and live with the validation cost.
- **Validation is binary.** No "intentionally incomplete" state.
- **Renaming a change is manual** — directory, branch, and every cross-reference,
  by hand.
- **`archive` moves the change a directory deeper and does not rewrite its
  relative links.** A change at `openspec/changes/<name>/` linking to
  `../../../docs/…` lands at `openspec/changes/archive/<date>-<name>/`, where
  that path is one `../` short and every such link is silently dead. Measured on
  a real archive in this repo: 2 files, 3 links. Check links after archiving, or
  prefer repository-root-relative references in change artifacts.
- **Nothing may reference a scenario id until the change is archived.** A
  scenario lives in the change's delta until `openspec archive` writes it into
  `openspec/specs/`, so a test marker or a declared gap naming it fails the
  traceability guard as an unknown claim until then. There is no `sync` command
  in the CLI to write main specs early (`openspec --help`, v1.6.0), so plan the
  task order with the archive *ahead* of anything that cites an id — the natural
  order of "implement, then archive" is backwards here.
- **The change argument is a flag on some commands and positional on others.**
  `status --change <name>` and `instructions <artifact> --change <name>`, but
  `validate <name>`. Getting it wrong on `validate` prints
  `error: unknown option '--change'` **and still exits 0**, so a script that
  trusts the exit code will read a typo as a pass. Verified against
  `@fission-ai/openspec@1.6.0`.
- **Relationships between changes are prose.** Supersedes and depends-on are not
  queryable, which is why learnings must be transcribed forward by hand.

## Growing this file

Add a convention when it has changed an outcome on a real project — not when it
sounds right. Anything a future reader might mistake for drift gets an ADR in
[`docs/decisions/`](docs/decisions/) instead. Anything that can be checked by
code belongs in the suite, not here.
