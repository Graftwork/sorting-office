# Design

All measurements quoted in this document were taken from real command output,
not derived on paper. Commands are named where a number appears.

## The window

The exposure is not "the agent knows something sensitive" — that is unavoidable
and fine, the person said it on purpose. The exposure is the moment a detail
crosses from conversation into a file that will be committed.

```
conversation   →   proposal   →   design   →   spec   →   code   →   commit   →   remote
    ^                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^                  ^
    │                    the window: every one of these is a copy              │
 safe: nothing                                                       past here the only
 is written                                                          honest remedy is to
                                                                     rebuild the repo
```

Two consequences follow, and they drive the whole design:

1. **The control has to sit at the crossing, not at the end.** A review before
   the PR is already too late if a commit was made an hour earlier — the detail
   is in history, and history is rewritten rather than edited.
2. **The crossing is a judgement, not a pattern.** "<a real person's name and
   what they email me about>" and "messages from a named correspondent on a
   weekly cadence" are the same requirement. No matcher distinguishes them; a
   person reading the sentence does so instantly.

   That placeholder is deliberate. The first draft of this document illustrated
   the point with a realistic-looking name and detail, which UAT case 4 caught
   before the commit — a plausible personal detail inside a document about not
   writing personal details down is indistinguishable, to a later reader, from a
   real one that leaked.

## What can and cannot be enforced

Splitting this honestly is the main design decision. Blurring it would be worse
than not having it, because a green hook reads as "checked" and this is exactly
the class of promise where a false sense of coverage is dangerous.

| Concern | Enforceable? | How |
| --- | --- | --- |
| API keys, tokens, high-entropy strings | Yes | `detect-secrets` pre-commit hook |
| A person's name, condition, address, relationship | No | Review policy — declared gap |
| Whether a specific is load-bearing or incidental | No | Review policy — declared gap |

The machine half is worth having even though it is the smaller half: it is free,
it runs before the commit rather than after, and credentials are the one category
where the damage is immediate rather than merely permanent.

## Choosing the secret scanner

Two candidates were tested rather than assumed.

**`gitleaks` — rejected.** Its hook definition declares `language: golang`
(measured: `curl .../gitleaks/master/.pre-commit-hooks.yaml`). Stock's
`[tools]` block pins `python`, `uv` and `node` and no Go, so adopting it means
adding a language runtime to the pinned toolchain for one hook. The
`gitleaks-docker` variant trades that for a Docker dependency. Neither is
proportionate.

**`Yelp/detect-secrets` — chosen.** Its hook declares `language: python`, which
pre-commit provisions itself. No change to `mise.toml`, no new runtime.

Latest release measured at **v1.5.0** —
`git ls-remote --tags --refs https://github.com/Yelp/detect-secrets | sort -V | tail`.
Note that `git ls-remote` orders lexicographically; the first attempt at this
number was wrong for exactly that reason, and `sort -V` is what corrected it.

**Behaviour verified, both directions**, because a guard that cannot fail is not
a guard ([Stock ADR 0004](../../../../docs/decisions/stock-0004-spec-traceability-guard.md)):

```
$ uvx pre-commit run detect-secrets --all-files
Detect secrets...........................................................Passed

$ # with a planted AWS example key in a scratch file
Secret Type: Base64 High Entropy String
Secret Type: Secret Keyword
```

Two detectors fired on the planted credential; the real repository is clean.

**No baseline file.** `detect-secrets` is commonly wired with
`--baseline .secrets.baseline`, which requires generating and committing that
file. Stock passes without one and has no false positives to suppress, so adding
it now would be ceremony for a problem that does not exist yet — the
"keep it unspeculative" rule. A project adds a baseline the day it gets its
first false positive; until then `pragma: allowlist secret` handles one-offs.

## Why a spec requirement rather than only documentation

A convention in `WORKFLOW.md` is advice. A requirement in `openspec/specs/` is a
promise that appears in the traceability report, has to be either tested or
declared with a written reason, and travels into every grafted project as part of
the foundation's contract.

Declaring the two review-policy scenarios as gaps is not a way to avoid testing
them. It is a written claim, reviewable, that no test could keep these promises —
and the guard checks the claim itself: a reason is mandatory, a declaration
naming a scenario that no longer exists fails, and a declaration for a gap a test
has since closed fails
([Stock ADR 0005](../../../../docs/decisions/stock-0005-declared-gaps-in-traceability.md)).

## Alternatives considered

- **Documentation only, no spec change.** Cheapest, and it would have been
  invisible. The point of putting it in the spec is that a grafted project
  inherits it as a promise rather than as a paragraph someone may not read.
- **Block the agent from ever writing specifics.** Unworkable and wrong — some
  specifics are the requirement. The control is confirmation, not prohibition.
- **A pattern matcher for personal data** (names, addresses, health terms).
  Rejected: it would be wrong in both directions, and its real cost is that a
  green run would read as "no personal data present", which is precisely the
  false assurance this design is trying to avoid.
- **Scan history rather than the staged change.** Catches what is already
  committed, which is the case where the remedy is a rebuild anyway. The hook
  runs pre-commit because that is the last moment the cheap fix exists.
