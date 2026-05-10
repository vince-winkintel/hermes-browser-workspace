from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .config import BrowserWorkspaceConfig
from .provenance import utc_now_iso
from .safety import scrub_sensitive
from .workspace import safe_join


PROTECTED_PATH_SUFFIXES = {
    "config.yaml",
    "agent_helpers.py",
}
PROTECTED_TOP_LEVEL_DIRS = {
    "domain-skills",
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_status(payload: dict[str, Any]) -> str | None:
    return payload.get("status") or payload.get("approval_state")


def _artifact_domain(payload: dict[str, Any]) -> str | None:
    if payload.get("domain"):
        return str(payload["domain"])
    provenance = payload.get("provenance")
    if isinstance(provenance, dict):
        return provenance.get("domain") or provenance.get("host")
    return None


def _artifact_session(payload: dict[str, Any]) -> str | None:
    if payload.get("session_id"):
        return str(payload["session_id"])
    provenance = payload.get("provenance")
    if isinstance(provenance, dict):
        return provenance.get("session_id")
    return None


def artifact_matches(
    payload: dict[str, Any],
    *,
    kind: str | None = None,
    status: str | None = None,
    session_id: str | None = None,
    domain: str | None = None,
) -> bool:
    if kind and payload.get("kind") != kind:
        return False
    if status and _artifact_status(payload) != status:
        return False
    if session_id and _artifact_session(payload) != session_id:
        return False
    if domain and _artifact_domain(payload) != domain:
        return False
    return True


def iter_json_artifacts(workspace_root: Path) -> list[tuple[Path, dict[str, Any]]]:
    artifacts: list[tuple[Path, dict[str, Any]]] = []
    for base_name in ("sessions", "domain-skills"):
        base = safe_join(workspace_root, base_name)
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.json")):
            payload = _read_json(path)
            if "kind" not in payload and path.name == "metadata.json":
                payload = {"kind": "domain_skill_metadata", **payload}
            artifacts.append((path, payload))
    return artifacts


def list_artifacts(
    workspace_root: Path,
    *,
    kind: str | None = None,
    status: str | None = None,
    session_id: str | None = None,
    domain: str | None = None,
) -> list[dict[str, Any]]:
    results = []
    for path, payload in iter_json_artifacts(workspace_root):
        if not artifact_matches(payload, kind=kind, status=status, session_id=session_id, domain=domain):
            continue
        results.append(
            {
                "kind": payload.get("kind", "unknown"),
                "path": str(path),
                "status": _artifact_status(payload),
                "session_id": _artifact_session(payload),
                "domain": _artifact_domain(payload),
                "created_at": payload.get("created_at") or payload.get("timestamp"),
            }
        )
    return results


def _is_protected_path(workspace_root: Path, path: Path) -> bool:
    relative = path.resolve().relative_to(workspace_root.resolve())
    if relative.name in PROTECTED_PATH_SUFFIXES:
        return True
    return bool(relative.parts and relative.parts[0] in PROTECTED_TOP_LEVEL_DIRS)


def cleanup_artifacts(
    workspace_root: Path,
    config: BrowserWorkspaceConfig,
    *,
    older_than_days: int | None = None,
    dry_run: bool = True,
    kind: str | None = None,
    status: str | None = None,
    session_id: str | None = None,
    domain: str | None = None,
) -> dict[str, Any]:
    cutoff_days = config.retention_days if older_than_days is None else older_than_days
    now = utc_now_iso()
    matches = []
    for path, payload in iter_json_artifacts(workspace_root):
        if not artifact_matches(payload, kind=kind, status=status, session_id=session_id, domain=domain):
            continue
        created_at = payload.get("created_at") or payload.get("timestamp")
        if not isinstance(created_at, str):
            continue
        age_seconds = _age_seconds(now, created_at)
        if age_seconds is None or age_seconds < cutoff_days * 86400:
            continue
        if _is_protected_path(workspace_root, path):
            continue
        matches.append({"path": str(path), "kind": payload.get("kind"), "created_at": created_at})
    deleted = []
    if not dry_run:
        for item in matches:
            path = Path(item["path"])
            if path.exists():
                path.unlink()
                deleted.append(item)
        _cleanup_empty_dirs(workspace_root)
    return {"dry_run": dry_run, "retention_days": cutoff_days, "matches": matches, "deleted": deleted}


def _age_seconds(now_iso: str, created_iso: str) -> float | None:
    from datetime import datetime

    try:
        now = datetime.fromisoformat(now_iso)
        created = datetime.fromisoformat(created_iso)
    except ValueError:
        return None
    return (now - created).total_seconds()


def _cleanup_empty_dirs(workspace_root: Path) -> None:
    for root_name in ("sessions", "screenshots", "traces"):
        root = safe_join(workspace_root, root_name)
        if not root.exists():
            continue
        for path in sorted(root.rglob("*"), reverse=True):
            if path.is_dir() and not any(path.iterdir()):
                path.rmdir()


def persist_review_artifact(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(scrub_sensitive(payload), indent=2) + "\n", encoding="utf-8")
    return path
