# Tasks

> **Ordering note (edited mid-flight).** The first draft of this list put the
> claiming test and the declared gaps before the archive step. That cannot work:
> scenario ids do not exist in `openspec/specs/` until the delta is archived, so
> the traceability guard rejects any marker or declaration naming them as
> unknown. The CLI has no `sync` command to write main specs early
> (`openspec --help`, v1.6.0), so **archive moves ahead of everything that
> references a scenario id.** Recorded as a rough edge in `WORKFLOW.md`.

## 1. The mechanical half

- [ ] 1.1 Add the `Yelp/detect-secrets` hook at `rev: v1.5.0` to
      `.pre-commit-config.yaml`, with no baseline file (see design.md).
- [ ] 1.2 Verify it passes clean across the repository:
      `uvx pre-commit run detect-secrets --all-files`.
- [ ] 1.3 Verify it fails on a planted credential in a scratch file, then delete
      the scratch file. A guard that cannot fail is not a guard.

## 2. The human half

- [ ] 2.1 Add the house rule to `CLAUDE.md`: abstract by default, say what was
      abstracted, ask before making it concrete.
- [ ] 2.2 Add the long-form convention to `WORKFLOW.md`, including the pipeline
      diagram and why the remedy after a push is a rebuild.
- [ ] 2.3 Add the rough edge to `WORKFLOW.md`: nothing may reference a scenario
      id until the change is archived.
- [ ] 2.4 Add a UAT case: read the artifacts as a stranger and flag anything
      identifying a real person, place, account or condition.

## 3. Archive — moved ahead of the spec-referencing work

- [ ] 3.1 Archive the change so the main spec is written by the tool rather than
      by hand.
- [ ] 3.2 Confirm `openspec/specs/foundation/spec.md` now carries the
      **Context Is Not Content** requirement and its three scenarios.

## 4. Claim and declare — only possible once the ids exist

- [ ] 4.1 Add a test claiming
      `foundation/a-commit-carrying-a-credential-is-refused` — assert the hook is
      configured in `.pre-commit-config.yaml`, since the suite cannot run git
      hooks but can check the wiring is present.
- [ ] 4.2 Declare `foundation/personal-detail-supplied-as-context-stays-out-of-the-artifacts`
      in `[tool.graftwork.traceability]` with a written reason.
- [ ] 4.3 Declare `foundation/a-load-bearing-specific-is-confirmed-before-it-is-written-down`
      with a written reason.
- [ ] 4.4 Run `mise run trace` and confirm the summary accounts for all three
      declared gaps and reports no unclaimed scenarios.

## 5. Release

- [ ] 5.1 Bump the version to 0.3.0 in every place that must move — `grep -rn
      "0\.2\.0"` and consult the backlog stub at
      `openspec/changes/version-string-consistency/` for which occurrences are
      permanent and must NOT be bumped.
- [ ] 5.2 Write the CHANGELOG entry as a migration instruction, not release
      notes.
- [ ] 5.3 Update the batched `Last passed` dates in `docs/UAT.md` — the first use
      of the batching decision.
- [ ] 5.4 `mise run check` and `uvx pre-commit run --all-files` both green.

## 6. Verification — before the PR

- [ ] 6.1 Fresh-graft rehearsal from tracked files only.
- [ ] 6.2 Run the UAT cases that do not need a published tag, and report what was
      seen. **Do not mark any case passed** — that is the person's call.
