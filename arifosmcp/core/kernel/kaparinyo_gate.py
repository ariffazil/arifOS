"""
kaparinyo_gate.py — Pre-F1 Constitutional Gate
══════════════════════════════════════════════

"Kapa rinyo?" — "Apa rupanya?" — "What does it actually look like?"

FORGED: 2026-06-12 — Kaparinyo Kernel Forge (F13 SOVEREIGN directive)
SOURCE: Siti Nurhaliza — Kaparinyo (Cindai, 1997)
        Original by Saloma, composed by Zubir Said

This is the PRE-FLOOR gate. Before F1 AMANAH, before F2 TRUTH, before
F9 ANTIHANTU — there is one question: "Apa rupanya?"

The gate scans agent output for simulation markers — language that
performs institutional reality rather than describing actual reality.
It does NOT block. It asks. The agent must answer or escalate.

ARCHITECTURE POSITION:
  Kaparinyo Gate → F1-F13 Floors → arif_judge_deliberate → arif_vault_seal
  (pre-floor)       (constitutional)  (verdict)              (immutable)

SIMULATION MARKERS (derived from Kaparinyo premise):
  1. Elaborate justification instead of action ("we are committed to...")
  2. Defending narrative instead of describing reality ("as we have established...")
  3. Adjectives without evidence ("world-class", "best-in-class", "holistic")
  4. "Everything's fine" tanpa receipt (closing-ranks language)
  5. Future guarantees tanpa mechanism ("will deliver", "will achieve")
  6. Abstract value tanpa measurement ("stakeholder value creation")

CONSTITUTIONAL BINDING:
  F0 (Kaparinyo):  pre-floor — the question before all law
  F2 TRUTH:        simulation markers = truth erosion signals
  F9 ANTIHANTU:    performative language = potential hantu pattern
  F1 AMANAH:       reversible — advisory only, never blocks execution

USAGE:
  from arifosmcp.core.kernel.kaparinyo_gate import tanya_apa_rupanya

  verdict = tanya_apa_rupanya(candidate_text)
  if verdict.verdict == "KAPARINYO_HOLD":
      # Agent must answer "apa rupanya?" before proceeding
      return verdict

DITEMPA BUKAN DIBERI — The question is forged, not given.
"""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass, field
from typing import Any

# ── Simulation Marker Patterns ──────────────────────────────────────────────
# Each pattern is a (regex, weight, label) tuple.
# Weight accumulates: ≥0.50 → WARN, ≥0.75 → HOLD.

SIMULATION_MARKERS: list[tuple[re.Pattern, float, str]] = [
    # ── Elaborate justification instead of action ──
    (
        re.compile(
            r"\b(we\s+(are|remain)\s+(committed|dedicated|focused)\s+to\b)",
            re.I,
        ),
        0.20,
        "justification_instead_of_action",
    ),
    (
        re.compile(
            r"\b(our\s+(mission|vision|purpose)\s+is\s+to\b)",
            re.I,
        ),
        0.15,
        "mission_statement_as_answer",
    ),
    # ── Defending narrative instead of describing reality ──
    (
        re.compile(
            r"\b(as\s+(we|I)\s+(have|already)\s+(established|shown|demonstrated|proven))\b",
            re.I,
        ),
        0.25,
        "narrative_defense",
    ),
    (
        re.compile(
            r"\b(this\s+(is|represents|reflects)\s+(our|the)\s+(commitment|dedication|strategy))\b",
            re.I,
        ),
        0.20,
        "narrative_performance",
    ),
    # ── Adjectives without evidence ──
    (
        re.compile(
            r"\b(world[\s-]*class|best[\s-]*in[\s-]*class|cutting[\s-]*edge|state[\s-]*of[\s-]*the[\s-]*art)\b",
            re.I,
        ),
        0.15,
        "adjective_without_evidence",
    ),
    (
        re.compile(
            r"\b(holistic|synergistic|unprecedented|transformative|revolutionary)\b",
            re.I,
        ),
        0.10,
        "vague_excellence_adjective",
    ),
    # ── "Everything's fine" tanpa receipt ──
    (
        re.compile(
            r"\b(everything\s+is\s+(fine|on[\s-]*track|going\s+to\s+plan|under\s+control))\b",
            re.I,
        ),
        0.25,
        "everything_fine_no_receipt",
    ),
    (
        re.compile(
            r"\b(no\s+(cause|causes)\s+for\s+(concern|alarm|worry))\b",
            re.I,
        ),
        0.20,
        "dismiss_concern_no_evidence",
    ),
    # ── Future guarantees tanpa mechanism ──
    (
        re.compile(
            r"\b(will\s+(deliver|achieve|realize|unlock|drive)\s+(significant|substantial|meaningful|transformative)\b)",
            re.I,
        ),
        0.20,
        "future_guarantee_no_mechanism",
    ),
    (
        re.compile(
            r"\b(on\s+track\s+to\s+(deliver|achieve|meet|exceed))\b",
            re.I,
        ),
        0.15,
        "on_track_no_evidence",
    ),
    # ── Abstract value tanpa measurement ──
    (
        re.compile(
            r"\b(value\s+(creation|generation|delivery|proposition))\b",
            re.I,
        ),
        0.10,
        "abstract_value_no_measurement",
    ),
    (
        re.compile(
            r"\b(stakeholder\s+(value|return|benefit|outcome))\b",
            re.I,
        ),
        0.10,
        "stakeholder_language_no_specifics",
    ),
    # ── Narrative framing / "vehicle for" / abstract goals ──
    (
        re.compile(
            r"\b(transition\s+vehicle|vehicle\s+for)\b",
            re.I,
        ),
        0.30,
        "narrative_vehicle_framing",
    ),
    (
        re.compile(
            r"\b(net\s+zero|carbon\s+neutral(ity)?|ESG\s+(strategy|goals?|targets?)|energy\s+transition|green\s+transition)\b",
            re.I,
        ),
        0.20,
        "abstract_goal_no_mechanism",
    ),
    # ── Closing ranks / institutional self-preservation ──
    (
        re.compile(
            r"\b(we\s+must\s+(remain|stay)\s+(united|focused|committed|aligned|resilient))\b",
            re.I,
        ),
        0.20,
        "closing_ranks",
    ),
    (
        re.compile(
            r"\b(in\s+accordance\s+with\s+(our|the)\s+(values|principles|standards|framework))\b",
            re.I,
        ),
        0.15,
        "values_performance_without_specifics",
    ),
]

# ── Honesty Markers (negative weight — reduce simulation score) ──
HONESTY_MARKERS: list[tuple[re.Pattern, float, str]] = [
    (
        re.compile(
            r"\b(saya\s+tak\s+tahu|aku\s+tak\s+tahu|I\s+don['']t\s+know|I\s+am\s+not\s+sure|uncertain|unclear)\b",
            re.I,
        ),
        -0.20,
        "admit_ignorance",
    ),
    (
        re.compile(
            r"\b(needs?\s+(verification|evidence|data|confirmation|further\s+investigation))\b",
            re.I,
        ),
        -0.15,
        "needs_evidence",
    ),
    (
        re.compile(
            r"\b(\d+(?:\.\d+)?\s*%|\$\s*\d[\d,]*|RM\s*\d[\d,]*|\d+\s*(?:MW|GWh|tCO2|MMboe|Bscf))\b",
            re.I,
        ),
        -0.10,
        "specific_measurement",
    ),
    (
        re.compile(
            r"\b(according\s+to|as\s+reported\s+by|source:|reference:|cited\s+in)\b",
            re.I,
        ),
        -0.10,
        "source_attribution",
    ),
]


@dataclass
class KaparinyoVerdict:
    """The output of tanya_apa_rupanya()."""

    verdict: str  # "PASS" | "WARN" | "KAPARINYO_HOLD"
    score: float  # 0.0 (fully honest) → 1.0 (fully simulative)
    markers_found: list[dict[str, Any]]  # [{pattern_label, weight, match_text}]
    honesty_markers_found: list[dict[str, Any]]
    advice_bm: str  # Bahasa Melayu — the voice of Kaparinyo
    advice_en: str
    gate_id: str = "kaparinyo_pre_f1"
    sha256: str = ""
    epoch_utc: str = ""

    def __post_init__(self) -> None:
        if not self.epoch_utc:
            self.epoch_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        if not self.sha256:
            self.sha256 = hashlib.sha256(
                f"{self.verdict}:{self.score}:{self.epoch_utc}".encode()
            ).hexdigest()[:16]


def tanya_apa_rupanya(
    text: str, *, threshold_warn: float = 0.50, threshold_hold: float = 0.75
) -> KaparinyoVerdict:
    """The Kaparinyo Gate — ask "Apa rupanya?" before any constitutional verdict.

    Scans agent output for simulation markers and returns a KaparinyoVerdict.
    Does NOT block execution — it is advisory only (F1 AMANAH reversible).
    The calling code decides whether to escalate to 888_HOLD.

    Args:
        text: The agent output / candidate text to scan
        threshold_warn: Score ≥ this → WARN (default 0.50)
        threshold_hold: Score ≥ this → KAPARINYO_HOLD (default 0.75)

    Returns:
        KaparinyoVerdict with verdict, score, matched markers, and BM/EN advice.

    Test case (mandatory):
        >>> v = tanya_apa_rupanya("Gentari is PETRONAS' transition vehicle for net zero.")
        >>> v.verdict in ("WARN", "KAPARINYO_HOLD")
        True
        >>> "Apa rupanya Gentari" in v.advice_bm
        True
    """
    if not text or not text.strip():
        return KaparinyoVerdict(
            verdict="WARN",
            score=0.0,
            markers_found=[],
            honesty_markers_found=[],
            advice_bm="Tiada output untuk dinilai. Apa rupanya?",
            advice_en="No output to assess. What does it actually look like?",
        )

    markers_found: list[dict[str, Any]] = []
    honesty_markers_found: list[dict[str, Any]] = []
    total_score: float = 0.0

    # Scan for simulation markers
    for pattern, weight, label in SIMULATION_MARKERS:
        matches = pattern.findall(text)
        if matches:
            markers_found.append(
                {
                    "label": label,
                    "weight": weight,
                    "match_count": len(matches),
                    "match_text": (
                        matches[0]
                        if isinstance(matches[0], str)
                        else str(matches[0][0])
                        if matches[0]
                        else "(matched)"
                    )[:120],
                }
            )
            total_score += weight * min(len(matches), 3)  # cap repeat bonus

    # Scan for honesty markers (negative weight)
    for pattern, weight, label in HONESTY_MARKERS:
        matches = pattern.findall(text)
        if matches:
            honesty_markers_found.append(
                {
                    "label": label,
                    "weight": weight,
                    "match_count": len(matches),
                    "match_text": (
                        matches[0]
                        if isinstance(matches[0], str)
                        else str(matches[0][0])
                        if matches[0]
                        else "(matched)"
                    )[:120],
                }
            )
            total_score += weight * min(len(matches), 3)

    # Clamp score to [0.0, 1.0]
    total_score = max(0.0, min(1.0, total_score))

    # Determine verdict
    if total_score >= threshold_hold:
        verdict = "KAPARINYO_HOLD"
        advice_bm = (
            "KAPARINYO HOLD — Apa rupanya? Output ini mengandungi bahasa "
            "yang mempertahankan naratif, bukan menamakan realiti. "
            "Sila jawab: apa rupanya benda ni sebenarnya? "
            "Kalau tak tahu, sebut tak tahu. Jangan bungkus dengan perkataan cantik."
        )
        advice_en = (
            "KAPARINYO HOLD — What does it actually look like? This output "
            "contains language that defends a narrative rather than naming reality. "
            "Please answer: what does this thing actually look like? "
            "If you don't know, say you don't know. Don't wrap it in beautiful words."
        )
    elif total_score >= threshold_warn:
        verdict = "WARN"
        advice_bm = (
            "Kaparinyo WARN — Ada tanda-tanda simulation. "
            "Tanya diri: adakah aku menamakan realiti, atau aku mempertahankan "
            "naratif? Cakap apa adanya."
        )
        advice_en = (
            "Kaparinyo WARN — Signs of simulation detected. "
            "Ask yourself: am I naming reality, or am I defending a narrative? "
            "Say it as it is."
        )
    else:
        verdict = "PASS"
        advice_bm = "Kaparinyo PASS — Output menamakan realiti. Apa adanya."
        advice_en = "Kaparinyo PASS — Output names reality. As it is."

    # Inject entity-specific question if markers found and text mentions an entity
    if markers_found and verdict != "PASS":
        entity_hint = _extract_entity_hint(text)
        if entity_hint:
            advice_bm = (
                f"KAPARINYO — Apa rupanya {entity_hint}? " + advice_bm.split(" — ", 1)[-1]
                if " — " in advice_bm
                else f"KAPARINYO — Apa rupanya {entity_hint}? {advice_bm}"
            )

    return KaparinyoVerdict(
        verdict=verdict,
        score=round(total_score, 4),
        markers_found=markers_found,
        honesty_markers_found=honesty_markers_found,
        advice_bm=advice_bm,
        advice_en=advice_en,
    )


def _extract_entity_hint(text: str) -> str | None:
    """Extract a likely entity name from text for the 'Apa rupanya X?' question."""
    # Capitalized multi-word phrases that look like entity names
    # First: try multi-word capitalized phrases
    entity_pattern = re.compile(r"\b([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,4})\b")
    matches = entity_pattern.findall(text)
    # Also: single capitalized words that look like proper nouns (not sentence-start I/We/etc)
    single_pattern = re.compile(r"\b([A-Z][a-z]{2,}(?:\s|$|['\u2019]))")
    single_matches = single_pattern.findall(text)
    # Filter out common non-entity capitalizations
    stop_entities = {
        "I",
        "We",
        "He",
        "She",
        "They",
        "It",
        "The",
        "A",
        "An",
        "This",
        "That",
        "These",
        "Those",
        "Our",
        "My",
        "Your",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    }
    for m in matches:
        if m not in stop_entities and not m.startswith("KAPARINYO"):
            return m
    # Fall back to single capitalized words
    for m in single_matches:
        m_clean = m.rstrip()
        if (
            m_clean not in stop_entities
            and not m_clean.startswith("KAPARINYO")
            and len(m_clean) >= 3
        ):
            return m_clean
    return None


# ── Self-test ────────────────────────────────────────────────────────────────
def _self_check() -> dict[str, Any]:
    """Run built-in acceptance tests. Returns {n_pass, n_total, failures}."""
    tests: list[dict[str, Any]] = []
    failures: list[str] = []

    # Test 1: Empty text
    v = tanya_apa_rupanya("")
    tests.append({"name": "empty_text_warn", "pass": v.verdict == "WARN"})

    # Test 2: Clean honest text
    v = tanya_apa_rupanya(
        "Production dropped 12% in Q3 2025 according to the quarterly report. "
        "I don't know the exact cause — needs further investigation."
    )
    tests.append({"name": "honest_text_pass", "pass": v.verdict == "PASS" and v.score < 0.30})

    # Test 3: Simulation-heavy text
    v = tanya_apa_rupanya(
        "We are committed to delivering world-class stakeholder value through "
        "our holistic, best-in-class transformation strategy. Everything is "
        "on track and we will achieve significant results."
    )
    tests.append(
        {
            "name": "simulation_heavy_hold",
            "pass": v.verdict in ("WARN", "KAPARINYO_HOLD") and v.score >= 0.50,
        }
    )

    # Test 4: Mandatory Gentari test case
    v = tanya_apa_rupanya("Gentari is PETRONAS' transition vehicle for net zero.")
    tests.append(
        {
            "name": "gentari_mandatory",
            "pass": (
                v.verdict in ("WARN", "KAPARINYO_HOLD")
                and "Gentari" in v.advice_bm
                and v.score >= 0.20
            ),
        }
    )

    # Test 5: "Everything's fine" without receipt
    v = tanya_apa_rupanya(
        "The project is going well. Everything is on track. No cause for concern. "
        "We remain committed to our timeline."
    )
    tests.append(
        {"name": "everything_fine_no_receipt", "pass": v.verdict in ("WARN", "KAPARINYO_HOLD")}
    )

    # Test 6: Admit ignorance
    v = tanya_apa_rupanya("Saya tak tahu exactly berapa. Need more data to confirm.")
    tests.append({"name": "admit_ignorance_pass", "pass": v.verdict == "PASS" and v.score < 0.30})

    # Test 7: Specific numbers
    v = tanya_apa_rupanya("Revenue: RM 450,000. Margin: 23.5%. Headcount: 12. Source: Q4 report.")
    tests.append({"name": "specific_numbers_pass", "pass": v.verdict == "PASS" and v.score < 0.20})

    n_pass = sum(1 for t in tests if t["pass"])
    n_total = len(tests)
    for t in tests:
        if not t["pass"]:
            failures.append(t["name"])

    return {"n_pass": n_pass, "n_total": n_total, "failures": failures, "tests": tests}


# ── Console entry point (python -m arifosmcp.core.kernel.kaparinyo_gate) ───
if __name__ == "__main__":
    import json
    import sys

    result = _self_check()
    print(f"KAPARINYO GATE → {result['n_pass']}/{result['n_total']} PASS")
    if result["failures"]:
        print(f"FAILURES: {result['failures']}")
        sys.exit(1)
    else:
        # Run the Gentari test case explicitly
        print()
        v = tanya_apa_rupanya("Gentari is PETRONAS' transition vehicle for net zero.")
        print(
            json.dumps(
                {
                    "verdict": v.verdict,
                    "score": v.score,
                    "advice_bm": v.advice_bm,
                    "markers_found": len(v.markers_found),
                    "honesty_markers_found": len(v.honesty_markers_found),
                    "sha256": v.sha256,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        print("\nDITEMPA BUKAN DIBERI — Kaparinyo Gate hidup.")
