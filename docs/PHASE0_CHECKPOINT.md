# Phase 0 Checkpoint

## Purpose

This document is the review packet for ending Phase 0 and deciding whether Hermes Browser Workspace should move into Phase 1 implementation.

Phase 1 must not begin until this checkpoint is explicitly approved.

## What Phase 0 Produced

- product definition for Hermes Browser Workspace as a plugin-first extension
- Phase 1 MVP boundary
- architecture for plugin, workspace, helper, and domain skill layers
- security model for helpers, browser profiles, artifacts, and CDP access
- phased roadmap with mandatory human checkpoints

## Decisions Needed

### 1. Approve Plugin-First Direction

Decision:

- proceed as installable Hermes plugin and skill pack first
- avoid Hermes fork unless plugin boundaries later prove insufficient

### 2. Approve Phase 1 MVP Boundary

Approve inclusion of:

- workspace bootstrap and doctor flow
- helper file template and read access
- screenshot capture and coordinate fallback
- bounded CDP wrapper
- local domain skill search and save
- provenance and audit metadata

Approve exclusion of:

- public skill marketplace
- remote browser service dependency
- trusted auto-apply helper mutation
- automatic phase progression

### 3. Approve Security Defaults

Recommended defaults:

- helper mutation `read_only` or `propose_only`
- profile integration disabled by default
- local-only storage
- explicit domain skill saving
- conservative artifact retention

### 4. Approve Open Questions

- Should Phase 1 include optional real Chrome profile support behind a flag?
- Should `browser_workspace_cdp` be on by default or explicitly enabled?
- Should helper proposals be allowed in Phase 1, or remain fully read-only?
- Are there any known Hermes-core gaps that must be resolved before implementation?

## Recommendation

Proceed to Phase 1 only if the reviewers agree with the plugin-first MVP and the default safety posture. If there is disagreement on helper mutation or profile access, choose the more conservative option for Phase 1.

## Approval Gate

Required explicit response from Vinny before Phase 1:

- `Approved for Phase 1 as specified`
- or `Approved for Phase 1 with these changes: ...`
- or `Not approved; revise Phase 0 on these points: ...`

## Checkpoint Prompt

Vinny: review the MVP boundary, helper trust model, and profile policy in particular. If approved, respond with the exact Phase 1 constraints you want preserved during implementation.
