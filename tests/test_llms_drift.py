"""
test_llms_drift.py — Public Discovery Layer Drift Gate
═══════════════════════════════════════════════════════

Verifies the public llms.txt and constitutional.llms.txt artifacts
remain in sync with the live tool registry and with their delivery copies.

Any drift = F2 TRUTH violation + F11 AUDIT failure.

Ditempa Bukan Diberi — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).parents[1]


def _normalized_llms_hash(path: Path) -> str:
    """Hash with timestamp line stripped so generator re-runs are idempotent."""
    lines = path.read_text().splitlines(keepends=True)
    filtered = [line for line in lines if not line.startswith("--- Auto-generated")]
    return hashlib.sha256("".join(filtered).encode()).hexdigest()


def test_llms_txt_matches_generator():
    """arifOS/llms.txt must equal the output of scripts/generate_tool_manifest.py."""
    script = REPO_ROOT / "scripts" / "generate_tool_manifest.py"
    current = REPO_ROOT / "llms.txt"

    assert current.exists(), "SOT llms.txt missing"
    assert script.exists(), "manifest generator missing"

    before_hash = _normalized_llms_hash(current)
    result = subprocess.run(
        ["python", str(script)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"generate_tool_manifest.py failed: {result.stderr}"
    after_hash = _normalized_llms_hash(current)

    assert before_hash == after_hash, (
        "llms.txt is stale. Run `python scripts/generate_tool_manifest.py` and commit."
    )


def test_llms_txt_copies_in_sync():
    """All arifOS llms.txt delivery copies must match the SOT."""
    sot = REPO_ROOT / "llms.txt"
    copies = [
        REPO_ROOT / "static" / "llms.txt",
        REPO_ROOT / "arifosmcp" / "static" / "llms.txt",
        REPO_ROOT / "arifosmcp" / "sites" / "llms.txt",
        REPO_ROOT / "arifosmcp" / "sites" / "developer" / "llms.txt",
    ]
    sot_hash = _normalized_llms_hash(sot)
    for copy in copies:
        assert copy.exists(), f"llms.txt copy missing: {copy}"
        assert _normalized_llms_hash(copy) == sot_hash, (
            f"llms.txt copy drift: {copy}. Run sync from SOT."
        )


def test_constitutional_llms_copies_in_sync():
    """All constitutional.llms.txt delivery copies must match the SOT."""
    sot = REPO_ROOT / "constitutional.llms.txt"
    copies = [
        REPO_ROOT / "static" / "constitutional.llms.txt",
        REPO_ROOT / "arifosmcp" / "static" / "constitutional.llms.txt",
        REPO_ROOT / "arifosmcp" / "sites" / "constitutional.llms.txt",
    ]
    sot_hash = hashlib.sha256(sot.read_bytes()).hexdigest()
    for copy in copies:
        assert copy.exists(), f"constitutional.llms.txt copy missing: {copy}"
        assert hashlib.sha256(copy.read_bytes()).hexdigest() == sot_hash, (
            f"constitutional.llms.txt copy drift: {copy}. Run sync from SOT."
        )


def test_constitutional_llms_lists_all_canonical_tools():
    """constitutional.llms.txt must mention every canonical tool."""
    from arifosmcp.constitutional_map import CANONICAL_TOOLS

    sot = REPO_ROOT / "constitutional.llms.txt"
    content = sot.read_text()
    missing = [name for name in CANONICAL_TOOLS if f"tool: {name}" not in content]
    assert not missing, f"constitutional.llms.txt missing canonical tools: {missing}"
