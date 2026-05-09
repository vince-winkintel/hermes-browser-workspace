# Hermes Browser Workspace Technical Specification

## 1. Purpose

Hermes Browser Workspace is a proposed plugin-first extension for Hermes that adds an opinionated browser automation workspace around existing Hermes capabilities. The system is intended to make browser tasks more adaptable by combining:

- editable helper code
- reusable domain skills
- direct CDP scripting
- screenshot and coordinate-first fallback workflows
- bounded learning loops that can convert successful task patterns into reusable artifacts

This specification defines the Phase 0 design only. No runtime implementation is included in scope.

## 2. Product Positioning

### 2.1 What It Is

An installable Hermes plugin and skill pack that organizes browser work into a local workspace with helper files, session artifacts, screenshots, traces, and domain-specific knowledge.

### 2.2 What It Is Not

- not a Browser Harness fork
- not a replacement for Hermes-native browser tools
- not a claim that all browser automation can be solved with one abstraction layer
- not a guarantee of stealth, anti-bot bypass, or shared browser state across all Hermes backends

### 2.3 Primary User

A Hermes user who already has browser tooling available but needs a more practical workflow for hard, stateful, or repetitive browser tasks.

## 3. Goals

### 3.1 Core Goals

- Provide a browser workspace pattern that can be installed on standard Hermes instances.
- Make helper logic editable and durable outside a single chat session.
- Allow domain skills to capture stable per-site knowledge.
- Expose CDP-level escape hatches without forcing every workflow to operate at raw CDP level.
- Enable safe post-task learning loops with provenance and review boundaries.
- Preserve a clear path for later upstreaming only where plugin boundaries prove insufficient.

### 3.2 Phase 1 MVP Goals

- Installable plugin package and local skill pack
- Workspace bootstrap and validation
- Read/write access to `agent_helpers.py`
- A minimal set of browser workspace tools
- Session artifact capture
- Local domain skill discovery and save flow
- Explicitly disabled or heavily gated self-modifying helper writes

## 4. Non-Goals

- Shipping a public shared skill marketplace in Phase 1
- Supporting remote cloud browsers as a first-party feature in Phase 1
- Solving anti-bot defenses generically
- Replacing Hermes core browser abstractions
- Implementing autonomous helper mutation without trust controls

## 5. Assumptions

- Hermes supports plugins via entry points and directory plugins.
- Hermes supports tool registration through `PluginContext.register_tool()`.
- Hermes exposes browser tools and a raw `browser_cdp` escape hatch.
- Hermes sessions can call plugin tools, file tools, and terminal tools.
- The local host environment may have access to a real Chrome profile, but that access should remain optional and configurable.

## 6. User Problems

### 6.1 Hard UI Recovery

Some browser tasks fail because DOM-first abstractions are insufficient. Users need screenshot-based inspection, coordinate clicks, and targeted CDP scripting when elements are hard to access.

### 6.2 Repetition Across Sites

Browser tasks on recurring domains often require stable selectors, common sequences, and defensive extraction logic that should be reusable.

### 6.3 Session-Limited Learning

Useful task knowledge is often lost when it remains only in chat context. Users need a structured way to preserve helpers and domain-specific knowledge safely.

### 6.4 Installation Friction

Advanced browser workflows should be installable into normal Hermes deployments without maintaining a fork.

## 7. Proposed Solution

### 7.1 Concept

Hermes Browser Workspace adds a persistent local workspace with:

- `agent_helpers.py` for reusable helper logic
- domain skill directories for site-specific knowledge
- session artifacts for screenshots, traces, and logs
- plugin tools that orchestrate Hermes browser capabilities against those files

### 7.2 Operating Model

1. A user installs the plugin and skill pack.
2. The plugin initializes or validates `~/.hermes/browser-workspace/`.
3. A task runs through normal Hermes interaction plus browser workspace tools.
4. The agent may consult existing helpers and domain skills.
5. If high-level actions fail, the agent may use screenshot-based capture, coordinate actions, or raw CDP scripts.
6. After task completion, the system may propose learning outputs such as a new domain skill, extraction pattern, or helper stub.
7. Persistence occurs only within configured safety boundaries.

## 8. Architecture Summary

Detailed architecture is in [ARCHITECTURE.md](ARCHITECTURE.md). At a high level the solution consists of:

- Hermes plugin package
- local workspace filesystem
- packaged skill instructions
- helper runtime contract
- domain skill format
- artifact capture pipeline
- optional post-task learning pipeline

## 9. Workspace Layout

Planned workspace root:

```text
~/.hermes/browser-workspace/
  config.yaml
  agent_helpers.py
  sessions/
  screenshots/
  traces/
  domain-skills/
```

### 9.1 File Responsibilities

- `config.yaml`: local configuration, safety flags, browser profile policy, retention limits
- `agent_helpers.py`: durable helper functions available to browser workflows
- `sessions/`: per-run metadata, logs, extracted observations
- `screenshots/`: captures for debugging and coordinate workflows
- `traces/`: optional structured traces or CDP dumps
- `domain-skills/`: per-domain skills, selectors, helpers, and examples

## 10. Plugin Capabilities

### 10.1 Planned Tools

#### `browser_workspace_doctor`

Validates plugin prerequisites, workspace structure, permissions, and optional browser profile availability.

#### `browser_workspace_run`

High-level entry point for running a browser-oriented workflow against the workspace context.

#### `browser_workspace_cdp`

Thin wrapper for bounded raw CDP scripts with logging and policy checks.

#### `browser_workspace_new_tab`

Opens or allocates a new browser tab within the current run context.

#### `browser_workspace_capture`

Captures screenshots, page metadata, coordinates, or selected DOM state.

#### `browser_workspace_click_xy`

Executes coordinate-based clicks with optional screenshot anchoring and audit logs.

#### `browser_workspace_extract`

Runs structured extraction using helpers, selectors, or domain skill metadata.

#### `browser_workspace_search_domain_skills`

Finds matching local domain skills by host, tags, and examples.

#### `browser_workspace_save_domain_skill`

Writes or updates a local domain skill package under trust and validation rules.

#### `browser_workspace_learn_from_task`

Proposes learning artifacts from a completed task and records provenance.

### 10.2 Planned Non-Tool Integrations

- CLI command for workspace bootstrap and diagnostics
- slash command shortcuts for common browser workspace flows
- lifecycle hooks for session setup, artifact finalization, and optional learning prompts

## 11. Helper Model

### 11.1 Helper Purpose

`agent_helpers.py` is the durable, editable helper layer. It exists to capture reusable browser logic that is too specific for core Hermes tools but too general to keep rewriting per task.

### 11.2 Helper Constraints

- helpers are local to the user workspace by default
- helpers must be auditable as normal files
- helper writes should be gated by trust level and validation mode
- helper execution must avoid automatic persistence of secrets or session tokens

### 11.3 Helper Mutation Modes

- `read_only`: helpers can be used but not modified
- `propose_only`: the system generates candidate diffs without applying them
- `review_required`: diffs may be staged locally but require explicit approval
- `trusted_auto_apply`: reserved for later phases, opt-in only

Phase 1 should support `read_only` and `propose_only` first.

## 12. Domain Skill Model

### 12.1 Purpose

Domain skills capture per-site knowledge that is stable enough to reuse:

- navigation patterns
- selectors
- extraction recipes
- warnings or anti-patterns
- examples and failure notes

### 12.2 Storage Shape

Example:

```text
domain-skills/
  github.com/
    SKILL.md
    helpers.py
    selectors.json
    examples/
```

### 12.3 Lookup Strategy

- exact host match first
- parent domain fallback when explicitly allowed
- tag and example search second
- local-only in early phases

### 12.4 Freshness Handling

Skills can become stale. Each saved skill should include:

- creation timestamp
- last verified timestamp
- provenance source
- optional confidence or review status

Phase 1 should store provenance and timestamps even if no automatic freshness scoring exists yet.

## 13. Learning Loop

### 13.1 Scope

The system may extract reusable knowledge after a task completes. This can include:

- helper proposals
- domain skill drafts
- selector updates
- example traces

### 13.2 Boundaries

- no automatic progression between roadmap phases
- no silent writes of sensitive data
- no autonomous helper mutation in default mode
- no public publishing in Phase 1

### 13.3 Provenance Requirements

Every generated artifact should record:

- task/session identifier
- source domain
- generation time
- whether content was human-authored, model-generated, or mixed
- approval status

## 14. Security and Trust Model

The full model is in [SECURITY_MODEL.md](SECURITY_MODEL.md). Required principles:

- safe defaults
- explicit helper trust levels
- auditable file writes
- no persistence of browser secrets by default
- clear risk handling for local browser profile access
- bounded use of gateway and remote execution paths

## 15. Plugin Boundaries vs Hermes Core

### 15.1 Keep Plugin-Local Initially

- workspace bootstrap
- helper file management
- domain skill storage and search
- artifact naming and retention
- learning proposal logic
- coordinate workflow utilities

### 15.2 Potential Upstream Candidates Later

- richer browser artifact APIs
- standard plugin-safe browser session handles
- first-class browser workspace lifecycle hooks
- safer CDP policy enforcement primitives
- standardized skill provenance metadata

Upstreaming should occur only after plugin limitations are demonstrated in practice.

## 16. Phase 1 MVP Definition

### 16.1 Must Include

- installable plugin skeleton
- local skill pack skeleton
- doctor/bootstrap flow
- workspace config and directory creation
- helper read access
- capture and coordinate fallback tools
- local domain skill search and save
- audit logging and provenance metadata

### 16.2 Must Exclude

- public skill network
- remote browser service integration as a core requirement
- automatic trusted helper rewrites
- broad background learning automation
- core Hermes changes unless strictly required and separately approved

## 17. Success Criteria

### 17.1 Phase 1 Success

- A normal Hermes user can install the plugin without forking Hermes.
- The plugin creates and validates the browser workspace predictably.
- A user can run at least one hard browser task with screenshot/CDP fallback support.
- The system can save a local domain skill with provenance metadata.
- Safety defaults prevent silent persistence of sensitive browser data.

### 17.2 Phase 2+ Success Signals

- repeated tasks on the same domain require fewer manual recoveries
- skill reuse reduces prompt and tool-call overhead
- helper proposals become more accurate with auditability intact

## 18. Known Limitations

- Browser backend session sharing may be constrained by Hermes internals.
- Browser Use Cloud equivalents are out of scope and may remain proprietary elsewhere.
- Public shared skill ecosystems create moderation and staleness problems.
- Anti-bot and stealth behavior is adversarial and should not be oversold.
- Real Chrome profile use increases power and risk simultaneously.

## 19. Open Decisions for Phase 0 Checkpoint

- Which helper mutation mode is acceptable for Phase 1?
- Is local real-Chrome profile support in or behind a later feature flag?
- Which exact plugin tools belong in the Phase 1 MVP?
- Should domain skill writes require an explicit user action every time?
- Which Hermes core gaps, if any, justify upstream requests before implementation?

## 20. Implementation Entry Criteria for Phase 1

Phase 1 should begin only when:

- Vinny approves the MVP boundary
- the security defaults are accepted
- the plugin-first scope is accepted
- the installability model is accepted
- any required Hermes core dependencies are identified explicitly
