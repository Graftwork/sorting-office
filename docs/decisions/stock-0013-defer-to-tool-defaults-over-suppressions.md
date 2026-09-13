# Stock ADR 0013: Defer to tool defaults over suppressions

- **Status:** accepted
- **Date:** 2026-08-25

## Context

Grafting Stock onto an existing project (the first case attempted after the
fact, rather than at creation — see the in-progress `stock-graft-existing-project`
skill) surfaced a concrete instance of a recurring choice: ruff's `F401`
treats a whole Jupyter notebook as one shared import namespace rather than
per-cell scopes. A name imported in an earlier cell reads as already
available in every later cell, so `ruff check --fix` strips a "redundant"
import from a later cell even when that cell calls the name directly. The
practical effect: that cell can no longer be run standalone — kernel
restart, run only that cell — without a `NameError`.

The instinctive engineering fix is a targeted suppression: a `# noqa: F401`
on the redundant-looking import, or excluding that cell's import line from
`--fix`, to keep the cell independently runnable. For a notebook already
written for sequential top-to-bottom execution — the normal way one is
used — that property was not actually needed. The suppression would have
bought nothing real, at the cost of a comment whose justification nobody
revisits.

This is not really about ruff, or about notebooks. It is about who is
expected to judge, later, whether a suppression is still warranted.
Graftwork's target user is a product owner, not an engineer — someone
directing an LLM to write code, not someone who reads diffs for a living
or carries the context to know why an exception was added. A suppression
comment is a standing claim: this specific case is fine to deviate on. That
claim needs re-evaluating every time the surrounding code changes, and this
audience is specifically the one least equipped to do that re-evaluation —
or to safely remove a suppression that has stopped being true.

Stock already applies this reasoning in one place: a declared traceability
gap ([Stock ADR 0005](stock-0005-declared-gaps-in-traceability.md)) requires
a written, checked reason precisely because "we cannot test this" has to be
a decision someone made, not a hole nobody noticed. A lint or format
suppression is the same shape of claim, made more casually and checked by
nothing.

## Decision

**Default to the tool's own defaults.** Do not add a suppression, exception,
or workaround to preserve a property a project does not actually need, even
in cases where an experienced engineer might reasonably judge it safe to
keep one. Treat a suppression as something that must be explicitly
justified in writing — the same bar as a declared traceability gap — not as
a routine option sitting alongside the default behavior.

This is deliberately a stricter bar than a typical project would set for
itself. That is the point: Stock's downstream audience skews non-technical
by design, not by accident, and the usual engineering judgement call —
"is this suppression still warranted?" — is not one this audience can
reliably make.

## Consequences

- Fewer suppressions across every grafted project, and the ones that remain
  carry a written reason a reviewer (human or agent) can check against,
  rather than a `# noqa` whose justification lives only in whoever wrote it.
- Some real, occasionally mildly annoying tool behavior gets accepted rather
  than worked around — the notebook-standalone-cell case above being the
  first measured example. That is an accepted cost, not an oversight.
- This raises the bar for *adding* an exception more than it constrains
  existing ones: nothing here mandates auditing every suppression already in
  a project at graft time, only that a new one earns its place the same way
  a declared gap does.
- Applies generally, not only to `ruff` or to notebooks — any linter,
  formatter, type checker, or CI check a grafted project adopts inherits the
  same default: its own defaults first, a justified-in-writing exception
  only when the default is genuinely wrong for the case, not merely
  inconvenient.

## Alternatives considered

- **Ordinary case-by-case engineering judgement**, the same standard a
  typical project would apply. Rejected: it puts the discernment burden on
  exactly the audience Stock is built to not require that discernment from.
- **Scope this narrowly to lint suppressions only**, rather than a general
  principle. Considered, but the underlying question — can this audience
  evaluate whether an exception still holds? — applies identically to a
  type-checker ignore, a disabled CI check, or a skipped test, not only to
  `# noqa`. A narrower rule would have to be rediscovered for each of those
  in turn.
