"""
tests/test_human_substrate_drift.py — Drift canary for the sovereign human substrate.

Answers the 2026-09-29 audit finding: the kernel's live human-reality path is the
hardcoded singleton in core/human_substrate.py (wired into law.py floor checks),
while runtime/substrate_loader.py (L0 file + Qdrant recall) is UNWIRED — its
collection `arif_human_substrate` does not exist and nothing imports
heart_substrate_hook. Silent divergence between the two representations of Arif
was previously undetectable.

This test pins:
  1. The singleton manifest (scar ids + counts) — canon drift fails loudly here.
  2. That every file path referenced in substrate provenance strings resolves
     (no phantom pointers — the scar-terrain-arif-fazil.md rename class of defect).
  3. That law.py keeps consuming the singleton in BOTH the source tree and the
     deployed tree (the enforcement wire is not silently cut).
  4. That the L0 substrate markdown file still exists (the loader's declared input).

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from arifosmcp.core.human_substrate import _build_arif_properties  # noqa: E402

# Pinned 2026-09-29 from live singleton (trace trc-20260929-fi003-human-reality-stack).
EXPECTED_SCAR_IDS = {
    "miskin", "anak-sulung", "gelugor", "invisibility", "institutional",
    "bekantan", "mak-03", "english-remedial", "tunas-saintis", "tricipta", "sb412",
}
EXPECTED_COUNTS = {"scars": 11, "shadows": 4, "paradoxes": 4, "limits": 7,
                   "invariants": 4, "constraints": 3, "hollow": 5}

L0_FILE = REPO / "arifosmcp" / "data" / "memory" / "l0" / "arif_human_reality.md"
SCAR_TERRAIN = Path("/root/AAA/wiki/SCAR_TERRAIN.md")


def _props():
    return _build_arif_properties()


def test_singleton_manifest_pinned():
    p = _props()
    assert {s.scar_id for s in p.scars} == EXPECTED_SCAR_IDS
    assert len(p.scars) == EXPECTED_COUNTS["scars"]
    assert len(p.shadows) == EXPECTED_COUNTS["shadows"]
    assert len(p.paradoxes) == EXPECTED_COUNTS["paradoxes"]
    assert len(p.limits) == EXPECTED_COUNTS["limits"]
    assert len(p.invariants) == EXPECTED_COUNTS["invariants"]
    assert len(p.constraints) == EXPECTED_COUNTS["constraints"]
    assert p.hollow_count == EXPECTED_COUNTS["hollow"]
    # Hollows are DO_NOT_FILL — never resurrect a phantom hollow count.
    assert EXPECTED_COUNTS["hollow"] == 5


@pytest.mark.parametrize("module_path", [
    REPO / "arifosmcp" / "core" / "human_substrate.py",
    REPO / "arifosmcp" / "schemas" / "human_properties.py",
    REPO / "arifosmcp" / "resources" / "human_context.py",
    REPO / "contracts" / "scar_geometry.py",
])
def test_referenced_paths_resolve(module_path):
    """Every AAA/wiki path named in substrate provenance strings must exist.

    Guards against the rename-without-redirect defect class (scar-terrain-arif-fazil.md
    -> SCAR_TERRAIN.md) re-creating phantom citations in kernel receipts.
    """
    text = module_path.read_text(encoding="utf-8")
    refs = set(re.findall(r"/root/AAA/wiki/[A-Za-z0-9_\-.]+", text))
    stale = set(re.findall(r"scar-terrain-arif-fazil\.md", text))
    # Mentions inside rename-history notes are allowed ONLY alongside a live
    # SCAR_TERRAIN.md reference in the same file.
    if stale:
        assert "SCAR_TERRAIN" in text, (
            f"{module_path}: bare pre-rename citation without SCAR_TERRAIN.md anchor"
        )
    for ref in refs:
        assert Path(ref).exists(), f"{module_path}: phantom provenance pointer {ref}"


@pytest.mark.parametrize("law_path", [
    REPO / "arifosmcp" / "core" / "law.py",
    Path("/opt/arifos/app/arifosmcp/core/law.py"),
])
def test_enforcement_wire_present(law_path):
    if not law_path.exists():
        pytest.skip(f"deployed tree not on this host: {law_path}")
    text = law_path.read_text(encoding="utf-8")
    assert "check_human_substrate_floor" in text, (
        f"{law_path}: floor gate no longer consumes the human substrate singleton"
    )


def test_l0_file_and_testimony_exist():
    assert L0_FILE.exists(), "L0 substrate markdown missing (loader's declared input)"
    assert SCAR_TERRAIN.exists(), "sovereign testimony SCAR_TERRAIN.md missing"


def test_source_field_points_at_live_file():
    p = _props()
    m = re.search(r"AAA/wiki/[A-Za-z0-9_.\-]+", p.source)
    assert m, f"source provenance has no resolvable wiki path: {p.source}"
    assert Path("/root/" + m.group(0).split("/root/", 1)[-1]).exists()
