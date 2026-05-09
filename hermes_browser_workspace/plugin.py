from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Callable

from .config import BrowserWorkspaceConfig
from .safety import SafetyError
from .tools import ToolRegistry
from .workspace import load_or_create_config

TOOLSET = "browser_workspace"


def _object_schema(properties: dict[str, Any] | None = None, required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties or {},
        "required": required or [],
        "additionalProperties": False,
    }


TOOL_SPECS: dict[str, dict[str, Any]] = {
    "browser_workspace_doctor": {
        "description": "Validate and bootstrap the local Hermes browser workspace.",
        "parameters": _object_schema(),
    },
    "browser_workspace_capture": {
        "description": "Record screenshot/capture metadata for a browser workspace session.",
        "parameters": _object_schema(
            {
                "session_id": {"type": "string"},
                "name": {"type": "string"},
                "metadata": {"type": "object"},
            },
            ["session_id", "name", "metadata"],
        ),
    },
    "browser_workspace_click_xy": {
        "description": "Record/prepare a coordinate fallback click with audit metadata.",
        "parameters": _object_schema(
            {
                "session_id": {"type": "string"},
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "screenshot_path": {"type": ["string", "null"]},
            },
            ["session_id", "x", "y"],
        ),
    },
    "browser_workspace_cdp": {
        "description": "Policy-check and audit a bounded CDP call. The actual CDP invocation remains with Hermes/browser runtime tools.",
        "parameters": _object_schema(
            {
                "session_id": {"type": "string"},
                "method": {"type": "string"},
                "params": {"type": "object"},
                "result": {"type": "object"},
                "task_id": {"type": ["string", "null"]},
            },
            ["session_id", "method"],
        ),
    },
    "browser_workspace_search_domain_skills": {
        "description": "Search local browser domain skills by domain and/or tags.",
        "parameters": _object_schema(
            {
                "domain": {"type": ["string", "null"]},
                "tags": {"type": ["array", "null"], "items": {"type": "string"}},
            }
        ),
    },
    "browser_workspace_save_domain_skill": {
        "description": "Explicitly save a local browser domain skill with provenance metadata.",
        "parameters": _object_schema(
            {
                "domain": {"type": "string"},
                "skill_markdown": {"type": "string"},
                "metadata": {"type": "object"},
                "selectors": {"type": ["object", "null"]},
                "helpers_code": {"type": ["string", "null"]},
            },
            ["domain", "skill_markdown", "metadata"],
        ),
    },
    "browser_workspace_read_helpers": {
        "description": "Read the local browser workspace helper file.",
        "parameters": _object_schema(),
    },
    "browser_workspace_propose_helper_update": {
        "description": "Persist a proposal/diff for helper updates without applying it.",
        "parameters": _object_schema(
            {
                "proposed_content": {"type": "string"},
                "session_id": {"type": ["string", "null"]},
                "task_id": {"type": ["string", "null"]},
            },
            ["proposed_content"],
        ),
    },
}


@dataclass
class BrowserWorkspacePlugin:
    name: str = "hermes-browser-workspace"

    def __post_init__(self) -> None:
        self.config: BrowserWorkspaceConfig | None = None
        self.registry: ToolRegistry | None = None

    def _get_registry(self) -> ToolRegistry:
        if self.registry is None:
            config = load_or_create_config(BrowserWorkspaceConfig().workspace_root)
            self.config = config
            self.registry = ToolRegistry(config)
        return self.registry

    def _handler_for(self, method_name: str) -> Callable[[dict[str, Any]], str]:
        def handler(args: dict[str, Any], **_: Any) -> str:
            try:
                method = getattr(self._get_registry(), method_name)
                return json.dumps({"success": True, "data": method(**(args or {}))})
            except SafetyError as exc:
                return json.dumps({"success": False, "error": str(exc), "error_type": "SafetyError"})
            except Exception as exc:  # defensive boundary for external plugin runtime
                return json.dumps({"success": False, "error": str(exc), "error_type": type(exc).__name__})

        return handler

    def register(self, context: Any) -> None:
        register_tool = getattr(context, "register_tool", None)
        if not callable(register_tool):
            return
        method_map = {
            "browser_workspace_doctor": "doctor",
            "browser_workspace_capture": "capture",
            "browser_workspace_click_xy": "click_xy",
            "browser_workspace_cdp": "cdp",
            "browser_workspace_search_domain_skills": "search_domain_skills",
            "browser_workspace_save_domain_skill": "save_domain_skill",
            "browser_workspace_read_helpers": "read_helpers",
            "browser_workspace_propose_helper_update": "propose_helper_update",
        }
        for tool_name, method_name in method_map.items():
            spec = TOOL_SPECS[tool_name]
            register_tool(
                name=tool_name,
                toolset=TOOLSET,
                schema={"name": tool_name, **spec},
                handler=self._handler_for(method_name),
                description=spec["description"],
                emoji="🌐",
            )

    def tool_names(self) -> list[str]:
        return list(TOOL_SPECS)


def get_plugin() -> BrowserWorkspacePlugin:
    return BrowserWorkspacePlugin()


def register(ctx: Any) -> None:
    """Directory-plugin entry point used by Hermes' plugin loader."""
    get_plugin().register(ctx)
