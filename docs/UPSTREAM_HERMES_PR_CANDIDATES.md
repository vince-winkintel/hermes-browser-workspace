# Upstream Hermes PR Candidates

Purpose: prompt-resource artifact for future tasks that generate upstream Hermes PRs. This file collects candidate upstream changes discovered while building Hermes Browser Workspace Phases 0–4. It is intentionally not a PR plan approval by itself; each candidate still needs a separate design/implementation task against the Hermes core repository.

## Source Evidence

- Phase 0 established the plugin-first boundary: prove the browser workspace externally before proposing Hermes core changes.
- Phase 1 validated that the plugin can ship externally, but exposed places where plugins duplicate browser/session integration glue.
- Phase 2 added review artifacts, helper validation, and artifact cleanup, exposing missing shared UX and validation primitives.
- Phase 3 added local package import/export, richer metadata, verification status, and checksums, exposing missing provenance/trust conventions.
- Phase 4 decision: keep browser-workspace experimentation plugin-local, but prepare focused upstream PRs for stable seams that multiple plugins or Hermes core tools can reuse.
- Post-roadmap Track 4 dogfooded the helper/domain-skill workflow on `example.org`, adding evidence that helper proposals, validation reports, domain-skill drafts, import review state, and artifact cleanup status need consistent review surfaces and trust vocabulary.
- Post-roadmap Track 5 piloted a community domain-skill contribution workflow, adding evidence for shared `community_proposed` trust vocabulary, PR/review artifacts, compatibility metadata, and import-as-untrusted semantics.
- Post-roadmap Track 7 prepared the first upstream PR candidate packet in `TRACK7_UPSTREAM_PR_CANDIDATE.md`, selecting shared provenance/trust metadata conventions as the safest first upstream seam.

## First Upstream Candidate Packet

Track 7 selected **shared provenance/trust metadata conventions** as the first upstream Hermes PR candidate. Use `TRACK7_UPSTREAM_PR_CANDIDATE.md` as the implementation-ready packet after explicit approval to work against Hermes core.

The recommended first PR remains additive and narrow: documentation plus optional backwards-compatible `PluginManifest` metadata preservation. It must not vendor Browser Workspace code, add browser-specific behavior, or treat provenance signals as authorization.

## Candidate 1: Standard Plugin Artifact and Review Surface

### Problem

Plugins can persist proposal/review artifacts locally, but Hermes does not yet provide a first-class shared interface for presenting plugin artifacts, validation results, reviewer decisions, or cleanup status in a consistent UI/CLI/gateway surface.

### Proposed Upstream Shape

Add a small plugin artifact registry/API that lets plugins register inspectable artifacts with:

- artifact id, kind, title, status, source plugin, source session/task, created/updated timestamps
- redacted preview text and optional structured metadata
- validation state and reviewer decision fields
- stable commands or dashboard hooks for list/show/review/archive/cleanup

### Browser Workspace Evidence

- Phase 2 helper proposal review metadata is plugin-local.
- Phase 2/3 domain skill draft/import review metadata is plugin-local.
- Phase 3 import/export bundles need a consistent review UX before trust changes.

### Suggested PR Boundary

Start with an API and CLI/dashboard display surface only. Do not move browser-workspace-specific artifact schemas into core.

### Acceptance Criteria

- External plugins can register artifacts without vendoring Hermes internals.
- Artifacts render consistently in CLI/dashboard/gateway-compatible contexts.
- Sensitive previews are redacted before persistence/display.
- Plugin-local storage remains possible; core owns the surface contract, not the artifact domain semantics.

## Candidate 2: Shared Provenance and Trust Metadata Conventions

### Problem

Reusable plugin artifacts need consistent provenance/trust language. Browser Workspace now tracks local domain skill trust, source packages, verification state, checksums, examples, and staleness, but these conventions are plugin-local and could diverge across ecosystem plugins.

### Proposed Upstream Shape

Document and optionally expose helper utilities/dataclasses for common metadata fields:

- `schema_version`
- `source_plugin`
- `source_session_id` / `source_task_id`
- `created_at` / `updated_at` / `last_verified_at`
- `trust_state` such as `draft`, `pending_review`, `trusted`, `deprecated`
- `verification_status`, confidence/reliability hints, and stale-warning metadata
- checksum/manifests for local bundles

### Browser Workspace Evidence

- Phase 3 richer domain skill metadata and local package checksums are useful beyond browser skills.
- Imported artifacts intentionally downgrade to draft/pending-review; this trust pattern should be reusable.
- Track 5 required a distinct `community_proposed` signal for source contributions that are maintainer-reviewed but still not locally trusted by consumers.

### Suggested PR Boundary

Begin as docs plus lightweight utilities. Avoid mandating one global trust workflow until more plugins validate the shape.

### Acceptance Criteria

- Plugin authors have a canonical vocabulary for provenance/trust metadata.
- Existing plugins can adopt fields incrementally.
- Hermes UI can display trust/provenance consistently when present.

## Candidate 3: Browser Artifact Enumeration and Retention Hooks

### Problem

Hermes browser tools, Browser Workspace, and future browser plugins can all produce screenshots, traces, captures, and extracted artifacts. Cleanup/review policies should not be invented separately in every plugin.

### Proposed Upstream Shape

Add standard browser/session artifact hooks for:

- registering screenshots, traces, captures, downloads, and extracted DOM/text snippets
- listing artifacts by session/task/domain/kind/status
- dry-run retention cleanup
- protected-path rules for config/helpers/active skills
- redacted summaries for gateway contexts

### Browser Workspace Evidence

- Phase 2 implemented plugin-local artifact listing and dry-run cleanup.
- Phase 3 package/export artifacts need review and cleanup without risking active local skills.

### Suggested PR Boundary

Expose generic artifact lifecycle hooks. Keep browser-workspace domain skill storage local to the plugin.

### Acceptance Criteria

- Plugins and core tools can enumerate artifacts through one surface.
- Cleanup is dry-run by default and honors protected paths.
- Users can inspect artifact provenance before deletion.

## Candidate 4: Stable Browser Session Handle Abstractions for Plugins

### Problem

External browser plugins need to interact with Hermes browser sessions/backends without depending on unstable internals or duplicating connection/session discovery logic. Today Browser Workspace relies on adapter-style assumptions and direct CDP configuration.

### Proposed Upstream Shape

Provide a stable plugin-facing browser session abstraction for:

- discovering current/available browser sessions
- obtaining a scoped CDP endpoint or operation handle when configured
- associating captures/events with a Hermes session/task
- handling local vs remote browser backends without plugin-specific branching

### Browser Workspace Evidence

- Phase 1/2/3 checkpoints note Hermes runtime integration assumptions remain adapter-based.
- The plugin intentionally did not fork or vendor Hermes core, but a stable seam would reduce duplicated glue.

### Suggested PR Boundary

Start with read/discovery/session-handle primitives. Avoid letting plugins bypass normal Hermes browser safety policies.

### Acceptance Criteria

- A plugin can discover and label browser sessions through public APIs.
- The abstraction works when CDP is unavailable and reports clear capability status.
- Existing core browser tools continue to own default browser operation behavior.

## Candidate 5: Stronger CDP Policy Enforcement Hooks

### Problem

Browser Workspace has bounded CDP policy/audit behavior, but CDP safety boundaries should be reusable and visible to Hermes rather than only plugin-local.

### Proposed Upstream Shape

Add optional CDP policy hooks that can be reused by browser-related tools/plugins:

- operation allow/deny policy by method/category
- audit event emission for CDP calls
- redaction of sensitive payloads/results
- per-context capability checks for gateway vs local CLI usage

### Browser Workspace Evidence

- Phase 1 required bounded CDP policy/audit logging.
- Phase 4 roadmap names stronger CDP policy enforcement hooks as a candidate area.

### Suggested PR Boundary

Policy and audit hooks only. Do not add broad autonomous CDP execution to core as part of this candidate.

### Acceptance Criteria

- Browser plugins can call a common policy checker before CDP operations.
- Denied operations explain which policy blocked them.
- Audit events are available to users without exposing secrets.

## Candidate 6: Inspect-Only Helper/Code Validation Primitives

### Problem

Plugins that propose local helper code need safe inspect-only validation. Browser Workspace currently implements Python AST validation locally; other plugins may duplicate or weaken this pattern.

### Proposed Upstream Shape

Provide inspect-only validation helpers for plugin-proposed snippets/files:

- parse-only AST checks with no execution
- disallowed import/call pattern configuration
- structured validation findings
- redacted source previews

### Browser Workspace Evidence

- Phase 2 added helper validation through AST parsing and explicitly avoided executing untrusted helper code.
- Phase 2 checkpoint identified shared code-review primitives as an upstream candidate.

### Suggested PR Boundary

Offer primitives only; do not create a general-purpose sandbox or trusted auto-apply workflow.

### Acceptance Criteria

- Plugins can validate proposed helper files without executing them.
- Findings are structured enough for CLI/dashboard display.
- The API defaults to conservative behavior.

## Deliberately Plugin-Local for Now

These should remain outside Hermes core until broader evidence exists:

- browser-workspace-specific domain skill schemas and extraction recipe semantics
- public marketplace/community sharing
- trusted helper auto-apply
- remote/cloud browser provider adapters that are not needed by core Hermes
- broad autonomous background learning loops
- anti-bot or site-specific browser behavior

## Recommended PR Generation Order

1. Shared provenance/trust metadata conventions — low-risk docs/utilities and useful across plugins.
2. Plugin artifact/review surface — enables better UX for existing Browser Workspace artifacts.
3. Browser artifact enumeration/retention hooks — aligns cleanup/review across core and plugins.
4. Browser session handle abstraction — needs closer coordination with Hermes browser internals.
5. CDP policy enforcement hooks — safety-sensitive; should follow session abstraction discussion.
6. Inspect-only helper/code validation primitives — can land earlier if another plugin also needs it, but keep scope narrow.

## Prompt Notes for Future PR Tasks

For each candidate PR task:

- Work in the upstream Hermes Agent repository, not this plugin repository.
- Load the `hermes-agent` skill before changing Hermes core.
- Treat this file as requirements context, not as implementation instructions.
- Keep PRs narrow and independently reviewable.
- Include tests and docs for any public plugin API.
- Do not vendor Browser Workspace code into Hermes core.
- Preserve plugin-first experimentation: upstream only stable seams, not domain-specific workflow logic.
