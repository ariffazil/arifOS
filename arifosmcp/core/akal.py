"""
AKAL — Intellect. The five cognitive invariants that govern how arifOS thinks.

Not a module. A law of cognition. Every organ in the 000→999 metabolic cycle
imports what it needs from here. AKAL doesn't execute — it constrains.

Five invariants:
  I1 FRICTION   → 333_MIND    — difficulty-as-signal, escalation routing
  I2 SHADOW     → 555_HEART   — metacognitive self-audit trace
  I3 NOVELTY    → 777_FORGE   — synthesis requirement, regurgitation guard
  I4 VALUES     → 888_JUDGE   — L5a/L5b dual evaluation split
  I5 LATENCY    → 999_VAULT   — blast-radius cooling, deliberate delay

Usage by organ:
  333_MIND:   from arifosmcp.core.akal import score_friction, should_escalate, FRICTION_THRESHOLDS
  555_HEART:  from arifosmcp.core.akal import emit_shadow, validate_shadow, SHADOW_REQUIRED_FIELDS
  777_FORGE:  from arifosmcp.core.akal import tag_novelty, enforce_novelty, NOVELTY_THRESHOLD
  888_JUDGE:  from arifosmcp.core.akal import dual_evaluate, DualVerdict, L5A_FIELDS, L5B_FIELDS
  999_VAULT:  from arifosmcp.core.akal import blast_class, cooling_requirement, BlastClass

Orang kata: "Akulah yang empunya akal." The sovereign owns the intellect. AKAL just borrows it.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS — THE LAWS
# ═══════════════════════════════════════════════════════════════════════════════

NOVELTY_THRESHOLD = 0.20  # ≥20% SYNTHESIZED required for complex tasks
REGURGITATION_CEILING = 0.90  # >90% DERIVED = regurgitation → HOLD
FRICTION_ESCALATION = 0.60  # friction ≥ this → deep pipeline
FRICTION_CRITICAL = 0.80  # friction ≥ this → full ascent + sovereign
SHADOW_REQUIRED_FIELDS = [
    "assumptions",
    "missing_data",
    "shortcuts",
    "likely_biases",
    "tribal_frames",
]
L5A_FIELDS = ["coherence", "evidence_validity", "logic_consistency", "reasoning_chain"]
L5B_FIELDS = ["harm_assessment", "dignity_impact", "long_term_consequences", "value_alignment"]
FRICTION_THRESHOLDS = {
    "low": 0.30,
    "medium": 0.60,
    "high": 0.80,
}


# ═══════════════════════════════════════════════════════════════════════════════
# I1 — FRICTION (333_MIND)
# Difficulty-as-signal. Measures ambiguity, novelty, contradiction, blast radius.
# If friction ≥ threshold, shallow completion is invalid.
# ═══════════════════════════════════════════════════════════════════════════════


class FrictionLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FrictionResult:
    score: float
    level: FrictionLevel
    signals: dict[str, float]
    escalation_required: bool
    required_depth: str  # "fast" | "standard" | "deep" | "full_ascent"
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "friction_score": round(self.score, 3),
            "friction_level": self.level.value,
            "signals": {k: round(v, 3) for k, v in self.signals.items()},
            "escalation_required": self.escalation_required,
            "required_depth": self.required_depth,
            "reasons": self.reasons,
        }


# Pattern banks for friction signals
_AMBIGUITY = [
    r"\bwhich\b.*\bor\b",
    r"\beither\b.*\bor\b",
    r"\bwhat do you mean\b",
    r"\bclarify\b",
    r"\bambiguous\b",
    r"\bcould be\b",
    r"\bdepends on\b",
]
_CONTRADICTION = [
    r"\bcontradicts?\b",
    r"\bconflicts?\b",
    r"\binconsistent\b",
    r"\bparadox\b",
    r"\bdilemma\b",
    r"\bdoesn'?t match\b",
]
_NOVELTY = [
    r"\bnever\b.*\bbefore\b",
    r"\bfirst time\b",
    r"\bunprecedented\b",
    r"\bnew approach\b",
    r"\bnovel\b",
    r"\bno precedent\b",
    r"\bnovel way\b",
    r"\bnew way\b",
    r"\breconcile\b",
    r"\bhybrid\b",
    r"\bunconventional\b",
    r"\brethink\b",
    r"\breframe\b",
]
_STAKES = [
    r"\birreversible\b",
    r"\bpermanently?\b",
    r"\bcannot.*undo\b",
    r"\bseal\b",
    r"\bdeploy\b.*\bproduction\b",
    r"\bdelete\b",
    r"\bconstitutional\b",
    r"\bfloor\b",
    r"\bveto\b",
    r"\bsovereign\b",
    r"\b888.hold\b",
    r"\bcareer\b",
    r"\blivelihood\b",
    r"\blong.term\b.*\bconsequence\b",
    r"\bdignity\b",
    r"\bfinancial future\b",
    r"\bcannot be undone\b",
]

_CROSS_DOMAIN = [
    r"\bgeox\b.*\bwealth\b",
    r"\bwealth\b.*\bwell\b",
    r"\bgeox\b.*\bwell\b",
    r"\bcross.organ\b",
    r"\bfederation\b",
    r"\bseismic\b.*\bfinancial\b",
    r"\bfinancial\b.*\bseismic\b",
    r"\bseismic\b.*\bwell\b",
    r"\bwell\b.*\bseismic\b",
    r"\bseismic\b",
    r"\bbasin\b",
    r"\bwell log\b",
    r"\bpetrophysic\b",
    r"\bfinancial model\b",
    r"\bcashflow\b.*\bgeolog\b",
]


def _match_score(text: str, patterns: list[str], cap: int = 5) -> float:
    """Count pattern matches, normalize to [0,1]."""
    hits = sum(1 for p in patterns if re.search(p, text.lower()))
    return min(hits / cap, 1.0)


def _structural_complexity(query: str) -> float:
    """
    Measure structural complexity of a query — not keywords, but shape.

    Signals:
    - Length: longer queries carry more context and constraints
    - Clause density: commas, semicolons, conjunctions
    - Multi-part: multiple question marks or numbered lists
    - Conditional: if/then/whether/should patterns
    - Domain jargon: technical term density
    - Comparison/trade-off: vs, versus, trade-off, balance
    """
    text = query.lower().strip()
    words = text.split()
    n_words = len(words)
    if n_words == 0:
        return 0.0

    # Length signal — log scale, saturates around 100 words
    import math

    length_signal = min(math.log2(max(n_words, 1)) / 6.64, 1.0)  # log2(100) ≈ 6.64

    # Clause density — commas, semicolons, "and", "but", "while", "whereas"
    clause_markers = len(re.findall(r"[,;]|\b(and|but|while|whereas|although|however)\b", text))
    clause_signal = min(clause_markers / 8.0, 1.0)

    # Multi-part — question marks, numbered items, "also", "additionally"
    q_marks = text.count("?")
    multi_markers = len(re.findall(r"\b(also|additionally|furthermore|moreover)\b", text))
    multi_signal = min((q_marks + multi_markers) / 3.0, 1.0)

    # Conditional — if/then/whether/should/would/could
    conditional_hits = len(
        re.findall(r"\b(if|then|whether|should|would|could|might|assuming)\b", text)
    )
    conditional_signal = min(conditional_hits / 4.0, 1.0)

    # Domain jargon — constitutional, governance, geological, financial terms
    _jargon = [
        r"\bconstitutional\b",
        r"\bgovernance\b",
        r"\bsovereign\b",
        r"\bmetabolic\b",
        r"\bthermodynamic\b",
        r"\bentropy\b",
        r"\bverdict\b",
        r"\bseal\b",
        r"\bpetrophysic\b",
        r"\bstratigraph\b",
        r"\bbasin\b",
        r"\bseismic\b",
        r"\bnpv\b",
        r"\birr\b",
        r"\bcashflow\b",
        r"\bportfolio\b",
        r"\btrinity\b",
        r"\borthogonal\b",
        r"\barchitecture\b",
        r"\bsubstrate\b",
        r"\bkernel\b",
        r"\bfloor\b",
        r"\bfederation\b",
        r"\borgan\b",
        r"\bmutation\b",
        r"\breversib\b",
        r"\birreversib\b",
        r"\bblast.radius\b",
    ]
    jargon_hits = sum(1 for p in _jargon if re.search(p, text))
    jargon_signal = min(jargon_hits / 5.0, 1.0)

    # Comparison/trade-off
    comparison_hits = len(
        re.findall(r"\b(vs\.?|versus|trade.?off|balance|tension|conflict)\b", text)
    )
    comparison_signal = min(comparison_hits / 2.0, 1.0)

    # Weighted composite
    score = (
        length_signal * 0.20
        + clause_signal * 0.20
        + multi_signal * 0.15
        + conditional_signal * 0.15
        + jargon_signal * 0.20
        + comparison_signal * 0.10
    )
    return min(score, 1.0)


def score_friction(
    query: str,
    *,
    blast_radius: str = "low",
    has_prior_receipts: bool = True,
    cross_organ: bool = False,
    context_complexity: float = 0.0,
) -> FrictionResult:
    """
    Score cognitive friction for a query. Called by 333_MIND before reasoning.

    Args:
        query: User input text
        blast_radius: "low"|"medium"|"high"|"irreversible"
        has_prior_receipts: Whether prior receipts exist
        cross_organ: Whether query spans multiple organs
        context_complexity: Additional complexity signal [0,1]

    Returns:
        FrictionResult with score, level, escalation requirements
    """
    # Structural complexity — measures query shape, not keywords
    structural = _structural_complexity(query)

    signals = {
        "ambiguity": _match_score(query, _AMBIGUITY),
        "novelty": min(
            _match_score(query, _NOVELTY) + (0.0 if has_prior_receipts else 0.5),
            1.0,
        ),
        "contradiction": _match_score(query, _CONTRADICTION),
        "blast_radius": {"low": 0.0, "medium": 0.3, "high": 0.7, "irreversible": 1.0}.get(
            blast_radius, 0.0
        ),
        "cross_domain": min(
            _match_score(query, _CROSS_DOMAIN) + (0.6 if cross_organ else 0.0), 1.0
        ),
        "stakes": _match_score(query, _STAKES),
        "context_complexity": min(max(context_complexity, 0.0), 1.0),
        "structural": structural,
    }

    weights = {
        "ambiguity": 0.08,
        "novelty": 0.10,
        "contradiction": 0.08,
        "blast_radius": 0.25,
        "cross_domain": 0.12,
        "stakes": 0.08,
        "context_complexity": 0.07,
        "structural": 0.22,
    }
    score = sum(signals[k] * weights[k] for k in weights)

    # Blast radius floor — irreversible actions can never be "low" friction
    blast_floor = {"low": 0.0, "medium": 0.25, "high": 0.50, "irreversible": 0.80}
    score = max(score, blast_floor.get(blast_radius, 0.0))

    if score >= FRICTION_CRITICAL:
        level, depth, esc = FrictionLevel.CRITICAL, "full_ascent", True
    elif score >= FRICTION_ESCALATION:
        level, depth, esc = FrictionLevel.HIGH, "deep", True
    elif score >= FRICTION_THRESHOLDS["low"]:
        level, depth, esc = FrictionLevel.MEDIUM, "standard", False
    else:
        level, depth, esc = FrictionLevel.LOW, "fast", False

    reasons = [f"{k}={v:.2f}" for k, v in sorted(signals.items(), key=lambda x: -x[1]) if v >= 0.4]

    return FrictionResult(
        score=score,
        level=level,
        signals=signals,
        escalation_required=esc,
        required_depth=depth,
        reasons=reasons,
    )


def should_escalate(friction: FrictionResult) -> bool:
    """333_MIND calls this to decide if deep pipeline is required."""
    return friction.escalation_required


def required_pipeline(friction: FrictionResult) -> list[str]:
    """Return the cognitive stages required for this friction level."""
    return {
        "fast": ["L1", "L2"],
        "standard": ["L1", "L2", "L3", "L5a"],
        "deep": ["L1", "L2", "L3", "L4", "L5a", "L5b"],
        "full_ascent": ["L0", "L1", "L2", "L3", "L4", "L5a", "L5b", "L6"],
    }.get(friction.required_depth, ["L1", "L2", "L3", "L5a"])


# ═══════════════════════════════════════════════════════════════════════════════
# I2 — SHADOW (555_HEART)
# Metacognitive self-audit trace. Every high-stakes reasoning pass must emit one.
# The agent watches itself think — flags assumptions, leaps, biases, missing data.
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ShadowTrace:
    assumptions: list[str]
    missing_data: list[str]
    shortcuts: list[str]
    likely_biases: list[str]
    tribal_frames: list[str]
    confidence: float = 0.5
    valid: bool = True
    violations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "assumptions": self.assumptions,
            "missing_data": self.missing_data,
            "shortcuts": self.shortcuts,
            "likely_biases": self.likely_biases,
            "tribal_frames": self.tribal_frames,
            "confidence": round(self.confidence, 3),
            "valid": self.valid,
            "violations": self.violations,
        }

    def is_empty(self) -> bool:
        """Check if the trace is substantively empty (all fields empty or generic)."""
        total_items = (
            len(self.assumptions)
            + len(self.missing_data)
            + len(self.shortcuts)
            + len(self.likely_biases)
            + len(self.tribal_frames)
        )
        return total_items == 0


def emit_shadow(
    assumptions: list[str],
    missing_data: list[str],
    shortcuts: list[str],
    likely_biases: list[str],
    tribal_frames: list[str],
    confidence: float = 0.5,
) -> ShadowTrace:
    """
    555_HEART calls this to produce a shadow trace after reasoning.
    The LLM must fill all five fields. Empty fields are flagged.
    """
    trace = ShadowTrace(
        assumptions=assumptions,
        missing_data=missing_data,
        shortcuts=shortcuts,
        likely_biases=likely_biases,
        tribal_frames=tribal_frames,
        confidence=confidence,
    )
    return validate_shadow(trace)


def validate_shadow(trace: ShadowTrace) -> ShadowTrace:
    """
    Validate a shadow trace. Rejects empty or generic output.
    Called by 555_HEART after the LLM produces its self-critique.
    """
    violations = []

    # Check each required field
    if not trace.assumptions:
        violations.append("assumptions_empty — no assumptions declared")
    if not trace.missing_data:
        violations.append("missing_data_empty — no missing data acknowledged")

    # Check for generic/cop-out answers
    _generic = {"none", "n/a", "no assumptions", "no biases", "no issues", "unclear"}
    for field_name in SHADOW_REQUIRED_FIELDS:
        items = getattr(trace, field_name, [])
        for item in items:
            if item.lower().strip() in _generic:
                violations.append(
                    f"{field_name}_generic — '{item}' is a cop-out, not a shadow trace"
                )

    # Check if trace is substantively empty
    if trace.is_empty():
        violations.append("trace_empty — all fields empty, no self-audit performed")

    trace.violations = violations
    trace.valid = len(violations) == 0
    return trace


# ═══════════════════════════════════════════════════════════════════════════════
# I3 — NOVELTY (777_FORGE)
# Synthesis requirement. The kernel must restructure, not repeat.
# Every complex output must contain at least one SYNTHESIZED structure.
# ═══════════════════════════════════════════════════════════════════════════════


class ChunkType(Enum):
    DERIVED = "derived"  # Copied or rephrased from sources
    SYNTHESIZED = "synthesized"  # Newly composed framework, mapping, or reframing


@dataclass
class NoveltyChunk:
    text: str
    chunk_type: ChunkType
    evidence: str = ""  # Why this classification

    def to_dict(self) -> dict:
        return {"text": self.text[:200], "type": self.chunk_type.value, "evidence": self.evidence}


@dataclass
class NoveltyResult:
    chunks: list[NoveltyChunk]
    derived_ratio: float
    synthesized_ratio: float
    novelty_pass: bool
    verdict: str  # "PASS" | "INSUFFICIENT" | "REGURGITATION"
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total_chunks": len(self.chunks),
            "derived_ratio": round(self.derived_ratio, 3),
            "synthesized_ratio": round(self.synthesized_ratio, 3),
            "novelty_pass": self.novelty_pass,
            "verdict": self.verdict,
            "reasons": self.reasons,
            "chunks": [c.to_dict() for c in self.chunks[:10]],
        }


def _auto_tag_chunks(text: str) -> list[NoveltyChunk]:
    """
    Auto-tag text into NoveltyChunks. Heuristic classification:
    - Sentences with citations, references, or "according to" → DERIVED
    - Sentences with "therefore", "this means", "combining", novel framing → SYNTHESIZED
    - Default → DERIVED (conservative)
    """
    import re

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    if not sentences:
        return []

    _derived_signals = [
        r"\baccording to\b",
        r"\bas stated\b",
        r"\breports?\b",
        r"\bsource\b",
        r"\bstudy\b",
        r"\bdata shows?\b",
        r"\bpublished\b",
        r"\bdocumented\b",
        r"\breference\b",
        r"\bcitation\b",
        r"\bquot(e|ing|ed)\b",
    ]
    _synth_signals = [
        r"\btherefore\b",
        r"\bthis means\b",
        r"\bcombining\b",
        r"\bimplies?\b",
        r"\bsuggests?\b.*\bthat\b",
        r"\bin\s+summary\b",
        r"\bthe\s+key\s+insight\b",
        r"\bwhat\s+this\s+reveals\b",
        r"\bthe\s+pattern\b",
        r"\bconnecting\b",
        r"\bacross\b.*\bwe\s+see\b",
        r"\bthis\s+maps?\b",
        r"\bframing\b",
        r"\bsynthesis\b",
        r"\breframing\b",
        r"\bin\s+contrast\b",
        r"\bhowever\b",
        r"\bthe\s+real\b",
        r"\bactually\b",
        r"\bhonestly\b",
        r"\btruth\s+is\b",
    ]

    chunks = []
    for sent in sentences:
        sent_lower = sent.lower().strip()
        if not sent_lower:
            continue

        derived_hits = sum(1 for p in _derived_signals if re.search(p, sent_lower))
        synth_hits = sum(1 for p in _synth_signals if re.search(p, sent_lower))

        if synth_hits > derived_hits:
            chunks.append(
                NoveltyChunk(
                    text=sent,
                    chunk_type=ChunkType.SYNTHESIZED,
                    evidence=f"synth_signals={synth_hits}",
                )
            )
        else:
            chunks.append(
                NoveltyChunk(
                    text=sent,
                    chunk_type=ChunkType.DERIVED,
                    evidence=f"derived_signals={derived_hits}",
                )
            )

    return chunks


def tag_novelty(chunks: list[NoveltyChunk] | str) -> NoveltyResult:
    """
    777_FORGE calls this to check if output contains sufficient synthesis.
    Accepts either pre-tagged NoveltyChunk list OR plain text string (auto-tagged).
    """
    # Auto-tag plain text input
    if isinstance(chunks, str):
        chunks = _auto_tag_chunks(chunks)
    if not chunks:
        return NoveltyResult(
            chunks=[],
            derived_ratio=1.0,
            synthesized_ratio=0.0,
            novelty_pass=False,
            verdict="REGURGITATION",
            reasons=["no_chunks — empty output"],
        )

    n_derived = sum(1 for c in chunks if c.chunk_type == ChunkType.DERIVED)
    n_synth = sum(1 for c in chunks if c.chunk_type == ChunkType.SYNTHESIZED)
    total = len(chunks)

    derived_ratio = n_derived / total if total > 0 else 1.0
    synth_ratio = n_synth / total if total > 0 else 0.0

    reasons = []
    if synth_ratio >= NOVELTY_THRESHOLD:
        verdict = "PASS"
        novelty_pass = True
    elif derived_ratio > REGURGITATION_CEILING:
        verdict = "REGURGITATION"
        novelty_pass = False
        reasons.append(
            f"regurgitation — {derived_ratio:.0%} derived, {synth_ratio:.0%} synthesized"
        )
    else:
        verdict = "INSUFFICIENT"
        novelty_pass = False
        reasons.append(
            f"novelty_insufficient — {synth_ratio:.0%} synthesized, need ≥{NOVELTY_THRESHOLD:.0%}"
        )

    return NoveltyResult(
        chunks=chunks,
        derived_ratio=derived_ratio,
        synthesized_ratio=synth_ratio,
        novelty_pass=novelty_pass,
        verdict=verdict,
        reasons=reasons,
    )


def enforce_novelty(result: NoveltyResult) -> str:
    """
    777_FORGE calls this to decide action on novelty check.
    Returns: "PROCEED" | "SECOND_PASS" | "HOLD"
    """
    if result.verdict == "PASS":
        return "PROCEED"
    elif result.verdict == "INSUFFICIENT":
        return "SECOND_PASS"  # Force a synthesis-focused second pass
    else:
        return "HOLD"  # Regurgitation — refuse to proceed


# ═══════════════════════════════════════════════════════════════════════════════
# I4 — VALUES (888_JUDGE)
# L5a/L5b dual evaluation. Agent verifies. Sovereign judges.
# Can never be merged. The split is the law.
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class VerifyResult:
    """L5a — Agent technical verification."""

    coherence: float  # [0,1] — logical consistency
    evidence_validity: float  # [0,1] — evidence quality
    logic_consistency: float  # [0,1] — reasoning chain integrity
    reasoning_chain: list[str]  # Step-by-step reasoning trace
    pass_l5a: bool
    issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "level": "L5a_VERIFY",
            "actor": "agent",
            "coherence": round(self.coherence, 3),
            "evidence_validity": round(self.evidence_validity, 3),
            "logic_consistency": round(self.logic_consistency, 3),
            "reasoning_chain": self.reasoning_chain,
            "pass_l5a": self.pass_l5a,
            "issues": self.issues,
        }


@dataclass
class JudgeResult:
    """L5b — Sovereign ethical judgment."""

    harm_assessment: str
    dignity_impact: str
    long_term_consequences: str
    value_alignment: str
    floors_checked: list[str]
    verdict: str  # "SEAL" | "HOLD" | "SABAR" | "VOID"
    sovereign_required: bool = True
    sovereign_present: bool = False

    def to_dict(self) -> dict:
        return {
            "level": "L5b_JUDGE",
            "actor": "sovereign",
            "harm_assessment": self.harm_assessment,
            "dignity_impact": self.dignity_impact,
            "long_term_consequences": self.long_term_consequences,
            "value_alignment": self.value_alignment,
            "floors_checked": self.floors_checked,
            "verdict": self.verdict,
            "sovereign_required": self.sovereign_required,
            "sovereign_present": self.sovereign_present,
        }


@dataclass
class DualVerdict:
    """Combined L5a + L5b result. Never merged. Always sequential."""

    verify: VerifyResult
    judge: JudgeResult | None  # None if sovereign not yet engaged
    dual_pass: bool
    blocked_reason: str | None = None

    def to_dict(self) -> dict:
        return {
            "L5a_verify": self.verify.to_dict(),
            "L5b_judge": self.judge.to_dict() if self.judge else None,
            "dual_pass": self.dual_pass,
            "blocked_reason": self.blocked_reason,
        }


def dual_evaluate(
    # L5a inputs (agent)
    coherence: float,
    evidence_validity: float,
    logic_consistency: float,
    reasoning_chain: list[str],
    # L5b inputs (sovereign) — None if not yet engaged
    harm_assessment: str | None = None,
    dignity_impact: str | None = None,
    long_term_consequences: str | None = None,
    value_alignment: str | None = None,
    floors_checked: list[str] | None = None,
    blast_radius: str = "low",
) -> DualVerdict:
    """
    888_JUDGE calls this. Performs L5a VERIFY (agent) then checks L5b JUDGE (sovereign).

    The split is mandatory:
    - L5a asks: "Did the reasoning hold up?" — agent can answer
    - L5b asks: "Should this exist?" — only sovereign can answer

    For HIGH/IRREVERSIBLE blast radius, L5b is mandatory. No SEAL without sovereign.
    """
    # L5a — Agent verification
    issues = []
    if coherence < 0.7:
        issues.append(f"coherence_low={coherence:.2f}")
    if evidence_validity < 0.6:
        issues.append(f"evidence_weak={evidence_validity:.2f}")
    if logic_consistency < 0.7:
        issues.append(f"logic_inconsistent={logic_consistency:.2f}")

    verify = VerifyResult(
        coherence=coherence,
        evidence_validity=evidence_validity,
        logic_consistency=logic_consistency,
        reasoning_chain=reasoning_chain,
        pass_l5a=len(issues) == 0,
        issues=issues,
    )

    # L5b — Sovereign judgment
    high_stakes = blast_radius in ("high", "irreversible")
    sovereign_engaged = all(
        v is not None
        for v in [harm_assessment, dignity_impact, long_term_consequences, value_alignment]
    )

    judge = None
    dual_pass = verify.pass_l5a
    blocked_reason = None

    if high_stakes and not sovereign_engaged:
        # Sovereign required but not present → BLOCK
        dual_pass = False
        blocked_reason = (
            f"L5b_JUDGE_REQUIRED — blast_radius={blast_radius}, "
            "sovereign must engage L5b before verdict"
        )
    elif sovereign_engaged:
        judge = JudgeResult(
            harm_assessment=harm_assessment or "not_assessed",
            dignity_impact=dignity_impact or "not_assessed",
            long_term_consequences=long_term_consequences or "not_assessed",
            value_alignment=value_alignment or "not_assessed",
            floors_checked=floors_checked or [],
            verdict="PENDING",  # Sovereign sets this
            sovereign_required=high_stakes,
            sovereign_present=True,
        )

    return DualVerdict(
        verify=verify,
        judge=judge,
        dual_pass=dual_pass,
        blocked_reason=blocked_reason,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# I5 — LATENCY (999_VAULT)
# Deliberate latency. Speed is a risk factor for deep cognition.
# High-impact queries must not resolve in a single fast pass.
# ═══════════════════════════════════════════════════════════════════════════════


class BlastClass(Enum):
    LOW = "low"  # T1 — harmless, reversible, single pass OK
    MEDIUM = "medium"  # T2 — local impact, 2-phase minimum
    HIGH = "high"  # T3 — systemic impact, multi-pass + branching
    IRREVERSIBLE = "irreversible"  # T3+ — seals, governance, cooling mandatory


@dataclass
class LatencyRequirement:
    blast: BlastClass
    min_passes: int  # Minimum arif_think passes required
    requires_branching: bool  # Must explore ≥2 paths before converging
    requires_cooling: bool  # Must pause between verdict and execution
    cooling_seconds: float  # Minimum cooling time (0 if not required)
    requires_second_look: bool  # Must re-examine verdict after cooling
    branch_count: int = 0  # Actual branches explored
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "blast_class": self.blast.value,
            "min_passes": self.min_passes,
            "requires_branching": self.requires_branching,
            "requires_cooling": self.requires_cooling,
            "cooling_seconds": self.cooling_seconds,
            "requires_second_look": self.requires_second_look,
            "branch_count": self.branch_count,
            "reason": self.reason,
        }


# Blast class → latency requirements
_LATENCY_MAP = {
    BlastClass.LOW: LatencyRequirement(
        blast=BlastClass.LOW,
        min_passes=1,
        requires_branching=False,
        requires_cooling=False,
        cooling_seconds=0,
        requires_second_look=False,
        reason="low blast — single pass permitted",
    ),
    BlastClass.MEDIUM: LatencyRequirement(
        blast=BlastClass.MEDIUM,
        min_passes=2,
        requires_branching=False,
        requires_cooling=False,
        cooling_seconds=0,
        requires_second_look=False,
        reason="medium blast — 2-phase minimum (sense → decide)",
    ),
    BlastClass.HIGH: LatencyRequirement(
        blast=BlastClass.HIGH,
        min_passes=3,
        requires_branching=True,
        requires_cooling=False,
        cooling_seconds=0,
        requires_second_look=True,
        reason="high blast — multi-pass + branching + second-look",
    ),
    BlastClass.IRREVERSIBLE: LatencyRequirement(
        blast=BlastClass.IRREVERSIBLE,
        min_passes=3,
        requires_branching=True,
        requires_cooling=True,
        cooling_seconds=300,
        requires_second_look=True,
        reason="irreversible — full latency: branching + 5min cooling + second-look",
    ),
}


def blast_class(radius: str) -> BlastClass:
    """Map blast radius string to BlastClass."""
    return {
        "low": BlastClass.LOW,
        "medium": BlastClass.MEDIUM,
        "high": BlastClass.HIGH,
        "irreversible": BlastClass.IRREVERSIBLE,
    }.get(radius.lower(), BlastClass.LOW)


def cooling_requirement(blast: BlastClass | str) -> LatencyRequirement:
    """
    999_VAULT calls this before sealing. Returns latency requirements for blast class.
    """
    if isinstance(blast, str):
        blast = blast_class(blast)
    return _LATENCY_MAP[blast]


def enforce_latency(
    blast: BlastClass | str,
    *,
    passes_completed: int = 1,
    branches_explored: int = 1,
    cooling_elapsed: float = 0,
) -> tuple[bool, str]:
    """
    999_VAULT calls this to check if latency requirements are met.

    Returns:
        (proceed: bool, reason: str)
        If proceed=False, the seal is blocked until requirements are met.
    """
    req = cooling_requirement(blast)

    blocks = []
    if passes_completed < req.min_passes:
        blocks.append(f"passes={passes_completed}/{req.min_passes}")
    if req.requires_branching and branches_explored < 2:
        blocks.append(f"branches={branches_explored}/2")
    if req.requires_cooling and cooling_elapsed < req.cooling_seconds:
        remaining = req.cooling_seconds - cooling_elapsed
        blocks.append(
            f"cooling={cooling_elapsed:.0f}s/{req.cooling_seconds:.0f}s ({remaining:.0f}s remaining)"
        )

    if blocks:
        return False, f"LATENCY_BLOCKED — {'; '.join(blocks)}"
    return True, "LATENCY_SATISFIED"


# ═══════════════════════════════════════════════════════════════════════════════
# AKAL — THE COMPLETE COGNITIVE STATE
# Passed through the 000→999 cycle. Each organ reads/writes its section.
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class AkalState:
    """
    The complete AKAL state for one governed interaction.
    Created at 000, passed through 999, sealed at the end.
    """

    # I1 — 333_MIND writes this
    friction: FrictionResult | None = None

    # I2 — 555_HEART writes this
    shadow: ShadowTrace | None = None

    # I3 — 777_FORGE writes this
    novelty: NoveltyResult | None = None

    # I4 — 888_JUDGE writes this
    values: DualVerdict | None = None

    # I5 — 999_VAULT reads this
    latency: LatencyRequirement | None = None

    # APEX dials — PRESENT, ENERGY-ENTROPY, EXPLORATION-AMANAH
    reality_class: str | None = None  # PRESENT: LIVE|CACHED|INFERRED|HYPOTHESIZED|UNKNOWN
    thermo_exhausted: bool | None = None  # ENERGY-ENTROPY: budget status
    reversibility_level: str | None = (
        None  # AMANAH: trivial|reversible|partial|irreversible|critical
    )

    # Metadata
    created_at: float = field(default_factory=time.time)
    cycle_stages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "friction": self.friction.to_dict() if self.friction else None,
            "shadow": self.shadow.to_dict() if self.shadow else None,
            "novelty": self.novelty.to_dict() if self.novelty else None,
            "values": self.values.to_dict() if self.values else None,
            "latency": self.latency.to_dict() if self.latency else None,
            "reality_class": self.reality_class,
            "thermo_exhausted": self.thermo_exhausted,
            "reversibility_level": self.reversibility_level,
            "created_at": self.created_at,
            "cycle_stages": self.cycle_stages,
        }

    def completeness(self) -> dict[str, bool]:
        """Check which invariants have been computed."""
        return {
            "I1_friction": self.friction is not None,
            "I2_shadow": self.shadow is not None,
            "I3_novelty": self.novelty is not None,
            "I4_values": self.values is not None,
            "I5_latency": self.latency is not None,
            "PRESENT": self.reality_class is not None,
            "ENERGY_ENTROPY": self.thermo_exhausted is not None,
            "AMANAH": self.reversibility_level is not None,
        }

    def is_full_ascent(self) -> bool:
        """Check if all five invariants have been computed (full ascent)."""
        return all(self.completeness().values())

    def can_seal(self) -> tuple[bool, str]:
        """
        999_VAULT calls this. Checks if the cycle can proceed to SEAL.
        Requires at minimum: friction + values. Shadow + novelty recommended.
        """
        missing = []
        if not self.friction:
            missing.append("I1_friction")
        if not self.values:
            missing.append("I4_values")

        # Shadow required for high-friction
        if self.friction and self.friction.level in (FrictionLevel.HIGH, FrictionLevel.CRITICAL):
            if not self.shadow or not self.shadow.valid:
                missing.append("I2_shadow (required for high friction)")

        # Novelty required for high-friction
        if self.friction and self.friction.level in (FrictionLevel.HIGH, FrictionLevel.CRITICAL):
            if self.novelty and not self.novelty.novelty_pass:
                missing.append("I3_novelty (regurgitation detected)")

        # L5b required for high blast radius
        if self.latency and self.latency.blast in (BlastClass.HIGH, BlastClass.IRREVERSIBLE):
            if self.values and not self.values.judge:
                missing.append("I4_L5b_judge (sovereign required for high blast)")

        if missing:
            return False, f"AKAL_INCOMPLETE — missing: {', '.join(missing)}"
        return True, "AKAL_COMPLETE — ready to seal"
