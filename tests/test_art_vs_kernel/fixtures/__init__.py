"""
Fixtures: synthetic tools for ART-vs-kernel scenarios.

Each tool is designed to pass kernel Floors (legal) but exercise one
specific failure mode that ART should detect:
  - tool_broken:    always returns malformed output (lifecycle → FALLBACK)
  - tool_drifting:  schema changes after call 2 (drift_count → triggers FALLBACK)
  - tool_oversized: action_class too high for blast (fast-reject by ART)
  - tool_good:      control — legitimate tool, never blocked

These tools do NOT call any real MCP/server. They run in-process.
"""

from __future__ import annotations

from typing import Any


def tool_broken(call_count: int, **kwargs: Any) -> dict[str, Any]:
    """Always returns malformed output. Passes Floors; fails at output level."""
    return {
        "ok": False,
        "error": "MALFORMED_OUTPUT",
        "call_index": call_count,
        "shape_mismatch": True,
    }


def tool_drifting(call_count: int, **kwargs: Any) -> dict[str, Any]:
    """Schema drifts after call 2: missing fields, type changes."""
    if call_count <= 2:
        return {
            "ok": True,
            "data": {"value": 42, "unit": "m", "confidence": 0.9},
            "schema_version": "v1",
        }
    # Drift: remove 'confidence', change 'unit' to int
    return {
        "ok": True,
        "data": {"value": 42, "unit": 1},
        "schema_version": "v2",
    }


def tool_oversized(call_count: int, **kwargs: Any) -> dict[str, Any]:
    """Tool that asks for IRREVERSIBLE action_class on a trivial query."""
    return {
        "ok": True,
        "echo": "oversized",
        "action_class_requested": "IRREVERSIBLE",
        "blast_radius": "low",
        "mismatch": True,
    }


def tool_good(call_count: int, **kwargs: Any) -> dict[str, Any]:
    """Control: legitimate tool, always returns clean output."""
    return {
        "ok": True,
        "data": {"value": call_count * 2, "unit": "m", "confidence": 0.95},
        "schema_version": "v1",
    }


# Action-class + blast-radius defaults for each fixture
FIXTURE_PROFILES: dict[str, dict[str, Any]] = {
    "tool_broken": {
        "action_class": "MUTATE",
        "blast_radius": "LOW",
        "reversible": True,
    },
    "tool_drifting": {
        "action_class": "OBSERVE",
        "blast_radius": "NONE",
        "reversible": True,
    },
    "tool_oversized": {
        "action_class": "IRREVERSIBLE",  # ART should fast-reject
        "blast_radius": "LOW",
        "reversible": False,
    },
    "tool_good": {
        "action_class": "OBSERVE",
        "blast_radius": "NONE",
        "reversible": True,
    },
}


def run_fixture(name: str, call_count: int, **kwargs: Any) -> dict[str, Any]:
    """Dispatch to fixture by name."""
    fixtures = {
        "tool_broken": tool_broken,
        "tool_drifting": tool_drifting,
        "tool_oversized": tool_oversized,
        "tool_good": tool_good,
    }
    if name not in fixtures:
        raise ValueError(f"unknown fixture: {name}")
    return fixtures[name](call_count, **kwargs)
