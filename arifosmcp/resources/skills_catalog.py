"""
arifos://skills-catalog — Machine-Readable Skill Registry
════════════════════════════════════════════════════════

DITEMPA BUKAN DIBERI — Forged, Not Given.

Scans /root/.agents/skills/ and produces a machine-readable catalog
of all available agent skills. Each skill entry includes:
  - name: skill identifier
  - path: filesystem path to SKILL.md
  - organ: which federation organ owns this skill
  - trigger_phrases: when to load this skill
  - floors: constitutional floors relevant to this skill
  - completeness: COMPLETE | STUB | QUARANTINED | ARCHIVE

This resource is DYNAMIC — computed on each read from the live filesystem.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

SKILLS_ROOT = Path("/root/.agents/skills")

# Organ mapping heuristics (skills directory → organ)
ORGAN_MAP: dict[str, str] = {
    "arifos": "arifOS",
    "geox": "GEOX",
    "wealth": "WEALTH",
    "well": "WELL",
    "aaa": "AAA",
    "aforge": "A-FORGE",
    "federation": "FEDERATION",
    "github": "AAA",
    "cloudflare": "INFRA",
    "web-perf": "INFRA",
    "workers": "INFRA",
    "wrangler": "INFRA",
    "sandbox": "A-FORGE",
    "pydantic-ai": "A-FORGE",
    "agentic": "AAA",
    "auditor": "AAA",
    "vault999": "VAULT999",
    ".archive": "ARCHIVE",
    ".quarantine": "QUARANTINE",
}

# Floor relevance hints (skill name → relevant floors)
FLOOR_HINTS: dict[str, list[str]] = {
    "arifos": ["F1", "F2", "F13"],
    "geox": ["F1", "F2", "F7"],
    "wealth": ["F1", "F2", "F5", "F6"],
    "well": ["F2", "F5", "F6", "F9"],
    "federation": ["F1", "F2", "F4"],
    "github": ["F1", "F11"],
    "cloudflare": ["F1", "F11"],
    "auditor": ["F1", "F2", "F4", "F11"],
    "vault999": ["F1", "F2", "F11"],
}


def _scan_skill_file(skill_path: Path) -> dict[str, Any]:
    """Extract metadata from a SKILL.md file."""
    if not skill_path.exists():
        return {
            "skill_md_exists": False,
            " completeness": "STUB",
        }

    content = skill_path.read_text()
    lines = content.splitlines()

    # Extract description from first non-header line
    description = ""
    for line in lines[1:]:
        line = line.strip()
        if line and not line.startswith("#"):
            description = line[:200]
            break

    # Extract trigger phrases
    trigger_match = re.search(
        r"(?:trigger|use when|load when)[:\s]+([^\n]+)", content, re.IGNORECASE
    )
    trigger_phrases = []
    if trigger_match:
        trigger_phrases = [t.strip() for t in re.split(r"[,;•\n]", trigger_match.group(1)) if t.strip()]

    # Count lines (proxy for completeness)
    line_count = len(content.splitlines())
    if line_count < 10:
        completeness = "STUB"
    elif line_count < 50:
        completeness = "PARTIAL"
    else:
        completeness = "COMPLETE"

    # Check quarantine/archive
    if ".quarantine" in str(skill_path):
        completeness = "QUARANTINED"
    elif ".archive" in str(skill_path):
        completeness = "ARCHIVE"

    return {
        "skill_md_exists": True,
        "description": description,
        "trigger_phrases": trigger_phrases[:5],
        "line_count": line_count,
        "completeness": completeness,
    }


def _build_skills_catalog() -> dict[str, Any]:
    """Build the skills catalog from the live filesystem."""
    if not SKILLS_ROOT.exists():
        return {
            "error": f"Skills root not found: {SKILLS_ROOT}",
            "skills": [],
        }

    skills: list[dict[str, Any]] = []
    total = 0
    complete = 0
    stub = 0
    quarantined = 0
    archived = 0

    for skill_dir in sorted(SKILLS_ROOT.iterdir()):
        if not skill_dir.is_dir():
            continue

        skill_name = skill_dir.name
        skill_md = skill_dir / "SKILL.md"

        # Determine organ
        organ = "UNKNOWN"
        for key, val in ORGAN_MAP.items():
            if key in skill_name.lower():
                organ = val
                break

        # Determine relevant floors
        relevant_floors = []
        for key, floors in FLOOR_HINTS.items():
            if key in skill_name.lower():
                relevant_floors.extend(floors)
        relevant_floors = sorted(set(relevant_floors))

        meta = _scan_skill_file(skill_md)

        entry = {
            "name": skill_name,
            "path": str(skill_dir),
            "organ": organ,
            "skill_md_exists": meta.get("skill_md_exists", False),
            "description": meta.get("description", ""),
            "trigger_phrases": meta.get("trigger_phrases", []),
            "relevant_floors": relevant_floors,
            "completeness": meta.get("completeness", "UNKNOWN"),
            "line_count": meta.get("line_count", 0),
        }
        skills.append(entry)

        total += 1
        c = meta.get("completeness", "UNKNOWN")
        if c == "COMPLETE":
            complete += 1
        elif c == "STUB":
            stub += 1
        elif c == "QUARANTINED":
            quarantined += 1
        elif c == "ARCHIVE":
            archived += 1

    return {
        "resource": "arifos://skills-catalog",
        "version": "v2026.06.25",
        "skills_root": str(SKILLS_ROOT),
        "generated_at": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": {
            "total": total,
            "complete": complete,
            "stub": stub,
            "quarantined": quarantined,
            "archived": archived,
        },
        "skills": skills,
    }


CATALOG_TEXT = """\
---arifos_meta
resource_class: supplemental
authority_level: DYNAMIC
owner: ARIF_FAZIL
version: 2026.06.25
mutation_allowed: false
requires_actor_verified: false
requires_session: false
lease_required: false
blast_radius: LOW
evidence_level: MODEL_INFERENCE
staleness_policy: warn
truth_level: 6
---end_arifos_meta

arifOS Skills Catalog
═══════════════════

This resource returns a JSON catalog of all agent skills in /root/.agents/skills/.
For the raw JSON catalog (machine-readable), access: arifos://skills-catalog?format=json

SKILL COMPLETENESS GUIDE:
  COMPLETE   — SKILL.md exists with >50 lines, clear trigger/use-when clause
  PARTIAL    — SKILL.md exists but <50 lines or missing trigger clause
  STUB       — Directory exists but no SKILL.md file
  QUARANTINED — Skill under evaluation or known issues (do not load without review)
  ARCHIVE    — Deprecated skill, retained for reference only

SKILL → ORGAN MAPPING:
  arifos-*      → arifOS (Constitutional Kernel)
  geox-*        → GEOX (Earth Intelligence)
  wealth-*      → WEALTH (Capital Intelligence)
  well-*        → WELL (Human Readiness)
  aaa-*         → AAA (Control Plane)
  aforge-*      → A-FORGE (Execution Shell)
  federation-*  → FEDERATION (Cross-organ routing)
  github-*      → AAA (GitHub operations)
  cloudflare-*  → INFRA (Cloudflare platform)
  auditor-*     → AAA (Audit/validation)
  vault999-*    → VAULT999 (Immutable ledger)
  .archive-*    → ARCHIVE (Deprecated)
  .quarantine-* → QUARANTINE (Known issues, do not load)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""  # The JSON catalog is returned separately via the register function


def register_skills_catalog(mcp: FastMCP) -> list[str]:
    """Register arifos://skills-catalog — machine-readable skill registry."""

    @mcp.resource(
        "arifos://skills-catalog",
        description=(
            "Machine-readable catalog of all agent skills in /root/.agents/skills/. "
            "Returns JSON with name, path, organ, completeness, trigger_phrases, "
            "relevant constitutional floors, and line count per skill. "
            "Dynamic — computed from live filesystem on each read. "
            "Completeness: COMPLETE | PARTIAL | STUB | QUARANTINED | ARCHIVE."
        ),
    )
    def skills_catalog_resource() -> dict[str, Any]:
        """Return the live skills catalog as JSON."""
        return _build_skills_catalog()

    return ["arifos://skills-catalog"]


__all__ = ["register_skills_catalog"]
