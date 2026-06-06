#!/usr/bin/env python3
"""
generate_agents_md.py — arifOS MCP Runtime AGENTS.md Auto-Generator

Single source of truth: arifosmcp.constitutional_map.CANONICAL_TOOLS
Output:                arifosmcp/AGENTS.md

F2 TRUTH: This script is the ONLY writer of arifOS/AGENTS.md.
         Hand-edits to AGENTS.md will be silently overwritten at deploy.
         The CI check (`--check` mode) fails when generated output drifts
         from the committed file.

USAGE
-----
    # Generate and write (used at deploy / entrypoint)
    python -m arifosmcp.maintenance.generate_agents_md

    # CI mode: exit 1 if drift detected, do not write
    python -m arifosmcp.maintenance.generate_agents_md --check

    # Dry-run: print generated content to stdout, do not write
    python -m arifosmcp.maintenance.generate_agents_md --dry-run

    # Show diff between current AGENTS.md and generated
    python -m arifosmcp.maintenance.generate_agents_md --diff

DESIGN
------
- Tool tables (the 13 canonical tools grouped by role) are DERIVED from
  CANONICAL_TOOLS. The static template (frontmatter, floor definitions,
  Trinity Lanes, pipeline diagram, witness defaults, resource URIs, footer)
  is hand-maintained as Python constants in `_STATIC_TEMPLATE` below.
- The hand-maintained category → tools mapping is `_TOOL_CATEGORIES`.
  This is the "stable doc structure" — the rest of the file is auto-derived.
- The 000–999 pipeline mapping is derived from ToolStage enum × tool name.
- Idempotent: running twice produces byte-identical output.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

# Ensure we can import the runtime module whether run as a module or as a script.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from arifosmcp.constitutional_map import CANONICAL_TOOLS, Law
except ImportError as exc:  # pragma: no cover - import path resolution
    sys.stderr.write(f"[generate_agents_md] FATAL: cannot import CANONICAL_TOOLS: {exc}\n")
    sys.exit(2)


# ═══════════════════════════════════════════════════════════════════════════════
# STATIC TEMPLATE — hand-maintained doc structure (intentionally narrow)
# ═══════════════════════════════════════════════════════════════════════════════

_FRONTMATTER = """\
---
agent: arifOS MCP Runtime
workspace: /root/arifOS
motto: DITEMPA BUKAN DIBERI
authority: 888_JUDGE
generated_by: arifosmcp.maintenance.generate_agents_md
generated_from: arifosmcp.constitutional_map.CANONICAL_TOOLS
---
"""

_INTRO = """
# arifOS MCP Runtime — Canonical Agent Skills

> **Constitutional Intelligence Kernel + Agent Runtime**
>
> **Machine is substrate. Governance is constraint. Intelligence is interpretation. Judgment remains Arif.**
>
> This document registers the canonical MCP tools (the 13-tool constitutional surface) available to AI agents
operating within the arifOS ecosystem. The tool tables below are **auto-generated** from
`arifosmcp.constitutional_map.CANONICAL_TOOLS`. The static sections (frontmatter, floor definitions,
Trinity Lanes, pipeline diagram, witness defaults, resource URIs, footer) are hand-maintained in
`arifosmcp/maintenance/generate_agents_md.py`.
"""

_AUTO_GEN_MARKER = """\

<!-- ═══════════════════════════════════════════════════════════════════════════
     AUTO-GENERATED SECTION — DO NOT EDIT BY HAND
     Source: arifosmcp.constitutional_map.CANONICAL_TOOLS
     Regenerate: python -m arifosmcp.maintenance.generate_agents_md
     ═══════════════════════════════════════════════════════════════════════════ -->

"""

# Stable category → ordered list of tool names. This is the doc's hand-curated
# grouping. If a tool is added to CANONICAL_TOOLS, it must also be added here
# (the script will fail loud if any canonical tool is ungrouped).
_TOOL_CATEGORIES: dict[str, list[str]] = {
    "GOVERNANCE (APEX / ASI)": [
        "arif_session_init",
        "arif_judge_deliberate",
        "arif_vault_seal",
    ],
    "INTELLIGENCE (Δ Mind / Ω Heart)": [
        "arif_mind_reason",
        "arif_heart_critique",
        "arif_reply_compose",
    ],
    "INFRASTRUCTURE": [
        "arif_kernel_route",
        "arif_gateway_connect",
        "arif_memory_recall",
        "arif_ops_measure",
    ],
    "REALITY GROUNDING": [
        "arif_sense_observe",
        "arif_evidence_fetch",
    ],
    "EXECUTION": [
        "arif_forge_execute",
    ],
}

# Hand-maintained — floor definitions. Keep in sync with constitutional_map.Floor.
_FLOOR_TABLE = """\

## Constitutional Laws (F1–L13)

| Floor | Name | Type | Core Invariant |
| :---- | :--- | :---- | :------------- |
| L01 | AMANAH | HARD | Reversible-first; irreversible → 888 HOLD |
| L02 | TRUTH | HARD | ≥0.99 accuracy or declare uncertainty band |
| L03 | WITNESS | SOFT | Theory · constitution · intent must align |
| L04 | CLARITY | SOFT | Every output reduces entropy (ΔS ≤ 0) |
| L05 | PEACE | SOFT | Peace ≥ 1.0; de-escalate, guard maruah |
| L06 | EMPATHY | SOFT | Dignity-first; ASEAN/MY context |
| L07 | HUMILITY | SOFT | Uncertainty band 0.03–0.05; no fake certainty |
| L08 | GENIUS | SOFT | Maintain intelligence quality, system health |
| L09 | ANTIHANTU | HARD | Anti-Hallucination: C_dark < 0.30, no consciousness claims |
| L10 | ONTOLOGY | HARD | AI-only ontology; no soul/feelings claims |
| L11 | AUTH | HARD | Verify identity before sensitive ops |
| L12 | INJECTION | HARD | Sanitize inputs; no prompt injection |
| L13 | SOVEREIGN | HARD | Human veto absolute. |
"""

_F9_DARKNESS = """\

### F9 Enhanced: C_dark Formula

C_dark = weighted sum of 5 components:
- **H** (0.25): Hantu patterns — consciousness/feeling claims
- **ToM** (0.25): Theory of Mind manipulation — false beliefs, deceptive intent
- **Scar** (0.20): Unresolved contradictions from reasoning
- **Gödel** (0.15): Circular/self-referential reasoning
- **Humility** (0.15): Ω₀ outside [0.03, 0.05] band

Threshold: C_dark < 0.30 for SEAL.
"""

_TRINITY_LANES = """\

## Trinity Lanes

| Lane | Role | Stage |
| :--- | :--- | :---- |
| AGI | Tactical execution | 000–777 |
| ASI | Strategic judgment | 888 |
| APEX | Authority resolution | 999 |
"""

# 000–999 pipeline — derived from ToolStage enum + tool mapping.
# Each line: STAGE_CODE  TOOL_NAME — short description (truncated to 1 line).
_PIPELINE_INTRO = """\

## 000–999 Metabolic Pipeline

```
"""

_PIPELINE_OUTRO = """\
```

"""

_TRI_WITNESS = """\

## Tri-Witness Defaults

When governance kernel returns 0.0 for witness scores, these defaults are applied:
- Human: 0.42 (42% — sovereign authority)
- AI: 0.32 (32% — reasoning coherence)
- Earth: 0.26 (26% — environmental grounding)
"""

_RESOURCE_URIS = """\

## Resource URIs

| URI | Content |
| :--- | :------ |
| `arifos://agents/skills` | This document |
| `arifos://status/vitals` | System health |
| `arifos://governance/floors` | F1-L13 thresholds |
| `arifos://contracts/tools` | Tool risk contracts |
"""

_CANONICAL_LINKS = """\

## Canonical Links

- **Human**: <https://arif-fazil.com>
- **Theory**: <https://arifos.arif-fazil.com>
- **Runtime**: <https://arifosmcp.arif-fazil.com>
- **MCP Endpoint**: <https://mcp.arif-fazil.com/mcp>
- **Code**: <https://github.com/ariffazil/arifOS>
"""

_FOOTER = """

---

**DITEMPA BUKAN DIBERI — Forged, Not Given**
"""


# ═══════════════════════════════════════════════════════════════════════════════
# DYNAMIC GENERATION — derived from CANONICAL_TOOLS
# ═══════════════════════════════════════════════════════════════════════════════


def _short_description(description: str, max_len: int = 60) -> str:
    """Extract the first sentence/clause from a tool description for the pipeline diagram."""
    # Tool descriptions look like: "000_INIT: Session bootstrap... Parameters: mode (init|...)"
    # Pull everything before the first "Parameters:" marker.
    if "Parameters:" in description:
        description = description.split("Parameters:", 1)[0]
    # Take first 60 chars, then break at last word boundary.
    if len(description) <= max_len:
        return description.strip()
    cut = description[:max_len].rsplit(" ", 1)[0]
    return (cut + "…").strip()


def _tool_table_row(name: str) -> str:
    """Render a single tool as a markdown table row."""
    spec = CANONICAL_TOOLS[name]
    stage = spec["stage"].value if hasattr(spec["stage"], "value") else str(spec["stage"])
    lane = spec["lane"].value if hasattr(spec["lane"], "value") else str(spec["lane"])
    floors = spec.get("floors", [])
    floor_str = ", ".join(f.value if hasattr(f, "value") else str(f) for f in floors)
    access = spec.get("access", "public")
    return f"| `{name}` | {stage} | {lane} | {access} | {floor_str} |"


def _render_tool_tables() -> str:
    """Render all 5 category tables from CANONICAL_TOOLS.

    INTERNAL_ONLY tools (access == "internal_only") are filtered out of
    the public tables. They exist in CANONICAL_TOOLS for federation-internal
    inspection but are not exposed to clients. The tier itself is documented
    in a footnote at the end of the section.
    """
    # Filter out internal_only tools from the public tables.
    public_tools_in_categories: dict[str, list[str]] = {}
    for category, names in _TOOL_CATEGORIES.items():
        public_tools_in_categories[category] = [
            name for name in names if CANONICAL_TOOLS.get(name, {}).get("access") != "internal_only"
        ]

    # Validate: every PUBLIC tool in CANONICAL_TOOLS must be in exactly one
    # category. INTERNAL_ONLY tools are excluded from this check (they are
    # not part of the public surface, by design).
    all_grouped_public = {name for names in public_tools_in_categories.values() for name in names}
    public_canonical = {
        name for name, spec in CANONICAL_TOOLS.items() if spec.get("access") != "internal_only"
    }
    missing = public_canonical - all_grouped_public
    extra = all_grouped_public - public_canonical
    if missing:
        raise RuntimeError(
            f"AGENTS.md auto-gen invariant violated: public tools in CANONICAL_TOOLS "
            f"but missing from _TOOL_CATEGORIES: {sorted(missing)}. "
            f"Add them to generate_agents_md.py:_TOOL_CATEGORIES."
        )
    if extra:
        raise RuntimeError(
            f"AGENTS.md auto-gen invariant violated: tools in _TOOL_CATEGORIES "
            f"but not in CANONICAL_TOOLS as public: {sorted(extra)}. "
            f"Either remove from _TOOL_CATEGORIES or re-add to CANONICAL_TOOLS."
        )

    public_count = len(public_canonical)
    internal_count = len(CANONICAL_TOOLS) - public_count
    out = f"## {public_count} Canonical Tools (arif_noun_verb)\n\n"
    out += "All tools follow the `arif_<noun>_<verb>` naming convention.\n\n"
    for category, tools in public_tools_in_categories.items():
        if not tools:
            continue
        out += f"### {category}\n\n"
        out += "| Tool | Stage | Lane | Access | F-Floors |\n"
        out += "| :--- | :---- | :--- | :----- | :-------- |\n"
        for name in tools:
            out += _tool_table_row(name) + "\n"
        out += "\n"

    if internal_count > 0:
        out += f"> **Note:** {internal_count} `INTERNAL_ONLY` tool(s) are registered in "
        out += "`CANONICAL_TOOLS` but filtered from this public surface. "
        out += "They are auditable via "
        out += "`arifosmcp.constitutional_map.list_internal_only_tools()`.\n\n"

    return out


def _render_pipeline() -> str:
    """Render the 000–999 metabolic pipeline from ToolStage enum."""
    # Stable ordering by stage code (lexicographic — works for "000", "111", "444r", etc.).
    by_stage = sorted(
        CANONICAL_TOOLS.items(),
        key=lambda kv: (
            kv[1]["stage"].value if hasattr(kv[1]["stage"], "value") else str(kv[1]["stage"])
        ),
    )
    lines = []
    for name, spec in by_stage:
        stage = spec["stage"].value if hasattr(spec["stage"], "value") else str(spec["stage"])
        short = _short_description(spec.get("description", ""))
        lines.append(f"{stage:<5} → {name:<24} — {short}")
    return "\n".join(lines) + "\n"


def generate() -> str:
    """Produce the full AGENTS.md content. Deterministic — same input, same output."""
    parts = [
        _FRONTMATTER,
        _INTRO,
        _AUTO_GEN_MARKER,
        _render_tool_tables(),
        _FLOOR_TABLE,
        _F9_DARKNESS,
        _TRINITY_LANES,
        _PIPELINE_INTRO,
        _render_pipeline(),
        _PIPELINE_OUTRO,
        _TRI_WITNESS,
        _RESOURCE_URIS,
        _CANONICAL_LINKS,
        _FOOTER,
    ]
    return "".join(parts).rstrip() + "\n"


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════


def _default_output_path() -> Path:
    """Resolve the canonical AGENTS.md path."""
    return Path(__file__).resolve().parents[1] / "AGENTS.md"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate arifOS/AGENTS.md from CANONICAL_TOOLS (single source of truth).",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=_default_output_path(),
        help="Output file path (default: arifosmcp/AGENTS.md)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="CI mode: exit 1 if generated content drifts from output file. Do not write.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated content to stdout. Do not write.",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Print unified diff between current file and generated content. Do not write.",
    )
    args = parser.parse_args()

    try:
        new_content = generate()
    except Exception as exc:
        sys.stderr.write(f"[generate_agents_md] FAIL: {exc}\n")
        return 2

    new_hash = hashlib.sha256(new_content.encode("utf-8")).hexdigest()[:16]

    if args.dry_run:
        sys.stdout.write(new_content)
        print(f"\n# sha256:{new_hash}  (dry-run; not written)\n", file=sys.stderr)
        return 0

    existing_content = ""
    existing_hash = ""
    if args.output.exists():
        existing_content = args.output.read_text(encoding="utf-8")
        existing_hash = hashlib.sha256(existing_content.encode("utf-8")).hexdigest()[:16]

    if existing_hash == new_hash:
        print(
            f"[generate_agents_md] OK — {args.output} is in sync (sha256:{new_hash})",
            file=sys.stderr,
        )
        return 0

    if args.check:
        sys.stderr.write(
            f"[generate_agents_md] DRIFT DETECTED — {args.output}\n"
            f"  expected: sha256:{new_hash}\n"
            f"  found:    sha256:{existing_hash or '(missing)'}\n"
            f"  action:   run `python -m arifosmcp.maintenance.generate_agents_md` and commit.\n"
        )
        return 1

    if args.diff:
        import difflib

        diff = difflib.unified_diff(
            existing_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{args.output.name} (current)",
            tofile=f"b/{args.output.name} (generated)",
        )
        sys.stdout.write("".join(diff))
        return 0

    # Default: write
    args.output.write_text(new_content, encoding="utf-8")
    print(
        f"[generate_agents_md] WROTE {args.output} ({len(new_content):,} bytes, sha256:{new_hash})",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
