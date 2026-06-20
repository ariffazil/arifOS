"""
core/physics/institutional_evolution.py — Mortality / Succession / Evolution

Tier 5 DRAFT — 888 HOLD ACTIVE

Implements invariant #15 from the substrate audit:
  Mortality / Succession / Institutional Evolution

Four constraints:
1. Human attention budget — no infinite operator assumption.
2. Population absorption — changes must be absorbable across communities.
3. Institutional succession — roles/obligations survive handover.
4. AI adaptation rate — agents adapt only under constitutional memory,
   audit, rate limits, and human recall.

This module exposes both a function-based API (for tests and scripting)
and an InstitutionalEvolutionGuard class (for daemon integration). All
hard failures raise InstitutionalEvolutionError (888_HOLD / SABAR / VOID).
F13 ratification is required before this invariant can block SEAL.
"""

from __future__ import annotations

from typing import Any

from core.physics.economic_invariants import EconomicInvariantError
from core.physics.thermodynamics_hardened import ThermodynamicError

try:
    from arifosmcp.runtime.heartbeat_registry import federation_liveness
except ImportError:  # pragma: no cover - defensive for standalone test imports
    federation_liveness = None


class SuccessionError(ThermodynamicError):
    """Institutional succession broken — change outruns human absorption."""

    def __init__(self, message: str):
        super().__init__(message, law_id="F11", verdict="888_HOLD")


class InstitutionalEvolutionError(EconomicInvariantError):
    """Base for all institutional evolution invariant breaches."""

    def __init__(self, message: str, *, invariant: str, verdict: str = "HOLD_888"):
        super().__init__(message, invariant=invariant, verdict=verdict)


class AttentionBudgetExceededError(InstitutionalEvolutionError):
    def __init__(self, message: str, verdict: str = "HOLD_888"):
        super().__init__(message, invariant="I15_attention_budget", verdict=verdict)


class PopulationAbsorptionError(InstitutionalEvolutionError):
    def __init__(self, message: str):
        super().__init__(message, invariant="I15_population_absorption", verdict="SABAR")


class SuccessionContinuityError(InstitutionalEvolutionError):
    def __init__(self, message: str):
        super().__init__(message, invariant="I15_succession_continuity", verdict="HOLD_888")


class AIAdaptationRateExceededError(InstitutionalEvolutionError):
    def __init__(self, message: str):
        super().__init__(message, invariant="I15_ai_adaptation_rate", verdict="HOLD_888")


class ConstitutionalRejectionError(InstitutionalEvolutionError):
    """Action violates a constitutional floor — cannot be fixed by more review.

    REJECT is reserved for F13-level prohibitions. Unlike HOLD_888 (which says
    "pause, human must review"), REJECT says "this action is constitutionally
    forbidden regardless of further review."
    """

    def __init__(self, message: str, floor: str = "F13"):
        super().__init__(message, invariant="I15_constitutional_rejection", verdict="REJECT")
        self.floor = floor


# ═══════════════════════════════════════════════════════
# CONSTRAINT 1 — Human Attention Budget (Mortality Floor)
# ═══════════════════════════════════════════════════════


def check_human_attention_budget(
    session_duration_s: float,
    operator_interventions: int,
    max_session_s: float = 14_400.0,  # 4 hours
    max_interventions: int = 200,
    raise_on_breach: bool = False,
) -> dict[str, Any]:
    """
    Enforce finite human attention.

    No system may assume infinite operator stamina, memory, or lifespan.
    Long sessions and high intervention counts degrade decision quality.
    """
    session_ok = session_duration_s <= max_session_s
    interventions_ok = operator_interventions <= max_interventions
    session_ratio = session_duration_s / max(max_session_s, 1.0)
    intervention_ratio = operator_interventions / max(max_interventions, 1)
    attention_score = max(0.0, 1.0 - max(session_ratio, intervention_ratio))

    result = {
        "constraint": "human_attention_budget",
        "passed": session_ok and interventions_ok,
        "session_duration_s": session_duration_s,
        "max_session_s": max_session_s,
        "session_ok": session_ok,
        "operator_interventions": operator_interventions,
        "max_interventions": max_interventions,
        "interventions_ok": interventions_ok,
        "attention_score": round(attention_score, 4),
        "tier": "DRAFT — TIER 5 (Governance Doctrine) — 888 HOLD ACTIVE",
    }

    if not result["passed"] and raise_on_breach:
        raise SuccessionError(
            f"Human attention budget exceeded: session={session_duration_s:.0f}s / "
            f"interventions={operator_interventions}. Mortality floor breached."
        )

    return result


# ═══════════════════════════════════════════════════════
# CONSTRAINT 2 — Institutional Succession Continuity
# ═══════════════════════════════════════════════════════


def check_institutional_succession(
    role_changes: list[dict[str, Any]],
    unacknowledged_obligations: list[str],
    raise_on_breach: bool = False,
) -> dict[str, Any]:
    """
    Every role, rule, memory, authority, and obligation must survive
    handover without myth-making.

    role_changes entries should be dicts like:
        {"role": "vault_admin", "action": "revoked", "successor": "...", "handoff_doc": "..."}
    """
    orphan_changes = [
        c for c in role_changes if not c.get("successor") or not c.get("handoff_doc")
    ]
    succession_score = 1.0
    if orphan_changes:
        succession_score -= min(1.0, len(orphan_changes) / max(len(role_changes), 1))
    if unacknowledged_obligations:
        succession_score -= min(0.5, len(unacknowledged_obligations) / 10.0)
    succession_score = max(0.0, succession_score)

    passed = len(orphan_changes) == 0 and len(unacknowledged_obligations) == 0

    result = {
        "constraint": "institutional_succession",
        "passed": passed,
        "role_changes_count": len(role_changes),
        "orphan_changes_count": len(orphan_changes),
        "orphan_changes": orphan_changes,
        "unacknowledged_obligations": unacknowledged_obligations,
        "succession_score": round(succession_score, 4),
        "tier": "DRAFT — TIER 5 (Governance Doctrine) — 888 HOLD ACTIVE",
    }

    if not passed and raise_on_breach:
        raise SuccessionError(
            f"Institutional succession breach: {len(orphan_changes)} orphan changes, "
            f"{len(unacknowledged_obligations)} unacknowledged obligations."
        )

    return result


# ═══════════════════════════════════════════════════════
# CONSTRAINT 3 — AI Adaptation Rate
# ═══════════════════════════════════════════════════════


def check_ai_adaptation_rate(
    changes_last_30d: int,
    human_reviews_last_30d: int,
    max_unreviewed_ratio: float = 0.10,
    raise_on_breach: bool = False,
) -> dict[str, Any]:
    """
    AI adaptation must not outrun human review capacity.

    Returns 888_HOLD if unreviewed changes exceed the ratio threshold.
    """
    unreviewed = max(0, changes_last_30d - human_reviews_last_30d)
    unreviewed_ratio = (
        unreviewed / max(changes_last_30d, 1) if changes_last_30d > 0 else 0.0
    )
    passed = unreviewed_ratio <= max_unreviewed_ratio
    adaptation_score = 1.0 - min(1.0, unreviewed_ratio / max(max_unreviewed_ratio, 1e-9))

    result = {
        "constraint": "ai_adaptation_rate",
        "passed": passed,
        "changes_last_30d": changes_last_30d,
        "human_reviews_last_30d": human_reviews_last_30d,
        "unreviewed_changes": unreviewed,
        "unreviewed_ratio": round(unreviewed_ratio, 4),
        "max_unreviewed_ratio": max_unreviewed_ratio,
        "adaptation_score": round(adaptation_score, 4),
        "tier": "DRAFT — TIER 5 (Governance Doctrine) — 888 HOLD ACTIVE",
    }

    if not passed and raise_on_breach:
        raise SuccessionError(
            f"AI adaptation outruns review: {unreviewed_ratio:.1%} unreviewed "
            f"({unreviewed}/{changes_last_30d}). Max allowed {max_unreviewed_ratio:.1%}."
        )

    return result


# ═══════════════════════════════════════════════════════
# CONSTRAINT 4 — Population Absorption
# ═══════════════════════════════════════════════════════


def check_population_absorption(
    affected_communities: list[str],
    consent_coverage: float,
    min_consent: float = 0.67,
    raise_on_breach: bool = False,
) -> dict[str, Any]:
    """
    Changes affecting people must be absorbable across communities.

    consent_coverage is the fraction of affected communities/stakeholders
    that have actively consented or been consulted.
    """
    passed = consent_coverage >= min_consent
    absorption_score = min(1.0, consent_coverage / max(min_consent, 1e-9))

    result = {
        "constraint": "population_absorption",
        "passed": passed,
        "affected_communities": affected_communities,
        "affected_count": len(affected_communities),
        "consent_coverage": consent_coverage,
        "min_consent": min_consent,
        "absorption_score": round(absorption_score, 4),
        "tier": "DRAFT — TIER 5 (Governance Doctrine) — 888 HOLD ACTIVE",
    }

    if not passed and raise_on_breach:
        raise SuccessionError(
            f"Population absorption breach: consent={consent_coverage:.1%} < "
            f"min={min_consent:.1%}. Change not absorbable across communities."
        )

    return result


# ═══════════════════════════════════════════════════════
# UNIFIED RUNNER
# ═══════════════════════════════════════════════════════


def check_institutional_evolution(
    session_duration_s: float = 0.0,
    operator_interventions: int = 0,
    role_changes: list[dict[str, Any]] | None = None,
    unacknowledged_obligations: list[str] | None = None,
    changes_last_30d: int = 0,
    human_reviews_last_30d: int = 0,
    affected_communities: list[str] | None = None,
    consent_coverage: float = 1.0,
    raise_on_breach: bool = False,
) -> dict[str, Any]:
    """
    Run all four #15 constraints and return a unified report.

    If raise_on_breach=True, the first failing constraint raises
    SuccessionError (888_HOLD). Otherwise all reports are collected.
    """
    role_changes = role_changes or []
    unacknowledged_obligations = unacknowledged_obligations or []
    affected_communities = affected_communities or []

    checks = [
        check_human_attention_budget(
            session_duration_s,
            operator_interventions,
            raise_on_breach=raise_on_breach,
        ),
        check_institutional_succession(
            role_changes,
            unacknowledged_obligations,
            raise_on_breach=raise_on_breach,
        ),
        check_ai_adaptation_rate(
            changes_last_30d,
            human_reviews_last_30d,
            raise_on_breach=raise_on_breach,
        ),
        check_population_absorption(
            affected_communities,
            consent_coverage,
            raise_on_breach=raise_on_breach,
        ),
    ]

    all_passed = all(c["passed"] for c in checks)
    return {
        "invariant": "I15_DRAFT",
        "passed": all_passed,
        "constraints": checks,
        "tier": "DRAFT — TIER 5 (Governance Doctrine) — 888 HOLD ACTIVE",
    }


# ═══════════════════════════════════════════════════════
# CLASS-BASED GUARD (daemon integration)
# ═══════════════════════════════════════════════════════


class InstitutionalEvolutionGuard:
    """
    Constitutional guard for Invariant #15: Mortality / Succession / Institutional Evolution.
    """

    @classmethod
    def check_human_attention_budget(
        cls,
        session_duration_s: float,
        operator_interventions: int,
        max_session_s: float = 14_400.0,
        max_interventions: int = 200,
    ) -> dict[str, Any]:
        """F1-F13: Human mortality floor — no infinite attention assumption."""
        if session_duration_s < 0 or operator_interventions < 0:
            raise InstitutionalEvolutionError(
                "Attention parameters cannot be negative.",
                invariant="I15_attention_budget",
                verdict="VOID",
            )

        if session_duration_s > max_session_s:
            raise AttentionBudgetExceededError(
                f"Operator session duration ({session_duration_s:.1f}s) exceeds max limit ({max_session_s}s). "
                "Fatigue risk: human attention capacity exceeded. Triggering 888 HOLD.",
            )

        if operator_interventions > max_interventions:
            raise AttentionBudgetExceededError(
                f"Operator interventions ({operator_interventions}) exceed max limit ({max_interventions}). "
                "Cognitive overload risk: trigger 888 HOLD.",
            )

        warning_verdict = "PASS"
        reasons = []
        if session_duration_s > max_session_s * 0.8:
            warning_verdict = "SABAR"
            reasons.append(
                f"Operator active for {session_duration_s:.1f}s (approaching max duration). Consider handover."
            )
        if operator_interventions > max_interventions * 0.8:
            warning_verdict = "SABAR"
            reasons.append(
                f"Operator interventions at {operator_interventions} (approaching max cognitive load)."
            )

        return {
            "passed": True,
            "verdict": warning_verdict,
            "session_duration_s": session_duration_s,
            "operator_interventions": operator_interventions,
            "reasons": reasons,
        }

    @classmethod
    def check_population_absorption(
        cls,
        affected_communities: list[str],
        consent_coverage: float,
        min_consent: float = 0.67,
    ) -> dict[str, Any]:
        """F6: Population evolution floor — changes affecting people must be absorbable."""
        if not (0.0 <= consent_coverage <= 1.0):
            raise InstitutionalEvolutionError(
                "Consent coverage must be between 0.0 and 1.0.",
                invariant="I15_population_absorption",
                verdict="VOID",
            )

        if affected_communities and consent_coverage < min_consent:
            raise PopulationAbsorptionError(
                f"Community consent ({consent_coverage*100:.1f}%) below required threshold ({min_consent*100:.1f}%) "
                f"for affected communities: {affected_communities}. SABAR."
            )

        return {
            "passed": True,
            "verdict": "PASS",
            "affected_communities": affected_communities,
            "consent_coverage": consent_coverage,
        }

    @classmethod
    def check_institutional_succession(
        cls,
        role_changes: list[dict[str, Any]],
        unacknowledged_obligations: list[str],
    ) -> dict[str, Any]:
        """F11: Institutional succession floor — roles and obligations must survive handover."""
        for role in role_changes:
            role_name = role.get("role_name", role.get("role", "unknown_role"))
            has_successor = role.get("successor_id") or role.get("successor")
            has_authority = role.get("authority_origin") or role.get("handoff_doc")
            if not has_successor or not has_authority:
                raise SuccessionContinuityError(
                    f"Role change for '{role_name}' lacks succession metadata. "
                    "Cannot verify succession continuity. HOLD_888."
                )

        if unacknowledged_obligations:
            raise SuccessionContinuityError(
                f"There are {len(unacknowledged_obligations)} unacknowledged obligations remaining. "
                "Succession pipeline blocked until obligations are accepted by successors. HOLD_888."
            )

        return {
            "passed": True,
            "verdict": "PASS",
            "role_changes": len(role_changes),
            "unacknowledged_obligations": len(unacknowledged_obligations),
        }

    @classmethod
    def check_ai_adaptation_rate(
        cls,
        changes_last_30d: int,
        human_reviews_last_30d: int,
        max_unreviewed_ratio: float = 0.10,
    ) -> dict[str, Any]:
        """F7: AI adaptation floor — rate limit AI-driven procedural changes."""
        if changes_last_30d < 0 or human_reviews_last_30d < 0:
            raise InstitutionalEvolutionError(
                "Change tracking values cannot be negative.",
                invariant="I15_ai_adaptation_rate",
                verdict="VOID",
            )

        if changes_last_30d > 0:
            unreviewed = max(0, changes_last_30d - human_reviews_last_30d)
            unreviewed_ratio = unreviewed / changes_last_30d
            if unreviewed_ratio > max_unreviewed_ratio:
                raise AIAdaptationRateExceededError(
                    f"AI-driven adaptation rate too high: {unreviewed} of {changes_last_30d} changes "
                    f"({unreviewed_ratio*100:.1f}%) remain unreviewed, exceeding limit ({max_unreviewed_ratio*100:.1f}%). HOLD_888."
                )

        return {
            "passed": True,
            "verdict": "PASS",
            "changes_last_30d": changes_last_30d,
            "human_reviews_last_30d": human_reviews_last_30d,
        }

    @classmethod
    def check_federation_liveness(
        cls,
        required_organs: list[str] | None = None,
        max_stale_seconds: float = 120.0,
    ) -> dict[str, Any]:
        """F8: Institutional evolution requires a live federation substrate.

        MUTATE / IRREVERSIBLE actions must not proceed when required organs
        are stale or degraded. The heartbeat registry is fed by the live NATS
        organ attestation subscriber (arifos.organ.>).
        """
        if federation_liveness is None:
            return {
                "passed": True,
                "verdict": "PASS",
                "reason": "heartbeat_registry not available (offline/test mode)",
            }

        liveness = federation_liveness(
            required_organs=required_organs,
            threshold_seconds=max_stale_seconds,
        )
        if liveness["verdict"] == "SEAL":
            return {
                "passed": True,
                "verdict": "PASS",
                "liveness": liveness,
            }

        raise SuccessionContinuityError(
            f"Federation liveness breach: {liveness}. "
            "Required organs are stale/degraded; institutional evolution cannot proceed. HOLD_888."
        )

    @classmethod
    def evaluate_evolution_invariants(cls, payload: dict[str, Any]) -> dict[str, Any]:
        """Evaluate all 4 Mortality / Succession / Institutional Evolution sub-checks."""
        results = {}
        first_failure = None

        if "session_duration_s" in payload and "operator_interventions" in payload:
            try:
                results["attention_budget"] = cls.check_human_attention_budget(
                    payload["session_duration_s"],
                    payload["operator_interventions"],
                    payload.get("max_session_s", 14_400.0),
                    payload.get("max_interventions", 200),
                )
            except InstitutionalEvolutionError as e:
                results["attention_budget"] = {"passed": False, "verdict": e.verdict, "error": str(e)}
                if not first_failure:
                    first_failure = e

        if "affected_communities" in payload and "consent_coverage" in payload:
            try:
                results["population_absorption"] = cls.check_population_absorption(
                    payload["affected_communities"],
                    payload["consent_coverage"],
                    payload.get("min_consent", 0.67),
                )
            except InstitutionalEvolutionError as e:
                results["population_absorption"] = {"passed": False, "verdict": e.verdict, "error": str(e)}
                if not first_failure:
                    first_failure = e

        if "role_changes" in payload or "unacknowledged_obligations" in payload:
            try:
                results["succession_continuity"] = cls.check_institutional_succession(
                    payload.get("role_changes", []),
                    payload.get("unacknowledged_obligations", []),
                )
            except InstitutionalEvolutionError as e:
                results["succession_continuity"] = {"passed": False, "verdict": e.verdict, "error": str(e)}
                if not first_failure:
                    first_failure = e

        if "changes_last_30d" in payload and "human_reviews_last_30d" in payload:
            try:
                results["ai_adaptation_rate"] = cls.check_ai_adaptation_rate(
                    payload["changes_last_30d"],
                    payload["human_reviews_last_30d"],
                    payload.get("max_unreviewed_ratio", 0.10),
                )
            except InstitutionalEvolutionError as e:
                results["ai_adaptation_rate"] = {"passed": False, "verdict": e.verdict, "error": str(e)}
                if not first_failure:
                    first_failure = e

        # Forge 3: federation liveness gate — requires live organ attestation
        if payload.get("check_federation_liveness", False):
            try:
                results["federation_liveness"] = cls.check_federation_liveness(
                    required_organs=payload.get("required_organs"),
                    max_stale_seconds=payload.get("max_stale_seconds", 120.0),
                )
            except InstitutionalEvolutionError as e:
                results["federation_liveness"] = {"passed": False, "verdict": e.verdict, "error": str(e)}
                if not first_failure:
                    first_failure = e

        passed = first_failure is None
        verdict = "PASS"
        if not passed:
            verdict = first_failure.verdict
        else:
            for check_res in results.values():
                if check_res.get("verdict") == "SABAR":
                    verdict = "SABAR"

        return {
            "passed": passed,
            "verdict": verdict,
            "first_failure": str(first_failure) if first_failure else None,
            "results": results,
            "final_doctrine_canonical": (
                "An AI-mediated institution must never evolve faster than mortal humans, "
                "successor operators, and affected populations can understand, inherit, contest, and recall."
            ),
        }
