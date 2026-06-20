"""
arifOS Vault Layer — Receipts and lineage primitives.

Per executive verdict: "VAULT999 = sealed constitutional memory."
This package provides typed receipts for:
- Lineage (OpenLineage-style)
- Evidence (claim + witness chain)
- Irreversible action (888_HOLD trigger)
"""

from .evidence_receipt import EvidenceReceipt
from .irreversible_action_receipt import IrreversibleActionReceipt
from .lineage_receipt import LineageReceipt

__all__ = ["LineageReceipt", "EvidenceReceipt", "IrreversibleActionReceipt"]
