from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .config import BrowserWorkspaceConfig
from .provenance import build_provenance, utc_now_iso
from .safety import SafetyError, method_allowed, scrub_sensitive
from .workspace import SessionContext, record_artifact


def check_cdp_policy(config: BrowserWorkspaceConfig, method: str) -> None:
    if not config.browser_workspace_cdp_enabled:
        raise SafetyError("browser_workspace_cdp is disabled by config")
    if not method_allowed(method, config.cdp_allowed_domains, config.cdp_blocked_domains):
        raise SafetyError(f"CDP method blocked by policy: {method}")


def log_cdp_call(
    session: SessionContext,
    method: str,
    params: dict[str, Any] | None,
    result: dict[str, Any] | None = None,
    task_id: str | None = None,
) -> Path:
    payload = {
        "kind": "cdp_call",
        "method": method,
        "params": scrub_sensitive(params or {}),
        "result": scrub_sensitive(result or {}),
        "timestamp": utc_now_iso(),
        "provenance": build_provenance(session_id=session.session_id, task_id=task_id),
    }
    filename = f"{utc_now_iso().replace(':', '-')}-{method.replace('.', '_')}.json"
    path = session.traces_dir / filename
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    record_artifact(session, {"kind": "cdp_trace", "path": str(path), "method": method})
    return path
