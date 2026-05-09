from __future__ import annotations

from pathlib import Path
import json
import re
from typing import Any

from .provenance import build_provenance, utc_now_iso
from .safety import SafetyError, scrub_sensitive, validate_domain_skill_status, validate_trust_state
from .workspace import safe_join


DOMAIN_RE = re.compile(r"^[a-z0-9.-]+$")


def normalize_domain(domain: str) -> str:
    normalized = domain.strip().lower()
    if normalized.startswith("www."):
        normalized = normalized[4:]
    if not DOMAIN_RE.fullmatch(normalized):
        raise SafetyError(f"Invalid domain: {domain}")
    return normalized


def domain_skill_dir(workspace_root: Path, domain: str) -> Path:
    return safe_join(workspace_root, f"domain-skills/{normalize_domain(domain)}")


def search_domain_skills(workspace_root: Path, domain: str | None = None, tags: list[str] | None = None) -> list[dict[str, Any]]:
    root = safe_join(workspace_root, "domain-skills")
    if not root.exists():
        return []
    requested_tags = {tag.lower() for tag in (tags or [])}
    candidates = []
    for entry in sorted(root.iterdir()):
        metadata_path = entry / "metadata.json"
        skill_path = entry / "SKILL.md"
        if not entry.is_dir() or not metadata_path.exists() or not skill_path.exists():
            continue
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if domain and normalize_domain(metadata.get("domain", entry.name)) != normalize_domain(domain):
            continue
        if requested_tags and not requested_tags.intersection({tag.lower() for tag in metadata.get("tags", [])}):
            continue
        candidates.append(
            {
                "domain": metadata.get("domain", entry.name),
                "title": metadata.get("title", entry.name),
                "tags": metadata.get("tags", []),
                "status": metadata.get("status", "draft"),
                "path": str(entry),
            }
        )
    return candidates


def save_domain_skill(
    workspace_root: Path,
    domain: str,
    skill_markdown: str,
    metadata: dict[str, Any],
    selectors: dict[str, Any] | None = None,
    helpers_code: str | None = None,
) -> dict[str, str]:
    normalized_domain = normalize_domain(domain)
    status = validate_domain_skill_status(metadata.get("status", "draft"))
    trust_state = validate_trust_state(metadata.get("trust_state", "model_proposed"))
    skill_dir = domain_skill_dir(workspace_root, normalized_domain)
    skill_dir.mkdir(parents=True, exist_ok=True)
    final_metadata = scrub_sensitive({
        "domain": normalized_domain,
        "title": metadata.get("title", normalized_domain),
        "tags": metadata.get("tags", []),
        "created_at": metadata.get("created_at", utc_now_iso()),
        "last_verified_at": metadata.get("last_verified_at"),
        "provenance": metadata.get("provenance", build_provenance(domain=normalized_domain, host=normalized_domain)),
        "author_type": metadata.get("author_type", "model_proposed"),
        "trust_state": trust_state,
        "status": status,
        "approval_state": metadata.get("approval_state", "pending_review"),
    })
    (skill_dir / "SKILL.md").write_text(skill_markdown.rstrip() + "\n", encoding="utf-8")
    (skill_dir / "metadata.json").write_text(json.dumps(final_metadata, indent=2) + "\n", encoding="utf-8")
    if selectors is not None:
        (skill_dir / "selectors.json").write_text(json.dumps(scrub_sensitive(selectors), indent=2) + "\n", encoding="utf-8")
    if helpers_code is not None:
        (skill_dir / "helpers.py").write_text(helpers_code.rstrip() + "\n", encoding="utf-8")
    (skill_dir / "examples").mkdir(exist_ok=True)
    return {"domain": normalized_domain, "path": str(skill_dir)}


def validate_domain_skill(workspace_root: Path, domain: str) -> dict[str, Any]:
    skill_dir = domain_skill_dir(workspace_root, domain)
    metadata_path = skill_dir / "metadata.json"
    skill_path = skill_dir / "SKILL.md"
    if not metadata_path.exists() or not skill_path.exists():
        raise SafetyError(f"Incomplete domain skill: {domain}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if normalize_domain(metadata.get("domain", "")) != skill_dir.name:
        raise SafetyError("Domain metadata does not match directory name")
    validate_domain_skill_status(metadata.get("status", "draft"))
    validate_trust_state(metadata.get("trust_state", "model_proposed"))
    return metadata
