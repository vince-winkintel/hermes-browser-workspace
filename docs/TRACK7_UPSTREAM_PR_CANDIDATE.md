# Track 7 Upstream Hermes PR Candidate

Date: 2026-05-11

Kanban task: `t_9d7a6856`

## Scope

Track 7 prepares the first narrow upstream Hermes PR candidate after the Browser Workspace public alpha release.

This track is **plan-only** for upstream Hermes. It does not modify Hermes core, open an upstream PR, or vendor Browser Workspace code into Hermes Agent. The purpose is to turn `docs/UPSTREAM_HERMES_PR_CANDIDATES.md` into an implementation-ready candidate packet that can be approved separately before work begins against the Hermes core repository.

Selected candidate: **shared provenance and trust metadata conventions**.

## Why This Candidate Comes First

Shared provenance/trust metadata is the safest first upstream seam because it is mostly additive documentation plus lightweight helper utilities. Browser Workspace has already needed these concepts across multiple independent workflows:

- Phase 3: package import/export, source packages, checksums, verification status, and local trust downgrade on import.
- Track 4: helper proposals, validation reports, domain-skill drafts, review decisions, and imported package state.
- Track 5: community contribution review artifacts, compatibility metadata, and `community_proposed` source trust vocabulary.
- Track 6: public alpha release notes reiterated that maintainer review, checksums, signatures, and repository provenance are signals only, not automatic local trust.

The common rule to preserve upstream: **provenance signals must not automatically grant trust or activation**.

## Upstream Hermes Evidence Reviewed

The current Hermes Agent checkout at `/Users/steven/.hermes/hermes-agent` has a plugin surface that can accept this as an incremental extension without requiring browser-specific behavior:

- `hermes_cli/plugins.py`
  - `PluginManifest` already models plugin identity, version, source, path, and registry key.
  - `PluginContext.register_tool(...)` is the central public plugin registration API for tools.
- `tools/registry.py`
  - `ToolEntry` and `ToolRegistry.register(...)` already hold tool metadata such as name, toolset, schema, handler, description, emoji, environment checks, and result caps.
- `website/docs/guides/build-a-hermes-plugin.md`
  - Plugin author docs already explain `plugin.yaml`, `register(ctx)`, tool schemas, handlers, and plugin registration rules.
- `tests/hermes_cli/test_plugins.py`
  - Existing plugin discovery/loading tests are a natural home for manifest metadata compatibility tests.

These seams suggest a docs-first PR with optional dataclass/helpers under plugin metadata utilities, not a Browser Workspace-specific import.

## Proposed Upstream PR Shape

Working title:

```text
docs/plugins: define shared plugin provenance and trust metadata
```

Recommended branch name:

```text
docs/plugin-provenance-trust-metadata
```

Recommended upstream files to touch:

- `website/docs/guides/build-a-hermes-plugin.md`
  - Add a section for optional provenance/trust metadata in `plugin.yaml` and plugin-produced artifacts.
  - State explicitly that metadata is a display/review signal, not authorization.
- `website/docs/user-guide/features/plugins.md`
  - Add user-facing explanation for interpreting plugin provenance/trust fields.
- `hermes_cli/plugins.py`
  - Optionally extend `PluginManifest` with a backwards-compatible `metadata: Dict[str, Any] = field(default_factory=dict)` field if the manifest parser can preserve unknown structured metadata cleanly.
  - Keep existing manifests valid; no new required fields.
- `tests/hermes_cli/test_plugins.py`
  - Add coverage that a plugin manifest with metadata loads successfully and preserves the metadata if the implementation chooses to expose it.

If code changes are considered too much for the first PR, split the candidate into a docs-only PR first and a utility/dataclass PR second.

## Canonical Vocabulary Seed

The upstream PR should avoid over-standardizing while still giving plugin authors shared names to converge on.

Recommended top-level provenance fields for plugin-produced artifacts:

- `schema_version`: metadata schema version string, initially `1` or `1.0`.
- `source_plugin`: plugin name or registry key that produced the artifact.
- `source_plugin_version`: plugin version when known.
- `source_session_id`: Hermes session identifier when available.
- `source_task_id`: task/run identifier when available.
- `source_repository`: source repository URL or identifier when relevant.
- `source_commit`: source commit SHA when relevant.
- `created_at`: ISO-8601 UTC timestamp.
- `updated_at`: ISO-8601 UTC timestamp when changed.
- `last_verified_at`: ISO-8601 UTC timestamp when independently verified.
- `checksum_sha256`: SHA-256 for portable artifact content or bundle manifests.

Recommended trust/review fields:

- `trust_state`: one of the seed values below.
- `verification_status`: concise current verification label.
- `review_state`: optional review lifecycle label.
- `reviewed_by`: optional reviewer identity or role.
- `reviewed_at`: optional ISO-8601 UTC timestamp.
- `limitations`: optional list of known limits.
- `sensitivity`: optional hint such as `public`, `redacted`, `private`, or `secret_risk`.

Seed `trust_state` values:

- `draft`: locally created or imported but not reviewed.
- `model_proposed`: proposed by an AI/model and requiring review.
- `pending_review`: awaiting human/local review.
- `community_proposed`: accepted or proposed in a community source but not locally trusted.
- `reviewed`: reviewed by a maintainer or human but not necessarily locally promoted.
- `trusted`: explicitly trusted in the local environment.
- `deprecated`: should no longer be used for new work.
- `rejected`: reviewed and not accepted.

Seed `verification_status` values:

- `unverified`
- `validated_static`
- `verified_safe_target`
- `imported_unverified`
- `stale`
- `failed_validation`

## Non-Goals for the First Upstream PR

Do not include these in the first PR:

- Browser Workspace domain skill schemas or extraction recipe semantics.
- Marketplace/community distribution behavior.
- Signature verification enforcement.
- Automatic trust or activation of imported artifacts.
- Broad artifact registry/review UI. That is a separate candidate.
- Browser/CDP/session abstractions.
- Migration of Browser Workspace code into Hermes core.

## Acceptance Criteria

The upstream candidate is ready to implement when an approved Hermes core task can meet these criteria:

1. Existing plugins and manifests continue to load unchanged.
2. Plugin authors have documented, canonical names for provenance/trust metadata.
3. Documentation clearly says provenance, signatures, checksums, maintainer review, and repository source are signals only.
4. Any code-level metadata support is optional and backwards-compatible.
5. Tests cover metadata parsing/preservation if code changes are included.
6. No browser-workspace-specific schemas or behavior are introduced upstream.

## Suggested Implementation Prompt for Hermes Core

Use this prompt only after explicit approval to work in the Hermes Agent core repository:

```text
Implement the first upstream Browser Workspace candidate in Hermes Agent: shared plugin provenance/trust metadata conventions. Start from docs in the Browser Workspace repository: docs/UPSTREAM_HERMES_PR_CANDIDATES.md and docs/TRACK7_UPSTREAM_PR_CANDIDATE.md. Keep the PR narrow and additive. Prefer docs plus optional backwards-compatible PluginManifest metadata preservation. Do not vendor Browser Workspace code, do not add browser-specific behavior, and do not make provenance/trust metadata grant authorization. Add/update tests if any code changes preserve metadata.
```

## Stop Gate

Before any upstream Hermes code changes or PR creation, get explicit approval for:

- whether the first PR should be docs-only or docs plus `PluginManifest.metadata` support
- the target branch/worktree in the Hermes Agent repository
- whether to open a GitHub PR or stop at a local branch/patch
