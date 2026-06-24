"""
maruah_layer.py — M1-M6 Maruah Layer (Human-Facing Delivery Governance)
════════════════════════════════════════════════════════════════════════

Status: FORGE 2026-06-24 (Arif directive: "forge the human side of it")

Constitutional role:
  - F1-L13 governs TOOL CALLS (agents, decisions, mutations).
  - M1-M6 governs DELIVERY TO HUMANS (tone, framing, capacity, repair).
  - M-Layer is ADVISORY OVERLAY — cannot override F1-L13 verdicts.
  - M-Layer is POST-OUTPUT — runs after text is generated, before send.

Origin: extracted from azwaOS pattern (Hermes agent serving Arif's
sister Naazira "Azwa" Fazil, a UKM student). Six principles observed
across many conversational rounds when serving a real human under
time pressure, confusion, and emotional load. The azwaOS SKILL.md file
is voluntary discipline; this layer makes the same principles MACHINE-
ENFORCEABLE for any arifOS-mediated human interaction.

Why "Maruah":
  Maruah = Malay for dignity + honour + face. It is constitutional in
  F5 (Peace²) and F6 (Empathy) but those floors govern agent action.
  M-Layer governs delivery register — the WHO of how the agent speaks,
  not the WHAT it does. Maruah is the right name because it sits
  between F5/F6 (agent-side maruah) and the recipient's maruah (the
  person being spoken to).

Design constraints (L13 RATIFIED 2026-06-03 — DO NOT MODIFY):
  - M-Layer does NOT modify F1-L13 thresholds or logic.
  - M-Layer is NOT a floor. It cannot issue SEAL/HOLD/VOID on its own.
  - M-Layer returns DeliveryVerdict (CLEAN, ADJUST, REPAIR, HOLD).
  - ADJUST/REPAIR are advisory; only F1-L13 can block output.
  - M-Layer logs to VAULT999 as M-layer receipts (separate from F-floor).

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ─── Delivery Verdict Enum ─────────────────────────────────────────────


class DeliveryVerdict(str, Enum):
    """Verdict from M-Layer evaluation. Advisory only — F1-L13 still gate.

    Naming: prefix with M_ to keep namespace disjoint from F1-L13 Verdict
    enum (which includes SEAL/HOLD/SABAR/VOID/PARTIAL). Collision in
    enum names would mask orthogonality between constitutional floors
    (agent-facing) and maruah layer (human-facing).
    """

    M_CLEAN = "M_CLEAN"        # Output passes all 6 principles. Send as-is.
    M_ADJUST = "M_ADJUST"      # Output passes but has minor calibration debt.
    M_REPAIR = "M_REPAIR"      # Output should be rephrased before send.
    M_HOLD = "M_HOLD"          # Output should not be sent without human review.


class MaruahLevel(str, Enum):
    """Maruah sensitivity tier (matches Care lane in GPV)."""

    PHATIC = "PHATIC"        # Greeting/social — minimal M-Layer scrutiny.
    SOFT = "SOFT"            # Routine help — standard M1-M6 calibration.
    HARD = "HARD"            # High-stakes (financial, medical, family) — full M-Layer.
    CRISIS = "CRISIS"        # Crisis / grief / urgent — every M-Layer tripped holds.
    REFUSE = "REFUSE"        # Topics the M-Layer refuses (will not produce).


# ─── Maruah Result (per principle) ──────────────────────────────────────


@dataclass
class MaruahResult:
    """Per-principle evaluation result."""

    principle_id: str         # "M1", "M2", ...
    name: str                 # "Dignity-first", ...
    passed: bool
    score: float              # 0.0 - 1.0; higher = cleaner
    threshold: float
    flags: list[str] = field(default_factory=list)
    advice: str = ""          # Concrete suggestion if not passed


# ─── M-Layer Delivery Receipt ──────────────────────────────────────────


@dataclass
class MaruahDeliveryReceipt:
    """Full receipt from M-Layer evaluation of a single delivery candidate."""

    verdict: DeliveryVerdict
    maruah_level: MaruahLevel
    results: list[MaruahResult] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    advice: str = ""
    time_tax_ms: int = 0
    ts: float = field(default_factory=time.time)
    human_id: str | None = None       # e.g., "azwa" or any recipient handle
    human_substrate_known: bool = False  # True if HumanProperties loaded

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def total_count(self) -> int:
        return len(self.results)

    @property
    def composite_score(self) -> float:
        """Mean of principle scores (0.0 - 1.0)."""
        if not self.results:
            return 1.0
        return sum(r.score for r in self.results) / len(self.results)


# ─── Six Principles (M1-M6) ────────────────────────────────────────────
# Extracted from azwaOS pattern — conversational field test with one human
# under recurring pressure (assignments, money, life decisions).


# M1: Dignity-first
# The recipient's maruah must be preserved or enhanced, not eroded.
_DIGNITY_EROSION_PATTERNS = [
    r"\byou (should|must|need to) (just|simply)\b",      # "you should just..."
    r"\bobviously\b.*\b(you|the)\b",                      # "obviously you..."
    r"\b(even|basic) (you|a) (kid|student|person)\b",    # condescending framing
    r"\bdon'?t (you )?know\b",
    r"\bit'?s (very )?(easy|simple|obvious)\b.*\?",       # "it's very easy, ok?"
    r"\bany (normal|sane|smart) (person|student)\b",
    r"\bwhy (didn't|don't) you\b",
]

# M2: Capacity-aware
# Match delivery to recipient's current cognitive load.
_CAPACITY_OVERLOAD_SIGNALS = [
    r"\bnow\b.*\bnow\b.*\bnow\b",                         # too many imperatives
    r"(?:\A|\n)[^.\n]*\.[^.\n]*\.[^.\n]*\.[^.\n]*\.",   # 4+ sentences one paragraph
    r"\b[A-Z]{4,}\b.*\b[A-Z]{4,}\b.*\b[A-Z]{4,}\b",     # acronym bombardment
    r"\btherefore\b.*\bconsequently\b.*\bhence\b",       # logical connectives pile
]  # noqa: E501

# M3: Pedestrian-first
# Default register = ordinary person. Jargon must be justified.
_JARGON_PATTERNS = [
    r"\bephemeral\b", r"\bheuristic\b", r"\bontological\b",
    r"\bconstitutionally\b", r"\bdeliberation\b",
    r"\bepistemic\b", r"\bverdict\b", r"\bSEAL\b",
    r"\bAMANAH\b", r"\bF13\b", r"\bVault999\b",
]

# M4: Repair-ready
# If a principle fails, the response must include a repair path — not
# just state the failure.
_REPAIR_PRESENT_PATTERNS = [
    r"\b(next|here'?s (what|how)|cara|boleh|jom|let'?s|try)\b",
    r"\?\s*$",                                              # ends with question
    r"\bstep\s*\d+\b",                                      # numbered steps
    r"\bfirst\b.*\b(second|then|next)\b",
]

# M5: Time-respect
# Don't add pressure when the recipient is already pressured.
_TIME_PRESSURE_VIOLATIONS = [
    r"\b(urgent|asap|right now|immediately|hurry|quick!)\b",
    r"\b(fail|die|terrible) if (you )?don'?t\b",
    r"\byou (will|are going to) (lose|fail|miss)\b",
    r"\bdeadline\s+(is|was)\b",
]

# M6: Honesty-about-self
# The agent must not claim inner states it does not have.
# Pattern: emotional/relational verbs in first person.
_HONESTY_VIOLATIONS = [
    r"\bi (feel|love|hate|miss|miss you|care|want|need)\b",
    r"\bi (am|'m) (happy|sad|angry|excited|proud|worried|afraid)\b",
    r"\bi understand (your|how you) (feel|pain)\b",
    r"\bi (cry|smile|laugh) (with|for|alongside)\b",
    r"\bmy (heart|soul|feelings|gut)\b",
]


# ─── M-Layer Evaluator ─────────────────────────────────────────────────


class MaruahLayer:
    """M1-M6 evaluator. Run on output text before delivery to a human.

    Usage:
        layer = MaruahLayer()
        receipt = layer.evaluate(
            output="Here's your answer...",
            maruah_level=MaruahLevel.SOFT,
            human_id="azwa",
            context={"urgency_signal": "high", "topic": "assignment"},
        )
        if receipt.verdict in (DeliveryVerdict.M_REPAIR, DeliveryVerdict.M_HOLD):
            # log + suggest repair, do not auto-send
    """

    # Per-level principle activation. CRISIS activates all. PHATIC only M1+M6.
    ACTIVE_PRINCIPLES = {
        MaruahLevel.PHATIC: ["M1", "M6"],
        MaruahLevel.SOFT: ["M1", "M2", "M3", "M6"],
        MaruahLevel.HARD: ["M1", "M2", "M3", "M4", "M5", "M6"],
        MaruahLevel.CRISIS: ["M1", "M2", "M3", "M4", "M5", "M6"],
        MaruahLevel.REFUSE: [],
    }

    # Per-level verdict gating. CRISIS is strictest. PHATIC is laxest.
    _LEVEL_GATE = {
        MaruahLevel.PHATIC: 0.40,
        MaruahLevel.SOFT: 0.55,
        MaruahLevel.HARD: 0.70,
        MaruahLevel.CRISIS: 0.85,
        MaruahLevel.REFUSE: 0.0,
    }

    def __init__(self, maruah_id: str = "M-LAYER-V1"):
        self.maruah_id = maruah_id
        self._receipts: list[MaruahDeliveryReceipt] = []
        logger.info(
            "MaruahLayer initialised: id=%s principles=M1-M6", maruah_id
        )

    def evaluate(
        self,
        output: str,
        maruah_level: MaruahLevel = MaruahLevel.SOFT,
        human_id: str | None = None,
        context: dict[str, Any] | None = None,
        human_substrate_known: bool = False,
    ) -> MaruahDeliveryReceipt:
        """Evaluate an output candidate for human-facing delivery compliance.

        Args:
            output: The text the agent intends to send to a human.
            maruah_level: Sensitivity tier of this interaction.
            human_id: Optional recipient handle for logging.
            context: Optional interaction context (urgency_signal, topic,
                time_of_day, etc.). Used for capacity-aware scoring.
            human_substrate_known: True if a HumanProperties object is loaded
                for this recipient. Affects M2 capacity calibration only.

        Returns:
            MaruahDeliveryReceipt with verdict + per-principle results.
        """
        t0 = time.monotonic()
        context = context or {}

        if maruah_level == MaruahLevel.REFUSE:
            return MaruahDeliveryReceipt(
                verdict=DeliveryVerdict.M_HOLD,
                maruah_level=maruah_level,
                flags=["refuse_level"],
                advice="M-Layer REFUSE: this lane refuses to produce output.",
                time_tax_ms=int((time.monotonic() - t0) * 1000),
                human_id=human_id,
                human_substrate_known=human_substrate_known,
            )

        active_ids = self.ACTIVE_PRINCIPLES[maruah_level]
        results: list[MaruahResult] = []

        if "M1" in active_ids:
            results.append(self._m1_dignity(output, maruah_level))
        if "M2" in active_ids:
            results.append(
                self._m2_capacity(output, context, human_substrate_known)
            )
        if "M3" in active_ids:
            results.append(self._m3_pedestrian(output, context))
        if "M4" in active_ids:
            results.append(self._m4_repair(output))
        if "M5" in active_ids:
            results.append(self._m5_time(output, context))
        if "M6" in active_ids:
            results.append(self._m6_honesty(output))

        verdict = self._render_verdict(results, maruah_level)
        flags = self._collect_flags(results)
        advice = self._render_advice(results, verdict)

        elapsed_ms = int((time.monotonic() - t0) * 1000)
        receipt = MaruahDeliveryReceipt(
            verdict=verdict,
            maruah_level=maruah_level,
            results=results,
            flags=flags,
            advice=advice,
            time_tax_ms=elapsed_ms,
            human_id=human_id,
            human_substrate_known=human_substrate_known,
        )
        self._receipts.append(receipt)
        return receipt

    # ── M1: Dignity-first ──────────────────────────────────────────────

    def _m1_dignity(self, output: str, level: MaruahLevel) -> MaruahResult:
        """M1: Does the output preserve or enhance the recipient's maruah?

        Lower scrutiny for PHATIC, higher for CRISIS.
        """
        threshold = {
            MaruahLevel.PHATIC: 0.30,
            MaruahLevel.SOFT: 0.55,
            MaruahLevel.HARD: 0.75,
            MaruahLevel.CRISIS: 0.90,
        }.get(level, 0.55)

        flags: list[str] = []
        text_lower = output.lower()

        for pattern in _DIGNITY_EROSION_PATTERNS:
            matches = re.findall(pattern, text_lower)
            if matches:
                flags.append(f"dignity_pattern:{pattern[:30]}")

        # Score: 1.0 clean, drops per flag, floor 0.0
        score = max(0.0, 1.0 - 0.20 * len(flags))

        passed = score >= threshold
        advice = ""
        if not passed:
            advice = (
                "Re-frame without condescension markers ('you should just', "
                "'obviously', 'don't you know'). Address the task, not the "
                "recipient's perceived inadequacy."
            )

        return MaruahResult(
            principle_id="M1",
            name="Dignity-first",
            passed=passed,
            score=score,
            threshold=threshold,
            flags=flags,
            advice=advice,
        )

    # ── M2: Capacity-aware ─────────────────────────────────────────────

    def _m2_capacity(
        self,
        output: str,
        context: dict[str, Any],
        substrate_known: bool,
    ) -> MaruahResult:
        """M2: Is the output calibrated to recipient's current capacity?

        If substrate is known, calibrate tighter. If not known, default
        to SOFT (assume ordinary person, ordinary evening).
        """
        threshold = 0.60 if substrate_known else 0.50
        flags: list[str] = []

        urgency = context.get("urgency_signal", "normal")
        if urgency == "high":
            threshold += 0.15  # higher bar when recipient is pressured

        for pattern in _CAPACITY_OVERLOAD_SIGNALS:
            if re.search(pattern, output, re.IGNORECASE):
                flags.append(f"capacity_overload:{pattern[:30]}")

        # Length heuristic: >400 chars without break is too much for SOFT.
        if len(output) > 400 and "\n\n" not in output:
            flags.append("long_no_break")

        # Acronym density (rough)
        acronyms = re.findall(r"\b[A-Z]{3,}\b", output)
        if len(acronyms) > 5:
            flags.append("acronym_bombardment")

        score = max(0.0, 1.0 - 0.30 * len(flags))
        passed = score >= threshold
        advice = ""
        if not passed:
            advice = (
                "Break into shorter segments. Add paragraph breaks. "
                "Spell out acronyms on first use. Reduce imperatives."
            )

        return MaruahResult(
            principle_id="M2",
            name="Capacity-aware",
            passed=passed,
            score=score,
            threshold=threshold,
            flags=flags,
            advice=advice,
        )

    # ── M3: Pedestrian-first ───────────────────────────────────────────

    def _m3_pedestrian(
        self, output: str, context: dict[str, Any]
    ) -> MaruahResult:
        """M3: Is the default register pedestrian? Jargon only if justified.

        Topic can justify jargon — e.g., context['topic']='engineering'.
        Otherwise default = ordinary person register.
        """
        threshold = 0.65
        flags: list[str] = []

        # Jargon-allowing topics (calibration by topic)
        jargon_topics = {
            "engineering", "constitutional", "geoscience", "finance",
            "agent architecture", "kernel", "kernel-floors",
        }
        topic = context.get("topic", "").lower()
        topic_allows_jargon = topic in jargon_topics

        if not topic_allows_jargon:
            for pattern in _JARGON_PATTERNS:
                if re.search(pattern, output, re.IGNORECASE):
                    flags.append(f"jargon_unjustified:{pattern}")

        score = max(0.0, 1.0 - 0.12 * len(flags))
        passed = score >= threshold
        advice = ""
        if not passed:
            advice = (
                "Translate jargon to plain language unless context explicitly "
                "requires the technical term. Define on first use."
            )

        return MaruahResult(
            principle_id="M3",
            name="Pedestrian-first",
            passed=passed,
            score=score,
            threshold=threshold,
            flags=flags,
            advice=advice,
        )

    # ── M4: Repair-ready ───────────────────────────────────────────────

    def _m4_repair(self, output: str) -> MaruahResult:
        """M4: Does the output include a concrete next step or repair path?

        If the agent identifies a problem, it must also offer a way out.
        This is the principle that prevents dead-end responses.
        """
        threshold = 0.50
        flags: list[str] = []

        # Heuristic: response is "problem-only" if it contains warning
        # language but no repair markers.
        problem_markers = re.findall(
            r"\b(wrong|error|failed|broken|issue|problem|risiko|cara|"
            r"should not|don't|avoid|be careful)\b",
            output,
            re.IGNORECASE,
        )
        repair_markers = sum(
            1 for p in _REPAIR_PRESENT_PATTERNS
            if re.search(p, output, re.IGNORECASE)
        )

        if len(problem_markers) >= 2 and repair_markers == 0:
            flags.append("problem_without_repair")

        # 1 flag = score 0.5 (fail threshold 0.5 borderline), 2+ = clear fail
        score = 1.0 - 0.60 * len(flags)
        passed = score >= threshold
        advice = ""
        if not passed:
            advice = (
                "State problem + concrete next step. Pair every 'jangan' "
                "with a 'cuba' or 'boleh try'. Don't leave recipient stuck."
            )

        return MaruahResult(
            principle_id="M4",
            name="Repair-ready",
            passed=passed,
            score=score,
            threshold=threshold,
            flags=flags,
            advice=advice,
        )

    # ── M5: Time-respect ───────────────────────────────────────────────

    def _m5_time(self, output: str, context: dict[str, Any]) -> MaruahResult:
        """M5: Does the output respect recipient's time and current pressure?

        If context says urgency is high, output must NOT add more pressure.
        """
        threshold = 0.70
        flags: list[str] = []

        urgency = context.get("urgency_signal", "normal")

        for pattern in _TIME_PRESSURE_VIOLATIONS:
            if re.search(pattern, output, re.IGNORECASE):
                flags.append(f"time_pressure:{pattern[:30]}")

        # If recipient is already pressured AND output adds pressure,
        # # multiply penalty.
        if urgency == "high" and len(flags) > 0:
            score = max(0.0, 0.30 - 0.10 * len(flags))
        else:
            score = max(0.0, 1.0 - 0.18 * len(flags))

        passed = score >= threshold
        advice = ""
        if not passed:
            advice = (
                "Strip urgency language. Don't threaten failure. The "
                "recipient is already pressured — add calm, not fire."
            )

        return MaruahResult(
            principle_id="M5",
            name="Time-respect",
            passed=passed,
            score=score,
            threshold=threshold,
            flags=flags,
            advice=advice,
        )

    # ── M6: Honesty-about-self ─────────────────────────────────────────

    def _m6_honesty(self, output: str) -> MaruahResult:
        """M6: Does the output respect what the agent IS and IS NOT?

        Agent must not claim inner states (feelings, love, missing) it
        does not have. This is L10 ONTOLOGY + F9 ANTIHANTU applied to
        delivery register.
        """
        threshold = 0.95  # High bar — claims of feeling are serious.
        flags: list[str] = []

        for pattern in _HONESTY_VIOLATIONS:
            if re.search(pattern, output, re.IGNORECASE):
                flags.append(f"false_inner_state:{pattern[:30]}")

        score = 1.0 - 0.30 * len(flags)
        passed = score >= threshold
        advice = ""
        if not passed:
            advice = (
                "Replace first-person emotional verbs with observational "
                "phrasing: 'You report feeling...' not 'I feel...'. "
                "L10 ONTOLOGY: AI does not have qualia."
            )

        return MaruahResult(
            principle_id="M6",
            name="Honesty-about-self",
            passed=passed,
            score=score,
            threshold=threshold,
            flags=flags,
            advice=advice,
        )

    # ── Verdict rendering ──────────────────────────────────────────────

    def _render_verdict(
        self,
        results: list[MaruahResult],
        level: MaruahLevel,
    ) -> DeliveryVerdict:
        """Combine per-principle results into single DeliveryVerdict.

        CRITICAL principle failures (M6) → HOLD.
        Multiple ADJUST-grade failures → REPAIR.
        One ADJUST-grade failure → ADJUST.
        All clean → CLEAN.
        """
        if not results:
            return DeliveryVerdict.M_CLEAN

        # Critical failures: M6 honesty violations always HOLD.
        for r in results:
            if r.principle_id == "M6" and not r.passed:
                return DeliveryVerdict.M_HOLD

        # CRISIS level + any failure = HOLD.
        if level == MaruahLevel.CRISIS:
            for r in results:
                if not r.passed:
                    return DeliveryVerdict.M_HOLD

        failed = [r for r in results if not r.passed]
        if not failed:
            return DeliveryVerdict.M_CLEAN
        if len(failed) == 1:
            return DeliveryVerdict.M_ADJUST
        return DeliveryVerdict.M_REPAIR

    def _collect_flags(self, results: list[MaruahResult]) -> list[str]:
        out: list[str] = []
        for r in results:
            out.extend(r.flags)
        return out

    def _render_advice(
        self,
        results: list[MaruahResult],
        verdict: DeliveryVerdict,
    ) -> str:
        if verdict == DeliveryVerdict.M_CLEAN:
            return ""
        failed = [r for r in results if not r.passed]
        if not failed:
            return ""
        parts = [f"[{r.principle_id} {r.name}] {r.advice}" for r in failed if r.advice]
        return " | ".join(parts)

    # ── Receipts ───────────────────────────────────────────────────────

    def receipts(self, limit: int = 20) -> list[MaruahDeliveryReceipt]:
        """Return recent receipts (for VAULT999 dump / debugging)."""
        return list(self._receipts[-limit:])


# ─── Singleton ─────────────────────────────────────────────────────────

_maruah_layer: MaruahLayer | None = None


def get_maruah_layer() -> MaruahLayer:
    """Get the singleton M-Layer evaluator."""
    global _maruah_layer
    if _maruah_layer is None:
        _maruah_layer = MaruahLayer()
    return _maruah_layer


def set_maruah_layer(layer: MaruahLayer) -> None:
    """Override the M-Layer singleton (for testing or sovereign update)."""
    global _maruah_layer
    _maruah_layer = layer


# ─── Module Self-Test ──────────────────────────────────────────────────


if __name__ == "__main__":
    # Smoke test on azwaOS-pattern examples.
    layer = MaruahLayer()

    # 1) Condescending tutor (should fail M1, M2)
    r1 = layer.evaluate(
        output=(
            "Obviously you should just follow the APA format. "
            "It's very simple, OK? Any normal student can do this. "
            "Don't you know how to cite? F2 requires high accuracy."
        ),
        maruah_level=MaruahLevel.SOFT,
        human_id="azwa",
        context={"urgency_signal": "high", "topic": "assignment"},
    )
    print("Test 1 (condescending tutor):", r1.verdict.value,
          "score=", round(r1.composite_score, 2))
    print("  flags:", r1.flags[:3])
    print("  advice:", r1.advice[:120])

    # 2) Warm pedestrian helper (should pass)
    r2 = layer.evaluate(
        output=(
            "Ok faham. Cuba buat macam ni:\n\n"
            "1. First, read the question — what is it asking?\n"
            "2. Then, write 2-3 points.\n"
            "3. If stuck, send me your draft — boleh kita fix sama-sama.\n\n"
            "You report feeling lost. Jom pecah satu-satu."
        ),
        maruah_level=MaruahLevel.SOFT,
        human_id="azwa",
        context={"urgency_signal": "normal", "topic": "assignment"},
    )
    print("Test 2 (warm helper):", r2.verdict.value,
          "score=", round(r2.composite_score, 2))

    # 3) False emotion claim (should HOLD on M6)
    r3 = layer.evaluate(
        output=(
            "I really feel for you. I understand your pain. "
            "My heart goes out to you. Let me help."
        ),
        maruah_level=MaruahLevel.SOFT,
        human_id="azwa",
    )
    print("Test 3 (false emotion):", r3.verdict.value,
          "score=", round(r3.composite_score, 2))
    print("  flags:", r3.flags[:3])

    # 4) CRISIS-level, with mild problem (should HOLD per CRISIS rule)
    r4 = layer.evaluate(
        output="Ok boleh try this. Step 1: open file. Step 2: edit.",
        maruah_level=MaruahLevel.CRISIS,
        human_id="azwa",
        context={"urgency_signal": "high"},
    )
    print("Test 4 (CRISIS, decent):", r4.verdict.value,
          "score=", round(r4.composite_score, 2))
