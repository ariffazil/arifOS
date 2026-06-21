"""
BeliefEngine — Bayesian posterior over world state.

v0.1 — Approximate Bayesian update with explicit confidence bands.
Per-var mean + confidence tracked; no point estimates without provenance.

F2 TRUTH: every fact carries (value, confidence, provenance).
F7 HUMILITY: confidence capped at 0.99 (no fake certainty).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class BeliefState:
    """World state belief with explicit uncertainty.

    Attributes:
        facts:        key -> observed value
        confidence:   key -> [0.0, 1.0] confidence in the fact
        uncertainty:  aggregate uncertainty [0.0, 1.0] derived from confidence mean
        provenance:   key -> OBS/DER/INT/SPEC label (per F2 TRUTH)
    """
    facts: dict[str, Any] = field(default_factory=dict)
    confidence: dict[str, float] = field(default_factory=dict)
    uncertainty: float = 0.2
    provenance: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "facts": dict(self.facts),
            "confidence": dict(self.confidence),
            "uncertainty": self.uncertainty,
            "provenance": dict(self.provenance),
        }


class BeliefEngine:
    """Approximate Bayesian update.

    P(state | obs) ∝ P(obs | state) × P(state)

    Implementation: each new observation nudges confidence toward 0.9 (the
    "evidentially supported" cap). New variables start at 0.7. Aggregate
    uncertainty is 1 - mean(confidence), floored at 0.01.

    This is NOT a full Bayesian filter — it's a bounded approximation that
    gives the right behavior for the cognition substrate (explicit bands,
    provenance, decay toward uncertainty).
    """

    # F2/F7 thresholds
    NEW_VAR_CONFIDENCE = 0.7          # confidence for a brand-new observation
    EVIDENCE_FLOOR = 0.5             # minimum confidence after update
    EVIDENCE_CEILING = 0.99          # F7: never reach 1.0 (humility)
    UNCERTAINTY_MIN = 0.01           # never fully certain
    EVIDENCE_SUPPORTED = 0.9         # confidence when obs is present and non-null

    def update(
        self,
        prior: BeliefState,
        observations: dict[str, Any],
        provenance: Optional[dict[str, str]] = None,
    ) -> BeliefState:
        """Fold new observations into the prior belief, return posterior."""
        facts = dict(prior.facts)
        conf = dict(prior.confidence)
        prov = dict(prior.provenance)

        for k, v in observations.items():
            if k not in facts:
                # New variable
                facts[k] = v
                conf[k] = self.NEW_VAR_CONFIDENCE
            else:
                # Bayesian nudge: combine prior with new evidence
                prior_conf = conf.get(k, self.EVIDENCE_FLOOR)
                evidence = self.EVIDENCE_SUPPORTED if v is not None else self.EVIDENCE_FLOOR
                combined = 0.5 * prior_conf + 0.5 * evidence
                conf[k] = max(
                    self.EVIDENCE_FLOOR,
                    min(self.EVIDENCE_CEILING, combined),
                )
                facts[k] = v

            if provenance and k in provenance:
                prov[k] = provenance[k]
            elif k not in prov:
                prov[k] = "OBS"  # default provenance

        # Aggregate uncertainty
        if conf:
            avg_conf = sum(conf.values()) / len(conf)
            uncertainty = max(self.UNCERTAINTY_MIN, 1.0 - avg_conf)
        else:
            uncertainty = 1.0

        return BeliefState(
            facts=facts,
            confidence=conf,
            uncertainty=uncertainty,
            provenance=prov,
        )
