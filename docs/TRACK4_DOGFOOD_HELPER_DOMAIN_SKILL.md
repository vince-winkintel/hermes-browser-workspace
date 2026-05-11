# Track 4 Dogfood Helper and Domain Skill Workflow

Date: 2026-05-11

Kanban task: `t_9f30cf66`

Public target: `https://example.org/`

## Scope

Track 4 dogfooded the Browser Workspace helper/domain-skill lifecycle on a low-risk public target. The goal was to exercise the workflow as a real plugin user would, without using private account state, cookies, credentials, or site-specific anti-bot behavior.

Exercised lifecycle:

- bootstrap isolated Browser Workspace roots with `browser_workspace_doctor`
- capture a browser-task artifact for `example.org`
- propose helper changes without auto-applying them
- validate helper proposal inspect-only
- record a helper review decision
- draft a domain skill from observations/selectors/examples/recipes
- validate the draft domain skill
- save an active local domain skill
- add selectors, examples, and extraction recipes
- mark the local skill verified
- list artifacts and dry-run cleanup
- export the verified skill as a package
- import the package into a fresh isolated workspace
- confirm imported skill remains untrusted-local: `draft`, `pending_review`, and `imported_unverified`

## Commands Exercised

The reusable dogfood script is checked in at:

```bash
scripts/track4_dogfood_workflow.py
```

Run from a prepared development checkout:

```bash
python -m pip install -e .[test]
python scripts/track4_dogfood_workflow.py
```

In the local checkout used for this track, the script was also verified with the existing development venv:

```bash
.venv/bin/python scripts/track4_dogfood_workflow.py
```

The script creates temporary isolated source/import workspaces, registers the plugin through its Hermes plugin entry point, invokes the registered tool handlers, and prints a JSON summary.

## Browser Observation

The browser was navigated to `https://example.org/` and observed:

- title: `Example Domain`
- heading: `Example Domain`
- primary paragraph: the domain is reserved for documentation examples
- only obvious outbound action: `Learn more` link to IANA

This made the target suitable for deterministic dogfooding without account state.

## Results

Tool registration:

- registered `23` `browser_workspace_*` tools

Workspace bootstrap:

- source workspace doctor passed
- import workspace doctor passed
- CDP default remained enabled
- helper mutation mode remained `propose_only`
- real Chrome profile remained disabled

Capture/artifacts:

- capture metadata was written for session `track4-example-org`
- artifact listing found the expected review artifacts
- dry-run cleanup matched only session/review artifacts and did not delete protected skill/config/helper paths

Helper proposal workflow:

- proposed an `extract_example_org_summary(document)` helper addition
- inspect-only helper validation passed
- review decision recorded as `approved`
- no helper content was auto-applied by the workflow

Domain skill workflow:

- drafted `Example.org Browser Skill`
- draft validation passed for selectors, examples, recipes, and helper code
- saved active local skill for `example.org`
- added a second example
- saved one extraction recipe
- marked local skill `verified` with high confidence
- stale-skill query with threshold `1` day returned no stale results

Export/import workflow:

- exported package: `example-org-track4-dogfood.zip`
- imported package into a fresh isolated workspace
- imported state was correctly downgraded/preserved as:
  - `status`: `draft`
  - `approval_state`: `pending_review`
  - `trust_state`: `model_proposed`
  - `verification_status`: `imported_unverified`

## Friction and Follow-ups

### 1. Local promotion is intentionally explicit, but there is no single promote command yet

The import path correctly prevents a package from becoming trusted just because the source workspace had verified it. However, the current tool surface has no dedicated `promote imported skill after local review` command. Local promotion can be represented by saving/verifying after review, but a future follow-up could make this clearer with an explicit promotion/review tool.

This reinforces the existing upstream candidate for a standard plugin artifact/review surface rather than requiring a Browser Workspace-only solution.

### 2. Dogfood script assumes a prepared checkout or installed package

Running the script with the system Python before installing the package failed because `hermes_browser_workspace` was not importable. This is expected for an uninstalled checkout, and Track 3 already fixed the documented contributor path to use:

```bash
python -m pip install -e .[test]
```

The Track 4 script is documented with that prerequisite.

## Upstream Candidate Evidence Added

Track 4 strengthens evidence for these upstream candidates in `UPSTREAM_HERMES_PR_CANDIDATES.md`:

- standard plugin artifact and review surface
- shared provenance and trust metadata conventions
- browser artifact enumeration and retention hooks
- inspect-only helper/code validation primitives

The most concrete new evidence is that helper proposals, validation reports, domain-skill drafts, import review state, and cleanup status are all useful but currently plugin-local surfaces.

## Conclusion

Track 4 passed. The helper/domain-skill lifecycle works end-to-end on a low-risk public target, and imported packages correctly remain draft/pending-review until local review and promotion.
