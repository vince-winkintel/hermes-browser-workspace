import pytest

from hermes_browser_workspace.safety import SafetyError, ensure_relative_path, method_allowed


def test_rejects_parent_path_traversal() -> None:
    with pytest.raises(SafetyError):
        ensure_relative_path("../escape.txt")


def test_cdp_method_policy() -> None:
    assert method_allowed("Runtime.evaluate", ["Runtime.", "Page."], ["Network.getCookies"]) is True
    assert method_allowed("Network.getCookies", ["Runtime.", "Page.", "Network."], ["Network.getCookies"]) is False
