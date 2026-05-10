from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


@dataclass
class ProvenanceRecord:
    source: str = "browser_workspace"
    session_id: str | None = None
    task_id: str | None = None
    domain: str | None = None
    host: str | None = None
    author_type: str = "model_proposed"
    trust_state: str = "model_proposed"
    approval_state: str = "pending_review"
    generated_at: str = ""

    def __post_init__(self) -> None:
        if not self.generated_at:
            self.generated_at = utc_now_iso()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_provenance(**kwargs: Any) -> dict[str, Any]:
    return ProvenanceRecord(**kwargs).to_dict()
