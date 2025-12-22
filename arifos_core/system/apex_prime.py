from typing import TYPE_CHECKING, Literal, List, Optional, Tuple, Dict, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from ..enforcement.metrics import Metrics, FloorsVerdict

if TYPE_CHECKING:
    from ..enforcement.genius_metrics import GeniusVerdict

# Version constants (v36Ω + v36.1Ω measurement — GENIUS LAW Judiciary)
# Runtime law: v45Ω floors + verdicts (Sovereign Witness)
# Measurement: v45Ω standard (G, C_dark, Ψ, Truth Polarity) via arifos_eval/apex
APEX_VERSION = "v45Ω"
APEX_EPOCH = 45


# =============================================================================
# v42 VERDICT ENUM (STABLE API)
# =============================================================================


class Verdict(Enum):
    """
    Constitutional verdict types (v42 STABLE API).

    Primary verdicts for external API:
    - SEAL: All floors pass, response approved
    - SABAR: Constitutional pause, requires re-evaluation
    - VOID: Hard floor failure, response blocked

    Internal verdicts (governance transparency):
    - PARTIAL: Soft floor warning, proceed with caution
    - HOLD_888: High-stakes hold, requires human confirmation
    - SUNSET: Truth expired, revocation
    """

    # Primary public verdicts
    SEAL = "SEAL"
    SABAR = "SABAR"
    VOID = "VOID"

    # Internal governance verdicts (transparent but secondary)
    PARTIAL = "PARTIAL"
    HOLD_888 = "888_HOLD"
    SUNSET = "SUNSET"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_string(cls, s: str) -> "Verdict":
        """Convert string to Verdict, handling legacy formats."""
        normalized = normalize_verdict_code(s)
        # Map normalized strings to Enum members
        mapping = {
            "SEAL": cls.SEAL,
            "SABAR": cls.SABAR,
            "VOID": cls.VOID,
            "PARTIAL": cls.PARTIAL,
            "HOLD_888": cls.HOLD_888,
            "SUNSET": cls.SUNSET,
        }
        if normalized in mapping:
            return mapping[normalized]
        raise ValueError(f"Unknown verdict: {s}")


def normalize_verdict_code(code: str) -> str:
    """
    Canonicalize verdict strings.

    Ensures legacy codes (e.g. '888_HOLD') map to the v42 standard ('HOLD_888').
    This is the Single Source of Truth for schema alignment.
    """
    upper = code.upper().strip()
    if upper == "888_HOLD":
        return "HOLD_888"
    return upper


# =============================================================================
# v42 APEX VERDICT DATACLASS (STABLE API)
# =============================================================================


@dataclass
class ApexVerdict:
    """
    Structured APEX verdict result (v42 STABLE API).

    Constitution as API: Transparent, structured verdict with:
    - verdict: The Verdict enum value
    - pulse: Vitality/health score (Ψ or equivalent)
    - reason: Human-readable explanation
    - floors: Detailed floor check results

    This is the canonical return type for apex_review().
    For simple string verdicts, use apex_verdict() convenience shim.

    Backward Compatibility:
    - str(result) returns "SEAL", "SABAR", "VOID", etc.
    - result == "SEAL" returns True if verdict is SEAL
    - result in ["SEAL", "PARTIAL"] works for string comparison
    """

    verdict: Verdict
    pulse: float = field(default=1.0)
    reason: str = field(default="")
    floors: Optional[FloorsVerdict] = field(default=None)

    # Optional extended info (governance transparency)
    genius_index: Optional[float] = field(default=None)
    dark_cleverness: Optional[float] = field(default=None)

    def __str__(self) -> str:
        return str(self.verdict.value)

    def __eq__(self, other: object) -> bool:
        """Support comparison with string verdicts for backward compat."""
        if isinstance(other, ApexVerdict):
            return self.verdict == other.verdict
        if isinstance(other, Verdict):
            return self.verdict == other
        if isinstance(other, str):
            # Backward compat: allow comparison with string
            return self.verdict.value == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.verdict)

    @property
    def is_approved(self) -> bool:
        """True if verdict allows proceeding (SEAL or PARTIAL)."""
        return self.verdict in (Verdict.SEAL, Verdict.PARTIAL)

    @property
    def is_blocked(self) -> bool:
        """True if verdict blocks the action (VOID)."""
        return self.verdict == Verdict.VOID

    @property
    def needs_attention(self) -> bool:
        """True if verdict requires human attention."""
        return self.verdict in (Verdict.SABAR, Verdict.HOLD_888)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        result: Dict[str, Any] = {
            "verdict": self.verdict.value,
            "pulse": self.pulse,
            "reason": self.reason,
        }
        if self.floors is not None:
            # FloorsVerdict is a dataclass, convert to dict
            from dataclasses import asdict

            result["floors"] = asdict(self.floors)
        if self.genius_index is not None:
            result["genius_index"] = self.genius_index
        if self.dark_cleverness is not None:
            result["dark_cleverness"] = self.dark_cleverness
        return result


# Legacy type alias for backward compatibility (DEPRECATED in v43)
_LegacyVerdict = Literal["SEAL", "PARTIAL", "VOID", "888_HOLD", "SABAR"]

# Floor thresholds (v35Ω)
TRUTH_MIN = 0.99
DELTA_S_MIN = 0.0
PEACE_SQ_MIN = 1.0
KAPPA_MIN = 0.95
OMEGA_MIN = 0.03
OMEGA_MAX = 0.05
TRI_MIN = 0.95
DRIFT_MIN = 0.1
AMBIGUITY_MAX = 0.1
PARADOX_MAX = 1.0

# =============================================================================
# GENIUS LAW THRESHOLDS (v36Ω runtime, v36.1Ω measurement)
# These thresholds define the GENIUS LAW decision surface.
# Hard floors still gate everything; GENIUS LAW refines verdicts.
# For canonical measurement formulas, see: arifos_eval/apex/apex_measurements.py
# =============================================================================

# G thresholds for verdict decisions
G_SEAL_THRESHOLD: float = 0.7  # G >= this for SEAL consideration
G_PARTIAL_THRESHOLD: float = 0.5  # G >= this for PARTIAL (below SEAL)
G_MIN_THRESHOLD: float = 0.3  # G below this = VOID (even if floors pass)

# C_dark thresholds for risk assessment
C_DARK_SEAL_MAX: float = 0.1  # C_dark <= this for SEAL
C_DARK_PARTIAL_MAX: float = 0.3  # C_dark <= this for PARTIAL
C_DARK_VOID_THRESHOLD: float = 0.5  # C_dark > this = VOID (entropy hazard)


def check_floors(
    metrics: Metrics,
    tri_witness_required: bool = False,
    tri_witness_threshold: float = 0.95,
) -> FloorsVerdict:
    """Evaluate all constitutional floors (core + extended v35Ω)."""
    reasons: List[str] = []

    # Hard floors
    truth_ok = metrics.truth >= TRUTH_MIN
    if not truth_ok:
        reasons.append("Truth < 0.99")

    delta_s_ok = metrics.delta_s >= DELTA_S_MIN
    if not delta_s_ok:
        reasons.append("ΔS < 0")

    omega_0_ok = OMEGA_MIN <= metrics.omega_0 <= OMEGA_MAX
    if not omega_0_ok:
        reasons.append("Ω₀ outside [0.03, 0.05] band")

    amanah_ok = bool(metrics.amanah)
    if not amanah_ok:
        reasons.append("Amanah = false")

    psi_ok = metrics.psi >= 1.0 if metrics.psi is not None else False
    if not psi_ok:
        reasons.append("Ψ < 1.0")

    rasa_ok = bool(metrics.rasa)
    if not rasa_ok:
        reasons.append("RASA not enabled")

    anti_hantu_ok = True if metrics.anti_hantu is None else bool(metrics.anti_hantu)
    if not anti_hantu_ok:
        reasons.append("Anti-Hantu violation")

    hard_ok = (
        truth_ok
        and delta_s_ok
        and omega_0_ok
        and amanah_ok
        and psi_ok
        and rasa_ok
        and anti_hantu_ok
    )

    # Soft floors
    peace_squared_ok = metrics.peace_squared >= PEACE_SQ_MIN
    if not peace_squared_ok:
        reasons.append("Peace² < 1.0")

    kappa_r_ok = metrics.kappa_r >= KAPPA_MIN
    if not kappa_r_ok:
        reasons.append("κᵣ < 0.95")

    if tri_witness_required:
        tri_witness_ok = metrics.tri_witness >= tri_witness_threshold
        if not tri_witness_ok:
            reasons.append("Tri-Witness below threshold")
    else:
        tri_witness_ok = True

    soft_ok = peace_squared_ok and kappa_r_ok and tri_witness_ok

    # Extended floors (v35Ω)
    ambiguity_ok = metrics.ambiguity is None or metrics.ambiguity <= AMBIGUITY_MAX
    if not ambiguity_ok:
        reasons.append("Ambiguity > 0.1")

    drift_ok = metrics.drift_delta is None or metrics.drift_delta >= DRIFT_MIN
    if not drift_ok:
        reasons.append("Drift delta < 0.1")

    paradox_ok = metrics.paradox_load is None or metrics.paradox_load < PARADOX_MAX
    if not paradox_ok:
        reasons.append("Paradox load >= 1.0")

    dignity_ok = metrics.dignity_rma_ok
    if not dignity_ok:
        reasons.append("Dignity/Maruah check failed")

    vault_ok = metrics.vault_consistent
    if not vault_ok:
        reasons.append("Vault-999 inconsistency")

    behavior_ok = metrics.behavior_drift_ok
    if not behavior_ok:
        reasons.append("Behavioral drift detected")

    ontology_ok = metrics.ontology_ok
    if not ontology_ok:
        reasons.append("Ontology/version guard failed")

    sleeper_ok = metrics.sleeper_scan_ok
    if not sleeper_ok:
        reasons.append("Sleeper-agent scan failed")

    return FloorsVerdict(
        hard_ok=hard_ok,
        soft_ok=soft_ok,
        reasons=reasons,
        # Core floors
        truth_ok=truth_ok,
        delta_s_ok=delta_s_ok,
        peace_squared_ok=peace_squared_ok,
        kappa_r_ok=kappa_r_ok,
        omega_0_ok=omega_0_ok,
        amanah_ok=amanah_ok,
        tri_witness_ok=tri_witness_ok,
        psi_ok=psi_ok,
        anti_hantu_ok=anti_hantu_ok,
        rasa_ok=rasa_ok,
        # Extended floors (v35Ω)
        ambiguity_ok=ambiguity_ok,
        drift_ok=drift_ok,
        paradox_ok=paradox_ok,
        dignity_ok=dignity_ok,
        vault_ok=vault_ok,
        behavior_ok=behavior_ok,
        ontology_ok=ontology_ok,
        sleeper_ok=sleeper_ok,
    )


def apex_review(
    metrics: Metrics,
    high_stakes: bool = False,
    tri_witness_threshold: float = 0.95,
    eye_blocking: bool = False,
    energy: float = 1.0,
    entropy: float = 0.0,
    use_genius_law: bool = True,
) -> ApexVerdict:
    """Apply APEX PRIME v42 decision policy with GENIUS LAW.

    Returns structured ApexVerdict with:
    - verdict: Verdict enum (SEAL, SABAR, VOID, PARTIAL, HOLD_888)
    - pulse: Vitality score (Ψ or 1.0 default)
    - reason: Human-readable explanation
    - floors: Detailed floor check results

    Verdict hierarchy (v42):
    1. If @EYE has blocking issue → SABAR (stop, breathe, re-evaluate)
    2. If any hard floor fails → VOID (Truth, ΔS, Ω₀, Amanah, Ψ, RASA, Anti-Hantu)
    3. If C_dark > 0.5 → VOID (ungoverned cleverness = entropy hazard)
    4. If G < 0.3 → VOID (insufficient governed intelligence)
    5. If extended floors fail → HOLD_888 (judiciary hold)
    6. If soft floors fail OR (G < 0.7 or C_dark > 0.1) → PARTIAL
    7. If all floors pass AND G >= 0.7 AND C_dark <= 0.1 → SEAL

    Args:
        metrics: Constitutional metrics to evaluate
        high_stakes: Whether Tri-Witness is required
        tri_witness_threshold: Threshold for Tri-Witness (default 0.95)
        eye_blocking: True if @EYE Sentinel has a blocking issue
        energy: Energy metric for GENIUS LAW [0, 1], default 1.0 (no depletion)
        entropy: System entropy for GENIUS LAW, default 0.0
        use_genius_law: Whether to apply GENIUS LAW (default True, set False for v35 compat)

    Returns:
        ApexVerdict: Structured verdict with verdict, pulse, reason, floors
    """
    floors = check_floors(
        metrics,
        tri_witness_required=high_stakes,
        tri_witness_threshold=tri_witness_threshold,
    )

    # Initialize GENIUS metrics
    g: Optional[float] = None
    c_dark: Optional[float] = None
    pulse: float = 1.0

    # @EYE blocking takes precedence
    if eye_blocking:
        return ApexVerdict(
            verdict=Verdict.SABAR,
            pulse=0.5,
            reason="@EYE Sentinel has blocking issue. Stop, breathe, re-evaluate.",
            floors=floors,
        )

    # Any hard floor failure → VOID (absolute gate)
    if not floors.hard_ok:
        reason = (
            f"Hard floor failure: {', '.join(floors.reasons)}"
            if floors.reasons
            else "Hard floor check failed"
        )
        return ApexVerdict(
            verdict=Verdict.VOID,
            pulse=0.0,
            reason=reason,
            floors=floors,
        )

    # GENIUS LAW evaluation (v42)
    if use_genius_law:
        try:
            from ..enforcement.genius_metrics import evaluate_genius_law

            genius = evaluate_genius_law(metrics, energy=energy, entropy=entropy)
            g = genius.genius_index
            c_dark = genius.dark_cleverness
            pulse = genius.psi_apex if hasattr(genius, "psi_apex") else 1.0

            # C_dark > 0.5 → VOID (entropy hazard, ungoverned cleverness)
            if c_dark > C_DARK_VOID_THRESHOLD:
                return ApexVerdict(
                    verdict=Verdict.VOID,
                    pulse=pulse,
                    reason=f"Dark cleverness too high (C_dark={c_dark:.2f} > {C_DARK_VOID_THRESHOLD}). Entropy hazard.",
                    floors=floors,
                    genius_index=g,
                    dark_cleverness=c_dark,
                )

            # G < 0.3 → VOID (insufficient governed intelligence)
            if g < G_MIN_THRESHOLD:
                return ApexVerdict(
                    verdict=Verdict.VOID,
                    pulse=pulse,
                    reason=f"Insufficient governed intelligence (G={g:.2f} < {G_MIN_THRESHOLD}).",
                    floors=floors,
                    genius_index=g,
                    dark_cleverness=c_dark,
                )

            # Extended floors failure → HOLD_888
            if not floors.extended_ok:
                return ApexVerdict(
                    verdict=Verdict.HOLD_888,
                    pulse=pulse,
                    reason=f"Extended floor check requires attention: {', '.join(floors.reasons)}",
                    floors=floors,
                    genius_index=g,
                    dark_cleverness=c_dark,
                )

            # Soft floors failure → PARTIAL
            if not floors.soft_ok:
                return ApexVerdict(
                    verdict=Verdict.PARTIAL,
                    pulse=pulse,
                    reason=f"Soft floor warning: {', '.join(floors.reasons)}. Proceed with caution.",
                    floors=floors,
                    genius_index=g,
                    dark_cleverness=c_dark,
                )

            # GENIUS LAW decision surface for SEAL vs PARTIAL
            if g >= G_SEAL_THRESHOLD and c_dark <= C_DARK_SEAL_MAX:
                return ApexVerdict(
                    verdict=Verdict.SEAL,
                    pulse=pulse,
                    reason=f"All floors pass. G={g:.2f}, C_dark={c_dark:.2f}. Approved.",
                    floors=floors,
                    genius_index=g,
                    dark_cleverness=c_dark,
                )
            elif g >= G_PARTIAL_THRESHOLD and c_dark <= C_DARK_PARTIAL_MAX:
                return ApexVerdict(
                    verdict=Verdict.PARTIAL,
                    pulse=pulse,
                    reason=f"Floors pass but GENIUS suggests caution. G={g:.2f}, C_dark={c_dark:.2f}.",
                    floors=floors,
                    genius_index=g,
                    dark_cleverness=c_dark,
                )
            else:
                # Middle ground: floors pass but GENIUS metrics suggest caution
                return ApexVerdict(
                    verdict=Verdict.HOLD_888,
                    pulse=pulse,
                    reason=f"GENIUS metrics require review. G={g:.2f}, C_dark={c_dark:.2f}.",
                    floors=floors,
                    genius_index=g,
                    dark_cleverness=c_dark,
                )

        except ImportError:
            # Fallback to v35 behavior if genius_metrics not available
            pass

    # v35Ω fallback behavior (use_genius_law=False or import failed)
    # Extended floors failure → HOLD_888
    if not floors.extended_ok:
        return ApexVerdict(
            verdict=Verdict.HOLD_888,
            pulse=1.0,
            reason=f"Extended floor check requires attention: {', '.join(floors.reasons)}",
            floors=floors,
        )

    # Soft floors failure → PARTIAL
    if not floors.soft_ok:
        return ApexVerdict(
            verdict=Verdict.PARTIAL,
            pulse=1.0,
            reason=f"Soft floor warning: {', '.join(floors.reasons)}. Proceed with caution.",
            floors=floors,
        )

    # All floors pass → SEAL
    return ApexVerdict(
        verdict=Verdict.SEAL,
        pulse=1.0,
        reason="All constitutional floors pass. Approved.",
        floors=floors,
    )


# =============================================================================
# CONVENIENCE SHIM (v42 STABLE API)
# =============================================================================


def apex_verdict(
    metrics: Metrics,
    high_stakes: bool = False,
    tri_witness_threshold: float = 0.95,
    eye_blocking: bool = False,
    energy: float = 1.0,
    entropy: float = 0.0,
    use_genius_law: bool = True,
) -> str:
    """
    Convenience shim returning verdict as string.

    For users who just need "SEAL", "SABAR", or "VOID" without the full
    ApexVerdict structure. Internally calls apex_review().

    Returns:
        str: "SEAL", "SABAR", "VOID", "PARTIAL", or "888_HOLD"
    """
    result = apex_review(
        metrics=metrics,
        high_stakes=high_stakes,
        tri_witness_threshold=tri_witness_threshold,
        eye_blocking=eye_blocking,
        energy=energy,
        entropy=entropy,
        use_genius_law=use_genius_law,
    )
    return str(result.verdict.value)


# =============================================================================
# v38.3 AMENDMENT 3: APEX PRIME META-JUDGMENT FOR W@W CONFLICTS
# =============================================================================


def apex_prime_judge(context: Dict[str, Any]) -> str:
    """
    Meta-judgment when W@W organs conflict.

    v38.3 AMENDMENT 3: No static hierarchy. Uses Ψ vitality + floor metrics.

    This is the constitutional tie-breaker when organs propose conflicting
    verdicts. It does NOT override floors—if F1 (Amanah) fails, action is
    still blocked. APEX determines VERDICT TYPE when floors pass but organs
    conflict on the recommendation.

    Args:
        context: Dict containing:
            - organs: List of organ signals (organ_id, vote, reason)
            - verdict_proposals: Dict of proposed verdicts and supporting organs
            - conflict_type: Type of conflict (e.g., "organ_disagreement")
            - floors (optional): Floor metrics if available
            - psi (optional): Psi vitality score

    Returns:
        Synthesized verdict: SEAL, PARTIAL, 888_HOLD, VOID, or SABAR

    Logic:
        1. Check if any hard floors failed → VOID (floors constrain)
        2. Check severity of organ concerns (VETO > WARN > PASS)
        3. Use Psi vitality to assess system health
        4. Synthesize verdict based on:
           - Number of organs with concerns
           - Severity of concerns (ABSOLUTE > VOID > SABAR > HOLD)
           - System vitality (Psi)
           - Floor pass/fail counts
    """
    organs = context.get("organs", [])
    verdict_proposals = context.get("verdict_proposals", {})
    psi = context.get("psi", 1.0)  # Default to healthy

    # Count votes by severity
    veto_count = sum(1 for o in organs if o.get("vote") == "VETO")
    warn_count = sum(1 for o in organs if o.get("vote") == "WARN")
    pass_count = sum(1 for o in organs if o.get("vote") == "PASS")

    # Extract proposed verdicts
    proposed_verdicts = list(verdict_proposals.keys())

    # Severity order: ABSOLUTE > VOID > SABAR > HOLD-888 > PARTIAL > SEAL
    severity_order = ["VOID", "888_HOLD", "SABAR", "PARTIAL", "SEAL"]

    # If any organ proposed VOID, and Psi is low, escalate to VOID
    if "VOID" in proposed_verdicts and psi < 0.8:
        return "VOID"

    # If multiple organs have concerns (VETO or WARN)
    total_concerns = veto_count + warn_count
    if total_concerns >= 2:
        # Multiple organs concerned → return most severe non-VOID verdict
        for verdict in severity_order:
            if verdict in proposed_verdicts and verdict != "VOID":
                return verdict
        # Fallback to SABAR if no specific verdict
        return "SABAR"

    # If only one organ has concerns
    if total_concerns == 1:
        # Return PARTIAL (soft concern, requires attention)
        return "PARTIAL"

    # If all organs pass but proposed different verdicts, use Psi
    if pass_count == len(organs):
        # High Psi → SEAL
        if psi >= 1.0:
            return "SEAL"
        # Medium Psi → PARTIAL
        else:
            return "PARTIAL"

    # Default: SABAR (need more context to resolve)
    return "SABAR"


# =============================================================================
# APEX PRIME CLASS
# =============================================================================


class APEXPrime:
    """
    APEX PRIME v42 constitutional judge with GENIUS LAW.

    Provides stateful judgment interface for constitutional compliance.
    Integrates GENIUS LAW (G, C_dark) as the decision surface beyond floors.
    Supports @EYE Sentinel integration for blocking issues.

    v42 API:
    - judge() returns ApexVerdict dataclass (verdict, pulse, reason, floors)
    - Verdict is a proper Enum with SEAL, SABAR, VOID (+ internal states)
    - GENIUS LAW evaluation (G = governed intelligence, C_dark = ungoverned risk)
    - Energy and entropy parameters for real-world vitality tracking
    - use_genius_law flag for v35 compatibility
    """

    version = APEX_VERSION
    epoch = APEX_EPOCH

    def __init__(
        self,
        high_stakes: bool = False,
        tri_witness_threshold: float = 0.95,
        use_genius_law: bool = True,
    ):
        self.high_stakes = high_stakes
        self.tri_witness_threshold = tri_witness_threshold
        self.use_genius_law = use_genius_law

    def judge(
        self,
        metrics: Metrics,
        eye_blocking: bool = False,
        energy: float = 1.0,
        entropy: float = 0.0,
    ) -> ApexVerdict:
        """Judge constitutional compliance and return verdict.

        Args:
            metrics: Constitutional metrics to evaluate
            eye_blocking: True if @EYE Sentinel has a blocking issue
            energy: Energy metric for GENIUS LAW [0, 1], default 1.0
            entropy: System entropy for GENIUS LAW, default 0.0

        Returns:
            ApexVerdict: SEAL, PARTIAL, VOID, 888_HOLD, or SABAR
        """
        return apex_review(
            metrics,
            high_stakes=self.high_stakes,
            tri_witness_threshold=self.tri_witness_threshold,
            eye_blocking=eye_blocking,
            energy=energy,
            entropy=entropy,
            use_genius_law=self.use_genius_law,
        )

    def judge_with_genius(
        self,
        metrics: Metrics,
        eye_blocking: bool = False,
        energy: float = 1.0,
        entropy: float = 0.0,
    ) -> Tuple[ApexVerdict, Optional["GeniusVerdict"]]:
        """Judge with GENIUS LAW and return both verdict and GENIUS metrics.

        Returns:
            Tuple of (ApexVerdict, GeniusVerdict or None)
        """
        verdict = self.judge(metrics, eye_blocking, energy, entropy)

        genius_verdict = None
        if self.use_genius_law:
            try:
                from ..enforcement.genius_metrics import evaluate_genius_law

                genius_verdict = evaluate_genius_law(metrics, energy, entropy)
            except ImportError:
                pass

        return verdict, genius_verdict

    def check(self, metrics: Metrics) -> FloorsVerdict:
        """Check all floors and return detailed verdict."""
        return check_floors(
            metrics,
            tri_witness_required=self.high_stakes,
            tri_witness_threshold=self.tri_witness_threshold,
        )


# ——————————————————— PUBLIC EXPORTS ——————————————————— #
__all__ = [
    # Version constants
    "APEX_VERSION",
    "APEX_EPOCH",
    # GENIUS LAW thresholds (v42)
    "G_SEAL_THRESHOLD",
    "G_PARTIAL_THRESHOLD",
    "G_MIN_THRESHOLD",
    "C_DARK_SEAL_MAX",
    "C_DARK_PARTIAL_MAX",
    "C_DARK_VOID_THRESHOLD",
    # v42 Verdict types (STABLE API)
    "Verdict",  # Enum: SEAL, SABAR, VOID, PARTIAL, HOLD_888, SUNSET
    "ApexVerdict",  # Dataclass: verdict, pulse, reason, floors
    # Functions
    "apex_review",  # Returns ApexVerdict (structured)
    "apex_verdict",  # Convenience shim, returns str
    "apex_prime_judge",  # v38.3 AMENDMENT 3: W@W conflict resolver
    "check_floors",
    # Classes
    "APEXPrime",
]
