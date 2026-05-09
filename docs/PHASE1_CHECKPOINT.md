# Phase 1 Checkpoint

## Status

Phase 1 Local MVP implemented in this repository. Phase 2 has not been started.

## What Was Implemented

- pip-installable Python package skeleton in `pyproject.toml`
- plugin metadata in `plugin.yaml`
- local plugin package under `hermes_browser_workspace/`
- workspace bootstrap and doctor flow
- conservative config loading and default config creation
- helper template, helper read access, and helper proposal persistence without auto-apply
- session metadata, event logs, capture metadata, and CDP trace provenance
- bounded `browser_workspace_cdp` policy checks enabled by default
- optional real Chrome profile config flags, disabled by default
- local domain skill search, save, and validation
- bundled browser workspace skill instructions
- pure-Python tests for config, workspace, domain-skill, and safety logic

## Install

```bash
pip install -e .
pytest
python3 -c "from hermes_browser_workspace.plugin import get_plugin; print(get_plugin().tool_names())"
```

## Verification Log

- Implemented package import surface through `hermes_agent.plugins` entry point.
- Added a directory-plugin `register(ctx)` entry point compatible with Hermes' plugin loader.
- Added Hermes-style tool registration metadata: toolset, schema, JSON-string handlers, descriptions, and emoji.
- Added default workspace bootstrap for `~/.hermes/browser-workspace/` with `config.yaml`, `agent_helpers.py`, `sessions/`, `screenshots/`, `traces/`, and `domain-skills/`.
- Added `HERMES_BROWSER_WORKSPACE_ROOT` override for tests and non-default local workspace roots.
- Added proposal-only helper persistence to session storage instead of trusted mutation.
- Added explicit domain skill save path with metadata and provenance sidecar JSON.
- Added CDP allow/block prefix checks and per-call trace logging.
- Added redaction of sensitive-looking keys before persisting capture metadata, CDP params/results, helper proposals, domain-skill metadata, and selectors.

Verification commands run in this repository:

- `python -m pytest -q` → 8 passed
- `python -m compileall hermes_browser_workspace tests`
- `python -c "from hermes_browser_workspace.plugin import get_plugin; print(get_plugin().tool_names())"`
- temporary venv smoke test: `/opt/homebrew/bin/python3 -m venv <tmp> && <tmp>/bin/python -m pip install -e . && <tmp>/bin/python -c "from hermes_browser_workspace.plugin import get_plugin; print(get_plugin().tool_names())"`

## Known Limitations

- Hermes plugin API assumptions are still adapter-based because the actual runtime `PluginContext.register_tool()` surface was not available in this repository.
- The CDP wrapper logs and enforces local policy but does not invoke Hermes core browser tools directly in tests.
- Screenshot capture currently records metadata and coordinate fallback intent; actual image acquisition still depends on Hermes browser/runtime integration.
- Config parsing is intentionally minimal and supports simple YAML-style key/value structure plus JSON literals for arrays.
- No trusted helper auto-apply or background learning automation is included.

## Upstream Hermes PR Candidates

1. Standardized plugin tool registration and capability introspection examples for external plugins.
2. Stable browser session/tab handle API that plugin tools can share without relying on hidden runtime state.
3. Core screenshot and artifact attachment API so plugins can store image outputs with consistent metadata.
4. Core CDP policy hook support for allow/block enforcement and standardized audit logging.

## Scope Guard

- No Hermes fork or vendored Hermes core behavior was added.
- No public skill marketplace was implemented.
- No remote browser service is required.
- No automatic progression to Phase 2 was implemented.
