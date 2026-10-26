"""Guard: llms.txt mirrors stay generator-owned and claim-clean (2026-10-25, 333-AGI).

Failure class prevented (commit 3980bbedf, "docs(sync) … update llms.txt mirrors"):
a hand mirror-sync edited the five tracked llms.txt copies and smuggled in an
unsupported registry claim ("Registry status: Verified on Glama (Score A) …")
that scripts/generate_tool_manifest.py never emitted. The claim was removed by
regeneration on 2026-10-25; this gate keeps it from coming back:

  1. generator output carries no registry-status / "Verified on" claim;
  2. every tracked mirror equals generator output modulo the timestamp footer
     (mirrors are regenerate-only — hand edits fail here);
  3. no mirror carries a registry-status claim (belt).

Run: pytest tests/test_llms_mirror_sync.py -q
"""

from __future__ import annotations

import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

MIRRORS = [
    "llms.txt",
    "static/llms.txt",
    "arifosmcp/static/llms.txt",
    "arifosmcp/sites/llms.txt",
    "arifosmcp/sites/developer/llms.txt",
]

CLAIM_RE = re.compile(r"registry status|verified on glama", re.IGNORECASE)
TS_RE = re.compile(r"^--- Auto-generated .* ---$", re.MULTILINE)
# The version line embeds the INSTALLED arifos package version
# (importlib.metadata) — environment metadata, not mirror content.
# Normalized so the gate catches hand-edits, not interpreter drift.
VER_RE = re.compile(r"(?m)^> Version: [^·]+·")


def _normalize(text: str) -> str:
    text = VER_RE.sub("> Version: <INSTALLED> ·", text)
    return TS_RE.sub("--- Auto-generated <TIMESTAMP> ---", text)


def _generated() -> str:
    import generate_tool_manifest as g  # scripts/ on sys.path

    return g.generate_llms_txt()


def test_generator_emits_no_registry_claim() -> None:
    out = _generated()
    assert not CLAIM_RE.search(out), (
        "generator reintroduced an unsupported registry claim — "
        "remove it from scripts/generate_tool_manifest.py, do not edit mirrors"
    )


def test_mirrors_match_generator_modulo_timestamp() -> None:
    gen = _normalize(_generated())
    for rel in MIRRORS:
        path = os.path.join(REPO_ROOT, rel)
        assert os.path.isfile(path), f"missing mirror: {rel}"
        with open(path, encoding="utf-8") as f:
            body = _normalize(f.read())
        assert body == gen, (
            f"{rel} drifted from generator output (hand-edit or stale sync) — "
            "resync with: python3 scripts/generate_tool_manifest.py"
        )


def test_mirrors_carry_no_registry_claim() -> None:
    for rel in MIRRORS:
        path = os.path.join(REPO_ROOT, rel)
        with open(path, encoding="utf-8") as f:
            body = f.read()
        assert not CLAIM_RE.search(body), f"{rel} carries an unsupported registry claim"
