from pathlib import Path

from hermes_browser_workspace.artifacts import cleanup_artifacts, list_artifacts
from hermes_browser_workspace.config import BrowserWorkspaceConfig
from hermes_browser_workspace.domain_skills import draft_domain_skill
from hermes_browser_workspace.helpers import propose_helper_update, review_helper_proposal
from hermes_browser_workspace.workspace import bootstrap_workspace


def test_list_artifacts_filters_by_kind_and_status(tmp_path: Path) -> None:
    bootstrap_workspace(tmp_path)
    config = BrowserWorkspaceConfig(workspace_root=tmp_path)
    proposal = propose_helper_update(tmp_path, config, proposed_content="def helper():\n    return 1\n", session_id="s1")
    review_helper_proposal(tmp_path, proposal["proposal_id"], "rejected", "vinny", "no")
    draft_domain_skill(tmp_path, domain="github.com", session_id="s1")
    rejected = list_artifacts(tmp_path, kind="helper_proposal", status="rejected")
    assert len(rejected) == 1
    assert rejected[0]["session_id"] == "s1"


def test_cleanup_artifacts_dry_run_then_delete(tmp_path: Path) -> None:
    bootstrap_workspace(tmp_path)
    config = BrowserWorkspaceConfig(workspace_root=tmp_path, retention_days=0)
    proposal = propose_helper_update(tmp_path, config, proposed_content="def helper():\n    return 1\n")
    dry_run = cleanup_artifacts(tmp_path, config, older_than_days=0, dry_run=True, kind="helper_proposal")
    assert len(dry_run["matches"]) == 1
    deleted = cleanup_artifacts(tmp_path, config, older_than_days=0, dry_run=False, kind="helper_proposal")
    assert len(deleted["deleted"]) == 1
    assert not Path(proposal["proposal_path"]).exists()
