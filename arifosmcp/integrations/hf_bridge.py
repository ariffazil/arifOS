"""
arifosmcp/integrations/hf_bridge.py — Hugging Face Import Bridge
═══════════════════════════════════════════════════════════════

Governed bridge between arifOS kernel and Hugging Face Hub.
Wraps HFImportGate with session-aware constitutional validation,
entropy pricing, and provenance generation.

Called by arif_forge / arif_route when a HF model import is requested.
The bridge validates, the kernel seals.

Architecture:
  arif_forge → hf_bridge.import_guarded() → HFImportGate.process()
              → thermodynamic_judge → return verdict → arif_seal

DITEMPA BUKAN DIBERI — Forged, Not Given. 2026-08-05.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from arifosmcp.federation.hf_import_gate import (
    HFImportConfig,
    HFImportGate,
    HFImportRequest,
    HFImportResult,
    ImportVerdict,
    ResourceType,
    quick_assess_license,
)

logger = logging.getLogger(__name__)


# ── Bridge result types ──────────────────────────────────────────────────────


@dataclass
class BridgeResult:
    """Structured result from the HF bridge for kernel consumption."""

    repo_id: str
    verdict: str  # SEAL | HOLD | VOID
    kappa_r: float
    G: float
    delta_s: float
    pathway: str
    floor_summary: dict[str, str] = field(default_factory=dict)
    violations: list[str] = field(default_factory=list)
    provenance_id: str = ""
    recommended_action: str = "HOLD"
    entropy_receipt: dict[str, Any] | None = None
    raw_result: HFImportResult | None = None

    def to_kernel_response(self) -> dict[str, Any]:
        """Render as arifOS kernel-compatible response dict."""
        return {
            "verdict": self.verdict,
            "repo_id": self.repo_id,
            "thermodynamic": {
                "kappa_r": self.kappa_r,
                "G": self.G,
                "delta_s": self.delta_s,
                "pathway": self.pathway,
            },
            "floors": self.floor_summary,
            "violations": self.violations,
            "provenance_id": self.provenance_id,
            "recommended_action": self.recommended_action,
            "entropy_receipt": self.entropy_receipt,
        }


# ── HF Bridge ─────────────────────────────────────────────────────────────────


class HFBridge:
    """Governed bridge: arifOS kernel ↔ Hugging Face Hub.

    Wraps HFImportGate with:
    - Session-aware actor binding
    - Constitutional pre-flight (quick_assess_license)
    - Entropy receipt rendering
    - Provenance ID generation for VAULT999 sealing
    """

    def __init__(self, hf_token: str | None = None):
        """Initialize with optional HuggingFace token.

        Args:
            hf_token: HF API token. Falls back to HF_TOKEN env var
                      (loaded from /root/.secrets/tokens/huggingface).
        """
        self._gate = HFImportGate(hf_token=hf_token)

    # ── Public API ────────────────────────────────────────────────────────

    def import_model(
        self,
        repo_id: str,
        intended_use: str = "general",
        actor_id: str = "unknown",
        session_id: str = "",
        verify_sha256: bool = True,
        require_model_card: bool = True,
        min_gain_override: Optional[float] = None,
    ) -> BridgeResult:
        """Import a model through the constitutional gate.

        Args:
            repo_id: HF repo ID (e.g., "microsoft/phi-2")
            intended_use: How the model will be used in arifOS
            actor_id: Calling actor for audit trail
            session_id: Governing session ID
            verify_sha256: Enable SHA256 verification
            require_model_card: Require model card metadata
            min_gain_override: Override F8 minimum G threshold

        Returns:
            BridgeResult with verdict, scores, floor summary, provenance
        """
        config = HFImportConfig(
            verify_sha256=verify_sha256,
            require_model_card=require_model_card,
            min_gain_override=min_gain_override,
        )

        request = HFImportRequest(
            repo_id=repo_id,
            resource_type=ResourceType.MODEL,
            intended_use=intended_use,
            config=config,
            actor_id=actor_id,
            session_id=session_id,
        )

        logger.info(f"HF Import: {repo_id} by {actor_id} (use: {intended_use})")
        result = self._gate.process(request)

        # Build floor summary
        floor_summary = {}
        for fid, fr in result.floor_results.items():
            floor_summary[fid] = fr.status

        bridge_result = BridgeResult(
            repo_id=repo_id,
            verdict=result.verdict.value,
            kappa_r=result.thermodynamic_scores.kappa_r,
            G=result.thermodynamic_scores.G,
            delta_s=result.thermodynamic_scores.delta_s,
            pathway=result.thermodynamic_scores.pathway,
            floor_summary=floor_summary,
            violations=result.violations,
            provenance_id=result.provenance_id,
            recommended_action=result.recommended_action,
            entropy_receipt=result.entropy_receipt,
            raw_result=result,
        )

        logger.info(
            f"HF Import verdict: {bridge_result.verdict} "
            f"(G={bridge_result.G:.3f}, κᵣ={bridge_result.kappa_r:.3f}, {bridge_result.pathway})"
        )

        return bridge_result

    def import_dataset(
        self,
        repo_id: str,
        intended_use: str = "training",
        actor_id: str = "unknown",
        session_id: str = "",
    ) -> BridgeResult:
        """Import a dataset through the constitutional gate.

        Dataset imports follow the same floor checks but with relaxed
        F8 (gain) threshold since datasets don't execute code.
        """
        return self.import_model(
            repo_id=repo_id,
            intended_use=intended_use,
            actor_id=actor_id,
            session_id=session_id,
            verify_sha256=True,
            require_model_card=True,
            min_gain_override=0.60,  # Lower bar for datasets
        )

    def preflight_license(self, license_str: str) -> dict[str, Any]:
        """Quick pre-flight: assess license without full gate run.

        Use this before importing to avoid wasting gate cycles on
        obviously incompatible licenses.
        """
        return quick_assess_license(license_str)

    def preflight_repo(self, repo_id: str) -> dict[str, Any]:
        """Quick pre-flight: run full gate but return minimal summary.

        Useful for batch screening of candidate models.
        """
        result = self.import_model(
            repo_id=repo_id,
            intended_use="preflight_screening",
            actor_id="preflight",
            verify_sha256=False,  # Skip for speed
            require_model_card=False,  # Relax for screening
        )

        return {
            "repo_id": repo_id,
            "verdict": result.verdict,
            "G": result.G,
            "kappa_r": result.kappa_r,
            "pathway": result.pathway,
            "violation_count": len(result.violations),
            "blocker_floors": [
                fid for fid, status in result.floor_summary.items() if status in ("HOLD", "VOID")
            ],
        }

    def batch_screen(self, repo_ids: list[str]) -> list[dict[str, Any]]:
        """Batch screen multiple repos with preflight checks.

        Returns list of preflight results, sorted by verdict (SEAL first).
        """
        results = []
        for repo_id in repo_ids:
            try:
                result = self.preflight_repo(repo_id)
                results.append(result)
            except Exception as exc:
                results.append(
                    {
                        "repo_id": repo_id,
                        "verdict": "ERROR",
                        "error": str(exc),
                    }
                )

        # Sort: SEAL → HOLD → VOID → ERROR
        verdict_order = {"SEAL": 0, "HOLD": 1, "VOID": 2, "ERROR": 3}
        results.sort(key=lambda r: verdict_order.get(r.get("verdict", "ERROR"), 99))

        return results


# ── Module-level singleton ────────────────────────────────────────────────────

# Import at module level for capability map routing.
# Tokens loaded from /root/.secrets/tokens/huggingface via environment.
try:
    hf_bridge = HFBridge()
    logger.info("HF Bridge initialized (token from HF_TOKEN env)")
except Exception as exc:
    logger.warning(f"HF Bridge initialization deferred: {exc}")
    hf_bridge = None  # type: ignore[assignment]


__all__ = [
    "HFBridge",
    "BridgeResult",
    "hf_bridge",
]
