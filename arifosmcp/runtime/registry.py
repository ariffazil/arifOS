"""
arifosmcp/runtime/registry.py — Internal Model Registry Data Layer
══════════════════════════════════════════════════════════════════

Direct filesystem access to the arifOS Model Registry v2.
No network calls, pure data ingestion for organ deepening.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from arifosmcp.runtime.public_surface import CANONICAL_13
from arifosmcp.schemas.model_card import (
    ModelAnchor,
    ModelGovernanceCard,
    RiskLeash,
    RuntimeTruth,
    SelfClaimBoundary,
    ShadowProfile,
)

_HERE = Path(__file__).resolve()
_REPO_ROOT = _HERE.parents[2]


def _candidate_registry_roots() -> list[Path]:
    env_root = os.environ.get("ARIFOS_REGISTRY_ROOT")
    candidates = [
        Path(env_root).expanduser() if env_root else None,
        Path("/root/arifos-model-registry"),  # LIVE spine (GitHub canonical, 2026-06-05)
        Path("/app/registry"),  # Docker default
        Path(
            "/root/arifOS/registry"
        ),  # DEPRECATED — 3-week stale ghost (May 15). Kept as fallback.
        _REPO_ROOT / "registry",  # Relative to arifOS repo
        _REPO_ROOT / "arifos-model-registry",  # Legacy relative
        _REPO_ROOT / "00_legacy_materials" / "arifOS-upstream" / "archive",
    ]
    return [path for path in candidates if path is not None]


def _resolve_registry_paths() -> tuple[Path, Path, Path, Path]:
    for root in _candidate_registry_roots():
        models = root / "models"
        souls = root / "provider_souls"
        runtime = root / "runtime_profiles"
        if models.exists() and souls.exists():
            return root, models, souls, runtime

    fallback_root = _candidate_registry_roots()[0]
    return (
        fallback_root,
        fallback_root / "models",
        fallback_root / "provider_souls",
        fallback_root / "runtime_profiles",
    )


REGISTRY_ROOT, MODELS_PATH, SOULS_PATH, RUNTIME_PATH = _resolve_registry_paths()

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
    """Load model spec by key (provider/family/variant). Returns v3 5-layer passport."""
    # 1. Flat lookup (legacy / short key)
    flat_path = MODELS_PATH / f"{model_key}.json"
    if flat_path.exists():
        return load_json(flat_path)
    # 2. Nested lookup (canonical catalog path: provider/family/variant)
    nested_path = MODELS_PATH / f"{model_key}.json"
    if nested_path.exists():
        return load_json(nested_path)
    # 3. Deep search fallback (search all subdirs for basename match)
    basename = f"{model_key}.json"
    for candidate in MODELS_PATH.rglob(basename):
        return load_json(candidate)
    return {}


def get_provider_soul(soul_key: str) -> dict:
    """Load provider soul profile."""
    return load_json(SOULS_PATH / f"{soul_key}.json")


def get_runtime_truth(deployment_id: str) -> dict:
    """Load runtime deployment profile."""
    return load_json(RUNTIME_PATH / f"{deployment_id}.json")


def derive_soul_key(model_spec: dict) -> str:
    """Derive soul key from model spec (prefer identity.soul_key, fallback to provider_family)."""
    # v3 schema: identity.soul_key
    identity = model_spec.get("identity", {})
    soul_key = identity.get("soul_key", "")
    if soul_key:
        return soul_key
    # Legacy fallback
    provider = identity.get("provider") or model_spec.get("provider", "")
    family = identity.get("family") or model_spec.get("model_family", "")
    if provider == "deepseek":
        return "deepseek"
    if provider == "minimax":
        return "minimax_m27"
    return f"{provider}_{family}"


def build_governance_card(
    session_id: str, declared_model_key: str, deployment_id: str = "vps_main_arifos"
) -> ModelGovernanceCard:
    """Assemble the full model_governance_card with graceful fallback."""
    is_degraded = False
    try:
        model_spec = get_model_spec(declared_model_key)
        identity = model_spec.get("identity", {})
        governance = model_spec.get("governance", {})
        model_spec.get("lifecycle", {})

        soul_key = derive_soul_key(model_spec) if model_spec else "unknown"
        soul = get_provider_soul(soul_key)
        runtime = get_runtime_truth(deployment_id)

        if not model_spec or not soul or not runtime:
            raise ValueError("Registry data incomplete")

        # Shadow profile derivation (embedded in soul or defaults)
        shadow_raw = soul.get(
            "shadow_profile",
            {
                "angel": soul.get("in_one_sentence", "standard capability"),
                "shadow": "generic drift",
                "paradox": "strength as limitation",
                "control_laws": ["verify all claims", "cite sources"],
                "tripwires": ["identity overclaim", "tool overclaim"],
            },
        )
        shadow_profile = ShadowProfile(
            angel=shadow_raw.get("angel"),
            shadow=shadow_raw.get("shadow"),
            paradox=shadow_raw.get("paradox"),
            control_laws=shadow_raw.get("control_laws", []),
            tripwires=shadow_raw.get("tripwires", []),
        )

        # Risk leash mapping — uses v3 governance fields
        risk_leash = RiskLeash(
            primary_control="certainty_discipline",
            risk_tier=governance.get("risk_tier", "medium"),
            allowed_organs=governance.get("allowed_organs", []),
            forbidden_organs=governance.get("forbidden_organs", []),
            max_action_class=governance.get("max_action_class", "analyze"),
            apex_score=governance.get("apex_score"),
            amanah_score=governance.get("amanah_score"),
            required_behaviors=soul.get("reasoning_style", []),
            forbidden_behaviors=[
                "claiming unverified identity",
                "claiming unavailable tools",
                "claiming unverified memory",
            ],
        )
        identity_verified = True

    except Exception as e:
        # ── Graceful Degraded Card (Fix 4) ──
        is_degraded = True
        declared_provider = (
            declared_model_key.split("/")[0] if "/" in declared_model_key else "unknown"
        )
        identity = {"provider": declared_provider, "family": "unknown"}
        governance = {"risk_tier": "degraded"}
        soul = {"soul_label": "degraded_clerk_fallback"}
        runtime = {
            "provider_capabilities": ["read", "write"],
            "tools_live": CANONICAL_ARIFOS_TOOLS,
            "arifos_public_tools": CANONICAL_ARIFOS_TOOLS,
            "verified_arifos_tools": CANONICAL_ARIFOS_TOOLS,
            "web_on": False,
            "side_effects_allowed": False,
            "memory_mode": "session_only",
        }
        shadow_profile = ShadowProfile(status="registry_unavailable", error=str(e))
        risk_leash = RiskLeash(status="registry_unavailable")
        identity_verified = False
        soul_key = "fallback"

    boundary_raw = runtime.get(
        "self_claim_boundary",
        {
            "identity": "provider_family_only_unless_verified",
            "tools": "verified_only",
            "knowledge": "mark_verified_vs_inferred",
            "actions": "mark_executed_vs_suggested",
        },
    )
    self_claim_boundary = SelfClaimBoundary(
        identity=boundary_raw.get("identity", "provider_family_only_unless_verified"),
        tools=boundary_raw.get("tools", "verified_only"),
        knowledge=boundary_raw.get("knowledge", "mark_verified_vs_inferred"),
        actions=boundary_raw.get("actions", "mark_executed_vs_suggested"),
    )

    model_anchor = ModelAnchor(
        declared_model_key=declared_model_key,
        verified_model_key=declared_model_key if identity_verified else None,
        provider_key=identity.get("provider"),
        family_key=identity.get("family"),
        soul_key=soul_key,
        soul_label=soul.get("soul_label"),
        identity_verified=identity_verified,
    )

    runtime_truth = RuntimeTruth(
        deployment_id=deployment_id,
        web_on=runtime.get("web_on", False),
        memory_mode=runtime.get("memory_mode", "session_only"),
        provider_capabilities=runtime.get("provider_capabilities", runtime.get("tools_live", [])),
        tools_live=runtime.get("tools_live", []),
        arifos_public_tools=runtime.get("arifos_public_tools", CANONICAL_ARIFOS_TOOLS),
        verified_arifos_tools=runtime.get(
            "verified_arifos_tools",
            runtime.get("arifos_public_tools", CANONICAL_ARIFOS_TOOLS),
        ),
        execution_mode=runtime.get("execution_mode", "dry_run"),
        side_effects_allowed=runtime.get("side_effects_allowed", False),
    )

    is_bound = identity_verified and soul_key not in ("unknown", "fallback")

    return ModelGovernanceCard(
        session_id=session_id,
        model_anchor=model_anchor,
        runtime_truth=runtime_truth,
        self_claim_boundary=self_claim_boundary,
        shadow_profile=shadow_profile,
        risk_leash=risk_leash,
        is_bound=is_bound,
        is_degraded=is_degraded,
    )
