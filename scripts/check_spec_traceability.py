#!/usr/bin/env python3
"""Spec traceability guard.

The contract between the plain-English review layer and the code layer: every
scenario written in an OpenSpec spec must be claimed by at least one test, and
every claim a test makes must name a scenario that actually exists.

Scenarios are read from ``openspec/specs/<capability>/spec.md`` — the layout the
OpenSpec CLI produces — where they appear as ``#### Scenario: <title>`` headings.
Each one gets an id of ``<capability>/<slugified-title>``.

Tests claim a scenario with a pytest marker::

    @pytest.mark.spec("foundation/every-scenario-is-claimed-by-a-test")
    def test_something():
        ...

Claims are found by parsing the test files' syntax tree, so this never imports
or executes test code.

Some scenarios genuinely cannot be claimed by a test — a review policy, or a
promise about something outside the suite's reach. Those are declared in
``pyproject.toml`` with the reason written down::

    [tool.graftwork.traceability]
    unclaimed = [
        { scenario = "foundation/...", reason = "review policy, not runtime-checkable" },
    ]

The reason is mandatory, and the declaration is itself checked: an entry with no
reason, an entry naming a scenario that does not exist, and an entry for a
scenario a test now claims are all reported. "We cannot test this" stays honest
only while it is written down and kept current.

Run it directly (``python scripts/check_spec_traceability.py``) or let the test
suite run it — both report the same thing.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
import tomllib
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

SCENARIO_HEADING = re.compile(r"^####\s+Scenario:\s*(.+?)\s*$")
REQUIREMENT_HEADING = re.compile(r"^###\s+Requirement:\s*(.+?)\s*$")

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS_DIR = REPO_ROOT / "openspec" / "specs"
TESTS_DIR = REPO_ROOT / "tests"
PYPROJECT = REPO_ROOT / "pyproject.toml"


def slugify(title: str) -> str:
    """Turn a scenario title into the stable part of its id."""
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower())
    return slug.strip("-")


@dataclass(frozen=True)
class Scenario:
    """A scenario declared in a spec."""

    id: str
    title: str
    requirement: str
    source: Path
    line: int


@dataclass(frozen=True)
class Claim:
    """A test's claim that it covers a scenario."""

    scenario_id: str
    test_name: str
    source: Path
    line: int


@dataclass(frozen=True)
class Allowed:
    """A scenario deliberately left unclaimed, and the written reason why."""

    scenario_id: str
    reason: str


@dataclass
class Report:
    """The result of checking claims against scenarios."""

    scenarios: list[Scenario] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)
    allowed: list[Allowed] = field(default_factory=list)
    unclaimed: list[Scenario] = field(default_factory=list)
    unknown: list[Claim] = field(default_factory=list)
    unexplained: list[Allowed] = field(default_factory=list)
    orphaned: list[Allowed] = field(default_factory=list)
    redundant: list[Allowed] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (
            self.unclaimed or self.unknown or self.unexplained or self.orphaned or self.redundant
        )

    def summary(self) -> str:
        claimed_ids = {claim.scenario_id for claim in self.claims}
        claimed = sum(1 for scenario in self.scenarios if scenario.id in claimed_ids)
        line = f"{claimed}/{len(self.scenarios)} scenarios claimed by tests"
        if self.allowed:
            line += f", {len(self.allowed)} allowed without one"
        return line


def find_scenarios(specs_dir: Path = SPECS_DIR) -> list[Scenario]:
    """Collect every scenario declared under ``specs_dir``."""
    scenarios: list[Scenario] = []
    if not specs_dir.is_dir():
        return scenarios

    for spec_file in sorted(specs_dir.glob("*/spec.md")):
        capability = spec_file.parent.name
        requirement = ""
        for lineno, line in enumerate(spec_file.read_text(encoding="utf-8").splitlines(), 1):
            if match := REQUIREMENT_HEADING.match(line):
                requirement = match.group(1)
            elif match := SCENARIO_HEADING.match(line):
                title = match.group(1)
                scenarios.append(
                    Scenario(
                        id=f"{capability}/{slugify(title)}",
                        title=title,
                        requirement=requirement,
                        source=spec_file,
                        line=lineno,
                    )
                )
    return scenarios


def _spec_marker_ids(decorator: ast.expr) -> list[str]:
    """Return the scenario ids named by a ``@pytest.mark.spec(...)`` decorator."""
    if not isinstance(decorator, ast.Call):
        return []
    func = decorator.func
    if not isinstance(func, ast.Attribute) or func.attr != "spec":
        return []
    # Match the `...mark.spec` shape without caring how pytest was imported.
    parent = func.value
    if not isinstance(parent, ast.Attribute) or parent.attr != "mark":
        return []
    return [
        arg.value
        for arg in decorator.args
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str)
    ]


def find_claims(tests_dir: Path = TESTS_DIR) -> list[Claim]:
    """Collect every scenario claim made by a test."""
    claims: list[Claim] = []
    if not tests_dir.is_dir():
        return claims

    for test_file in sorted(tests_dir.rglob("test_*.py")):
        tree = ast.parse(test_file.read_text(encoding="utf-8"), filename=str(test_file))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            for decorator in node.decorator_list:
                for scenario_id in _spec_marker_ids(decorator):
                    claims.append(
                        Claim(
                            scenario_id=scenario_id,
                            test_name=node.name,
                            source=test_file,
                            line=node.lineno,
                        )
                    )
    return claims


def load_allowlist(pyproject: Path = PYPROJECT) -> list[Allowed]:
    """Read the declared gaps from ``[tool.graftwork.traceability]``.

    A project with no declarations — the state a fresh graft starts in — has no
    table, and that is not an error.
    """
    if not pyproject.is_file():
        return []

    table = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    for key in ("tool", "graftwork", "traceability"):
        table = table.get(key, {}) if isinstance(table, dict) else {}
    entries = table.get("unclaimed", []) if isinstance(table, dict) else []

    allowed: list[Allowed] = []
    for position, entry in enumerate(entries, 1):
        if not isinstance(entry, dict) or "scenario" not in entry:
            raise ValueError(
                f"{_display_path(pyproject)}: unclaimed[{position}] needs a `scenario` key "
                "naming the scenario id, and a `reason` saying why no test claims it"
            )
        allowed.append(Allowed(str(entry["scenario"]), str(entry.get("reason", "")).strip()))
    return allowed


def check(
    specs_dir: Path = SPECS_DIR,
    tests_dir: Path = TESTS_DIR,
    allowed: Sequence[Allowed] | None = None,
) -> Report:
    """Check that scenarios, test claims, and declared gaps all line up.

    Passing ``allowed`` explicitly overrides the declarations in
    ``pyproject.toml``; ``[]`` checks the specs on their own.
    """
    scenarios = find_scenarios(specs_dir)
    claims = find_claims(tests_dir)
    allowed = list(load_allowlist()) if allowed is None else list(allowed)

    claimed_ids = {claim.scenario_id for claim in claims}
    known_ids = {scenario.id for scenario in scenarios}
    # An entry with no reason explains nothing, so it does not excuse anything.
    excused_ids = {entry.scenario_id for entry in allowed if entry.reason}

    return Report(
        scenarios=scenarios,
        claims=claims,
        allowed=allowed,
        unclaimed=[s for s in scenarios if s.id not in claimed_ids and s.id not in excused_ids],
        unknown=[c for c in claims if c.scenario_id not in known_ids],
        unexplained=[a for a in allowed if not a.reason],
        orphaned=[a for a in allowed if a.scenario_id not in known_ids],
        redundant=[a for a in allowed if a.scenario_id in claimed_ids],
    )


def _display_path(path: Path) -> Path:
    """Show a repo-relative path when we can, and the full path when we cannot."""
    try:
        return path.relative_to(REPO_ROOT)
    except ValueError:
        return path


def format_report(report: Report) -> str:
    """Render a report as the plain-English explanation of what is missing."""
    lines: list[str] = []

    if report.unclaimed:
        lines.append("Scenarios with no test claiming them:")
        for scenario in report.unclaimed:
            location = _display_path(scenario.source)
            lines.append(f"  {scenario.id}")
            lines.append(f'    "{scenario.title}" under "{scenario.requirement}"')
            lines.append(f"    {location}:{scenario.line}")
            lines.append(f'    fix: add @pytest.mark.spec("{scenario.id}") to a test')
        lines.append("")

    if report.unknown:
        lines.append("Tests claiming scenarios that do not exist:")
        for claim in report.unknown:
            location = _display_path(claim.source)
            lines.append(f"  {claim.scenario_id}")
            lines.append(f"    claimed by {claim.test_name}() at {location}:{claim.line}")
            lines.append("    fix: correct the id, or write the scenario in the spec")
        lines.append("")

    if report.unexplained:
        lines.append("Scenarios allowed to go unclaimed with no reason given:")
        for entry in report.unexplained:
            lines.append(f"  {entry.scenario_id}")
            lines.append("    fix: give it a `reason`, or delete the entry and write a test")
        lines.append("")

    if report.orphaned:
        lines.append("Allowed scenarios that no spec declares:")
        for entry in report.orphaned:
            lines.append(f"  {entry.scenario_id}")
            if entry.reason:
                lines.append(f'    allowed because "{entry.reason}"')
            lines.append("    fix: the scenario was renamed or removed — update or drop the entry")
        lines.append("")

    if report.redundant:
        lines.append("Allowed scenarios that a test now claims:")
        for entry in report.redundant:
            lines.append(f"  {entry.scenario_id}")
            lines.append("    fix: it is tested after all — drop the entry")
        lines.append("")

    lines.append(report.summary())
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--specs-dir", type=Path, default=SPECS_DIR)
    parser.add_argument("--tests-dir", type=Path, default=TESTS_DIR)
    parser.add_argument("--pyproject", type=Path, default=PYPROJECT)
    args = parser.parse_args(argv)

    try:
        allowed = load_allowlist(args.pyproject)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1

    report = check(args.specs_dir, args.tests_dir, allowed)
    print(format_report(report))
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
