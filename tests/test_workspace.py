from pathlib import Path

from hermes_browser_workspace.workspace import bootstrap_workspace, create_session_context


def test_bootstrap_workspace_creates_expected_files(tmp_path: Path) -> None:
    result = bootstrap_workspace(tmp_path)
    assert Path(result["config"]).exists()
    assert Path(result["helpers"]).exists()
    assert Path(result["domain_skills"]).is_dir()


def test_create_session_context_creates_paths(tmp_path: Path) -> None:
    bootstrap_workspace(tmp_path)
    session = create_session_context(tmp_path, "test-session")
    assert session.session_dir.exists()
    assert session.outputs_dir.exists()
    assert session.screenshots_dir.exists()
    assert session.traces_dir.exists()
    assert session.metadata_path.exists()
