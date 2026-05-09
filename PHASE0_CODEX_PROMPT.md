# Phase 0 Goal: Hermes Browser Workspace Tech Spec

You are Codex working for Victor/Hermes and Vinny on an open-source project proposal.

## Context

We discussed Browser Use's `browser-harness` project and compared it with Hermes Agent's native browser tooling. Browser Harness strengths:

- Thin direct Chrome DevTools Protocol (CDP) control.
- Editable agent workspace (`agent_helpers.py`).
- Domain-specific browser skills (`domain-skills/`).
- Self-healing pattern: if a helper is missing, the agent writes it.
- Screenshot/coordinate-first workflows for hard UIs.
- Local real-Chrome profile usage.
- Optional Browser Use Cloud support for remote/stealth/headless browsers.
- Post-task skill extraction and reuse.

Hermes already has many primitives:

- browser tools and raw `browser_cdp` escape hatch,
- terminal/file tools,
- plugin system with `PluginContext.register_tool()`, CLI commands, slash commands, and hooks,
- skills and durable memory,
- gateway/messaging, cron, subagents.

The proposed direction is **Option B: borrow the pattern natively**, but start as an installable open-source plugin/skill pack for any current Hermes instance rather than a Hermes fork.

Working product name: **Hermes Browser Workspace**.

Possible tagline: "Adaptive browser automation for Hermes: editable helpers, domain skills, CDP scripting, and safe learning loops."

## Non-negotiable phase boundary

This is **Phase 0 only**. Produce a high-quality technical specification and project plan. Do **not** implement runtime/plugin code beyond lightweight documentation scaffolding. Do not proceed to Phase 1.

Vinny wants explicit human checkpoints between phases. End Phase 0 with a checkpoint section that asks for approval before Phase 1.

## Deliverables

Create these files:

- `README.md` — GitHub-ready project overview, goals, installability vision, status: Phase 0/spec only.
- `docs/TECH_SPEC.md` — complete technical specification.
- `docs/ARCHITECTURE.md` — architecture, components, plugin boundaries, workspace layout.
- `docs/SECURITY_MODEL.md` — safety, PII/secrets, helper trust levels, gateway risks, browser profile risks.
- `docs/ROADMAP.md` — phase-gated roadmap from Phase 0 through community ecosystem.
- `docs/PHASE0_CHECKPOINT.md` — concise review packet for Vinny with decisions needed before Phase 1.

Optional if useful:

- `docs/DOMAIN_SKILL_FORMAT.md`
- `docs/PLUGIN_INSTALLATION_MODEL.md`

## Technical constraints and facts

Hermes current plugin system supports:

- bundled/user/project/pip plugins,
- `hermes_agent.plugins` entry point group,
- directory plugins under `~/.hermes/plugins/<name>/` with `plugin.yaml` and `__init__.py register(ctx)`,
- plugin tools via `PluginContext.register_tool()`,
- plugin CLI commands and slash commands,
- hooks including `pre_tool_call`, `post_tool_call`, `transform_tool_result`, `pre_llm_call`, `post_llm_call`, `on_session_start`, `on_session_finalize`, `on_session_reset`.

Preferred open-source repo shape:

```text
hermes-browser-workspace/
  pyproject.toml              # future phase, not necessary in Phase 0 unless docs mention it
  hermes_browser_workspace/   # future plugin package
  skills/browser-workspace/SKILL.md
  templates/agent_helpers.py
  docs/
```

Suggested eventual workspace path:

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

Suggested eventual plugin tools:

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

Core design principle:

> Build as a Hermes plugin first, upstream later only where plugin boundaries prove insufficient.

Security principle:

> Safe by default; self-modifying helpers are powerful but must have trust levels, provenance, validation, and no sensitive data persistence.

Human collaboration principle:

> Each roadmap phase stops at a checkpoint for Vinny. No automatic progression.

## What to emphasize

- This is not a Browser Harness fork and not a replacement for Hermes browser tools.
- It is a complementary Hermes browser workspace/plugin inspired by proven patterns.
- External installability is a first-class goal.
- The design should be honest about limitations: backend session sharing, proprietary cloud features, public skill network effects, stale skills, anti-bot/stealth arms race.
- Make docs practical and actionable enough for Phase 1 implementation.

## Quality bar

- Concise but complete.
- GitHub-ready.
- No hype beyond what is technically credible.
- Explicit phase gates and success criteria.
- Clear MVP definition for Phase 1.
- Clear upstream/core-Hermes opportunities separated from plugin-local implementation.

When finished, summarize the files created and stop.