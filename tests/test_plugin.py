import json

from hermes_browser_workspace.plugin import get_plugin, register


class FakeContext:
    def __init__(self):
        self.tools = []

    def register_tool(self, **kwargs):
        self.tools.append(kwargs)


def test_directory_register_exposes_browser_workspace_tools(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_BROWSER_WORKSPACE_ROOT", str(tmp_path))
    ctx = FakeContext()
    register(ctx)
    names = {tool["name"] for tool in ctx.tools}
    assert "browser_workspace_doctor" in names
    assert "browser_workspace_cdp" in names
    assert "browser_workspace_list_helper_proposals" in names
    assert "browser_workspace_draft_domain_skill" in names
    assert "browser_workspace_cleanup_artifacts" in names
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


def test_phase2_tool_handlers_work_end_to_end(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_BROWSER_WORKSPACE_ROOT", str(tmp_path))
    plugin = get_plugin()
    ctx = FakeContext()
    plugin.register(ctx)
    tools = {tool["name"]: tool for tool in ctx.tools}

    proposal = json.loads(
        tools["browser_workspace_propose_helper_update"]["handler"](
            {"proposed_content": 'def helper():\n    return "ok"\n', "session_id": "s1"}
        )
    )
    assert proposal["success"] is True
    proposal_id = proposal["data"]["proposal_id"]

    validate = json.loads(tools["browser_workspace_validate_helper_proposal"]["handler"]({"proposal_id": proposal_id}))
    assert validate["success"] is True
    assert validate["data"]["validation"]["ok"] is True

    draft = json.loads(
        tools["browser_workspace_draft_domain_skill"]["handler"](
            {"domain": "github.com", "observations": ["Use repo header selectors."]}
        )
    )
    assert draft["success"] is True

    listed = json.loads(tools["browser_workspace_list_artifacts"]["handler"]({"session_id": "s1"}))
    assert listed["success"] is True
    assert any(item["kind"] == "helper_proposal" for item in listed["data"]["results"])
