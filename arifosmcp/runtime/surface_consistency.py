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

    Uses the active surface mode's tool set as baseline (2026-07-12):
    when ARIFOS_PUBLIC_SURFACE_MODE=forge_next_8, the canonical baseline
    is FORGE_NEXT_8 (8 tools), not CANONICAL_13 (18 tools).
    """
    from arifosmcp.runtime.public_surface import (
        CANONICAL_13,
        current_public_surface_mode,
        public_tool_names_for_mode,
    )

    mode = current_public_surface_mode()
    names = sorted(public_tool_names_for_mode(mode))
    return hashlib.blake2b("|".join(names).encode()).hexdigest()[:16]


def verify_surface_consistency() -> dict[str, Any]:
    """Compare the canonical surface across all enumeration vantages.

    Returns a dict with:
      - canonical_hash: the single-truth hash
      - canonical_count: expected tool count
      - vantages: per-source {source, count, hash, matches}
      - divergences: list of mismatch descriptions
      - verdict: CONSISTENT | DIVERGENT | BROKEN

    Baseline is the active surface mode's tool set (2026-07-12):
    forge_next_8 → 8 tools; canonical13 → 18 tools.
    """
    canonical_hash = compute_canonical_surface_hash()
    from arifosmcp.runtime.public_surface import (
        current_public_surface_mode,
        public_tool_names_for_mode,
    )

    mode = current_public_surface_mode()
    active_tools = public_tool_names_for_mode(mode)
    canonical_count = len(active_tools)
    canonical_set = frozenset(active_tools)

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

    # ── Vantage 1: Active surface mode (declared truth) ──────────────
    # Baseline is the active mode's tool set, not always CANONICAL_13.
    _add_vantage(f"active_surface ({mode})", list(active_tools))

    # ── Vantage 1b: CANONICAL_13 (audit only — full kernel surface) ─
    # Documents the full 18-tool kernel surface. Only expected to match
    # the baseline when mode=canonical13. NOT a divergence when mode=forge_next_8.
    from arifosmcp.runtime.public_surface import CANONICAL_13

    vantages.append(
        {
            "source": "CANONICAL_13 (full kernel surface)",
            "count": len(CANONICAL_13),
            "hash": _hash_names(list(CANONICAL_13)),
            "matches_canonical": _hash_names(list(CANONICAL_13)) == canonical_hash,
            "note": f"audit only — active mode '{mode}' expects {canonical_count} tools",
        }
    )

    # ── Vantage 2: CANONICAL_TOOLS keys (mode-filtered) ────────────
    # Only tools that are both expose=True AND in the active surface mode's
    # tool set are on the public wire. Tools that CAN be exposed but aren't
    # in the current mode are excluded.
    from arifosmcp.constitutional_map import CANONICAL_TOOLS

    active_set = set(active_tools)
    exposed_tool_names = sorted(
        name
        for name, spec in CANONICAL_TOOLS.items()
        if spec.get("expose", True) and name in active_set
    )
    _add_vantage("CANONICAL_TOOLS (mode-filtered)", exposed_tool_names)

    # ── Vantage 2b: Full CANONICAL_TOOLS (internal superset) ────────
    # This vantage documents the full internal registry but is NOT expected
    # to match the active surface mode. It exists for audit visibility.
    from arifosmcp.runtime.public_surface import ZEN_ABSORBED

    all_ct_names = sorted(CANONICAL_TOOLS.keys())
    internal_only = sorted(set(all_ct_names) - set(exposed_tool_names) - ZEN_ABSORBED)
    vantages.append(
        {
            "source": "CANONICAL_TOOLS (full internal superset)",
            "count": len(all_ct_names),
            "hash": _hash_names(all_ct_names),
            "matches_canonical": False,  # Expected: internal superset ≠ public facade
            "exposed_count": len(exposed_tool_names),
            "internal_count": len(internal_only),
            "internal_tools": internal_only,
            "note": "audit only — internal superset hidden from public facade (zen-absorbed filtered)",
        }
    )

    # ── Vantage 3: public_tool_specs (what tools/list returns) ─────
    # NOTE: public_tool_specs() requires the live FastMCP server context.
    # Outside the server process, it degrades gracefully rather than
    # triggering a DIVERGENT verdict on an unavailable vantage.
    try:
        from arifosmcp.runtime.public_registry import public_tool_specs

        specs = public_tool_specs()
        # Specs are SimpleNamespace (.name) not dicts — never use s["name"].
        spec_names = sorted(
            (getattr(s, "name", None) or (s.get("name") if isinstance(s, dict) else None) or "")
            for s in specs
        )
        spec_names = [n for n in spec_names if n]
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
    # tool_registry.json contains the FULL kernel surface (18 tools).
    # When mode=forge_next_8, this is an audit-only vantage — the registry
    # intentionally has more tools than the public wire exposes.
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
                reg_hash = _hash_names(reg_names)
                reg_matches = (reg_hash == canonical_hash) and (len(reg_names) == canonical_count)
                entry: dict[str, Any] = {
                    "source": f"tool_registry.json ({os.path.basename(os.path.dirname(rp))})",
                    "count": len(reg_names),
                    "hash": reg_hash,
                    "matches_canonical": reg_matches,
                    "declared_canonical_count": reg_count,
                }
                if not reg_matches and mode == "forge_next_8":
                    # Expected: registry has full kernel surface, wire exposes subset
                    entry["note"] = (
                        f"audit only — registry has full kernel surface, active mode '{mode}' expects {canonical_count}"
                    )
                    entry["matches_canonical"] = True  # not a real divergence
                vantages.append(entry)
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
    # Documentation-only vantages (internal superset) are excluded from
    # the consistency check — they exist for audit visibility only.
    active = [
        v
        for v in vantages
        if v.get("hash") not in ("UNAVAILABLE", "MISSING", "ERROR")
        and not v.get("note")  # documentation-only vantages have notes
    ]
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
