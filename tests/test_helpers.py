import json
from pathlib import Path

import pytest

from hermes_browser_workspace.config import BrowserWorkspaceConfig
from hermes_browser_workspace.helpers import (
    list_helper_proposals,
    propose_helper_update,
    read_helper_proposal,
    review_helper_proposal,
    validate_helper_proposal,
)
from hermes_browser_workspace.safety import SafetyError
from hermes_browser_workspace.workspace import bootstrap_workspace


def test_helper_proposal_review_flow(tmp_path: Path) -> None:
    bootstrap_workspace(tmp_path)
    config = BrowserWorkspaceConfig(workspace_root=tmp_path)
    result = propose_helper_update(
        tmp_path,
        config,
        proposed_content='def helper():\n    return "ok"\n',
        session_id="session-1",
        task_id="task-1",
    )
    proposal = read_helper_proposal(tmp_path, result["proposal_id"])
    assert proposal["status"] == "pending_review"
    assert proposal["session_id"] == "session-1"
    validate = validate_helper_proposal(tmp_path, result["proposal_id"])
    assert validate["validation"]["ok"] is True
    review = review_helper_proposal(tmp_path, result["proposal_id"], "approved", "vinny", "Looks safe.")
    assert review["status"] == "approved"
    listed = list_helper_proposals(tmp_path, status="approved")
    assert len(listed) == 1
    report_path = tmp_path / "sessions" / "helper-proposals" / f'{result["proposal_id"]}.validation.json'
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["kind"] == "helper_validation_report"


def test_helper_validation_rejects_unsafe_calls(tmp_path: Path) -> None:
    bootstrap_workspace(tmp_path)
    config = BrowserWorkspaceConfig(workspace_root=tmp_path)
    result = propose_helper_update(
        tmp_path,
        config,
        proposed_content="import subprocess\n\nsubprocess.run(['whoami'])\n",
    )
    validate = validate_helper_proposal(tmp_path, result["proposal_id"])
    assert validate["validation"]["ok"] is False
    assert any("subprocess" in error for error in validate["validation"]["errors"])


def test_helper_proposal_id_rejects_path_traversal(tmp_path: Path) -> None:
    bootstrap_workspace(tmp_path)
    with pytest.raises(SafetyError):
        read_helper_proposal(tmp_path, "../escape")


def test_review_notes_are_scrubbed_before_persist(tmp_path: Path) -> None:
    bootstrap_workspace(tmp_path)
    config = BrowserWorkspaceConfig(workspace_root=tmp_path)
    result = propose_helper_update(tmp_path, config, proposed_content="def helper():\n    return 1\n")
    review_helper_proposal(tmp_path, result["proposal_id"], "rejected", "vinny", {"token": "secret-value"})
    payload = read_helper_proposal(tmp_path, result["proposal_id"])
    assert payload["decision_notes"]["token"] == "[REDACTED]"


def test_helper_proposal_content_redacts_sensitive_assignments(tmp_path: Path) -> None:
    bootstrap_workspace(tmp_path)
    config = BrowserWorkspaceConfig(workspace_root=tmp_path)
    result = propose_helper_update(tmp_path, config, proposed_content='TOKEN = "secret-value"\n')
    payload = read_helper_proposal(tmp_path, result["proposal_id"])
    assert "secret-value" not in payload["proposed_content"]
    assert "secret-value" not in payload["diff"]
    assert "secret-value" not in result["diff"]
