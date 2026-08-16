# Stock ADR 0008: Stock's own ADRs carry a `stock-` prefix

- **Status:** accepted
- **Date:** 2026-08-16

## Context

ADRs travel with the graft — that is the point of them, and
[the graft instructions](../../README.md#grafting-a-project-from-stock) say to
keep `docs/decisions/`. Until now Stock numbered its ADRs `0001`, `0002`, … and
told grafted projects to start their own at the next free number: 0005 when Stock
had four, then 0008 when Stock had seven.

That advice cannot work, and a real graft proved it. A project stamped when Stock
had four ADRs starts its own at 0005. Stock then adds three of its own — 0005,
0006, 0007 — and the next re-sync collides head-on with three files the project
already owns.

The collision was measured on a project grafted at v0.1.2 with six ADRs of its
own: three direct filename collisions, and **45 references across 11 files** that
a renumber would have to rewrite by hand — README, CLAUDE.md, a glossary, the
ADRs' own cross-references, and artifacts inside `openspec/changes/`.

Worse, the cost recurs. Every future Stock release that adds an ADR imposes
another renumber on every grafted project, and each one is a chance to break a
link silently — a URL that still resolves but now points at a different decision.

The measurement that decided the fix: in that project, **nothing referenced
Stock's inherited ADRs by number.** The only match for each was its own title
line. Stock's ADR filenames are, in practice, cited only within Stock. Renaming
*Stock's* files is therefore close to free; renaming *the project's* is what
costs 45 edits.

## Decision

Stock's ADRs are named `stock-NNNN-<slug>.md` and titled `# Stock ADR NNNN:`.
Prose cites them as "Stock ADR 0004".

A grafted project numbers its own ADRs from `0001` and never renumbers them. The
two sequences share a directory and cannot collide.

`0000-adr-template.md` keeps its bare name: it is a template both sides copy from,
not a decision Stock made.

## Consequences

- A re-sync never rewrites a project's history. That is the whole point — the
  previous scheme made Stock's growth into a migration cost the project paid in
  hand-edited cross-references.
- `ls docs/decisions/` in a grafted project separates at a glance into what the
  project decided and what it inherited.
- Stock's own directory reads slightly oddly — everything in it is Stock's, so
  the prefix is redundant *there*. That redundancy is the price of the file being
  identical in both places, which is what makes the graft a copy rather than a
  transformation.
- Existing links to Stock's ADR files break — README badges, any bookmark, and
  the file paths quoted in released CHANGELOG entries for v0.1.0–v0.1.2. Since
  Stock has no live grafts at the time of this decision, the blast radius is
  Stock's own repository and the cost is paid once, now, rather than compounding.
- The prefix has to be remembered when adding a Stock ADR. Nothing enforces it;
  it is a naming convention, and a `stock-`less ADR in Stock would simply be
  wrong in a way only review catches.

## Alternatives considered

- **Reserve a number block — Stock keeps 0001–0099, projects start at 0100.**
  Also permanent, and keeps filenames uniform. Rejected because it still forced
  the one-time 45-reference renumber on the existing graft, and "start at 0100"
  is an arbitrary rule a newcomer has to be told; `stock-` explains itself.
- **A subdirectory — `docs/decisions/stock/`.** Cleanest separation, and both
  sequences could start at 0001. Rejected because it changes the relative depth
  of every link *inside* the ADRs (`../UAT.md` becomes `../../UAT.md`) and adds a
  file-moving step at graft time that is easy to skip and silently breaks links.
- **Tell re-syncers to renumber, as originally suggested.** Smallest change to
  Stock and the largest cost to everyone else, recurring at every release that
  adds an ADR. This is the option the measurement argued against.
