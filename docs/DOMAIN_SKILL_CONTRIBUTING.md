# Domain Skill Contribution Guide

## Purpose

This guide defines the expected contribution model for community-maintained Hermes Browser Workspace domain skills.

Contributions should improve reuse while preserving the local-first, review-required trust model.

## What Makes a Good Domain Skill

A good community domain skill is:

- narrowly scoped to a public domain or well-described app surface
- useful for repeatable browser tasks
- explicit about supported task types
- conservative about selectors and fallbacks
- clear about known failure modes
- free of secrets, account-specific data, and private screenshots
- verified recently enough to be useful

## Minimum Files

Each contributed skill directory should include:

```text
skills/<domain>/
  SKILL.md
  metadata.json
  selectors.json
  REVIEW_CHECKLIST.md
```

Optional files:

```text
  recipes.json
  examples/
    README.md
    *.json
```

Avoid helper code unless there is a strong reason. Helper code raises review burden and should never execute during validation.

## Required Metadata

`metadata.json` should include:

- `schema_version`
- `domain`
- `title`
- `description`
- `supported_task_types`
- `created_at`
- `updated_at`
- `last_verified_at`
- `verification_status`
- `trust_state`
- `source_repository`
- `source_commit`
- `maintainers`
- `compatible_hermes_agent`
- `compatible_browser_workspace`
- `known_limitations`

Recommended trust state for public source contributions: `community_proposed`.
Recommended imported local state: `draft` plus `pending_review`.

## Review Checklist

Before a contribution is accepted, reviewers should confirm:

- [ ] The domain is public or the private/internal nature is clearly documented.
- [ ] No cookies, tokens, localStorage, credentials, API keys, session IDs, private URLs, customer records, or raw private screenshots are present.
- [ ] Examples are synthetic, public, or aggressively redacted.
- [ ] Selectors are explained and include stability notes.
- [ ] Recipes are task-oriented and do not encode account-specific assumptions.
- [ ] Metadata includes compatibility and verification fields.
- [ ] Known limitations and failure modes are documented.
- [ ] Any helper code is avoided or receives manual source review.
- [ ] The contribution does not encourage bypassing site terms, anti-bot controls, paywalls, or authorization boundaries.

## Pull Request Expectations

A domain skill PR should include:

1. summary of the domain and supported tasks
2. list of files added/changed
3. verification date and environment
4. sensitive-data review statement
5. compatibility notes
6. screenshots only if they are public/redacted and necessary

## Versioning

Use additive changes whenever possible. If a selector or recipe becomes unreliable:

- update `last_verified_at`
- update `verification_status`
- record the failure mode
- avoid deleting historical notes that explain why a fallback exists

## Deprecation

Deprecate a skill when:

- the domain changed enough that selectors are misleading
- maintainers can no longer verify it
- the skill depends on private/account-specific behavior
- safety review finds sensitive data that cannot be cleanly removed

Deprecated skills should remain inspectable but should not be presented as active recommendations.

## Import Guidance for Users

Even accepted community contributions should be imported locally as untrusted drafts. Run validation, inspect metadata, review examples/selectors/recipes, and verify on a safe task before promoting locally.
