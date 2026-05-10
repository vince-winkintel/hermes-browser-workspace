# Bundle Trust and Review

## Purpose

This document defines how signed or reviewed Hermes Browser Workspace skill bundles should be treated in Phase 5.

The core rule: signatures, checksums, reviews, and maintainer reputation are provenance signals, not authorization to trust or activate a bundle automatically.

## Bundle Contents

A transferable bundle should include:

```text
bundle/
  manifest.json
  checksums.txt
  REVIEW.md
  skill/
    SKILL.md
    metadata.json
    selectors.json
    recipes.json
    examples/
```

`manifest.json` should include:

- bundle id and version
- created timestamp
- source repository and commit
- domain list
- file list with SHA-256 checksums
- compatible Hermes Agent version range
- compatible Browser Workspace version range
- reviewer/maintainer attestations, if any
- known limitations

## Integrity Levels

### Unreviewed

The bundle has source metadata but no maintainer or third-party review. Import only as `draft` and `pending_review`.

### Maintainer Reviewed

A repository maintainer reviewed the bundle contents. This improves confidence but still imports as `draft` and `pending_review`.

### Independently Reviewed

A second reviewer checked the bundle against the review checklist. This improves confidence and may shorten local review, but must not bypass local promotion.

### Locally Verified

The local user/operator verified the imported skill on a safe task and explicitly promoted it. This is the only level that can become locally trusted.

## Signature Guidance

Optional signatures can prove that a bundle was produced by a known key, but they do not prove the bundle is safe. If signatures are used, record:

- key fingerprint
- signing identity
- signature timestamp
- verification command/result
- source commit/release tag

Unsigned bundles are allowed, but should be treated as lower-confidence artifacts.

## Import Rules

When importing a bundle:

1. Verify checksums before reading trust metadata.
2. Parse JSON files without executing helper code.
3. Redact sensitive-looking values from persisted review previews.
4. Import as `draft` and `pending_review` by default.
5. Preserve source repository, commit, bundle checksum, and reviewer notes.
6. Require explicit local promotion before active use.

## Review Questions

- Does the bundle contain only expected files?
- Do all checksums match the manifest?
- Are examples redacted and non-sensitive?
- Are selectors stable enough for the supported task types?
- Are recipes generic and free of account-specific steps?
- Is helper code absent? If present, was it reviewed without execution?
- Are compatibility ranges plausible?
- Are known limitations honest?

## Rejection Conditions

Reject or quarantine a bundle if it contains:

- secrets, credentials, cookies, localStorage, API keys, session IDs, or private customer data
- code intended to exfiltrate data or bypass authorization
- raw private screenshots or traces
- unclear provenance
- incompatible schema versions without migration notes
- hidden binary blobs or unexpected executable files

## Future Work

A future Hermes core PR could provide shared plugin artifact review surfaces, provenance conventions, and signature verification helpers. Until then, Browser Workspace should keep bundle review explicit and local.
