# ADR 0006: Postal-era terminology is the ubiquitous language

- **Status:** accepted
- **Date:** 2026-08-12
- **Carried forward:** written before this repository was rebuilt, and renumbered
  on the way in. The reasoning is unchanged.

## Context

The project is named for the postal sorting office metaphor. The question is
whether that stays at the level of the name, or goes all the way into the
codebase — module names, domain concepts, and the labels a user sees in the
admin UI.

Themed naming is often a mistake: cute names that obscure what code does are a
tax on every future reader. So this needs justifying rather than assuming.

## Decision

Use postal-era terminology throughout — domain concepts, module names, and
user-facing labels. The vocabulary is recorded in the
[glossary](../glossary.md), which is the reference when adding a concept.

## Consequences

- The metaphor maps unusually well, which is what makes it work here rather than
  being decoration. A real sorting office genuinely does collect, cull, face, and
  cancel; those are the actual operations of this pipeline, not strained
  analogies.
- It gives awkward concepts an expressive name. "Facing" is a far better name for
  normalising a message to a canonical format than "normaliser" or "transformer",
  and it comes with a mental image that explains *why* the step exists.
- "Poste restante" for keep-until-read has near-exact semantics — mail held at
  the office until the recipient calls for it. No invented term would be clearer.
- It is memorable, which matters for a project worked on in short bursts with
  gaps between them.
- The cost is a vocabulary to learn. The glossary exists to make that a
  five-minute read rather than an archaeology exercise, and it must be kept
  current — a stale glossary would be worse than no theme at all.
- Two terms carry a collision risk and are called out in the glossary:
  **Dead Letter Office** (against "dead letter queue") and **Sieve**, which must
  never be used internally because it means RFC 5228 in this exact domain.

## Alternatives considered

- **Plain technical naming** (`extractor`, `normaliser`, `classifier`). Instantly
  legible to any developer and completely forgettable. It also leaves the
  genuinely awkward concepts with genuinely awkward names.
- **Theme the UI only, keep the code plain.** Avoids the learning curve in code,
  but then the UI and the code use different words for the same thing — which is
  the actual cost people attribute to themed naming.
