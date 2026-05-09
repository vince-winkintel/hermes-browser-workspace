import json

from hermes_browser_workspace.plugin import get_plugin, register


class FakeContext:
    def __init__(self):
        self.tools = []

    def register_tool(self, **kwargs):
        self.tools.append(kwargs)


def test_directory_register_exposes_hardware_workspace_tools(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_BROWSER_WORKSPACE_ROOT", str(tmp_path))
    ctx = FakeContext()
    register(ctx)
    names = {tool["name"] for tool in ctx.tools}
    assert "browser_workspace_doctor" in names
    assert "browser_workspace_cdp" in names
    assert all(tool["toolset"] == "browser_workspace" for tool in ctx.tools)
    assert all(callable(tool["handler"]) for tool in ctx.tools)


def test_registered_handler_returns_json(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_BROWSER_WORKSPACE_ROOT", str(tmp_path))
    plugin = get_plugin()
    ctx = FakeContext()
    plugin.register(ctx)
    doctor = next(tool for tool in ctx.tools if tool["name"] == "browser_workspace_doctor")
    payload = json.loads(doctor["handler"]({}))
    assert payload["success"] is True
    assert payload["data"]["checks"]["cdp_enabled"] is True
