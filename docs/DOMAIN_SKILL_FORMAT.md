# Domain Skill Format

## Purpose

This document defines the proposed local format for Hermes Browser Workspace domain skills. The format is intended to be simple, inspectable, and safe enough for Phase 1 local storage.

## Directory Shape

```text
domain-skills/
  <domain>/
    SKILL.md
    metadata.json
    selectors.json
    helpers.py
    examples/
```

All files are optional except `SKILL.md` and `metadata.json` for a saved skill package.

## File Roles

### `SKILL.md`

Human-readable instructions for operating on the domain. Typical contents:

- task patterns
- navigation hints
- warnings
- extraction notes
- known failure modes

### `metadata.json`

Machine-readable metadata. Proposed fields:

- `domain`
- `title`
- `tags`
- `created_at`
- `last_verified_at`
- `provenance`
- `author_type`
- `trust_state`
- `status`

### `selectors.json`

Structured selectors or extraction hints. Typical contents:

- named selectors
- fallback selectors
- notes on selector stability

### `helpers.py`

Optional domain-specific helper code. Phase 1 should treat this as more sensitive than markdown or JSON metadata.

### `examples/`

Small example inputs, outputs, or task notes. No secrets or raw private data should be stored here.

## Status Fields

Suggested `status` values:

- `draft`
- `active`
- `stale`
- `disabled`

Suggested `trust_state` values:

- `human_authored`
- `model_proposed`
- `human_reviewed`
- `trusted_local`

## Provenance Minimum

Every saved domain skill should record:

- source session id
- source hostname
- creation timestamp
- author type
- approval state

## Phase 1 Validation

Phase 1 should validate:

- required files exist
- metadata contains minimum fields
- JSON files parse cleanly
- domain directory name matches metadata domain

Phase 1 does not need a full schema registry if a simpler validator is enough.

## Non-Goals

- cross-instance synchronization
- signed skill bundles
- public marketplace packaging
- complex inheritance across domains
