from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import re
import shutil
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

from .artifacts import persist_review_artifact
from .config import BrowserWorkspaceConfig
from .provenance import build_provenance, utc_now_iso
from .safety import SafetyError, scrub_sensitive, validate_domain_skill_status, validate_trust_state
from .workspace import safe_join
from .validation import (
    validate_examples,
    validate_extraction_recipes,
    validate_helper_code,
    validate_selectors,
)


DOMAIN_RE = re.compile(r"^[a-z0-9.-]+$")
DRAFT_ID_RE = re.compile(r"^ds-[0-9a-z.+-]+$")
PACKAGE_NAME_RE = re.compile(r"^[a-z0-9._-]+$")
PACKAGE_IMPORT_MODELS = {"draft", "pending_review"}
DOMAIN_SKILL_SCHEMA_VERSION = "1.1"


def normalize_domain(domain: str) -> str:
    normalized = domain.strip().lower()
    if normalized.startswith("www."):
        normalized = normalized[4:]
    if not DOMAIN_RE.fullmatch(normalized):
        raise SafetyError(f"Invalid domain: {domain}")
    return normalized


def domain_skill_dir(workspace_root: Path, domain: str) -> Path:
    return safe_join(workspace_root, f"domain-skills/{normalize_domain(domain)}")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _metadata_path(skill_dir: Path) -> Path:
    return skill_dir / "metadata.json"


def _selectors_path(skill_dir: Path) -> Path:
    return skill_dir / "selectors.json"


def _recipes_path(skill_dir: Path) -> Path:
    return skill_dir / "recipes.json"


def _examples_dir(skill_dir: Path) -> Path:
    return skill_dir / "examples"


def _examples_index_path(skill_dir: Path) -> Path:
    return _examples_dir(skill_dir) / "index.json"


def _phase3_metadata(metadata: dict[str, Any], *, selectors: dict[str, Any] | None, examples_count: int, recipes_count: int) -> dict[str, Any]:
    existing_verification = metadata.get("verification")
    if not isinstance(existing_verification, dict):
        existing_verification = {}
    return {
        "schema_version": metadata.get("schema_version", DOMAIN_SKILL_SCHEMA_VERSION),
        "verification_status": metadata.get("verification_status", "unverified"),
        "confidence": metadata.get("confidence"),
        "reliability": metadata.get("reliability"),
        "supported_task_types": metadata.get("supported_task_types", []),
        "selector_count": metadata.get("selector_count", _count_selector_entries(selectors)),
        "example_count": metadata.get("example_count", examples_count),
        "recipe_count": metadata.get("recipe_count", recipes_count),
        "source_package": metadata.get("source_package"),
        "source_import": metadata.get("source_import"),
        "verification": {
            "last_verified_at": metadata.get("last_verified_at"),
            "verification_notes": existing_verification.get("verification_notes"),
            "verified_by": existing_verification.get("verified_by"),
        },
    }


def _normalize_metadata(
    domain: str,
    metadata: dict[str, Any],
    *,
    selectors: dict[str, Any] | None = None,
    example_count: int = 0,
    recipe_count: int = 0,
    imported_from: dict[str, Any] | None = None,
) -> dict[str, Any]:
    status = validate_domain_skill_status(metadata.get("status", "draft"))
    trust_state = validate_trust_state(metadata.get("trust_state", "model_proposed"))
    final_metadata = scrub_sensitive(
        {
            "domain": domain,
            "title": metadata.get("title", domain),
            "tags": metadata.get("tags", []),
            "created_at": metadata.get("created_at", utc_now_iso()),
            "last_verified_at": metadata.get("last_verified_at"),
            "provenance": metadata.get("provenance", build_provenance(domain=domain, host=domain)),
            "author_type": metadata.get("author_type", "model_proposed"),
            "trust_state": trust_state,
            "status": status,
            "approval_state": metadata.get("approval_state", "pending_review"),
            **_phase3_metadata(metadata, selectors=selectors, examples_count=example_count, recipes_count=recipe_count),
        }
    )
    if imported_from is not None:
        final_metadata["imported_from"] = scrub_sensitive(imported_from)
        final_metadata["approval_state"] = "pending_review"
        final_metadata["status"] = "draft"
        if final_metadata["trust_state"] in {"trusted_local", "human_reviewed"}:
            final_metadata["trust_state"] = "model_proposed"
    elif metadata.get("imported_from") is not None:
        final_metadata["imported_from"] = scrub_sensitive(metadata.get("imported_from"))
    verification = final_metadata.setdefault("verification", {})
    verification["last_verified_at"] = final_metadata.get("last_verified_at")
    return final_metadata


def _count_selector_entries(selectors: dict[str, Any] | None) -> int:
    return len(selectors) if isinstance(selectors, dict) else 0


def _list_saved_examples(skill_dir: Path) -> list[dict[str, Any]]:
    index_path = _examples_index_path(skill_dir)
    if not index_path.exists():
        return []
    payload = _read_json(index_path)
    examples = payload.get("examples", [])
    return examples if isinstance(examples, list) else []


def _sync_skill_metadata_counts(skill_dir: Path) -> dict[str, Any]:
    metadata = _read_json(_metadata_path(skill_dir))
    selectors = _read_json(_selectors_path(skill_dir)) if _selectors_path(skill_dir).exists() else None
    recipes_payload = _read_json(_recipes_path(skill_dir)) if _recipes_path(skill_dir).exists() else {"recipes": []}
    recipes = recipes_payload.get("recipes", []) if isinstance(recipes_payload, dict) else []
    examples = _list_saved_examples(skill_dir)
    metadata["selector_count"] = _count_selector_entries(selectors)
    metadata["example_count"] = len(examples)
    metadata["recipe_count"] = len(recipes)
    metadata.setdefault("schema_version", DOMAIN_SKILL_SCHEMA_VERSION)
    metadata.setdefault("verification_status", "unverified")
    metadata.setdefault("supported_task_types", [])
    metadata.setdefault("verification", {})
    metadata["verification"]["last_verified_at"] = metadata.get("last_verified_at")
    persist_review_artifact(_metadata_path(skill_dir), metadata)
    return metadata


def load_domain_skill_metadata(workspace_root: Path, domain: str) -> dict[str, Any]:
    skill_dir = domain_skill_dir(workspace_root, domain)
    metadata_path = _metadata_path(skill_dir)
    if not metadata_path.exists():
        raise SafetyError(f"Missing domain skill metadata: {domain}")
    metadata = _read_json(metadata_path)
    return _sync_skill_metadata_counts(skill_dir) if isinstance(metadata, dict) else metadata


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
        metadata = _sync_skill_metadata_counts(entry)
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
                "verification_status": metadata.get("verification_status", "unverified"),
                "example_count": metadata.get("example_count", 0),
                "recipe_count": metadata.get("recipe_count", 0),
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
    examples: list[dict[str, Any]] | None = None,
    extraction_recipes: list[dict[str, Any]] | None = None,
) -> dict[str, str]:
    normalized_domain = normalize_domain(domain)
    selectors_report = validate_selectors(selectors)
    examples_report = validate_examples(examples)
    recipes_report = validate_extraction_recipes(extraction_recipes)
    skill_dir = domain_skill_dir(workspace_root, normalized_domain)
    skill_dir.mkdir(parents=True, exist_ok=True)
    final_metadata = _normalize_metadata(
        normalized_domain,
        metadata,
        selectors=selectors_report["sanitized"],
        example_count=examples_report["count"],
        recipe_count=recipes_report["count"],
    )
    (skill_dir / "SKILL.md").write_text(skill_markdown.rstrip() + "\n", encoding="utf-8")
    persist_review_artifact(_metadata_path(skill_dir), final_metadata)
    if selectors is not None:
        persist_review_artifact(_selectors_path(skill_dir), selectors_report["sanitized"])
    if helpers_code is not None:
        (skill_dir / "helpers.py").write_text(helpers_code.rstrip() + "\n", encoding="utf-8")
    _examples_dir(skill_dir).mkdir(exist_ok=True)
    if examples is not None:
        persist_review_artifact(_examples_index_path(skill_dir), {"kind": "domain_skill_examples", "domain": normalized_domain, "examples": examples_report["sanitized"]})
    if extraction_recipes is not None:
        persist_review_artifact(_recipes_path(skill_dir), {"kind": "domain_skill_recipes", "domain": normalized_domain, "recipes": recipes_report["sanitized"]})
    _sync_skill_metadata_counts(skill_dir)
    return {"domain": normalized_domain, "path": str(skill_dir)}


def validate_domain_skill(workspace_root: Path, domain: str) -> dict[str, Any]:
    skill_dir = domain_skill_dir(workspace_root, domain)
    metadata_path = _metadata_path(skill_dir)
    skill_path = skill_dir / "SKILL.md"
    if not metadata_path.exists() or not skill_path.exists():
        raise SafetyError(f"Incomplete domain skill: {domain}")
    metadata = _sync_skill_metadata_counts(skill_dir)
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
    extraction_recipes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    normalized_domain = normalize_domain(domain)
    selectors_report = validate_selectors(selectors)
    examples_report = validate_examples(examples)
    recipes_report = validate_extraction_recipes(extraction_recipes)
    helper_report = validate_helper_code(helpers_code or "") if helpers_code is not None else {"ok": True, "errors": [], "warnings": []}
    draft_id = f"ds-{utc_now_iso().replace(':', '-').lower()}"
    draft_dir = domain_skill_drafts_dir(workspace_root) / draft_id
    draft_dir.mkdir(parents=True, exist_ok=True)
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
    skill_lines.extend(["", "## Safety", "- Review selectors, recipes, and examples before activation.", "- Do not add secrets or account-specific details."])
    metadata = _normalize_metadata(
        normalized_domain,
        {
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
                "examples": examples_report,
                "recipes": recipes_report,
                "helpers": helper_report,
            },
        },
        selectors=selectors_report["sanitized"],
        example_count=examples_report["count"],
        recipe_count=recipes_report["count"],
    )
    metadata["kind"] = "domain_skill_draft"
    metadata["draft_id"] = draft_id
    metadata["validation"] = {
        "selectors": selectors_report,
        "examples": examples_report,
        "recipes": recipes_report,
        "helpers": helper_report,
    }
    persist_review_artifact(draft_dir / "metadata.json", metadata)
    (draft_dir / "SKILL.md").write_text("\n".join(skill_lines).rstrip() + "\n", encoding="utf-8")
    if selectors is not None:
        persist_review_artifact(draft_dir / "selectors.json", selectors_report["sanitized"])
    if examples is not None:
        persist_review_artifact(draft_dir / "examples.json", {"kind": "domain_skill_draft_examples", "examples": examples_report["sanitized"]})
    if extraction_recipes is not None:
        persist_review_artifact(draft_dir / "recipes.json", {"kind": "domain_skill_draft_recipes", "recipes": recipes_report["sanitized"]})
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
    metadata = _read_json(metadata_path)
    selectors = _read_json(draft_dir / "selectors.json") if (draft_dir / "selectors.json").exists() else None
    examples_payload = _read_json(draft_dir / "examples.json") if (draft_dir / "examples.json").exists() else {"examples": []}
    recipes_payload = _read_json(draft_dir / "recipes.json") if (draft_dir / "recipes.json").exists() else {"recipes": []}
    helper_report = {"ok": True, "errors": [], "warnings": []}
    helper_path = draft_dir / "helpers.py"
    if helper_path.exists():
        helper_report = validate_helper_code(helper_path.read_text(encoding="utf-8"))
    validation = {
        "selectors": validate_selectors(selectors),
        "examples": validate_examples(examples_payload.get("examples")),
        "recipes": validate_extraction_recipes(recipes_payload.get("recipes")),
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


def mark_domain_skill_verified(
    workspace_root: Path,
    domain: str,
    *,
    verified_by: str,
    verification_notes: str | None = None,
    verification_status: str = "verified",
    confidence: str | None = None,
    reliability: str | None = None,
) -> dict[str, Any]:
    skill_dir = domain_skill_dir(workspace_root, domain)
    metadata = validate_domain_skill(workspace_root, domain)
    verified_at = utc_now_iso()
    metadata["last_verified_at"] = verified_at
    metadata["verification_status"] = verification_status
    if confidence is not None:
        metadata["confidence"] = confidence
    if reliability is not None:
        metadata["reliability"] = reliability
    verification = metadata.setdefault("verification", {})
    verification["last_verified_at"] = verified_at
    verification["verified_by"] = verified_by
    verification["verification_notes"] = scrub_sensitive(verification_notes or "")
    persist_review_artifact(_metadata_path(skill_dir), metadata)
    return {
        "domain": metadata["domain"],
        "last_verified_at": verified_at,
        "verification_status": verification_status,
        "verified_by": verified_by,
    }


def _parse_iso_datetime(value: str | None) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _stale_report(metadata: dict[str, Any], threshold_days: int) -> dict[str, Any]:
    last_verified_at = metadata.get("last_verified_at")
    parsed = _parse_iso_datetime(last_verified_at)
    stale = True
    age_days: int | None = None
    if parsed is not None:
        age_days = int((datetime.now(timezone.utc) - parsed).total_seconds() // 86400)
        stale = age_days >= threshold_days
    return {
        "domain": metadata.get("domain"),
        "title": metadata.get("title"),
        "status": metadata.get("status"),
        "verification_status": metadata.get("verification_status", "unverified"),
        "last_verified_at": last_verified_at,
        "age_days": age_days,
        "stale": stale,
        "reason": "never_verified" if parsed is None else ("stale" if stale else "fresh"),
        "warning_threshold_days": threshold_days,
        "path": None,
    }


def list_stale_domain_skills(workspace_root: Path, config: BrowserWorkspaceConfig, threshold_days: int | None = None) -> dict[str, Any]:
    threshold = config.stale_skill_warning_days if threshold_days is None else threshold_days
    root = safe_join(workspace_root, "domain-skills")
    results: list[dict[str, Any]] = []
    if not root.exists():
        return {"warning_threshold_days": threshold, "results": results}
    for entry in sorted(root.iterdir()):
        metadata_path = entry / "metadata.json"
        if not entry.is_dir() or not metadata_path.exists():
            continue
        metadata = _sync_skill_metadata_counts(entry)
        report = _stale_report(metadata, threshold)
        report["path"] = str(entry)
        if report["stale"]:
            results.append(report)
    return {"warning_threshold_days": threshold, "results": results}


def add_domain_skill_example(workspace_root: Path, domain: str, example: dict[str, Any]) -> dict[str, Any]:
    skill_dir = domain_skill_dir(workspace_root, domain)
    validate_domain_skill(workspace_root, domain)
    report = validate_examples([example])
    if not report["ok"]:
        raise SafetyError("; ".join(report["errors"]))
    examples = _list_saved_examples(skill_dir)
    examples.append(report["sanitized"][0])
    persist_review_artifact(_examples_index_path(skill_dir), {"kind": "domain_skill_examples", "domain": normalize_domain(domain), "examples": examples})
    metadata = _sync_skill_metadata_counts(skill_dir)
    return {"domain": normalize_domain(domain), "example_count": metadata["example_count"]}


def list_domain_skill_examples(workspace_root: Path, domain: str) -> dict[str, Any]:
    skill_dir = domain_skill_dir(workspace_root, domain)
    validate_domain_skill(workspace_root, domain)
    examples = _list_saved_examples(skill_dir)
    return {"domain": normalize_domain(domain), "examples": examples, "count": len(examples)}


def save_domain_skill_recipes(workspace_root: Path, domain: str, recipes: list[dict[str, Any]]) -> dict[str, Any]:
    skill_dir = domain_skill_dir(workspace_root, domain)
    validate_domain_skill(workspace_root, domain)
    report = validate_extraction_recipes(recipes)
    if not report["ok"]:
        raise SafetyError("; ".join(report["errors"]))
    persist_review_artifact(_recipes_path(skill_dir), {"kind": "domain_skill_recipes", "domain": normalize_domain(domain), "recipes": report["sanitized"]})
    metadata = _sync_skill_metadata_counts(skill_dir)
    return {"domain": normalize_domain(domain), "recipe_count": metadata["recipe_count"]}


def list_domain_skill_recipes(workspace_root: Path, domain: str) -> dict[str, Any]:
    skill_dir = domain_skill_dir(workspace_root, domain)
    validate_domain_skill(workspace_root, domain)
    payload = _read_json(_recipes_path(skill_dir)) if _recipes_path(skill_dir).exists() else {"recipes": []}
    recipes = payload.get("recipes", []) if isinstance(payload, dict) else []
    return {"domain": normalize_domain(domain), "recipes": recipes, "count": len(recipes)}


def _iter_skill_files(skill_dir: Path) -> list[Path]:
    return sorted(path for path in skill_dir.rglob("*") if path.is_file())


def _file_sha256(path: Path) -> str:
    digest = sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def export_domain_skill_package(
    workspace_root: Path,
    domain: str,
    *,
    package_name: str | None = None,
    as_zip: bool = True,
) -> dict[str, Any]:
    skill_dir = domain_skill_dir(workspace_root, domain)
    metadata = validate_domain_skill(workspace_root, domain)
    export_root = safe_join(workspace_root, "domain-skill-packages")
    export_root.mkdir(parents=True, exist_ok=True)
    package_base = package_name or f"{metadata['domain']}-{utc_now_iso().split('T', 1)[0]}"
    if not PACKAGE_NAME_RE.fullmatch(package_base):
        raise SafetyError(f"Invalid package name: {package_base}")
    bundle_dir = safe_join(workspace_root, f"domain-skill-packages/{package_base}")
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir(parents=True, exist_ok=True)
    skill_bundle_dir = bundle_dir / metadata["domain"]
    shutil.copytree(skill_dir, skill_bundle_dir)
    files = []
    for path in _iter_skill_files(skill_bundle_dir):
        files.append({"path": str(path.relative_to(bundle_dir)), "sha256": _file_sha256(path)})
    manifest = {
        "kind": "domain_skill_package_manifest",
        "package_name": package_base,
        "domain": metadata["domain"],
        "created_at": utc_now_iso(),
        "format_version": 1,
        "source": {
            "workspace_root": str(workspace_root),
            "skill_path": str(skill_dir),
        },
        "files": files,
    }
    persist_review_artifact(bundle_dir / "manifest.json", manifest)
    if as_zip:
        zip_path = safe_join(workspace_root, f"domain-skill-packages/{package_base}.zip")
        with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as handle:
            for path in _iter_skill_files(bundle_dir):
                handle.write(path, arcname=str(path.relative_to(bundle_dir)))
        return {"domain": metadata["domain"], "package_path": str(zip_path), "manifest_path": str(bundle_dir / "manifest.json"), "format": "zip"}
    return {"domain": metadata["domain"], "package_path": str(bundle_dir), "manifest_path": str(bundle_dir / "manifest.json"), "format": "directory"}


def _extract_package_to_dir(workspace_root: Path, package_path: str) -> Path:
    source = Path(package_path).expanduser().resolve()
    if source.suffix.lower() == ".zip":
        bundle_name = source.stem
        if not PACKAGE_NAME_RE.fullmatch(bundle_name):
            raise SafetyError(f"Invalid package name: {bundle_name}")
        import_root = safe_join(workspace_root, f"sessions/imports/{bundle_name}")
        if import_root.exists():
            shutil.rmtree(import_root)
        import_root.mkdir(parents=True, exist_ok=True)
        with ZipFile(source, "r") as handle:
            for member in handle.namelist():
                ensure = Path(member)
                if ensure.is_absolute() or ".." in ensure.parts:
                    raise SafetyError(f"Unsafe package member path: {member}")
            handle.extractall(import_root)
        return import_root
    if source.is_dir():
        return source
    raise SafetyError(f"Unsupported package path: {package_path}")


def _verify_manifest_files(package_root: Path, manifest: dict[str, Any]) -> None:
    files = manifest.get("files")
    if not isinstance(files, list):
        raise SafetyError("Domain skill package manifest must include a files list")
    package_root_resolved = package_root.resolve()
    for index, item in enumerate(files):
        if not isinstance(item, dict):
            raise SafetyError(f"Package manifest file entry {index} must be an object")
        relative_path = item.get("path")
        expected_hash = item.get("sha256")
        if not isinstance(relative_path, str) or not relative_path:
            raise SafetyError(f"Package manifest file entry {index} is missing a path")
        candidate = Path(relative_path)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise SafetyError(f"Unsafe package manifest path: {relative_path}")
        path = (package_root / candidate).resolve()
        if package_root_resolved != path and package_root_resolved not in path.parents:
            raise SafetyError(f"Package manifest path escapes package root: {relative_path}")
        if not path.is_file():
            raise SafetyError(f"Package manifest references missing file: {relative_path}")
        if not isinstance(expected_hash, str) or _file_sha256(path) != expected_hash:
            raise SafetyError(f"Package checksum mismatch for: {relative_path}")


def import_domain_skill_package(workspace_root: Path, package_path: str, *, import_mode: str = "draft") -> dict[str, Any]:
    if import_mode not in PACKAGE_IMPORT_MODELS:
        raise SafetyError(f"Unsupported import mode: {import_mode}")
    extracted_root = _extract_package_to_dir(workspace_root, package_path)
    manifest_path = extracted_root / "manifest.json"
    if not manifest_path.exists():
        raise SafetyError("Domain skill package is missing manifest.json")
    manifest = _read_json(manifest_path)
    _verify_manifest_files(extracted_root, manifest)
    domain = normalize_domain(manifest.get("domain", ""))
    source_skill_dir = extracted_root / domain
    if not source_skill_dir.exists():
        raise SafetyError(f"Domain skill package missing skill directory for {domain}")
    metadata = _read_json(source_skill_dir / "metadata.json")
    selectors = _read_json(source_skill_dir / "selectors.json") if (source_skill_dir / "selectors.json").exists() else None
    examples_payload = _read_json(source_skill_dir / "examples" / "index.json") if (source_skill_dir / "examples" / "index.json").exists() else {"examples": []}
    recipes_payload = _read_json(source_skill_dir / "recipes.json") if (source_skill_dir / "recipes.json").exists() else {"recipes": []}
    validate_domain_skill_status(metadata.get("status", "draft"))
    validate_trust_state(metadata.get("trust_state", "model_proposed"))
    validate_selectors(selectors)
    examples_report = validate_examples(examples_payload.get("examples"))
    recipes_report = validate_extraction_recipes(recipes_payload.get("recipes"))
    imported_metadata = _normalize_metadata(
        domain,
        metadata,
        selectors=selectors,
        example_count=examples_report["count"],
        recipe_count=recipes_report["count"],
        imported_from={
            "package_path": str(Path(package_path).expanduser()),
            "manifest": manifest,
            "imported_at": utc_now_iso(),
            "import_mode": import_mode,
        },
    )
    imported_metadata["verification_status"] = "imported_unverified"
    imported_metadata["status"] = "draft"
    imported_metadata["approval_state"] = "pending_review"
    save_domain_skill(
        workspace_root,
        domain=domain,
        skill_markdown=(source_skill_dir / "SKILL.md").read_text(encoding="utf-8"),
        metadata=imported_metadata,
        selectors=selectors,
        helpers_code=(source_skill_dir / "helpers.py").read_text(encoding="utf-8") if (source_skill_dir / "helpers.py").exists() else None,
        examples=examples_report["sanitized"],
        extraction_recipes=recipes_report["sanitized"],
    )
    saved_metadata = load_domain_skill_metadata(workspace_root, domain)
    return {
        "domain": domain,
        "status": saved_metadata["status"],
        "approval_state": saved_metadata["approval_state"],
        "trust_state": saved_metadata["trust_state"],
        "verification_status": saved_metadata["verification_status"],
        "path": str(domain_skill_dir(workspace_root, domain)),
    }
