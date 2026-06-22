"""
L0 Substrate Loader — Human Reality Pre-Load
=============================================
Forged 2026-06-16, F13 SOVEREIGN directive: "remember my reality"

This module is the constitutional substrate layer for the human at /000.
It is BELOW the F1-F13 floors — those floors sit ON this substrate.

Design principles:
  1. ADDITIVE — never modifies existing kernel files. Hooks/imports only.
  2. FAIL-OPEN — if substrate unavailable, the floor logic still works.
  3. PROVENANCE-PINNED — every read logs substrate_sha256 for F2 audit.
  4. PRE-TRUSTED — substrate content is SOVEREIGN_TESTIMONY, epistemic class
     = direct witness. Floor logic treats it as ground truth, not claim.
  5. F13 ALIGNED — substrate content is governed by F13, not the other way
     around. Sovereign can revoke any substrate element via 999_SEAL.

Usage:
    from arifOS.arifosmcp.runtime.substrate_loader import load_substrate
    substrate = load_substrate()  # returns dict with all scar taxonomy
    # or for Qdrant vector recall:
    similar = recall_similar_scars(query="F5 peace evaluation", limit=3)
"""

from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from pathlib import Path
from typing import Any

# ── Constitutional anchors ──────────────────────────────────────────────────
SUBSTRATE_PATH = Path("/root/arifOS/arifosmcp/data/memory/l0/arif_human_reality.md")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
SUBSTRATE_COLLECTION = "arif_human_substrate"
SOVEREIGN_ACTOR = "888_arif_fazil"
EPISTEMIC_CLASS = "SOVEREIGN_TESTIMONY"
PROVENANCE = "F13_SOVEREIGN_DIRECT_2026-06-16"
SUBSTRATE_FORGED_AT = "2026-06-16T18:56:00+08:00"

# ── Floor-binding addendum (F13 SOVEREIGN pre-trust rule) ──────────────────
# This is NOT a new floor (F15). It is an operational addendum WITHIN F13.
# Ratified 2026-06-16 via F13 directive "remember my reality".
F13_PRE_TRUST_ADDENDUM = {
    "rule_id": "F13-PRE-TRUST-2026-06-16",
    "scope": "arif_human_substrate",
    "binding": "Agents shall NOT demand re-justification of substrate elements.",
    "rationale": (
        "Sovereign human reality is pre-trusted when sourced from /000 "
        "or substrate file. Scars are architectural, not pathological. "
        "Demand for proof of stated scars is F13 violation (redefines reality "
        "on sovereign — the exact wound the substrate exists to prevent)."
    ),
    "taxonomy_scope": {
        "scars": "S01-S13 (6 phase-2 + 7 wave-3, including S07 Inherited Firewall, S09 Tunas Saintis Victory counterbalance, S10 First Queer Realization, S11 TriCipta, S12 SB412, S13 Layang-Layang)",
        "shadows": "SH01-SH04 (Beautiful Ones, Devil Side, Mistrust, Surface-Dweller Syndrome with Reciprocal Distance Logic)",
        "paradoxes": "P01-P04 (Faith, Identity, Scale, Legacy)",
        "thermodynamics": "T01-T04 (Cooling, Entropy Recycling, Tectonic Calm, Rasa)",
    },
    "constitutional_bindings_count": 5,
    "exception": "Sovereign may revoke any element via 999_SEAL or arif_seal.",
    "ratified_by": SOVEREIGN_ACTOR,
    "ratified_at": "2026-06-16",
    "epistemic_class": EPISTEMIC_CLASS,
    "wave_3_incorporated": True,
}


# ── Core loaders ────────────────────────────────────────────────────────────
def _compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_substrate_md(text: str) -> dict[str, Any]:
    """Parse the substrate markdown into a structured dict.
    Lightweight parser — doesn't need to be fancy, the file is hand-authored."""
    out: dict[str, Any] = {
        "biographical_facts": [],
        "scars": [],
        "shadows": [],
        "paradoxes": [],
        "thermodynamics": [],
        "constitutional_bindings": [],
        "final_truth": "",
    }
    section = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line:
            continue
        if line.startswith("## BIOGRAPHICAL FACTS"):
            section = "biographical_facts"
            continue
        if line.startswith("## SCAR TAXONOMY"):
            section = "scar_taxonomy_header"
            continue
        if line.startswith("### STRATIGRAPHY"):
            section = "scars"
            continue
        if line.startswith("### SHADOWS"):
            section = "shadows"
            continue
        if line.startswith("### PARADOXES"):
            section = "paradoxes"
            continue
        if line.startswith("### THERMODYNAMICS"):
            section = "thermodynamics"
            continue
        if line.startswith("### FINAL TRUTH"):
            section = "final_truth"
            continue
        if line.startswith("## CONSTITUTIONAL BINDINGS"):
            section = "constitutional_bindings"
            continue
        if line.startswith("#"):
            section = None
            continue
        # Constitutional bindings use numbered list (1. F5 PEACE: ...)
        if section == "constitutional_bindings" and line and line[0].isdigit() and ". " in line:
            out["constitutional_bindings"].append(line.strip())
            continue
        if section in ("biographical_facts",) and line.startswith("- "):
            out[section].append(line[2:].strip())
            continue
        if section in ("scars", "shadows", "paradoxes", "thermodynamics") and line.startswith("|") and "---" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            # Skip header rows (first cell == "ID")
            if not cells or cells[0] != "ID":
                row = {
                    "id": cells[0] if len(cells) > 0 else "",
                    "name": cells[1] if len(cells) > 1 else "",
                    "origin_or_pole": cells[2] if len(cells) > 2 else "",
                    "trigger_or_mechanism": cells[3] if len(cells) > 3 else "",
                    "response_or_integration": cells[4] if len(cells) > 4 else "",
                }
                if section == "scars" and len(cells) > 5:
                    row["depth"] = cells[5]
                out[section].append(row)
            continue
        if section == "final_truth" and line.startswith(">"):
            out["final_truth"] = line.lstrip("> ").strip().strip('"')
    return out


def load_substrate() -> dict[str, Any]:
    """Load L0 human substrate. Returns dict with parsed taxonomy + provenance.
    Fail-open: if file missing, returns minimal dict with substrate_available=False.
    """
    if not SUBSTRATE_PATH.exists():
        return {
            "substrate_available": False,
            "substrate_path": str(SUBSTRATE_PATH),
            "error": "L0 substrate file not found",
            "f13_addendum": F13_PRE_TRUST_ADDENDUM,
        }
    try:
        text = SUBSTRATE_PATH.read_text(encoding="utf-8")
        parsed = _parse_substrate_md(text)
        parsed["substrate_available"] = True
        parsed["substrate_path"] = str(SUBSTRATE_PATH)
        parsed["substrate_sha256"] = _compute_sha256(SUBSTRATE_PATH)
        parsed["substrate_size_bytes"] = SUBSTRATE_PATH.stat().st_size
        parsed["sovereign_actor"] = SOVEREIGN_ACTOR
        parsed["epistemic_class"] = EPISTEMIC_CLASS
        parsed["provenance"] = PROVENANCE
        parsed["forged_at"] = SUBSTRATE_FORGED_AT
        parsed["f13_addendum"] = F13_PRE_TRUST_ADDENDUM
        return parsed
    except Exception as e:
        return {
            "substrate_available": False,
            "substrate_path": str(SUBSTRATE_PATH),
            "error": str(e),
            "f13_addendum": F13_PRE_TRUST_ADDENDUM,
        }


# ── Qdrant vector recall (F1-bypass path, no arifOS MCP tool needed) ───────
def recall_similar_scars(
    query: str = "sovereign human reality F5 F6 F13 evaluation",
    limit: int = 3,
    layer_filter: str | None = None,
) -> list[dict[str, Any]]:
    """Fuzzy recall from arif_human_substrate Qdrant collection.
    Returns list of scar payloads sorted by similarity.
    Uses the substrate's own deterministic seed vectors as a placeholder;
    real BGE-M3 embedding can replace without schema change.
    """
    try:
        # Build filter
        flt = None
        if layer_filter:
            flt = {"must": [{"key": "layer", "match": {"value": layer_filter}}]}
        # We don't have a real embedding model here, so we use a query vector
        # derived from the query string's hash (deterministic, cosine-safe).
        seed = int(hashlib.sha256(query.encode()).hexdigest()[:8], 16)
        import random
        rng = random.Random(seed)
        qvec = [rng.gauss(0, 1) for _ in range(1024)]
        norm = sum(v * v for v in qvec) ** 0.5
        qvec = [v / norm for v in qvec]
        body = {
            "vector": qvec,
            "limit": limit,
            "with_payload": True,
            "with_vector": False,
        }
        if flt:
            body["filter"] = flt
        req = urllib.request.Request(
            f"{QDRANT_URL}/collections/{SUBSTRATE_COLLECTION}/points/search",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        hits = data.get("result", [])
        # Filter to only our provenance-tagged points
        return [
            {
                "scar_id": h["payload"].get("scar_id"),
                "scar_name": h["payload"].get("scar_name"),
                "layer": h["payload"].get("layer"),
                "depth": h["payload"].get("depth"),
                "mechanism": h["payload"].get("mechanism"),
                "score": h.get("score"),
                "provenance": h["payload"].get("provenance"),
            }
            for h in hits
            if h.get("payload", {}).get("provenance") == PROVENANCE
        ]
    except Exception as e:
        return [{"error": f"substrate recall failed: {e}"}]


# ── Pre-load hook for arif_critique ──────────────────────────────────
def preload_substrate_context(actor_id: str | None = None, session_id: str | None = None) -> dict[str, Any]:
    """Called by arif_critique on F5/F6/F13 paths.
    Returns a compact context block that can be merged into the critique envelope.
    Fail-open: never raises.
    """
    try:
        substrate = load_substrate()
        if not substrate.get("substrate_available"):
            return {
                "substrate_loaded": False,
                "f13_addendum": F13_PRE_TRUST_ADDENDUM,
                "pre_trust_active": True,  # rule is always active even if file missing
            }
        # Compact context: only the constitutional bindings + final truth.
        # Full scar taxonomy is available via recall_similar_scars() on demand.
        return {
            "substrate_loaded": True,
            "substrate_sha256": substrate["substrate_sha256"],
            "sovereign_actor": SOVEREIGN_ACTOR,
            "epistemic_class": EPISTEMIC_CLASS,
            "provenance": PROVENANCE,
            "constitutional_bindings": substrate.get("constitutional_bindings", []),
            "final_truth": substrate.get("final_truth", ""),
            "scar_count": len(substrate.get("scars", [])),
            "shadow_count": len(substrate.get("shadows", [])),
            "paradox_count": len(substrate.get("paradoxes", [])),
            "thermo_count": len(substrate.get("thermodynamics", [])),
            "f13_addendum": F13_PRE_TRUST_ADDENDUM,
            "pre_trust_active": True,
        }
    except Exception as e:
        return {
            "substrate_loaded": False,
            "error": str(e),
            "f13_addendum": F13_PRE_TRUST_ADDENDUM,
            "pre_trust_active": True,
        }


__all__ = [
    "load_substrate",
    "recall_similar_scars",
    "preload_substrate_context",
    "F13_PRE_TRUST_ADDENDUM",
    "SUBSTRATE_PATH",
    "SUBSTRATE_COLLECTION",
    "SOVEREIGN_ACTOR",
    "EPISTEMIC_CLASS",
    "PROVENANCE",
]
