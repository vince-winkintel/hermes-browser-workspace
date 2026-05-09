from __future__ import annotations

from pathlib import Path
from typing import Any


ALLOWED_HELPER_MUTATION_MODES = {"read_only", "propose_only", "review_required"}
ALLOWED_DOMAIN_SKILL_STATUSES = {"draft", "active", "stale", "disabled"}
ALLOWED_TRUST_STATES = {"human_authored", "model_proposed", "human_reviewed", "trusted_local", "disabled"}
DEFAULT_REDACT_KEYS = {"token", "cookie", "authorization", "password", "secret", "localstorage", "local_storage", "api_key"}


class SafetyError(ValueError):
    pass


def ensure_relative_path(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        raise SafetyError(f"Absolute paths are not allowed: {path}")
    if ".." in candidate.parts:
        raise SafetyError(f"Parent path traversal is not allowed: {path}")
    return candidate


def ensure_within_root(root: Path, candidate: Path) -> Path:
    root_resolved = root.resolve()
    candidate_resolved = candidate.resolve()
    if candidate_resolved != root_resolved and root_resolved not in candidate_resolved.parents:
        raise SafetyError(f"Path escapes workspace root: {candidate_resolved}")
    return candidate_resolved


def validate_helper_mutation_mode(mode: str) -> str:
    if mode not in ALLOWED_HELPER_MUTATION_MODES:
        raise SafetyError(f"Unsupported helper mutation mode: {mode}")
    return mode


def validate_trust_state(state: str) -> str:
    if state not in ALLOWED_TRUST_STATES:
        raise SafetyError(f"Unsupported trust state: {state}")
    return state


def validate_domain_skill_status(status: str) -> str:
    if status not in ALLOWED_DOMAIN_SKILL_STATUSES:
        raise SafetyError(f"Unsupported domain skill status: {status}")
    return status


def method_allowed(method: str, allowed_prefixes: list[str], blocked_prefixes: list[str]) -> bool:
    if any(method.startswith(prefix) for prefix in blocked_prefixes):
        return False
    return any(method.startswith(prefix) for prefix in allowed_prefixes)


def _is_sensitive_key(key: str, patterns: set[str]) -> bool:
    lowered = key.lower()
    return any(pattern in lowered for pattern in patterns)


def scrub_sensitive(value: Any, patterns: list[str] | None = None) -> Any:
    """Recursively redact values for sensitive-looking keys before persistence."""
    pattern_set = {p.lower() for p in (patterns or DEFAULT_REDACT_KEYS)}
    if isinstance(value, dict):
        return {
            str(key): "[REDACTED]" if _is_sensitive_key(str(key), pattern_set) else scrub_sensitive(item, list(pattern_set))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [scrub_sensitive(item, list(pattern_set)) for item in value]
    return value
