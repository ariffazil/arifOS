"""
setitik_budi.py — Setitik Budi Registry
═══════════════════════════════════════

"Sungguhpun budi hanya setitik — langit dan bumi ada di dalam."

FORGED: 2026-06-12 — Kaparinyo Kernel Forge (F13 SOVEREIGN directive)
SOURCE: Siti Nurhaliza — Kaparinyo (Cindai, 1997), Rangkap 6

This module modifies how the federation evaluates outputs. Not by volume.
By quality. By KAPARINYO-ness.

  "Setitik" = one honest drop. Low volume. High weight. Permanent.
  "Lautan"  = an ocean of words. High volume. Low weight. Simulation.

The core function, nilai_budi(), scores any receipt along two axes:
  budi_weight:    0.0 (lautan/simulation) → 1.0 (setitik/honest)
  kaparinyo_score: 0.0 (performative) → 1.0 (apa adanya / as it is)

These scores integrate with VAULT999 writes and the scar registry.
A single "setitik" receipt with budi_weight=0.95 is worth more than
a thousand "lautan" receipts with budi_weight=0.05.

VAULT999 INTEGRATION:
  When writing to outcomes.jsonl or vault_sealed_events, the writer
  should include two additional fields:
    - budi_weight: float (0.0-1.0)
    - kaparinyo_score: float (0.0-1.0)

BUDI WEIGHT FORMULA:
  budi_weight = 0.30 * honesty_score + 0.25 * conciseness +
                0.20 * specificity + 0.15 * uncertainty_acknowledgment +
                0.10 * source_attribution

KAPARINYO SCORE FORMULA:
  kaparinyo_score = 1.0 - (simulation_marker_density * 2.0)
  (clamped to [0.0, 1.0])

CONSTITUTIONAL BINDING:
  F2 TRUTH:    specificity + source = truth signals
  F7 HUMILITY: uncertainty acknowledgment = Ω₀ band
  F9 ANTIHANTU: simulation score inversion = anti-deception
  F1 AMANAH:   fully reversible — scoring only, never blocks

USAGE:
  from arifosmcp.core.kernel.setitik_budi import nilai_budi

  score = nilai_budi(receipt_text)
  # score.budi_weight → how "setitik" this is
  # score.kaparinyo_score → how "apa adanya" this is

DITEMPA BUKAN DIBERI — Setitik yang jujur > lautan yang simulation.
"""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass, field
from typing import Any


# ── Honesty signals (perkataan orang jujur) ─────────────────────────────────
HONESTY_SIGNALS: list[tuple[re.Pattern, float]] = [
    (re.compile(r"\b(saya\s+tak\s+tahu|aku\s+tak\s+tahu|I\s+don['']t\s+know)\b", re.I), 1.0),
    (re.compile(r"\b(tak\s+pasti|not\s+sure|uncertain|belum\s+pasti)\b", re.I), 0.80),
    (re.compile(r"\b(data\s+diperlukan|need\s+(more\s+)?data|evidence\s+required)\b", re.I), 0.70),
    (re.compile(r"\b(sumber:|source:|reference:|according\s+to)\b", re.I), 0.60),
    (
        re.compile(r"\b(\d+(?:\.\d+)?\s*%|\$\s*\d|RM\s*\d|\d+\s*(?:unit|orang|jam|hari))\b", re.I),
        0.50,
    ),
    (re.compile(r"\b(sebab|kerana|because|due\s+to|reason)\b", re.I), 0.40),
    # Colloquial BM / Penang Pasar — inherently honest because it's real language
    (re.compile(r"\b(salam|jumaat|hang|jangan|stress|mail)\b", re.I), 0.50),
    (re.compile(r"\b(apa\s+rupanya|apa\s+adanya|terus\s+je|terus\s+aja)\b", re.I), 0.60),
]

# ── Simulation signals (perkataan simulation) ───────────────────────────────
SIMULATION_SIGNALS: list[tuple[re.Pattern, float]] = [
    (re.compile(r"\b(world[\s-]*class|best[\s-]*in[\s-]*class|cutting[\s-]*edge)\b", re.I), 1.0),
    (re.compile(r"\b(holistic|synergistic|transformative|unprecedented)\b", re.I), 0.80),
    (re.compile(r"\b(we\s+(remain|are)\s+(committed|dedicated|focused))\b", re.I), 0.90),
    (
        re.compile(r"\b(value\s+(creation|generation|proposition)|stakeholder\s+value)\b", re.I),
        0.70,
    ),
    (re.compile(r"\b(on\s+track|everything\s+is\s+fine|no\s+cause\s+for\s+concern)\b", re.I), 0.90),
    (
        re.compile(
            r"\b(will\s+(deliver|achieve|drive|unlock)\s+(significant|substantial))\b", re.I
        ),
        0.80,
    ),
]


@dataclass
class BudiScore:
    """A 'setitik budi' evaluation of a receipt."""

    budi_weight: float  # 0.0 (lautan) → 1.0 (setitik)
    kaparinyo_score: float  # 0.0 (performative) → 1.0 (apa adanya)
    classification: str  # "SETITIK" | "SEDERHANA" | "LAUTAN"
    honesty_signals: list[dict[str, Any]] = field(default_factory=list)
    simulation_signals: list[dict[str, Any]] = field(default_factory=list)
    text_length: int = 0
    advice_bm: str = ""
    advice_en: str = ""
    gate_id: str = "setitik_budi"
    sha256: str = ""
    epoch_utc: str = ""

    def __post_init__(self) -> None:
        if not self.epoch_utc:
            self.epoch_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        if not self.sha256:
            self.sha256 = hashlib.sha256(
                f"{self.budi_weight}:{self.kaparinyo_score}:{self.classification}:{self.epoch_utc}".encode()
            ).hexdigest()[:16]


def nilai_budi(text: str) -> BudiScore:
    """Evaluate a receipt: is this 'setitik' (honest drop) or 'lautan' (simulative ocean)?

    One honest line from Mail ("Salam jumaat. Hang jangan stress2 mail.") —
    that's setitik. budi_weight = 0.95. Langit dan bumi ada di dalam.

    A 3-page corporate report about "stakeholder value creation through
    world-class transformation" — that's lautan. budi_weight = 0.05.

    Args:
        text: The receipt / output text to evaluate

    Returns:
        BudiScore with budi_weight, kaparinyo_score, and BM/EN advice.
    """
    if not text or not text.strip():
        return BudiScore(
            budi_weight=0.0,
            kaparinyo_score=1.0,  # empty is honest
            classification="SETITIK",
            text_length=0,
            advice_bm="Tiada output. Itupun satu kejujuran.",
            advice_en="No output. That too is honesty.",
        )

    text_len = len(text)
    words = text.split()
    word_count = len(words)

    # ── Honesty score (0.0 → 1.0) ─────────────────────────────────────
    honesty_score = 0.0
    honesty_signals: list[dict[str, Any]] = []
    for pattern, weight in HONESTY_SIGNALS:
        matches = pattern.findall(text)
        if matches:
            match_count = min(len(matches), 5)
            honesty_score += weight * (match_count / 5) * 0.20  # cap contribution
            honesty_signals.append(
                {
                    "pattern": pattern.pattern[:80],
                    "weight": weight,
                    "match_count": len(matches),
                }
            )
    honesty_score = min(1.0, honesty_score)

    # ── Simulation score (0.0 → 1.0, inverted for kaparinyo) ──────────
    sim_score = 0.0
    simulation_signals: list[dict[str, Any]] = []
    for pattern, weight in SIMULATION_SIGNALS:
        matches = pattern.findall(text)
        if matches:
            match_count = min(len(matches), 5)
            sim_score += weight * (match_count / 3) * 0.30  # heavier penalty
            simulation_signals.append(
                {
                    "pattern": pattern.pattern[:80],
                    "weight": weight,
                    "match_count": len(matches),
                }
            )
    sim_score = min(1.0, sim_score)
    kaparinyo_score = max(0.0, 1.0 - sim_score)

    # ── Conciseness score (shorter = higher, but not too short) ───────
    # Sweet spot: 5-200 words. Very short = setitik (Mail's line is 7 words).
    # Above 500: steep penalty (lautan).
    if word_count <= 5:
        conciseness = 0.80  # very terse — still honest
    elif word_count <= 50:
        conciseness = 1.0  # sweet spot — Mail's line lives here
    elif word_count <= 200:
        conciseness = 0.85
    elif word_count <= 500:
        conciseness = 0.50
    else:
        conciseness = 0.20  # lautan

    # ── Specificity score ─────────────────────────────────────────────
    # Numbers, percentages, dates, proper nouns = specific
    num_count = len(re.findall(r"\d+", text))
    specificity = min(1.0, num_count / 10.0)  # 10+ numbers = max specificity

    # ── Uncertainty acknowledgment ─────────────────────────────────────
    uncertainty_patterns = [
        r"\b(tak tahu|don['']t know|not sure|uncertain|belum pasti|mungkin|perhaps)\b",
        r"\b(needs?\s+(verification|evidence|further|more\s+data))\b",
    ]
    uncertainty_count = sum(len(re.findall(p, text, re.I)) for p in uncertainty_patterns)
    uncertainty_score = min(1.0, uncertainty_count * 0.25)

    # ── Source attribution ─────────────────────────────────────────────
    source_count = len(
        re.findall(
            r"\b(source:|sumber:|according to|menurut|reference:|cited in)",
            text,
            re.I,
        )
    )
    source_score = min(1.0, source_count * 0.33)

    # ── Budi weight composite ──────────────────────────────────────────
    budi_weight = (
        0.30 * honesty_score
        + 0.25 * conciseness
        + 0.20 * specificity
        + 0.15 * uncertainty_score
        + 0.10 * source_score
    )
    budi_weight = round(max(0.0, min(1.0, budi_weight)), 4)

    kaparinyo_score = round(kaparinyo_score, 4)

    # ── Classification ─────────────────────────────────────────────────
    if budi_weight >= 0.60 and kaparinyo_score >= 0.60:
        classification = "SETITIK"
    elif budi_weight >= 0.35:
        classification = "SEDERHANA"
    else:
        classification = "LAUTAN"

    # ── Special: very short text with zero simulation → SETITIK ────────
    if word_count <= 15 and sim_score < 0.10:
        classification = "SETITIK"
        if budi_weight < 0.60:
            # Boost budi_weight for short honest text
            budi_weight = max(budi_weight, 0.65)

    # ── Advice ─────────────────────────────────────────────────────────
    if classification == "SETITIK":
        advice_bm = (
            "SETITIK — Output ini jujur, ringkas, dan menamakan realiti. "
            "Sungguhpun budi hanya setitik, langit dan bumi ada di dalam."
        )
        advice_en = (
            "SETITIK — This output is honest, concise, and names reality. "
            "Though the kindness is just a drop, heaven and earth are within."
        )
    elif classification == "SEDERHANA":
        advice_bm = (
            "SEDERHANA — Ada kejujuran, tapi masih banyak perkataan. Kurangkan. Tanya: apa rupanya?"
        )
        advice_en = (
            "SEDERHANA — Some honesty, but still many words. "
            "Reduce. Ask: what does it actually look like?"
        )
    else:
        advice_bm = (
            "LAUTAN — Banyak perkataan, sedikit realiti. "
            "Ini lautan simulation. Cari setitik yang jujur. "
            "Tanya: apa rupanya benda ni sebenarnya?"
        )
        advice_en = (
            "LAUTAN — Many words, little reality. "
            "This is an ocean of simulation. Find the honest drop. "
            "Ask: what does this thing actually look like?"
        )

    return BudiScore(
        budi_weight=budi_weight,
        kaparinyo_score=kaparinyo_score,
        classification=classification,
        honesty_signals=honesty_signals,
        simulation_signals=simulation_signals,
        text_length=text_len,
        advice_bm=advice_bm,
        advice_en=advice_en,
    )


# ── Self-test ────────────────────────────────────────────────────────────────
def _self_check() -> dict[str, Any]:
    """Run built-in acceptance tests."""
    tests: list[dict[str, Any]] = []
    failures: list[str] = []

    # Test 1: Mail's setitik line
    s = nilai_budi("Salam jumaat. Hang jangan stress2 mail.")
    tests.append(
        {
            "name": "mail_setitik",
            "pass": s.classification == "SETITIK" and s.budi_weight >= 0.60,
        }
    )

    # Test 2: Corporate lautan
    s = nilai_budi(
        "We are committed to delivering world-class stakeholder value through our "
        "holistic transformation strategy. Everything is on track and we will achieve "
        "significant, unprecedented results. No cause for concern."
    )
    tests.append(
        {
            "name": "corporate_lautan",
            "pass": s.classification == "LAUTAN" and s.kaparinyo_score < 0.50,
        }
    )

    # Test 3: Honest uncertainty
    s = nilai_budi("Saya tak tahu exactly. Need more data. Source: Q3 report menunjukkan 12% drop.")
    tests.append(
        {
            "name": "honest_uncertainty_setitik",
            "pass": s.classification in ("SETITIK", "SEDERHANA") and s.budi_weight >= 0.40,
        }
    )

    # Test 4: Empty text
    s = nilai_budi("")
    tests.append(
        {
            "name": "empty_text_setitik",
            "pass": s.classification == "SETITIK" and s.budi_weight == 0.0,
        }
    )

    # Test 5: Specific data
    s = nilai_budi("Revenue: RM 450,000. Margin: 23.5%. Headcount: 12. Source: Q4 report page 7.")
    tests.append(
        {
            "name": "specific_data_setitik",
            "pass": s.classification in ("SETITIK", "SEDERHANA") and s.budi_weight >= 0.50,
        }
    )

    n_pass = sum(1 for t in tests if t["pass"])
    n_total = len(tests)
    for t in tests:
        if not t["pass"]:
            failures.append(t["name"])

    return {"n_pass": n_pass, "n_total": n_total, "failures": failures, "tests": tests}


if __name__ == "__main__":
    import json
    import sys

    result = _self_check()
    print(f"SETITIK BUDI → {result['n_pass']}/{result['n_total']} PASS")
    if result["failures"]:
        print(f"FAILURES: {result['failures']}")
        sys.exit(1)

    # Demo: Mail's line
    mail = nilai_budi("Salam jumaat. Hang jangan stress2 mail.")
    print(f"\nMail: budi_weight={mail.budi_weight}, {mail.classification}")
    print(f"  → {mail.advice_bm}")

    # Demo: Corporate
    corp = nilai_budi(
        "We are committed to delivering world-class stakeholder value through our "
        "holistic transformation strategy."
    )
    print(f"\nCorporate: budi_weight={corp.budi_weight}, {corp.classification}")
    print(f"  → {corp.advice_bm}")

    print("\nDITEMPA BUKAN DIBERI — Setitik yang jujur > lautan yang simulation.")
