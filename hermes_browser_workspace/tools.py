from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .capture import coordinate_fallback, write_capture_metadata
from .cdp import check_cdp_policy, log_cdp_call
from .artifacts import cleanup_artifacts, list_artifacts
from .config import BrowserWorkspaceConfig
from .doctor import run_doctor
from .domain_skills import (
    add_domain_skill_example,
    draft_domain_skill,
    export_domain_skill_package,
    import_domain_skill_package,
    list_domain_skill_examples,
    list_domain_skill_recipes,
    list_stale_domain_skills,
    mark_domain_skill_verified,
    save_domain_skill,
    save_domain_skill_recipes,
    search_domain_skills,
    validate_domain_skill_draft,
)
from .helpers import (
    list_helper_proposals,
    propose_helper_update,
    read_helper_proposal,
    read_helpers,
    review_helper_proposal,
    validate_helper_proposal,
)
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
        examples: list[dict[str, Any]] | None = None,
        extraction_recipes: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        return save_domain_skill(
            self.config.workspace_root,
            domain=domain,
            skill_markdown=skill_markdown,
            metadata=metadata,
            selectors=selectors,
            helpers_code=helpers_code,
            examples=examples,
            extraction_recipes=extraction_recipes,
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

    def list_helper_proposals(self, status: str | None = None) -> dict[str, Any]:
        return {"results": list_helper_proposals(self.config.workspace_root, status=status)}

    def review_helper_proposal(
        self,
        proposal_id: str,
        decision: str | None = None,
        reviewer: str | None = None,
        decision_notes: Any | None = None,
    ) -> dict[str, Any]:
        if decision is None:
            return read_helper_proposal(self.config.workspace_root, proposal_id)
        if reviewer is None:
            raise ValueError("reviewer is required when recording a decision")
        return review_helper_proposal(
            self.config.workspace_root,
            proposal_id=proposal_id,
            decision=decision,
            reviewer=reviewer,
            decision_notes=decision_notes,
        )

    def validate_helper_proposal(self, proposal_id: str) -> dict[str, Any]:
        return validate_helper_proposal(self.config.workspace_root, proposal_id)

    def draft_domain_skill(
        self,
        domain: str,
        observations: list[str] | None = None,
        selectors: dict[str, Any] | None = None,
        examples: list[dict[str, Any]] | None = None,
        title: str | None = None,
        task_id: str | None = None,
        session_id: str | None = None,
        helpers_code: str | None = None,
        extraction_recipes: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        return draft_domain_skill(
            self.config.workspace_root,
            domain=domain,
            observations=observations,
            selectors=selectors,
            examples=examples,
            title=title,
            task_id=task_id,
            session_id=session_id,
            helpers_code=helpers_code,
            extraction_recipes=extraction_recipes,
        )

    def validate_domain_skill(self, draft_id: str) -> dict[str, Any]:
        return validate_domain_skill_draft(self.config.workspace_root, draft_id)

    def mark_domain_skill_verified(
        self,
        domain: str,
        verified_by: str,
        verification_notes: str | None = None,
        verification_status: str = "verified",
        confidence: str | None = None,
        reliability: str | None = None,
    ) -> dict[str, Any]:
        return mark_domain_skill_verified(
            self.config.workspace_root,
            domain,
            verified_by=verified_by,
            verification_notes=verification_notes,
            verification_status=verification_status,
            confidence=confidence,
            reliability=reliability,
        )

    def list_stale_domain_skills(self, threshold_days: int | None = None) -> dict[str, Any]:
        return list_stale_domain_skills(self.config.workspace_root, self.config, threshold_days=threshold_days)

    def add_domain_skill_example(self, domain: str, example: dict[str, Any]) -> dict[str, Any]:
        return add_domain_skill_example(self.config.workspace_root, domain, example)

    def list_domain_skill_examples(self, domain: str) -> dict[str, Any]:
        return list_domain_skill_examples(self.config.workspace_root, domain)

    def save_domain_skill_recipes(self, domain: str, recipes: list[dict[str, Any]]) -> dict[str, Any]:
        return save_domain_skill_recipes(self.config.workspace_root, domain, recipes)

    def list_domain_skill_recipes(self, domain: str) -> dict[str, Any]:
        return list_domain_skill_recipes(self.config.workspace_root, domain)

    def export_domain_skill_package(
        self,
        domain: str,
        package_name: str | None = None,
        as_zip: bool = True,
    ) -> dict[str, Any]:
        return export_domain_skill_package(self.config.workspace_root, domain, package_name=package_name, as_zip=as_zip)

    def import_domain_skill_package(self, package_path: str, import_mode: str = "draft") -> dict[str, Any]:
        return import_domain_skill_package(self.config.workspace_root, package_path, import_mode=import_mode)

    def list_artifacts(
        self,
        kind: str | None = None,
        status: str | None = None,
        session_id: str | None = None,
        domain: str | None = None,
    ) -> dict[str, Any]:
        return {
            "results": list_artifacts(
                self.config.workspace_root,
                kind=kind,
                status=status,
                session_id=session_id,
                domain=domain,
            )
        }

    def cleanup_artifacts(
        self,
        older_than_days: int | None = None,
        dry_run: bool = True,
        kind: str | None = None,
        status: str | None = None,
        session_id: str | None = None,
        domain: str | None = None,
    ) -> dict[str, Any]:
        return cleanup_artifacts(
            self.config.workspace_root,
            self.config,
            older_than_days=older_than_days,
            dry_run=dry_run,
            kind=kind,
            status=status,
            session_id=session_id,
            domain=domain,
        )


def build_registry(config_path: Path | None = None) -> ToolRegistry:
    root = config_path.parent if config_path else BrowserWorkspaceConfig().workspace_root
    config = load_or_create_config(root)
    return ToolRegistry(config=config)
