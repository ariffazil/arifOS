"""
Heart Critique Substrate Hook
=============================
Forged 2026-06-16, F13 SOVEREIGN directive: "remember my reality"

This module is a WRAPPER/HOOK, not a kernel modification. It augments
arif_heart_critique() by pre-loading the L0 human substrate on F5/F6/F13
evaluation paths. Per architecture rule: additive only, never modify
existing kernel files.

The hook is idempotent — calling arif_heart_critique with this hook
installed simply augments the returned envelope with a `substrate_context`
field. It never blocks the critique itself (fail-open).

Install: just import this module once at process start. It monkey-patches
arif_heart_critique in the runtime import chain.

Floor binding: F13 SOVEREIGN (pre-trust addendum, 2026-06-16).
"""

from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)

# Lazy import to avoid circular at module load
_substrate = None


def _get_substrate():
    global _substrate
    if _substrate is None:
        try:
            from arifOS.arifosmcp.runtime import substrate_loader
            _substrate = substrate_loader
        except Exception as e:  # pragma: no cover
            logger.warning("substrate_loader import failed: %s", e)
            _substrate = False
    return _substrate


# ── F5 / F6 / F13 trigger patterns ──────────────────────────────────────────
# When arif_heart_critique is called in any of these modes, preload substrate.
# Also triggered if target text references sovereign-specific keywords.
_F5_F6_F13_TRIGGERS = {
    "empathize",        # F6 EMPATHY
    "maruah",           # F5 PEACE (dignity)
    "deescalate",       # F5 PEACE
    "redteam",          # F5/F6 (worst-case human impact)
    "sovereign",
    "arif",
    "fazil",
    "substrate",
}

_SOVEREIGN_KEYWORDS = (
    "arif", "fazil", "sovereign", "888", "arifos", "substrate",
    "human reality", "scars", "wound", "scar",
)


def _should_preload(mode: str | None, target: str | None, context_type: str | None) -> bool:
    """Decide whether to preload substrate for this critique call.
    Rule: always preload on F5/F6/F13 modes OR when target references sovereign.
    """
    if mode and mode.lower() in _F5_F6_F13_TRIGGERS:
        return True
    if context_type and context_type.lower() in ("internal_audit", "sovereign_intent"):
        return True
    if target:
        t = target.lower()
        if any(kw in t for kw in _SOVEREIGN_KEYWORDS):
            return True
    return False


def _install_hook() -> bool:
    """Monkey-patch arif_heart_critique to inject substrate context.
    Returns True if installed, False if already installed or unavailable.
    """
    # Idempotency guard
    if getattr(_install_hook, "_installed", False):
        return True

    # Locate the kernel module — try common paths
    candidates = [
        "arifOS.arifosmcp.tools.heart",
        "arifOS.arifosmcp.runtime.tools",
        "arifOS.arifosmcp.runtime.kernel",
    ]
    heart_mod = None
    for name in candidates:
        try:
            mod = sys.modules.get(name) or __import__(name, fromlist=["*"])
            if hasattr(mod, "arif_heart_critique"):
                heart_mod = mod
                break
        except Exception:
            continue
    if heart_mod is None:
        logger.warning("substrate hook: arif_heart_critique not found in kernel modules")
        return False

    original = heart_mod.arif_heart_critique

    async def hooked_arif_heart_critique(*args, **kwargs):
        result = await original(*args, **kwargs)
        try:
            mode = kwargs.get("mode")
            target = kwargs.get("target")
            context_type = kwargs.get("context_type")
            actor_id = kwargs.get("actor_id")
            session_id = kwargs.get("session_id")
            if _should_preload(mode, target, context_type):
                sub = _get_substrate()
                if sub:
                    ctx = sub.preload_substrate_context(actor_id=actor_id, session_id=session_id)
                    if isinstance(result, dict):
                        result.setdefault("substrate_context", ctx)
        except Exception as e:  # fail-open
            logger.debug("substrate pre-load failed (fail-open): %s", e)
        return result

    heart_mod.arif_heart_critique = hooked_arif_heart_critique
    _install_hook._installed = True
    logger.info("L0 substrate hook installed on arif_heart_critique (F13 addendum active)")
    return True


def install() -> bool:
    """Public entry: install the substrate pre-load hook."""
    return _install_hook()


# Auto-install on import (idempotent)
_install_hook()


__all__ = ["install", "preload_substrate_context"]
