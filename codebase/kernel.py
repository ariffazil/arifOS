"""
Codebase Kernel Manager (v53 Hybrid)
Central registry for the Trinity Cores (Proxies).

This module instantiates the Proxy Kernels that bridge to arifOS Core.
It provides the 'manager' expected by the Bridge.
"""

from codebase.engines.agi.kernel import AGINeuralCore
from codebase.engines.asi.kernel import ASIActionCore
from codebase.engines.apex.kernel import APEXJudicialCore

# Import 000 logic from arifOS Monolith (The Source of Truth)
try:
    from arifos.mcp.tools.mcp_aaa import mcp_000_init
except ImportError:
    # Fallback if mcp_aaa is not found (should not happen in valid env)
    async def mcp_000_init(**kwargs):
        return {"status": "VOID", "error": "mcp_aaa unavailable"}

class KernelManager:
    """
    Manages the lifecycle of the Trinity Engines (Proxies).
    """
    def __init__(self):
        # Instantiate Proxies
        self.agi = AGINeuralCore()
        self.asi = ASIActionCore()
        # APEX usually requires init args in v52, but Proxy might handle defaults
        # Checked arifos/core/apex/kernel.py: __init__() takes no args. Safe.
        self.apex = APEXJudicialCore()
        
    def get_agi(self):
        return self.agi
        
    def get_asi(self):
        return self.asi
        
    def get_apex(self):
        return self.apex
        
    def get_prompt_router(self):
        # Placeholder for 111 prompt router if needed
        async def mock_router(text):
            return {"status": "routed", "text": text}
        return mock_router

    async def init_session(self, action: str, kwargs: dict):
        """
        Delegates initialization to the Monolith's mcp_000_init.
        Bridge packs kwargs, we unpack for the function.
        """
        # Clean kwargs to match signature if needed, or pass through
        # mcp_000_init args: action, query, session_id, authority_token, context
        return await mcp_000_init(
            action=action,
            query=kwargs.get("query", ""),
            session_id=kwargs.get("session_id"),
            authority_token=kwargs.get("authority_token"),
            context=kwargs.get("context")
        )

# Singleton Instance
_MANAGER = None

def get_kernel_manager():
    global _MANAGER
    if not _MANAGER:
        _MANAGER = KernelManager()
    return _MANAGER
