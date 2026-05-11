# Hermes Browser Workspace

Adaptive browser automation for Hermes: editable helpers, domain skills, CDP scripting, and safe learning loops.

## Status

Phases 0–5 are complete. The repository contains the external Browser Workspace plugin, bundled skill guidance, local safety/review workflows, domain skill maturity features, upstream-decision documentation, and a conservative community ecosystem model.

Current status: public alpha. The public GitHub repository is published at `https://github.com/vince-winkintel/hermes-browser-workspace`.

Phase 5 community ecosystem work is complete; future community repository setup should use the Phase 5 templates and review model.

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

## Phase and Decision Artifacts

- [Technical spec](docs/TECH_SPEC.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Security model](docs/SECURITY_MODEL.md)
- [Roadmap](docs/ROADMAP.md)
- [Phase 0 checkpoint](docs/PHASE0_CHECKPOINT.md)
- [Phase 1 checkpoint](docs/PHASE1_CHECKPOINT.md)
- [Phase 2 checkpoint](docs/PHASE2_CHECKPOINT.md)
- [Phase 3 checkpoint](docs/PHASE3_CHECKPOINT.md)
- [Phase 4 checkpoint](docs/PHASE4_CHECKPOINT.md)
- [Phase 5 checkpoint](docs/PHASE5_CHECKPOINT.md)
- [Upstream Hermes PR candidates](docs/UPSTREAM_HERMES_PR_CANDIDATES.md)
- [Community ecosystem model](docs/COMMUNITY_ECOSYSTEM.md)
- [Domain skill contribution guide](docs/DOMAIN_SKILL_CONTRIBUTING.md)
- [Bundle trust and review](docs/BUNDLE_TRUST_AND_REVIEW.md)
- [Compatibility matrix](docs/COMPATIBILITY_MATRIX.md)
- [Public repository readiness checklist](docs/PUBLIC_REPO_READINESS.md)
- [Track 3 install/update verification](docs/TRACK3_INSTALL_UPDATE_VERIFICATION.md)
- [Track 4 dogfood helper/domain-skill workflow](docs/TRACK4_DOGFOOD_HELPER_DOMAIN_SKILL.md)
- [Track 5 community skill contribution pilot](docs/TRACK5_COMMUNITY_SKILL_CONTRIBUTION_PILOT.md)
- [Domain skill format](docs/DOMAIN_SKILL_FORMAT.md)
- [Plugin installation model](docs/PLUGIN_INSTALLATION_MODEL.md)

## Design Principles

- Plugin first: build as a Hermes plugin before proposing core changes.
- Safe by default: self-modifying helpers require trust levels, provenance, and validation.
- External installability: support real Hermes instances without a custom fork.
- Human checkpoints: each roadmap phase ends with explicit approval gates.
- Honest scope: do not overclaim around cloud browsers, anti-bot behavior, or skill sharing effects.

## Repository Shape

```text
hermes-browser-workspace/
  AGENTS.md
  pyproject.toml
  hermes_browser_workspace/
    resources/
      templates/agent_helpers.py
      skills/browser-workspace/SKILL.md
  skills/browser-workspace/SKILL.md
  templates/
  docs/
```

Runtime workspace:

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

## Tool Surface

The plugin includes browser workspace tools for local setup, CDP/capture helpers, helper proposals, artifacts, domain skill review, verification/staleness tracking, examples, recipes, and local import/export packaging. The original Phase 1 seed tools were:

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

## Installation and Update

Install from GitHub:

```bash
python -m pip install git+https://github.com/vince-winkintel/hermes-browser-workspace.git
```

For local development from a checkout:

```bash
git clone https://github.com/vince-winkintel/hermes-browser-workspace.git
cd hermes-browser-workspace
python -m pip install -e .[test]
python -m pytest -q
```

To update from GitHub after publication:

```bash
python -m pip install --upgrade git+https://github.com/vince-winkintel/hermes-browser-workspace.git
```

The plugin registers through the `hermes_agent.plugins` entry point group. A first run of `browser_workspace_doctor` bootstraps local files under the user's Hermes Browser Workspace directory without overwriting existing local domain skills or helpers.

## Non-Goals

- Replacing Hermes browser tools
- Shipping a Hermes fork
- Reproducing proprietary cloud browser features
- Enabling unrestricted self-modifying code without review controls
- Automatically trusting imported community skills or helper code

## Next Step

The original roadmap phases are complete. Future work should be framed as a narrow upstream Hermes PR task, a scoped Browser Workspace follow-on, or a community repository setup task using the Phase 5 templates and review model.
