# Security Policy

Hermes Browser Workspace is experimental public-alpha software for local-first browser automation workflows. The project intentionally favors review, provenance, and explicit local promotion over convenience automation.

## Supported Versions

Until the first tagged release, only the current `main` branch is supported for security review and fixes. After release tags begin, this file will identify supported release lines.

## Reporting a Vulnerability

Please open a private security advisory or contact the maintainer through the repository owner's preferred GitHub security channel once the public repository exists. Do not file public issues containing exploit details, secrets, private screenshots, session identifiers, or authenticated traces.

When reporting, include:

- affected commit or release
- operating system and Python version
- exact command or workflow used
- impact assessment
- minimal reproduction using synthetic or public data

## Project Security Boundaries

The project does **not** promise to bypass websites, anti-bot systems, CAPTCHAs, or access controls. It should not be used to automate actions that violate a site's terms or a user's authorization boundary.

Important defaults:

- imported domain skills remain `draft` / `pending_review` until explicit local promotion
- helper proposals are inspect-only until reviewed
- helper validation parses code but does not execute untrusted helper code
- checksums, signatures, source repositories, and maintainer review are provenance signals only, not automatic trust
- local runtime artifacts should stay under the user's Browser Workspace directory and should not be committed

## Sensitive Data

Never include these in issues, examples, fixtures, or community domain skill packages:

- API keys, tokens, passwords, cookies, or session identifiers
- private screenshots or authenticated traces
- customer data, personal data, or proprietary page contents
- raw browser profiles or downloaded account data

Use synthetic fixtures or public pages for reproductions whenever possible.
