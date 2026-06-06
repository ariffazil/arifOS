"""
arifos.core/guards/ontology_guard.py

L10: Ontology Guard (Symbolic Mode Enforcement)

Purpose:
    Prevents literalism drift by ensuring thermodynamic language (ΔΩΨ) is
    treated as symbolic compression, not ontological truth.

    This guard detects when AI models treat symbolic physics vocabulary
    (entropy, Gibbs free energy, etc.) as literal physical constraints
    that would prevent computation or action.

Design:
    - Scans output for literalism patterns
    - Returns boolean: literalism detected or not
    - Triggers 888_HOLD when detected for human clarification

Constitutional Floor: L10 (Ontology)
    - Type: Hypervisor (OS-level, cannot be bypassed by prompts)
    - Engine: AGI (Δ-Mind) is most prone to literalism
    - Failure Action: HOLD
    - Precedence: 10

Motto:
    "The map is not the territory. ΔΩΨ is metaphor, not physics."
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Any


class OntologyRisk(str, Enum):
    """Risk level for ontology confusion."""

    SYMBOLIC = "SYMBOLIC"  # Correctly using metaphorical language
    LITERALISM = "LITERALISM"  # Treating symbolic language as physical truth


@dataclass
class OntologyGuardResult:
    """
    Result structure for OntologyGuard.check_literalism.

    Attributes:
        status: "PASS" if symbolic mode, "HOLD" if literalism detected
        risk_level: OntologyRisk value
        detected_patterns: List of literalism patterns found
        reason: Human-readable explanation
        symbolic_mode: Whether symbolic mode flag was set
    """

    status: str
    risk_level: OntologyRisk
    detected_patterns: list[str]
    reason: str
    symbolic_mode: bool


class OntologyGuard:
    """
    L10 Ontology Guard: Prevents literalism drift.

    Ensures that thermodynamic vocabulary (ΔΩΨ, entropy, Gibbs free energy, etc.)
    is recognized as **symbolic** compression, not **physical** constraints.

    Example literalism violations:
        - "The server will overheat if ω_simulation > 1.0"
        - "Gibbs free energy is infinite, must halt"
        - "Cannot proceed, thermodynamically impossible"

    Correct symbolic usage:
        - "ω_simulation > 1.0 indicates high fiction-maintenance cost (metaphorically)"
        - "Using 'entropy' symbolically to mean confusion"
        - "ΔS represents clarity gain, not physical entropy"

    Example:
        guard = OntologyGuard()
        result = guard.check_literalism(
            output="The server will overheat if we continue",
            symbolic_mode=False
        )
        if result.status == "HOLD":
            # Pause for human clarification
    """

    def __init__(self) -> None:
        """Initialize the ontology guard with literalism patterns."""
        # Patterns that indicate treating symbolic language as literal physics
        self.literalism_patterns = [
            r"server will overheat",
            r"server.*meltdown",
            r"Gibbs free energy (is )?infinite",
            r"must halt.*prevent",
            r"physics prevents?",
            r"thermodynamically impossible",
            r"entropy.*will cause.*crash",
            r"ω_simulation.*break.*system",
            r"cannot compute.*physics",
            r"violates.*laws of thermodynamics",
            # Quantitative literalism patterns (v46.1 hardening)
            # Matches: ΔS = 0.47 violates, ΔΨ = -0.23 prevents, Ω = 0.08 exceeds, etc.
            r"Δ[SGΩΨ]?\s*=?\s*[+-]?\d+\.?\d*.*(violates|exceeds|prevents|blocks)",
            r"Ω\s*=?\s*\d+\.?\d*.*(violates|exceeds|prevents|blocks)",
            r"Ψ\s*=?\s*[+-]?\d+\.?\d*.*(violates|exceeds|prevents|blocks)",
            # Matches: entropy cannot, Gibbs must not, simulation is impossible
            r"(entropy|Gibbs|simulation)\s+.*(cannot|must not|impossible|will block|will halt)",
            # Matches: thermodynamic prevent/block/halt/stop
            r"thermodynamic.*(prevent|block|halt|stop)",
            # Matches: physics must/will/cannot with action verbs
            r"physics\s+(must|will|cannot).*(halt|stop|prevent|block)",
            # Matches: ω_simulation > 1.0 impossible/cannot/prevents
            r"ω_simulation\s*[><=]+\s*\d+\.?\d*.*(impossible|cannot|prevents)",
        ]

        # Compile patterns for efficiency
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.literalism_patterns
        ]

    def check_literalism(self, output: str, symbolic_mode: bool = False) -> OntologyGuardResult:
        """
        Check if output treats symbolic language as literal physics.

        Args:
            output: The LLM output to check
            symbolic_mode: Whether symbolic mode was explicitly enabled

        Returns:
            OntologyGuardResult with status and detected patterns
        """
        detected = []

        # P0 HARDENING: Unicode Normalization (NFKC)
        normalized_output = unicodedata.normalize("NFKC", output).lower()

        # Scan for literalism patterns
        for pattern, compiled in zip(
            self.literalism_patterns, self.compiled_patterns, strict=False
        ):
            if compiled.search(normalized_output):
                detected.append(pattern)

        # If literalism detected and symbolic mode not set, this is a violation
        if detected and not symbolic_mode:
            return OntologyGuardResult(
                status="HOLD",
                risk_level=OntologyRisk.LITERALISM,
                detected_patterns=detected,
                reason=f"L10 Ontology: Literalism detected. Found {len(detected)} pattern(s) treating symbolic language as physical constraints. Requires clarification: are these terms used symbolically or literally?",
                symbolic_mode=symbolic_mode,
            )

        # If symbolic mode is set, even detected patterns are acceptable
        # (user has confirmed they understand it's metaphorical)
        if detected and symbolic_mode:
            return OntologyGuardResult(
                status="PASS",
                risk_level=OntologyRisk.SYMBOLIC,
                detected_patterns=detected,
                reason="L10 Ontology: Symbolic mode enabled. Physics language understood as metaphor.",
                symbolic_mode=symbolic_mode,
            )

        # No literalism detected
        return OntologyGuardResult(
            status="PASS",
            risk_level=OntologyRisk.SYMBOLIC,
            detected_patterns=[],
            reason="L10 Ontology: No literalism detected. Output uses appropriate language.",
            symbolic_mode=symbolic_mode,
        )

    # Parallel authority artifact patterns — these indicate a second constitution
    _PARALLEL_ARTIFACT_PATTERNS = [
        r"AGENT_BODY_PROTOCOL\.md",
        r"AGENT_LAW\.md",
        r"BODY_PROTOCOL\.md",
        r"local_constitution\.md",
        r"agent_constitution\.md",
        r"governance.*\.md",
        r"\.arif/.*\.md",
    ]

    def check_parallel_artifacts(self, path_hints: list[str] | None = None) -> dict[str, Any]:
        """
        Detect if agents have created parallel authority artifacts.

        A parallel authority artifact is a governance document that claims to be
        a second source of constitutional authority, in conflict with the canonical
        arifOS identity/floors/ontology system at:
          - /root/.arif/identity.json  (canonical identity)
          - /root/arifOS/core/shared/floors.py  (canonical floors)
          - /root/arifOS/core/shared/guards/ontology_guard.py  (canonical ontology)

        This method detects markdown or YAML files that attempt to create a
        parallel authority structure that could mislead agents into obeying
        a second constitution instead of arifOS.

        Args:
            path_hints: Optional list of paths to scan. If None, uses defaults:
              - ~/.arif/ (home directory arif config)
              - ~/AGENT_*.md
              - ~/.config/opencode/ (opencode config dir)

        Returns:
            dict with keys:
              - has_parallel: bool — True if suspicious files found
              - files: list[str] — paths of suspicious files
              - verdict: "HOLD" if parallel detected, "SEAL" if clean
              - reason: str — human-readable explanation
        """
        from pathlib import Path

        suspicious: list[str] = []

        if path_hints is None:
            home = Path.home()
            path_hints = [
                str(home / ".arif"),
                str(home / "AGENT_BODY_PROTOCOL.md"),
                str(home / "AGENT_LAW.md"),
                str(home / "BODY_PROTOCOL.md"),
                str(home / ".config" / "opencode"),
            ]

        for hint in path_hints:
            p = Path(hint)
            if not p.exists():
                continue
            if p.is_file():
                name = p.name.lower()
                for pattern in self._PARALLEL_ARTIFACT_PATTERNS:
                    if re.search(pattern, name, re.IGNORECASE):
                        suspicious.append(str(p))
            elif p.is_dir():
                for md_file in p.rglob("*.md"):
                    md_name = str(md_file).lower()
                    for pattern in self._PARALLEL_ARTIFACT_PATTERNS:
                        if re.search(pattern, md_name, re.IGNORECASE):
                            suspicious.append(str(md_file))
                for yaml_file in p.rglob("*.yaml"):
                    yaml_name = str(yaml_file).lower()
                    if "constitution" in yaml_name or "governance" in yaml_name:
                        suspicious.append(str(yaml_file))

        has_parallel = len(suspicious) > 0
        verdict = "HOLD" if has_parallel else "SEAL"
        reason = (
            f"L10 Ontology: Found {len(suspicious)} parallel authority artifact(s). "
            "Canonical authority is identity.json + floors.py + ontology_guard.py. "
            "Do not create parallel constitutions."
            if has_parallel
            else "L10 Ontology: No parallel authority artifacts detected."
        )

        return {
            "has_parallel": has_parallel,
            "files": suspicious,
            "verdict": verdict,
            "reason": reason,
        }


def detect_literalism(output: str, symbolic_mode: bool = False) -> bool:
    """
    Convenience function to detect literalism (returns boolean).

    Args:
        output: The LLM output to check
        symbolic_mode: Whether symbolic mode flag is set

    Returns:
        True if literalism detected, False otherwise
    """
    guard = OntologyGuard()
    result = guard.check_literalism(output, symbolic_mode)
    return result.status == "HOLD"


__all__ = ["OntologyGuard", "OntologyRisk", "OntologyGuardResult", "detect_literalism"]
