"""
Static check: no protected tool re-implements auth logic inline.

Per the audit: "Tool implementations MUST NOT repeat this logic."
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Patterns that signal inline auth logic (re-implementing the gate).
FORBIDDEN_PATTERNS = [
    re.compile(r"verify_signature", re.IGNORECASE),
    re.compile(r"decode_jwt", re.IGNORECASE),
    re.compile(r"hvac_key\.", re.IGNORECASE),
    re.compile(r"verify_token|verify_authorization|verify_session"),
    re.compile(r"aud\s*==\s*['\"]wealth['\"]"),
    re.compile(r"aud\s*==\s*['\"]arifOS['\"]"),
]

# Paths where protected tools might live. We scan only protected-tool locations.
SCAN_ROOTS = [
    Path("/root/arifOS/arifosmcp/runtime/rest_routes"),
    Path("/root/arifOS/arifosmcp/runtime/wealth"),
]


def test_no_inline_auth_in_protected_modules() -> None:
    findings: list[tuple[str, int, str]] = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            try:
                src = path.read_text(encoding="utf-8")
            except Exception:
                continue
            for lineno, line in enumerate(src.splitlines(), start=1):
                for pat in FORBIDDEN_PATTERNS:
                    if pat.search(line):
                        findings.append((str(path), lineno, line.strip()[:120]))
    if findings:
        msg = "\n".join(f"  {p}:{ln}: {line}" for p, ln, line in findings)
        pytest.fail(f"Inline auth logic detected (must use the audit-mandated middleware):\n{msg}")
