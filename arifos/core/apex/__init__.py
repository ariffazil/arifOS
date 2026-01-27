"""
APEX (Soul/Ψ) - The Judge

Unified namespace for arifOS Soul engine.

Modules:
    engine.py    - APEX engine core logic
    judge.py     - APEX judicial functions (legacy, removed)
    vault/       - VAULT-999 sealing
    paradox/     - APEX paradox codex

Note: VAULT999 moved to arifos.core.memory.vault.vault999
"""

from .engine import APEXEngine

__all__ = ["APEXEngine"]  # render_verdict and VAULT999 removed - moved to codebase structure
