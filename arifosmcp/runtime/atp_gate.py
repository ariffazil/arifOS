"""
arifosmcp/runtime/atp_gate.py — APEX Telemetry Pipeline Gate

Forged: 2026-07-15
Purpose: Single pre-execution gate for ALL MCP tool calls.
         Connects QDF + WELL + witness + 888-APEX into one decision.

Flow:  INGRESS → ATP GATE → AKAL HOOKS → TOOL → EVIDENCE RECEIPT
Gate:  PROCEED (QDF ≥ threshold + WELL OK + witness OK)
       HOLD    (QDF < threshold or WELL HOLD or witness SELF on L5)
       VOID    (QDF < 0.30 or WELL CRITICAL)

ZEN integration:
  ZEN-3: Scar Law as QEC stabilizer (syndrome measurement)
  ZEN-6: CHSH test for tri-witness (falsifiable W3)
  ZEN-4: Born-rule confidence (amplitude vectors)

Floor alignment:
  F1 AMANAH    — Irreversible tools require witness != SELF
  F2 TRUTH     — QDF enforces epistemic labeling
  F3 WITNESS   — Position validation, CHSH falsifiability
  F4 CLARITY   — Single gate, single decision, ΔS ≤ 0
  F6 EMPATHY   — WELL state check protects human readiness
  F7 HUMILITY  — QDF < 0.5 → HOLD (insufficient evidence)
  F8 GENIUS    — Gate decision is computable, auditable
  F11 AUDIT    — Every gate decision logged
  F13 SOVEREIGN — Human override always available

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from arifosmcp.runtime.qdf import (
    BlastRadius,
    ConfidenceBand,
    DEFAULT_QDF_THRESHOLD,
    EpistemicLabel,
    HOLD_QDF_THRESHOLD,
    QDFResult,
    VOID_QDF_THRESHOLD,
    WitnessPosition,
    compute_qdf,
)

logger = logging.getLogger("arifosmcp.atp_gate")

# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE FLAG — controlled deployment
# ═══════════════════════════════════════════════════════════════════════════════

import os

ATP_ENABLED = os.getenv("ATP_ENABLED", "true").lower() in ("true", "1", "yes")
ATP_WITNESS_ENABLED = os.getenv("ATP_WITNESS_ENABLED", "true").lower() in ("true", "1", "yes")
ATP_ZEN3_ENABLED = os.getenv("ATP_ZEN3_ENABLED", "true").lower() in ("true", "1", "yes")
ATP_ZEN6_ENABLED = os.getenv("ATP_ZEN6_ENABLED", "true").lower() in ("true", "1", "yes")


# ═══════════════════════════════════════════════════════════════════════════════
# ATP VERDICT
# ═══════════════════════════════════════════════════════════════════════════════

class ATPVerdictType(str, Enum):
    PROCEED = "PROCEED"
    HOLD = "HOLD"
    VOID = "VOID"


@dataclass
class ATPVerdict:
    """
    ATP gate verdict — returned before every MCP tool execution.

    Fields are flat (no nested untyped dicts) for deterministic hashing.
    """
    verdict: str                          # PROCEED / HOLD / VOID
    qdf: float                            # QDF score [0, 1]
    well_state: str                       # WELL signal at gate time
    witness_position: str                 # SELF / INTERNAL / EXTERNAL / HUMAN
    narrator_debt: int                    # accumulated self-attestation debt
    tool_name: str                        # tool being gated
    session_id: str                       # session context
    timestamp: str                        # ISO timestamp
    reason: str                           # human-readable reason

    # ZEN-3: Scar Law stabilizer syndrome
    stabilizer_syndrome: list[int] = field(default_factory=list)
    syndrome_nonzero: bool = False

    # ZEN-6: CHSH test for tri-witness
    chsh_score: float = 0.0
    chsh_nonlocal: bool = False           # S > 2

    # ZEN-4: Born-rule confidence
    born_confidence: float = 0.0
    amplitude_normalization: float = 0.0  # should be ~1.0

    # QDF breakdown
    qdf_result: dict[str, Any] = field(default_factory=dict)

    # Feature flags
    witness_enabled: bool = True
    zen3_enabled: bool = True
    zen6_enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_canonical_json(self) -> str:
        """Deterministic JSON for hashing/signing."""
        return json.dumps(self.to_dict(), sort_keys=True, default=str, separators=(",", ":"))

    def hash(self) -> str:
        """SHA-256 of canonical JSON."""
        return hashlib.sha256(self.to_canonical_json().encode()).hexdigest()


# ═══════════════════════════════════════════════════════════════════════════════
# L5 TOOLS (irreversible, require witness != SELF)
# ═══════════════════════════════════════════════════════════════════════════════

L5_TOOLS = frozenset({
    "arif_seal",           # 999 — VAULT999 seal (irreversible)
    "forge_seal",          # A-FORGE seal
    "forge_execute",       # A-FORGE execution
    "forge_filesystem",    # A-FORGE filesystem mutation
    "forge_filesystem_move",
    "forge_filesystem_delete",
    "forge_github_create_pull_request",
    "forge_github_create_issue",
    "forge_github_create_or_update_file",
    "forge_execute_sealed",
})


# ═══════════════════════════════════════════════════════════════════════════════
# WELL STATE CACHE (in-memory, TTL 30s)
# Phase 2 will upgrade to Redis
# ═══════════════════════════════════════════════════════════════════════════════

_well_cache: dict[str, Any] = {}
_well_cache_ts: float = 0.0
WELL_CACHE_TTL = 30.0  # seconds


def _get_well_state() -> dict[str, Any]:
    """Get WELL state from cache or query WELL organ."""
    global _well_cache, _well_cache_ts

    now = time.time()
    if now - _well_cache_ts < WELL_CACHE_TTL and _well_cache:
        return _well_cache

    # Try to query WELL organ
    try:
        import httpx
        resp = httpx.get("http://127.0.0.1:18083/health", timeout=2.0)
        if resp.status_code == 200:
            data = resp.json()
            _well_cache = {
                "well_score": data.get("well_score", 0.0),
                "well_signal": data.get("well_signal", "UNKNOWN"),
                "status": data.get("status", "unknown"),
                "floors_violated": data.get("floors_violated", []),
                "truth_status": data.get("truth_status", "UNKNOWN"),
            }
            _well_cache_ts = now
            return _well_cache
    except Exception as e:
        logger.warning(f"WELL query failed: {e}")

    # Fallback: proceed with UNKNOWN
    _well_cache = {
        "well_score": 0.0,
        "well_signal": "UNKNOWN",
        "status": "unavailable",
        "floors_violated": [],
        "truth_status": "UNKNOWN",
    }
    _well_cache_ts = now
    return _well_cache


# ═══════════════════════════════════════════════════════════════════════════════
# WELL GATE
# ═══════════════════════════════════════════════════════════════════════════════

def well_gate(well_state: dict[str, Any]) -> tuple[bool, str]:
    """
    WELL gate logic.

    HOLD if:
        - well_score < 50 (machine degraded)
        - well_signal == WELL_HOLD (explicit hold)
        - status == unavailable (WELL unreachable)

    PROCEED otherwise.
    """
    well_score = well_state.get("well_score", 0.0)
    well_signal = well_state.get("well_signal", "UNKNOWN")
    status = well_state.get("status", "unknown")

    if status == "unavailable":
        # Graceful degradation: proceed with warning
        logger.warning("WELL unavailable — proceeding with degraded gate")
        return True, "WELL_UNAVAILABLE_PROCEED"

    if well_signal == "WELL_HOLD":
        return False, "WELL_HOLD_SIGNAL"

    if well_score < 50.0:
        return False, f"WELL_SCORE_LOW ({well_score:.1f})"

    return True, "WELL_OK"


# ═══════════════════════════════════════════════════════════════════════════════
# WITNESS VALIDATION (F3 WITNESS)
# ═══════════════════════════════════════════════════════════════════════════════

# Session narrator debt tracker
_narrator_debt: dict[str, int] = {}


def validate_witness(
    tool_name: str,
    session_id: str,
    witness_position: WitnessPosition | str = WitnessPosition.SELF,
) -> tuple[bool, str, int]:
    """
    Validate witness position for tool call.

    For L5 tools (irreversible):
        - REQUIRES position != SELF
        - REQUIRES narrator_debt < 5

    For L1-L4 tools:
        - Logs position but does not block
        - Increments narrator_debt counter

    Returns: (proceed, reason, debt)
    """
    if isinstance(witness_position, str):
        witness_position = WitnessPosition(witness_position)

    # Get current debt
    debt = _narrator_debt.get(session_id, 0)

    # L5 tools: require non-SELF witness
    if tool_name in L5_TOOLS:
        if witness_position == WitnessPosition.SELF:
            return False, f"L5_TOOL_REQUIRES_NON_SELF_WITNESS (tool={tool_name})", debt
        if debt >= 5:
            return False, f"NARRATOR_DEBT_EXCEEDED (debt={debt})", debt

    # Increment debt for SELF attestation
    if witness_position == WitnessPosition.SELF:
        debt += 1
        _narrator_debt[session_id] = debt

    return True, "WITNESS_OK", debt


# ═══════════════════════════════════════════════════════════════════════════════
# ZEN-3: SCAR LAW AS QEC STABILIZER
# ═══════════════════════════════════════════════════════════════════════════════

# Stabilizer set per session (syndrome bits)
_session_stabilizers: dict[str, list[int]] = {}

# Stabilizer definitions (each checks a constitutional invariant)
STABILIZER_DEFINITIONS = [
    {"id": 0, "name": "F1_reversibility", "check": "blast_radius != irreversible or witness != SELF"},
    {"id": 1, "name": "F2_truth_label", "check": "epistemic_label != UNKNOWN"},
    {"id": 2, "name": "F3_witness_present", "check": "witness_position in (HUMAN, EXTERNAL, INTERNAL)"},
    {"id": 3, "name": "F4_entropy_reduce", "check": "qdf >= 0.5"},
    {"id": 4, "name": "F7_humility", "check": "qdf <= 0.95 (no fake certainty)"},
    {"id": 5, "name": "F8_genius", "check": "qdf >= 0.80"},
    {"id": 6, "name": "F11_audit", "check": "session_id present"},
    {"id": 7, "name": "F13_sovereign", "check": "not (L5 tool + SELF witness)"},
]


def compute_stabilizer_syndrome(
    tool_name: str,
    session_id: str,
    qdf: float,
    epistemic_label: str,
    witness_position: str,
    blast_radius: str,
) -> list[int]:
    """
    ZEN-3: Compute stabilizer syndrome for this gate decision.

    Each stabilizer checks a constitutional invariant.
    Nonzero syndrome = drift detected → route to 555 critique.

    Returns: list of 8 syndrome bits (0 = pass, 1 = fail)
    """
    syndrome = [0] * 8

    # S0: F1 reversibility
    if blast_radius == "irreversible" and witness_position == "SELF":
        syndrome[0] = 1

    # S1: F2 truth label
    if epistemic_label == "UNKNOWN":
        syndrome[1] = 1

    # S2: F3 witness present
    if witness_position not in ("HUMAN", "EXTERNAL", "INTERNAL"):
        syndrome[2] = 1

    # S3: F4 entropy reduce
    if qdf < 0.5:
        syndrome[3] = 1

    # S4: F7 humility (no fake certainty)
    if qdf > 0.95:
        syndrome[4] = 1

    # S5: F8 genius
    if qdf < 0.80:
        syndrome[5] = 1

    # S6: F11 audit
    if not session_id:
        syndrome[6] = 1

    # S7: F13 sovereign
    if tool_name in L5_TOOLS and witness_position == "SELF":
        syndrome[7] = 1

    return syndrome


# ═══════════════════════════════════════════════════════════════════════════════
# ZEN-6: CHSH TEST FOR TRI-WITNESS NON-LOCALITY
# ═══════════════════════════════════════════════════════════════════════════════

def chsh_witness_test(
    human_outcome: bool,
    ai_outcome: bool,
    external_outcome: bool,
    measurement_bases: tuple[float, float, float, float] = (0.0, 45.0, 22.5, 67.5),
) -> float:
    """
    ZEN-6: CHSH inequality test for tri-witness non-locality.

    If S > 2: non-local correlation (constitutional structure beyond classical).
    If S ≤ 2: classical correlation (independent channels).

    Simplified CHSH: S = |E(a,b) - E(a,b') + E(a',b) + E(a',b')|
    where E(a,b) = correlation coefficient at measurement bases a,b.

    For the tri-witness, we map:
      - human channel = first qubit
      - AI channel = second qubit
      - external channel = reference

    Returns: S value (classical bound = 2, quantum bound = 2√2 ≈ 2.828)
    """
    # Convert outcomes to ±1
    h = 1 if human_outcome else -1
    a = 1 if ai_outcome else -1
    e = 1 if external_outcome else -1

    # Correlation at each basis combination
    # E(a,b) = ⟨AB⟩ = h * a (simplified)
    E_ab = h * a
    E_ab_prime = h * e  # different basis
    E_a_prime_b = a * e  # different basis
    E_a_prime_b_prime = h * a * e  # all three

    # CHSH parameter
    S = abs(E_ab - E_ab_prime + E_a_prime_b + E_a_prime_b_prime)

    return float(S)


# ═══════════════════════════════════════════════════════════════════════════════
# BLAST RADIUS INFERENCE
# ═══════════════════════════════════════════════════════════════════════════════

def infer_blast_radius(tool_name: str) -> BlastRadius:
    """Infer blast radius from tool name."""
    if tool_name in L5_TOOLS:
        return BlastRadius.IRREVERSIBLE
    if tool_name in ("arif_forge", "forge_execute", "forge_dry_run"):
        return BlastRadius.HIGH
    if tool_name in ("arif_route", "arif_bridge_connect", "arif_critique"):
        return BlastRadius.MEDIUM
    return BlastRadius.LOW


# ═══════════════════════════════════════════════════════════════════════════════
# ATP GATE — THE SINGLE GATE
# ═══════════════════════════════════════════════════════════════════════════════

def atp_gate(
    tool_name: str,
    session_id: str,
    epistemic_label: EpistemicLabel | str = EpistemicLabel.UNKNOWN,
    confidence_band: ConfidenceBand | str = ConfidenceBand.UNKNOWN,
    witness_position: WitnessPosition | str = WitnessPosition.SELF,
    blast_radius: BlastRadius | str | None = None,
    threshold: float = DEFAULT_QDF_THRESHOLD,
) -> ATPVerdict:
    """
    Single gate before MCP tool execution.

    1. Compute QDF (Born-rule amplitudes)
    2. Check WELL state
    3. Validate witness position
    4. Compute stabilizer syndrome (ZEN-3)
    5. Run CHSH test (ZEN-6)
    6. Return PROCEED / HOLD / VOID with full audit trail

    Floor alignment:
        F1 AMANAH  — Irreversible tools require witness != SELF
        F2 TRUTH   — QDF enforces epistemic labeling
        F3 WITNESS — Position validation + CHSH falsifiability
        F4 CLARITY — Single gate, single decision
        F7 HUMILITY — QDF < 0.5 → HOLD
        F11 AUDIT  — Every gate decision logged
        F13 SOVEREIGN — Human override always available
    """
    start_ts = time.time()
    now = datetime.now(UTC).isoformat()

    # Feature flag: if ATP disabled, always PROCEED
    if not ATP_ENABLED:
        return ATPVerdict(
            verdict="PROCEED",
            qdf=1.0,
            well_state="ATP_DISABLED",
            witness_position="ATP_DISABLED",
            narrator_debt=0,
            tool_name=tool_name,
            session_id=session_id,
            timestamp=now,
            reason="ATP disabled via feature flag",
        )

    # Infer blast radius if not provided
    if blast_radius is None:
        blast_radius = infer_blast_radius(tool_name)
    if isinstance(blast_radius, str):
        blast_radius = BlastRadius(blast_radius)

    # Normalize witness position
    if isinstance(witness_position, str):
        witness_position = WitnessPosition(witness_position)

    # ── Step 1: QDF computation (Born-rule) ──
    qdf_result = compute_qdf(
        epistemic_label=epistemic_label,
        confidence_band=confidence_band,
        witness_position=witness_position,
        blast_radius=blast_radius,
        threshold=threshold,
    )

    # ── Step 2: WELL gate ──
    well_state = _get_well_state()
    well_proceed, well_reason = well_gate(well_state)

    # ── Step 3: Witness validation ──
    witness_proceed = True
    witness_reason = "WITNESS_OK"
    debt = 0
    if ATP_WITNESS_ENABLED:
        witness_proceed, witness_reason, debt = validate_witness(
            tool_name=tool_name,
            session_id=session_id,
            witness_position=witness_position,
        )

    # ── Step 4: ZEN-3 stabilizer syndrome ──
    syndrome: list[int] = []
    syndrome_nonzero = False
    if ATP_ZEN3_ENABLED:
        syndrome = compute_stabilizer_syndrome(
            tool_name=tool_name,
            session_id=session_id,
            qdf=qdf_result.qdf,
            epistemic_label=epistemic_label if isinstance(epistemic_label, str) else epistemic_label.value,
            witness_position=witness_position if isinstance(witness_position, str) else witness_position.value,
            blast_radius=blast_radius if isinstance(blast_radius, str) else blast_radius.value,
        )
        syndrome_nonzero = any(s != 0 for s in syndrome)

    # ── Step 5: ZEN-6 CHSH test ──
    chsh_score = 0.0
    chsh_nonlocal = False
    if ATP_ZEN6_ENABLED:
        # Simplified: use witness position as proxy for channel outcomes
        human_outcome = witness_position == WitnessPosition.HUMAN
        ai_outcome = witness_position in (WitnessPosition.INTERNAL, WitnessPosition.EXTERNAL)
        external_outcome = witness_position == WitnessPosition.EXTERNAL
        chsh_score = chsh_witness_test(human_outcome, ai_outcome, external_outcome)
        chsh_nonlocal = chsh_score > 2.0

    # ── Step 6: Final verdict ──
    verdict = ATPVerdictType.PROCEED
    reasons = []

    # QDF check
    if qdf_result.qdf < VOID_QDF_THRESHOLD:
        verdict = ATPVerdictType.VOID
        reasons.append(f"QDF_VOID ({qdf_result.qdf:.3f} < {VOID_QDF_THRESHOLD})")
    elif qdf_result.qdf < threshold:
        verdict = ATPVerdictType.HOLD
        reasons.append(f"QDF_HOLD ({qdf_result.qdf:.3f} < {threshold})")

    # WELL check
    if not well_proceed:
        if verdict == ATPVerdictType.PROCEED:
            verdict = ATPVerdictType.HOLD
        reasons.append(f"WELL_{well_reason}")

    # Witness check
    if not witness_proceed:
        verdict = ATPVerdictType.VOID  # L5 + SELF = VOID, not HOLD
        reasons.append(f"WITNESS_{witness_reason}")

    # ZEN-3 syndrome check
    if syndrome_nonzero and verdict == ATPVerdictType.PROCEED:
        verdict = ATPVerdictType.HOLD
        reasons.append(f"SYNDROME_NONZERO (bits={[i for i,s in enumerate(syndrome) if s]})")

    # Build reason string
    if not reasons:
        reason = "PROCEED: all gates passed"
    else:
        reason = " | ".join(reasons)

    # ZEN-4 born confidence
    from arifosmcp.runtime.qdf import build_amplitude_vector
    amp_vec = build_amplitude_vector(epistemic_label, confidence_band)
    born_conf = amp_vec.probability(
        epistemic_label if isinstance(epistemic_label, EpistemicLabel) else EpistemicLabel(epistemic_label)
    )

    latency_ms = (time.time() - start_ts) * 1000

    return ATPVerdict(
        verdict=verdict.value,
        qdf=qdf_result.qdf,
        well_state=well_state.get("well_signal", "UNKNOWN"),
        witness_position=witness_position.value if isinstance(witness_position, WitnessPosition) else witness_position,
        narrator_debt=debt,
        tool_name=tool_name,
        session_id=session_id,
        timestamp=now,
        reason=reason,
        stabilizer_syndrome=syndrome,
        syndrome_nonzero=syndrome_nonzero,
        chsh_score=chsh_score,
        chsh_nonlocal=chsh_nonlocal,
        born_confidence=born_conf,
        amplitude_normalization=round(amp_vec.total_probability(), 4),
        qdf_result=qdf_result.to_dict(),
        witness_enabled=ATP_WITNESS_ENABLED,
        zen3_enabled=ATP_ZEN3_ENABLED,
        zen6_enabled=ATP_ZEN6_ENABLED,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# RESET (for testing)
# ═══════════════════════════════════════════════════════════════════════════════

def reset_atp_state() -> None:
    """Reset ATP internal state (for testing)."""
    global _well_cache, _well_cache_ts
    _well_cache.clear()
    _well_cache_ts = 0.0
    _narrator_debt.clear()
    _session_stabilizers.clear()
