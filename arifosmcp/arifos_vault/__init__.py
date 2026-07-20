"""
arifOS Vault Layer — Receipts and lineage primitives.

Per executive verdict: "VAULT999 = sealed constitutional memory."
This package provides typed receipts for:
- Lineage (OpenLineage-style)
- Evidence (claim + witness chain)
- Irreversible action (888_HOLD trigger)
"""

from .claim_receipt import ArifOSClaimReceipt, create_claim_receipt, verify_claim_receipt
from .evidence_receipt import EvidenceReceipt
from .irreversible_action_receipt import IrreversibleActionReceipt
from .lineage_receipt import LineageReceipt
from .truth_enforcement import (
    assign_evidence_layer,
    claim_must_use_receipt,
    enforce_claim,
    enforce_for_warga,
    get_warga_config,
    hermes_claim_to_receipt,
    require_receipt,
)

__all__ = [
    "LineageReceipt",
    "EvidenceReceipt",
    "IrreversibleActionReceipt",
    "ArifOSClaimReceipt",
    "create_claim_receipt",
    "verify_claim_receipt",
    "assign_evidence_layer",
    "enforce_claim",
    "enforce_for_warga",
    "claim_must_use_receipt",
    "get_warga_config",
    "hermes_claim_to_receipt",
    "require_receipt",
]
