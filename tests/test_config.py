from pathlib import Path

from hermes_browser_workspace.config import BrowserWorkspaceConfig, default_config_text, load_config


def test_default_config_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "config.yaml"
    path.write_text(default_config_text(tmp_path), encoding="utf-8")
    config = load_config(path)
    assert isinstance(config, BrowserWorkspaceConfig)
    assert config.workspace_root == tmp_path.resolve()
    assert config.browser_workspace_cdp_enabled is True
    assert config.real_chrome_profile_enabled is False
    assert config.stale_skill_warning_days == 30
