"""
APEX (Soul/Ψ) - The Judge

Unified namespace for arifOS Soul engine.

Modules:
    kernel.py           - APEX judicial kernel (APEXJudicialCore)
    psi_kernel.py       - APEX PSI kernel (PsiKernel)
    governance/         - VAULT-999 governance
        ledger.py       - Hash-chained ledger
        merkle.py       - Merkle tree sealing
        proof_of_governance.py  # Proof system
    judicial/           # Judicial functions
    contracts/          # APEX contracts

Note: APEXEngine removed - use APEXJudicialCore from .kernel instead
"""

from .kernel import APEXJudicialCore
from .psi_kernel import PsiKernel

__all__ = ["APEXJudicialCore", "PsiKernel"]  # APEXEngine and APEXKernel removed - classes don't exist
