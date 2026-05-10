# Phase 4 Checkpoint

## Status

Phase 4 Ecosystem and Upstream Decisions is implemented as documentation and planning artifacts. No Hermes core changes were made in this phase.

## Phase 4 Decision

Hermes Browser Workspace should remain an external plugin/skill-pack for domain-specific browser workflow innovation. The upstream Hermes work should focus only on stable, reusable seams that multiple plugins and core browser tools can share.

## What Was Added

- `docs/UPSTREAM_HERMES_PR_CANDIDATES.md`: collected upstream Hermes PR candidates into a standalone prompt-resource artifact for future PR-generation tasks.
- Roadmap/README status updates describing Phase 4 completion and the plugin-local vs upstream boundary.
- Kanban project board backfill for the original ideation discussion and Phases 0–3, with Phase 4 tracked on the same board.

## Upstream Candidates Selected for Future PR Tasks

The candidate PR areas are now centralized in `docs/UPSTREAM_HERMES_PR_CANDIDATES.md`:

1. shared provenance and trust metadata conventions
2. standard plugin artifact and review surface
3. browser artifact enumeration and retention hooks
4. stable browser session handle abstractions for plugins
5. stronger CDP policy enforcement hooks
6. inspect-only helper/code validation primitives

## What Should Stay Plugin-Local

- Browser Workspace domain skill schemas and extraction recipe semantics.
- Public marketplace/community sharing until governance and trust evidence exists.
- Trusted helper auto-apply.
- Required remote/cloud browser provider dependencies.
- Broad autonomous background learning loops.
- Site-specific or anti-bot browser behavior.

## Kanban Backfill

Board: `hermes-browser-workspace`

Retrofitted historical chain:

1. Ideation: compare browser-harness with Hermes browser tools
2. Phase 0: Specification
3. Phase 1: Local MVP
4. Phase 2: Safer Adaptation
5. Phase 3: Domain Skill Maturity
6. Phase 4: Ecosystem and Upstream Decisions

The completed phases were marked done in order so the durable board now preserves the project history from the original ideation phase forward.

## Verification Commands

Verified locally in this repository:

```bash
python -m pytest -q
python -m compileall hermes_browser_workspace tests
python -c "from hermes_browser_workspace.plugin import get_plugin; print(len(get_plugin().tool_names()), get_plugin().tool_names())"
```

Expected after Phase 4: no runtime tool-surface changes from Phase 3; 23 browser workspace tools remain registered.

## Scope Guard

- no Hermes fork or vendored Hermes core behavior was added
- no upstream Hermes PR was opened or generated in this phase
- no public marketplace or sharing flow was added
- no required remote browser service was added
- no trusted helper auto-apply was added
- no broad autonomous background learning automation was added

## Stop Before Phase 5

This checkpoint intentionally stops after Phase 4 Ecosystem and Upstream Decisions. Phase 5 community ecosystem work requires explicit approval before any implementation or public sharing/governance work begins.
