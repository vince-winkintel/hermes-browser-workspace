# Plugin Installation Model

## Goal

Hermes Browser Workspace should install into normal Hermes environments without requiring a Hermes fork.

## Supported Hermes Plugin Paths

The design should align with existing Hermes plugin mechanisms:

- bundled plugins
- user plugins
- project plugins
- pip-installed plugins via the `hermes_agent.plugins` entry point group
- directory plugins under `~/.hermes/plugins/<name>/`

## Preferred Distribution Model

Primary target after Phase 0:

- pip-installable plugin package
- repository-managed skill pack and templates

Secondary compatibility target:

- directory plugin installation for local development and early adopters

## Proposed Install Surface

### Option A: Pip Package

Current public-alpha target after repository publication:

```text
python -m pip install git+https://github.com/vince-winkintel/hermes-browser-workspace.git
```

For local development from a checkout:

```text
python -m pip install -e .[test]
```

This registers the plugin through `hermes_agent.plugins` and includes packaged helper/skill resources needed for first-run bootstrap.

### Option B: Directory Plugin

Future shape:

```text
~/.hermes/plugins/hermes-browser-workspace/
  plugin.yaml
  __init__.py
```

This is useful for local iteration and manual install scenarios.

## First-Run Bootstrap

The plugin should create or validate:

```text
~/.hermes/browser-workspace/
```

Bootstrap responsibilities:

- create directories
- place starter `agent_helpers.py` if missing
- create default `config.yaml` if missing
- verify permissions
- print clear warnings for disabled high-risk features

## Upgrade Considerations

Track 3 exercised update behavior from the public GitHub install path; see `TRACK3_INSTALL_UPDATE_VERIFICATION.md`.

Current expectations:

- package updates must not overwrite existing local helpers, domain skills, examples, recipes, or review artifacts
- starter templates may change in the installed package, but local workspace files remain user-owned after first bootstrap
- future workspace schema migrations should be explicit, reviewable, and dry-run capable when practical

Later releases should add workspace schema versioning and migration commands if package updates introduce incompatible local data changes.

## Success Criteria

- install does not require Hermes source modification
- plugin can be discovered by Hermes through standard plugin mechanisms
- first-run bootstrap is deterministic
- failure states are diagnosable through `browser_workspace_doctor`
