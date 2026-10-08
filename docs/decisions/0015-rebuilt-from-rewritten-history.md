# ADR 0015: Rebuilt from rewritten history

- **Status:** accepted
- **Date:** 2026-10-08

## Context

Between August and October 2026, cloud coding sessions added a
`Claude-Session:` trailer to commit messages, each a link to the private
session that produced the commit. [`foundation`'s "Coding Session Links Are
Not Disclosed"](../../openspec/specs/foundation/spec.md) stops new ones, but
it cannot remove the ones already in history: 16 of the 26 commits on `main`
carried one, 25 trailer lines in all. Only a history rewrite removes them, and
rewriting a repository in place breaks every existing clone without telling it
why.

Stock met the same problem first and solved it this way; [Stock ADR
0017](https://github.com/Graftwork/stock/blob/main/docs/decisions/stock-0017-rebuilt-from-rewritten-history.md)
is the record there. It has not been re-synced into this project yet. This
project follows the same method.

## Decision

Publish a new repository built from rewritten history; keep the old one.

- The old repository was renamed `Graftwork/sorting-office-archive` and stays
  private. This repository took the original name.
- History is **rewritten, not squashed**: every commit is kept and only commit
  messages changed. A `Claude-Session:` line, or a line that is only a session
  link, was dropped; the blank lines that left behind were collapsed.
  `Co-Authored-By` lines were kept. Commit hashes cited inside commit messages
  were left verbatim.
- Only `main` was carried over. This project has cut no tags. Branches and
  pull-request refs were not carried over.
- **Pull request and issue numbers, and commit hashes, cited anywhere in this
  repository before 2026-10-08 refer to the archive, not to this
  repository.** They were left as written rather than edited one by one. This
  repository's own pull request numbering starts again at 1, so a `#NN` from
  before the rebuild — in a document or a commit subject — may link to an
  unrelated pull request here. Hashes of Stock commits cited here (in
  `CHANGELOG.md` and archived OpenSpec changes) refer to Stock's own archive;
  Stock ADR 0017 translates them.

Measured before the first push, against a fresh mirror of the old repository
(`git rev-list --count`, `git rev-parse main^{tree}`, `git log --format=%B |
grep`, and a per-commit comparison of `git log --format='%T %an %ae %cn %ce
%ad %cd %P'`):

| | Before | After |
|---|---|---|
| Commits on `main` | 26 | 26 |
| Commit messages with a session link | 16 | 0 |
| `Claude-Session:` lines | 25 | 0 |
| `main`'s tree | `d25f80f` | `d25f80f` |
| `Co-Authored-By` lines on `main` | 41 | 41 |
| Commits whose tree, author, committer, dates or parent count changed | — | 0 |

`main` moved from `e5fe19c` to `dfbd81b`.

The file contents of every commit are identical, so the session-link guard's
own test fixtures still contain placeholder links (`session_01ABC` and
similar); no real session id appears in any file.

Four commit messages cite a commit by hash. Three cite Stock commits. One
cites this project's own `6b3b1bf`, from the commit that wires up the
SessionStart hook. That commit was only ever on a pull request's branch,
never on `main`, so it exists only in the archive.

Every number above came from real command output.

## Consequences

- Links into the archive are dead for anyone without access to it. The
  reasoning they pointed at is kept in the documents that cite them.
- Clones of the old repository do not share history with this one. Re-clone
  rather than pull.
- `stock-version` in `pyproject.toml` records a Stock tag name, and Stock's tag
  names survived its own rebuild, so it needs no change.

## Alternatives considered

- **Rewrite the existing repository in place.** Rejected: it silently breaks
  every clone and keeps pull requests whose descriptions and branches still
  carry links.
- **Squash to one commit.** Rejected: it throws away the history the
  CHANGELOG and ADRs are written against.
- **Edit every old hash and `#NN` to point at the new repository.** Rejected:
  it cannot reach commit subjects without a further rewrite, and one dated
  note explains all of them.
