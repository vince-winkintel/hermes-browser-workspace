# Community Domain Skill Template

Copy this directory for each community-maintained domain skill:

```text
skills/<domain>/
  SKILL.md
  metadata.json
  selectors.json
  recipes.json
  REVIEW_CHECKLIST.md
  PR_SUMMARY.md
  examples/
    README.md
    synthetic-example.json
```

## Rules

- Keep examples synthetic, public, or redacted.
- Do not include cookies, tokens, credentials, localStorage, private screenshots, or customer data.
- Import community skills locally as `draft` plus `pending_review`.
- Promote only after explicit local review and safe-task verification.
- Use `community_proposed` for source contributions; local consumers should not treat that as trusted.
- Fill out `PR_SUMMARY.md` so maintainers can review verification, compatibility, and sensitive-data claims without reconstructing them from the files.
