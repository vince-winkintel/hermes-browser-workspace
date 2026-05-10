from __future__ import annotations

from pathlib import Path
import difflib
import json
import re
from typing import Any

from .artifacts import list_artifacts, persist_review_artifact
from .config import BrowserWorkspaceConfig
from .provenance import build_provenance, utc_now_iso
from .safety import SafetyError, scrub_sensitive, validate_helper_mutation_mode
from .workspace import safe_join
from .validation import validate_helper_code


PROPOSAL_ID_RE = re.compile(r"^hp-[0-9a-z.+-]+$")


def read_helpers(workspace_root: Path) -> str:
    helpers_path = safe_join(workspace_root, "agent_helpers.py")
    return helpers_path.read_text(encoding="utf-8")


def helper_proposals_dir(workspace_root: Path) -> Path:
    return safe_join(workspace_root, "sessions/helper-proposals")


def helper_proposal_path(workspace_root: Path, proposal_id: str) -> Path:
    if not PROPOSAL_ID_RE.fullmatch(proposal_id):
        raise SafetyError(f"Invalid helper proposal id: {proposal_id}")
    return helper_proposals_dir(workspace_root) / f"{proposal_id}.json"


def _new_proposal_id() -> str:
    return "hp-" + re.sub(r"[^0-9a-z]+", "-", utc_now_iso().lower()).strip("-")


def propose_helper_update(
    workspace_root: Path,
    config: BrowserWorkspaceConfig,
    proposed_content: str,
    session_id: str | None = None,
    task_id: str | None = None,
) -> dict[str, str]:
    mode = validate_helper_mutation_mode(config.helper_mutation_mode)
    if mode == "read_only":
        raise SafetyError("Helper mutation is disabled in read_only mode")
    current = read_helpers(workspace_root).splitlines(keepends=True)
    proposed = proposed_content.splitlines(keepends=True)
    diff = "".join(
        difflib.unified_diff(current, proposed, fromfile="agent_helpers.py", tofile="agent_helpers.proposed.py")
    )
    proposals_dir = helper_proposals_dir(workspace_root)
    proposal_id = _new_proposal_id()
    validation = validate_helper_code(proposed_content)
    proposal_path = helper_proposal_path(workspace_root, proposal_id)
    payload = {
        "kind": "helper_proposal",
        "proposal_id": proposal_id,
        "created_at": utc_now_iso(),
        "session_id": session_id,
        "task_id": task_id,
        "domain": None,
        "source": {
            "session_id": session_id,
            "task_id": task_id,
            "domain": None,
        },
        "provenance": build_provenance(session_id=session_id, task_id=task_id),
        "mode": mode,
        "status": "pending_review",
        "reviewer": None,
        "reviewed_at": None,
        "decision_notes": None,
        "diff": scrub_sensitive(diff),
        "proposed_content": scrub_sensitive({"content": proposed_content})["content"],
        "validation": validation,
    }
    persist_review_artifact(proposal_path, payload)
    return {"proposal_id": proposal_id, "proposal_path": str(proposal_path), "diff": scrub_sensitive(diff), "validation_ok": str(validation["ok"]).lower()}


def list_helper_proposals(workspace_root: Path, status: str | None = None) -> list[dict[str, Any]]:
    return list_artifacts(workspace_root, kind="helper_proposal", status=status)


def read_helper_proposal(workspace_root: Path, proposal_id: str) -> dict[str, Any]:
    path = helper_proposal_path(workspace_root, proposal_id)
    if not path.exists():
        raise SafetyError(f"Unknown helper proposal: {proposal_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_helper_proposal(workspace_root: Path, proposal_id: str) -> dict[str, Any]:
    payload = read_helper_proposal(workspace_root, proposal_id)
    validation = validate_helper_code(payload.get("proposed_content", ""))
    payload["validation"] = validation
    report_path = helper_proposals_dir(workspace_root) / f"{proposal_id}.validation.json"
    persist_review_artifact(
        report_path,
        {
            "kind": "helper_validation_report",
            "proposal_id": proposal_id,
            "created_at": utc_now_iso(),
            "status": "completed",
            "validation": validation,
            "provenance": payload.get("provenance"),
            "session_id": payload.get("session_id"),
            "domain": payload.get("domain"),
        },
    )
    persist_review_artifact(helper_proposal_path(workspace_root, proposal_id), payload)
    return {"proposal_id": proposal_id, "validation": validation, "report_path": str(report_path)}


def review_helper_proposal(
    workspace_root: Path,
    proposal_id: str,
    decision: str,
    reviewer: str,
    decision_notes: Any | None = None,
) -> dict[str, Any]:
    if decision not in {"approved", "rejected", "superseded"}:
        raise SafetyError(f"Unsupported review decision: {decision}")
    payload = read_helper_proposal(workspace_root, proposal_id)
    payload["status"] = decision
    payload["reviewer"] = reviewer
    payload["reviewed_at"] = utc_now_iso()
    payload["decision_notes"] = decision_notes
    persist_review_artifact(helper_proposal_path(workspace_root, proposal_id), payload)
    return {
        "proposal_id": proposal_id,
        "status": decision,
        "reviewer": reviewer,
        "reviewed_at": payload["reviewed_at"],
    }
