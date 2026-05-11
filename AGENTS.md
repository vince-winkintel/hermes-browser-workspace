# AGENTS.md

Guidance for AI coding agents working in this repository. This file complements `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, and the design docs under `docs/`.

## Project overview

Hermes Browser Workspace is an experimental public-alpha Hermes plugin that adds a local browser automation workspace: editable helpers, reviewed helper proposals, reusable domain skills, CDP/capture helpers, artifacts, and safe learning loops.

Important boundaries:

- This is a plugin-first project, not a Hermes fork.
- Do not replace Hermes' built-in browser tools; compose with them.
- Keep self-modifying/helper-learning flows review-first and safe by default.
- Do not add hidden remote sync, marketplace behavior, anti-bot bypass behavior, or automatic trust of imported skills.

## Repository map

- `hermes_browser_workspace/` — Python package and Hermes plugin entry point.
- `hermes_browser_workspace/resources/` — packaged templates copied into user workspaces by doctor/bootstrap flows.
- `skills/browser-workspace/` — source skill guidance for the plugin workflow.
- `templates/community-domain-skill/` — starter template for community domain skills.
- `docs/` — roadmap, architecture, security, public-readiness, community, and phase-gate artifacts.
- `tests/` — pytest coverage for plugin tools, workspace bootstrap, artifacts, and domain skills.

## Setup commands

Use Python 3.10+.

```bash
python -m pip install -e .
python -m pytest -q
```

For distribution build checks:

```bash
python -m pip install build
python -m build
```

## Build and test commands

Run relevant checks before finishing changes:

```bash
python -m pytest -q
python -m compileall hermes_browser_workspace tests
python -c "from hermes_browser_workspace.plugin import get_plugin; names=get_plugin().tool_names(); assert len(names) == 23; print(names)"
python -m json.tool templates/community-domain-skill/metadata.json > /dev/null
python -m json.tool templates/community-domain-skill/selectors.json > /dev/null
python -m json.tool templates/community-domain-skill/recipes.json > /dev/null
```

When packaging behavior changes, also build the wheel and inspect packaged resources:

```bash
python -m build
python - <<'PY'
import zipfile
from pathlib import Path
wheel = next(Path('dist').glob('*.whl'))
names = set(zipfile.ZipFile(wheel).namelist())
required = {
    'hermes_browser_workspace/resources/templates/agent_helpers.py',
    'hermes_browser_workspace/resources/skills/browser-workspace/SKILL.md',
}
missing = sorted(required - names)
if missing:
    raise SystemExit(f'Missing wheel resources: {missing}')
print(f'Wheel resources OK: {wheel}')
PY
```

## Code style guidelines

- Prefer small, explicit Python functions with clear data boundaries.
- Keep plugin tool handlers deterministic and JSON-serializable.
- Validate file paths before reading or writing workspace artifacts; never allow traversal outside the configured workspace root.
- Preserve existing public tool names and payload shapes unless the change intentionally updates the plugin contract and docs/tests together.
- Keep docs concise and phase-gated; update the relevant checkpoint or design doc when behavior changes.

## Testing instructions

- Add or update tests with behavior changes.
- Use temporary directories for workspace/domain-skill tests; do not depend on a real `~/.hermes/browser-workspace`.
- Exercise both happy paths and safety failures for file, helper, import/export, and domain-skill flows.
- If the plugin tool count changes, update the plugin registration smoke tests and CI command intentionally.

## Security considerations

- Never commit secrets, cookies, browser profiles, screenshots with private data, authenticated traces, or real user runtime artifacts.
- Keep examples synthetic, public, or clearly redacted.
- Helper proposal text and learned examples must avoid leaking sensitive page content.
- Imported bundles/domain skills are not trusted automatically; preserve checksum/provenance/review semantics.
- Follow `SECURITY.md` for vulnerability reporting expectations and `docs/SECURITY_MODEL.md` for project-specific safety boundaries.

## Commit and pull request guidelines

- Use conventional commit style where practical: `feat:`, `fix:`, `docs:`, `test:`, `ci:`, `chore:`.
- Keep PRs scoped to one behavioral/documentation concern.
- Include a short summary, test plan, and security/safety notes for changes touching helper execution, artifacts, domain skills, import/export, or packaging.
- Do not claim production readiness; describe this project as experimental/public alpha unless the project status docs are intentionally changed.

## Documentation expectations

When changing behavior, update the closest relevant documentation:

- Public install/update/publish posture: `README.md`, `docs/PLUGIN_INSTALLATION_MODEL.md`, `docs/PUBLIC_REPO_READINESS.md`.
- Safety or trust behavior: `SECURITY.md`, `docs/SECURITY_MODEL.md`, `docs/BUNDLE_TRUST_AND_REVIEW.md`.
- Domain skill format or community contribution flow: `docs/DOMAIN_SKILL_FORMAT.md`, `docs/DOMAIN_SKILL_CONTRIBUTING.md`, `templates/community-domain-skill/`.
- Upstream Hermes candidate planning: `docs/UPSTREAM_HERMES_PR_CANDIDATES.md`.
