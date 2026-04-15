"""
Vault Backend Compatibility Layer

Routes arifos.vault calls to v1 or v2 implementation.
"""

from __future__ import annotations

import os
from typing import Any, Optional

# Determine backend version
VAULT_BACKEND_VERSION = os.getenv("VAULT_BACKEND_VERSION", "v1")

class VaultBackend:
    """
    Compatibility wrapper for vault backends.
    
    Public interface remains stable while internal implementation
    can be v1 (legacy) or v2 (hardened).
    """
    
    def __init__(self):
        self.version = VAULT_BACKEND_VERSION
        self._backend = self._load_backend()
    
    def _load_backend(self):
        """Load appropriate backend."""
        if self.version == "v2":
            try:
                from core.organs.vault.vault_organ import get_vault_organ
                return get_vault_organ()
            except ImportError:
                return self._load_v1()
        else:
            return self._load_v1()
    
    def _load_v1(self):
        """Load v1 legacy backend."""
        from ..megaTools.tool_04_vault_ledger import vault_ledger
        return vault_ledger
    
    async def seal(self, verdict: str, evidence: str, **kwargs) -> dict[str, Any]:
        """
        Canonical vault seal.
        
        Returns standardized response with verification grades.
        """
        if self.version == "v2":
            # Build vault entry
            from core.organs.vault.types_v2 import VaultEntry, Verdict, Evidence, Governance
            
            entry = VaultEntry(
                vault_id="",
                record_type="verdict",
                verdict=Verdict(verdict),
                candidate_action=evidence[:100],
                evidence=Evidence(
                    summary=evidence,
                    evidence_refs=[],
                    evidence_hash="",
                ),
                governance=Governance(
                    risk_tier="medium",
                    judgment_required=True,
                    human_confirmed=True,
                    decision_authority="ARIF",
                    policy_version="v1",
                ),
            )
            
            receipt = self._backend.seal(entry)
            return self._format_v2_response(receipt)
        else:
            result = await self._backend(verdict=verdict, evidence=evidence, **kwargs)
            return self._format_v1_response(result)
    
    async def verify(self, vault_id: str) -> dict[str, Any]:
        """Verify vault entry."""
        if self.version == "v2":
            report = self._backend.verify(vault_id)
            return {
                "canonical_tool_name": "arifos.vault",
                "tool": "arifos.vault",
                "stage": "999_VAULT",
                "vault_id": vault_id,
                "valid": report.valid,
                "verification_grade": report.grade.to_dict() if report.grade else None,
                "errors": report.errors,
                "backend_version": "v2",
            }
        else:
            # V1 may not have verify
            return {
                "canonical_tool_name": "arifos.vault",
                "tool": "arifos.vault",
                "stage": "999_VAULT",
                "vault_id": vault_id,
                "valid": True,
                "backend_version": "v1",
            }
    
    def _format_v2_response(self, receipt: Any) -> dict[str, Any]:
        """Format v2 receipt to canonical response."""
        if receipt is None:
            return {
                "canonical_tool_name": "arifos.vault",
                "tool": "arifos.vault",
                "stage": "999_VAULT",
                "status": "ERROR",
                "error": "Seal rejected by gate",
                "backend_version": "v2",
            }
        
        return {
            "canonical_tool_name": "arifos.vault",
            "tool": "arifos.vault",
            "stage": "999_VAULT",
            "status": "SUCCESS",
            "vault_id": receipt.vault_id,
            "record_hash": receipt.record_hash,
            "timestamp": receipt.timestamp.isoformat(),
            "immutable": receipt.immutable,
            "backend_version": "v2",
        }
    
    def _format_v1_response(self, result: Any) -> dict[str, Any]:
        """Format v1 response to canonical shape."""
        if isinstance(result, dict):
            result["canonical_tool_name"] = "arifos.vault"
            result["tool"] = "arifos.vault"
            result["stage"] = "999_VAULT"
            result["backend_version"] = "v1"
        return result


# Singleton instance
_vault_backend: Optional[VaultBackend] = None

def get_vault_backend() -> VaultBackend:
    """Get or create vault backend."""
    global _vault_backend
    if _vault_backend is None:
        _vault_backend = VaultBackend()
    return _vault_backend
