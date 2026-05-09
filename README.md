# Hermes Browser Workspace

Adaptive browser automation for Hermes: editable helpers, domain skills, CDP scripting, and safe learning loops.

## Status

Phase 0 only. This repository currently contains a technical specification and project plan. It does not yet include the runtime plugin, packaged skill, or browser workspace implementation.

Phase 1 must not begin until the Phase 0 checkpoint is reviewed and explicitly approved.

## What This Project Is

Hermes Browser Workspace is a proposed open-source plugin and skill pack for Hermes that brings a browser-centric working model inspired by proven agent automation patterns:

- editable local browser helpers
- reusable domain skills
- direct CDP escape hatches when high-level tools are insufficient
- screenshot and coordinate-oriented recovery paths for difficult UIs
- post-task learning loops with explicit safety controls

The design goal is to complement Hermes' existing browser tools, terminal tools, skills, memory, and plugin system. It is not a Browser Harness fork and not a replacement for Hermes-native browser tooling.

## Why This Exists

Hermes already has strong primitives:

- browser tools and raw `browser_cdp`
- terminal and file tools
- skills and durable memory
- plugins, hooks, CLI commands, and slash commands
- gateway, cron, and subagents

What is missing is a cohesive browser workspace pattern that makes these primitives easy to combine into repeatable browser automation workflows. Hermes Browser Workspace is intended to fill that gap as an installable plugin-first layer.

## Phase 0 Deliverables

- [Technical spec](docs/TECH_SPEC.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Security model](docs/SECURITY_MODEL.md)
- [Roadmap](docs/ROADMAP.md)
- [Phase 0 checkpoint](docs/PHASE0_CHECKPOINT.md)
- [Domain skill format](docs/DOMAIN_SKILL_FORMAT.md)
- [Plugin installation model](docs/PLUGIN_INSTALLATION_MODEL.md)

## Design Principles

- Plugin first: build as a Hermes plugin before proposing core changes.
- Safe by default: self-modifying helpers require trust levels, provenance, and validation.
- External installability: support real Hermes instances without a custom fork.
- Human checkpoints: each roadmap phase ends with explicit approval gates.
- Honest scope: do not overclaim around cloud browsers, anti-bot behavior, or skill sharing effects.

## Intended Future Shape

Planned repository shape in later phases:

```text
hermes-browser-workspace/
  pyproject.toml
  hermes_browser_workspace/
  skills/browser-workspace/SKILL.md
  templates/agent_helpers.py
  docs/
```

Planned runtime workspace:

```text
~/.hermes/browser-workspace/
  config.yaml
  agent_helpers.py
  sessions/
  screenshots/
  traces/
  domain-skills/
    github.com/
      SKILL.md
      helpers.py
      selectors.json
      examples/
```

## Planned Tool Surface

The current proposal targets these plugin tools in Phase 1 and later:

- `browser_workspace_doctor`
- `browser_workspace_run`
- `browser_workspace_cdp`
- `browser_workspace_new_tab`
- `browser_workspace_capture`
- `browser_workspace_click_xy`
- `browser_workspace_extract`
- `browser_workspace_search_domain_skills`
- `browser_workspace_save_domain_skill`
- `browser_workspace_learn_from_task`

## Non-Goals

- Replacing Hermes browser tools
- Shipping a Hermes fork
- Reproducing proprietary cloud browser features
- Enabling unrestricted self-modifying code without review controls
- Starting Phase 1 implementation during Phase 0

## Next Step

Review [docs/PHASE0_CHECKPOINT.md](docs/PHASE0_CHECKPOINT.md). Phase 1 should begin only after Vinny approves the Phase 0 decisions and MVP boundary.
