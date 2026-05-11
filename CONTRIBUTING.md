# Contributing

Thanks for your interest in Hermes Browser Workspace. The project is currently a public-alpha candidate, so contributions should stay narrow, reviewable, and aligned with the local-first security model.

## Development Setup

```bash
git clone https://github.com/<owner>/hermes-browser-workspace.git
cd hermes-browser-workspace
python -m pip install -e .
python -m pytest -q
```

Before opening a pull request, run:

```bash
python -m pytest -q
python -m compileall hermes_browser_workspace tests
python -c "from hermes_browser_workspace.plugin import get_plugin; print(len(get_plugin().tool_names()))"
```

For package-facing changes, also run:

```bash
python -m pip install build
python -m build
```

## Pull Request Expectations

A good PR includes:

- clear scope and motivation
- tests for behavior changes
- docs updates when public behavior changes
- no secrets, private artifacts, screenshots, cookies, tokens, or authenticated traces
- no automatic trust or hidden remote execution paths

Keep changes small enough to review independently. Upstream Hermes core changes should be proposed separately using `docs/UPSTREAM_HERMES_PR_CANDIDATES.md`; do not vendor Hermes core code into this plugin.

## Domain Skill Contributions

For domain skills or community bundles, follow:

- `docs/DOMAIN_SKILL_CONTRIBUTING.md`
- `docs/BUNDLE_TRUST_AND_REVIEW.md`
- `templates/community-domain-skill/REVIEW_CHECKLIST.md`

Community artifacts must remain untrusted until explicit local review. Maintainer acceptance, signatures, checksums, and source repository metadata are provenance signals only.

## Safety Non-Goals

Please do not submit PRs that add:

- trusted auto-application of helper code
- automatic promotion of imported skills
- public marketplace behavior without separate governance
- hidden remote synchronization
- anti-bot, CAPTCHA bypass, or site-specific evasion behavior
- examples containing private or account-specific data
