from pathlib import Path

from hermes_browser_workspace.workspace import bootstrap_workspace, create_session_context, load_template_helpers_text


def test_bootstrap_workspace_creates_expected_files(tmp_path: Path) -> None:
    result = bootstrap_workspace(tmp_path)
    assert Path(result["config"]).exists()
    assert Path(result["helpers"]).exists()
    assert Path(result["domain_skills"]).is_dir()


def test_bootstrap_workspace_uses_packaged_helper_template(tmp_path: Path) -> None:
    result = bootstrap_workspace(tmp_path)
    helpers_text = Path(result["helpers"]).read_text(encoding="utf-8")
    assert helpers_text == load_template_helpers_text()
    assert "normalize_text" in helpers_text


def test_create_session_context_creates_paths(tmp_path: Path) -> None:
    bootstrap_workspace(tmp_path)
    session = create_session_context(tmp_path, "test-session")
    assert session.session_dir.exists()
    assert session.outputs_dir.exists()
    assert session.screenshots_dir.exists()
    assert session.traces_dir.exists()
    assert session.metadata_path.exists()
