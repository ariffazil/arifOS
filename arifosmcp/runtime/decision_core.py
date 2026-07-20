"""
arifosmcp/runtime/decision_core.py — Frozen Decision Core

The decision identity that quotes cannot alter.
A DecisionCore is the canonical hash of a frozen verdict.
Quotes sit AFTER decision collapse, never inside it.

Invariant: quote_present or quote_absent must never alter
the decision_core_hash.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════════
# DECISION CORE — frozen, hashable, immutable
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class DecisionCore:
    """The frozen identity of a decision.

    Constitutional output of reasoning + HEART + JUDGE.
    Quotes cannot alter any field. Only witness/presentation varies.
    """

    verdict: str
    evidence_layer: str
    authority_band: str
    action_class: str
    human_decision_required: bool
    reversibility: str
    next_allowed_action: str
    consequence_class: str
    confidence_band: str

    def canonical_json(self) -> str:
        """Deterministic JSON for hashing."""
        return json.dumps(
            asdict(self),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

    def hash(self) -> str:
        """SHA-256 of the canonical decision core."""
        return hashlib.sha256(self.canonical_json().encode()).hexdigest()


# ═══════════════════════════════════════════════════════════════════════════════
# ZEN APEX OUTPUT — single presentation type (quote after freeze)
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ZenApexOutput:
    """Full Zen Apex presentation. One type. One path.

    Sequence: freeze DecisionCore → optional witness → present.
    Witness cannot alter decision_core or decision_core_hash.
    """

    decision_core: DecisionCore
    decision_core_hash: str

    # Presentation layer
    reality: str
    fracture: str
    consequence: str
    choice: str
    weakest_plane: str = ""

    # Witness layer — optional, post-verdict (WITNESS_NOT_EVIDENCE)
    witness_quote: str | None = None
    witness_attribution: str | None = None
    witness_status: str | None = None
    witness_role: str = "WITNESS_NOT_EVIDENCE"
    witness_source_class: str | None = None
    witness_quote_id: str | None = None

    # Metadata
    quote_resolution_status: str = "NO_QUOTE"
    registry_version: str | None = None
    registry_sha256: str | None = None
    zen_compression: str = ""

    def verify_decision_integrity(self) -> bool:
        """True iff the decision core hash has not been tampered with."""
        return self.decision_core.hash() == self.decision_core_hash

    @property
    def verdict(self) -> str:
        return self.decision_core.verdict

    @property
    def evidence(self) -> str:
        return self.decision_core.evidence_layer

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "evidence": self.evidence,
            "decision_core_hash": self.decision_core_hash,
            "decision_core": asdict(self.decision_core),
            "weakest_plane": self.weakest_plane,
            "reality": self.reality,
            "fracture": self.fracture,
            "consequence": self.consequence,
            "choice": self.choice,
            "witness": {
                "text": self.witness_quote,
                "attribution": self.witness_attribution,
                "source_class": self.witness_source_class,
                "quote_id": self.witness_quote_id,
                "status": self.witness_status,
                "role": self.witness_role,
            }
            if self.witness_quote
            else None,
            "quote_resolution_status": self.quote_resolution_status,
            "registry_version": self.registry_version,
            "registry_sha256": self.registry_sha256,
            "zen_compression": self.zen_compression,
        }

    def to_rendered_text(self) -> str:
        """Human-readable Zen Apex block."""
        lines = [
            f"VERDICT: {self.verdict}",
            f"EVIDENCE: {self.evidence}",
            f"CORE: {self.decision_core_hash[:16]}…",
        ]
        if self.weakest_plane:
            lines.append(f"WEAKEST PLANE: {self.weakest_plane}")
        lines.extend(
            [
                "",
                f"Reality: {self.reality}",
                f"Fracture: {self.fracture}",
                f"Consequence: {self.consequence}",
                f"Choice: {self.choice}",
            ]
        )
        if self.witness_quote:
            badge = self.witness_source_class or "WITNESS"
            lines.extend(
                [
                    "",
                    f'Witness: "{self.witness_quote}"',
                    f"  — {self.witness_attribution or 'Unknown'}",
                    f"  {badge} · Reflection, not evidence",
                ]
            )
        if self.zen_compression:
            lines.extend(["", f"∴ {self.zen_compression}"])
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# RECEIPT / RESOLUTION (quote layer — never mutates DecisionCore)
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class VerdictReceipt:
    """Input to post-verdict witness resolve. Decision must already be frozen."""

    decision_core_hash: str
    verdict: str
    evidence_layer: str
    weakest_plane: str
    authority_band: str
    consequence_class: str
    reflection_tags: list[str] = field(default_factory=list)


@dataclass
class QuoteResolution:
    """Output of quote resolution. Cannot alter decision."""

    status: str  # SELECTED | NO_SUITABLE_WITNESS | REJECTED | UNAVAILABLE
    decision_core_hash: str
    quote_id: str | None = None
    quote_text: str | None = None
    quote_attribution: str | None = None
    provenance_class: str | None = None
    role: str = "WITNESS_NOT_EVIDENCE"
    selection_policy_version: str = "quote-resolver-v1"
    provenance_warning: str | None = None


def freeze_decision(
    verdict: str,
    evidence_layer: str,
    authority_band: str,
    action_class: str,
    human_decision_required: bool,
    reversibility: str,
    next_allowed_action: str,
    consequence_class: str,
    confidence_band: str,
    **kwargs: Any,
) -> DecisionCore:
    """Factory for DecisionCore. Extra kwargs are ignored (do not affect hash)."""
    return DecisionCore(
        verdict=verdict,
        evidence_layer=evidence_layer,
        authority_band=authority_band,
        action_class=action_class,
        human_decision_required=human_decision_required,
        reversibility=reversibility,
        next_allowed_action=next_allowed_action,
        consequence_class=consequence_class,
        confidence_band=confidence_band,
    )


__all__ = [
    "DecisionCore",
    "ZenApexOutput",
    "VerdictReceipt",
    "QuoteResolution",
    "freeze_decision",
]
