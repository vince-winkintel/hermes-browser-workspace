# Phase 2 Checkpoint

## Status

Phase 2 Safer Adaptation implemented in this repository. Phase 3 has not been started.

## What Was Implemented

- helper proposals now persist richer review metadata including `proposal_id`, timestamps, source session/task context, status, reviewer fields, decision notes, and validation state
- helper proposal utilities added for listing, reading/reviewing, and structural validation without executing untrusted code
- domain skill draft generation added as an inspectable local draft package with provenance, trust state, validation, and redacted examples/selectors
- selector validation added for expected object/string shapes and sensitive-looking fields
- helper validation added through Python AST parsing with basic disallowed import/call detection and no code execution
- artifact listing and retention cleanup utilities added with filtering by kind/session/domain/status and dry-run by default
- bundled browser workspace skill updated with concise Phase 2 operating guidance

## Verification Commands

Verified locally after review hardening:

```bash
python -m pytest -q
# 19 passed
python -m compileall hermes_browser_workspace tests
python -c "from hermes_browser_workspace.plugin import get_plugin; print(get_plugin().tool_names())"
/opt/homebrew/bin/python3 -m venv <tmp>
<tmp>/bin/python -m pip install -e .
<tmp>/bin/python -c "from hermes_browser_workspace.plugin import get_plugin; print(get_plugin().tool_names())"
```

Additional review hardening added after the Codex pass:

- microsecond timestamps for artifact/proposal id uniqueness
- helper proposal and domain skill draft id validation to block path traversal
- centralized redaction in `persist_review_artifact()` plus text redaction for sensitive assignments in proposal content/diffs
- regression tests for traversal rejection and redaction of review notes/proposal content

## Tool Surface

Phase 2 adds:

- `browser_workspace_list_helper_proposals`
- `browser_workspace_review_helper_proposal`
- `browser_workspace_validate_helper_proposal`
- `browser_workspace_draft_domain_skill`
- `browser_workspace_validate_domain_skill`
- `browser_workspace_list_artifacts`
- `browser_workspace_cleanup_artifacts`

Phase 1 tools remain present and keep the same safety defaults.

## Known Limitations

- helper validation is intentionally conservative and heuristic; it does not prove code safety
- helper proposal review records decisions locally but still does not modify `agent_helpers.py`
- domain skill draft validation focuses on structure and sensitive-field screening, not runtime correctness against live pages
- artifact cleanup targets JSON review artifacts and leaves protected config, helper, and active domain skill material alone by default
- editable install can require a fresh virtual environment on externally managed Python installations
- Hermes runtime integration assumptions remain adapter-based because the live Hermes plugin/runtime API is not part of this repository

## Upstream Hermes PR Candidates

1. A standardized external-plugin review artifact interface so plugins can attach proposal metadata and validation results with richer first-class UX.
2. Core-safe helper or code-review primitives for inspect-only validation flows that plugins can reuse instead of each plugin building its own AST policy layer.
3. Standardized browser artifact enumeration and retention hooks so plugin-local cleanup can align with Hermes-managed screenshots, traces, and session artifacts.

## Scope Guard

- no Hermes fork or vendored Hermes core behavior was added
- no automatic helper mutation or trusted auto-apply was added
- no public marketplace or sharing flow was added
- no required remote browser service was added
- no broad autonomous background learning automation was added

## Stop Before Phase 3

This checkpoint intentionally stops after Phase 2 Safer Adaptation. Phase 3 ideas such as stale-skill warnings, richer verification timestamps, and stronger reuse packaging remain out of scope and are not implemented here.
