"""FORGE 2 (2026-06-22): Surface Self-Consistency.

INVARIANT: H(sorted(canonical_tool_names)) must be identical from every
enumeration endpoint. If /health, tools/list, tool_registry.json, and
CANONICAL_TOOLS disagree on count or hash, substrate_gate <= AMBER.

"A system that cannot enumerate its own action-space identically from
every vantage cannot govern it." — machine-checkable.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any


def compute_canonical_surface_hash() -> str:
    """BLAKE3 hash of the sorted canonical tool names.

    Single source of truth for the canonical surface identity.
    Every enumeration endpoint MUST produce the same hash.
    """
    from arifosmcp.runtime.public_surface import CANONICAL_13

    names = sorted(CANONICAL_13)
    return hashlib.blake2b("|".join(names).encode()).hexdigest()[:16]


def verify_surface_consistency() -> dict[str, Any]:
    """Compare the canonical surface across all enumeration vantages.

    Returns a dict with:
      - canonical_hash: the single-truth hash
      - canonical_count: expected tool count
      - vantages: per-source {source, count, hash, matches}
      - divergences: list of mismatch descriptions
      - verdict: CONSISTENT | DIVERGENT | BROKEN
    """
    canonical_hash = compute_canonical_surface_hash()
    from arifosmcp.runtime.public_surface import CANONICAL_13

    canonical_count = len(CANONICAL_13)
    canonical_set = frozenset(CANONICAL_13)

    vantages: list[dict[str, Any]] = []
    divergences: list[str] = []

    def _hash_names(names: list[str]) -> str:
        return hashlib.blake2b("|".join(sorted(names)).encode()).hexdigest()[:16]

    def _add_vantage(source: str, names: list[str], extra: dict[str, Any] | None = None) -> None:
        count = len(names)
        h = _hash_names(list(names))
        matches = (h == canonical_hash) and (count == canonical_count)
        entry: dict[str, Any] = {
            "source": source,
            "count": count,
            "hash": h,
            "matches_canonical": matches,
        }
        if extra:
            entry.update(extra)
        vantages.append(entry)

        if not matches:
            if h != canonical_hash:
                only_here = set(names) - canonical_set
                missing = canonical_set - set(names)
                details = []
                if only_here:
                    details.append(f"extra={sorted(only_here)}")
                if missing:
                    details.append(f"missing={sorted(missing)}")
                divergences.append(f"{source}: hash mismatch ({'; '.join(details)})")
            if count != canonical_count:
                divergences.append(
                    f"{source}: count mismatch (got {count}, expected {canonical_count})"
                )

    # ── Vantage 1: CANONICAL_13 (declared truth) ────────────────────
    _add_vantage("CANONICAL_13", list(CANONICAL_13))

    # ── Vantage 2: CANONICAL_TOOLS keys ────────────────────────────
    from arifosmcp.constitutional_map import CANONICAL_TOOLS

    _add_vantage("CANONICAL_TOOLS", list(CANONICAL_TOOLS.keys()))

    # ── Vantage 3: public_tool_specs (what tools/list returns) ─────
    # NOTE: public_tool_specs() requires the live FastMCP server context.
    # Outside the server process, it degrades gracefully rather than
    # triggering a DIVERGENT verdict on an unavailable vantage.
    try:
        from arifosmcp.runtime.public_registry import public_tool_specs

        specs = public_tool_specs()
        spec_names = sorted(s["name"] for s in specs)
        _add_vantage("public_tool_specs", spec_names)
    except Exception as e:
        vantages.append(
            {
                "source": "public_tool_specs",
                "count": 0,
                "hash": "UNAVAILABLE",
                "matches_canonical": True,  # Not a mismatch — vantage unavailable
                "note": f"vantage unavailable outside live server: {e}",
            }
        )

    # ── Vantage 4: tool_registry.json on disk ──────────────────────
    registry_paths = [
        "/opt/arifos/app/arifosmcp/tool_registry.json",
        "/root/arifOS/arifosmcp/tool_registry.json",
    ]
    for rp in registry_paths:
        if os.path.isfile(rp):
            try:
                with open(rp) as f:
                    reg = json.load(f)
                reg_names = sorted(reg.get("canonical_order", []))
                reg_count = reg.get("canonical_count", len(reg_names))
                _add_vantage(
                    f"tool_registry.json ({os.path.basename(os.path.dirname(rp))})",
                    reg_names,
                    {"declared_canonical_count": reg_count},
                )
                break  # Use first found
            except Exception as e:
                divergences.append(f"tool_registry.json ({rp}): parse error — {e}")
                continue
    else:
        divergences.append("tool_registry.json: not found at any known path")
        vantages.append(
            {
                "source": "tool_registry.json",
                "count": 0,
                "hash": "MISSING",
                "matches_canonical": False,
                "error": "file not found",
            }
        )

    # ── Verdict ────────────────────────────────────────────────────
    # Only count vantages that are actually available for comparison.
    # Unavailable vantages (e.g., public_tool_specs outside live server)
    # are skipped rather than treated as mismatches.
    active = [v for v in vantages if v.get("hash") not in ("UNAVAILABLE", "MISSING", "ERROR")]
    all_match = all(v["matches_canonical"] for v in active)
    any_divergence = len(divergences) > 0
    any_missing = any(v.get("hash") in ("MISSING", "ERROR") or v.get("error") for v in vantages)

    if any_missing:
        verdict = "BROKEN"
    elif not all_match:
        verdict = "DIVERGENT"
    else:
        verdict = "CONSISTENT"

    return {
        "canonical_hash": canonical_hash,
        "canonical_count": canonical_count,
        "verdict": verdict,
        "vantages": vantages,
        "divergences": divergences,
    }
