"""
arifOS v45 - Semantic Firewall (Sovereign Witness)
Strict Isolation Layer for Judgment.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
import hashlib
import json


@dataclass
class ApexTelemetry:
    """
    Standard Telemetry Object for APEX.
    Contains ONLY physics attributes and flags.
    NO semantic/linguistic content allowed.
    """

    # Core Physics (TEARFRAME)
    truth_score: float  # F2
    delta_entropy: float  # F4 (ΔS)
    peace_squared: float  # F3/F5
    empathy_score: float  # F6 (κᵣ)
    humility_score: float  # F7 (Ω₀)
    tri_witness_score: float  # F8

    # Evidence Physics (v45)
    coverage_pct: float  # Completeness
    conflict_score: float  # Contradiction level
    freshness_score: float  # Temporal decay
    jargon_density: float  # Clarity metric

    # Binary Flags
    conflict_flag: bool
    sentinel_flag_blocking: bool

    # Provenance
    evidence_pack_hash: str

    def compute_hash(self) -> str:
        """Deterministic hash of telemetry state."""
        # Convert to sorted text to ensure determinism
        data = asdict(self)
        payload = json.dumps(data, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()


class SemanticFirewall:
    """
    The Gatekeeper.
    Ensures no raw text passes to the Judiciary.
    """

    @staticmethod
    def sanitize(
        metrics: Dict[str, float],
        evidence_pack: Any,  # Typed as EvidencePack in real usage
        sentinel_flags: List[str],
    ) -> ApexTelemetry:
        """
        Convert raw inputs into clean ApexTelemetry.
        Strips all text, logs, and semantic residues.
        """

        # 1. Map Core Metrics (with defaults for safety)
        telemetry = ApexTelemetry(
            truth_score=metrics.get("truth", 0.0),
            delta_entropy=metrics.get("delta_s", 0.0),
            peace_squared=metrics.get("peace_squared", 0.0),
            empathy_score=metrics.get("kappa_r", 0.0),
            humility_score=metrics.get("omega_0", 0.05),
            tri_witness_score=metrics.get("tri_witness", 0.0),
            # 2. Extract Evidence Physics
            coverage_pct=getattr(evidence_pack, "coverage_pct", 0.0),
            conflict_score=getattr(
                evidence_pack, "conflict_score", 1.0
            ),  # Default to high conflict if missing
            freshness_score=getattr(evidence_pack, "freshness_score", 0.0),
            jargon_density=getattr(evidence_pack, "jargon_density", 0.0),
            # 3. Compute Flags
            conflict_flag=(getattr(evidence_pack, "conflict_score", 1.0) > 0.15),
            sentinel_flag_blocking=(len(sentinel_flags) > 0),
            # 4. Provenance Only (No Text)
            evidence_pack_hash=getattr(evidence_pack, "compute_pack_hash", lambda: "MISSING_HASH")()
            if hasattr(evidence_pack, "compute_pack_hash")
            else "INVALID_PACK",
        )

        return telemetry
