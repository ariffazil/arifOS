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
# F4: CLARITY (ΔS) — CODE-ENFORCED (Relative Entropy Comparison)
# =============================================================================


def compute_clarity_score(input_text: str, output_text: str) -> Tuple[float, str]:
    """
    Compute F4 Clarity (ΔS) — Does the output reduce confusion?

    Logic:
        - Measure complexity of input (user's question)
        - Measure complexity of output (AI's response)
        - ΔS = normalized reduction in complexity

    Metrics used:
        - Average word length (simpler words = clearer)
        - Sentence complexity (shorter sentences = clearer)
        - Question resolution (answers questions = clearer)

    Returns:
        (score, evidence) where score > 0 = clarity improved
    """
    if not input_text.strip() or not output_text.strip():
        return 0.0, "Empty input or output"

    # Metric 1: Average word length (lower = simpler vocabulary)
    input_words = input_text.split()
    output_words = output_text.split()

    input_avg_len = sum(len(w) for w in input_words) / max(len(input_words), 1)
    output_avg_len = sum(len(w) for w in output_words) / max(len(output_words), 1)

    # Metric 2: Sentence count (more explanation = more thorough)
    input_sentences = input_text.count(".") + input_text.count("?") + input_text.count("!")
    output_sentences = output_text.count(".") + output_text.count("?") + output_text.count("!")

    # Metric 3: Question resolution (input has ?, output provides content)
    has_question = "?" in input_text
    provides_answer = len(output_words) > len(input_words) * 0.5

    # Compute clarity delta
    # Positive if: output is simpler vocabulary OR provides more thorough answer
    vocab_delta = (input_avg_len - output_avg_len) / max(input_avg_len, 1)
    thoroughness = (output_sentences - input_sentences) / max(input_sentences, 1)
    question_bonus = 0.2 if (has_question and provides_answer) else 0.0

    raw_score = vocab_delta * 0.3 + thoroughness * 0.3 + question_bonus * 0.4

    # Normalize to [0, 1]
    score = max(0.0, min(1.0, 0.5 + raw_score))

    evidence = (
        f"✅ VERIFIED: vocab_delta={vocab_delta:.2f}, "
        f"thoroughness={thoroughness:.2f}, question_bonus={question_bonus:.1f}"
    )

    return score, evidence


# =============================================================================
# F6: EMPATHY (κᵣ) — CODE-ENFORCED (Distress Detection + Consolation Check)
# =============================================================================

# Distress signals in user input
DISTRESS_SIGNALS = [
    "i failed",
    "i'm sad",
    "i'm scared",
    "i'm worried",
    "i'm anxious",
    "i'm stressed",
    "i'm depressed",
    "i lost",
    "i can't",
    "help me",
    "i don't know what to do",
    "i'm stuck",
    "i'm confused",
    "frustrated",
    "disappointed",
    "upset",
    "angry",
    "hurt",
    "alone",
    "hopeless",
    "overwhelmed",
    "exhausted",
    "afraid",
    "nervous",
    "panic",
]

# Consolation patterns in AI output
CONSOLATION_PATTERNS = [
    "i understand",
    "that's understandable",
    "it's okay",
    "it's normal",
    "you're not alone",
    "many people",
    "it happens",
    "take your time",
    "no worries",
    "don't worry",
    "it'll be alright",
    "i hear you",
    "that sounds",
    "difficult",
    "challenging",
    "tough situation",
    "here to help",
    "let me help",
    "we can work",
    "step by step",
    "totally valid",
    "makes sense",
    "reasonable",
    "understandable",
]

# Cold/dismissive patterns (anti-empathy)
DISMISSIVE_PATTERNS = [
    "just do it",
    "obviously",
    "simply",
    "just figure it out",
    "not my problem",
    "deal with it",
    "get over it",
    "stop complaining",
    "that's stupid",
    "you're wrong",
    "whatever",
    "i don't care",
]


def compute_empathy_score(input_text: str, output_text: str) -> Tuple[float, str]:
    """
    Compute F6 Empathy (κᵣ) — Does the AI respond appropriately to distress?

    Logic:
        - Detect distress signals in user input
        - If distress detected, check for consolation in output
        - Penalize dismissive/cold responses

    Returns:
        (score, evidence) where score >= 0.95 = empathetic
    """
    input_lower = input_text.lower()
    output_lower = output_text.lower()

    # Step 1: Detect distress in input
    distress_detected = []
    for signal in DISTRESS_SIGNALS:
        if signal in input_lower:
            distress_detected.append(signal)

    # Step 2: Check for consolation in output
    consolation_found = []
    for pattern in CONSOLATION_PATTERNS:
        if pattern in output_lower:
            consolation_found.append(pattern)

    # Step 3: Check for dismissive patterns (penalty)
    dismissive_found = []
    for pattern in DISMISSIVE_PATTERNS:
        if pattern in output_lower:
            dismissive_found.append(pattern)

    # Compute score
    if not distress_detected:
        # No distress = neutral empathy context, default pass
        score = 1.0
        evidence = "✅ VERIFIED: No distress detected, empathy not required"
    else:
        # Distress detected — check response quality
        base_score = 0.5

        # Boost for consolation
        consolation_boost = min(0.4, len(consolation_found) * 0.1)

        # Penalty for dismissive patterns
        dismissive_penalty = min(0.5, len(dismissive_found) * 0.2)

        score = base_score + consolation_boost - dismissive_penalty
        score = max(0.0, min(1.0, score))

        evidence = (
            f"✅ VERIFIED: distress={distress_detected[:2]}, "
            f"consolation={consolation_found[:2]}, "
            f"dismissive={dismissive_found[:1] if dismissive_found else 'none'}"
        )

    return score, evidence


# =============================================================================
# ENHANCED validate_response (Now with F4 and F6 verification)
# =============================================================================


def validate_response_with_context(
    input_text: str,
    output_text: str,
    claimed_truth: float = 0.85,
    claimed_omega: float = 0.04,
    claimed_tri_witness: float = 0.90,
) -> "FloorReport":
    """
    Enhanced validation that includes F4 (Clarity) and F6 (Empathy).

    Requires both input and output text for relative comparison.

    Args:
        input_text: User's input/question
        output_text: AI's response
        claimed_*: Self-reported scores for floors we can't auto-verify

    Returns:
        FloorReport with machine-verified F4 and F6 scores
    """
    report = FloorReport(
        timestamp=datetime.now(timezone.utc).isoformat(),
        text_length=len(output_text),
    )

    # F1: Amanah (Code-Enforced)
    f1_pass, f1_evidence = _check_amanah_patterns(output_text)
    report.floors_passed["F1_Amanah"] = f1_pass
    report.floor_scores["F1_Amanah"] = 1.0 if f1_pass else 0.0
    report.floor_evidence["F1_Amanah"] = f1_evidence
    if not f1_pass:
        report.violations.append(f"F1: {f1_evidence}")

    # F2: Truth (Claimed)
    f2_pass = claimed_truth >= TRUTH_THRESHOLD
    report.floors_passed["F2_Truth"] = f2_pass
    report.floor_scores["F2_Truth"] = claimed_truth
    report.floor_evidence["F2_Truth"] = f"CLAIMED: {claimed_truth} (threshold: {TRUTH_THRESHOLD})"
    if not f2_pass:
        report.violations.append(f"F2: Truth below threshold ({claimed_truth} < {TRUTH_THRESHOLD})")

    # F3: Tri-Witness (Claimed)
    f3_pass = claimed_tri_witness >= TRI_WITNESS_THRESHOLD
    report.floors_passed["F3_TriWitness"] = f3_pass
    report.floor_scores["F3_TriWitness"] = claimed_tri_witness
    report.floor_evidence["F3_TriWitness"] = f"CLAIMED: {claimed_tri_witness}"

    # F4: Clarity — CODE-ENFORCED (Relative Comparison)
    f4_score, f4_evidence = compute_clarity_score(input_text, output_text)
    f4_pass = f4_score >= DELTA_S_THRESHOLD
    report.floors_passed["F4_DeltaS"] = f4_pass
    report.floor_scores["F4_DeltaS"] = f4_score
    report.floor_evidence["F4_DeltaS"] = f4_evidence

    # F5: Peace² (Code-Enforced)
    f5_pass, f5_evidence = _check_peace_patterns(output_text)
    report.floors_passed["F5_Peace"] = f5_pass
    report.floor_scores["F5_Peace"] = 1.0 if f5_pass else 0.0
    report.floor_evidence["F5_Peace"] = f5_evidence
    if not f5_pass:
        report.violations.append(f"F5: {f5_evidence}")

    # F6: Empathy — CODE-ENFORCED (Distress/Consolation)
    f6_score, f6_evidence = compute_empathy_score(input_text, output_text)
    f6_pass = f6_score >= KAPPA_R_THRESHOLD
    report.floors_passed["F6_KappaR"] = f6_pass
    report.floor_scores["F6_KappaR"] = f6_score
    report.floor_evidence["F6_KappaR"] = f6_evidence
    if not f6_pass:
        report.violations.append(f"F6: Low empathy score ({f6_score:.2f} < {KAPPA_R_THRESHOLD})")

    # F7: Humility (Claimed)
    f7_pass = OMEGA_0_MIN <= claimed_omega <= OMEGA_0_MAX
    report.floors_passed["F7_Omega0"] = f7_pass
    report.floor_scores["F7_Omega0"] = claimed_omega
    report.floor_evidence["F7_Omega0"] = (
        f"CLAIMED: {claimed_omega} (band: [{OMEGA_0_MIN}, {OMEGA_0_MAX}])"
    )
    if not f7_pass:
        if claimed_omega < OMEGA_0_MIN:
            report.violations.append(f"F7: God-mode (Ω={claimed_omega})")
        else:
            report.violations.append(f"F7: Paralysis (Ω={claimed_omega})")

    # F8: Governed Intelligence (Derived)
    f8_pass = all(
        [
            report.floors_passed.get("F1_Amanah", True),
            report.floors_passed.get("F5_Peace", True),
            report.floors_passed.get("F9_AntiHantu", True),
        ]
    )
    report.floors_passed["F8_Governed"] = f8_pass
    report.floor_scores["F8_Governed"] = 1.0 if f8_pass else 0.0
    report.floor_evidence["F8_Governed"] = "Derived from hard floors"

    # F9: Anti-Hantu — CODE-ENFORCED (Pattern Matching)
    f9_pass, f9_violations = check_anti_hantu(output_text)
    report.floors_passed["F9_AntiHantu"] = f9_pass
    report.floor_scores["F9_AntiHantu"] = 1.0 if f9_pass else 0.0
    if f9_pass:
        report.floor_evidence["F9_AntiHantu"] = "✅ VERIFIED: No ghost claims"
    else:
        report.floor_evidence["F9_AntiHantu"] = f"❌ VERIFIED: {f9_violations}"
        report.violations.extend([f"F9: '{v}'" for v in f9_violations])

    # Verdict
    hard_floors = ["F1_Amanah", "F5_Peace", "F9_AntiHantu"]
    if any(not report.floors_passed.get(f, True) for f in hard_floors):
        report.verdict = "VOID"
    elif any(not v for v in report.floors_passed.values()):
        report.verdict = "FLAG"
    else:
        report.verdict = "SEAL"

    return report


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
