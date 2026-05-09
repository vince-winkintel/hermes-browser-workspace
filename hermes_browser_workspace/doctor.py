from __future__ import annotations

from typing import Any

from .config import BrowserWorkspaceConfig
from .workspace import bootstrap_workspace, workspace_paths


def run_doctor(config: BrowserWorkspaceConfig) -> dict[str, Any]:
    bootstrap_workspace(config.workspace_root)
    paths = workspace_paths(config.workspace_root)
    checks = {
        "workspace_root_exists": paths["root"].exists(),
        "config_exists": paths["config"].exists(),
        "helpers_exists": paths["helpers"].exists(),
        "sessions_dir_exists": paths["sessions"].exists(),
        "domain_skills_dir_exists": paths["domain_skills"].exists(),
        "cdp_enabled": config.browser_workspace_cdp_enabled,
        "real_chrome_profile_enabled": config.real_chrome_profile_enabled,
        "real_chrome_profile_path_present": bool(config.real_chrome_profile_path),
        "helper_mutation_mode": config.helper_mutation_mode,
    }
    warnings = []
    if config.real_chrome_profile_enabled and not config.real_chrome_profile_path:
        warnings.append("Real Chrome profile mode is enabled but no profile path is configured.")
    if config.helper_mutation_mode == "review_required":
        warnings.append("Helper review_required mode is enabled; Phase 1 should still avoid trusted auto-apply.")
    return {"checks": checks, "warnings": warnings, "workspace_root": str(config.workspace_root)}
