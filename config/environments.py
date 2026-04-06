"""
arifOS Environment Configuration
Handles dual-sovereignty deployment: VPS (Sovereign) vs Horizon (Public)
"""

import os
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class DeploymentMode(Enum):
    """Deployment sovereignty modes."""
    VPS_SOVEREIGN = "vps"          # Your Hostinger VPS - full sovereignty
    HORIZON_PUBLIC = "horizon"      # Prefect Horizon - public ambassador
    LOCAL_DEV = "local"             # Local development
    TEST = "test"                   # Test environment


class ToolAccessClass(Enum):
    """Public exposure policy for gatewayed tools."""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    SOVEREIGN_ONLY = "sovereign-only"


@dataclass
class EnvironmentConfig:
    """Environment-specific configuration."""
    mode: DeploymentMode
    name: str
    base_url: str
    vault_backend: str
    memory_backend: str
    rate_limit_enabled: bool
    auth_required: bool
    thermo_budget_multiplier: float
    constitutional_floors: list[str]  # Which F1-F13 floors are enforced


# =============================================================================
# SOVEREIGN KERNEL (VPS) - Maximum constitutional enforcement
# =============================================================================
VPS_CONFIG = EnvironmentConfig(
    mode=DeploymentMode.VPS_SOVEREIGN,
    name="arifOS Sovereign Kernel",
    base_url="https://arifos.arif-fazil.com",
    vault_backend="postgresql",      # Local PostgreSQL
    memory_backend="redis",          # Local Redis
    rate_limit_enabled=True,
    auth_required=True,              # Strict auth
    thermo_budget_multiplier=1.0,    # Full thermodynamic budget
    constitutional_floors=[f"F{i}" for i in range(1, 14)],  # All F1-F13
)

# =============================================================================
# PUBLIC AMBASSADOR (Horizon) - Public access, limited scope
# =============================================================================
HORIZON_CONFIG = EnvironmentConfig(
    mode=DeploymentMode.HORIZON_PUBLIC,
    name="arifOS Horizon Gateway",
    base_url="https://arifos.fastmcp.app",
    vault_backend="external",        # External DB service
    memory_backend="external",       # External Redis
    rate_limit_enabled=True,
    auth_required=False,             # Public access (tools decide)
    thermo_budget_multiplier=0.5,    # Conservative budget
    constitutional_floors=[          # Gateway-enforced floors
        "F1",  # Truth
        "F2",  # Evidence
        "F3",  # Uncertainty
        "F5",  # Empathy
        "F7",  # Humility
        "F9",  # Security (basic)
        "F12", # Audit
    ],
)

# =============================================================================
# LOCAL DEVELOPMENT
# =============================================================================
LOCAL_CONFIG = EnvironmentConfig(
    mode=DeploymentMode.LOCAL_DEV,
    name="arifOS Development",
    base_url="http://localhost:8080",
    vault_backend="sqlite",          # SQLite for local
    memory_backend="memory",         # In-memory
    rate_limit_enabled=False,
    auth_required=False,
    thermo_budget_multiplier=2.0,    # Relaxed for dev
    constitutional_floors=["F1", "F2", "F3"],  # Basic only
)


def get_environment() -> EnvironmentConfig:
    """
    Detect and return the current environment configuration.
    
    Detection order:
    1. ARIFOS_DEPLOYMENT env var
    2. Horizon-specific env vars
    3. VPS-specific files/vars
    4. Default to local
    """
    deployment = os.getenv("ARIFOS_DEPLOYMENT", "").lower()
    
    # Explicit configuration
    if deployment == "horizon":
        return HORIZON_CONFIG
    elif deployment == "vps":
        return VPS_CONFIG
    elif deployment == "local":
        return LOCAL_CONFIG
    
    # Auto-detection for Horizon
    if os.getenv("HORIZON_DEPLOYMENT") or os.getenv("PREFECT_CLOUD_API_URL"):
        return HORIZON_CONFIG
    
    # Auto-detection for VPS
    if os.path.exists("/etc/arifos-vps") or os.getenv("VPS_HOSTNAME"):
        return VPS_CONFIG
    
    # Default to local
    return LOCAL_CONFIG


def is_sovereign() -> bool:
    """Check if running in sovereign (VPS) mode."""
    return get_environment().mode == DeploymentMode.VPS_SOVEREIGN


def is_public() -> bool:
    """Check if running in public (Horizon) mode."""
    return get_environment().mode == DeploymentMode.HORIZON_PUBLIC


# =============================================================================
# Tool visibility and access policy
# =============================================================================

TOOL_ACCESS_POLICY = {
    # Public-safe tools that Horizon can expose directly through the gateway.
    "init_anchor": ToolAccessClass.PUBLIC.value,
    "arifOS_kernel": ToolAccessClass.PUBLIC.value,
    "apex_judge": ToolAccessClass.PUBLIC.value,
    "apex_soul": ToolAccessClass.PUBLIC.value,
    "agi_mind": ToolAccessClass.PUBLIC.value,
    "asi_heart": ToolAccessClass.PUBLIC.value,
    "physics_reality": ToolAccessClass.PUBLIC.value,
    "math_estimator": ToolAccessClass.PUBLIC.value,
    "architect_registry": ToolAccessClass.PUBLIC.value,
    "compat_probe": ToolAccessClass.PUBLIC.value,
    "agi_reason": ToolAccessClass.PUBLIC.value,
    "agi_reflect": ToolAccessClass.PUBLIC.value,
    "asi_critique": ToolAccessClass.PUBLIC.value,
    "asi_simulate": ToolAccessClass.PUBLIC.value,
    "reality_compass": ToolAccessClass.PUBLIC.value,
    "reality_atlas": ToolAccessClass.PUBLIC.value,
    "search_reality": ToolAccessClass.PUBLIC.value,
    "ingest_evidence": ToolAccessClass.PUBLIC.value,
    "check_vital": ToolAccessClass.PUBLIC.value,
    "audit_rules": ToolAccessClass.PUBLIC.value,
    "search_tool": ToolAccessClass.PUBLIC.value,
    "fetch_tool": ToolAccessClass.PUBLIC.value,

    # Authenticated tools can be proxied later once Horizon auth continuity
    # is bound to arifOS sessions end-to-end.
    "vault_ledger": ToolAccessClass.AUTHENTICATED.value,
    "engineering_memory": ToolAccessClass.AUTHENTICATED.value,
    "shared_memory": ToolAccessClass.AUTHENTICATED.value,
    "agent_logbook": ToolAccessClass.AUTHENTICATED.value,
    "verify_vault_ledger": ToolAccessClass.AUTHENTICATED.value,
    "init_000_get_deployment": ToolAccessClass.AUTHENTICATED.value,
    "init_000_get_provider_soul": ToolAccessClass.AUTHENTICATED.value,
    "init_000_get_session_anchor": ToolAccessClass.AUTHENTICATED.value,
    "init_000_log_drift_event": ToolAccessClass.AUTHENTICATED.value,

    # Sovereign-only tools must remain on the VPS execution plane.
    "code_engine": ToolAccessClass.SOVEREIGN_ONLY.value,
    "vault_seal": ToolAccessClass.SOVEREIGN_ONLY.value,
    "seal_vault_commit": ToolAccessClass.SOVEREIGN_ONLY.value,
    "forge": ToolAccessClass.SOVEREIGN_ONLY.value,
    "metabolic_loop_router": ToolAccessClass.SOVEREIGN_ONLY.value,
    "agi_asi_forge_handler": ToolAccessClass.SOVEREIGN_ONLY.value,
    "reason_mind_synthesis": ToolAccessClass.SOVEREIGN_ONLY.value,
    "agentzero_engineer": ToolAccessClass.SOVEREIGN_ONLY.value,
    "agentzero_validate": ToolAccessClass.SOVEREIGN_ONLY.value,
    "agentzero_armor_scan": ToolAccessClass.SOVEREIGN_ONLY.value,
    "agentzero_hold_check": ToolAccessClass.SOVEREIGN_ONLY.value,
    "agentzero_memory_query": ToolAccessClass.SOVEREIGN_ONLY.value,
}


def is_tool_available(tool_name: str) -> bool:
    """Check if a tool should be available in current environment."""
    env = get_environment().mode.value
    access_class = TOOL_ACCESS_POLICY.get(tool_name, ToolAccessClass.SOVEREIGN_ONLY.value)
    if env == "horizon":
        return access_class == ToolAccessClass.PUBLIC.value
    if env in {"vps", "local"}:
        return True
    return False


def get_tool_access_class(tool_name: str) -> str:
    """Return the gateway access class for a tool."""
    return TOOL_ACCESS_POLICY.get(tool_name, ToolAccessClass.SOVEREIGN_ONLY.value)


# =============================================================================
# Environment-Specific Server Configuration
# =============================================================================

def get_server_config() -> dict:
    """Get FastMCP server configuration for current environment."""
    env = get_environment()
    
    base_config = {
        "name": env.name,
        "version": os.getenv("ARIFOS_VERSION", "2026.03.25"),
    }
    
    if env.mode == DeploymentMode.VPS_SOVEREIGN:
        base_config.update({
            "strict_input_validation": True,
            "mask_error_details": False,  # Full error details for debugging
            "on_duplicate_tools": "error",
        })
    
    elif env.mode == DeploymentMode.HORIZON_PUBLIC:
        base_config.update({
            "strict_input_validation": True,
            "mask_error_details": True,   # Hide internal errors
            "on_duplicate_tools": "warn",
        })
    
    return base_config
