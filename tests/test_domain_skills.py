import json
from pathlib import Path

from hermes_browser_workspace.domain_skills import save_domain_skill, search_domain_skills, validate_domain_skill
from hermes_browser_workspace.workspace import bootstrap_workspace


def test_save_and_search_domain_skill(tmp_path: Path) -> None:
    bootstrap_workspace(tmp_path)
    save_domain_skill(
        tmp_path,
        domain="github.com",
        skill_markdown="# GitHub\n\nUse stable selectors.\n",
        metadata={"title": "GitHub", "tags": ["repo", "issues"], "status": "active"},
        selectors={"repo_name": "[itemprop='name']"},
    )
    results = search_domain_skills(tmp_path, domain="github.com")
    assert len(results) == 1
    metadata = validate_domain_skill(tmp_path, "github.com")
    assert metadata["domain"] == "github.com"
    assert metadata["status"] == "active"
    selectors = json.loads((tmp_path / "domain-skills" / "github.com" / "selectors.json").read_text(encoding="utf-8"))
    assert "repo_name" in selectors
