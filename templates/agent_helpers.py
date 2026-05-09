"""Local helper file for Hermes Browser Workspace.

Phase 1 treats this file as durable but not auto-mutable.
Use it for reusable parsing, selector helpers, and site-specific utility code
that does not require secrets or account-specific data.
"""


def normalize_text(value: str) -> str:
    return " ".join(value.split())
