# Codex Task: Hermes Browser Workspace Phase 1 Local MVP

You are implementing Phase 1 for the Hermes Browser Workspace project in this repository.

## Background

Phase 0 produced only specifications. Phase 1 is now explicitly approved by Vinny.

Read these files before coding:

- README.md
- docs/TECH_SPEC.md
- docs/ARCHITECTURE.md
- docs/SECURITY_MODEL.md
- docs/ROADMAP.md
- docs/DOMAIN_SKILL_FORMAT.md
- docs/PLUGIN_INSTALLATION_MODEL.md
- docs/PHASE0_CHECKPOINT.md

## Phase 1 approval decisions to preserve

- Optional real Chrome profile support is included in Phase 1, but only behind an explicit flag/config option.
- `browser_workspace_cdp` should be enabled by default.
- Helper proposals are allowed in Phase 1.
- There are no known Hermes-core blockers before implementation.
- Forking Hermes is forbidden. Do not modify Hermes core here. If you discover a required Hermes upstream change, document it as an upstream PR candidate for Hermes rather than building a fork or vendoring core behavior.

## Phase 1 target scope

Implement a minimal installable Hermes plugin and skill pack that supports:

- Python package skeleton and install metadata.
- Hermes plugin registration.
- Workspace bootstrap and doctor flow.
- Local config loading and safe default config creation.
- Helper file template, helper read access, and helper proposal support without trusted auto-apply.
- Screenshot capture and coordinate fallback utilities where possible without relying on Hermes core modifications.
- Bounded CDP wrapper tool, enabled by default, with policy checks and audit/provenance logging.
- Optional real Chrome profile support behind a flag/config option only.
- Local domain skill search and save.
- Session artifact metadata and provenance.
- Bundled Hermes skill instructions for using the plugin.
- Basic tests for config/workspace/domain-skill/safety logic where feasible.
- A Phase 1 checkpoint document describing what was implemented, how to install/test, known limitations, and any upstream Hermes PR candidates.

## Deliberate exclusions

Do not implement:

- Public skill sharing/marketplace.
- Remote browser service as a required dependency.
- Trusted auto-apply helper mutation.
- Broad autonomous background learning automation.
- Any Hermes fork or local copy of Hermes core.
- Automatic progression to Phase 2.

## Design requirements

- Keep the implementation plugin-first and installable out-of-tree.
- Prefer small, auditable modules over large monoliths.
- All persisted artifacts must avoid cookies, tokens, localStorage, API keys, and account-specific secrets by default.
- Preserve provenance metadata: task/session id when available, domain/host when relevant, generated timestamp, source, approval/review status.
- Make defaults conservative:
  - helper mutation mode: `propose_only` or safer
  - browser profile integration: disabled unless explicitly enabled
  - storage: local only
  - domain skill saving: explicit tool action
- Validate/sanitize paths to keep writes under the browser workspace root.
- Use normal Python stdlib dependencies where practical.

## Expected repository shape

You may adjust as needed, but aim for something like:

```text
pyproject.toml
plugin.yaml
hermes_browser_workspace/
  __init__.py
  config.py
  workspace.py
  safety.py
  provenance.py
  domain_skills.py
  helpers.py
  cdp.py
  capture.py
  tools.py
  doctor.py
skills/browser-workspace/SKILL.md
templates/agent_helpers.py
tests/
docs/PHASE1_CHECKPOINT.md
```

## Testing and verification

- Add tests for pure-Python parts.
- Run the test suite you create.
- Run import/packaging smoke checks if feasible.
- Leave a clear verification log in docs/PHASE1_CHECKPOINT.md.

## Stop condition

Stop after completing Phase 1 Local MVP and the Phase 1 checkpoint. Do not begin Phase 2. Do not implement any feature that violates the deliberate exclusions. If a requirement is blocked by plugin API uncertainty, document the exact issue and a proposed upstream Hermes PR candidate.
