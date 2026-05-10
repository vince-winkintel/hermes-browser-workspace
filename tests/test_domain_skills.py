import json
from pathlib import Path

from hermes_browser_workspace.config import BrowserWorkspaceConfig
from hermes_browser_workspace.domain_skills import (
    add_domain_skill_example,
    export_domain_skill_package,
    import_domain_skill_package,
    list_domain_skill_examples,
    list_stale_domain_skills,
    mark_domain_skill_verified,
    save_domain_skill,
    search_domain_skills,
    validate_domain_skill,
)
from hermes_browser_workspace.safety import SafetyError
from hermes_browser_workspace.workspace import bootstrap_workspace
import pytest


def test_save_and_search_domain_skill_phase3_metadata(tmp_path: Path) -> None:
    bootstrap_workspace(tmp_path)
    save_domain_skill(
        tmp_path,
        domain="github.com",
        skill_markdown="# GitHub\n\nUse stable selectors.\n",
        metadata={
            "title": "GitHub",
            "tags": ["repo", "issues"],
            "status": "active",
            "supported_task_types": ["navigation", "extraction"],
            "confidence": "medium",
            "reliability": "reviewed_locally",
            "source_package": "hermes-browser-workspace",
            "source_import": "local://skills/github.com",
        },
        selectors={"repo_name": "[itemprop='name']"},
        examples=[{"task": "Open repo", "authorization": "Bearer abc"}],
        extraction_recipes=[{"name": "repo_name", "steps": [{"action": "extract", "field": "repo_name", "selector": "[itemprop='name']"}]}],
    )
    results = search_domain_skills(tmp_path, domain="github.com")
    assert len(results) == 1
    assert results[0]["example_count"] == 1
    assert results[0]["recipe_count"] == 1
    metadata = validate_domain_skill(tmp_path, "github.com")
    assert metadata["domain"] == "github.com"
    assert metadata["status"] == "active"
    assert metadata["schema_version"] == "1.1"
    assert metadata["supported_task_types"] == ["navigation", "extraction"]
    assert metadata["verification_status"] == "unverified"
    examples = json.loads((tmp_path / "domain-skills" / "github.com" / "examples" / "index.json").read_text(encoding="utf-8"))
    assert examples["examples"][0]["authorization"] == "[REDACTED]"
    recipes = json.loads((tmp_path / "domain-skills" / "github.com" / "recipes.json").read_text(encoding="utf-8"))
    assert recipes["recipes"][0]["name"] == "repo_name"


def test_mark_verified_and_list_stale_domain_skills(tmp_path: Path) -> None:
    bootstrap_workspace(tmp_path)
    save_domain_skill(
        tmp_path,
        domain="github.com",
        skill_markdown="# GitHub\n",
        metadata={"title": "GitHub", "status": "active"},
    )
    stale = list_stale_domain_skills(tmp_path, BrowserWorkspaceConfig(workspace_root=tmp_path), threshold_days=7)
    assert stale["results"][0]["reason"] == "never_verified"
    verified = mark_domain_skill_verified(tmp_path, "github.com", verified_by="vinny", verification_notes="Reviewed locally.")
    assert verified["verification_status"] == "verified"
    fresh = list_stale_domain_skills(tmp_path, BrowserWorkspaceConfig(workspace_root=tmp_path), threshold_days=7)
    assert fresh["results"] == []


def test_add_and_list_domain_skill_examples(tmp_path: Path) -> None:
    bootstrap_workspace(tmp_path)
    save_domain_skill(
        tmp_path,
        domain="github.com",
        skill_markdown="# GitHub\n",
        metadata={"title": "GitHub", "status": "active"},
    )
    added = add_domain_skill_example(tmp_path, "github.com", {"task": "Find PR", "output": "Opened pull requests tab"})
    assert added["example_count"] == 1
    listed = list_domain_skill_examples(tmp_path, "github.com")
    assert listed["count"] == 1
    assert listed["examples"][0]["task"] == "Find PR"


def test_export_and_import_domain_skill_package_stays_pending_review(tmp_path: Path) -> None:
    bootstrap_workspace(tmp_path)
    save_domain_skill(
        tmp_path,
        domain="github.com",
        skill_markdown="# GitHub\n",
        metadata={"title": "GitHub", "status": "active", "trust_state": "trusted_local"},
        selectors={"repo_name": "[itemprop='name']"},
        examples=[{"task": "Open repo", "output": "Repo page"}],
    )
    export_result = export_domain_skill_package(tmp_path, "github.com", package_name="github-skill", as_zip=False)
    skill_dir = tmp_path / "domain-skills" / "github.com"
    for child in list(skill_dir.iterdir()):
        if child.is_dir():
            for nested in child.rglob("*"):
                if nested.is_file():
                    nested.unlink()
            for nested in sorted(child.rglob("*"), reverse=True):
                if nested.is_dir():
                    nested.rmdir()
            child.rmdir()
        else:
            child.unlink()
    skill_dir.rmdir()
    imported = import_domain_skill_package(tmp_path, export_result["package_path"])
    assert imported["status"] == "draft"
    assert imported["approval_state"] == "pending_review"
    assert imported["trust_state"] == "model_proposed"
    metadata = validate_domain_skill(tmp_path, "github.com")
    assert metadata["verification_status"] == "imported_unverified"
    assert metadata["imported_from"]["import_mode"] == "draft"


def test_import_domain_skill_package_rejects_checksum_mismatch(tmp_path: Path) -> None:
    bootstrap_workspace(tmp_path)
    save_domain_skill(
        tmp_path,
        domain="github.com",
        skill_markdown="# GitHub\n",
        metadata={"title": "GitHub", "status": "active"},
    )
    export_result = export_domain_skill_package(tmp_path, "github.com", package_name="github-skill", as_zip=False)
    skill_file = Path(export_result["package_path"]) / "github.com" / "SKILL.md"
    skill_file.write_text("# Tampered\n", encoding="utf-8")
    with pytest.raises(SafetyError, match="checksum mismatch"):
        import_domain_skill_package(tmp_path, export_result["package_path"])
