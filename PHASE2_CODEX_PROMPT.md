# Codex Task: Hermes Browser Workspace Phase 2 Safer Adaptation

You are implementing Phase 2 for the Hermes Browser Workspace project in this repository.

## Approval

Vinny explicitly approved Phase 1 and authorized Phase 2: `Phase 1 approved. Proceed to Phase 2.`

## Read first

Before coding, read:

- README.md
- docs/TECH_SPEC.md
- docs/ARCHITECTURE.md
- docs/SECURITY_MODEL.md
- docs/ROADMAP.md
- docs/DOMAIN_SKILL_FORMAT.md
- docs/PLUGIN_INSTALLATION_MODEL.md
- docs/PHASE0_CHECKPOINT.md
- docs/PHASE1_CHECKPOINT.md
- Existing package: hermes_browser_workspace/
- Existing skill: skills/browser-workspace/SKILL.md
- Existing tests: tests/

## Non-negotiable constraints

- Implement Phase 2 only. Do not begin Phase 3.
- Do not fork Hermes.
- Do not vendor or modify Hermes core.
- If a Hermes core change appears necessary, document it in the Phase 2 checkpoint as an upstream PR candidate instead.
- Keep the plugin installable out-of-tree.
- Preserve Phase 1 safety defaults:
  - `browser_workspace_cdp_enabled` stays on by default.
  - real Chrome profile support remains disabled by default and only behind explicit config/flag.
  - helper mutation must not auto-apply trusted changes.
  - storage remains local-only.
  - domain skill saving remains explicit.
- Do not implement public marketplace/sharing.
- Do not implement required remote browser services.
- Do not implement broad autonomous background learning automation.

## Phase 2 roadmap scope

Goal: add controlled learning and review workflows now that the MVP exists.

Implement:

1. Helper proposals with richer review metadata
   - proposal id, created_at, source task/session/domain, status, reviewer, reviewed_at, decision notes
   - status transitions such as pending_review, approved, rejected, superseded
   - utilities/tools to list, read, and mark review decisions
   - still no automatic application to `agent_helpers.py`

2. Domain skill draft generation
   - a tool/function that creates a draft domain skill package from structured observations/selectors/examples
   - draft should be inspectable before explicit save/activation
   - provenance and trust state must be recorded
   - avoid storing secrets or account-specific data

3. Basic validation for selectors and helper structure
   - selector validation for expected shape/types and dangerous/sensitive fields
   - helper proposal validation: parse/compile Python, reject obvious unsafe imports/calls if feasible, and never execute helper code during validation
   - validation reports should be persisted as review artifacts where useful

4. Retention cleanup and artifact review utilities
   - local artifact listing by session/domain/kind/status
   - retention cleanup based on config/age, with dry-run by default
   - never delete workspace config, agent_helpers.py, or active domain skills by default

5. Browser workspace skill update
   - update the bundled `skills/browser-workspace/SKILL.md` with Phase 2 operating guidance
   - keep it concise

6. Phase 2 checkpoint document
   - create `docs/PHASE2_CHECKPOINT.md`
   - summarize implementation, tests, verification commands, known limitations, upstream PR candidates, and explicit stop-before-Phase-3 statement

7. Tests
   - add/extend tests for review metadata, proposal review, domain skill draft generation, validation, retention dry-run/cleanup, and plugin registration/tool surface
   - keep tests pure-Python/local

## Existing Phase 1 tool surface

Current tools include:

- `browser_workspace_doctor`
- `browser_workspace_capture`
- `browser_workspace_click_xy`
- `browser_workspace_cdp`
- `browser_workspace_search_domain_skills`
- `browser_workspace_save_domain_skill`
- `browser_workspace_read_helpers`
- `browser_workspace_propose_helper_update`

You may add Phase 2 tools such as:

- `browser_workspace_list_helper_proposals`
- `browser_workspace_review_helper_proposal`
- `browser_workspace_validate_helper_proposal`
- `browser_workspace_draft_domain_skill`
- `browser_workspace_validate_domain_skill`
- `browser_workspace_list_artifacts`
- `browser_workspace_cleanup_artifacts`

Use Hermes-style plugin registration compatible with the existing implementation: toolset, schema, JSON-string handlers, description, emoji.

## Safety requirements

- Redact sensitive-looking fields before persistence.
- Do not persist cookies, tokens, Authorization headers, localStorage, API keys, passwords, or account-specific secrets.
- Path writes must remain inside the browser workspace root.
- Validation must inspect but not execute untrusted helper code.
- Review flows must not depend on hidden state; persisted JSON/markdown artifacts should be auditable.

## Verification expectations

Run and document:

- `python -m pytest -q`
- `python -m compileall hermes_browser_workspace tests`
- an editable install smoke test in a temporary venv if feasible
- a tool registration smoke check showing the Phase 2 tools

## Stop condition

Stop after Phase 2 Safer Adaptation and the Phase 2 checkpoint. Do not begin Phase 3. Leave any Phase 3 ideas as checkpoint notes only.
