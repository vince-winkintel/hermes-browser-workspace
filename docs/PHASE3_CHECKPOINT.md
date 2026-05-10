# Phase 3 Checkpoint

## Status

Phase 3 Domain Skill Maturity is implemented in this repository. Phase 4 has not been started.

## What Was Implemented

- richer domain skill metadata with additive Phase 3 fields for `schema_version`, `verification_status`, `confidence`, `reliability`, `supported_task_types`, selector/example/recipe counts, and source package/import hints while preserving older Phase 1/2 metadata compatibility
- local verification tracking via `last_verified_at`, explicit verification metadata, configurable stale-skill warning thresholds, and advisory stale/never-verified reporting with no automatic disabling
- redacted example storage and extraction recipe storage with structural validation, sensitive-value redaction, and conservative rejection for explicit add/save recipe flows
- local-only domain skill packaging with inspectable manifest metadata and per-file SHA-256 checksums using stdlib only
- local package import flow that validates package contents and imports skills as `draft` plus `pending_review` by default without silently trusting or activating them
- concise bundled skill guidance updates for Phase 3 usage and safety posture

## Verification Commands

Verified locally in this repository:

```bash
python -m pytest -q
# 24 passed
python -m compileall hermes_browser_workspace tests
python -c "from hermes_browser_workspace.plugin import get_plugin; print(get_plugin().tool_names())"
/opt/homebrew/bin/python3 -m venv <tmp>
<tmp>/bin/python -m pip install -e .
# editable install smoke passed; plugin import reported 23 registered tools
```

## Tool Surface

Phase 3 adds:

- `browser_workspace_mark_domain_skill_verified`
- `browser_workspace_list_stale_domain_skills`
- `browser_workspace_add_domain_skill_example`
- `browser_workspace_list_domain_skill_examples`
- `browser_workspace_save_domain_skill_recipes`
- `browser_workspace_list_domain_skill_recipes`
- `browser_workspace_export_domain_skill_package`
- `browser_workspace_import_domain_skill_package`

Phase 1 and Phase 2 tools remain present. `browser_workspace_save_domain_skill` and `browser_workspace_draft_domain_skill` now also accept additive Phase 3 examples and extraction recipe payloads.

## Known Limitations

- verification state is local metadata only; this phase intentionally does not re-verify selectors or recipes against live pages
- example and recipe validation is heuristic and conservative rather than a full schema registry
- package import currently supports local directory bundles and zip archives created from the local export flow
- imported packages overwrite the local skill for the same domain rather than creating parallel variants; trust still remains downgraded to draft plus pending review
- Hermes runtime integration assumptions remain adapter-based because the live Hermes plugin/runtime API is not part of this repository

## Upstream Hermes PR Candidates

1. First-class plugin artifact APIs for import/export bundle presentation and review UX.
2. Shared provenance and trust metadata conventions for reusable plugin artifacts such as domain skills.
3. Optional core review surfaces for imported local bundles so plugin-local review metadata can render consistently in Hermes.

## Scope Guard

- no Hermes fork or vendored Hermes core behavior was added
- `browser_workspace_cdp_enabled` remains enabled by default
- real Chrome profile support remains disabled by default
- helper mutation still does not auto-apply trusted changes
- storage remains local-only
- domain skill saving remains explicit
- no public marketplace or sharing flow was added
- no required remote browser service was added
- no broad autonomous background learning automation was added

## Stop Before Phase 4

This checkpoint intentionally stops after Phase 3 Domain Skill Maturity. Phase 4 ecosystem or upstream decisions are documented only as notes above and are not implemented here.
