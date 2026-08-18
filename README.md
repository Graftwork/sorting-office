# Sorting Office

[![CI](https://github.com/Graftwork/sorting-office/actions/workflows/ci.yml/badge.svg)](https://github.com/Graftwork/sorting-office/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/Graftwork/sorting-office/branch/main/graph/badge.svg)](https://codecov.io/gh/Graftwork/sorting-office)

Marketing and newsletter email accumulates faster than it gets cleaned up.
Filters already sort incoming mail into folders, but nothing prunes what lands
there, so the inbox falls further behind every week. Some of it is genuinely
wanted — the problem is retention and format, not simply deletion.

Sorting Office is a pipeline that collects that mail, decides how long each
message is worth keeping, and clears the rest.

> **This repo is also a case study.** It is part of the Graftwork initiative on
> how a Product Owner can work effectively with tools like Claude Code. The
> journey — including dead ends and changes of direction — is part of the point,
> so decisions are recorded with their reasoning in
> [`docs/decisions/`](docs/decisions/) rather than tidied away after the fact.
> [ADR 0004](docs/decisions/0004-sieve-ruled-out.md) is a good example: an option
> that would have deleted the entire architecture, and why it lost.

## Status

**In design, at 0.0.0.** The decisions are recorded and the foundation is
grafted and green. No pipeline code yet — what each version number will mean is
set out in [`docs/RELEASING.md`](docs/RELEASING.md), and 0.0.x means nothing runs
end to end.

This repository was rebuilt from a clean graft of
[Graftwork Stock](https://github.com/Graftwork/stock) v0.3.0-rc.1. The reason is
worth reading rather than skipping: personal detail supplied as *context* while
scoping the work ended up written into a spec, then into code, then pushed — and
git history is rewritten rather than edited. Stock v0.3.0 carries the mechanism
that stops that happening again, and this repository is the first to start from
it. See [Context is not content](WORKFLOW.md#context-is-not-content).

## Shape of the solution

Three stages, deliberately separate rather than one monolith:

1. **Collection** — pull messages from a source. v1 is a single IMAP collector
   emptying **the postbox**, the upstream mail account. It speaks plain IMAP and
   names no provider ([ADR 0009](docs/decisions/0009-provider-agnostic-collection.md)),
   which also means it can be tested against a throwaway IMAP server. Other
   sources (RSS, chat relays) are *not* being built, but the shape shouldn't
   exclude them.
2. **Facing** — classify each message and normalise it to a canonical format.
3. **Dispatch** — write the result somewhere it can be read, archived, or deleted.

It isn't purely one-directional. Several retention behaviours need state read
back from the far end — was this read? has a newer one superseded it? — and fed
into later decisions. It is a reconciliation loop layered over a pipeline, not a
run-once flow.

## How it's put together

The design choice that shapes everything else: **only a small, low-privilege
sweeper ever touches the postbox.** It relays two already-sorted folders into a
local mailbox and clears them. Every piece of real logic — classification,
retention, the admin UI — runs against that local mailbox instead.
([ADR 0002](docs/decisions/0002-two-tier-sweeper.md))

| Decision | Where |
| --- | --- |
| Runs on the always-on mini PC, Tailscale-only | [ADR 0001](docs/decisions/0001-where-it-runs.md) |
| Only a low-privilege sweeper touches the postbox | [ADR 0002](docs/decisions/0002-two-tier-sweeper.md) |
| A real local IMAP mailbox, not a bespoke store | [ADR 0003](docs/decisions/0003-real-local-mailbox.md) |
| Server-side Sieve filtering ruled out | [ADR 0004](docs/decisions/0004-sieve-ruled-out.md) |
| n8n as the execution engine | [ADR 0005](docs/decisions/0005-n8n-execution-engine.md) |
| Postal-era terminology throughout | [ADR 0006](docs/decisions/0006-postal-terminology.md) |
| Walk rules in a database, not in this repo | [ADR 0007](docs/decisions/0007-rules-in-a-database.md) |
| Pruning moves to Trash, never deletes | [ADR 0008](docs/decisions/0008-pruning-moves-to-trash.md) |
| Collection is IMAP-agnostic; no provider named | [ADR 0009](docs/decisions/0009-provider-agnostic-collection.md) |

## Retention

Not "days per category", but a small set of **behaviours** a message can have:

| Behaviour | Applies to | Rule |
| --- | --- | --- |
| Keep-recent | Daily headlines, general marketing | Keep the newest *n* (one by default); a new arrival supersedes the rest, read or not |
| Poste restante (keep-until-read) | Comics, reviews, commentary | Untouched while unread; fair game once opened |
| Timer | Delivery notifications | Fixed short shelf life, seven days unless the walk says otherwise |
| Keep indefinitely | Purchase confirmations | Never auto-pruned |

**Pruning moves a message to Trash; it never deletes**
([ADR 0008](docs/decisions/0008-pruning-moves-to-trash.md)). A wrong rule, a
mistaken behaviour or an accidental open costs a drag back rather than a restore.

The address domain is a catch-all, so new addresses appear the moment they're
typed into a signup form, with nothing to hook into. Unrecognised addresses must
therefore be handled gracefully by default and logged to the **Dead Letter
Office** for batch triage — never a per-signup chore.

## Vocabulary

The codebase uses postal-era terminology throughout — *collection*, *facing*,
*culling*, *walks*, *poste restante*, *the Counter*. This is deliberate and the
mapping is unusually good; see the [glossary](docs/glossary.md) before naming
anything new.

## Getting started

```bash
mise trust          # once per clone — mise won't run an untrusted config
mise install && uv sync
mise run check      # lint + tests
```

## How this project is verified

Behaviour is described in plain English as scenarios under
[`openspec/specs/`](openspec/specs/), and every scenario must be claimed by a
test:

```python
@pytest.mark.spec("<capability>/<slugified-scenario-title>")
def test_something(): ...
```

`mise run trace` checks both directions — a scenario nobody tests, and a test
claiming a scenario that doesn't exist — so the link between what was promised
and what is actually checked can't quietly rot. A promise no test can keep is
declared, in writing, with its reason.

[`docs/UAT.md`](docs/UAT.md) holds the checks that need a person. Case 4 — *the
artifacts read clean to a stranger* — is the one that runs before every commit,
and it is the check this repository exists to institutionalise.

## Out of scope for the first release

Recorded so the boundaries are deliberate rather than forgotten:

- **Message-level classification for mixed-purpose senders.** One address can
  carry order confirmations, shipping updates and promos. Address-level rules
  can't disambiguate that, and the alternative is inherently heuristic. The first
  release does address-level rules well with a conservative fallback.
- **Tracker stripping and reader-mode reformatting.** A bad delete is obvious and
  recoverable from Trash; a bad content rewrite mangles things silently. Both are
  later, handled carefully.
- **RSS and social sources**, and **any reading UI**.

## Grafted from Stock

Grafted from [Graftwork Stock](https://github.com/Graftwork/stock) at
`v0.3.0-rc.1`, currently synced to `v0.3.0-rc.2`; the version is recorded in
`pyproject.toml` under `[tool.graftwork]`. To re-sync, read Stock's CHANGELOG
forward from there and apply each entry as a small PR.
