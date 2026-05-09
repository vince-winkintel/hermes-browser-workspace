from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import shutil
from typing import Any

from .config import BrowserWorkspaceConfig, default_config_text, load_config
from .provenance import utc_now_iso
from .safety import ensure_relative_path, ensure_within_root


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_HELPERS_PATH = PACKAGE_ROOT / "templates" / "agent_helpers.py"
DEFAULT_HELPERS_TEXT = '''"""Local helper file for Hermes Browser Workspace.

Phase 1 treats this file as durable but not auto-mutable.
Use it for reusable parsing, selector helpers, and site-specific utility code
that does not require secrets or account-specific data.
"""


def normalize_text(value: str) -> str:
    return " ".join(value.split())
'''


@dataclass
class SessionContext:
    session_id: str
    session_dir: Path
    outputs_dir: Path
    screenshots_dir: Path
    traces_dir: Path
    metadata_path: Path


def workspace_paths(root: Path) -> dict[str, Path]:
    return {
        "root": root,
        "config": root / "config.yaml",
        "helpers": root / "agent_helpers.py",
        "sessions": root / "sessions",
        "screenshots": root / "screenshots",
        "traces": root / "traces",
        "domain_skills": root / "domain-skills",
    }


def bootstrap_workspace(root: Path) -> dict[str, str]:
    paths = workspace_paths(root)
    for key, path in paths.items():
        if key in {"config", "helpers"}:
            continue
        path.mkdir(parents=True, exist_ok=True)
    paths["root"].mkdir(parents=True, exist_ok=True)
    if not paths["config"].exists():
        paths["config"].write_text(default_config_text(root), encoding="utf-8")
    if not paths["helpers"].exists():
        if TEMPLATE_HELPERS_PATH.exists():
            shutil.copyfile(TEMPLATE_HELPERS_PATH, paths["helpers"])
        else:
            paths["helpers"].write_text(DEFAULT_HELPERS_TEXT, encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def load_or_create_config(root: Path) -> BrowserWorkspaceConfig:
    bootstrap_workspace(root)
    return load_config(root / "config.yaml")


def safe_join(root: Path, relative_path: str) -> Path:
    rel = ensure_relative_path(relative_path)
    candidate = root / rel
    return ensure_within_root(root, candidate)


def create_session_context(root: Path, session_id: str) -> SessionContext:
    base = safe_join(root, f"sessions/{session_id}")
    outputs_dir = base / "outputs"
    screenshots_dir = safe_join(root, f"screenshots/{session_id}")
    traces_dir = safe_join(root, f"traces/{session_id}")
    for path in [base, outputs_dir, screenshots_dir, traces_dir]:
        path.mkdir(parents=True, exist_ok=True)
    metadata_path = base / "metadata.json"
    if not metadata_path.exists():
        metadata_path.write_text(
            json.dumps({"session_id": session_id, "created_at": utc_now_iso(), "artifacts": []}, indent=2) + "\n",
            encoding="utf-8",
        )
    return SessionContext(
        session_id=session_id,
        session_dir=base,
        outputs_dir=outputs_dir,
        screenshots_dir=screenshots_dir,
        traces_dir=traces_dir,
        metadata_path=metadata_path,
    )


def append_session_event(session: SessionContext, event: dict[str, Any]) -> None:
    events_path = session.session_dir / "events.jsonl"
    with events_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"timestamp": utc_now_iso(), **event}, sort_keys=True) + "\n")


def record_artifact(session: SessionContext, artifact: dict[str, Any]) -> None:
    payload = json.loads(session.metadata_path.read_text(encoding="utf-8"))
    payload.setdefault("artifacts", []).append(artifact)
    payload["updated_at"] = utc_now_iso()
    session.metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
