from pathlib import Path

from hermes_browser_workspace.domain_skills import (
    export_domain_skill_package,
    import_domain_skill_package,
    save_domain_skill,
    validate_domain_skill,
)
from hermes_browser_workspace.workspace import bootstrap_workspace


def test_community_proposed_trust_state_round_trips_as_untrusted_import(tmp_path: Path) -> None:
    source = tmp_path / "source"
    consumer = tmp_path / "consumer"
    bootstrap_workspace(source)
    bootstrap_workspace(consumer)

    save_domain_skill(
        source,
        domain="example.org",
        skill_markdown="# Example.org\n\nPublic community contribution.\n",
        metadata={
            "title": "Example.org Public Demo Skill",
            "status": "draft",
            "approval_state": "pending_review",
            "trust_state": "community_proposed",
            "verification_status": "community_verified",
            "supported_task_types": ["public-page-summary"],
            "source_repository": "https://github.com/example/example.org-browser-skill",
            "source_commit": "0000000000000000000000000000000000000000",
        },
        selectors={
            "selectors": {
                "page_heading": {
                    "selector": "h1",
                    "type": "css",
                    "purpose": "Read public heading.",
                    "stability": "high",
                }
            },
            "fallbacks": [],
            "sensitive_fields": [],
        },
        examples=[{"source_type": "synthetic-public", "task_type": "public-page-summary"}],
        extraction_recipes=[
            {
                "name": "extract_public_summary",
                "steps": ["Open the public page.", "Read heading."],
                "expected_output": {"type": "object", "required_fields": ["heading"]},
                "safety_notes": ["Public page only."],
            }
        ],
    )

    source_metadata = validate_domain_skill(source, "example.org")
    assert source_metadata["trust_state"] == "community_proposed"

    export_result = export_domain_skill_package(source, "example.org", package_name="example-org-community", as_zip=True)
    imported = import_domain_skill_package(consumer, export_result["package_path"])

    assert imported["status"] == "draft"
    assert imported["approval_state"] == "pending_review"
    assert imported["trust_state"] == "community_proposed"
    assert imported["verification_status"] == "imported_unverified"
