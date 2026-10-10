"""
test_actor_id_default_anonymous_regression.py — Regression test (T1, test-only)

Locks in the 2026-10-10 P0 identity-bypass hygiene fix. Before the fix, nine
default-string sites in the kernel hardcoded actor_id="ARIF" — meaning any
omitted actor_id was attributed to the sovereign, not "anonymous". After
the fix, every default is "anonymous" so an unverified caller cannot get
"ARIF" attribution by omission.

The actual P0 (cryptographic proof bypass in _arif_session_init) is
separate and F13-gated. THIS test is a regression guard for the hygiene
fix: it fails if any of the nine sites regresses to "ARIF" default,
which is a known exploitable condition.

If the test fails: a regression has reintroduced an unauthenticated
"ARIF" attribution path. Investigate with git log, then re-apply the
9-site fix.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO = Path("/root/arifOS/arifosmcp")

# The 9 fixed sites (file -> banned signatures/defaults).
# Each entry is (file, list_of_regex_patterns) that MUST NOT appear in
# non-comment, non-test, non-docstring positions.
FIXED_SITES = [
    (
        REPO / "runtime" / "tools.py",
        [
            re.compile(r'actor_id:\s*str\s*=\s*[\'"]ARIF[\'"]'),
            # The .get fallback in _arif_session_init
            re.compile(r'\.get\(\s*[\'"]actor_id[\'"]\s*,\s*[\'"]ARIF[\'"]\s*\)'),
        ],
    ),
    (
        REPO / "runtime" / "vault_registry.py",
        [
            re.compile(r'actor_id:\s*str\s*=\s*[\'"]ARIF[\'"]'),
        ],
    ),
    (
        REPO / "runtime" / "copilot_gateway.py",
        [
            re.compile(r'actor_id:\s*str\s*=\s*[\'"]ARIF[\'"]'),
        ],
    ),
    (
        REPO / "server.py",
        [
            # The body.get("actor_id") or "ARIF" route-15 fallback
            re.compile(r'body\.get\(\s*[\'"]actor_id[\'"]\s*\)\s*or\s*[\'"]ARIF[\'"]'),
        ],
    ),
]


def _strip_comments_and_docstrings(src: str) -> list[tuple[int, str]]:
    """Return (line_no, content) for non-comment, non-string-literal lines.

    Tolerant: tracks # comments and triple-quote-bounded string contexts,
    but does not attempt to fully tokenize Python. Good enough to drop the
    obvious noise (line comments, docstring bodies) without false negatives.
    """
    out: list[tuple[int, str]] = []
    in_triple = False
    triple_quote: str | None = None
    for lineno, line in enumerate(src.splitlines(), start=1):
        stripped = line.lstrip()
        # Triple-quoted string tracking (docstrings / multi-line strings)
        if not in_triple and (chr(34) * 3 in line or chr(39) * 3 in line):
            for q in (chr(34) * 3, chr(39) * 3):
                if q in line and line.count(q) == 1:
                    in_triple = True
                    triple_quote = q
                    break
        if in_triple:
            if triple_quote and triple_quote in line:
                in_triple = False
                triple_quote = None
            continue
        if stripped.startswith("#"):
            continue
        out.append((lineno, line))
    return out


@pytest.mark.parametrize(
    "file_path,patterns",
    FIXED_SITES,
    ids=lambda v: str(v) if not isinstance(v, list) else "patterns",
)
def test_no_actor_id_default_arif(file_path, patterns):
    """No fixed site has regressed to actor_id="ARIF" default."""
    if not file_path.exists():
        pytest.skip(f"{file_path} not present in this checkout")
    src = file_path.read_text(encoding="utf-8")
    code_lines = _strip_comments_and_docstrings(src)
    offenders: list[tuple[int, str]] = []
    for lineno, line in code_lines:
        for pat in patterns:
            if pat.search(line):
                offenders.append((lineno, line.strip()))
    assert not offenders, (
        f"REGRESSION in {file_path}: 'ARIF' default re-introduced at:\n"
        + "\n".join(f"  L{ln}: {c}" for ln, c in offenders)
    )


def test_actor_id_default_uses_anonymous_string():
    """Sanity: the new default value 'anonymous' actually appears in the fixed files."""
    expected_count = 0
    for file_path, _ in FIXED_SITES:
        if not file_path.exists():
            continue
        src = file_path.read_text(encoding="utf-8")
        expected_count += len(re.findall(r'[\'"]anonymous[\'"]', src))
    assert expected_count >= 5, (
        f"Expected 'anonymous' to appear in the fixed files; found only "
        f"{expected_count} occurrences. The 2026-10-10 fix may not be in place."
    )


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))
