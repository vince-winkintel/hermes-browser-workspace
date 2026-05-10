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
SENSITIVE_EXAMPLE_KEYS = {
    "authorization",
    "cookie",
    "cookies",
    "headers",
    "html",
    "localstorage",
    "password",
    "request",
    "response",
    "storage",
    "token",
}
ALLOWED_RECIPE_STEP_ACTIONS = {
    "click",
    "extract",
    "fill",
    "goto",
    "read_text",
    "wait_for",
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


def validate_examples(examples: list[dict[str, Any]] | None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    sanitized = scrub_sensitive(examples or [])
    if examples is None:
        return {"ok": True, "errors": errors, "warnings": warnings, "sanitized": sanitized, "count": 0}
    if not isinstance(examples, list):
        return {"ok": False, "errors": ["Examples must be a list of objects."], "warnings": warnings, "sanitized": [], "count": 0}
    for index, example in enumerate(examples):
        if not isinstance(example, dict):
            errors.append(f"Example {index} must be an object.")
            continue
        if not any(key in example for key in ("task", "input", "output", "notes")):
            warnings.append(f"Example {index} is missing common fields such as task, input, output, or notes.")
        for key in example:
            lowered = str(key).lower()
            if any(sensitive in lowered for sensitive in SENSITIVE_EXAMPLE_KEYS):
                errors.append(f"Example {index} contains sensitive-looking field '{key}'.")
    return {"ok": not errors, "errors": errors, "warnings": warnings, "sanitized": sanitized, "count": len(sanitized)}


def validate_extraction_recipes(recipes: list[dict[str, Any]] | None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    sanitized = scrub_sensitive(recipes or [])
    if recipes is None:
        return {"ok": True, "errors": errors, "warnings": warnings, "sanitized": sanitized, "count": 0}
    if not isinstance(recipes, list):
        return {"ok": False, "errors": ["Extraction recipes must be a list of recipe objects."], "warnings": warnings, "sanitized": [], "count": 0}
    for recipe_index, recipe in enumerate(recipes):
        if not isinstance(recipe, dict):
            errors.append(f"Recipe {recipe_index} must be an object.")
            continue
        name = recipe.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"Recipe {recipe_index} must include a non-empty name.")
        steps = recipe.get("steps")
        if not isinstance(steps, list) or not steps:
            errors.append(f"Recipe {recipe_index} must include a non-empty steps list.")
            continue
        for step_index, step in enumerate(steps):
            if not isinstance(step, dict):
                errors.append(f"Recipe {recipe_index} step {step_index} must be an object.")
                continue
            action = step.get("action")
            if action not in ALLOWED_RECIPE_STEP_ACTIONS:
                errors.append(f"Recipe {recipe_index} step {step_index} has unsupported action '{action}'.")
            field = step.get("field")
            if field is not None and (not isinstance(field, str) or not field.strip()):
                errors.append(f"Recipe {recipe_index} step {step_index} field must be a non-empty string.")
            selector = step.get("selector")
            selectors = step.get("selectors")
            if selector is None and selectors is None and action in {"click", "extract", "fill", "read_text", "wait_for"}:
                warnings.append(f"Recipe {recipe_index} step {step_index} should usually include selector or selectors.")
            for key in step:
                lowered = str(key).lower()
                if any(sensitive in lowered for sensitive in SENSITIVE_EXAMPLE_KEYS):
                    errors.append(f"Recipe {recipe_index} step {step_index} contains sensitive-looking field '{key}'.")
    return {"ok": not errors, "errors": errors, "warnings": warnings, "sanitized": sanitized, "count": len(sanitized)}


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None
