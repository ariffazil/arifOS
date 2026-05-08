"""
Portfolio Correlation Guard.

Tracks model_lineage_hash across all prospects in a portfolio.
Detects when >= 3 prospects share the same lineage hash —
correlated model bias can cause portfolio collapse.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class CorrelatedProspect:
    prospect_id: str
    model_lineage_hash: str
    integrity_score: float


@dataclass
class CorrelationReport:
    systemic_risk: bool
    correlated_prospects: List[CorrelatedProspect] = field(default_factory=list)
    lineage_groups: Dict[str, List[str]] = field(default_factory=dict)
    action: str = "PASS"
    reason: Optional[str] = None
    correlation_threshold: int = 3

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "systemic_risk": self.systemic_risk,
            "action": self.action,
            "correlation_threshold": self.correlation_threshold,
        }
        if self.correlated_prospects:
            result["correlated_prospects"] = [
                {
                    "prospect_id": cp.prospect_id,
                    "model_lineage_hash": cp.model_lineage_hash,
                    "integrity_score": cp.integrity_score,
                }
                for cp in self.correlated_prospects
            ]
        if self.lineage_groups:
            result["lineage_groups"] = self.lineage_groups
        if self.reason:
            result["reason"] = self.reason
        return result


class PortfolioCorrelationGuard:
    """
    Tracks model_lineage_hash across portfolio.
    If >= 3 prospects share same lineage hash → systemic risk detected.
    """

    CORRELATION_THRESHOLD = 3

    def __init__(self, correlation_threshold: int = 3) -> None:
        self.correlation_threshold = correlation_threshold

    def check_prospect(self, prospect: Dict[str, Any]) -> CorrelationReport:
        lineage_hash = prospect.get("model_lineage_hash")
        if not lineage_hash:
            return CorrelationReport(
                systemic_risk=False,
                action="PASS",
                reason="No model_lineage_hash provided — cannot assess correlation",
            )

        return CorrelationReport(
            systemic_risk=False,
            action="PASS",
            reason="Single prospect — correlation check not applicable",
        )

    def check_portfolio(self, prospects: List[Dict[str, Any]]) -> CorrelationReport:
        lineage_to_prospects: Dict[str, List[CorrelatedProspect]] = defaultdict(list)

        for prospect in prospects:
            lineage_hash = prospect.get("model_lineage_hash")
            if not lineage_hash:
                continue

            lineage_to_prospects[lineage_hash].append(
                CorrelatedProspect(
                    prospect_id=prospect.get("prospect_id", "UNKNOWN"),
                    model_lineage_hash=lineage_hash,
                    integrity_score=prospect.get("integrity_score", 0.0),
                )
            )

        correlated_groups: Dict[str, List[str]] = {}
        all_correlated: List[CorrelatedProspect] = []

        for lineage_hash, prospects_list in lineage_to_prospects.items():
            if len(prospects_list) >= self.correlation_threshold:
                correlated_groups[lineage_hash] = [
                    p.prospect_id for p in prospects_list
                ]
                all_correlated.extend(prospects_list)

        if all_correlated:
            prospect_ids = [p.prospect_id for p in all_correlated]
            lineage_hashes = list(set([p.model_lineage_hash for p in all_correlated]))
            return CorrelationReport(
                systemic_risk=True,
                correlated_prospects=all_correlated,
                lineage_groups=correlated_groups,
                action="HOLD",
                reason=f"Correlated model bias detected: {len(all_correlated)} prospects share {len(lineage_hashes)} lineage hash(es). One flawed AI interpretation can influence multiple wells simultaneously.",
                correlation_threshold=self.correlation_threshold,
            )

        return CorrelationReport(
            systemic_risk=False,
            lineage_groups={
                h: [p.prospect_id for p in ps]
                for h, ps in lineage_to_prospects.items()
                if len(ps) < self.correlation_threshold
            },
            action="PASS",
            reason=f"No lineage groups with >= {self.correlation_threshold} prospects detected",
            correlation_threshold=self.correlation_threshold,
        )

    def assess_epistemic_diversity(self, prospects: List[Dict[str, Any]]) -> Dict[str, Any]:
        lineage_counter = Counter()
        total_with_hash = 0
        total_without_hash = 0

        for prospect in prospects:
            lineage_hash = prospect.get("model_lineage_hash")
            if lineage_hash:
                lineage_counter[lineage_hash] += 1
                total_with_hash += 1
            else:
                total_without_hash += 1

        unique_lineages = len(lineage_counter)
        max_share = max(lineage_counter.values()) if lineage_counter else 0

        return {
            "total_prospects": len(prospects),
            "prospects_with_lineage_hash": total_with_hash,
            "prospects_without_lineage_hash": total_without_hash,
            "unique_lineages": unique_lineages,
            "max_prospects_per_lineage": max_share,
            "diversity_score": unique_lineages / len(prospects) if prospects else 0.0,
            "lineage_distribution": dict(lineage_counter),
        }
