#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path

from hermes_browser_workspace.plugin import get_plugin


class FakeContext:
    def __init__(self):
        self.tools = []

    def register_tool(self, **kwargs):
        self.tools.append(kwargs)


def register_tools(root: Path):
    os.environ["HERMES_BROWSER_WORKSPACE_ROOT"] = str(root)
    plugin = get_plugin()
    ctx = FakeContext()
    plugin.register(ctx)
    return {tool["name"]: tool for tool in ctx.tools}


def call(tools, name: str, payload: dict):
    raw = tools[name]["handler"](payload)
    parsed = json.loads(raw)
    if not parsed.get("success"):
        raise RuntimeError(f"{name} failed: {parsed}")
    return parsed["data"]


def main() -> None:
    base = Path(tempfile.mkdtemp(prefix="hbw-track4-dogfood-"))
    source_root = base / "source-workspace"
    import_root = base / "import-workspace"
    session_id = "track4-example-org"
    task_id = "t_9f30cf66"
    domain = "example.org"

    tools = register_tools(source_root)
    doctor = call(tools, "browser_workspace_doctor", {})

    capture = call(
        tools,
        "browser_workspace_capture",
        {
            "session_id": session_id,
            "name": "example-org-accessibility-snapshot",
            "metadata": {
                "kind": "browser_snapshot",
                "domain": domain,
                "url": "https://example.org/",
                "title": "Example Domain",
                "observations": [
                    "Public low-risk documentation domain.",
                    "Page has one h1: Example Domain.",
                    "Primary paragraph explains the domain is reserved for documentation examples.",
                    "Only obvious outbound action is the Learn more link.",
                ],
                "selectors": {
                    "heading": "h1",
                    "learn_more_link": "a[href^='https://www.iana.org/']",
                },
            },
        },
    )

    helper_content = call(tools, "browser_workspace_read_helpers", {})["content"]
    proposed_helper = (
        helper_content.rstrip()
        + "\n\n"
        + "def extract_example_org_summary(document):\n"
        + "    \"\"\"Return the example.org heading and primary text from a parsed document.\"\"\"\n"
        + "    heading = document.querySelector('h1')\n"
        + "    paragraph = document.querySelector('p')\n"
        + "    return {\n"
        + "        'heading': heading.textContent.strip() if heading else None,\n"
        + "        'summary': paragraph.textContent.strip() if paragraph else None,\n"
        + "    }\n"
    )
    proposal = call(
        tools,
        "browser_workspace_propose_helper_update",
        {"proposed_content": proposed_helper, "session_id": session_id, "task_id": task_id},
    )
    proposal_id = proposal["proposal_id"]
    helper_validation = call(tools, "browser_workspace_validate_helper_proposal", {"proposal_id": proposal_id})
    helper_review = call(
        tools,
        "browser_workspace_review_helper_proposal",
        {
            "proposal_id": proposal_id,
            "decision": "approved",
            "reviewer": "Victor dogfood run",
            "decision_notes": "Inspect-only validation passed; proposal was not auto-applied.",
        },
    )

    selectors = {
        "heading": {"selector": "h1", "purpose": "Extract page heading", "stability": "high"},
        "summary": {"selector": "p", "purpose": "Extract primary explanatory text", "stability": "high"},
        "learn_more_link": {
            "selector": "a[href^='https://www.iana.org/']",
            "purpose": "Find the IANA more-information link",
            "stability": "medium",
        },
    }
    examples = [
        {
            "task": "Summarize example.org landing page",
            "input": "https://example.org/",
            "output": "Example Domain page reserved for documentation examples.",
        }
    ]
    recipes = [
        {
            "name": "example_org_page_summary",
            "description": "Extract the public example.org heading, summary paragraph, and learn-more link.",
            "steps": [
                {"action": "extract", "field": "heading", "selector": "h1"},
                {"action": "extract", "field": "summary", "selector": "p"},
                {"action": "extract", "field": "learn_more_href", "selector": "a[href^='https://www.iana.org/']", "attribute": "href"},
            ],
        }
    ]
    skill_markdown = """# Example.org Browser Skill

## Use Cases
- Verify browser automation and extraction plumbing against a stable public documentation page.
- Practice selector capture without account state, cookies, or private data.

## Navigation Notes
- Navigate to `https://example.org/`.
- Expect a single `h1` with `Example Domain`.
- Expect one primary explanatory paragraph and one `Learn more` link to IANA.

## Safety Notes
- Do not store cookies or local storage.
- This skill is intentionally low-risk and public-data only.
"""

    draft = call(
        tools,
        "browser_workspace_draft_domain_skill",
        {
            "domain": domain,
            "title": "Example.org Browser Skill",
            "observations": [
                "Use example.org for public, deterministic browser-workspace smoke exercises.",
                "Selectors are intentionally simple and stable: h1, p, and IANA Learn more link.",
                "No authenticated state or private data is involved.",
            ],
            "selectors": selectors,
            "examples": examples,
            "extraction_recipes": recipes,
            "helpers_code": "def noop():\n    return None\n",
            "session_id": session_id,
            "task_id": task_id,
        },
    )
    draft_validation = call(tools, "browser_workspace_validate_domain_skill", {"draft_id": draft["draft_id"]})

    saved = call(
        tools,
        "browser_workspace_save_domain_skill",
        {
            "domain": domain,
            "skill_markdown": skill_markdown,
            "metadata": {
                "title": "Example.org Browser Skill",
                "status": "active",
                "trust_state": "human_reviewed",
                "approval_state": "approved",
                "author_type": "model_proposed",
                "tags": ["dogfood", "public", "synthetic", "browser-workspace"],
                "supported_task_types": ["extraction", "browser-smoke-test"],
            },
            "selectors": selectors,
            "helpers_code": "def extract_expected_heading():\n    return 'Example Domain'\n",
            "examples": examples,
            "extraction_recipes": recipes,
        },
    )
    extra_example = call(
        tools,
        "browser_workspace_add_domain_skill_example",
        {
            "domain": domain,
            "example": {
                "task": "Check learn-more affordance",
                "input": "Find the only link on the page.",
                "output": "Learn more link points to IANA documentation.",
            },
        },
    )
    recipes_saved = call(tools, "browser_workspace_save_domain_skill_recipes", {"domain": domain, "recipes": recipes})
    examples_listed = call(tools, "browser_workspace_list_domain_skill_examples", {"domain": domain})
    recipes_listed = call(tools, "browser_workspace_list_domain_skill_recipes", {"domain": domain})
    verified = call(
        tools,
        "browser_workspace_mark_domain_skill_verified",
        {
            "domain": domain,
            "verified_by": "Victor dogfood run",
            "verification_notes": "Verified against live example.org snapshot captured during Track 4 dogfood.",
            "verification_status": "verified",
            "confidence": "high",
            "reliability": "stable-public-page",
        },
    )
    stale = call(tools, "browser_workspace_list_stale_domain_skills", {"threshold_days": 1})
    search = call(tools, "browser_workspace_search_domain_skills", {"domain": domain})
    artifacts = call(tools, "browser_workspace_list_artifacts", {"session_id": session_id})
    cleanup = call(tools, "browser_workspace_cleanup_artifacts", {"older_than_days": 0, "dry_run": True, "session_id": session_id})
    exported = call(
        tools,
        "browser_workspace_export_domain_skill_package",
        {"domain": domain, "package_name": "example-org-track4-dogfood", "as_zip": True},
    )

    import_tools = register_tools(import_root)
    import_doctor = call(import_tools, "browser_workspace_doctor", {})
    imported = call(
        import_tools,
        "browser_workspace_import_domain_skill_package",
        {"package_path": exported["package_path"], "import_mode": "draft"},
    )
    imported_search = call(import_tools, "browser_workspace_search_domain_skills", {"domain": domain})

    summary = {
        "base": str(base),
        "source_root": str(source_root),
        "import_root": str(import_root),
        "tool_count": len(tools),
        "doctor_ok": doctor["checks"],
        "capture_path": capture["path"],
        "helper_proposal": proposal,
        "helper_validation_ok": helper_validation["validation"]["ok"],
        "helper_review": helper_review,
        "draft": draft,
        "draft_validation_ok": all(report["ok"] for report in draft_validation["validation"].values()),
        "saved": saved,
        "examples_count": examples_listed["count"],
        "extra_example": extra_example,
        "recipes_count": recipes_listed["count"],
        "recipes_saved": recipes_saved,
        "verified": verified,
        "stale_results": stale["results"],
        "search": search["results"],
        "artifact_kinds": sorted({item["kind"] for item in artifacts["results"]}),
        "artifact_count": len(artifacts["results"]),
        "cleanup_dry_run_matches": cleanup["matches"],
        "exported": exported,
        "import_doctor_ok": import_doctor["checks"],
        "imported": imported,
        "imported_search": imported_search["results"],
    }

    print(json.dumps(summary, indent=2, sort_keys=True))

    # Leave temp artifacts available for inspection by printing the base path. The caller can delete it later.


if __name__ == "__main__":
    main()
