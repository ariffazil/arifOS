"""
arifOS Policy Layer — Substrate governance primitives.

Per the executive verdict (2026-06-15): "OPA/Cedar should help arifOS decide policy,
but arifOS remains the constitutional authority."

This package provides:
- opa_bridge.py: OPA HTTP eval client + policy bundle loader
- cedar_bridge.py: Cedar policy evaluator (Phase 2, stub)
- rego/: policy bundles (lease, tool, mutation)

Constitutional binding:
- F8 LAW: All policy decisions route through arifOS
- F11 AUDIT: Every policy eval is traced via OpenTelemetry
- F13 SOVEREIGN: arifOS can always override OPA verdicts
"""

from .cedar_bridge import CedarBridge  # Phase 2
from .opa_bridge import OPABridge, PolicyInput, PolicyVerdict

__all__ = ["OPABridge", "PolicyVerdict", "PolicyInput", "CedarBridge"]
