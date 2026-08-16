# Backlog stub — not yet designed

This is a **proposal-only change**: a tracked problem that has not been designed
yet. It carries the research so that whoever picks it up starts from measured
facts rather than re-deriving them.

`openspec validate` will report this change as invalid ("no deltas found") for as
long as it stays a stub. That is expected and documented — read `openspec status`
(`1/4 artifacts`) for progress. See
[Ways of working](../../../WORKFLOW.md#backlog-stubs-are-proposal-only-changes).

## Why

Stock's version number appears in **13 places across 6 files** at v0.2.0, and
nothing checks any of them. Measured with:

```bash
grep -rn "0\.2\.0" --include="*.md" --include="*.toml" . | grep -v "^./openspec/changes/"
```

The important finding is that **they do not all mean the same thing.** Only five
must move at a release; the rest are permanent statements about the past, and
bumping them would be the bug:

**Must be bumped every release**

| File | Line | Occurrence |
| --- | --- | --- |
| `pyproject.toml` | 3 | `version = "0.2.0"` — the source of truth |
| `README.md` | 10 | `**Version 0.2.0.**` |
| `README.md` | 119 | graft clone `--branch v0.2.0` |
| `README.md` | 141 | `stock-version = "0.2.0"` in the recorded graft |
| `docs/UAT.md` | — | the tag-dependent graftability case's `Last passed` note (case 5 as of v0.3.0; cited by name, since case numbers shift) |

Plus two *additions* to `CHANGELOG.md` — a new heading and a new link-footer
entry — which are appended rather than edited, and the git tag itself.

**Must never be bumped**

| File | Why it is permanent |
| --- | --- |
| `docs/decisions/stock-0007-...md` ×4 | ADR text recording what v0.2.0 specifically did |
| `docs/RELEASING.md` ×2 | the cutover statement — "this rule starts at v0.2.0" |
| `docs/RELEASING.md` ×1 | note recording where the v0.2.0 conventions were earned |

A naive find-and-replace across the repo therefore *corrupts the record* while
appearing to do the release correctly. That is a worse failure than the one this
stub started out describing.

The quiet failure in the other direction: a release bumps `pyproject.toml` and
the CHANGELOG — the two a person naturally thinks of — and leaves the README
telling new projects to clone a tag that is one version stale. The graft still
succeeds, so nothing goes red; the project just starts from the wrong foundation
and records a wrong `stock-version`, which then corrupts its re-sync path.

Both directions are the class of error the traceability guard exists to catch in
its own domain: a link that looks healthy while pointing at the wrong thing.

## What Changes

Not yet designed. The obvious shape — read the version from `pyproject.toml` and
assert every other occurrence agrees — **does not survive the measurement above**,
because it would flag eight correct historical references as errors. Whatever is
built has to distinguish "this is the current version" from "this is a fact about
v0.2.0", and that distinction is not recoverable from the string alone.

Open questions, in the order they need answering:

- **How is a live reference marked?** An explicit marker comment next to each
  one, an allowlist of file/line locations, or a rule that only certain files are
  scanned? The traceability guard's declared-gap mechanism is the nearest prior
  art in this repo and the same "written reason" discipline probably applies.
- **Does the check know about the git tag, or stop at the working tree?** Reading
  tags makes it behave differently in a shallow CI clone, and CI is where it
  would most need to be trustworthy.
- **Is this Stock-specific or a foundation capability?** Grafted projects record
  a `stock-version` that goes stale the same way, which argues for the latter —
  but a general "version strings agree" check is a much larger promise than
  Stock's own five lines.

Answer those before writing deltas. Do not start from the naive
single-source-of-truth check — it was tried on paper here and the measurement is
what killed it.

## Impact

`scripts/`, `tests/`, `openspec/specs/foundation/spec.md`. Under the process in
[`docs/RELEASING.md`](../../../docs/RELEASING.md) this touches specs and the
verification layer, so it runs as a full OpenSpec change rather than a direct
commit.
