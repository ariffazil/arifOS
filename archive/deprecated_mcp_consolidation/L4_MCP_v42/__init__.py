"""
L4_MCP - Black-box Constitutional Authority via Single Tool.

This layer exposes exactly ONE tool: `apex.verdict`

All internal governance (Floors F1-F9, W@W weighting, 000→999 routing,
cooling ledger) runs internally and is NOT directly callable.

Architecture:
    External (MCP boundary):
        └── apex.verdict(task, context) → {verdict, reasons, evidence, constraints}

    Internal (hidden):
        ├── Floors (F1–F9, parallel evaluation)
        ├── W@W Weighting (confidence metrics)
        ├── 000→999 Pipeline (routing logic)
        └── cooling_ledger (append-only audit log)

Security Invariants:
    ✓ Fail-closed (ledger down → VOID)
    ✓ Atomic (one call → one verdict)
    ✓ Non-bypassable (internals not exposed)
    ✓ Single authority (apex.verdict only)
    ✓ Auditable (everything logged)

Version: v45.1.0
Status: PRODUCTION
Layer: L4 (Reclaimed from deprecated status)
"""

__version__ = "45.1.0"
__layer__ = "L4_MCP"
__purpose__ = "Black-box Constitutional Authority"
