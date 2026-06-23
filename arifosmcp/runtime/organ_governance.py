"""
organ_governance.py — Shared Governance Module for ArifOS Organs
================================================================
DITEMPA BUKAN DIBERI — Forged, Not Given

Every organ (GEOX, WEALTH, WELL) imports this module to:
  1. Register its tool surface with arifOS on startup
  2. Check risk tier before executing C2+ tools
  3. Call arifOS kernel (arif_judge) for C2/IRREVERSIBLE tools
  4. Execute only after receiving SEAL verdict

Risk Tier Classification:
  READONLY  → Execute directly, log to VAULT999
  C1        → arifOS pre-check advisory, execute anyway, log result
  C2        → arifOS SEAL required before execution
  IRREVERSIBLE → arifOS SEAL + explicit human ack required

Usage in organ server:
  from arifosmcp.runtime.organ_governance import OrganGovernance, RiskTier

  governance = OrganGovernance(organ_name="GEOX", organ_version="v2.0.0")

  # At start of each tool handler:
  result = governance.check_governance("geox_prospect_judge_seal", arguments)
  if result["verdict"] == "HOLD":
      return error_response(result)
  if result["verdict"] == "VOID":
      return error_response(result)
  # proceed with tool execution...
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

logger = logging.getLogger("organ_governance")


class RiskTier(StrEnum):
    READONLY = "readonly"  # No governance needed, log only
    C1_ADVISORY = "c1"  # Pre-check with arifOS, execute anyway
    C2_EXECUTE = "c2"  # SEAL required before execution
    IRREVERSIBLE = "irreversible"  # SEAL + human ack required


# ─── Certainty Cap Classification (Chapter 6 Upgrade) ─────────────────────────


class CertaintyCap(StrEnum):
    """Epistemic certainty ceiling per tool."""

    OBSERVED = "verified"
    DERIVED = "calculated"
    INTERPRETED = "likely"
    SPECULATIVE = "possible"
    MYTHIC = "symbolically_framed"


# Mapping: truth_class → max certainty expression allowed
CERTAINTY_CAP_RANK: dict[str, int] = {
    CertaintyCap.OBSERVED: 4,
    CertaintyCap.DERIVED: 3,
    CertaintyCap.INTERPRETED: 2,
    CertaintyCap.SPECULATIVE: 1,
    CertaintyCap.MYTHIC: 0,
}

# Tool-level certainty caps (default = SPECULATIVE for safety)
TOOL_CERTAINTY_CAP: dict[str, CertaintyCap] = {
    # GEOX: direct measurements
    "geox_well_analyze_sequence": CertaintyCap.DERIVED,
    "geox_data_qc_bundle": CertaintyCap.OBSERVED,
    "geox_forward_model_synthetic": CertaintyCap.DERIVED,
    "geox_seismic_well_tie_compute": CertaintyCap.DERIVED,
    "geox_time_depth_anchor": CertaintyCap.OBSERVED,
    "geox_anomalous_contrast_detector": CertaintyCap.INTERPRETED,
    "geox_subsurface_verify_integrity": CertaintyCap.INTERPRETED,
    "geox_prospect_evaluate": CertaintyCap.SPECULATIVE,
    "geox_prospect_judge_preview": CertaintyCap.SPECULATIVE,
    "geox_prospect_judge_seal": CertaintyCap.INTERPRETED,
    "geox_process_abduction": CertaintyCap.SPECULATIVE,
    # WEALTH: financial calculations
    "wealth_field_macro": CertaintyCap.OBSERVED,
    "wealth_conservation_capital": CertaintyCap.DERIVED,
    "wealth_flow_liquidity": CertaintyCap.DERIVED,
    "wealth_energy_productivity": CertaintyCap.DERIVED,
    "wealth_gradient_price": CertaintyCap.OBSERVED,
    "wealth_entropy_risk": CertaintyCap.INTERPRETED,
    "wealth_synthesize": CertaintyCap.SPECULATIVE,
    "wealth_governance_verdict": CertaintyCap.SPECULATIVE,
    # WELL: biological assessments
    "well_classify_substrate": CertaintyCap.INTERPRETED,
    "well_assess_metabolism": CertaintyCap.INTERPRETED,
    "well_assess_homeostasis": CertaintyCap.INTERPRETED,
    "well_assess_livelihood": CertaintyCap.INTERPRETED,
    "well_guard_dignity": CertaintyCap.MYTHIC,
}


# ─── Risk Classification Per Organ ────────────────────────────────────────────

TOOL_RISK_MAP: dict[str, dict[str, RiskTier]] = {
    "GEOX": {
        # READONLY tools — no governance check needed
        "geox_well_analyze_sequence": RiskTier.READONLY,
        "geox_well_compute_gr_bins": RiskTier.READONLY,
        "geox_well_build_packages": RiskTier.READONLY,
        "geox_well_infer_seq_strat": RiskTier.READONLY,
        "geox_section_interpret_correlation": RiskTier.READONLY,
        "geox_map_context_scene": RiskTier.READONLY,
        "geox_bundle_security_audit": RiskTier.READONLY,
        "geox_data_qc_bundle": RiskTier.READONLY,
        "geox_forward_model_synthetic": RiskTier.READONLY,
        "geox_seismic_well_tie_compute": RiskTier.READONLY,
        "geox_time_depth_anchor": RiskTier.READONLY,
        "geox_process_abduction": RiskTier.READONLY,
        "geox_subsurface_verify_integrity": RiskTier.READONLY,
        "geox_evidence_contradiction_scan": RiskTier.READONLY,
        "geox_evidence_summarize_cross": RiskTier.READONLY,
        "geox_resource_registry_status": RiskTier.READONLY,
        "geox_contradiction_registry_status": RiskTier.READONLY,
        "geox_test_receipt_status": RiskTier.READONLY,
        "geox_mcp_health_check": RiskTier.READONLY,
        "geox_anomalous_contrast_detector": RiskTier.READONLY,
        "geox_vision_time_to_depth": RiskTier.READONLY,
        "geox_time4d_analyze_system": RiskTier.READONLY,
        "geox_prospect_evaluate": RiskTier.C1_ADVISORY,
        "geox_prospect_judge_preview": RiskTier.C1_ADVISORY,
        # IRREVERSIBLE — SEAL + ack_irreversible required
        "geox_prospect_judge_seal": RiskTier.IRREVERSIBLE,
        "geox_task_metabolize_basin": RiskTier.C2_EXECUTE,
        "geox_task_ingest_las_batch": RiskTier.C2_EXECUTE,
        "geox_stratigraphy_run_pipeline": RiskTier.C2_EXECUTE,
    },
    "WEALTH": {
        # READONLY tools
        "wealth_field_macro": RiskTier.READONLY,
        "wealth_mass_networth": RiskTier.READONLY,
        "wealth_flow_liquidity": RiskTier.READONLY,
        "wealth_velocity_runway": RiskTier.READONLY,
        "wealth_energy_productivity": RiskTier.READONLY,
        "wealth_gradient_price": RiskTier.READONLY,
        "wealth_signal_information": RiskTier.READONLY,
        "wealth_signal_evoi": RiskTier.READONLY,
        "wealth_probability_monte_carlo": RiskTier.READONLY,
        "wealth_preference_rank": RiskTier.READONLY,
        "wealth_conservation_capital": RiskTier.READONLY,
        "wealth_density_pi": RiskTier.READONLY,
        "wealth_energy_irr": RiskTier.READONLY,
        "wealth_time_discount": RiskTier.READONLY,
        "wealth_time_payback": RiskTier.READONLY,
        "wealth_gravity_dscr": RiskTier.READONLY,
        "wealth_entropy_risk": RiskTier.READONLY,
        "wealth_entropy_audit": RiskTier.READONLY,
        "wealth_inertia_leverage": RiskTier.READONLY,
        "wealth_inequality_kernel": RiskTier.READONLY,
        "wealth_game_coordination": RiskTier.READONLY,
        "wealth_boundary_governance": RiskTier.READONLY,
        "wealth_governance_verdict": RiskTier.READONLY,
        "wealth_system_registry_status": RiskTier.READONLY,
        "wealth_mcp_health_check": RiskTier.READONLY,
        # C1 — pre-check
        "wealth_synthesize": RiskTier.C1_ADVISORY,
        "wealth_ledger_query": RiskTier.C1_ADVISORY,
        # C2 — SEAL required
        "wealth_ledger_write": RiskTier.IRREVERSIBLE,
        "wealth_value_npv": RiskTier.C1_ADVISORY,
    },
    "WELL": {
        # READONLY tools
        "well_classify_substrate": RiskTier.READONLY,
        "well_measure_gradient": RiskTier.READONLY,
        "well_detect_boundary": RiskTier.READONLY,
        "well_assess_metabolism": RiskTier.READONLY,
        "well_assess_homeostasis": RiskTier.READONLY,
        "well_assess_livelihood": RiskTier.READONLY,
        "well_assess_reliability": RiskTier.READONLY,
        "well_check_repair": RiskTier.READONLY,
        "well_guard_dignity": RiskTier.READONLY,
        "well_validate_vitality": RiskTier.READONLY,
        "well_trace_lineage": RiskTier.READONLY,
        "well_compute_metabolic_flux": RiskTier.READONLY,
        "well_system_registry_status": RiskTier.READONLY,
        "well_mcp_health_check": RiskTier.READONLY,
        # C1 — pre-check
        "well_registry_status": RiskTier.C1_ADVISORY,
    },
}


# ─── arifOS Kernel Client ──────────────────────────────────────────────────────

ARIFOS_KERNEL_URL = os.getenv("ARIFOS_KERNEL_URL", "http://arifosmcp:8080")
ARIFOS_KERNEL_TOKEN = os.getenv("ARIFOS_KERNEL_TOKEN", "")  # Optional auth


def _call_arif_kernel_sync(tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
    """
    Synchronous call to arifOS MCP kernel.
    Falls back to HOLD on network failure (fail-closed).
    """
    import urllib.request

    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params,
            },
        }
    ).encode()

    req = urllib.request.Request(
        f"{ARIFOS_KERNEL_URL}/mcp",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    if ARIFOS_KERNEL_TOKEN:
        req.add_header("Authorization", f"Bearer {ARIFOS_KERNEL_TOKEN}")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            if "result" in result:
                return result["result"]
            elif "error" in result:
                logger.error(f"arifOS kernel error: {result['error']}")
                return {"status": "ERROR", "error": result["error"]}
    except Exception as exc:
        logger.error(f"arifOS kernel call failed: {exc}")
        return {"status": "ERROR", "error": str(exc)}

    return {"status": "ERROR", "error": "Unknown kernel response"}


# ─── Governance Check Result ──────────────────────────────────────────────────


@dataclass
class GovernanceResult:
    verdict: str  # SEAL | HOLD | VOID | SABAR | ADVISORY
    tool: str
    risk_tier: RiskTier
    reason: str
    session_id: str | None = None
    constitution_hash: str | None = None
    requires_ack: bool = False
    raw_judgment: dict | None = None


# ─── Main OrganGovernance Class ───────────────────────────────────────────────


class OrganGovernance:
    """
    Shared governance client for ArifOS organs.

    Each organ (GEOX, WEALTH, WELL) instantiates one of these
    at startup and calls check_governance() at the start of
    every tool handler.
    """

    def __init__(
        self,
        organ_name: str,
        organ_version: str,
        risk_map: dict[str, RiskTier] | None = None,
    ):
        self.organ_name = organ_name
        self.organ_version = organ_version
        self.risk_map = risk_map or TOOL_RISK_MAP.get(organ_name, {})
        self._session_id: str | None = None
        self._constitution_hash: str | None = None
        self._logged_tools: list[str] = []

        logger.info(
            f"OrganGovernance initialized for {organ_name} v{organ_version} "
            f"with {len(self.risk_map)} tool risk classifications"
        )

    @property
    def session_id(self) -> str | None:
        return self._session_id

    def register_session(self, session_id: str, constitution_hash: str) -> None:
        """Bind organ to an arifOS session."""
        self._session_id = session_id
        self._constitution_hash = constitution_hash
        logger.info(
            f"OrganGovernance session bound: {session_id} (constitution={constitution_hash[:8]}...)"
        )

    def get_risk_tier(self, tool_name: str) -> RiskTier:
        """Look up risk tier for a tool. Default to C1 if unknown."""
        return self.risk_map.get(tool_name, RiskTier.C1_ADVISORY)

    def get_certainty_cap(self, tool_name: str) -> CertaintyCap:
        """Look up certainty cap for a tool. Default to SPECULATIVE for safety."""
        return TOOL_CERTAINTY_CAP.get(tool_name, CertaintyCap.SPECULATIVE)

    def check_certainty_cap(
        self,
        tool_name: str,
        output_text: str,
        claimed_certainty: str | None = None,
    ) -> dict[str, Any]:
        """
        Chapter 6 Upgrade: Check if a tool's output exceeds its certainty cap.

        Returns dict with:
          - ok: bool
          - cap: the tool's CertaintyCap
          - overclaim_detected: bool
          - reason: human-readable explanation
        """
        cap = self.get_certainty_cap(tool_name)
        cap_rank = CERTAINTY_CAP_RANK.get(cap, 1)
        overclaim = False
        reason = f"Certainty cap for {tool_name}: {cap.value}"

        # Detect overclaim patterns in output text
        text_lower = (output_text or "").lower()
        overclaim_patterns = {
            CertaintyCap.OBSERVED: [],  # top rank — cannot overclaim
            CertaintyCap.DERIVED: ["verified", "proven", "certain"],
            CertaintyCap.INTERPRETED: ["verified", "proven", "certain", "calculated"],
            CertaintyCap.SPECULATIVE: ["verified", "proven", "certain", "calculated", "likely"],
            CertaintyCap.MYTHIC: [
                "verified",
                "proven",
                "certain",
                "calculated",
                "likely",
                "possible",
            ],
        }
        forbidden = overclaim_patterns.get(cap, [])
        found = [p for p in forbidden if p in text_lower]
        if found:
            overclaim = True
            reason = (
                f"Certainty overclaim detected in {tool_name}: "
                f"cap={cap.value}, forbidden words found={found}. "
                f"F9 ANTI-HANTU: downgrade certainty or provide evidence receipt."
            )

        # If explicit claimed_certainty is provided, validate rank
        if claimed_certainty:
            claimed_rank = CERTAINTY_CAP_RANK.get(claimed_certainty, 99)
            if claimed_rank > cap_rank:
                overclaim = True
                reason = (
                    f"Explicit certainty overclaim: {tool_name} claims {claimed_certainty} "
                    f"but cap is {cap.value}. F9 ANTI-HANTU violation."
                )

        return {
            "ok": not overclaim,
            "cap": cap.value,
            "overclaim_detected": overclaim,
            "reason": reason,
        }

    def check_governance(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        session_id: str | None = None,
        actor_id: str = "organ-governed",
    ) -> GovernanceResult:
        """
        Main governance check. Call this at the start of every tool handler.

        Returns a GovernanceResult with:
          - verdict: SEAL (proceed) | HOLD (wait) | VOID (reject) | ADVISORY (noted)
          - reason: human-readable explanation
          - requires_ack: True if irreversible tool needs explicit ack

        For READONLY: returns SEAL immediately (log only)
        For C1: calls arifOS pre-check, executes anyway
        For C2: calls arifOS, waits for SEAL before proceeding
        For IRREVERSIBLE: calls arifOS, requires SEAL + ack_irreversible=True
        """
        risk_tier = self.get_risk_tier(tool_name)
        effective_session = session_id or self._session_id

        # ── READONLY: log and proceed ──────────────────────────────────────────
        if risk_tier == RiskTier.READONLY:
            self._log_tool_call(tool_name, arguments, "SEAL", risk_tier)
            return GovernanceResult(
                verdict="SEAL",
                tool=tool_name,
                risk_tier=risk_tier,
                reason="READONLY tool — no governance check required",
            )

        # ── IRREVERSIBLE: check ack_irreversible flag ──────────────────────────
        if risk_tier == RiskTier.IRREVERSIBLE:
            if not arguments.get("ack_irreversible", False):
                return GovernanceResult(
                    verdict="HOLD",
                    tool=tool_name,
                    risk_tier=risk_tier,
                    reason=(
                        f"F1 AMANAH: {tool_name} is IRREVERSIBLE. "
                        "Requires ack_irreversible=True in arguments. "
                        "Human consent required before execution."
                    ),
                    requires_ack=True,
                )

        # ── Build candidate for arifOS judgment ───────────────────────────────
        candidate = {
            "action": f"{self.organ_name}_ORGAN:{tool_name}",
            "description": (
                f"{self.organ_name} organ tool '{tool_name}' with risk tier {risk_tier.value}"
            ),
            "actor_id": actor_id,
            "organ": self.organ_name,
            "tool": tool_name,
            "risk_tier": risk_tier.value,
            "arguments_keys": list(arguments.keys()),
        }

        # ── Call arifOS kernel: arif_judge ──────────────────────────
        judge_params = {
            "mode": "judge",
            "candidate": json.dumps(candidate),
            "session_id": effective_session,
            "actor_id": actor_id,
        }

        logger.info(f"GOVERNANCE CHECK: {tool_name} [{risk_tier.value}] → calling arifOS kernel")

        kernel_result = _call_arif_kernel_sync("arif_judge", judge_params)

        # Parse verdict from kernel response
        verdict = "HOLD"  # fail-closed default
        reason = "arifOS kernel unreachable — fail-closed"

        if isinstance(kernel_result, dict):
            verdict = kernel_result.get("verdict", "HOLD")
            judgment = kernel_result.get("judgment", {})
            reason = judgment.get("reason", kernel_result.get("reason", "No reason provided"))

            # Extract constitution hash if returned
            if "constitution_hash" in kernel_result:
                self._constitution_hash = kernel_result["constitution_hash"]

        result = GovernanceResult(
            verdict=verdict,
            tool=tool_name,
            risk_tier=risk_tier,
            reason=reason,
            session_id=effective_session,
            constitution_hash=self._constitution_hash,
            raw_judgment=kernel_result if isinstance(kernel_result, dict) else None,
            requires_ack=(risk_tier == RiskTier.IRREVERSIBLE),
        )

        # ── Log regardless of verdict ──────────────────────────────────────────
        self._log_tool_call(tool_name, arguments, verdict, risk_tier)

        return result

    def _log_tool_call(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        verdict: str,
        risk_tier: RiskTier,
    ) -> None:
        """Append to tool call log (in-memory, surfaced to arifOS via kernel call)."""
        entry = {
            "ts": time.time(),
            "organ": self.organ_name,
            "tool": tool_name,
            "verdict": verdict,
            "risk_tier": risk_tier.value,
            "session_id": self._session_id,
        }
        self._logged_tools.append(entry)

        # Also log to arifOS kernel for VAULT999
        if verdict in ("SEAL", "HOLD", "VOID"):
            try:
                _call_arif_kernel_sync(
                    "arif_judge",
                    {
                        "mode": "judge",
                        "candidate": json.dumps(
                            {
                                "action": f"ORGAN_LOG:{self.organ_name}:{tool_name}",
                                "description": f"Organ tool call logged for {self.organ_name}",
                                "actor_id": "organ-governance-logger",
                                "verdict": verdict,
                            }
                        ),
                        "session_id": self._session_id,
                        "actor_id": "organ-governance-logger",
                    },
                )
            except Exception:
                pass  # Non-fatal — logging failure doesn't block tool execution


# ─── Convenience Decorator ─────────────────────────────────────────────────────


def governed(
    tool_name: str,
    governance: OrganGovernance,
    session_id: str | None = None,
    actor_id: str = "organ-governed",
):
    """
    Decorator that wraps a tool handler with governance checks.

    Usage:
        @governed("geox_prospect_judge_seal", governance=geox_gov)
        def geox_prospect_judge_seal(tool_name, arguments, ...):
            # Tool execution — only reached if governance returns SEAL
            ...
    """

    def decorator(func):
        def wrapper(arguments: dict[str, Any], **kwargs):
            result = governance.check_governance(
                tool_name=tool_name,
                arguments=arguments,
                session_id=session_id,
                actor_id=actor_id,
            )
            if result.verdict == "HOLD":
                return {
                    "status": "HOLD",
                    "tool": tool_name,
                    "reason": result.reason,
                    "requires_ack": result.requires_ack,
                    "guard": "ORGAN_GOVERNANCE",
                }
            if result.verdict == "VOID":
                return {
                    "status": "VOID",
                    "tool": tool_name,
                    "reason": result.reason,
                    "guard": "ORGAN_GOVERNANCE",
                }
            # SEAL or ADVISORY — proceed with execution
            return func(arguments=arguments, **kwargs)

        return wrapper

    return decorator


# ─── Risk Leash Config (for mcporter.json integration) ────────────────────────

ORGAN_MCP_SERVERS: dict[str, dict[str, str]] = {
    "geox": {
        "url": "http://geox_eic:8081",
        "transport": "streamable-http",
        "organ": "GEOX",
        "description": "Earth intelligence — subsurface, seismic, well analysis",
    },
    "wealth-organ": {
        "url": "http://wealth-organ:8082",
        "transport": "streamable-http",
        "organ": "WEALTH",
        "description": "Capital intelligence — NPV, IRR, entropy, inequality",
    },
    "well": {
        "url": "http://well:8083",
        "transport": "streamable-http",
        "organ": "WELL",
        "description": "Biological substrate — vitality, dignity, gradient",
    },
}
