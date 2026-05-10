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
    assert "browser_workspace_mark_domain_skill_verified" in names
    assert "browser_workspace_save_domain_skill_recipes" in names
    assert "browser_workspace_list_domain_skill_recipes" in names
    assert "browser_workspace_export_domain_skill_package" in names
    assert "browser_workspace_import_domain_skill_package" in names
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


def test_phase3_tool_handlers_work_end_to_end(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_BROWSER_WORKSPACE_ROOT", str(tmp_path))
    plugin = get_plugin()
    ctx = FakeContext()
    plugin.register(ctx)
    tools = {tool["name"]: tool for tool in ctx.tools}

    saved = json.loads(
        tools["browser_workspace_save_domain_skill"]["handler"](
            {
                "domain": "github.com",
                "skill_markdown": "# GitHub\n",
                "metadata": {"title": "GitHub", "status": "active"},
                "examples": [{"task": "Open repo", "output": "Repo page"}],
                "extraction_recipes": [{"name": "repo_name", "steps": [{"action": "extract", "field": "repo_name", "selector": "[itemprop='name']"}]}],
            }
        )
    )
    assert saved["success"] is True

    verified = json.loads(
        tools["browser_workspace_mark_domain_skill_verified"]["handler"](
            {"domain": "github.com", "verified_by": "vinny", "verification_notes": "Reviewed locally."}
        )
    )
    assert verified["success"] is True
    assert verified["data"]["verification_status"] == "verified"

    example = json.loads(
        tools["browser_workspace_add_domain_skill_example"]["handler"](
            {"domain": "github.com", "example": {"task": "Find issues", "output": "Issues tab"}}
        )
    )
    assert example["success"] is True
    assert example["data"]["example_count"] == 2

    recipes_saved = json.loads(
        tools["browser_workspace_save_domain_skill_recipes"]["handler"](
            {
                "domain": "github.com",
                "recipes": [{"name": "issue_title", "steps": [{"action": "extract", "field": "title", "selector": "h1"}]}],
            }
        )
    )
    assert recipes_saved["success"] is True
    recipes_listed = json.loads(tools["browser_workspace_list_domain_skill_recipes"]["handler"]({"domain": "github.com"}))
    assert recipes_listed["success"] is True
    assert recipes_listed["data"]["count"] == 1

    exported = json.loads(
        tools["browser_workspace_export_domain_skill_package"]["handler"](
            {"domain": "github.com", "package_name": "github-skill", "as_zip": False}
        )
    )
    assert exported["success"] is True

    stale = json.loads(tools["browser_workspace_list_stale_domain_skills"]["handler"]({"threshold_days": 1}))
    assert stale["success"] is True
    assert stale["data"]["results"] == []

    imported = json.loads(
        tools["browser_workspace_import_domain_skill_package"]["handler"]({"package_path": exported["data"]["package_path"]})
    )
    assert imported["success"] is True
    assert imported["data"]["approval_state"] == "pending_review"
