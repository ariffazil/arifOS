#!/usr/bin/env python3
"""
gen_tools_sot.py — M3 codegen: emit tools_sot.yaml from constitutional_map.py

GENERATED — DO NOT HAND-EDIT tools_sot.yaml.
Re-run this script whenever constitutional_map.py canon changes:
    python3 scripts/gen_tools_sot.py > tools_sot.yaml

Source of truth:
    CORE_NINE         — ordered list of the 8 public tools
    CORE_NINE_STAGE_MAP — canonical stage → tool mapping (header says 666=JUDGE)
    CANONICAL_TOOLS   — full tool specs (modes, floors, risk_tier)

We deliberately skip stage 888 (legacy "compose absorbed into forge" —
per CORE_NINE_STAGE_MAP comment). The ToolStage enum currently says
JUDGE='888' which contradicts the constitutional_map header; that
inconsistency is on M6 (sovereign decision stub D5) — not solved here.

F2 acceptance: emitted file has ONE stage per tool, stages derived from
the constitutional_map spine, mode aliases deduplicated.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make arifosmcp importable when run from repo root.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from arifosmcp.constitutional_map import (  # noqa: E402
    CANONICAL_TOOLS,
    CORE_NINE,
    CORE_NINE_STAGE_MAP,
)


def _invert_stage_map(stage_map: dict[str, str]) -> dict[str, str]:
    """stage→tool becomes tool→stage. Skips stage 888 (legacy compose alias).

    The CORE_NINE_STAGE_MAP has 9 entries for 8 tools because 888 is the
    legacy "compose absorbed into forge" alias for arif_forge. We drop
    the 888 entry FIRST so the inverted map has clean tool→stage pairs
    with arif_forge correctly mapped to its canonical 777.
    """
    inverted: dict[str, str] = {}
    for stage, tool in stage_map.items():
        if stage == "888":
            # Legacy "compose absorbed into forge" — drop. The canonical
            # 777 entry for arif_forge remains and wins in the inverted map.
            continue
        inverted[tool] = stage
    return inverted


def _clean_description(text: str) -> str:
    """Collapse internal mode aliases into the canonical tool description.

    The CANONICAL_TOOLS descriptions include parenthetical mode lists like
    "(modes: init, light, resume, canary, ...)". We keep these as a
    single line and strip trailing whitespace — no semantic change.
    """
    return " ".join(text.split())


def emit_tools_sot() -> str:
    """Build the canonical tools_sot.yaml content from constitutional_map."""
    tool_to_stage = _invert_stage_map(CORE_NINE_STAGE_MAP)

    # Determine which stages are canonical (skip 888 legacy alias).
    canonical_tools_in_order = [
        t for t in CORE_NINE
        if tool_to_stage.get(t) and tool_to_stage[t] != "888"
    ]

    lines: list[str] = []

    # ── Header — every line must be safe for the surface-map lint ────────
    lines.append("# tools_sot.yaml — GENERATED. DO NOT HAND-EDIT.")
    lines.append("# Source of truth: arifosmcp/constitutional_map.py")
    lines.append("# Regenerate via: python3 scripts/gen_tools_sot.py > tools_sot.yaml")
    lines.append("#")
    lines.append("# M3 codegen contract:")
    lines.append("#   - one stage per tool (sourced from CORE_NINE_STAGE_MAP)")
    lines.append("#   - 8 canonical public tools only (KERNEL_ABI_8)")
    lines.append('#   - 888 legacy "compose absorbed into forge" alias is DROPPED')
    lines.append("#   - if constitutional_map canon changes, regenerate this file")
    lines.append("---")
    lines.append("sot_source: constitutional_map.py")
    lines.append("sot_version: v2026.07.31-M3-codegen")
    lines.append("canonical_tools: 8")
    lines.append("tools:")
    lines.append("")

    for tool_id in canonical_tools_in_order:
        spec = CANONICAL_TOOLS.get(tool_id)
        if not spec:
            # CORE_NINE has an entry not present in CANONICAL_TOOLS — surface drift.
            print(
                f"[gen_tools_sot] WARNING: CORE_NINE entry '{tool_id}' missing "
                f"from CANONICAL_TOOLS; skipping (surface drift)",
                file=sys.stderr,
            )
            continue

        stage = tool_to_stage[tool_id]
        description = _clean_description(spec.get("description", ""))
        floors = spec.get("floors", [])
        risk_tier = spec.get("risk_tier", "unknown")
        modes = spec.get("modes", [])

        lines.append(f"  - id: {tool_id}")
        lines.append(f"    name: {spec.get('name', tool_id)}")
        lines.append(f"    stage: '{stage}'")
        lines.append(f"    description: >")
        # Wrap long description at ~100 chars per line, indented under description.
        wrapped = _wrap_text(description, width=96, indent="      ")
        lines.append(wrapped)
        lines.append(f"    risk_tier: {risk_tier}")
        lines.append(f"    floors:")
        for f in floors:
            lines.append(f"      - {getattr(f, 'name', f)}")
        if modes:
            lines.append(f"    modes:")
            for m in modes:
                lines.append(f"      - {m}")
        lines.append("")

    return "\n".join(lines)


def _wrap_text(text: str, width: int, indent: str) -> str:
    """Naive word-wrap with indent prefix on continuation lines."""
    words = text.split()
    out: list[str] = []
    line = indent
    for w in words:
        if len(line) + len(w) + 1 > width and line != indent:
            out.append(line.rstrip())
            line = indent + w + " "
        else:
            line += w + " "
    if line.strip():
        out.append(line.rstrip())
    return "\n".join(out)


def main() -> int:
    sys.stdout.write(emit_tools_sot())
    return 0


if __name__ == "__main__":
    sys.exit(main())
