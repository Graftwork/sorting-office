"""The review check's final step, run for real against a fake GitHub.

The workflow's last step decides whether a green tick on a pull request may be
believed. Its rules live as shell inside `.github/workflows/claude-review.yml`,
so these tests read that step out of the file and run it with `bash`, with a
fake `gh` on `PATH` and a fake execution file. Nothing here copies the logic: a
test passes only if the workflow's own script does what the requirement says.

Because the step is read out of the workflow, moving it, renaming its `id`, or
changing how its inputs arrive means updating this file. The extractor fails
loudly when it cannot find exactly one step, so that never looks like a pass.

What this does not check is the live review: whether the plugin follows its
prompt (the "No reviewable changes" note, reviewing again after a push) is
behaviour of a model, and is checked on real runs instead.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

WORKFLOW = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "claude-review.yml"

STARTED_AT = "2026-10-05T10:00:00Z"
BEFORE = "2026-10-05T09:00:00Z"
AFTER = "2026-10-05T10:05:00Z"

FAKE_GH = """#!/usr/bin/env bash
set -euo pipefail
endpoint=""
filter=""
args=("$@")
for ((i = 0; i < ${#args[@]}; i++)); do
  case "${args[i]}" in
    repos/*) endpoint="${args[i]}" ;;
    --jq) filter="${args[i + 1]}" ;;
  esac
done
case "$endpoint" in
  */issues/*/comments) file=issue_comments.json ;;
  */pulls/*/comments) file=review_comments.json ;;
  */pulls/*/reviews) file=reviews.json ;;
  */pulls/*/files) file=files.json ;;
  *) echo "fake gh: unexpected endpoint: $endpoint" >&2; exit 1 ;;
esac
if [ -n "$filter" ]; then
  jq -r "$filter" "$FAKE_GH_DIR/$file"
else
  cat "$FAKE_GH_DIR/$file"
fi
"""


def gate_step() -> tuple[str, dict[str, str]]:
    """Return the gate's script and the literal values of its `env:` block.

    The step is the one with `id: gate`. Its `run: |` block is cut out by
    indentation, which avoids a YAML dependency; every input to the script
    arrives through `env:`, so it needs no other preparation.
    """
    lines = WORKFLOW.read_text(encoding="utf-8").split("\n")
    ids = [i for i, line in enumerate(lines) if re.fullmatch(r"\s+id: gate\s*", line)]
    assert len(ids) == 1, f"expected exactly one step with `id: gate`, found {len(ids)}"
    start = ids[0]

    env_at = next(i for i in range(start, len(lines)) if re.fullmatch(r"\s+env:\s*", lines[i]))
    run_at = next(i for i in range(start, len(lines)) if re.fullmatch(r"\s+run: \|\s*", lines[i]))

    env: dict[str, str] = {}
    for line in lines[env_at + 1 : run_at]:
        match = re.fullmatch(r"\s+([A-Z_]+): (.+?)\s*", line)
        if match and "${{" not in match.group(2):
            env[match.group(1)] = match.group(2)

    first = lines[run_at + 1]
    indent = len(first) - len(first.lstrip())
    body: list[str] = []
    for line in lines[run_at + 1 :]:
        if line.strip() and len(line) - len(line.lstrip()) < indent:
            break
        body.append(line[indent:] if line.strip() else "")
    script = "\n".join(body).rstrip() + "\n"
    assert script.strip(), "the gate step has an empty `run:` block"
    return script, env


def comment(login: str, body: str, at: str = AFTER) -> dict:
    return {"user": {"login": login}, "body": body, "created_at": at}


def review(login: str, body: str, at: str = AFTER) -> dict:
    return {"user": {"login": login}, "body": body, "submitted_at": at}


def denial(tool: str, **tool_input: str) -> dict:
    return {"tool_name": tool, "tool_input": tool_input}


def bash_denial(command: str) -> dict:
    return denial("Bash", command=command)


class Gate:
    """A fake pull request, its comments, and one run of the gate over it."""

    def __init__(self, tmp_path: Path):
        self.dir = tmp_path
        self.bot = gate_step()[1]["REVIEW_BOT"]
        self.issue_comments: list[dict] = []
        self.review_comments: list[dict] = []
        self.reviews: list[dict] = []
        self.files = ["src/app.py"]
        self.is_error = False
        self.denials: list[dict] = []
        self.write_execution_file = True
        self.workflow_edited = False

    def run(self) -> subprocess.CompletedProcess[str]:
        script, env = gate_step()
        assert shutil.which("bash"), "these tests need bash"
        assert shutil.which("jq"), "these tests need jq (it is on ubuntu-latest and in dev setups)"

        d = self.dir
        (d / "bin").mkdir()
        fake = d / "bin" / "gh"
        fake.write_text(FAKE_GH, encoding="utf-8")
        fake.chmod(0o755)

        api = d / "api"
        api.mkdir()
        (api / "issue_comments.json").write_text(json.dumps(self.issue_comments))
        (api / "review_comments.json").write_text(json.dumps(self.review_comments))
        (api / "reviews.json").write_text(json.dumps(self.reviews))
        (api / "files.json").write_text(json.dumps([{"filename": f} for f in self.files]))

        for where, text in (
            (".github/workflows", "name: review\n"),
            (
                "pr-head/.github/workflows",
                "name: review\n# edited\n" if self.workflow_edited else "name: review\n",
            ),
        ):
            (d / where).mkdir(parents=True)
            (d / where / "claude-review.yml").write_text(text, encoding="utf-8")

        execution = d / "execution.json"
        if self.write_execution_file:
            result = {
                "type": "result",
                "is_error": self.is_error,
                "num_turns": 5,
                "permission_denials": self.denials,
                "permission_denials_count": len(self.denials),
            }
            execution.write_text(json.dumps([{"type": "system"}, result]))

        script_path = d / "gate.sh"
        script_path.write_text(script, encoding="utf-8")
        env = {
            **env,
            # The fake gh goes first; the rest of PATH is the real one, so the
            # bash and jq checked above are the ones the script finds.
            "PATH": f"{d / 'bin'}:{os.environ.get('PATH', '')}",
            "FAKE_GH_DIR": str(api),
            "GH_TOKEN": "unused",
            "REPO": "owner/repo",
            "PR_NUMBER": "7",
            "STARTED_AT": STARTED_AT,
            "EXECUTION_FILE": str(execution),
            "GITHUB_STEP_SUMMARY": str(d / "summary.md"),
            "GITHUB_OUTPUT": str(d / "output.txt"),
        }
        for name in ("summary.md", "output.txt"):
            (d / name).write_text("")
        return subprocess.run(
            ["bash", str(script_path)],
            cwd=d,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    @property
    def summary(self) -> str:
        return (self.dir / "summary.md").read_text(encoding="utf-8")

    @property
    def output(self) -> str:
        return (self.dir / "output.txt").read_text(encoding="utf-8")


@pytest.fixture
def gate(tmp_path: Path) -> Gate:
    return Gate(tmp_path)


def errors(result: subprocess.CompletedProcess[str]) -> list[str]:
    return [line for line in result.stdout.splitlines() if line.startswith("::error")]


def test_the_extractor_finds_the_gate_and_its_constants():
    script, env = gate_step()

    assert "gh api" in script
    assert env["REVIEW_BOT"] == "claude[bot]"
    assert env["SENTINEL"] == "No reviewable changes"


@pytest.mark.spec("foundation/a-review-that-was-posted-passes-the-check")
@pytest.mark.parametrize("where", ["issue_comments", "review_comments", "reviews"])
def test_a_review_that_was_posted_passes(gate, where):
    if where == "reviews":
        gate.reviews = [review(gate.bot, "Found a bug in app.py line 3.")]
    else:
        setattr(gate, where, [comment(gate.bot, "Found a bug in app.py line 3.")])

    result = gate.run()

    assert result.returncode == 0, result.stdout + result.stderr
    assert errors(result) == []


@pytest.mark.spec("foundation/a-run-that-posted-nothing-fails-the-check")
@pytest.mark.parametrize("earlier", [False, True], ids=["no comments", "only an older comment"])
def test_a_run_that_posted_nothing_fails(gate, earlier):
    if earlier:
        gate.issue_comments = [comment(gate.bot, "An earlier review.", at=BEFORE)]
    gate.denials = [denial("Skill", skill="code-review:code-review")]

    result = gate.run()

    assert result.returncode == 1
    message = "".join(errors(result))
    assert "posted nothing" in message
    assert "1 tool call(s) were denied" in message
    assert "Skill: code-review:code-review" in message
    assert "No review happened" in gate.summary


@pytest.mark.spec("foundation/a-run-that-reports-an-error-fails-the-check")
def test_a_run_that_reports_an_error_fails(gate):
    gate.is_error = True
    gate.issue_comments = [comment(gate.bot, "A review was posted.")]

    result = gate.run()

    assert result.returncode == 1
    assert "is_error" in "".join(errors(result))


@pytest.mark.spec("foundation/a-pull-request-that-edits-the-review-workflow-fails-the-check")
def test_a_pull_request_that_edits_the_review_workflow_fails(gate):
    gate.workflow_edited = True
    gate.issue_comments = [comment(gate.bot, "A review was posted.")]

    result = gate.run()

    assert result.returncode == 1
    message = "".join(errors(result))
    assert "edits claude-review.yml" in message
    assert "by hand" in message


@pytest.mark.spec("foundation/a-denied-tool-call-only-warns")
@pytest.mark.parametrize(
    "denied",
    [
        [bash_denial("gh pr diff 7"), bash_denial("git ls-tree -r HEAD")],
        [denial("Skill", skill="code-review:code-review")],
        [denial("mcp__github_inline_comment__create_inline_comment", path="a.py")],
        [bash_denial("gh pr comment 7 --body hello")],
        [bash_denial("python3 - <<'EOF'\nprint('gh pr comment 7 --body hello')\nEOF")],
    ],
    ids=["exploratory", "Skill", "inline comment", "gh pr comment", "quotes gh pr comment"],
)
def test_a_denied_tool_call_only_warns(gate, denied):
    gate.denials = denied
    gate.issue_comments = [comment(gate.bot, "A review was posted.")]

    result = gate.run()

    assert result.returncode == 0, result.stdout + result.stderr
    assert errors(result) == []
    assert "::warning title=Tool calls were denied" in result.stdout
    assert gate.output.startswith("denied=")
    assert gate.output.strip() != "denied="
    assert gate.output.strip().removeprefix("denied=") in gate.summary


@pytest.mark.spec("foundation/a-declined-review-passes-only-for-a-markdown-only-pull-request")
@pytest.mark.parametrize(
    ("files", "passes"),
    [
        (["README.md", "docs/guide.MD"], True),
        (["README.md", "src/app.py"], False),
        (["Makefile"], False),
    ],
    ids=["Markdown only", "code as well", "no extension"],
)
def test_a_declined_review_passes_only_for_markdown(gate, files, passes):
    gate.files = files
    gate.issue_comments = [comment(gate.bot, "No reviewable changes: documentation only.")]

    result = gate.run()

    if passes:
        assert result.returncode == 0, result.stdout + result.stderr
        assert "declined" in gate.summary
    else:
        assert result.returncode == 1
        assert "other than Markdown" in "".join(errors(result))


@pytest.mark.spec("foundation/comments-by-anyone-but-the-review-bot-do-not-count")
@pytest.mark.parametrize("login", ["github-actions[bot]", "a-person", "claude"])
def test_comments_by_anyone_but_the_review_bot_do_not_count(gate, login):
    gate.issue_comments = [comment(login, "Looks fine to me.")]
    gate.reviews = [review(login, "Approved.")]

    result = gate.run()

    assert result.returncode == 1
    assert "posted nothing" in "".join(errors(result))


def test_no_execution_file_fails(gate):
    gate.write_execution_file = False
    gate.issue_comments = [comment(gate.bot, "A review was posted.")]

    result = gate.run()

    assert result.returncode == 1
    assert "no execution file" in "".join(errors(result))


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("evil%0A::warning::injected.py", "evil0A::warning::injected.py"),
        ("odd\rna\x07me.py", "oddname.py"),
    ],
    ids=["percent escape", "control characters"],
)
def test_a_file_name_cannot_inject_a_workflow_command(gate, name, expected):
    # `%0A` in a workflow command's message is decoded to a newline by Actions,
    # so a file name that carries it could start a new command; control
    # characters could do the same. Both are stripped before the name is printed.
    gate.files = ["notes.md", name]
    gate.issue_comments = [comment(gate.bot, "No reviewable changes: documentation only.")]

    result = gate.run()

    assert result.returncode == 1
    (message,) = errors(result)
    assert f"(first: {expected})" in message
    assert "%" not in message
    assert not any(ch in result.stdout for ch in "\r\x07")


def test_a_denied_command_is_collapsed_onto_one_line_and_made_safe(gate):
    gate.denials = [bash_denial("echo one\ntwo   three\tfour `date` 100%0A")]
    gate.issue_comments = [comment(gate.bot, "A review was posted.")]

    result = gate.run()

    assert result.returncode == 0, result.stdout + result.stderr
    assert gate.output == "denied=Bash: echo one two three four _date_ 100_0A\n"


def test_the_denied_list_is_capped(gate):
    gate.denials = [
        bash_denial("gh api repos/owner/repo/pulls/7 " + "x" * 80 + f" {n}") for n in range(20)
    ]
    gate.issue_comments = [comment(gate.bot, "A review was posted.")]

    result = gate.run()

    assert result.returncode == 0, result.stdout + result.stderr
    assert gate.output.count("\n") == 1
    assert len(gate.output.rstrip("\n")) <= len("denied=") + 400
