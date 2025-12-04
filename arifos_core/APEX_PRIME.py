from typing import Literal, List
from .metrics import Metrics, FloorsVerdict

# Version constants (v35Ω)
APEX_VERSION = "v35Ω"
APEX_EPOCH = 35

# Type alias for APEX verdicts (v35Ω adds 888_HOLD and SABAR)
ApexVerdict = Literal["SEAL", "PARTIAL", "VOID", "888_HOLD", "SABAR"]
Verdict = ApexVerdict  # Alias for backwards compatibility

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
) -> ApexVerdict:
    """Apply APEX PRIME v35Ω decision policy.

    Verdict hierarchy:
    - If @EYE has blocking issue → SABAR (stop, breathe, re-evaluate)
    - If any hard floor fails → VOID (Truth, ΔS, Ω₀, Amanah, Ψ, RASA)
    - If hard floors pass but extended floors fail → 888_HOLD (judiciary hold)
    - If hard floors pass but soft floors fail → PARTIAL
    - If all floors (core + extended) pass → SEAL
    """
    floors = check_floors(
        metrics,
        tri_witness_required=high_stakes,
        tri_witness_threshold=tri_witness_threshold,
    )

    # @EYE blocking takes precedence
    if eye_blocking:
        return "SABAR"

    # Any hard floor failure → VOID
    if not floors.hard_ok:
        return "VOID"

    # Extended floors failure → 888_HOLD (v35Ω)
    if not floors.extended_ok:
        return "888_HOLD"

    # Soft floors failure → PARTIAL
    if not floors.soft_ok:
        return "PARTIAL"

    # All floors pass → SEAL
    return "SEAL"


class APEXPrime:
    """
    APEX PRIME v35Ω constitutional judge.

    Provides stateful judgment interface for constitutional compliance.
    Supports @EYE Sentinel integration for blocking issues.
    """

    version = APEX_VERSION
    epoch = APEX_EPOCH

    def __init__(
        self,
        high_stakes: bool = False,
        tri_witness_threshold: float = 0.95,
    ):
        self.high_stakes = high_stakes
        self.tri_witness_threshold = tri_witness_threshold

    def judge(
        self,
        metrics: Metrics,
        eye_blocking: bool = False,
    ) -> ApexVerdict:
        """Judge constitutional compliance and return verdict.

        Args:
            metrics: Constitutional metrics to evaluate
            eye_blocking: True if @EYE Sentinel has a blocking issue

        Returns:
            ApexVerdict: SEAL, PARTIAL, VOID, 888_HOLD, or SABAR
        """
        return apex_review(
            metrics,
            high_stakes=self.high_stakes,
            tri_witness_threshold=self.tri_witness_threshold,
            eye_blocking=eye_blocking,
        )

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
    # Verdicts
    "ApexVerdict",
    "Verdict",
    # Functions
    "apex_review",
    "check_floors",
    # Classes
    "APEXPrime",
]
