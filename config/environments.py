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
    # ══════════════════════════════════════════════════════════════════════
    # Option A+B: Canonical Collapse
    # 9 canonical tools only. Legacy/alias names kept for backward compat
    # (F1 Amanah) but mapped to canonical handlers internally.
    # Internal sub-mode tools (agi_reason, asi_critique, etc.) are
    # SOVEREIGN_ONLY — they are called by canonical tools, not exposed.
    # ══════════════════════════════════════════════════════════════════════

    # ── 9 Canonical PUBLIC tools (v2 names) ─────────────────────────────
    "arifos_init":     ToolAccessClass.PUBLIC.value,      # 000_INIT
    "arifos_sense":    ToolAccessClass.PUBLIC.value,      # 111_SENSE
    "arifos_mind":     ToolAccessClass.PUBLIC.value,      # 333_MIND
    "arifos_kernel":   ToolAccessClass.PUBLIC.value,      # 444_ROUTER
    "arifos_memory":   ToolAccessClass.PUBLIC.value,      # 555_MEMORY
    "arifos_heart":    ToolAccessClass.PUBLIC.value,      # 666_HEART
    "arifos_ops":      ToolAccessClass.PUBLIC.value,      # 777_OPS
    "arifos_judge":    ToolAccessClass.PUBLIC.value,      # 888_JUDGE
    "arifos_vault":    ToolAccessClass.AUTHENTICATED.value,# 999_VAULT (needs audit trail)

    # ── Canonical FORGE + UTILITY ────────────────────────────────────────
    "arifos_forge":    ToolAccessClass.SOVEREIGN_ONLY.value,  # FORGE_010
    "architect_registry": ToolAccessClass.PUBLIC.value,       # M-4_ARCH (introspection)
    "compat_probe":    ToolAccessClass.PUBLIC.value,      # F12 compatibility probe
    "check_vital":     ToolAccessClass.PUBLIC.value,      # VPS telemetry

    # ── DEPRECATED aliases (backward compat — route to canonical) ──────────
    # These names exist in older configs; kept so existing callers don't break.
    # New code should use the canonical v2 names above.
    "init_anchor":       ToolAccessClass.SOVEREIGN_ONLY.value,  # → arifos_init
    "arifOS_kernel":     ToolAccessClass.SOVEREIGN_ONLY.value,  # → arifos_kernel
    "physics_reality":   ToolAccessClass.SOVEREIGN_ONLY.value,  # → arifos_sense
    "agi_mind":          ToolAccessClass.SOVEREIGN_ONLY.value,  # → arifos_mind
    "asi_heart":         ToolAccessClass.SOVEREIGN_ONLY.value,  # → arifos_heart
    "math_estimator":    ToolAccessClass.SOVEREIGN_ONLY.value,  # → arifos_ops
    "apex_soul":         ToolAccessClass.SOVEREIGN_ONLY.value,  # → arifos_judge
    "apex_judge":        ToolAccessClass.SOVEREIGN_ONLY.value,  # → arifos_judge
    "engineering_memory": ToolAccessClass.SOVEREIGN_ONLY.value,# → arifos_memory
    "vault_ledger":      ToolAccessClass.SOVEREIGN_ONLY.value,  # → arifos_vault
    "code_engine":       ToolAccessClass.SOVEREIGN_ONLY.value,  # → arifos_forge

    # ── Internal sub-mode tools — SOVEREIGN_ONLY ──────────────────────────
    # These are called BY canonical tools (via mode= parameters), not directly.
    # Exposing them as public tools causes alias chaos and LLM routing entropy.
    "agi_reason":        ToolAccessClass.SOVEREIGN_ONLY.value,  # internal: arifos_mind mode=reason
    "agi_reflect":       ToolAccessClass.SOVEREIGN_ONLY.value,  # internal: arifos_mind mode=reflect
    "asi_critique":      ToolAccessClass.SOVEREIGN_ONLY.value,  # internal: arifos_heart
    "asi_simulate":      ToolAccessClass.SOVEREIGN_ONLY.value,  # internal: arifos_heart
    "reality_compass":   ToolAccessClass.SOVEREIGN_ONLY.value,  # internal: arifos_sense
    "reality_atlas":     ToolAccessClass.SOVEREIGN_ONLY.value,  # internal: arifos_sense
    "search_reality":    ToolAccessClass.SOVEREIGN_ONLY.value,  # internal: arifos_sense
    "ingest_evidence":   ToolAccessClass.SOVEREIGN_ONLY.value,  # internal: arifos_sense

    # ── Other ──────────────────────────────────────────────────────────────
    "audit_rules":       ToolAccessClass.AUTHENTICATED.value,
    "search_tool":       ToolAccessClass.AUTHENTICATED.value,
    "fetch_tool":        ToolAccessClass.AUTHENTICATED.value,
    "shared_memory":     ToolAccessClass.AUTHENTICATED.value,
    "agent_logbook":     ToolAccessClass.AUTHENTICATED.value,
    "verify_vault_ledger": ToolAccessClass.AUTHENTICATED.value,

    # ── Sovereign-only internal handlers ───────────────────────────────────
    "vault_seal":             ToolAccessClass.SOVEREIGN_ONLY.value,
    "seal_vault_commit":      ToolAccessClass.SOVEREIGN_ONLY.value,
    "forge":                  ToolAccessClass.SOVEREIGN_ONLY.value,
    "metabolic_loop_router":  ToolAccessClass.SOVEREIGN_ONLY.value,
    "agi_asi_forge_handler":  ToolAccessClass.SOVEREIGN_ONLY.value,
    "reason_mind_synthesis":  ToolAccessClass.SOVEREIGN_ONLY.value,
    "agentzero_engineer":     ToolAccessClass.SOVEREIGN_ONLY.value,
    "agentzero_validate":     ToolAccessClass.SOVEREIGN_ONLY.value,
    "agentzero_armor_scan":   ToolAccessClass.SOVEREIGN_ONLY.value,
    "agentzero_hold_check":   ToolAccessClass.SOVEREIGN_ONLY.value,
    "agentzero_memory_query": ToolAccessClass.SOVEREIGN_ONLY.value,
}
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
# Tool visibility and access policy — Option A+B Canonical Collapse (2026-04-11)
# ════════════════════════════════════════════════════════════════════════════════
# Option A+B: 9 canonical PUBLIC tools. Legacy/alias names kept for backward
# compat (F1 Amanah) as SOVEREIGN_ONLY (not routed publicly). Internal
# sub-mode handlers (agi_reason, asi_critique, etc.) are SOVEREIGN_ONLY —
# called by canonical tools via mode=params, never exposed directly.
# ════════════════════════════════════════════════════════════════════════════════

TOOL_ACCESS_POLICY = {
    # ── 9 Canonical PUBLIC tools (v2 names) ─────────────────────────────────
    "arifos_init":     ToolAccessClass.PUBLIC.value,       # 000_INIT
    "arifos_sense":    ToolAccessClass.PUBLIC.value,       # 111_SENSE
    "arifos_mind":     ToolAccessClass.PUBLIC.value,       # 333_MIND
    "arifos_kernel":   ToolAccessClass.PUBLIC.value,       # 444_ROUTER
    "arifos_memory":   ToolAccessClass.PUBLIC.value,       # 555_MEMORY
    "arifos_heart":    ToolAccessClass.PUBLIC.value,       # 666_HEART
    "arifos_ops":      ToolAccessClass.PUBLIC.value,       # 777_OPS
    "arifos_judge":    ToolAccessClass.PUBLIC.value,       # 888_JUDGE
    "architect_registry": ToolAccessClass.PUBLIC.value,    # M-4_ARCH
    "compat_probe":    ToolAccessClass.PUBLIC.value,       # M-6_PROBE
    "check_vital":     ToolAccessClass.PUBLIC.value,       # M-5_VPS

    # ── DEPRECATED aliases (F1 backward compat) ─────────────────────────────
    # Existing callers use these names; canonical handlers accept both.
    # NOT public endpoints — mapped to SOVEREIGN_ONLY so old configs still work.
    "init_anchor":       ToolAccessClass.SOVEREIGN_ONLY.value,   # → arifos_init
    "arifOS_kernel":     ToolAccessClass.SOVEREIGN_ONLY.value,   # → arifos_kernel
    "physics_reality":   ToolAccessClass.SOVEREIGN_ONLY.value,   # → arifos_sense
    "agi_mind":          ToolAccessClass.SOVEREIGN_ONLY.value,    # → arifos_mind
    "asi_heart":         ToolAccessClass.SOVEREIGN_ONLY.value,    # → arifos_heart
    "math_estimator":    ToolAccessClass.SOVEREIGN_ONLY.value,   # → arifos_ops
    "apex_soul":         ToolAccessClass.SOVEREIGN_ONLY.value,   # → arifos_judge
    "apex_judge":        ToolAccessClass.SOVEREIGN_ONLY.value,   # → arifos_judge
    "engineering_memory": ToolAccessClass.SOVEREIGN_ONLY.value,  # → arifos_memory
    "vault_ledger":      ToolAccessClass.SOVEREIGN_ONLY.value,    # → arifos_vault
    "code_engine":       ToolAccessClass.SOVEREIGN_ONLY.value,    # → arifos_forge

    # ── Internal sub-mode handlers — SOVEREIGN_ONLY ─────────────────────────
    # Called by canonical tools through mode= parameters. NOT public endpoints.
    "agi_reason":        ToolAccessClass.SOVEREIGN_ONLY.value,  # arifos_mind mode=reason
    "agi_reflect":       ToolAccessClass.SOVEREIGN_ONLY.value,  # arifos_mind mode=reflect
    "asi_critique":      ToolAccessClass.SOVEREIGN_ONLY.value,  # arifos_heart
    "asi_simulate":      ToolAccessClass.SOVEREIGN_ONLY.value,  # arifos_heart
    "reality_compass":   ToolAccessClass.SOVEREIGN_ONLY.value,  # arifos_sense
    "reality_atlas":     ToolAccessClass.SOVEREIGN_ONLY.value,  # arifos_sense
    "search_reality":    ToolAccessClass.SOVEREIGN_ONLY.value,  # arifos_sense
    "ingest_evidence":   ToolAccessClass.SOVEREIGN_ONLY.value,  # arifos_sense

    # ── AUTHENTICATED ───────────────────────────────────────────────────────
    "arifos_vault":        ToolAccessClass.AUTHENTICATED.value,  # 999_VAULT
    "audit_rules":         ToolAccessClass.AUTHENTICATED.value,
    "search_tool":         ToolAccessClass.AUTHENTICATED.value,
    "fetch_tool":          ToolAccessClass.AUTHENTICATED.value,
    "shared_memory":       ToolAccessClass.AUTHENTICATED.value,
    "agent_logbook":       ToolAccessClass.AUTHENTICATED.value,
    "verify_vault_ledger": ToolAccessClass.AUTHENTICATED.value,
    "init_000_get_deployment":  ToolAccessClass.AUTHENTICATED.value,
    "init_000_get_provider_soul": ToolAccessClass.AUTHENTICATED.value,
    "init_000_get_session_anchor":  ToolAccessClass.AUTHENTICATED.value,
    "init_000_log_drift_event":    ToolAccessClass.AUTHENTICATED.value,

    # ── SOVEREIGN-only internal handlers ─────────────────────────────────────
    "arifos_forge":              ToolAccessClass.SOVEREIGN_ONLY.value,
    "vault_seal":                ToolAccessClass.SOVEREIGN_ONLY.value,
    "seal_vault_commit":         ToolAccessClass.SOVEREIGN_ONLY.value,
    "forge":                     ToolAccessClass.SOVEREIGN_ONLY.value,
    "metabolic_loop_router":     ToolAccessClass.SOVEREIGN_ONLY.value,
    "agi_asi_forge_handler":     ToolAccessClass.SOVEREIGN_ONLY.value,
    "reason_mind_synthesis":     ToolAccessClass.SOVEREIGN_ONLY.value,
    "agentzero_engineer":        ToolAccessClass.SOVEREIGN_ONLY.value,
    "agentzero_validate":        ToolAccessClass.SOVEREIGN_ONLY.value,
    "agentzero_armor_scan":      ToolAccessClass.SOVEREIGN_ONLY.value,
    "agentzero_hold_check":      ToolAccessClass.SOVEREIGN_ONLY.value,
    "agentzero_memory_query":    ToolAccessClass.SOVEREIGN_ONLY.value,
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
