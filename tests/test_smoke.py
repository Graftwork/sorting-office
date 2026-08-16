"""Proof that the test harness itself runs.

This is the test that makes "green from commit one" true: on a freshly stamped
project there is no source code yet, but the suite still has something real to
say — the toolchain is wired up and the runner works.
"""

import sys

import pytest


@pytest.mark.spec("foundation/a-freshly-stamped-project-passes-its-test-suite")
def test_harness_runs_on_a_supported_python():
    assert sys.version_info >= (3, 13)
