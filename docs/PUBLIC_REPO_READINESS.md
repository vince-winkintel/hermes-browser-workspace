# Public Repository Readiness Checklist

Use this checklist before creating or pushing the public GitHub repository.

## Repository Hygiene

- [ ] `.gitignore` excludes OS files, caches, build outputs, virtual environments, and local Browser Workspace runtime artifacts.
- [ ] No `.DS_Store`, cache directories, build outputs, or local runtime artifacts are staged.
- [ ] `git status --short` contains only intentional changes.

## Sensitive Data Review

- [ ] No secrets, tokens, passwords, cookies, session identifiers, private screenshots, browser profiles, or authenticated traces are committed.
- [ ] Examples use synthetic, public, or clearly redacted data only.
- [ ] Security docs tell contributors not to file sensitive details publicly.

## Public Docs

- [ ] README describes project status as public alpha / experimental.
- [ ] README includes install and update commands for local editable and GitHub installs.
- [ ] `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, and `CHANGELOG.md` exist.
- [ ] Safety boundaries remain explicit: no auto-trust, no marketplace, no hidden remote sync, no anti-bot bypass behavior.

## Packaging

- [ ] `pyproject.toml` package data includes resources required by wheel installs.
- [ ] Fresh editable install works.
- [ ] Built wheel can be installed into a clean environment.
- [ ] `browser_workspace_doctor` can bootstrap from packaged resources.

## CI / Verification

- [ ] GitHub Actions runs pytest on supported Python versions.
- [ ] CI compiles/import-smokes plugin code.
- [ ] CI validates JSON templates.
- [ ] Local verification passes before publishing.

## Publication Gate

Only create/push the public GitHub repository after this checklist is satisfied or any exceptions are documented as known limitations.
