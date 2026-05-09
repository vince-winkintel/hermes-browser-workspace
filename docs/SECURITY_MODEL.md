# Hermes Browser Workspace Security Model

## 1. Security Posture

Hermes Browser Workspace should be safe by default. The design intentionally treats editable helpers, browser profiles, screenshots, traces, and learned artifacts as sensitive surfaces.

Default posture:

- no silent persistence of secrets
- no unrestricted self-modifying helper writes
- no assumption that local browser profiles are safe to expose broadly
- no hidden remote execution path

## 2. Assets to Protect

- browser session tokens and cookies
- credentials and autofill data
- screenshots containing PII or internal content
- traces and extracted page data
- helper code integrity
- domain skill provenance
- gateway or remote execution credentials

## 3. Threat Model

### 3.1 Local Risks

- helper code writes introduce unsafe logic
- traces and screenshots capture secrets
- real browser profiles expose authenticated sessions
- domain skills accidentally preserve sensitive workflow details

### 3.2 Agentic Risks

- model-generated helpers are incorrect or malicious by mistake
- learned artifacts overfit to one session and fail elsewhere
- automation stores raw page content that should not be retained
- coordinate actions perform unintended clicks on sensitive controls

### 3.3 Integration Risks

- gateway forwarding expands the trust boundary
- future remote browser support introduces third-party data exposure
- plugin hooks create hidden write paths if poorly designed

## 4. Core Security Principles

### 4.1 Least Persistence

Store the minimum durable data needed for reuse and debugging.

### 4.2 Explicit Trust Levels

Differentiate human-authored, model-proposed, reviewed, and auto-applied artifacts.

### 4.3 Provenance Everywhere

All learned or generated artifacts should carry source session and approval metadata.

### 4.4 Safe Defaults

High-risk features should start disabled.

### 4.5 Auditability

Writes to helpers, domain skills, and major artifacts should be inspectable as normal files and metadata.

## 5. Helper Trust Levels

Proposed trust states:

- `human_authored`
- `model_proposed`
- `human_reviewed`
- `trusted_local`
- `disabled`

Phase 1 should avoid automatic transition into `trusted_local`. That should require explicit user action.

## 6. Helper Mutation Policy

### 6.1 Allowed Modes

- `read_only`
- `propose_only`
- `review_required`
- `trusted_auto_apply`

### 6.2 Phase 1 Recommendation

- default: `read_only`
- optional developer mode: `propose_only`

`review_required` can be implemented if the review mechanism is simple and reliable. `trusted_auto_apply` should not be in the Phase 1 MVP.

## 7. Sensitive Data Handling

### 7.1 Screenshots

Risks:

- PII exposure
- credential prompts
- internal documents or dashboards

Controls:

- configurable retention windows
- session-scoped storage
- metadata flagging for sensitive captures
- no public sync or publication behavior

### 7.2 Traces and Extracted Data

Risks:

- accidental capture of tokens, headers, or private records
- excessive raw HTML storage

Controls:

- structured extraction preferred over full dumps
- configurable redaction filters
- retention limits
- provenance metadata

### 7.3 Browser Profiles

Risks:

- account takeover if profile data is exposed
- accidental action under privileged accounts

Controls:

- opt-in only
- explicit profile mode recorded in config and session metadata
- clear warning boundaries in docs and doctor output
- prefer isolated or dedicated profiles over a daily-use personal profile

## 8. Domain Skill Safety

Domain skills are useful but can leak sensitive workflow knowledge.

Controls:

- local-only storage in early phases
- metadata for source domain and creation context
- prohibition on storing secrets or tokens
- validation of expected file schema before activation
- optional review requirement before a newly learned skill becomes discoverable

## 9. Gateway and Remote Risks

Hermes may interact with gateway or messaging layers. The plugin should assume that any remote path expands the trust boundary.

Rules:

- do not require gateway connectivity for core local functionality
- record when actions depend on remote infrastructure
- treat any future remote browser integration as a separate threat model

Phase 1 should stay local-first.

## 10. CDP Risk Model

Raw CDP access is powerful and bypasses many higher-level safety assumptions.

Risks:

- arbitrary browser state manipulation
- sensitive inspection or exfiltration
- difficult-to-audit side effects

Controls:

- dedicated wrapper tool
- session logging of scripts and targets
- policy checks around disallowed operations if feasible
- clear distinction between standard browser actions and escape-hatch actions

## 11. Audit and Provenance Requirements

Each durable write should record:

- timestamp
- session id
- domain
- author type
- trust state
- approval state

Prefer sidecar metadata files or embedded front matter where practical.

## 12. Retention and Deletion

The workspace should define configurable retention policies for:

- screenshots
- traces
- session metadata
- generated proposals

Phase 1 should at minimum document retention defaults and expose a cleanup path through the doctor or CLI surface.

## 13. Recommended Phase 1 Defaults

- helper mutation disabled or propose-only
- domain skill saving explicit, not automatic
- profile integration disabled by default
- local-only storage
- artifact retention conservative and configurable
- no public publishing

## 14. Security Review Questions for Checkpoint

- Is real profile support acceptable in Phase 1 if disabled by default?
- Should `browser_workspace_cdp` be enabled by default or behind an explicit setting?
- What minimum provenance metadata is mandatory for any saved artifact?
- Is `propose_only` helper mutation acceptable, or should Phase 1 stay fully read-only?

## 15. Minimum Approval Condition for Phase 1

Phase 1 should not start until the default trust model, profile policy, and helper mutation policy are explicitly approved.
