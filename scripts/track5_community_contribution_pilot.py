from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hermes_browser_workspace.domain_skills import (  # noqa: E402
    export_domain_skill_package,
    import_domain_skill_package,
    save_domain_skill,
    validate_domain_skill,
)
TEMPLATE_DIR = REPO_ROOT / "templates" / "community-domain-skill"
SENSITIVE_RE = re.compile(
    r"(?i)\b(cookie|token|authorization|password|secret|api[_-]?key|localstorage|local_storage|sessionid)\b"
)

REQUIRED_FILES = {
    "SKILL.md",
    "metadata.json",
    "selectors.json",
    "recipes.json",
    "REVIEW_CHECKLIST.md",
    "PR_SUMMARY.md",
    "examples/README.md",
    "examples/synthetic-example.json",
}

REQUIRED_METADATA_FIELDS = {
    "schema_version",
    "domain",
    "title",
    "description",
    "supported_task_types",
    "created_at",
    "updated_at",
    "last_verified_at",
    "verification_status",
    "trust_state",
    "status",
    "approval_state",
    "source_repository",
    "source_commit",
    "maintainers",
    "compatible_hermes_agent",
    "compatible_browser_workspace",
    "known_limitations",
}


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ensure_no_sensitive_text(path: Path) -> None:
    if SENSITIVE_RE.search(path.read_text(encoding="utf-8")):
        # The template may name forbidden data types in review docs. Only scan contribution payload files.
        raise AssertionError(f"sensitive-looking term found in contribution payload: {path}")


def build_sample_contribution(root: Path) -> Path:
    contribution_dir = root / "community-domain-skills" / "skills" / "example.org"
    shutil.copytree(TEMPLATE_DIR, contribution_dir)

    metadata = {
        "schema_version": "1.0",
        "domain": "example.org",
        "title": "Example.org Public Demo Skill",
        "description": "Public, synthetic community contribution for reading the example.org demo page.",
        "supported_task_types": ["public-page-summary", "title-and-heading-extraction"],
        "tags": ["community", "browser-workspace", "public-demo"],
        "created_at": "2026-05-11T00:00:00Z",
        "updated_at": "2026-05-11T00:00:00Z",
        "last_verified_at": "2026-05-11T00:00:00Z",
        "verification_status": "community_verified",
        "trust_state": "community_proposed",
        "status": "draft",
        "approval_state": "pending_review",
        "author_type": "human_authored",
        "source_repository": "https://github.com/example/example.org-browser-skill",
        "source_commit": "0000000000000000000000000000000000000000",
        "maintainers": ["@example-maintainer"],
        "compatible_hermes_agent": ">=0.13.0",
        "compatible_browser_workspace": ">=0.1.0",
        "tested_with": {
            "hermes_agent": "0.13.0",
            "browser_workspace_commit": "local-track5-pilot",
            "browser": "Hermes browser tool or any standards browser",
            "platform": "macOS/Linux test runner",
        },
        "known_limitations": [
            "Only covers the public example.org demo page shape.",
            "Does not authenticate, mutate data, or bypass controls.",
        ],
    }
    write_json(contribution_dir / "metadata.json", metadata)

    skill_md = """# Example.org Public Demo Skill

## Scope

Domain: `example.org`

Supported task types:

- `public-page-summary`
- `title-and-heading-extraction`

## Operating Notes

- Prefer Hermes native browser tools first.
- Use Browser Workspace capture/CDP helpers only when a native snapshot is insufficient.
- Keep this skill limited to the public, static example.org page.

## Navigation Hints

- Open `https://example.org/`.
- Expect one `h1` heading and a short explanatory paragraph.

## Selectors and Stability

- `page_heading`: CSS selector `h1`; stable because the page is intentionally static.
- `main_content`: CSS selector `body`; broad fallback for summary extraction.

## Extraction Recipes

- `extract_public_summary`: capture page title, heading text, and first paragraph.

## Known Failure Modes

- If the public page is unreachable, stop and report network failure rather than using stale cached text.
- If the page shape changes, mark the skill stale and update selectors before reuse.

## Safety Notes

- No secrets or private account data are included.
- Examples are synthetic/public/redacted.
- Imported copies should remain pending review until locally verified.
"""
    (contribution_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    selectors = {
        "selectors": {
            "page_heading": {
                "selector": "h1",
                "type": "css",
                "purpose": "Read the public example.org page heading.",
                "stability": "high",
                "notes": "Static public demo page; verify before relying on it.",
            },
            "main_content": {
                "selector": "body",
                "type": "css",
                "purpose": "Fallback summary extraction from visible body text.",
                "stability": "medium",
                "notes": "Broad fallback, not a private or account-specific selector.",
            },
        },
        "fallbacks": [
            {
                "name": "title_only",
                "when": "heading selector missing",
                "action": "Use document title and report selector drift.",
            }
        ],
        "sensitive_fields": [],
    }
    write_json(contribution_dir / "selectors.json", selectors)

    recipes = {
        "recipes": [
            {
                "name": "extract_public_summary",
                "description": "Extract title, public heading, and first paragraph from example.org.",
                "supported_task_type": "public-page-summary",
                "steps": [
                    "Open https://example.org/ without credentials or custom browser profile.",
                    "Read document title and the documented page_heading selector.",
                    "Return only public visible text and selector verification status.",
                ],
                "expected_output": {
                    "type": "object",
                    "required_fields": ["title", "heading", "summary", "verified_selectors"],
                },
                "safety_notes": [
                    "Run only on the public example.org page.",
                    "Do not add account-specific selectors, traces, cookies, or screenshots.",
                ],
            }
        ]
    }
    write_json(contribution_dir / "recipes.json", recipes)

    example = {
        "source_type": "synthetic-public",
        "generated_at": "2026-05-11T00:00:00Z",
        "task_type": "public-page-summary",
        "input": {"url": "https://example.org/"},
        "expected_output": {
            "title": "Example Domain",
            "heading": "Example Domain",
            "summary": "This domain is for use in illustrative examples in documents.",
            "verified_selectors": ["page_heading"],
        },
    }
    write_json(contribution_dir / "examples" / "synthetic-example.json", example)

    pr_summary = """# Community Domain Skill PR Summary

## Domain and Supported Tasks

- Domain: `example.org`
- Supported tasks: public page summary, title and heading extraction

## Files Added or Changed

- `SKILL.md`
- `metadata.json`
- `selectors.json`
- `recipes.json`
- `examples/synthetic-example.json`
- `REVIEW_CHECKLIST.md`

## Verification

- Date: 2026-05-11
- Environment: deterministic Track 5 pilot script
- Result: metadata, selectors, recipes, example payload, and import trust-state checks passed

## Sensitive-Data Review

This contribution includes only public/synthetic example.org data and no credentials, private traces, browser profiles, screenshots, or account-specific state.

## Compatibility Notes

- Hermes Agent: `>=0.13.0`
- Hermes Browser Workspace: `>=0.1.0`

## Reviewer Notes

Local consumers must import this as a draft and keep it pending review until locally verified.
"""
    (contribution_dir / "PR_SUMMARY.md").write_text(pr_summary, encoding="utf-8")

    checklist = (contribution_dir / "REVIEW_CHECKLIST.md").read_text(encoding="utf-8")
    checklist = checklist.replace("- [ ]", "- [x]")
    checklist = checklist.replace("Reviewer:\n", "Reviewer: Track 5 pilot maintainer\n")
    checklist = checklist.replace("Date:\n", "Date: 2026-05-11\n")
    checklist = checklist.replace("Notes:\n", "Notes: Deterministic sample contribution passed static and import trust-state checks.\n")
    (contribution_dir / "REVIEW_CHECKLIST.md").write_text(checklist, encoding="utf-8")

    return contribution_dir


def validate_contribution(contribution_dir: Path) -> dict[str, Any]:
    missing = sorted(str(path) for path in REQUIRED_FILES if not (contribution_dir / path).exists())
    if missing:
        raise AssertionError(f"missing required files: {missing}")

    metadata = json.loads((contribution_dir / "metadata.json").read_text(encoding="utf-8"))
    missing_metadata = sorted(REQUIRED_METADATA_FIELDS - set(metadata))
    if missing_metadata:
        raise AssertionError(f"missing metadata fields: {missing_metadata}")
    if metadata["domain"] != "example.org":
        raise AssertionError("domain metadata does not match contribution directory")
    if metadata["trust_state"] != "community_proposed":
        raise AssertionError("community contribution must use community_proposed trust_state")
    if metadata["status"] != "draft" or metadata["approval_state"] != "pending_review":
        raise AssertionError("community contribution must remain draft/pending_review")

    selectors = json.loads((contribution_dir / "selectors.json").read_text(encoding="utf-8"))
    for name, selector in selectors.get("selectors", {}).items():
        if not selector.get("selector") or not selector.get("purpose") or not selector.get("stability"):
            raise AssertionError(f"selector lacks selector/purpose/stability: {name}")

    recipes = json.loads((contribution_dir / "recipes.json").read_text(encoding="utf-8"))
    for recipe in recipes.get("recipes", []):
        if not recipe.get("steps") or not recipe.get("expected_output") or not recipe.get("safety_notes"):
            raise AssertionError(f"recipe lacks steps/output/safety notes: {recipe.get('name')}")

    for payload in [
        contribution_dir / "metadata.json",
        contribution_dir / "selectors.json",
        contribution_dir / "recipes.json",
        contribution_dir / "examples" / "synthetic-example.json",
        contribution_dir / "SKILL.md",
        contribution_dir / "PR_SUMMARY.md",
    ]:
        text = payload.read_text(encoding="utf-8")
        if re.search(r"(?i)(actual[_-]?cookie|bearer\s+[a-z0-9]|sk-[a-z0-9])", text):
            raise AssertionError(f"high-confidence secret pattern found in {payload}")

    checklist = (contribution_dir / "REVIEW_CHECKLIST.md").read_text(encoding="utf-8")
    if "- [ ]" in checklist:
        raise AssertionError("review checklist still has incomplete items")

    return {"metadata": metadata, "selectors": selectors, "recipes": recipes}


def simulate_import_cycle(contribution_dir: Path, parsed: dict[str, Any], root: Path) -> dict[str, Any]:
    source_workspace = root / "source-workspace"
    consumer_workspace = root / "consumer-workspace"
    example_payload = json.loads((contribution_dir / "examples" / "synthetic-example.json").read_text(encoding="utf-8"))

    save_domain_skill(
        source_workspace,
        domain="example.org",
        skill_markdown=(contribution_dir / "SKILL.md").read_text(encoding="utf-8"),
        metadata=parsed["metadata"],
        selectors=parsed["selectors"],
        examples=[example_payload],
        extraction_recipes=parsed["recipes"]["recipes"],
    )
    source_metadata = validate_domain_skill(source_workspace, "example.org")
    if source_metadata["trust_state"] != "community_proposed":
        raise AssertionError("source community trust_state was not preserved")

    exported = export_domain_skill_package(source_workspace, "example.org", package_name="example-org-community-pilot", as_zip=True)
    imported = import_domain_skill_package(consumer_workspace, exported["package_path"], import_mode="draft")
    expected = {
        "status": "draft",
        "approval_state": "pending_review",
        "trust_state": "community_proposed",
        "verification_status": "imported_unverified",
    }
    for key, value in expected.items():
        if imported[key] != value:
            raise AssertionError(f"imported {key}={imported[key]!r}, expected {value!r}")

    return {"package_path": exported["package_path"], "imported": imported}


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="hbw-track5-") as temp:
        root = Path(temp)
        contribution_dir = build_sample_contribution(root)
        parsed = validate_contribution(contribution_dir)
        import_result = simulate_import_cycle(contribution_dir, parsed, root)

    print("Track 5 community contribution pilot passed")
    print("- required files validated:", ", ".join(sorted(REQUIRED_FILES)))
    print("- sample domain: example.org")
    print("- imported state:", json.dumps(import_result["imported"], sort_keys=True))


if __name__ == "__main__":
    main()
