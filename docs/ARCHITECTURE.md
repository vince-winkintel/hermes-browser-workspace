# Hermes Browser Workspace Architecture

## 1. Architectural Intent

Hermes Browser Workspace should be implemented as an installable plugin and skill pack that sits on top of existing Hermes browser and filesystem primitives. The architecture should preserve three boundaries:

- Hermes core remains the execution host.
- The plugin owns browser workspace orchestration and persistence.
- The local filesystem workspace owns durable artifacts and domain knowledge.

## 2. System Context

```text
User
  -> Hermes session
    -> Hermes core browser tools / browser_cdp
    -> Hermes Browser Workspace plugin
      -> local workspace files
      -> packaged skill instructions
      -> optional local browser profile access
```

The plugin does not replace Hermes browser tools. It coordinates them, adds conventions, and persists reusable artifacts.

## 3. Major Components

### 3.1 Hermes Plugin Package

Future package location:

```text
hermes_browser_workspace/
```

Responsibilities:

- register plugin tools
- register CLI and slash command entry points if needed
- enforce config and security policy
- mediate access to helpers and domain skills
- manage artifact creation and retention
- record provenance and audit metadata

### 3.2 Skill Pack

Future location:

```text
skills/browser-workspace/SKILL.md
```

Responsibilities:

- teach Hermes how to use the workspace tools safely
- explain helper and domain skill patterns
- direct the model toward local reuse before ad hoc browser improvisation

### 3.3 Local Workspace

Planned root:

```text
~/.hermes/browser-workspace/
```

Responsibilities:

- durable helper code
- config and policy storage
- screenshots, traces, and session artifacts
- domain skill storage

### 3.4 Hermes Browser Layer

Existing Hermes browser tools plus `browser_cdp` are treated as underlying execution primitives. The workspace plugin should not duplicate full browser control logic if Hermes already provides it.

## 4. Proposed Repository Shape

```text
hermes-browser-workspace/
  README.md
  docs/
  skills/
    browser-workspace/
      SKILL.md
  templates/
    agent_helpers.py
  hermes_browser_workspace/
    # future Phase 1+ plugin code
```

Phase 0 keeps only documentation. Phase 1 may add the package and templates.

## 5. Runtime Workspace Shape

```text
~/.hermes/browser-workspace/
  config.yaml
  agent_helpers.py
  sessions/
    <session-id>/
      metadata.json
      events.jsonl
      outputs/
  screenshots/
    <session-id>/
  traces/
    <session-id>/
  domain-skills/
    <domain>/
      SKILL.md
      helpers.py
      selectors.json
      metadata.json
      examples/
```

## 6. Data Flow

### 6.1 Task Execution Flow

1. Hermes starts a session.
2. The plugin validates config and workspace availability.
3. The user or skill invokes a browser workspace tool.
4. The plugin reads helper and domain skill context relevant to the target site.
5. The plugin calls Hermes browser tools or `browser_cdp`.
6. The plugin records session artifacts and provenance.
7. The plugin optionally proposes reusable outputs after task completion.

### 6.2 Learning Flow

1. A task completes with useful reusable knowledge.
2. The plugin packages candidate helper or domain-skill changes.
3. The plugin attaches provenance and sensitivity metadata.
4. The user reviews or explicitly invokes save actions.
5. The plugin writes validated artifacts to the workspace.

## 7. Plugin Boundaries

### 7.1 Inside Plugin Scope

- workspace bootstrap
- config loading
- artifact storage
- domain skill lookup
- helper read/write policy enforcement
- CDP wrapper policies
- coordinate action wrappers

### 7.2 Outside Plugin Scope

- Hermes browser engine internals
- browser rendering internals
- general-purpose package management for Hermes
- cloud browser infrastructure
- global shared skill registry governance

## 8. Tool Architecture

### 8.1 High-Level Tools

- `browser_workspace_run`
- `browser_workspace_extract`
- `browser_workspace_search_domain_skills`
- `browser_workspace_save_domain_skill`
- `browser_workspace_learn_from_task`

These should express browser workspace intent and hide some storage and provenance details.

### 8.2 Low-Level Tools

- `browser_workspace_cdp`
- `browser_workspace_capture`
- `browser_workspace_click_xy`
- `browser_workspace_new_tab`

These should expose narrower primitives with strong audit logs and policy checks.

### 8.3 Support Tool

- `browser_workspace_doctor`

This is the bootstrap and diagnostics entry point and should be usable before any task execution.

## 9. Hook Opportunities

Hermes hooks that matter to this design:

- `on_session_start`: create or bind session artifact context
- `on_session_finalize`: write final metadata and cleanup
- `on_session_reset`: clear transient workspace state for the active session
- `pre_tool_call` / `post_tool_call`: audit and route browser workspace operations
- `transform_tool_result`: normalize captured artifacts
- `pre_llm_call` / `post_llm_call`: optional learning or instruction injection, used conservatively

Hooks should not become hidden control paths for risky writes. Default behavior should remain explicit and inspectable.

## 10. Session Model

Each session should receive a stable artifact directory and metadata record. At minimum:

- session id
- timestamps
- domain targets
- tools invoked
- artifacts created
- learning proposals generated
- approval outcomes

This structure is important for later debugging and provenance.

## 11. Domain Skill Architecture

Each domain skill should be an isolated package with:

- human-readable instructions
- optional helper code
- selectors or extraction metadata
- examples
- machine-readable metadata

Isolation by domain reduces accidental cross-site leakage and makes stale skills easier to retire.

## 12. Helper Execution Model

Phase 1 should treat helper execution as local, explicit, and auditable. The architecture should assume:

- helper code is not inherently trusted
- helper mutation is more sensitive than helper execution
- helper code may need lint or structural validation before activation
- helpers should operate through plugin APIs rather than direct uncontrolled side effects where possible

## 13. Browser Profile Integration

Real browser profile support is optional and high risk. Architecture should separate:

- profile-disabled mode
- ephemeral or isolated profile mode
- local real-profile mode with explicit opt-in

The plugin must know which mode it is in and record that in session metadata.

## 14. Upstream Pressure Points

The following areas may prove difficult in plugin-only form:

- stable browser session handles across tools
- standardized screenshot and trace storage APIs
- safe core-level CDP policy gates
- richer artifact attachment semantics

Phase 1 should collect evidence before proposing core Hermes changes.

## 15. Architecture Decision Summary

- Plugin first rather than Hermes fork
- Workspace persistence on local filesystem
- Domain skills stored locally by domain
- Helper mutations gated by trust and review
- CDP exposed as an escape hatch, not the default path
- Learning loops explicit and auditable
