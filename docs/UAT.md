# User acceptance tests

The things a test suite cannot judge: whether the output looks right, reads
right, or works the way a person expected. Each case is judged by a human, and
the `Last passed` date is the point — it is what stops UAT from going quietly
stale while the suite stays green.

**Run these before opening the PR and before archiving the change.** Not after.
The archive is one-way, and a PR is the wrong place to discover the concept was
wrong. See [Ways of working](../WORKFLOW.md#uat-is-a-gate-and-it-comes-before-the-pr).

**Case 4 is the exception and runs before the *commit*.** Everything after the
commit is a rewrite rather than an edit, so a check that runs later is worth
nothing. This project exists in its current form because that check did not exist
the first time round.

An agent may run the commands and report what it saw. It may not mark a case
passed — that is the whole point of the gate.

Because that line is easy to blur, each case carries **two** dates:

- **Last agent run** — the commands were executed and this is what came back. An
  agent may write this. It is evidence, not a verdict.
- **Last passed** — a person looked at that output and accepted it. Only a
  person writes this line.

Dates are **batched** — they are updated as part of the next real change rather
than each earning its own pull request.

## Case format

```markdown
### N. <what a person is checking>

- **Command:** the exact thing to run
- **Expect:** what you should see, specifically enough to be wrong
- **Last agent run:** YYYY-MM-DD — what came back
- **Last passed:** YYYY-MM-DD (or `never`) — a person's judgement only
```

---

## Sorting Office's cases

### 1. A fresh clone is green before anyone writes code

- **Command:**

  ```bash
  rm -rf /tmp/so-check && mkdir -p /tmp/so-check
  git ls-files -z | xargs -0 tar cf - | tar xf - -C /tmp/so-check
  cd /tmp/so-check && uv sync && uv run pytest && uv run ruff check .
  ```

  `git ls-files` is what makes this a real rehearsal: it copies only tracked
  files, so anything you forgot to `git add` is missing here exactly as it would
  be missing from a clone.

- **Expect:** lint clean, suite passes, no edits needed to get there.
- **Last agent run:** 2026-08-17 — 18 passed, ruff clean, from tracked files
  only. `mise` cannot be installed in a cloud container, so this ran through `uv`
  directly; the `mise run` equivalents are unverified here.
- **Last passed:** never

### 2. The artifacts read clean to a stranger

The one check that runs **before the commit**. See
[Context is not content](../WORKFLOW.md#context-is-not-content).

- **Command:** read the change's `proposal.md`, `design.md`, delta specs, ADRs
  and any new code as someone with no knowledge of the project would. Then:

  ```bash
  git diff --cached
  ```

- **Expect:** nothing that identifies a real person, place, account, employer,
  or medical or financial circumstance. Requirements read as categories and
  rules. Where a specific *is* present, you recognise it as one you were asked
  about and agreed to.

  Judgement call, and the one to be honest about: if you needed project context
  to understand why a detail is harmless, a stranger reading the public
  repository does not have it.

- **Last agent run:** 2026-08-17 (twice). First pass, on the identity-only
  change: found and abstracted an ADR naming a product the owner uses; flagged
  two placeholder addresses in unstaged code for when it landed. Second pass, on
  this change: those two addresses were replaced with the owner's own fictional
  choices, then this same read caught three *stale* ADR cross-references the
  renumbering script had missed, because it only ran against `openspec/changes/`
  and not `sorting_office/*.py`. Fixed before staging. No personal or
  identifying detail found either time; both misses were process, not privacy.
- **Last passed:** never

### 3. No mail provider is named, and every address is obviously invented

Narrower than case 2 and mechanically checkable up to the last step, which is
where the judgement lives.

- **Command:**

  ```bash
  grep -rniE '@[a-z0-9.-]+\.(com|org|uk|net|io)' --exclude-dir=.git --exclude-dir=.venv .
  ```

- **Expect:** no mail provider named anywhere
  ([ADR 0009](decisions/0009-provider-agnostic-collection.md)), and every address
  on the `sorting-office.test` domain or similarly unmistakable. The judgement: could
  any of these be real? A grep cannot tell you.
- **Last agent run:** 2026-08-17 — no provider named. Every address in the tree
  is on `sorting-office.test`, including `parcels-weekly@` and `stamp-exchange@`
  — the owner's own choices for the retention-behaviour fixtures.
- **Last passed:** never

### 4. A declared gap reads as a decision, not an oversight

- **Command:** `mise run trace`, then read `[tool.graftwork.traceability]` in
  `pyproject.toml`.
- **Expect:** the summary line accounts for the gaps (`…, 3 allowed without
  one`), and every declared reason still holds today. A reason that has quietly
  stopped being true is exactly what this case exists to catch.
- **Last agent run:** 2026-08-17 — `34/37 scenarios claimed by tests, 3 allowed
  without one`. `walks` and `retention` now claim 25 scenarios between them; the
  three gaps are still the ones inherited from Stock, unexamined by this
  project. Whether they hold here is exactly the judgement this case wants.
- **Last passed:** never

---

## Adding cases

A case belongs here when the check needs human senses or human judgement. If a
test could make the call instead, write the test.

Cases this project will earn as the pipeline is built, each needing something to
exist first:

- A dry-run report at the Counter that a person can act on — does it say *why* a
  message would be pruned, in words that make sense without reading the code?
- Mail moved to Trash is still readable from an ordinary mail client.
- The postbox is genuinely untouched by anything except the sweeper.
