"""
arifOS MCP Tools - Individual tool implementations.

Each tool wraps existing arifOS functionality for MCP integration.

Phase 1 (Foundation):
    - mcp_000_reset: Session initialization
    - mcp_111_sense: Lane classification & truth threshold determination

Phase 2 (Veto Logic & Core Governance):
    - mcp_222_reflect: Omega0 prediction (epistemic honesty)
    - mcp_444_evidence: Truth grounding via tri-witness convergence
    - mcp_555_empathize: Power-aware recalibration (Peace & kappa)
    - mcp_666_align: ABSOLUTE VETO GATES (F1/F8/F9)
    - mcp_777_forge: Clarity refinement & humility injection
    - mcp_888_judge: Final verdict aggregation (decision tree)

Phase 3 (Cryptographic Audit Trail):
    - mcp_889_proof: Merkle tree proof generation
    - mcp_999_seal: Final verdict sealing & memory routing
"""

# Phase 1 tools (Foundation)
from .mcp_000_reset import mcp_000_reset, mcp_000_reset_sync
from .mcp_111_sense import mcp_111_sense, mcp_111_sense_sync

# Phase 2 tools (Veto Logic & Core Governance)
from .mcp_222_reflect import mcp_222_reflect, mcp_222_reflect_sync
from .mcp_444_evidence import mcp_444_evidence, mcp_444_evidence_sync
from .mcp_555_empathize import mcp_555_empathize, mcp_555_empathize_sync
from .mcp_666_align import mcp_666_align, mcp_666_align_sync
from .mcp_777_forge import mcp_777_forge, mcp_777_forge_sync
from .mcp_888_judge import mcp_888_judge, mcp_888_judge_sync

# Phase 3 tools (Cryptographic Audit Trail)
from .mcp_889_proof import mcp_889_proof, mcp_889_proof_sync
from .mcp_999_seal import mcp_999_seal, mcp_999_seal_sync

# Legacy tools (existing)
from .judge import arifos_judge
from .recall import arifos_recall
from .audit import arifos_audit
from .apex_llama import apex_llama

__all__ = [
    # Phase 1
    "mcp_000_reset",
    "mcp_000_reset_sync",
    "mcp_111_sense",
    "mcp_111_sense_sync",
    # Phase 2
    "mcp_222_reflect",
    "mcp_222_reflect_sync",
    "mcp_444_evidence",
    "mcp_444_evidence_sync",
    "mcp_555_empathize",
    "mcp_555_empathize_sync",
    "mcp_666_align",
    "mcp_666_align_sync",
    "mcp_777_forge",
    "mcp_777_forge_sync",
    "mcp_888_judge",
    "mcp_888_judge_sync",
    # Phase 3
    "mcp_889_proof",
    "mcp_889_proof_sync",
    "mcp_999_seal",
    "mcp_999_seal_sync",
    # Legacy
    "arifos_judge",
    "arifos_recall",
    "arifos_audit",
    "apex_llama",
]
