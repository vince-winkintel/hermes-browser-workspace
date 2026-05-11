# Track 5 Community Skill Contribution Pilot

## Purpose

Track 5 piloted the community domain skill contribution workflow using the Phase 5 template and review model. The goal was to verify that a contributor can produce a reviewable skill package and that a consumer import preserves the untrusted local-review boundary.

## Scope

The pilot used a synthetic/public `example.org` domain skill contribution. It covered:

- metadata required for a community source contribution
- selectors with stability notes
- recipes with expected output and safety notes
- synthetic example payload expectations
- PR summary and maintainer review checklist
- import behavior into a local Browser Workspace consumer workspace
- compatibility and deprecation guidance touchpoints

No credentials, cookies, browser profiles, authenticated traces, private screenshots, anti-bot behavior, or site-specific bypass behavior were used.

## Added Pilot Script

`python scripts/track5_community_contribution_pilot.py`

The script performs the contribution path end to end in temporary directories:

1. copies `templates/community-domain-skill/` into a sample community repository shape
2. fills a synthetic `example.org` contribution
3. validates required files and required metadata
4. checks selectors, recipes, example payload, PR summary, and checklist completion
5. saves the contribution into an isolated source Browser Workspace
6. exports a local package
7. imports the package into an isolated consumer Browser Workspace
8. asserts imported state remains:
   - `status=draft`
   - `approval_state=pending_review`
   - `trust_state=community_proposed`
   - `verification_status=imported_unverified`

## Template Gaps Patched

The pilot found three concrete gaps:

1. **Template trust state was documented but not accepted by runtime validation.**
   - `metadata.json` recommended `community_proposed`.
   - `hermes_browser_workspace.safety.ALLOWED_TRUST_STATES` did not include it.
   - Track 5 added `community_proposed` as an accepted provenance/trust signal.

2. **The contribution template lacked a PR body artifact.**
   - Track 5 added `templates/community-domain-skill/PR_SUMMARY.md`.
   - The guide now recommends using it as the default PR body.

3. **The examples directory had guidance but no structured example payload.**
   - Track 5 added `templates/community-domain-skill/examples/synthetic-example.json`.
   - The pilot script requires an example payload for the sample contribution path.

Additional template cleanup:

- added `approval_state=pending_review`
- added `author_type=human_authored`
- corrected `compatible_browser_workspace` to the current public-alpha line (`>=0.1.0`)

## Review Model Result

Track 5 confirms the Phase 5 trust model is workable:

- A community source contribution may use `community_proposed` to distinguish it from model-generated local drafts and locally trusted skills.
- Importing a community package does **not** promote it to trusted local content.
- Consumer workspaces still receive the skill as `draft`, `pending_review`, and `imported_unverified`.
- Maintainer acceptance and local consumer promotion remain separate gates.

## Compatibility and Deprecation Notes

The pilot reinforces the existing compatibility matrix guidance:

- source contributions should state compatible Hermes Agent and Browser Workspace ranges
- maintainers should update verification timestamps when selectors or recipes change
- stale, unverifiable, private, or unsafe contributions should be deprecated rather than silently reused

## Verification Commands

Run from the repository root:

```bash
python scripts/track5_community_contribution_pilot.py
python -m json.tool templates/community-domain-skill/metadata.json > /dev/null
python -m json.tool templates/community-domain-skill/selectors.json > /dev/null
python -m json.tool templates/community-domain-skill/recipes.json > /dev/null
python -m json.tool templates/community-domain-skill/examples/synthetic-example.json > /dev/null
python -m pytest -q
python -m compileall hermes_browser_workspace tests scripts
python -c "from hermes_browser_workspace.plugin import get_plugin; names=get_plugin().tool_names(); assert len(names) == 23; print(names)"
```

## Outcome

Track 5 passed when the pilot script and full verification checks passed. The contribution workflow is now represented as a deterministic prompt/resource artifact and a reusable verification script.
