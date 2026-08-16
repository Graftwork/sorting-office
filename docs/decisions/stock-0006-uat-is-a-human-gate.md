# Stock ADR 0006: UAT is a human gate, ordered before the PR and the archive

- **Status:** accepted
- **Date:** 2026-08-16

## Context

The verification layer checks what a test can check. Plenty of what a project
promises is outside that: generated files, rendered images, printed parts, UI,
the readability of an error message. For those, the only instrument is a person
looking at the output.

Two failure modes showed up in practice, and neither is exotic.

**The gate gets closed by the wrong party.** An agent working a task list will
mark every box, because marking boxes is what the list is for. A task that says
"check the output looks right" gets ticked on the strength of the code having
run. The result is a 35/35 report where the one step that mattered never
happened.

**The gate happens too late.** If the UAT step is present but unordered, the
natural sequence is: finish the checklist, open the PR, then look at the output.
That is the wrong moment to discover the concept was wrong — and on a real
project one physical test killed a change that was fully specced *and*
implemented. The reviewing was wasted because the looking came last.

The archive being one-way makes the ordering load-bearing rather than tidy.

## Decision

Cases live in [`docs/UAT.md`](../UAT.md), numbered, each with a `Command`, an
`Expect`, and a `Last passed` date.

A change whose output a test cannot fully judge carries verification tasks that
regenerate the artifacts and look at them, **ordered before the archive step and
before any PR**.

An agent may run the commands and report what it saw. It may not mark a case
passed. Reporting 34/35 with the eyeball task named and open is the correct
outcome; 35/35 is not.

## Consequences

- The date is the mechanism. A case with `Last passed: never`, or a date from six
  months ago, is visible in a way that "we have UAT" is not.
- UAT stays cheap to skim, and the cases that matter accumulate in one place
  rather than being re-derived per change.
- It is deliberately not automated. Automating it would convert the one check a
  machine cannot make into one it can appear to make, which is the failure this
  ADR exists to prevent.
- Stock's own cases are real and runnable, so a grafted project starts with
  worked examples rather than an empty heading.
- The cost is a manual step before every archive on output-shaped changes. For
  changes the suite fully covers, there is nothing to run.

## Alternatives considered

- **Snapshot/golden-file tests instead.** Good for catching *change*, useless for
  catching *wrong* — a golden file happily locks in output nobody ever looked at.
  Worth having as well, never instead.
- **UAT as a checklist inside each change.** Keeps it close to the work, but the
  cases vanish into `archive/` and get rewritten from memory next time.
- **A `Last passed` field maintained by CI.** CI cannot pass a case that needs
  eyes, and a machine-written date here would be a lie with a timestamp on it.
