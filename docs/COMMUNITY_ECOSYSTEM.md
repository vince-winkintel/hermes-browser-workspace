# Community Ecosystem Model

## Purpose

Phase 5 defines how Hermes Browser Workspace can support broader open-source collaboration without changing the security posture established in Phases 0–4.

The ecosystem model is deliberately conservative: community artifacts can be discovered, reviewed, and imported as untrusted local drafts, but they must not become active or trusted without explicit local review.

## Ecosystem Principles

1. **Local trust is never delegated.** A repository maintainer, signature, or bundle checksum can improve provenance, but the local Hermes user still decides whether to trust an imported skill.
2. **Review beats automation.** Imports default to `draft` plus `pending_review`. Promotion requires explicit review.
3. **Provenance remains visible.** Every shared artifact should identify its source repository, commit/release, package checksum, author/maintainer, verification date, supported Hermes/plugin versions, and known limitations.
4. **No secrets in public artifacts.** Community domain skills must not include cookies, tokens, localStorage, raw private screenshots, account-specific URLs, private customer data, or internal-only selectors.
5. **Compatibility is explicit.** Skill bundles should state the Hermes Browser Workspace version and Hermes Agent version range they were tested against.
6. **Governance stays lightweight until evidence justifies more.** Start with documented repository conventions and review checklists before adding marketplaces, registries, or trust automation.

## Recommended Repository Shape

A community-maintained domain skill repository should use an inspectable layout:

```text
browser-workspace-domain-skills/
  README.md
  SECURITY.md
  CONTRIBUTING.md
  COMPATIBILITY.md
  skills/
    example.com/
      SKILL.md
      metadata.json
      selectors.json
      examples/
      recipes.json
      REVIEW_CHECKLIST.md
  bundles/
    example.com-YYYYMMDD/
      manifest.json
      checksums.txt
      skill/
        ...
```

Use `templates/community-domain-skill/` from this repository as a starting point.

## Artifact Classes

### Domain Skill Source Trees

Human-readable source directories containing `SKILL.md`, metadata, selectors, redacted examples, and recipes. These are best for review and collaboration.

### Local Bundle Packages

Exported bundles with manifests and checksums. These are best for transfer/import, but still require review after import.

### Review Records

Markdown or JSON notes that capture what was checked, who reviewed it, when it was verified, and what remains risky.

## Trust Lifecycle

Community artifacts should move through this lifecycle:

1. **Published externally** — maintained in a public repository, but not trusted locally.
2. **Imported locally** — imported as `draft` and `pending_review`.
3. **Validated structurally** — JSON parses, required files exist, checksums match, sensitive fields are absent.
4. **Reviewed by a human/operator** — selectors, examples, recipes, and helper code are inspected.
5. **Verified against the live domain** — the skill works on a non-sensitive page/task.
6. **Promoted locally** — only after explicit local action.
7. **Rechecked periodically** — stale skills produce advisory warnings and should be reverified.

No phase of this lifecycle should silently transition a community artifact into trusted active use.

## Maintainer Responsibilities

Community maintainers should:

- publish reviewable source, not only opaque archives
- keep examples redacted and minimal
- document supported task types and known failure modes
- publish compatibility notes with every meaningful change
- avoid accepting helper code that performs network exfiltration, credential access, filesystem traversal, or browser profile manipulation
- remove or deprecate stale skills rather than leaving them ambiguous

## Consumer Responsibilities

Local users/importers should:

- inspect source before import when possible
- validate imported bundles before promotion
- keep imported skills in `pending_review` until locally verified
- avoid using community skills on sensitive accounts before verifying selectors and recipes
- treat signatures/checksums as integrity signals, not proof of safety

## Non-Goals

Phase 5 does **not** implement:

- a public marketplace
- automatic remote sync
- trusted auto-activation of community skills
- centralized moderation infrastructure
- remote browser services
- domain-specific anti-bot behavior

## Relationship to Upstream Hermes PRs

The community ecosystem would benefit from the upstream candidates documented in `UPSTREAM_HERMES_PR_CANDIDATES.md`, especially shared provenance/trust metadata and plugin artifact review surfaces. Those are separate Hermes core PR tasks and are not prerequisites for the Phase 5 documentation model.
