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

Future shape:

```text
pip install hermes-browser-workspace
```

This should register the plugin through `hermes_agent.plugins` and provide packaged templates and skill files.

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

Later phases should plan for:

- workspace schema versioning
- template migrations
- skill metadata migrations

Phase 1 can keep migrations minimal if they are documented clearly.

## Success Criteria

- install does not require Hermes source modification
- plugin can be discovered by Hermes through standard plugin mechanisms
- first-run bootstrap is deterministic
- failure states are diagnosable through `browser_workspace_doctor`
