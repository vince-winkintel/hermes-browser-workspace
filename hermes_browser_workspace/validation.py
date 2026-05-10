from __future__ import annotations

import ast
from typing import Any

from .safety import scrub_sensitive


DISALLOWED_IMPORT_ROOTS = {
    "subprocess",
    "socket",
    "requests",
    "httpx",
    "urllib",
    "os",
    "pathlib",
    "shutil",
}
DISALLOWED_CALL_ROOTS = {
    "eval",
    "exec",
    "compile",
    "__import__",
    "open",
    "input",
    "breakpoint",
}
DISALLOWED_CALL_PREFIXES = {
    "os.system",
    "os.popen",
    "subprocess.",
    "socket.",
    "requests.",
    "httpx.",
    "urllib.",
    "pathlib.Path.write_text",
    "pathlib.Path.write_bytes",
    "shutil.",
}
SENSITIVE_SELECTOR_KEYS = {
    "authorization",
    "cookie",
    "headers",
    "localstorage",
    "password",
    "token",
}


def validate_selectors(selectors: dict[str, Any] | None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    sanitized = scrub_sensitive(selectors or {})
    if selectors is None:
        return {"ok": True, "errors": errors, "warnings": warnings, "sanitized": sanitized}
    if not isinstance(selectors, dict):
        return {"ok": False, "errors": ["Selectors must be an object mapping names to selector definitions."], "warnings": warnings, "sanitized": {}}
    for name, value in selectors.items():
        if not isinstance(name, str) or not name.strip():
            errors.append("Selector names must be non-empty strings.")
            continue
        lowered = name.lower()
        if any(key in lowered for key in SENSITIVE_SELECTOR_KEYS):
            errors.append(f"Selector '{name}' uses a sensitive-looking field name.")
        if isinstance(value, str):
            if not value.strip():
                errors.append(f"Selector '{name}' cannot be empty.")
            continue
        if isinstance(value, dict):
            if "selector" in value and not isinstance(value["selector"], str):
                errors.append(f"Selector '{name}.selector' must be a string.")
            if "selectors" in value:
                nested = value["selectors"]
                if not isinstance(nested, list) or not all(isinstance(item, str) and item.strip() for item in nested):
                    errors.append(f"Selector '{name}.selectors' must be a list of non-empty strings.")
            for key in value:
                if any(sensitive in key.lower() for sensitive in SENSITIVE_SELECTOR_KEYS):
                    errors.append(f"Selector '{name}' contains sensitive-looking field '{key}'.")
            continue
        errors.append(f"Selector '{name}' must be a string or object.")
    return {"ok": not errors, "errors": errors, "warnings": warnings, "sanitized": sanitized}


def validate_helper_code(code: str) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        tree = ast.parse(code, filename="proposed_helper.py")
    except SyntaxError as exc:
        return {"ok": False, "errors": [f"Syntax error: {exc.msg} (line {exc.lineno})"], "warnings": warnings}

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            else:
                names = [node.module or ""]
            for name in names:
                root = name.split(".", 1)[0]
                if root in DISALLOWED_IMPORT_ROOTS:
                    errors.append(f"Disallowed import in helper proposal: {name}")
        if isinstance(node, ast.Call):
            call_name = _call_name(node.func)
            if not call_name:
                continue
            if call_name in DISALLOWED_CALL_ROOTS or any(call_name.startswith(prefix) for prefix in DISALLOWED_CALL_PREFIXES):
                errors.append(f"Disallowed call in helper proposal: {call_name}")
    return {"ok": not errors, "errors": errors, "warnings": warnings}


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None
