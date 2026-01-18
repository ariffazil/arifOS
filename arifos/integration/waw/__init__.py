"""
arifos_core.waw - W@W Federation Constitutional Organs (v35Omega)

The five-organ constitutional execution layer of arifOS.
Each organ evaluates outputs from its domain and returns PASS/WARN/VETO.

Organs:
- @WELL  - Somatic safety, tone, emotional stability (Peace², κᵣ)
- @RIF   - Logic, clarity, entropy reduction (ΔS, Truth)
- @WEALTH - Integrity, dignity, justice (Amanah, maruah)
- @GEOX  - Physics, feasibility, reality (E_earth, Tri-Witness)
- @PROMPT - Language, culture, expression (Anti-Hantu, RASA)

Protocol:
- Organs receive AAA outputs and metrics
- Each returns OrganSignal with vote (PASS/WARN/VETO) + evidence
- Aggregated signals feed into APEX PRIME at 888

Constraints:
- Organs CANNOT self-seal or override floors
- VETO escalates to APEX PRIME, does not directly VOID
- @WEALTH has absolute veto power (Amanah LOCK violation → immediate VOID)

See: canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md
     docs/W@W/WAW_v36Omega_FINAL_CANON.md
"""

from .base import OrganSignal, OrganVote, WAWOrgan
from .well import WellOrgan
from .rif import RifOrgan
from .wealth import WealthOrgan
from .geox import GeoxOrgan
from .prompt import PromptOrgan
from .federation import WAWFederationCore, FederationVerdict

# @WELL File Care (v42 - Universal Migration Tool)
from .well_file_care import (
    WellFileCare,
    WellConstants,
    WellOperationType,
    WellOperationStatus,
    WellAuditEntry,
    WellHealthReport,
    WellOperationResult,
    create_well_file_care,
)

__all__ = [
    # Base types
    "OrganSignal",
    "OrganVote",
    "WAWOrgan",
    # Organs
    "WellOrgan",
    "RifOrgan",
    "WealthOrgan",
    "GeoxOrgan",
    "PromptOrgan",
    # Federation
    "WAWFederationCore",
    "FederationVerdict",
    # @WELL File Care (v42)
    "WellFileCare",
    "WellConstants",
    "WellOperationType",
    "WellOperationStatus",
    "WellAuditEntry",
    "WellHealthReport",
    "WellOperationResult",
    "create_well_file_care",
]
