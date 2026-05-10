from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import os
from typing import Any


DEFAULT_WORKSPACE_ROOT = Path.home() / ".hermes" / "browser-workspace"


def default_workspace_root() -> Path:
    return Path(os.path.expanduser(os.getenv("HERMES_BROWSER_WORKSPACE_ROOT", str(DEFAULT_WORKSPACE_ROOT)))).resolve()


class ConfigError(ValueError):
    pass


def _parse_scalar(raw: str) -> Any:
    text = raw.strip()
    lowered = text.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none"}:
        return None
    if text.startswith("[") or text.startswith("{"):
        return json.loads(text)
    if text.startswith('"') and text.endswith('"'):
        return json.loads(text)
    if text.startswith("'") and text.endswith("'"):
        return text[1:-1]
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        pass
    return text


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if ":" not in raw_line:
            raise ConfigError(f"Unsupported config syntax on line {lineno}")
        key, value = raw_line.strip().split(":", 1)
        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise ConfigError(f"Invalid indentation on line {lineno}")
        current = stack[-1][1]
        if not value.strip():
            child: dict[str, Any] = {}
            current[key] = child
            stack.append((indent, child))
        else:
            current[key] = _parse_scalar(value)
    return root


@dataclass
class BrowserWorkspaceConfig:
    workspace_root: Path = field(default_factory=default_workspace_root)
    helper_mutation_mode: str = "propose_only"
    browser_workspace_cdp_enabled: bool = True
    real_chrome_profile_enabled: bool = False
    real_chrome_profile_path: str | None = None
    storage_mode: str = "local_only"
    domain_skill_save_mode: str = "explicit"
    retention_days: int = 14
    stale_skill_warning_days: int = 30
    redact_patterns: list[str] = field(
        default_factory=lambda: ["token", "cookie", "authorization", "password", "secret", "localStorage"]
    )
    cdp_allowed_domains: list[str] = field(
        default_factory=lambda: [
            "Runtime.evaluate",
            "Page.captureScreenshot",
            "Page.getLayoutMetrics",
            "DOM.getDocument",
            "DOM.getBoxModel",
            "Emulation.setDeviceMetricsOverride",
            "Input.dispatchMouseEvent",
        ]
    )
    cdp_blocked_domains: list[str] = field(
        default_factory=lambda: [
            "Storage.",
            "Network.getCookies",
            "Network.setCookie",
            "Network.setCookies",
            "Fetch.",
        ]
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "workspace_root": str(self.workspace_root),
            "helper_mutation_mode": self.helper_mutation_mode,
            "browser_workspace_cdp_enabled": self.browser_workspace_cdp_enabled,
            "real_chrome_profile_enabled": self.real_chrome_profile_enabled,
            "real_chrome_profile_path": self.real_chrome_profile_path,
            "storage_mode": self.storage_mode,
            "domain_skill_save_mode": self.domain_skill_save_mode,
            "retention_days": self.retention_days,
            "stale_skill_warning_days": self.stale_skill_warning_days,
            "redact_patterns": self.redact_patterns,
            "cdp_allowed_domains": self.cdp_allowed_domains,
            "cdp_blocked_domains": self.cdp_blocked_domains,
        }

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "BrowserWorkspaceConfig":
        merged = cls().to_dict()
        merged.update(data)
        merged["workspace_root"] = Path(os.path.expanduser(str(merged["workspace_root"]))).resolve()
        return cls(**merged)


def default_config_text(root: Path | None = None) -> str:
    workspace_root = str((root or default_workspace_root()).resolve())
    template = BrowserWorkspaceConfig(workspace_root=Path(workspace_root)).to_dict()
    lines = [
        "# Hermes Browser Workspace Phase 2 config",
        f'workspace_root: "{template["workspace_root"]}"',
        f'helper_mutation_mode: "{template["helper_mutation_mode"]}"',
        f'browser_workspace_cdp_enabled: {str(template["browser_workspace_cdp_enabled"]).lower()}',
        f'real_chrome_profile_enabled: {str(template["real_chrome_profile_enabled"]).lower()}',
        "real_chrome_profile_path: null",
        f'storage_mode: "{template["storage_mode"]}"',
        f'domain_skill_save_mode: "{template["domain_skill_save_mode"]}"',
        f'retention_days: {template["retention_days"]}',
        f'stale_skill_warning_days: {template["stale_skill_warning_days"]}',
        f'redact_patterns: {json.dumps(template["redact_patterns"])}',
        f'cdp_allowed_domains: {json.dumps(template["cdp_allowed_domains"])}',
        f'cdp_blocked_domains: {json.dumps(template["cdp_blocked_domains"])}',
    ]
    return "\n".join(lines) + "\n"


def load_config(path: Path) -> BrowserWorkspaceConfig:
    text = path.read_text(encoding="utf-8")
    if text.lstrip().startswith("{"):
        data = json.loads(text)
    else:
        data = _parse_simple_yaml(text)
    return BrowserWorkspaceConfig.from_mapping(data)
