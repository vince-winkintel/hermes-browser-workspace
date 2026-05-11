# Track 3 Install and Update Verification

Date: 2026-05-11

Repository under test: `https://github.com/vince-winkintel/hermes-browser-workspace`

## Scope

Track 3 exercised the public install and update paths after the GitHub repository was published.

Validated paths:

- local editable development install from a checkout
- pip install from the public GitHub repository
- plugin discovery through the `hermes_agent.plugins` entry point group
- first-run workspace bootstrap through `browser_workspace_doctor`
- package upgrade/reinstall behavior against existing local workspace data
- Hermes CLI directory-plugin install/update in an isolated `HERMES_HOME`
- public GitHub Actions status after Track 3 changes

## Commands Exercised

### Local editable development install

```bash
git clone https://github.com/vince-winkintel/hermes-browser-workspace.git
cd hermes-browser-workspace
python -m pip install -e .[test]
python -m pytest -q
```

### Public GitHub package install

```bash
python -m pip install git+https://github.com/vince-winkintel/hermes-browser-workspace.git
```

Verification loaded the package, discovered the `hermes_agent.plugins` entry point, registered tools through a stub plugin context, and ran the doctor handler with an isolated `HERMES_BROWSER_WORKSPACE_ROOT`.

### Public GitHub package update/reinstall

```bash
python -m pip install --upgrade --force-reinstall git+https://github.com/vince-winkintel/hermes-browser-workspace.git
```

Verification created user-owned local workspace files before the reinstall, then reran the doctor handler and confirmed local helper and domain-skill data were preserved.

### Hermes CLI directory plugin install/update

```bash
HERMES_HOME=<temp-hermes-home> hermes plugins install vince-winkintel/hermes-browser-workspace --enable
HERMES_HOME=<temp-hermes-home> hermes plugins list
HERMES_HOME=<temp-hermes-home> hermes plugins update hermes-browser-workspace
```

This validates the secondary directory-plugin path without modifying the user's real Hermes home.

## Results

- Editable install from checkout succeeded.
- Public GitHub pip install succeeded.
- `hermes_agent.plugins` entry point discovery succeeded with entry point `hermes_browser_workspace.plugin:get_plugin`.
- Plugin registration exposed 23 `browser_workspace_*` tools.
- `browser_workspace_doctor` bootstrapped isolated workspace roots from packaged resources.
- Upgrade/reinstall preserved:
  - existing `agent_helpers.py` user edits
  - existing local `domain-skills/example.com/metadata.json`
- Hermes CLI directory plugin install created:
  - `<temp-hermes-home>/plugins/hermes-browser-workspace/plugin.yaml`
  - enabled plugin config in the isolated Hermes home
- `hermes plugins update hermes-browser-workspace` reported the plugin was already up to date.
- Public GitHub Actions latest run was green after Track 3 changes.

## Friction Found and Fixed

The public repo previously documented `python -m pip install -e .` followed by `python -m pytest -q`, but `pytest` is not a runtime dependency. Track 3 added a dedicated test extra:

```toml
[project.optional-dependencies]
test = ["pytest"]
```

Docs and CI now use:

```bash
python -m pip install -e .[test]
```

This keeps runtime dependencies empty while making contributor/test setup reproducible.

## Notes

- The package install/update path is the preferred public-alpha distribution path.
- The Hermes CLI directory-plugin path works for early adopters and local/manual plugin installs.
- Package updates currently do not perform workspace schema migrations. Future incompatible workspace changes should add explicit migration/versioning commands with dry-run behavior where practical.
- Existing local workspace files remain user-owned after first bootstrap; starter resources can change in the installed package without overwriting local helpers, domain skills, examples, recipes, or review artifacts.
