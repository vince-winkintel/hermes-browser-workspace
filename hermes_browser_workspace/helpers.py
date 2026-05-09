from __future__ import annotations

from pathlib import Path
import difflib
import json

from .config import BrowserWorkspaceConfig
from .provenance import build_provenance, utc_now_iso
from .safety import SafetyError, scrub_sensitive, validate_helper_mutation_mode
from .workspace import safe_join


def read_helpers(workspace_root: Path) -> str:
    helpers_path = safe_join(workspace_root, "agent_helpers.py")
    return helpers_path.read_text(encoding="utf-8")


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
    proposals_dir = safe_join(workspace_root, "sessions")
    proposal_id = utc_now_iso().replace(":", "-")
    proposal_path = proposals_dir / f"helper-proposal-{proposal_id}.json"
    payload = {
        "kind": "helper_proposal",
        "created_at": utc_now_iso(),
        "provenance": build_provenance(session_id=session_id, task_id=task_id),
        "mode": mode,
        "diff": diff,
        "proposed_content": scrub_sensitive({"content": proposed_content})["content"],
    }
    proposal_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {"proposal_path": str(proposal_path), "diff": diff}
