import json
from pathlib import Path

import pytest

from hermes_browser_workspace.domain_skills import draft_domain_skill, validate_domain_skill_draft
from hermes_browser_workspace.safety import SafetyError
from hermes_browser_workspace.workspace import bootstrap_workspace


def test_draft_domain_skill_persists_redacted_inputs(tmp_path: Path) -> None:
    bootstrap_workspace(tmp_path)
    result = draft_domain_skill(
        tmp_path,
        domain="github.com",
        title="GitHub Draft",
        observations=["Use stable repo header selectors."],
        selectors={"repo_name": {"selector": "[itemprop='name']"}, "authToken": "secret"},
        examples=[{"prompt": "Open repo", "authorization": "Bearer abc"}],
        extraction_recipes=[{"name": "repo_name", "steps": [{"action": "extract", "field": "repo_name", "selector": "[itemprop='name']"}]}],
        session_id="session-2",
        task_id="task-2",
    )
    draft_path = Path(result["path"])
    metadata = json.loads((draft_path / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["kind"] == "domain_skill_draft"
    assert metadata["validation"]["selectors"]["ok"] is False
    assert metadata["validation"]["recipes"]["ok"] is True
    examples = json.loads((draft_path / "examples.json").read_text(encoding="utf-8"))
    assert examples["examples"][0]["authorization"] == "[REDACTED]"


def test_validate_domain_skill_draft_writes_report(tmp_path: Path) -> None:
    bootstrap_workspace(tmp_path)
    result = draft_domain_skill(
        tmp_path,
        domain="github.com",
        selectors={"repo_name": "[itemprop='name']"},
        helpers_code="def parse_repo():\n    return True\n",
    )
    validate = validate_domain_skill_draft(tmp_path, result["draft_id"])
    assert validate["validation"]["selectors"]["ok"] is True
    report = json.loads((Path(result["path"]) / "validation-report.json").read_text(encoding="utf-8"))
    assert report["kind"] == "domain_skill_validation_report"


def test_domain_skill_draft_id_rejects_path_traversal(tmp_path: Path) -> None:
    bootstrap_workspace(tmp_path)
    with pytest.raises(SafetyError):
        validate_domain_skill_draft(tmp_path, "../escape")
