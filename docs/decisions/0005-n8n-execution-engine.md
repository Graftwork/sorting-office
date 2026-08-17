# ADR 0005: n8n as the pipeline execution engine

- **Status:** proposed
- **Date:** 2026-08-12
- **Carried forward:** written before this repository was rebuilt, and renumbered
  on the way in. The reasoning is unchanged, and it is still *proposed* — nothing
  has been built on n8n yet, which is what would confirm it.

## Context

The Collection → Facing → Dispatch pipeline needs something to schedule it,
retry it, and give visibility into what ran. Writing that scheduling and
retry machinery by hand is a well-known way to spend all the effort on plumbing
rather than on the actual sorting logic.

The bespoke parts — classification, retention decisions, content extraction —
will need real code regardless. So the engine's job is orchestration, not logic.

## Decision

Use n8n, self-hosted via Docker, as the execution engine. Bespoke logic lives in
code nodes; n8n supplies scheduling, retries, and run history.

Marked **proposed** rather than accepted: this should be confirmed by actually
building the first Collection duty on it. If n8n's IMAP handling turns out to be
awkward for this workload, that is worth finding out early, and the pipeline
logic should stay portable enough to move.

## Consequences

- Native IMAP and RSS nodes cover the transport work, and RSS matters for the
  deferred feed-reader direction without committing to it now.
- Run history and retries come free, which is most of what "visibility into what
  ran" means in practice.
- **Licensing:** n8n is under the Sustainable Use License — source-available
  "fair-code", *not* OSI open source. Free for personal self-hosted use, which is
  exactly this. The restriction bites only if this were ever resold as a hosted
  service for others. Worth knowing before anyone suggests productising it.
- n8n's recent AI-orchestration marketing pivot is noted and consciously set
  aside. The underlying automation core is unaffected and none of the AI features
  need touching.
- Keep the bespoke logic in code nodes that are testable outside n8n where
  possible. Logic trapped in a visual workflow is logic that cannot be unit
  tested, and the traceability guard needs tests to claim scenarios.
- The Counter is built separately, custom. n8n's own workflow editor is for
  editing workflows, not for triaging the Dead Letter Office.

## Alternatives considered

- **Node-RED.** Foundation-governed with no commercial angle, which is
  attractive, but less mature at content handling.
- **ActivePieces.** Properly MIT-licensed, which sidesteps the fair-code caveat
  entirely, but newer and less proven.
- **Huginn.** MIT, and the original of the category, but slow-moving — no major
  release since around 2022.
- **Hand-rolled scheduler (cron plus scripts).** Fewest dependencies and total
  control; loses run history, retries, and visibility, all of which would then
  need building.
