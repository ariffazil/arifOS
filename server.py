"""
Canonical public entrypoint for arifOS deployments.
═══════════════════════════════════════════════════════════════════════════════

This is the only supported public FastMCP entrypoint for both:
1. VPS sovereign execution (full F1-F13 floors)
2. Horizon gateway/proxy mode (public tools only)

Environment-specific behavior is delegated to ``arifosmcp.server``.
No parallel ingress narrative should point at legacy horizon-specific files.

FastMCP Compatibility:
- Entrypoint: server.py:mcp
- Custom Routes: /health, /metadata (Horizon mode)
- Transport: HTTP (port 8000) or STDIO (local mode)
"""

import os
import sys

# ═══════════════════════════════════════════════════════════════════════════════
# HORIZON-SAFE BOOTSTRAP (Import-light for FastMCP Cloud)
# ═══════════════════════════════════════════════════════════════════════════════

_sys_path_inserted = False

def _ensure_path():
    """Ensure project root is in path - safe for both VPS and Horizon."""
    global _sys_path_inserted
    if not _sys_path_inserted:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        _sys_path_inserted = True


def _is_horizon_environment() -> bool:
    """
    Detect Horizon environment WITHOUT importing heavy modules.
    This must work even if FastMCP is not installed (build-time detection).
    """
    # Primary: Explicit deployment flag
    deployment = os.getenv("ARIFOS_DEPLOYMENT", "").lower()
    if deployment == "horizon":
        return True
    
    # Secondary: Horizon-specific env vars
    if os.getenv("FASTMCP_CLOUD_URL"):
        return True
    if os.getenv("FASTMCP_API_KEY"):
        return True
    if os.getenv("HORIZON_ENVIRONMENT"):
        return True
    if os.getenv("HORIZON_DEPLOYMENT"):
        return True
    
    # Tertiary: Container/cloud detection
    if os.getenv("KUBERNETES_SERVICE_HOST"):
        return True
    if os.path.exists("/.dockerenv") and not os.getenv("VPS_MODE"):
        return True
    
    # Quaternary: FastMCP version check (runtime only)
    try:
        import fastmcp
        version = getattr(fastmcp, "__version__", "0.0.0")
        major = int(version.split(".")[0])
        if major < 3:
            return True
    except Exception:
        pass
    
    return False


# Detect mode BEFORE any heavy imports
IS_HORIZON = _is_horizon_environment()

# ═══════════════════════════════════════════════════════════════════════════════
# MODE-SPECIFIC SERVER IMPORT (Deferred until needed)
# ═══════════════════════════════════════════════════════════════════════════════

_ensure_path()

if IS_HORIZON:
    # ═════════════════════════════════════════════════════════════════════════
    # HORIZON MODE: Lightweight gateway, no heavy runtime imports
    # ═════════════════════════════════════════════════════════════════════════
    from ops.runtime.server_horizon import mcp
    
    # Import config only for logging (it's lightweight)
    try:
        from config.environments import get_environment, is_public
        env = get_environment()
        print(f"☁️  HORIZON GATEWAY: {env.name}", file=sys.stderr)
        print(f"   Public tools: /metadata endpoint for policy", file=sys.stderr)
        print(f"   Health check: GET /health", file=sys.stderr)
    except Exception:
        # If config fails, we're still operational
        print("☁️  HORIZON GATEWAY: Public entrypoint active", file=sys.stderr)

else:
    # ═════════════════════════════════════════════════════════════════════════
    # VPS MODE: Full sovereign kernel (or fallback to Horizon if deps missing)
    # ═════════════════════════════════════════════════════════════════════════
    try:
        from arifosmcp.server import mcp
        
        try:
            from config.environments import get_environment, is_sovereign
            env = get_environment()
            if is_sovereign():
                print(f"🔥 SOVEREIGN KERNEL: {env.name}", file=sys.stderr)
                print(f"   All F1-F13 floors enforced", file=sys.stderr)
            else:
                print(f"🏛️  arifOS: {env.mode.value.upper()} mode", file=sys.stderr)
        except Exception:
            print("🔥 SOVEREIGN KERNEL: Full execution plane", file=sys.stderr)
            
    except (ImportError, ModuleNotFoundError) as e:
        # Fallback: Heavy deps missing, use Horizon gateway
        print(f"⚠️  VPS deps unavailable ({e}), falling back to Horizon mode", file=sys.stderr)
        from ops.runtime.server_horizon import mcp


# Export for FastMCP Cloud / Horizon / CLI
__all__ = ["mcp"]
