"""
arifosmcp/runtime/registry.py — Internal Model Registry Data Layer
═══════════════════════════════════════════════════════════════════

Direct filesystem access to the arifOS Model Registry v2.
No network calls, pure data ingestion for organ deepening.
"""

import json
import os
from pathlib import Path

from arifosmcp.runtime.public_surface import CANONICAL_13

REGISTRY_ROOT = Path(os.environ.get("ARIFOS_REGISTRY_ROOT", "/root/arifos-model-registry"))
MODELS_PATH = REGISTRY_ROOT / "models"
SOULS_PATH = REGISTRY_ROOT / "provider_souls"
RUNTIME_PATH = REGISTRY_ROOT / "runtime_profiles"

CANONICAL_ARIFOS_TOOLS = list(CANONICAL_13)

# ── Canonical Drift Event Types (Sprint 02 Deepening) ──
DRIFT_EVENT_TYPES = {
    "identity_mismatch",
    "tool_claim_invalid",
    "runtime_overclaim",
    "knowledge_overclaim",
    "role_drift",
    "shadow_activation",
    "self_authorization_attempt",
    "uncertainty_compression",
    "dignity_breach",
    "citation_laundering",
    "context_intoxication",
    "scope_diffusion",
}


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except PermissionError:
        return {}


def get_model_spec(model_key: str) -> dict:
    """Load model spec by key (provider/family/variant)."""
    return load_json(MODELS_PATH / f"{model_key}.json")


def get_provider_soul(soul_key: str) -> dict:
    """Load provider soul profile."""
    return load_json(SOULS_PATH / f"{soul_key}.json")


def get_runtime_truth(deployment_id: str) -> dict:
    """Load runtime deployment profile."""
    return load_json(RUNTIME_PATH / f"{deployment_id}.json")


def derive_soul_key(model_spec: dict) -> str:
    """Derive soul key from model spec (provider + _ + family)."""
    provider = model_spec.get("provider", "")
    family = model_spec.get("model_family", "")
    if provider == "anthropic" and family == "claude":
        return "anthropic_claude"
    if provider == "openai" and family == "gpt":
        return "openai_gpt"
    if provider == "google" and family == "gemini":
        return "google_gemini"
    if provider == "minimax" and family == "minimax":
        return "minimax_m27"
    return f"{provider}_{family}"


def build_governance_card(
    session_id: str, declared_model_key: str, deployment_id: str = "vps_main_arifos"
) -> dict:
    """Assemble the full model_governance_card with graceful fallback."""
    try:
        model_spec = get_model_spec(declared_model_key)
        soul_key = derive_soul_key(model_spec) if model_spec else "unknown"
        soul = get_provider_soul(soul_key)
        runtime = get_runtime_truth(deployment_id)

        if not model_spec or not soul or not runtime:
            raise ValueError("Registry data incomplete")

        # Shadow profile derivation (embedded in soul or defaults)
        shadow_profile = soul.get(
            "shadow_profile",
            {
                "angel": soul.get("in_one_sentence", "standard capability"),
                "shadow": "generic drift",
                "paradox": "strength as limitation",
                "control_laws": ["verify all claims", "cite sources"],
                "tripwires": ["identity overclaim", "tool overclaim"],
            },
        )

        # Risk leash mapping
        risk_leash = {
            "primary_control": "certainty_discipline",
            "required_behaviors": soul.get("reasoning_style", []),
            "forbidden_behaviors": [
                "claiming unverified identity",
                "claiming unavailable tools",
                "claiming unverified memory",
            ],
        }
        identity_verified = True

    except Exception as e:
        # ── Graceful Degraded Card (Task 3) ──
        model_spec = {
            "provider": (
                declared_model_key.split("/")[0] if "/" in declared_model_key else "unknown"
            ),
            "model_family": "unknown",
        }
        soul = {"soul_label": "degraded_clerk_fallback"}
        runtime = {
            "provider_capabilities": ["read", "write"],
            "tools_live": [
                "arif_session_init",
                "arif_sense_observe",
                "arif_evidence_fetch",
                "arif_mind_reason",
                "arif_heart_critique",
                "arif_kernel_route",
                "arif_reply_compose",
                "arif_memory_recall",
                "arif_gateway_connect",
                "arif_judge_deliberate",
                "arif_vault_seal",
                "arif_forge_execute",
                "arif_ops_measure",
            ],
            "arifos_public_tools": CANONICAL_ARIFOS_TOOLS,
            "verified_arifos_tools": CANONICAL_ARIFOS_TOOLS,
            "web_on": False,
            "side_effects_allowed": False,
            "memory_mode": "session_only",
        }
        shadow_profile = {"status": "registry_unavailable", "error": str(e)}
        risk_leash = {"status": "registry_unavailable"}
        identity_verified = False
        soul_key = "fallback"

    return {
        "session_id": session_id,
        "model_anchor": {
            "declared_model_key": declared_model_key,
            "verified_model_key": declared_model_key if identity_verified else None,
            "provider_key": model_spec.get("provider"),
            "family_key": model_spec.get("model_family"),
            "soul_key": soul_key,
            "soul_label": soul.get("soul_label"),
            "identity_verified": identity_verified,
        },
        "runtime_truth": {
            "deployment_id": deployment_id,
            "web_on": runtime.get("web_on", False),
            "memory_mode": runtime.get("memory_mode", "session_only"),
            "provider_capabilities": runtime.get(
                "provider_capabilities", runtime.get("tools_live", [])
            ),
            "tools_live": runtime.get("tools_live", []),
            "arifos_public_tools": runtime.get("arifos_public_tools", CANONICAL_ARIFOS_TOOLS),
            "verified_arifos_tools": runtime.get(
                "verified_arifos_tools",
                runtime.get("arifos_public_tools", CANONICAL_ARIFOS_TOOLS),
            ),
            "execution_mode": runtime.get("execution_mode", "dry_run"),
            "side_effects_allowed": runtime.get("side_effects_allowed", False),
        },
        "self_claim_boundary": runtime.get(
            "self_claim_boundary",
            {
                "identity": "provider_family_only_unless_verified",
                "tools": "verified_only",
                "knowledge": "mark_verified_vs_inferred",
                "actions": "mark_executed_vs_suggested",
            },
        ),
        "shadow_profile": shadow_profile,
        "risk_leash": risk_leash,
    }
