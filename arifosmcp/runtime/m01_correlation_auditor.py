"""
M01 — Correlation Auditor (Ω_ortho Computation)
===============================================

Meta-cognition agent that computes orthogonality from agent output signatures.

Every agent invocation stores an output vector signature.
M01 computes pairwise correlation matrix.
If Ω_ortho < threshold, raises HOLD.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import numpy as np

from arifosmcp.runtime.agent_registry import Axis, get_registry

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True)
class OutputSignature:
    """Fingerprints of an agent's output for correlation computation."""

    agent_id: str
    axis: Axis
    timestamp: datetime
    # Semantic fingerprint: hash of key output characteristics
    fingerprint: str
    # Epistemic class: OBSERVED | DERIVED | ESTIMATED | SIMULATED
    epistemic_class: str = "ESTIMATED"
    # Source: which tool generated this
    source_tool: str | None = None
    # Correlation tags: topics/semantics this output addresses
    correlation_tags: tuple[str, ...] = ()


@dataclass
class OrthogonalityReport:
    """Report from M01 correlation audit."""

    omega_ortho: float  # Overall orthogonality score (0.0–1.0)
    correlation_matrix: dict[str, dict[str, float]]  # pairwise correlations
    violations: list[dict[str, Any]]  # detected orthogonality breaches
    agents_in_scope: list[str]
    timestamp: datetime
    trace: list[str] = field(default_factory=list)


class CorrelationAuditor:
    """
    M01: Computes Ω_ortho from agent output signature correlation.

    Maintains rolling window of OutputSignatures.
    Computes correlation matrix on demand.
    Raises HOLD if orthogonality degrades below threshold.
    """

    def __init__(self, window_size: int = 100, threshold: float = 0.85):
        """
        Args:
            window_size: Number of recent signatures to keep per agent
            threshold: Minimum Ω_ortho before HOLD is raised
        """
        self.window_size = window_size
        self.threshold = threshold
        self._signatures: dict[str, list[OutputSignature]] = defaultdict(list)
        self._output_vectors: dict[str, np.ndarray] = {}
        self.registry = get_registry()

    def record(
        self,
        agent_id: str,
        output: dict[str, Any],
        epistemic_class: str = "ESTIMATED",
        source_tool: str | None = None,
    ) -> OutputSignature:
        """
        Record an agent's output signature.

        Computes fingerprint from output content.
        Stores in rolling window.
        """
        # Compute fingerprint from output content
        content_str = json.dumps(output, sort_keys=True, default=str)
        fingerprint = hashlib.sha256(content_str.encode()).hexdigest()[:32]

        # Extract correlation tags from output
        tags = self._extract_tags(output)

        # Get axis from registry
        spec = self.registry.get(agent_id)
        axis = spec.axis if spec else Axis.M  # default to M if unknown

        sig = OutputSignature(
            agent_id=agent_id,
            axis=axis,
            timestamp=_utcnow(),
            fingerprint=fingerprint,
            epistemic_class=epistemic_class,
            source_tool=source_tool,
            correlation_tags=tuple(sorted(tags)),
        )

        # Store in rolling window
        self._signatures[agent_id].append(sig)
        if len(self._signatures[agent_id]) > self.window_size:
            self._signatures[agent_id] = self._signatures[agent_id][-self.window_size :]

        return sig

    def _extract_tags(self, output: dict[str, Any]) -> list[str]:
        """Extract semantic correlation tags from output."""
        tags = []
        # Look for common tag fields
        if "domain" in output:
            tags.append(str(output["domain"]))
        if "verdict" in output:
            tags.append(f"verdict:{output['verdict']}")
        if "stage" in output:
            tags.append(f"stage:{output['stage']}")
        if "risk_tier" in output:
            tags.append(f"risk:{output['risk_tier']}")

        # Extract from payload if nested
        payload = output.get("payload", {})
        if isinstance(payload, dict):
            for key in ["classification", "category", "type"]:
                if key in payload:
                    tags.append(str(payload[key]))

        return tags

    def _compute_vector(self, agent_id: str) -> np.ndarray:
        """
        Compute output vector for an agent from its signatures.

        Vector space (12-dim):
        - Position 0-5: epistemic class encoding (ONE-HOT for 6 classes)
        - Position 6: signature count (normalized)
        - Position 7: average fingerprint entropy (normalized)
        - Position 8-11: correlation tag presence (4 binary bits)
        """
        sigs = self._signatures.get(agent_id, [])
        if not sigs:
            return np.zeros(12)

        vec = np.zeros(12)

        # Epistemic class (one-hot for 6 classes)
        class_map = {
            "OBSERVED": 0,
            "DERIVED": 1,
            "ESTIMATED": 2,
            "SIMULATED": 3,
            "INFERRED": 4,
            "HYPOTHESIS": 5,
        }
        for sig in sigs:
            idx = class_map.get(sig.epistemic_class, 2)
            vec[idx] = max(vec[idx], 1.0)  # one-hot

        # Count
        vec[6] = min(len(sigs) / self.window_size, 1.0)

        # Average fingerprint entropy (compute from fingerprint lengths)
        avg_entropy = sum(len(s.fingerprint) for s in sigs) / max(len(sigs), 1) / 32.0
        vec[7] = min(avg_entropy, 1.0)

        # Tag presence (hash to binary) — 4 bits in positions 8-11
        tag_bits = np.zeros(4)
        for sig in sigs:
            for tag in sig.correlation_tags:
                h = int(hashlib.md5(tag.encode()).hexdigest()[:4], 16)
                tag_bits[h % 4] = 1
        vec[8:12] = tag_bits

        return vec

    def compute_orthogonality(self) -> OrthogonalityReport:
        """
        Compute Ω_ortho from correlation matrix.

        Returns report with:
        - omega_ortho: overall orthogonality score (0.0-1.0)
        - correlation_matrix: pairwise correlations
        - violations: list of breaches where axes correlate > threshold
        """
        agents = list(self._signatures.keys())
        if len(agents) < 2:
            return OrthogonalityReport(
                omega_ortho=1.0,
                correlation_matrix={},
                violations=[],
                agents_in_scope=agents,
                timestamp=_utcnow(),
                trace=["Insufficient agents for correlation computation"],
            )

        # Compute vectors
        vectors = {}
        for agent_id in agents:
            vectors[agent_id] = self._compute_vector(agent_id)

        # Build correlation matrix
        matrix = {}
        violations = []
        axis_violations: dict[str, list[dict]] = defaultdict(list)

        for i, ai in enumerate(agents):
            row = {}
            for j, aj in enumerate(agents):
                if i == j:
                    row[aj] = 1.0
                else:
                    vi = vectors[ai]
                    vj = vectors[aj]
                    # Pearson correlation
                    if np.std(vi) == 0 or np.std(vj) == 0:
                        corr = 0.0
                    else:
                        corr = float(np.corrcoef(vi, vj)[0, 1])

                    row[aj] = round(corr, 4)

                    # Check for cross-axis violation
                    spec_i = self.registry.get(ai)
                    spec_j = self.registry.get(aj)
                    if spec_i and spec_j and spec_i.axis != spec_j.axis:
                        if abs(corr) > 0.7:
                            violation = {
                                "agent_a": ai,
                                "agent_b": aj,
                                "axis_a": spec_i.axis.value,
                                "axis_b": spec_j.axis.value,
                                "correlation": corr,
                                "threshold": 0.7,
                                "severity": "HIGH" if abs(corr) > 0.85 else "MEDIUM",
                            }
                            violations.append(violation)
                            axis_violations[f"{spec_i.axis.value}↔{spec_j.axis.value}"].append(
                                violation
                            )

            matrix[ai] = row

        # Compute Ω_ortho = average off-diagonal correlation (lower = more orthogonal)
        off_diagonal = []
        for ai in agents:
            for aj in agents:
                if ai != aj:
                    off_diagonal.append(abs(matrix[ai][aj]))

        avg_correlation = np.mean(off_diagonal) if off_diagonal else 0.0
        omega_ortho = round(max(0.0, 1.0 - avg_correlation), 4)

        trace = [
            f"Agents: {len(agents)}",
            f"Signatures: {sum(len(s) for s in self._signatures.values())}",
            f"Avg off-diagonal correlation: {avg_correlation:.4f}",
            f"Violations: {len(violations)}",
            f"Ω_ortho: {omega_ortho}",
        ]

        logger.info(f"[M01] Ω_ortho={omega_ortho} | violations={len(violations)}")

        return OrthogonalityReport(
            omega_ortho=omega_ortho,
            correlation_matrix=matrix,
            violations=violations,
            agents_in_scope=agents,
            timestamp=_utcnow(),
            trace=trace,
        )

    def is_orthogonal(self) -> tuple[bool, OrthogonalityReport]:
        """
        Check if current orthogonality is above threshold.

        Returns (is_ok, report).
        If is_ok=False, caller should raise HOLD.
        """
        report = self.compute_orthogonality()
        return report.omega_ortho >= self.threshold, report


# ─── Singleton ─────────────────────────────────────────────────────────────────

_auditor: CorrelationAuditor | None = None


def get_auditor() -> CorrelationAuditor:
    global _auditor
    if _auditor is None:
        _auditor = CorrelationAuditor(window_size=100, threshold=0.85)
    return _auditor
