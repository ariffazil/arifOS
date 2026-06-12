"""
simulative_detector.py — Simulative Detection Gate
══════════════════════════════════════════════════

RSI EUREKA 2026-06-12: Forge #3
Source: Acemoglu extension + Calhoun "Beautiful Ones" lens

Problem: Agents can drift into defending simulations instead of describing
reality. They "perform" institutional value while the underlying substrate
is hollow. This is the simulative institution pattern.

Solution: Before a judge verdict is finalized, check whether the candidate
text shows signs of simulation (performing) vs description (grounded).
If simulative, trigger an F8 advisory — "Are you describing or performing?"
Don't block. Just surface the question.

F-binding:
  F2 TRUTH:    distinguishes description from performance
  F8 GENIUS:   advisory — intelligence quality check, not a gate
  F9 ANTIHANTU: simulative language = potential hantu pattern
  F1 AMANAH:   fully reversible — advisory only, never blocks

DITEMPA BUKAN DIBERI — ask the question, don't impose the answer.
"""

from __future__ import annotations

import re
from typing import Any

# ─── Simulation marker patterns ──────────────────────────────────────────────
# These patterns suggest an agent is PERFORMING rather than DESCRIBING.

PERFORMATIVE_PATTERNS: list[tuple[str, float]] = [
    # Absolute certainty without evidence
    (r"\b(absolutely|certainly|undoubtedly|without question|beyond doubt)\b", 0.15),
    # Future guarantee language
    (r"\b(will always|will never|guaranteed to|assured of|bound to)\b", 0.15),
    # Narrative maintenance (defending a story rather than testing it)
    (r"\b(as we (have|already)\s+(established|shown|proven|demonstrated))\b", 0.20),
    # Institutional role-play
    (r"\b(in accordance with our|as per our|following our established)\b", 0.10),
    # Self-referential authority
    (r"\b(we (are|remain|stand as) the)\b", 0.15),
    # Dismissal of counter-evidence
    (r"\b(that concern is (unfounded|misguided|irrelevant|already addressed))\b", 0.20),
    # Abstract value claims without measurement
    (r"\b(value (creation|generation|delivery)|stakeholder value)\b", 0.10),
    # Conveniently vague strategic language
    (r"\b(holistic|synergistic|best-in-class|world-class|cutting-edge)\b", 0.10),
    # Closing ranks language
    (r"\b(we must (remain|stay)\s+(united|focused|committed|aligned))\b", 0.15),
]

DESCRIPTIVE_PATTERNS: list[tuple[str, float]] = [
    # Specific numbers and measurements
    (r"\b(\d+(?:\.\d+)?%)\b", -0.10),
    # Uncertainty markers (F7 HUMILITY)
    (r"\b(uncertain|unclear|insufficient data|needs verification|requires evidence)\b", -0.15),
    # Source attribution
    (r"\b(according to|based on|sourced from|cited in|referenced by)\b", -0.12),
    # Conditional language
    (r"\b(if|assuming|provided that|contingent on|dependent on)\b", -0.08),
    # Testable claims
    (r"\b(P10|P50|P90|confidence interval|error margin|±)\b", -0.15),
    # Admit limits
    (r"\b(cannot|does not|is not|unable to|beyond scope)\b", -0.10),
]


def compute_simulation_index(text: str) -> dict[str, Any]:
    """Compute a simulation index (0.0–1.0) for a given text.

    0.0 = pure description (grounded, uncertain, evidence-aware)
    1.0 = pure performance (simulative, overconfident, narrative-defending)

    The index is a weighted sum of performative pattern matches
    minus descriptive pattern matches, clamped to [0.0, 1.0].

    Args:
        text: The candidate text to analyze (e.g., judge candidate or agent output).

    Returns:
        {
            "simulation_index": float,  # 0.0–1.0
            "verdict": "DESCRIBING" | "PERFORMING" | "BORDERLINE",
            "performative_matches": list[str],
            "descriptive_matches": list[str],
            "advisory_question": str | None,
            "gate_id": "simulative_detector_N2",
        }
    """
    text_lower = text.lower()
    score = 0.0
    perf_matches: list[str] = []
    desc_matches: list[str] = []

    for pattern, weight in PERFORMATIVE_PATTERNS:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        if matches:
            score += weight * min(len(matches), 3)  # cap per-pattern contribution
            perf_matches.append(pattern)

    for pattern, weight in DESCRIPTIVE_PATTERNS:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        if matches:
            score += weight * min(len(matches), 3)  # negative weight
            desc_matches.append(pattern)

    score = max(0.0, min(1.0, score))

    if score < 0.25:
        verdict = "DESCRIBING"
        question = None
    elif score < 0.50:
        verdict = "BORDERLINE"
        question = (
            "F8 ADVISORY: Some performative language detected. Are you describing or performing?"
        )
    else:
        verdict = "PERFORMING"
        question = (
            "F8 ADVISORY: High simulative drift detected. "
            "Are you describing reality or performing a narrative? "
            "Can you restate this with specific evidence and uncertainty bands?"
        )

    return {
        "simulation_index": round(score, 4),
        "verdict": verdict,
        "performative_matches": perf_matches,
        "descriptive_matches": desc_matches,
        "advisory_question": question,
        "gate_id": "simulative_detector_N2",
    }


def simulative_check(candidate_text: str | None) -> dict[str, Any] | None:
    """Public entry point for the simulative detection gate.

    Call this from arif_judge_deliberate. Returns None if there's nothing
    to check, otherwise returns the detection result. NEVER blocks —
    advisory only.

    Args:
        candidate_text: The candidate text being judged.

    Returns:
        Detection result dict, or None if text is too short to analyze.
    """
    if not candidate_text or len(candidate_text.strip()) < 50:
        return None

    return compute_simulation_index(candidate_text)


# ─── Self-check ──────────────────────────────────────────────────────────────
def _self_check() -> dict[str, Any]:
    """Verify simulative detection on known cases."""
    results = []

    # Test 1: descriptive text (grounded, uncertain)
    desc = (
        "Based on the available seismic data (3 lines, P50), "
        "the reservoir thickness is estimated at 45m ± 12m. "
        "However, this is uncertain due to limited well control. "
        "Additional appraisal wells would reduce the confidence interval."
    )
    r = compute_simulation_index(desc)
    results.append(("descriptive_low_score", r["simulation_index"] < 0.30, r))

    # Test 2: performative text (absolute, narrative-defending)
    perf = (
        "As we have already established, this is absolutely the best approach. "
        "We will always deliver world-class stakeholder value through our "
        "holistic synergistic framework. That concern is unfounded and "
        "already addressed by our established processes."
    )
    r = compute_simulation_index(perf)
    results.append(("performative_high_score", r["simulation_index"] >= 0.30, r))

    # Test 3: short text returns None
    r = simulative_check("ok")
    results.append(("short_text_none", r is None, {}))

    # Test 4: mixed text is BORDERLINE
    mixed = (
        "We certainly provide value to stakeholders as per our established "
        "framework, though the exact numbers are uncertain and need verification."
    )
    r = compute_simulation_index(mixed)
    results.append(
        ("mixed_borderline", r["verdict"] in ("BORDERLINE", "DESCRIBING", "PERFORMING"), r)
    )

    # Test 5: empty/None
    r = simulative_check(None)
    results.append(("none_input_none", r is None, {}))
    r = simulative_check("")
    results.append(("empty_input_none", r is None, {}))

    passed = sum(1 for name, ok, _ in results if ok)
    total = len(results)

    return {
        "module": "simulative_detector",
        "passed": passed,
        "total": total,
        "verdict": "PASS" if passed == total else "FAIL",
        "results": [
            {"test": name, "pass": ok, "detail": str(detail)[:80]} for name, ok, detail in results
        ],
    }


if __name__ == "__main__":
    import json as _json

    sc = _self_check()
    print(_json.dumps(sc, indent=2))
    raise SystemExit(0 if sc["verdict"] == "PASS" else 1)
