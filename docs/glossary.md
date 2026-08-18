# Glossary

Sorting Office uses **postal-era terminology throughout** — domain concepts,
module names, and labels in the admin UI. This is deliberate, not decoration:
the operations of a real sorting office map unusually well onto what this
pipeline does, and the vocabulary gives otherwise-awkward concepts (normalising
a message, say) a genuinely expressive name. See
[ADR 0006](decisions/0006-postal-terminology.md).

If you are adding a concept, look for the postal term first.

## The vocabulary

| Concept | Term | Origin |
| --- | --- | --- |
| The upstream account mail is collected from | **Postbox** | What the collection round empties |
| Pulling messages from a source | **Collection** | Emptying a postbox |
| Normalising to a canonical format | **Facing** | Orienting every item the same way for the next machine |
| Pre-filtering or separating awkward items | **Culling** | From the Culler Facer Canceller machine |
| A category / retention grouping | **Walk** | A postman's delivery round — a named set handled together |
| Unrecognised addresses awaiting triage | **Dead Letter Office** | The department for undeliverable mail |
| A wrongly classified message | **Miss-sort** | Royal Mail slang, still in use |
| Keep-until-read retention | **Poste restante** | Mail held at the office until called for |
| The admin UI | **The Counter** | The public-facing part of the office |
| A scheduled pipeline run | **Duty** (a shift's work) or **Dispatch** (a batch sent onward) | |
| A batch of messages | **Sack** / **Mailbag** | Self-explanatory |
| Ingestion timestamp | **Postmark** | The mark applied on acceptance |
| Marking as processed | **Cancellation** | What the canceller does so a stamp can't be reused |
| Removing a message under a retention rule | **Pruning** | |
| How many of the newest to keep on a walk | **Keep-recent** | |

## Four cautions

**No mail provider is named in this repo.** The upstream account is *the
postbox*, and it is reached over plain IMAP
([ADR 0009](decisions/0009-provider-agnostic-collection.md)). Whatever a
particular provider needs to expose IMAP is deployment configuration on the mini
PC, not something this codebase knows about.

**Pruning never means deleting.** Retention prunes by moving a message to a local
Trash folder, and has no way to express a delete
([ADR 0008](decisions/0008-pruning-moves-to-trash.md)). Anywhere that needs to
mean genuinely gone has to say so in those words. Note also that two Trashes
appear in the story — the postbox's, which backstops the sweeper clearing
collected mail, and the local one, which backstops retention.

**Dead Letter Office.** "Dead letter queue" already has a precise meaning in
messaging: failed or undeliverable messages needing intervention. The usage here
is close enough that it reads as a feature rather than a clash — but readers will
import that meaning, so be explicit when the distinction matters.

**Never use "Sieve" as an internal name**, however tempting the metaphor. In this
exact domain it means the RFC 5228 mail filtering language, which this project
[considered and ruled out](decisions/0008-sieve-ruled-out.md); reusing the word
internally would confuse anyone reading the repo. For the same reason, avoid
`pigeonhole` — that is Dovecot's Sieve implementation.
