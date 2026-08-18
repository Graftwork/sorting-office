# ADR 0004: Server-side Sieve filtering considered and ruled out

- **Status:** accepted
- **Date:** 2026-08-12
- **Carried forward:** rewritten, not copied, when this repository was rebuilt.
  The original named a mail provider and quoted a real address pattern; the
  argument below is the same one, made without either. See
  [ADR 0009](0009-provider-agnostic-collection.md).

## Context

The mail provider supports Sieve filters, including a provider-specific expiry
action that can set a per-message expiry entirely server-side. On paper this
solves the whole problem with **no local infrastructure at all** — no mini PC, no
local mailbox, no pipeline.

An option that deletes the entire architecture deserves a serious hearing, so it
got one. This ADR records why it lost, because "why didn't you just use Sieve?"
is the obvious question for anyone reading this repo later.

## Decision

Do not use Sieve. Build the pipeline.

## Rationale

**The access method is not open, even though the language is.** Sieve is a
genuine IETF standard (RFC 5228). The provider's *way in* is not: no ManageSieve
support, no API. Rules are entered by copy-pasting into their web UI, by hand.

**The rules would need editing per new address, not per new category.** The
domain is a catch-all, so a fresh alias works the instant it is typed into a
signup form. Every new signup would mean another manual edit in a web UI. Given
the inbox is *already* falling behind, a solution whose maintenance burden grows
with every signup is not a solution.

**There is no API to automate around the gap.** As of mid-2026 the provider
offers none — still an open community request. So there is no way to push rules
programmatically, short of unofficial browser automation, which would be fragile
and would break silently on any UI change.

## Consequences

- We accept substantially more infrastructure (mini PC, local mailbox, pipeline)
  in exchange for automation that scales with new addresses instead of degrading
  with them.
- Retention rules become message-level and behaviour-based rather than a
  server-side expiry timestamp, which is what makes richer behaviours like
  keep-recent and keep-until-read possible at all — Sieve expiry could not
  express those.
- **Revisit if the provider ships an official API.** ManageSieve support or a
  rules API would make server-side expiry viable for the simple timer cases, and
  could retire part of this pipeline. Worth re-reading this ADR if that lands.
- This reasoning is about one provider's Sieve *access*, not about Sieve. A
  postbox that offers ManageSieve would deserve a fresh hearing — though the
  per-address maintenance argument above would still apply, and it is the one
  that does most of the work here.
- Do not use "sieve" as an internal name anywhere in the codebase — see the
  [glossary](../glossary.md).
