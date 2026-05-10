# Hermes Browser Workspace Roadmap

## Roadmap Rules

- Every phase ends with a human checkpoint.
- No automatic progression between phases.
- Upstream Hermes changes require separate justification.
- Security defaults must stay ahead of convenience features.

## Phase 0: Specification

Status: complete

Objectives:

- define product scope
- define plugin-first architecture
- define security and trust model
- define Phase 1 MVP boundary

Deliverables:

- README
- technical spec
- architecture document
- security model
- roadmap
- Phase 0 checkpoint packet

Exit criteria:

- Vinny approves the MVP boundary
- installability model is accepted
- security defaults are accepted
- any Hermes-core dependencies are identified

## Phase 1: Local MVP

Goal:

Ship a minimal installable plugin and skill pack for current Hermes instances.

Target scope:

- package skeleton and plugin registration
- workspace bootstrap and doctor flow
- local config loading
- helper file template and read access
- screenshot capture and coordinate fallback utilities
- bounded CDP wrapper
- local domain skill search and save
- session artifact metadata and provenance

Deliberate exclusions:

- public skill sharing
- remote browser services as a core dependency
- trusted auto-apply helper mutation
- required Hermes fork

Success criteria:

- installable on a normal Hermes setup
- usable for at least one difficult browser workflow
- domain skill saved locally with provenance
- conservative security defaults hold under normal use

Checkpoint questions:

- Was the MVP useful without core Hermes changes?
- Which tool interfaces were awkward or missing?
- Is helper mutation needed yet, or should it remain deferred?

## Phase 2: Safer Adaptation

Goal:

Add controlled learning and review workflows once the MVP is stable.

Target scope:

- helper proposals with review metadata
- domain skill draft generation
- basic validation for selectors and helper structure
- retention cleanup and artifact review utilities

Success criteria:

- repeated tasks get measurably easier on a small set of target domains
- generated proposals are inspectable and usually useful
- safety review does not depend on hidden state

Checkpoint questions:

- Is proposal quality good enough to justify wider rollout?
- Do review flows create too much friction?
- What evidence exists for any upstream Hermes asks?

## Phase 3: Domain Skill Maturity

Goal:

Improve skill quality, freshness, and local reuse.

Target scope:

- richer domain skill metadata
- verification timestamps and stale-skill warnings
- examples and extraction recipes
- optional import/export packaging for local teams

Success criteria:

- domain skills become reliable enough to reduce repeated prompt engineering
- stale skills are detectable rather than silently reused

Checkpoint questions:

- Is local team sharing worth supporting before any broader ecosystem work?
- What governance is needed for importing third-party skill packs?

## Phase 4: Ecosystem and Upstream Decisions

Status: complete. See `PHASE4_CHECKPOINT.md` and `UPSTREAM_HERMES_PR_CANDIDATES.md`.

Goal:

Decide what should remain plugin-local and what should move upstream into Hermes core.

Candidate areas:

- browser artifact APIs
- session handle abstractions
- standardized provenance metadata
- stronger CDP policy enforcement hooks

Success criteria:

- upstream proposals are backed by concrete plugin pain points
- plugin-local innovation remains possible without blocking on core changes

Deliverables:

- standalone upstream PR candidate prompt-resource artifact
- explicit plugin-local vs upstream boundary decisions
- Kanban board backfill from ideation through Phase 4

Checkpoint questions:

- Which boundaries actually blocked adoption or safety?
- What should stay outside core to preserve flexibility?

## Phase 5: Community Ecosystem

Status: complete. See `PHASE5_CHECKPOINT.md`, `COMMUNITY_ECOSYSTEM.md`, `DOMAIN_SKILL_CONTRIBUTING.md`, `BUNDLE_TRUST_AND_REVIEW.md`, and `COMPATIBILITY_MATRIX.md`.

Goal:

Support broader open-source collaboration without weakening security posture.

Possible scope:

- community-maintained domain skill repositories
- documented contribution model
- signed or reviewed skill bundles
- compatibility matrix across Hermes versions

Risks:

- stale or unsafe shared skills
- moderation burden
- unclear trust assumptions for imported artifacts

Success criteria:

- ecosystem sharing improves reuse without encouraging unsafe defaults
- provenance and trust remain visible to end users

Deliverables:

- community ecosystem model and repository shape
- domain skill contribution guide and review checklist
- bundle trust/review guidance for checksums, signatures, and local promotion
- compatibility matrix guidance
- reusable community-domain-skill template

Checkpoint questions:

- Is there a credible governance model for shared skills?
- Are imported artifacts distinguishable from local trusted content?

## Cross-Phase Metrics

- installation success rate
- successful completion of hard browser tasks
- reduction in repeated task setup on known domains
- number of useful domain skills reused
- frequency of safety-related write blocks or redactions

## Stop Condition

If any phase shows that plugin boundaries are fundamentally insufficient, pause and document the exact limitation before proposing Hermes core changes.
