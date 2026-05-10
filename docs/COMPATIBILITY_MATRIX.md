# Compatibility Matrix

## Purpose

Community domain skills and bundles should declare what they were tested with. This matrix gives maintainers a lightweight compatibility vocabulary for Phase 5.

## Current Project Compatibility

- Hermes Browser Workspace repository phase: Phase 5
- Browser Workspace tool surface: 23 `browser_workspace_*` tools
- Baseline verification command: `python -m pytest -q`
- Current expected test result: 24 passed

## Compatibility Fields

Use these fields in `metadata.json` and bundle manifests:

```json
{
  "compatible_hermes_agent": ">=0.13.0",
  "compatible_browser_workspace": ">=0.5.0",
  "tested_with": {
    "hermes_agent": "0.13.x",
    "browser_workspace_commit": "<commit>",
    "browser": "Chrome local CDP or Hermes browser backend",
    "platform": "macOS/Linux/Windows as tested"
  }
}
```

If exact package versions are not available, record the commit hash and verification date.

## Compatibility Status Values

- `tested`: verified against the stated versions and task types
- `expected`: likely compatible based on schema/tool stability but not recently verified
- `stale`: not verified within the configured freshness window
- `unknown`: imported without enough metadata
- `incompatible`: known not to work with the stated versions

## Maintainer Update Rules

When changing a community skill:

1. Update `updated_at` for any material change.
2. Update `last_verified_at` only after live verification.
3. Update compatibility ranges if tool/schema assumptions changed.
4. Record known incompatible versions when found.
5. Prefer `expected` or `stale` over overclaiming `tested`.

## Consumer Guidance

Treat compatibility metadata as advisory. Even a `tested` skill should be imported as a draft and locally verified before use on sensitive workflows.

## Matrix Template

For repository-level docs, use this markdown shape:

- Skill: `<domain>`
  - Supported task types: `<list>`
  - Browser Workspace version/commit: `<version-or-commit>`
  - Hermes Agent version: `<version>`
  - Browser/backend: `<browser/backend>`
  - Platform: `<platform>`
  - Status: `tested | expected | stale | unknown | incompatible`
  - Last verified: `<YYYY-MM-DD>`
  - Notes: `<known limits>`
