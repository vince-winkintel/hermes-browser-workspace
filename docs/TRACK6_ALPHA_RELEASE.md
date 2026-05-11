# Track 6: v0.1.0-alpha.1 Release

Date: 2026-05-11

## Scope

Track 6 tags the first public alpha release after public repository publication, install/update verification, helper/domain-skill dogfooding, and community contribution pilot work.

Release scope is intentionally narrow:

- align version and changelog for the alpha tag
- document install-from-tag instructions
- document known limitations and support posture
- create GitHub tag/release `v0.1.0-alpha.1`
- keep PyPI publishing out of scope until separately approved

## Version Mapping

- Git tag / GitHub release: `v0.1.0-alpha.1`
- Python package version: `0.1.0a1`

The package uses PEP 440 prerelease syntax while the Git tag keeps the human-readable alpha label used by the public roadmap.

## Install From Tag

```bash
python -m pip install git+https://github.com/vince-winkintel/hermes-browser-workspace.git@v0.1.0-alpha.1
```

For editable local development, continue to use:

```bash
git clone https://github.com/vince-winkintel/hermes-browser-workspace.git
cd hermes-browser-workspace
python -m pip install -e .[test]
python -m pytest -q
```

## Known Limitations

- Public alpha quality: APIs, docs, and workspace shape may change before a stable release.
- PyPI is not published for this alpha; GitHub install by branch, commit, or tag is the supported distribution path.
- Browser Workspace is plugin-first and does not replace Hermes' built-in browser tools.
- Helper proposal and imported community skill flows remain review-first; there is no trusted auto-apply path.
- Imported community bundles remain provenance signals only until explicitly reviewed and promoted locally.
- No remote browser service, marketplace, automatic sync, CAPTCHA bypass, or anti-bot bypass behavior is included.

## Release Verification Checklist

Before tagging:

- `python -m pytest -q`
- `python -m compileall hermes_browser_workspace tests scripts`
- plugin registration smoke reports 23 tools
- community template JSON files validate
- Track 5 community contribution pilot passes
- wheel/sdist build succeeds and packaged resources are present
- git status is clean except ignored local artifacts
- current GitHub `main` CI is green

## Release Notes Seed

```markdown
## v0.1.0-alpha.1

First public alpha of Hermes Browser Workspace, an experimental plugin-first browser automation workspace for Hermes.

Included:
- local Browser Workspace plugin and 23 `browser_workspace_*` tools
- safe workspace bootstrap/doctor flow
- CDP/capture helpers and coordinate fallback support
- review-first helper proposal workflows
- local domain skill creation, validation, verification, examples, recipes, and import/export packaging
- public repository readiness, install/update verification, dogfood evidence, and community contribution pilot docs
- conservative community ecosystem guidance with provenance-first trust semantics

Install:
`python -m pip install git+https://github.com/vince-winkintel/hermes-browser-workspace.git@v0.1.0-alpha.1`

Notes:
- GitHub tag/release only; no PyPI release.
- Experimental public alpha; do not treat imported community skills or signatures as automatic trust.
```
