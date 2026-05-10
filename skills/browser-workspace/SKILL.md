# Browser Workspace

Use Hermes Browser Workspace tools as a local-first browser workflow layer.

## Operating Order

1. Run `browser_workspace_doctor` before first use in a fresh environment.
2. Search local domain skills before inventing new selectors or instructions.
3. Prefer normal Hermes browser tools first.
4. Use `browser_workspace_capture` and `browser_workspace_click_xy` only for recovery when DOM-first actions fail.
5. Use `browser_workspace_cdp` as an escape hatch, not as the default path.
6. Save domain skills explicitly with provenance when a pattern is reusable.
7. Propose helper updates instead of applying them automatically.

## Safety Rules

- Do not store cookies, tokens, localStorage, API keys, or account-specific secrets.
- Treat screenshots and traces as sensitive local artifacts.
- Real Chrome profile usage must remain explicitly enabled in config.
- Helper mutation is proposal-only in Phase 1.
- Domain skill saving is an explicit action, not an automatic side effect.

## Phase 2 Notes

- Review helper proposals through `browser_workspace_list_helper_proposals`, `browser_workspace_validate_helper_proposal`, and `browser_workspace_review_helper_proposal`.
- Generate inspectable domain skill drafts with `browser_workspace_draft_domain_skill` before any explicit save flow.
- Use `browser_workspace_list_artifacts` and dry-run `browser_workspace_cleanup_artifacts` to review retention effects before deletion.
- `browser_workspace_cdp` remains enabled by default but bounded by local policy checks.
- If Hermes integration points are missing, document the exact gap as an upstream Hermes PR candidate instead of forking Hermes.
