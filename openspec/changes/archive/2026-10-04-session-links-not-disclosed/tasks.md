## 1. The guard

- [x] 1.1 Add `scripts/check_no_session_link.py`, carried verbatim from Stock `v0.6.0-rc.1`
- [x] 1.2 Add `tests/test_check_no_session_link.py`, carried verbatim; the two commit-message tests claim *A commit message containing a coding-session link is refused*

## 2. The hook

- [x] 2.1 Add the `no-session-link` hook (stage `commit-msg`) and `default_install_hook_types: [pre-commit, commit-msg]` to `.pre-commit-config.yaml`
- [x] 2.2 Confirm a plain `pre-commit install` installs the `commit-msg` stage, and that the hook refuses a message with a link and accepts a clean one

## 3. Declare and document

- [x] 3.1 Declare *A pull request or issue contains no session link* as a gap in `[tool.graftwork.traceability]`, with Stock's written reason
- [x] 3.2 Add the "Never link the coding session" house rule to `CLAUDE.md`

## 4. Verify and archive

- [x] 4.1 Run ruff, pytest and the traceability guard; the guard should read 35/39 claimed with 4 allowed without one
- [x] 4.2 Run `openspec validate --all`
- [x] 4.3 Archive the change so the requirement is written into `openspec/specs/foundation/spec.md`
