# Codex Task: Hermes Browser Workspace Phase 3 Domain Skill Maturity

You are implementing Phase 3 for the Hermes Browser Workspace project in this repository.

## Approval

Vinny explicitly approved Phase 2 and authorized Phase 3: `Phase 2 approved. Proceed to Phase 3.`

## Read first

Before coding, read:

- README.md
- docs/TECH_SPEC.md
- docs/ARCHITECTURE.md
- docs/SECURITY_MODEL.md
- docs/ROADMAP.md, especially Phase 3
- docs/DOMAIN_SKILL_FORMAT.md
- docs/PLUGIN_INSTALLATION_MODEL.md
- docs/PHASE0_CHECKPOINT.md
- docs/PHASE1_CHECKPOINT.md
- docs/PHASE2_CHECKPOINT.md
- Existing package: hermes_browser_workspace/
- Existing skill: skills/browser-workspace/SKILL.md
- Existing tests: tests/

## Non-negotiable constraints

- Implement Phase 3 only. Do not begin Phase 4 or Phase 5.
- Do not fork Hermes.
- Do not vendor or modify Hermes core.
- If a Hermes core change appears necessary, document it in the Phase 3 checkpoint as an upstream PR candidate instead.
- Keep the plugin installable out-of-tree.
- Preserve safety defaults:
  - `browser_workspace_cdp_enabled` stays on by default.
  - real Chrome profile support remains disabled by default and only behind explicit config/flag.
  - helper mutation must not auto-apply trusted changes.
  - storage remains local-only.
  - domain skill saving remains explicit.
- Do not implement public marketplace/sharing.
- Do not implement required remote browser services.
- Do not implement broad autonomous background learning automation.
- Do not implement Phase 4 ecosystem/upstream decisions.

## Phase 3 roadmap scope

Goal: improve domain skill quality, freshness, and local reuse.

Implement:

1. Richer domain skill metadata
   - Add structured metadata fields for schema/version, verification status, confidence/reliability, supported task types, selectors/examples counts, source package/import metadata where relevant.
   - Preserve compatibility with existing Phase 1/2 metadata. Avoid breaking older saved skills.
   - Keep trust/provenance/approval states visible.

2. Verification timestamps and stale-skill warnings
   - Add config/defaults for stale-skill warning threshold, e.g. days since `last_verified_at`.
   - Add functions/tools to mark domain skills verified and to report stale/never-verified skills.
   - Do not verify by hitting live web pages; this phase tracks local metadata/freshness only.
   - Stale warnings must be advisory and auditable, not automatic disabling.

3. Examples and extraction recipes
   - Add support for storing/listing redacted examples and extraction recipes for domain skills.
   - Validate examples/recipes structurally and reject or flag sensitive-looking fields.
   - Keep all writes inside the browser workspace root.

4. Optional local import/export packaging for teams
   - Implement local-only packaging of domain skills into an inspectable archive or directory bundle.
   - Implement import as draft/pending-review by default; imported skills must not become trusted/active silently.
   - Include manifest/provenance/checksum-style metadata if feasible with stdlib only.
   - This is local team packaging only, not a public marketplace or remote sharing flow.

5. Browser workspace skill update
   - Update bundled `skills/browser-workspace/SKILL.md` with concise Phase 3 guidance.
   - Keep it concise and avoid doc bloat.

6. Phase 3 checkpoint document
   - Create `docs/PHASE3_CHECKPOINT.md`.
   - Summarize implementation, tests, verification commands, known limitations, upstream PR candidates, and explicit stop-before-Phase-4 statement.

7. Tests
   - Add/extend pure-Python local tests for metadata compatibility, stale detection, mark verified, examples/recipes validation, local package export/import safety, and plugin registration/tool surface.

## Existing Phase 2 tool surface

Current tools include:

- `browser_workspace_doctor`
- `browser_workspace_capture`
- `browser_workspace_click_xy`
- `browser_workspace_cdp`
- `browser_workspace_search_domain_skills`
- `browser_workspace_save_domain_skill`
- `browser_workspace_read_helpers`
- `browser_workspace_propose_helper_update`
- `browser_workspace_list_helper_proposals`
- `browser_workspace_review_helper_proposal`
- `browser_workspace_validate_helper_proposal`
- `browser_workspace_draft_domain_skill`
- `browser_workspace_validate_domain_skill`
- `browser_workspace_list_artifacts`
- `browser_workspace_cleanup_artifacts`

You may add Phase 3 tools such as:

- `browser_workspace_mark_domain_skill_verified`
- `browser_workspace_list_stale_domain_skills`
- `browser_workspace_add_domain_skill_example`
- `browser_workspace_list_domain_skill_examples`
- `browser_workspace_export_domain_skill_package`
- `browser_workspace_import_domain_skill_package`

Use Hermes-style plugin registration compatible with the existing implementation: toolset, schema, JSON-string handlers, description, emoji.

## Safety requirements

- Redact sensitive-looking fields before persistence.
- Do not persist cookies, tokens, Authorization headers, localStorage, API keys, passwords, or account-specific secrets.
- Path writes must remain inside the browser workspace root.
- Imported packages must be validated and imported as draft/pending review, never trusted/active by default.
- Review/verification flows must not depend on hidden state; persisted JSON/markdown artifacts should be auditable.

## Verification expectations

Run and document:

- `python -m pytest -q`
- `python -m compileall hermes_browser_workspace tests`
- an editable install smoke test in a temporary venv if feasible
- a tool registration smoke check showing the Phase 3 tools

## Stop condition

Stop after Phase 3 Domain Skill Maturity and the Phase 3 checkpoint. Do not begin Phase 4. Leave any Phase 4 ideas as checkpoint notes only.
