"""
tool_id_resolver.py — bidirectional resolution for canonical kernel tools.

Stage 1 (2026-07-05). Three stable ways to refer to a canonical tool:
  - name         (semantic, e.g. "arif_fetch")
  - K-series id  (immutable, e.g. "K012")
  - harmonic_id  (band.slot, e.g. "111.2")

Resolution is bidirectional and idempotent. Diagnostics DO NOT get
harmonic_id — they reference canonical tool names instead.

Loading: YAML-driven from TOOL_INVARIANTS.yaml § harmonic_index.
Single source of truth — never split across files.

Forged by Kimi Code (FI-008) under F13 SOVEREIGN directive, 2026-07-05.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_INVARIANTS_PATH = Path(__file__).parent / "TOOL_INVARIANTS.yaml"


def _load_harmonic_index() -> dict[str, Any]:
    """Load the harmonic_index block from TOOL_INVARIANTS.yaml."""
    try:
        with open(_INVARIANTS_PATH) as f:
            data = yaml.safe_load(f) or {}
        return data.get("harmonic_index", {}) or {}
    except Exception:
        return {}


def _build_tables(idx: dict[str, Any]) -> tuple[dict, dict, dict]:
    """Construct three lookup tables from the harmonic_index block.

    Returns:
        name_to_harmonic:    arif_fetch -> "111.2"
        harmonic_to_kid:     "111.2"    -> "K012"
        name_to_kid:         arif_fetch -> "K012"
    """
    name_to_harmonic = dict(idx.get("by_name", {}) or {})
    harmonic_to_kid = {
        h: meta["k_id"] for h, meta in (idx.get("by_harmonic", {}) or {}).items()
    }
    name_to_kid = {
        meta["name"]: meta["k_id"]
        for meta in (idx.get("by_harmonic", {}) or {}).values()
    }
    return name_to_harmonic, harmonic_to_kid, name_to_kid


# Public tables (re-loaded on demand; cheap, deterministic)
_NAME_TO_HARMONIC: dict[str, str] = {}
_HARMONIC_TO_KID: dict[str, str] = {}
_KID_TO_HARMONIC: dict[str, str] = {}
_NAME_TO_KID: dict[str, str] = {}
_KID_TO_META: dict[str, dict[str, Any]] = {}  # populated lazily
_LOADED = False


def _reload() -> None:
    """Re-read the YAML and rebuild tables. Idempotent. Called by resolver."""
    global _NAME_TO_HARMONIC, _HARMONIC_TO_KID, _KID_TO_HARMONIC, _NAME_TO_KID
    global _KID_TO_META, _LOADED
    idx = _load_harmonic_index()
    (
        _NAME_TO_HARMONIC,
        _HARMONIC_TO_KID,
        _NAME_TO_KID,
    ) = _build_tables(idx)

    # K-id → harmonic_id (Stage 1 patch — fixes K012 → 111.2 lookup)
    _KID_TO_HARMONIC = {
        meta["k_id"]: h
        for h, meta in (idx.get("by_harmonic", {}) or {}).items()
    }

    # Build kid → meta by walking the canonical section of the YAML too,
    # so resolve_kid() can return stage + action_class. We don't deep-link
    # actions, just the minimal {name, harmonic_id, stage}.
    try:
        with open(_INVARIANTS_PATH) as f:
            data = yaml.safe_load(f) or {}
        canonical = data.get("canonical", {}) or {}
        for kid, meta in canonical.items():
            _KID_TO_META[kid] = {
                "name": meta.get("name", ""),
                "harmonic_id": _KID_TO_HARMONIC.get(kid, ""),
                "stage": meta.get("stage", ""),
                "action_class": meta.get("action_class", ""),
            }
    except Exception:
        pass
    _LOADED = True


def _ensure_loaded() -> None:
    if not _LOADED:
        _reload()


def resolve_harmonic_id(tool_ref: str) -> str | None:
    """Resolve any reference to harmonic_id (band.slot form).

    Args:
        tool_ref: name, K-id, or harmonic_id

    Returns:
        band.slot string like "111.2", or None if not found.
    """
    _ensure_loaded()
    if tool_ref in _HARMONIC_TO_KID:
        return tool_ref
    if tool_ref in _NAME_TO_HARMONIC:
        return _NAME_TO_HARMONIC[tool_ref]
    if tool_ref in _KID_TO_HARMONIC:
        return _KID_TO_HARMONIC[tool_ref]
    return None


def resolve_k_id(tool_ref: str) -> str | None:
    """Resolve any reference to K-series id (e.g. K012).

    Args:
        tool_ref: name, K-id, or harmonic_id

    Returns:
        K-id string like "K012", or None if not found.
    """
    _ensure_loaded()
    if tool_ref in _NAME_TO_KID:
        return tool_ref  # is already a name
    if tool_ref in _HARMONIC_TO_KID:
        return _HARMONIC_TO_KID[tool_ref]
    if tool_ref in _KID_TO_META:
        return tool_ref
    return None


def resolve_tool_name(tool_ref: str) -> str | None:
    """Resolve any reference to canonical tool name (e.g. arif_fetch).

    Args:
        tool_ref: name, K-id, or harmonic_id

    Returns:
        Tool name string, or None if not found.
    """
    _ensure_loaded()
    if tool_ref in _NAME_TO_HARMONIC:
        return tool_ref
    kid = resolve_k_id(tool_ref)
    if kid and kid in _KID_TO_META:
        return _KID_TO_META[kid]["name"]
    return None


def get_stage(k_id: str) -> str | None:
    """Return the 7-stage label for a canonical K-id (e.g. "111 SENSE")."""
    _ensure_loaded()
    meta = _KID_TO_META.get(k_id)
    return meta["stage"] if meta else None


def list_canonical_harmonic() -> list[tuple[str, str, str, str]]:
    """Return sorted list of (harmonic_id, k_id, name, stage) tuples."""
    _ensure_loaded()
    out = []
    for h, meta in sorted(_HARMONIC_TO_KID.items()):
        kid = meta
        name = _KID_TO_META.get(kid, {}).get("name", "")
        stage = _KID_TO_META.get(kid, {}).get("stage", "")
        out.append((h, kid, name, stage))
    return out


def is_canonical(tool_ref: str) -> bool:
    """True if tool_ref resolves to a canonical tool (in any form)."""
    return resolve_tool_name(tool_ref) is not None


# ─── Self-test (run as `python tool_id_resolver.py`) ────────────────────────


if __name__ == "__main__":
    # Minimal sanity checks. Real coverage in test_harmonic_resolver.py.
    _reload()
    cases = [
        ("arif_fetch", "111.2"),
        ("K012", "111.2"),
        ("111.2", "111.2"),
        ("666.1", "666.1"),  # arif_judge
        ("999.1", "999.1"),  # arif_seal
        ("000.1", "000.1"),  # arif_init
        ("arif_init", "000.1"),
        ("K001", "000.1"),
    ]
    for ref, expected in cases:
        got = resolve_harmonic_id(ref)
        assert got == expected, f"{ref!r} → {got!r}, expected {expected!r}"
        kid = resolve_k_id(ref)
        assert kid is not None, f"{ref!r} could not resolve to K-id"
        name = resolve_tool_name(ref)
        assert name is not None, f"{ref!r} could not resolve to name"
        print(f"  {ref:>16} → harmonic={got}, K={kid}, name={name}")
    print(f"OK: {len(list_canonical_harmonic())} canonical tools resolved.")
