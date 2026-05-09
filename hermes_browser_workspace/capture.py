from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .provenance import build_provenance, utc_now_iso
from .safety import scrub_sensitive
from .workspace import SessionContext, record_artifact


def write_capture_metadata(
    session: SessionContext,
    capture_name: str,
    metadata: dict[str, Any],
    include_provenance: bool = True,
) -> Path:
    payload = scrub_sensitive(dict(metadata))
    if include_provenance:
        payload["provenance"] = build_provenance(session_id=session.session_id)
    payload["captured_at"] = utc_now_iso()
    path = session.screenshots_dir / f"{capture_name}.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    record_artifact(session, {"kind": "capture_metadata", "path": str(path), "name": capture_name})
    return path


def coordinate_fallback(x: int, y: int, screenshot_path: str | None = None) -> dict[str, Any]:
    return {
        "action": "click_xy",
        "x": x,
        "y": y,
        "screenshot_path": screenshot_path,
        "warning": "Coordinate fallbacks are less reliable than DOM-based actions and should be audited.",
    }
