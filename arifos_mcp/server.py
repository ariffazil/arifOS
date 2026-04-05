"""
arifOS MCP Server - Canonical deployment entrypoint
═══════════════════════════════════════════════════════════════════════════════

Auto-detects environment and switches between:
• VPS Mode:      Full sovereign execution plane
• Horizon Mode:  Gateway/proxy policy layer over the sovereign VPS

This is the runtime behind the single public entrypoint ``server.py:mcp``.
"""

import logging
import os
import sys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("arifos-gateway")

# ═══════════════════════════════════════════════════════════════════════════════
# CRITICAL: Detect Horizon BEFORE any imports that might fail
# ═══════════════════════════════════════════════════════════════════════════════

def _is_horizon_environment() -> bool:
    """
    Detect if running in Prefect Horizon environment.
    Checks multiple signals to handle both runtime and build-time detection.
    """
    # Primary: Horizon-specific environment variables
    if os.getenv("FASTMCP_CLOUD_URL"):
        return True
    if os.getenv("HORIZON_ENVIRONMENT"):
        return True
    
    # Secondary: FastMCP version check (works during build inspection)
    try:
        import fastmcp
        version = getattr(fastmcp, "__version__", "0.0.0")
        major_version = int(version.split(".")[0])
        if major_version < 3:
            logger.info(f"[DETECT] FastMCP {version} < 3.x → Horizon Mode")
            return True
    except Exception:
        pass
    
    # Tertiary: Check if we're in a containerized/cloud environment
    if os.getenv("KUBERNETES_SERVICE_HOST"):
        return True
    if os.path.exists("/.dockerenv") and not os.getenv("VPS_MODE"):
        # In Docker but not explicitly marked as VPS
        return True
        
    return False


IS_HORIZON = _is_horizon_environment()


# ═══════════════════════════════════════════════════════════════════════════════
# PATH SETUP (Safe for both environments)
# ═══════════════════════════════════════════════════════════════════════════════

def _setup_paths():
    """Ensure arifos_mcp can be found in all environments."""
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    if _current_dir not in sys.path:
        sys.path.insert(0, _current_dir)
    
    # Create fake module structure for Horizon if needed
    if 'arifos_mcp' not in sys.modules:
        import types
        mod = types.ModuleType('arifos_mcp')
        mod.__path__ = [_current_dir]
        sys.modules['arifos_mcp'] = mod


_setup_paths()


# ═══════════════════════════════════════════════════════════════════════════════
# MODE-SPECIFIC IMPORTS (Only import what won't break)
# ═══════════════════════════════════════════════════════════════════════════════

if IS_HORIZON:
    # ═════════════════════════════════════════════════════════════════════════
    # HORIZON MODE: FastMCP 2.x Compatible - No 3.x imports!
    # ═════════════════════════════════════════════════════════════════════════
    logger.info("[BOOT] Horizon environment detected → Gateway Mode")
    logger.info("[BOOT] Public tools proxied to sovereign VPS; sensitive tools remain gated")
    
    # Import the Horizon-safe server (no fastmcp.dependencies!)
    from server_horizon import mcp
    
else:
    # ═════════════════════════════════════════════════════════════════════════
    # VPS MODE: Full Sovereign Kernel (FastMCP 3.x)
    # Falls back to Horizon Ambassador if runtime modules not present
    # ═════════════════════════════════════════════════════════════════════════
    logger.info("[BOOT] VPS environment detected → attempting Full Sovereign Kernel Mode")

    try:
        from arifos_mcp.runtime.server import mcp
        logger.info("[BOOT] Sovereign Kernel loaded ✓")
    except (ImportError, ModuleNotFoundError) as e:
        logger.warning(f"[FALLBACK] arifos_mcp.runtime not available ({e}) → Horizon Gateway Mode")
        logger.info("[BOOT] Falling back to gateway/proxy policy layer")
        from server_horizon import mcp


# Export for FastMCP Cloud / Horizon
__all__ = ["mcp"]

if __name__ == "__main__":
    mcp.run()
