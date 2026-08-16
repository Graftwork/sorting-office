"""The mechanical half of "context is not content".

A credential reaching a commit is the one part of that promise a machine can
keep, and it is kept by a pre-commit hook rather than by the suite. The suite
cannot run git hooks, so what it checks is that the wiring is present and pinned
— if the hook is removed or its pin floats, this test fails and the scenario
stops being covered.

The config is read as text rather than parsed, to avoid adding a YAML dependency
for one assertion. See openspec/specs/foundation/spec.md, "Context Is Not
Content", and the change archived at
openspec/changes/archive/2026-08-16-context-is-not-content/.
"""

import re
from pathlib import Path

import pytest

CONFIG = Path(__file__).resolve().parent.parent / ".pre-commit-config.yaml"

SCANNER_REPO = "https://github.com/Yelp/detect-secrets"
SCANNER_HOOK = "detect-secrets"


@pytest.mark.spec("foundation/a-commit-carrying-a-credential-is-refused")
def test_a_secret_scanner_runs_before_every_commit():
    config = CONFIG.read_text(encoding="utf-8")

    assert SCANNER_REPO in config, (
        f"{CONFIG.name} no longer configures a secret scanner. "
        "Committed artifacts carrying credentials is a promise in the foundation "
        "spec; removing the hook silently drops it."
    )
    assert f"id: {SCANNER_HOOK}" in config, (
        f"the {SCANNER_REPO} repo is present but its `{SCANNER_HOOK}` hook is not enabled"
    )


def test_the_secret_scanner_is_pinned_to_an_exact_revision():
    """A floating pin would let the check change under us without a commit."""
    config = CONFIG.read_text(encoding="utf-8")

    block = config.split(SCANNER_REPO, 1)[1]
    rev = re.search(r"^\s*rev:\s*(\S+)", block, re.MULTILINE)

    assert rev, f"no `rev:` pinned for {SCANNER_REPO}"
    assert re.fullmatch(r"v\d+\.\d+\.\d+", rev.group(1)), (
        f"{SCANNER_REPO} is pinned to {rev.group(1)!r}, which is not an exact "
        "release tag. The toolchain is pinned everywhere else for the same reason."
    )
