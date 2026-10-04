#!/usr/bin/env python3
"""Refuse a commit message that links to the coding session that produced it.

Foundation's "Coding Session Links Are Not Disclosed" requirement: naming the
coding agent and model is the promise (see AI Authorship Is Disclosed); the
private session or conversation that produced a change is not the reviewer's
business, and a session link identifies more than either -- an account,
sometimes a device, always a private exchange nobody but its participants
agreed to publish.

Run as a pre-commit commit-msg hook, which passes the commit message file's
path as the sole argument.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SESSION_LINK = re.compile(r"claude\.ai/code/session", re.IGNORECASE)


def check(message: str) -> list[str]:
    """Return every line in message that links to a coding session."""
    return [line for line in message.splitlines() if SESSION_LINK.search(line)]


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("check_no_session_link: expected the commit message file path", file=sys.stderr)
        return 2

    message = Path(argv[0]).read_text(encoding="utf-8")
    offending = check(message)
    if offending:
        print("Commit message links to a coding session:", file=sys.stderr)
        for line in offending:
            print(f"  {line}", file=sys.stderr)
        print(
            "fix: remove the link -- name the coding agent and model instead, "
            "not the conversation that produced this change",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
