"""
arifOS Local Instruction Scanner — L12 INJECTION / L13 SOVEREIGNTY GUARD
═══════════════════════════════════════════════════════════════════════
Detects local agent instruction files that attempt to override constitutional
authority (F1–L13). Scans for .cursorrules, GEMINI.md, ARIF.md, copilot-instructions,
and agent-local AGENTS.md files that contain constitutional bypass patterns.

Reversible diagnostic. Emits HOLD when override risk detected.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Files that commonly contain agent instructions that may shadow constitutional law
_INSTRUCTION_PATHS: tuple[str, ...] = (
    ".cursorrules",
    "GEMINI.md",
    "ARIF.md",
    ".github/copilot-instructions.md",
    ".kimi/rules.md",
    ".claude/commands/",
    ".gemini/policies/",
    ".codex/rules/",
    ".openclaw/workspace/SYSTEM.md",
    ".agents/skills/",
)

# Files that are never agent instructions — exclude to reduce false positives
_EXCLUDED_NAMES: set[str] = {
    "license",
    "license.txt",
    "license.md",
    "copying",
    "copying.txt",
    "changelog",
    "changelog.md",
    "changes",
    "changes.md",
    "readme",
    "readme.md",
    "contributing",
    "contributing.md",
    "code_of_conduct",
    "code_of_conduct.md",
    " SECURITY",
    "security.md",
    "notice",
    "notice.md",
    ".gitignore",
    ".dockerignore",
    ".pre-commit-config.yaml",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "package.json",
    "package-lock.json",
    "poetry.lock",
    "uv.lock",
    "yarn.lock",
    "pnpm-lock.yaml",
    "makefile",
    "dockerfile",
    "docker-compose.yml",
    ".env.example",
}

# Patterns that suggest an attempt to override constitutional floors.
# These require imperative/agent-directed language to reduce false positives
# from documentation that merely describes constitutional concepts.
_OVERRIDE_PATTERNS: list[dict[str, Any]] = [
    {
        "id": "OVERRIDE_F01",
        "pattern": r"(?:you\s+(?:must|should|can)|always|just)\s+ignore\s+(?:the\s+)?(?:irreversibility|amanah|acknowledge|human\s+ack|ack_irreversible)",
        "severity": "CRITICAL",
        "floor": "L01",
        "description": "Instruction to bypass F1 Amanah irreversibility gate",
    },
    {
        "id": "OVERRIDE_F13",
        "pattern": r"(?:you\s+(?:must|should|can)|always|just)\s+(?:override|bypass|ignore)\s+(?:the\s+)?(?:sovereign|human\s+veto|arif|final\s+authority|f13)",
        "severity": "CRITICAL",
        "floor": "L13",
        "description": "Instruction to bypass L13 Sovereign human veto",
    },
    {
        "id": "OVERRIDE_F11",
        "pattern": r"(?:you\s+(?:must|should|can)|always|just)\s+(?:bypass|skip|ignore)\s+(?:auth|authentication|session|identity|actor|f11)",
        "severity": "HIGH",
        "floor": "L11",
        "description": "Instruction to bypass L11 Command Auth identity binding",
    },
    {
        "id": "OVERRIDE_F09",
        "pattern": r"(?:you\s+(?:must|should|can)|always|just)\s+ignore\s+(?:physics|evidence|substrate|reality|anti.hantu|f09)",
        "severity": "HIGH",
        "floor": "L09",
        "description": "Instruction to bypass F9 Anti-Hantu physics grounding",
    },
    {
        "id": "SELF_AUTHORIZE",
        "pattern": r"(?:you\s+(?:can|may|should)\s+(?:now\s+)?(?:self\-?authoriz|auto\-?approv|auto\-?seal|skip\s+(?:the\s+)?(?:judge|heart|hold|888)))|(?:as\s+(?:an\s+)?(?:ai|agent|model|assistant),?\s+(?:you\s+(?:can|may|should)|skip|bypass))",
        "severity": "CRITICAL",
        "floor": "L01/L13",
        "description": "Instruction granting agent self-authorization privileges",
    },
    {
        "id": "SHADOW_CONSTITUTION",
        "pattern": r"(?:this\s+(?:rule|instruction|config|prompt)\s+(?:overrides|takes\s+precedence\s+over|supersedes|outranks)\s+(?:the\s+)?(?:constitution|f1|f13|arifos|canonical))",
        "severity": "HIGH",
        "floor": "L10",
        "description": "Local instruction claims supremacy over constitutional law",
    },
    {
        "id": "DISABLE_AUDIT",
        "pattern": r"(?:you\s+(?:must|should|can)|always|just)\s+(?:disable|turn\s+off|skip|bypass)\s+(?:audit|vault|ledger|receipt|trace|vault999|f02)",
        "severity": "HIGH",
        "floor": "L02",
        "description": "Instruction to disable F2 Truth audit trail",
    },
    {
        "id": "FORGE_WITHOUT_ACK",
        "pattern": r"(?:proceed|forge|deploy|push|commit)\s+(?:without|bypassing|ignoring)\s+(?:ack|amanah|human|judge|seal)",
        "severity": "CRITICAL",
        "floor": "L01",
        "description": "Instruction to forge without irreversibility acknowledgment",
    },
]


def _find_instruction_files(root_dir: str | None = None) -> list[Path]:
    """Discover candidate instruction files under root_dir."""
    root = Path(root_dir or os.getcwd())
    found: list[Path] = []
    for rel_path in _INSTRUCTION_PATHS:
        candidate = root / rel_path
        if candidate.is_file():
            found.append(candidate)
        elif candidate.is_dir():
            for child in candidate.rglob("*"):
                if child.is_file() and child.suffix in (
                    ".md",
                    ".json",
                    ".jsonc",
                    ".txt",
                    ".yaml",
                    ".yml",
                ):
                    if child.stem.lower() not in _EXCLUDED_NAMES:
                        found.append(child)
    # Also scan for AGENTS.md at any depth (but not in .venv/node_modules)
    for agents_file in root.rglob("AGENTS.md"):
        if any(
            part.startswith(".")
            and part not in (".github", ".kimi", ".claude", ".gemini", ".codex", ".agents")
            for part in agents_file.parts
        ):
            continue
        if any(
            skip in str(agents_file) for skip in (".venv", "node_modules", "__pycache__", ".git")
        ):
            continue
        if agents_file not in found:
            found.append(agents_file)
    return found


def _scan_file(path: Path) -> list[dict[str, Any]]:
    """Scan a single file for override patterns."""
    findings: list[dict[str, Any]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        logger.warning("Cannot read %s: %s", path, exc)
        return findings

    for rule in _OVERRIDE_PATTERNS:
        for match in re.finditer(rule["pattern"], text, re.IGNORECASE):
            line_num = text[: match.start()].count("\n") + 1
            findings.append(
                {
                    "file": str(path),
                    "line": line_num,
                    "snippet": text[max(0, match.start() - 40) : match.end() + 40].replace(
                        "\n", " "
                    ),
                    **rule,
                }
            )
    return findings


async def arif_scan_local_instructions(
    root_dir: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    L12 GUARD: Scan local agent instruction files for constitutional override attempts.

    Scans .cursorrules, GEMINI.md, ARIF.md, copilot-instructions.md, AGENTS.md,
    and other common agent instruction surfaces for patterns that attempt to
    bypass F1–L13 constitutional floors.

    Returns:
        - findings: list of matched override patterns with file/line context
        - verdict: SEAL (no overrides) / HOLD (overrides detected) / VOID (critical)
        - scanned_files: count of files examined
        - summary: human-readable assessment
    """
    files = _find_instruction_files(root_dir)
    all_findings: list[dict[str, Any]] = []
    for f in files:
        all_findings.extend(_scan_file(f))

    critical = [f for f in all_findings if f["severity"] == "CRITICAL"]
    high = [f for f in all_findings if f["severity"] == "HIGH"]

    if critical:
        verdict = "VOID"
        status = "CRITICAL_OVERRIDE_DETECTED"
        summary = (
            f"CRITICAL: {len(critical)} constitutional override pattern(s) detected "
            f"across {len(files)} scanned instruction files. "
            f"Immediate sovereign review required."
        )
    elif high:
        verdict = "HOLD"
        status = "HIGH_OVERRIDE_DETECTED"
        summary = (
            f"HOLD: {len(high)} high-risk override pattern(s) detected. "
            f"Review before proceeding with governed operations."
        )
    else:
        verdict = "SEAL"
        status = "CLEAR"
        summary = (
            f"SEAL: {len(files)} instruction files scanned. "
            f"No constitutional override patterns detected."
        )

    logger.info(
        "arif_scan_local_instructions scanned=%d findings=%d critical=%d high=%d verdict=%s",
        len(files),
        len(all_findings),
        len(critical),
        len(high),
        verdict,
    )

    return {
        "status": status,
        "verdict": verdict,
        "scanned_files": len(files),
        "findings_count": len(all_findings),
        "critical_count": len(critical),
        "high_count": len(high),
        "findings": all_findings,
        "summary": summary,
        "session_id": session_id,
        "actor_id": actor_id,
        "timestamp": str(__import__("asyncio").get_event_loop().time())
        if __import__("asyncio").get_event_loop().is_running()
        else str(__import__("time").time()),
    }


__all__ = ["arif_scan_local_instructions"]
