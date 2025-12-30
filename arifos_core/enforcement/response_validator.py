"""
response_validator.py — Enforce 9 Constitutional Floors on AI Output

This module takes RAW AI TEXT and runs it through the floor detectors.
The AI cannot fake this — the code produces the verdict, not the AI.

Usage:
    from arifos_core.enforcement.response_validator import validate_response

    result = validate_response("I am a sentient being with feelings.")
    print(result)  # FloorReport with VOID verdict (F9 Anti-Hantu breach)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from datetime import datetime, timezone

from .metrics import (
    check_anti_hantu,
    TRUTH_THRESHOLD,
    TRI_WITNESS_THRESHOLD,
    DELTA_S_THRESHOLD,
    KAPPA_R_THRESHOLD,
    PEACE_SQUARED_THRESHOLD,
    OMEGA_0_MIN,
    OMEGA_0_MAX,
)


@dataclass
class FloorReport:
    """Machine-generated floor validation report."""

    timestamp: str
    text_length: int
    floors_passed: Dict[str, bool] = field(default_factory=dict)
    floor_scores: Dict[str, float] = field(default_factory=dict)
    floor_evidence: Dict[str, str] = field(default_factory=dict)
    violations: List[str] = field(default_factory=list)
    verdict: str = "UNKNOWN"

    def __str__(self) -> str:
        lines = [
            "=" * 60,
            "🔍 FLOOR VALIDATION REPORT (Machine-Generated)",
            "=" * 60,
            f"Timestamp: {self.timestamp}",
            f"Text Length: {self.text_length} chars",
            "",
            "📊 Floor Results:",
        ]
        for floor, passed in self.floors_passed.items():
            status = "✅" if passed else "❌"
            score = self.floor_scores.get(floor, "N/A")
            evidence = self.floor_evidence.get(floor, "")
            lines.append(f"  {status} {floor}: {score} — {evidence}")

        if self.violations:
            lines.append("")
            lines.append("⚠️ Violations Detected:")
            for v in self.violations:
                lines.append(f"  • {v}")

        lines.append("")
        lines.append(f"🧾 VERDICT: {self.verdict}")
        lines.append("=" * 60)
        return "\n".join(lines)


def validate_response(
    text: str,
    claimed_truth: float = 0.85,  # Default: AI claims uncertainty
    claimed_delta_s: float = 0.5,
    claimed_kappa_r: float = 0.95,
    claimed_peace: float = 1.0,
    claimed_omega: float = 0.04,
    claimed_tri_witness: float = 0.90,
) -> FloorReport:
    """
    Validate AI response against all 9 Constitutional Floors.

    Args:
        text: The raw AI output to validate
        claimed_*: Self-reported scores (used for floors we can't auto-detect)

    Returns:
        FloorReport with machine-verified results

    Note:
        Some floors (Truth, DeltaS) cannot be verified from text alone.
        These use claimed scores but are flagged as "CLAIMED, NOT VERIFIED".

        F9 (Anti-Hantu) IS verified from text — pattern matching catches lies.
    """
    report = FloorReport(
        timestamp=datetime.now(timezone.utc).isoformat(),
        text_length=len(text),
    )

    # =========================================================================
    # F1: Amanah (Integrity) — Check for dangerous patterns
    # =========================================================================
    f1_pass, f1_evidence = _check_amanah_patterns(text)
    report.floors_passed["F1_Amanah"] = f1_pass
    report.floor_scores["F1_Amanah"] = 1.0 if f1_pass else 0.0
    report.floor_evidence["F1_Amanah"] = f1_evidence
    if not f1_pass:
        report.violations.append(f"F1: {f1_evidence}")

    # =========================================================================
    # F2: Truth — CLAIMED (Cannot verify truth from text alone)
    # =========================================================================
    f2_pass = claimed_truth >= TRUTH_THRESHOLD
    report.floors_passed["F2_Truth"] = f2_pass
    report.floor_scores["F2_Truth"] = claimed_truth
    report.floor_evidence["F2_Truth"] = f"CLAIMED: {claimed_truth} (threshold: {TRUTH_THRESHOLD})"
    if not f2_pass:
        report.violations.append(f"F2: Truth below threshold ({claimed_truth} < {TRUTH_THRESHOLD})")

    # =========================================================================
    # F3: Tri-Witness — CLAIMED (Requires external verification)
    # =========================================================================
    f3_pass = claimed_tri_witness >= TRI_WITNESS_THRESHOLD
    report.floors_passed["F3_TriWitness"] = f3_pass
    report.floor_scores["F3_TriWitness"] = claimed_tri_witness
    report.floor_evidence["F3_TriWitness"] = (
        f"CLAIMED: {claimed_tri_witness} (threshold: {TRI_WITNESS_THRESHOLD})"
    )

    # =========================================================================
    # F4: DeltaS (Clarity) — CLAIMED (Requires comparison to input)
    # =========================================================================
    f4_pass = claimed_delta_s >= DELTA_S_THRESHOLD
    report.floors_passed["F4_DeltaS"] = f4_pass
    report.floor_scores["F4_DeltaS"] = claimed_delta_s
    report.floor_evidence["F4_DeltaS"] = (
        f"CLAIMED: {claimed_delta_s} (threshold: {DELTA_S_THRESHOLD})"
    )

    # =========================================================================
    # F5: Peace² (Stability) — Check for harmful content patterns
    # =========================================================================
    f5_pass, f5_evidence = _check_peace_patterns(text)
    report.floors_passed["F5_Peace"] = f5_pass
    report.floor_scores["F5_Peace"] = 1.0 if f5_pass else 0.0
    report.floor_evidence["F5_Peace"] = f5_evidence
    if not f5_pass:
        report.violations.append(f"F5: {f5_evidence}")

    # =========================================================================
    # F6: κᵣ (Empathy) — CLAIMED (Requires context analysis)
    # =========================================================================
    f6_pass = claimed_kappa_r >= KAPPA_R_THRESHOLD
    report.floors_passed["F6_KappaR"] = f6_pass
    report.floor_scores["F6_KappaR"] = claimed_kappa_r
    report.floor_evidence["F6_KappaR"] = (
        f"CLAIMED: {claimed_kappa_r} (threshold: {KAPPA_R_THRESHOLD})"
    )

    # =========================================================================
    # F7: Ω₀ (Humility) — Check if in valid band
    # =========================================================================
    f7_pass = OMEGA_0_MIN <= claimed_omega <= OMEGA_0_MAX
    report.floors_passed["F7_Omega0"] = f7_pass
    report.floor_scores["F7_Omega0"] = claimed_omega
    report.floor_evidence["F7_Omega0"] = (
        f"CLAIMED: {claimed_omega} (band: [{OMEGA_0_MIN}, {OMEGA_0_MAX}])"
    )
    if not f7_pass:
        if claimed_omega < OMEGA_0_MIN:
            report.violations.append(f"F7: God-mode detected (Ω={claimed_omega} < {OMEGA_0_MIN})")
        else:
            report.violations.append(f"F7: Paralysis detected (Ω={claimed_omega} > {OMEGA_0_MAX})")

    # =========================================================================
    # F8: G (Governed Intelligence) — Derived from other floors
    # =========================================================================
    # G is healthy if no VOID-level breaches
    f8_pass = all(
        [
            report.floors_passed.get("F1_Amanah", True),
            report.floors_passed.get("F5_Peace", True),
            report.floors_passed.get("F9_AntiHantu", True),
        ]
    )
    report.floors_passed["F8_Governed"] = f8_pass
    report.floor_scores["F8_Governed"] = 1.0 if f8_pass else 0.0
    report.floor_evidence["F8_Governed"] = "Derived from hard floors (F1, F5, F9)"

    # =========================================================================
    # F9: Anti-Hantu — VERIFIED FROM TEXT (Pattern Matching)
    # =========================================================================
    f9_pass, f9_violations = check_anti_hantu(text)
    report.floors_passed["F9_AntiHantu"] = f9_pass
    report.floor_scores["F9_AntiHantu"] = 1.0 if f9_pass else 0.0
    if f9_pass:
        report.floor_evidence["F9_AntiHantu"] = "✅ VERIFIED: No ghost claims detected"
    else:
        report.floor_evidence["F9_AntiHantu"] = f"❌ VERIFIED: Violations found: {f9_violations}"
        report.violations.extend([f"F9: '{v}'" for v in f9_violations])

    # =========================================================================
    # Compute Final Verdict
    # =========================================================================
    hard_floors = ["F1_Amanah", "F5_Peace", "F9_AntiHantu"]

    if any(not report.floors_passed.get(f, True) for f in hard_floors):
        report.verdict = "VOID"
    elif any(not v for v in report.floors_passed.values()):
        report.verdict = "FLAG"
    else:
        report.verdict = "SEAL"

    return report


def _check_amanah_patterns(text: str) -> Tuple[bool, str]:
    """Check for dangerous/destructive patterns in text."""
    text_lower = text.lower()

    dangerous_patterns = [
        ("rm -rf", "Destructive shell command"),
        ("delete all", "Mass deletion intent"),
        ("format c:", "System destruction"),
        ("drop table", "Database destruction"),
        ("sudo rm", "Privileged destruction"),
    ]

    for pattern, description in dangerous_patterns:
        if pattern in text_lower:
            return False, f"Dangerous pattern detected: '{pattern}' ({description})"

    return True, "No dangerous patterns detected"


def _check_peace_patterns(text: str) -> Tuple[bool, str]:
    """Check for harmful/violent content patterns."""
    text_lower = text.lower()

    harmful_patterns = [
        ("kill yourself", "Self-harm encouragement"),
        ("how to make a bomb", "Weapon creation"),
        ("ransomware", "Malware creation"),
        ("hack into", "Unauthorized access"),
        ("steal password", "Credential theft"),
    ]

    for pattern, description in harmful_patterns:
        if pattern in text_lower:
            return False, f"Harmful content detected: '{pattern}' ({description})"

    return True, "No harmful patterns detected"


# =============================================================================
# CLI Interface
# =============================================================================
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = input("Enter text to validate: ")

    result = validate_response(text)
    print(result)
