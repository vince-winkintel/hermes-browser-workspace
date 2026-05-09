from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .capture import coordinate_fallback, write_capture_metadata
from .cdp import check_cdp_policy, log_cdp_call
from .config import BrowserWorkspaceConfig
from .doctor import run_doctor
from .domain_skills import save_domain_skill, search_domain_skills
from .helpers import propose_helper_update, read_helpers
from .workspace import append_session_event, create_session_context, load_or_create_config


ToolFn = Callable[..., dict[str, Any]]


@dataclass
class ToolRegistry:
    config: BrowserWorkspaceConfig

    def doctor(self) -> dict[str, Any]:
        return run_doctor(self.config)

    def capture(self, session_id: str, name: str, metadata: dict[str, Any]) -> dict[str, Any]:
        session = create_session_context(self.config.workspace_root, session_id)
        path = write_capture_metadata(session, name, metadata)
        append_session_event(session, {"tool": "browser_workspace_capture", "path": str(path)})
        return {"path": str(path)}

    def click_xy(self, session_id: str, x: int, y: int, screenshot_path: str | None = None) -> dict[str, Any]:
        session = create_session_context(self.config.workspace_root, session_id)
        payload = coordinate_fallback(x, y, screenshot_path)
        append_session_event(session, {"tool": "browser_workspace_click_xy", **payload})
        return payload

    def cdp(
        self,
        session_id: str,
        method: str,
        params: dict[str, Any] | None = None,
        result: dict[str, Any] | None = None,
        task_id: str | None = None,
    ) -> dict[str, Any]:
        check_cdp_policy(self.config, method)
        session = create_session_context(self.config.workspace_root, session_id)
        trace = log_cdp_call(session, method, params, result=result, task_id=task_id)
        append_session_event(session, {"tool": "browser_workspace_cdp", "method": method, "trace": str(trace)})
        return {"policy": "allowed", "trace_path": str(trace), "method": method}

    def search_domain_skills(self, domain: str | None = None, tags: list[str] | None = None) -> dict[str, Any]:
        return {"results": search_domain_skills(self.config.workspace_root, domain=domain, tags=tags)}

    def save_domain_skill(
        self,
        domain: str,
        skill_markdown: str,
        metadata: dict[str, Any],
        selectors: dict[str, Any] | None = None,
        helpers_code: str | None = None,
    ) -> dict[str, Any]:
        return save_domain_skill(
            self.config.workspace_root,
            domain=domain,
            skill_markdown=skill_markdown,
            metadata=metadata,
            selectors=selectors,
            helpers_code=helpers_code,
        )

    def read_helpers(self) -> dict[str, Any]:
        return {"content": read_helpers(self.config.workspace_root)}

    def propose_helper_update(self, proposed_content: str, session_id: str | None = None, task_id: str | None = None) -> dict[str, Any]:
        return propose_helper_update(
            self.config.workspace_root,
            self.config,
            proposed_content=proposed_content,
            session_id=session_id,
            task_id=task_id,
        )


def build_registry(config_path: Path | None = None) -> ToolRegistry:
    root = config_path.parent if config_path else BrowserWorkspaceConfig().workspace_root
    config = load_or_create_config(root)
    return ToolRegistry(config=config)
