from __future__ import annotations

from pathlib import Path
import json
import re
from typing import Any

from .artifacts import list_artifacts, persist_review_artifact
from .provenance import build_provenance, utc_now_iso
from .safety import SafetyError, scrub_sensitive, validate_domain_skill_status, validate_trust_state
from .workspace import safe_join
from .validation import validate_helper_code, validate_selectors


DOMAIN_RE = re.compile(r"^[a-z0-9.-]+$")
DRAFT_ID_RE = re.compile(r"^ds-[0-9a-z.+-]+$")


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


def domain_skill_drafts_dir(workspace_root: Path) -> Path:
    return safe_join(workspace_root, "sessions/domain-skill-drafts")


def draft_domain_skill(
    workspace_root: Path,
    *,
    domain: str,
    observations: list[str] | None = None,
    selectors: dict[str, Any] | None = None,
    examples: list[dict[str, Any]] | None = None,
    title: str | None = None,
    task_id: str | None = None,
    session_id: str | None = None,
    helpers_code: str | None = None,
) -> dict[str, Any]:
    normalized_domain = normalize_domain(domain)
    selectors_report = validate_selectors(selectors)
    helper_report = validate_helper_code(helpers_code or "") if helpers_code is not None else {"ok": True, "errors": [], "warnings": []}
    draft_id = f"ds-{utc_now_iso().replace(':', '-').lower()}"
    draft_dir = domain_skill_drafts_dir(workspace_root) / draft_id
    draft_dir.mkdir(parents=True, exist_ok=True)
    sanitized_examples = scrub_sensitive(examples or [])
    sanitized_observations = [str(item).strip() for item in (observations or []) if str(item).strip()]
    skill_lines = [
        f"# {title or normalized_domain}",
        "",
        "## Draft Notes",
    ]
    if sanitized_observations:
        skill_lines.extend(f"- {line}" for line in sanitized_observations)
    else:
        skill_lines.append("- Draft generated from structured observations.")
    skill_lines.extend(["", "## Safety", "- Review selectors and examples before activation.", "- Do not add secrets or account-specific details."])
    metadata = {
        "kind": "domain_skill_draft",
        "draft_id": draft_id,
        "domain": normalized_domain,
        "title": title or normalized_domain,
        "created_at": utc_now_iso(),
        "status": "draft",
        "trust_state": "model_proposed",
        "author_type": "model_proposed",
        "approval_state": "pending_review",
        "provenance": build_provenance(session_id=session_id, task_id=task_id, domain=normalized_domain, host=normalized_domain),
        "validation": {
            "selectors": selectors_report,
            "helpers": helper_report,
        },
    }
    persist_review_artifact(draft_dir / "metadata.json", metadata)
    (draft_dir / "SKILL.md").write_text("\n".join(skill_lines).rstrip() + "\n", encoding="utf-8")
    if selectors_report["sanitized"]:
        persist_review_artifact(draft_dir / "selectors.json", selectors_report["sanitized"])
    if sanitized_examples:
        persist_review_artifact(draft_dir / "examples.json", {"kind": "domain_skill_draft_examples", "examples": sanitized_examples})
    if helpers_code is not None:
        (draft_dir / "helpers.py").write_text((helpers_code.rstrip() + "\n") if helpers_code.strip() else "", encoding="utf-8")
    return {
        "draft_id": draft_id,
        "domain": normalized_domain,
        "path": str(draft_dir),
        "validation": metadata["validation"],
    }


def validate_domain_skill_draft(workspace_root: Path, draft_id: str) -> dict[str, Any]:
    if not DRAFT_ID_RE.fullmatch(draft_id):
        raise SafetyError(f"Invalid domain skill draft id: {draft_id}")
    draft_dir = domain_skill_drafts_dir(workspace_root) / draft_id
    metadata_path = draft_dir / "metadata.json"
    skill_path = draft_dir / "SKILL.md"
    if not metadata_path.exists() or not skill_path.exists():
        raise SafetyError(f"Incomplete domain skill draft: {draft_id}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    selectors = None
    selectors_path = draft_dir / "selectors.json"
    if selectors_path.exists():
        selectors = json.loads(selectors_path.read_text(encoding="utf-8"))
    helper_report = {"ok": True, "errors": [], "warnings": []}
    helper_path = draft_dir / "helpers.py"
    if helper_path.exists():
        helper_report = validate_helper_code(helper_path.read_text(encoding="utf-8"))
    validation = {
        "selectors": validate_selectors(selectors),
        "helpers": helper_report,
    }
    report = {
        "kind": "domain_skill_validation_report",
        "draft_id": draft_id,
        "domain": metadata.get("domain"),
        "created_at": utc_now_iso(),
        "status": "completed",
        "validation": validation,
        "provenance": metadata.get("provenance"),
    }
    persist_review_artifact(draft_dir / "validation-report.json", report)
    metadata["validation"] = validation
    persist_review_artifact(metadata_path, metadata)
    return {"draft_id": draft_id, "validation": validation, "report_path": str(draft_dir / "validation-report.json")}
