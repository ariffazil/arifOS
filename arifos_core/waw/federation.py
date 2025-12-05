"""
federation.py - W@W Federation Core (Organ Aggregation)

The W@W Federation aggregates signals from all 5 organs:
- @WELL (somatic safety, Peace², κᵣ)
- @RIF (epistemic rigor, ΔS, Truth)
- @WEALTH (resource stewardship, Amanah)
- @GEOX (physical feasibility, E_earth)
- @PROMPT (language optics, Anti-Hantu)

Voting Protocol:
- Any ABSOLUTE veto → immediate VOID
- Any VETO → aggregate VETO (SABAR/VOID/HOLD-888 based on type)
- Mixed WARN/PASS → PARTIAL
- All PASS → SEAL candidate

See: canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..metrics import Metrics
from .base import OrganSignal, OrganVote, WAWOrgan
from .well import WellOrgan
from .rif import RifOrgan
from .wealth import WealthOrgan
from .geox import GeoxOrgan
from .prompt import PromptOrgan


@dataclass
class FederationVerdict:
    """
    Aggregated verdict from W@W Federation.

    Contains all organ signals and the computed verdict.
    """

    # Individual signals
    signals: List[OrganSignal] = field(default_factory=list)

    # Aggregated vote
    aggregate_vote: OrganVote = OrganVote.PASS

    # Verdict string (for APEX PRIME compatibility)
    verdict: str = "SEAL"  # SEAL, PARTIAL, VOID, SABAR, HOLD-888

    # Flags
    has_absolute_veto: bool = False
    has_veto: bool = False
    has_warn: bool = False

    # Summary
    veto_organs: List[str] = field(default_factory=list)
    warn_organs: List[str] = field(default_factory=list)
    pass_organs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize verdict for logging."""
        return {
            "verdict": self.verdict,
            "aggregate_vote": self.aggregate_vote.value,
            "has_absolute_veto": self.has_absolute_veto,
            "has_veto": self.has_veto,
            "has_warn": self.has_warn,
            "veto_organs": self.veto_organs,
            "warn_organs": self.warn_organs,
            "pass_organs": self.pass_organs,
            "signals": [s.to_dict() for s in self.signals],
        }


class WAWFederationCore:
    """
    W@W Federation Core - Organ aggregation and voting.

    Runs all 5 organs and aggregates their signals into a
    unified verdict for APEX PRIME.

    Usage:
        federation = WAWFederationCore()
        verdict = federation.evaluate(output_text, metrics)
        if verdict.has_veto:
            # Handle veto
    """

    def __init__(self) -> None:
        """Initialize federation with all 5 organs."""
        self.organs: List[WAWOrgan] = [
            WellOrgan(),
            RifOrgan(),
            WealthOrgan(),
            GeoxOrgan(),
            PromptOrgan(),
        ]

    def evaluate(
        self,
        output_text: str,
        metrics: Metrics,
        context: Optional[Dict[str, Any]] = None,
    ) -> FederationVerdict:
        """
        Evaluate output through all W@W organs.

        Runs each organ's check() and aggregates signals into
        a unified verdict.

        Args:
            output_text: The draft output to evaluate
            metrics: Constitutional metrics from AAA engines
            context: Additional context

        Returns:
            FederationVerdict with all signals and aggregate vote
        """
        context = context or {}

        # Collect signals from all organs
        signals: List[OrganSignal] = []
        for organ in self.organs:
            signal = organ.check(output_text, metrics, context)
            signals.append(signal)

        # Classify signals
        veto_organs: List[str] = []
        warn_organs: List[str] = []
        pass_organs: List[str] = []
        has_absolute_veto = False

        for signal in signals:
            if signal.vote == OrganVote.VETO:
                veto_organs.append(signal.organ_id)
                if signal.is_absolute_veto:
                    has_absolute_veto = True
            elif signal.vote == OrganVote.WARN:
                warn_organs.append(signal.organ_id)
            else:
                pass_organs.append(signal.organ_id)

        # Determine aggregate vote
        has_veto = len(veto_organs) > 0
        has_warn = len(warn_organs) > 0

        if has_veto:
            aggregate_vote = OrganVote.VETO
        elif has_warn:
            aggregate_vote = OrganVote.WARN
        else:
            aggregate_vote = OrganVote.PASS

        # Determine verdict string
        if has_absolute_veto:
            verdict = "VOID"  # Absolute vetoes are always VOID
        elif has_veto:
            # Determine veto type based on which organ vetoed
            veto_types = []
            for signal in signals:
                if signal.vote == OrganVote.VETO:
                    # Get veto type from organ
                    for organ in self.organs:
                        if organ.organ_id == signal.organ_id:
                            veto_types.append(organ.veto_type)
                            break

            # Priority: ABSOLUTE > VOID > SABAR > HOLD-888 > PARTIAL
            if "ABSOLUTE" in veto_types:
                verdict = "VOID"
            elif "VOID" in veto_types:
                verdict = "VOID"
            elif "SABAR" in veto_types:
                verdict = "SABAR"
            elif "HOLD-888" in veto_types:
                verdict = "888_HOLD"
            else:
                verdict = "PARTIAL"
        elif has_warn:
            verdict = "PARTIAL"
        else:
            verdict = "SEAL"

        return FederationVerdict(
            signals=signals,
            aggregate_vote=aggregate_vote,
            verdict=verdict,
            has_absolute_veto=has_absolute_veto,
            has_veto=has_veto,
            has_warn=has_warn,
            veto_organs=veto_organs,
            warn_organs=warn_organs,
            pass_organs=pass_organs,
        )

    def get_organ(self, organ_id: str) -> Optional[WAWOrgan]:
        """Get a specific organ by ID."""
        for organ in self.organs:
            if organ.organ_id == organ_id:
                return organ
        return None


__all__ = ["WAWFederationCore", "FederationVerdict"]
