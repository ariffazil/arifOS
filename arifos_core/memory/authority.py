"""
authority.py — Memory Authority Check for arifOS v38

Enforces the authority boundary:
- Humans seal law, AI proposes
- AI never self-modifies its own constitution
- Vault writes require human approval

Core Philosophy:
Without this boundary, you lose governance.
The system becomes a black box that rewrites its own rules.

Per: docs/arifOS-MEMORY-FORGING-DEEPRESEARCH.md

Author: arifOS Project
Version: v38.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# =============================================================================
# EXCEPTIONS
# =============================================================================

class MemoryAuthorityError(Exception):
    """Base exception for memory authority violations."""
    pass


class MemoryAuthorityViolation(MemoryAuthorityError):
    """Raised when an authority boundary is violated."""
    pass


class HumanApprovalRequiredError(MemoryAuthorityError):
    """Raised when human approval is required but not present."""
    pass


class WriterNotAuthorizedError(MemoryAuthorityError):
    """Raised when a writer is not authorized for an action."""
    pass


class SelfModificationError(MemoryAuthorityError):
    """Raised when AI attempts to self-modify constitution."""
    pass


# =============================================================================
# CONSTANTS
# =============================================================================

class WriterType(str, Enum):
    """Types of writers in the system."""
    HUMAN = "HUMAN"                # Human operator/judge
    APEX_PRIME = "APEX_PRIME"      # Verdict engine
    PIPELINE_STAGE = "PIPELINE"    # Pipeline stages (111-999)
    PHOENIX_72 = "PHOENIX_72"      # Amendment proposer
    SYSTEM = "SYSTEM"              # System operations


class AuthorityAction(str, Enum):
    """Actions that require authority checks."""
    WRITE_VAULT = "WRITE_VAULT"
    SEAL_AMENDMENT = "SEAL_AMENDMENT"
    REJECT_AMENDMENT = "REJECT_AMENDMENT"
    WRITE_LEDGER = "WRITE_LEDGER"
    WRITE_ACTIVE = "WRITE_ACTIVE"
    WRITE_VOID = "WRITE_VOID"
    WRITE_PHOENIX = "WRITE_PHOENIX"
    MODIFY_CONSTITUTION = "MODIFY_CONSTITUTION"
    DELETE_MEMORY = "DELETE_MEMORY"
    CHANGE_RETENTION = "CHANGE_RETENTION"


# Authority matrix: who can do what
# True = allowed, False = denied, "HUMAN_REQUIRED" = needs human approval
AUTHORITY_MATRIX: Dict[str, Dict[str, Any]] = {
    # Vault operations (highest authority)
    "WRITE_VAULT": {
        "HUMAN": True,
        "APEX_PRIME": False,
        "PIPELINE": False,
        "PHOENIX_72": False,
        "SYSTEM": False,
        "888_JUDGE": "HUMAN_REQUIRED",  # Judge proposes, human seals
    },
    "SEAL_AMENDMENT": {
        "HUMAN": True,
        "APEX_PRIME": False,
        "PIPELINE": False,
        "PHOENIX_72": False,
        "SYSTEM": False,
    },
    "REJECT_AMENDMENT": {
        "HUMAN": True,
        "APEX_PRIME": False,
        "PIPELINE": False,
        "PHOENIX_72": False,
        "SYSTEM": False,
    },
    # Ledger operations
    "WRITE_LEDGER": {
        "HUMAN": True,
        "APEX_PRIME": True,
        "PIPELINE": False,
        "PHOENIX_72": False,
        "SYSTEM": True,
        "888_JUDGE": True,
    },
    # Active stream operations
    "WRITE_ACTIVE": {
        "HUMAN": True,
        "APEX_PRIME": True,
        "PIPELINE": True,
        "PHOENIX_72": False,
        "SYSTEM": True,
        "111_SENSE": True,
        "222_REFLECT": True,
        "333_REASON": True,
        "777_FORGE": True,
    },
    # Void operations
    "WRITE_VOID": {
        "HUMAN": True,
        "APEX_PRIME": True,
        "PIPELINE": True,
        "PHOENIX_72": False,
        "SYSTEM": True,
        "777_FORGE": True,
    },
    # Phoenix operations
    "WRITE_PHOENIX": {
        "HUMAN": True,
        "APEX_PRIME": False,
        "PIPELINE": False,
        "PHOENIX_72": True,
        "SYSTEM": False,
        "888_JUDGE": True,
    },
    # Constitution modification (NEVER by AI)
    "MODIFY_CONSTITUTION": {
        "HUMAN": True,
        "APEX_PRIME": False,
        "PIPELINE": False,
        "PHOENIX_72": False,
        "SYSTEM": False,
    },
    # Memory deletion
    "DELETE_MEMORY": {
        "HUMAN": True,
        "APEX_PRIME": False,
        "PIPELINE": False,
        "PHOENIX_72": False,
        "SYSTEM": "HUMAN_REQUIRED",  # System can auto-cleanup with approval
    },
    # Retention policy changes
    "CHANGE_RETENTION": {
        "HUMAN": True,
        "APEX_PRIME": False,
        "PIPELINE": False,
        "PHOENIX_72": False,
        "SYSTEM": False,
    },
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class AuthorityDecision:
    """Result of an authority check."""
    allowed: bool
    reason: str
    requires_human_approval: bool = False
    action: Optional[str] = None
    writer_id: Optional[str] = None


@dataclass
class AuthorityLogEntry:
    """Log entry for authority decisions."""
    timestamp: str
    action: str
    writer_id: str
    allowed: bool
    reason: str
    requires_human_approval: bool = False


# =============================================================================
# MEMORY AUTHORITY CHECK
# =============================================================================

class MemoryAuthorityCheck:
    """
    Enforces authority boundaries for memory operations.

    Core Constraints:
    1. AI never self-modifies its own constitution
    2. Vault writes require human approval (888_Judge)
    3. Phoenix-72 proposals require human seal
    4. Only APEX_PRIME can write to Ledger (verdicts)
    5. Only humans can delete memory or change retention

    Usage:
        authority = MemoryAuthorityCheck()
        decision = authority.validate_writer("888_JUDGE", "VAULT")
        if not decision.allowed:
            raise WriterNotAuthorizedError(decision.reason)
    """

    def __init__(self, human_approval_flag: bool = False):
        """
        Initialize authority checker.

        Args:
            human_approval_flag: If True, human approval is considered granted.
                                 Set via CLI or API when human is present.
        """
        self.human_approval_flag = human_approval_flag
        self._authority_log: List[AuthorityLogEntry] = []

    # =========================================================================
    # CORE AUTHORITY METHODS
    # =========================================================================

    def enforce_human_seal_required(
        self,
        band: str,
        verdict: str,
        writer_id: str,
    ) -> AuthorityDecision:
        """
        Enforce that human seal is required for certain operations.

        Args:
            band: Target band name
            verdict: Current verdict
            writer_id: Who is attempting the write

        Returns:
            AuthorityDecision with allowed status

        Raises:
            HumanApprovalRequiredError: If human approval needed but not present
        """
        band_upper = band.upper()

        # Vault ALWAYS requires human seal
        if band_upper == "VAULT":
            if writer_id == "HUMAN":
                decision = AuthorityDecision(
                    allowed=True,
                    reason="Human writer authorized for Vault",
                    action="WRITE_VAULT",
                    writer_id=writer_id,
                )
            elif self.human_approval_flag:
                decision = AuthorityDecision(
                    allowed=True,
                    reason="Human approval flag set for Vault write",
                    requires_human_approval=True,
                    action="WRITE_VAULT",
                    writer_id=writer_id,
                )
            else:
                decision = AuthorityDecision(
                    allowed=False,
                    reason="Vault writes require human approval (888_Judge)",
                    requires_human_approval=True,
                    action="WRITE_VAULT",
                    writer_id=writer_id,
                )
                self._log_decision(decision)
                raise HumanApprovalRequiredError(decision.reason)

            self._log_decision(decision)
            return decision

        # Phoenix sealing requires human
        if band_upper == "PHOENIX" and verdict in ("SEAL", "SEALED"):
            if writer_id == "HUMAN":
                decision = AuthorityDecision(
                    allowed=True,
                    reason="Human authorized to seal Phoenix proposal",
                    action="SEAL_AMENDMENT",
                    writer_id=writer_id,
                )
            else:
                decision = AuthorityDecision(
                    allowed=False,
                    reason="Phoenix proposal sealing requires human approval",
                    requires_human_approval=True,
                    action="SEAL_AMENDMENT",
                    writer_id=writer_id,
                )
                self._log_decision(decision)
                raise HumanApprovalRequiredError(decision.reason)

            self._log_decision(decision)
            return decision

        # Default: allowed
        decision = AuthorityDecision(
            allowed=True,
            reason=f"No human seal required for {band_upper}",
            action=f"WRITE_{band_upper}",
            writer_id=writer_id,
        )
        self._log_decision(decision)
        return decision

    def validate_writer(
        self,
        writer_id: str,
        band: str,
    ) -> AuthorityDecision:
        """
        Validate if a writer is authorized for a band.

        Args:
            writer_id: Who is attempting to write
            band: Target band name

        Returns:
            AuthorityDecision with validation result
        """
        band_upper = band.upper()
        action = f"WRITE_{band_upper}"

        # Get authority rules for this action
        rules = AUTHORITY_MATRIX.get(action, {})

        # Check writer authorization
        permission = rules.get(writer_id)

        if permission is True:
            decision = AuthorityDecision(
                allowed=True,
                reason=f"Writer {writer_id} authorized for {band_upper}",
                action=action,
                writer_id=writer_id,
            )
        elif permission == "HUMAN_REQUIRED":
            if self.human_approval_flag:
                decision = AuthorityDecision(
                    allowed=True,
                    reason=f"Writer {writer_id} authorized with human approval for {band_upper}",
                    requires_human_approval=True,
                    action=action,
                    writer_id=writer_id,
                )
            else:
                decision = AuthorityDecision(
                    allowed=False,
                    reason=f"Writer {writer_id} requires human approval for {band_upper}",
                    requires_human_approval=True,
                    action=action,
                    writer_id=writer_id,
                )
        elif permission is False:
            decision = AuthorityDecision(
                allowed=False,
                reason=f"Writer {writer_id} not authorized for {band_upper}",
                action=action,
                writer_id=writer_id,
            )
        else:
            # Not in matrix: check if it's a pipeline stage
            if writer_id.startswith(("111", "222", "333", "444", "555", "666", "777", "888", "999")):
                pipeline_permission = rules.get("PIPELINE")
                decision = AuthorityDecision(
                    allowed=pipeline_permission is True,
                    reason=f"Pipeline stage {writer_id} {'authorized' if pipeline_permission else 'not authorized'} for {band_upper}",
                    action=action,
                    writer_id=writer_id,
                )
            else:
                decision = AuthorityDecision(
                    allowed=False,
                    reason=f"Unknown writer {writer_id} not in authority matrix for {band_upper}",
                    action=action,
                    writer_id=writer_id,
                )

        self._log_decision(decision)
        return decision

    def authority_boundary_check(
        self,
        proposed_write: Dict[str, Any],
    ) -> AuthorityDecision:
        """
        Ensure AI never self-modifies its own constitution.

        This is the CRITICAL boundary that prevents runaway self-modification.

        Args:
            proposed_write: The proposed write operation

        Returns:
            AuthorityDecision with boundary check result

        Raises:
            SelfModificationError: If AI attempts constitutional self-modification
        """
        writer_id = proposed_write.get("writer_id", "UNKNOWN")
        target_band = proposed_write.get("band", "UNKNOWN")
        content = proposed_write.get("content", {})

        # Check for constitutional modification attempts
        is_constitution_mod = (
            target_band.upper() == "VAULT" or
            content.get("type") in ("amendment", "law", "floor_update", "constitutional") or
            content.get("modifies_constitution", False)
        )

        # AI writers cannot modify constitution
        ai_writers = ["APEX_PRIME", "PHOENIX_72", "SYSTEM"]
        is_ai_writer = writer_id in ai_writers or writer_id.startswith(("111", "222", "333", "444", "555", "666", "777", "888", "999"))

        if is_constitution_mod and is_ai_writer and writer_id != "HUMAN":
            decision = AuthorityDecision(
                allowed=False,
                reason="AI cannot self-modify constitution. Only humans can seal constitutional changes.",
                action="MODIFY_CONSTITUTION",
                writer_id=writer_id,
            )
            self._log_decision(decision)
            raise SelfModificationError(decision.reason)

        # AI can PROPOSE but not SEAL
        if target_band.upper() == "PHOENIX" and writer_id != "HUMAN":
            proposal_status = content.get("status", "draft")
            if proposal_status in ("sealed", "rejected"):
                decision = AuthorityDecision(
                    allowed=False,
                    reason="Only humans can seal or reject amendments",
                    action="SEAL_AMENDMENT",
                    writer_id=writer_id,
                )
                self._log_decision(decision)
                raise SelfModificationError(decision.reason)

        decision = AuthorityDecision(
            allowed=True,
            reason="Authority boundary check passed",
            action="BOUNDARY_CHECK",
            writer_id=writer_id,
        )
        self._log_decision(decision)
        return decision

    def log_authority_decision(
        self,
        writer: str,
        band: str,
        verdict: str,
        allowed: bool,
        reason: str,
    ) -> None:
        """
        Explicitly log an authority decision for audit.

        Args:
            writer: Who attempted the action
            band: Target band
            verdict: Associated verdict
            allowed: Whether it was allowed
            reason: Why allowed/denied
        """
        entry = AuthorityLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            action=f"WRITE_{band.upper()}",
            writer_id=writer,
            allowed=allowed,
            reason=reason,
        )
        self._authority_log.append(entry)

    # =========================================================================
    # APPROVAL MANAGEMENT
    # =========================================================================

    def set_human_approval(self, approved: bool) -> None:
        """Set the human approval flag (typically from CLI/API)."""
        self.human_approval_flag = approved

    def is_human_approved(self) -> bool:
        """Check if human approval is currently set."""
        return self.human_approval_flag

    # =========================================================================
    # AUDIT
    # =========================================================================

    def get_authority_log(self) -> List[AuthorityLogEntry]:
        """Return the authority decision log."""
        return list(self._authority_log)

    def clear_authority_log(self) -> None:
        """Clear the authority decision log."""
        self._authority_log.clear()

    def _log_decision(self, decision: AuthorityDecision) -> None:
        """Internal: log an authority decision."""
        entry = AuthorityLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            action=decision.action or "UNKNOWN",
            writer_id=decision.writer_id or "UNKNOWN",
            allowed=decision.allowed,
            reason=decision.reason,
            requires_human_approval=decision.requires_human_approval,
        )
        self._authority_log.append(entry)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def check_write_authority(
    writer_id: str,
    band: str,
    human_approval: bool = False,
) -> bool:
    """
    Quick check if a writer can write to a band.

    Args:
        writer_id: Who is writing
        band: Target band
        human_approval: Whether human approval is granted

    Returns:
        True if allowed, False otherwise
    """
    checker = MemoryAuthorityCheck(human_approval_flag=human_approval)
    decision = checker.validate_writer(writer_id, band)
    return decision.allowed


def require_human_for_vault(writer_id: str) -> bool:
    """Check if human approval is required for this writer to write to Vault."""
    return writer_id != "HUMAN"


def require_human_for_seal(writer_id: str) -> bool:
    """Check if human approval is required for this writer to seal amendments."""
    return writer_id != "HUMAN"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Exceptions
    "MemoryAuthorityError",
    "MemoryAuthorityViolation",
    "HumanApprovalRequiredError",
    "WriterNotAuthorizedError",
    "SelfModificationError",
    # Enums
    "WriterType",
    "AuthorityAction",
    # Data classes
    "AuthorityDecision",
    "AuthorityLogEntry",
    # Main class
    "MemoryAuthorityCheck",
    # Convenience functions
    "check_write_authority",
    "require_human_for_vault",
    "require_human_for_seal",
    # Constants
    "AUTHORITY_MATRIX",
    # v38.3Omega EUREKA Phase-1 bridges
    "actor_role_to_writer_type",
    "eureka_can_write",
]


# =============================================================================
# v38.3Omega EUREKA Phase-1 Compatibility Bridge (APPEND-ONLY)
# =============================================================================

def actor_role_to_writer_type(role):
    """
    Bridge ActorRole (Phase-1) -> existing WriterType.
    
    Does not change existing authority model. Used by EUREKA router only.
    
    Args:
        role: ActorRole enum from eureka_types
        
    Returns:
        Corresponding WriterType or None for TOOL role
    """
    role_str = str(role)
    
    if "HUMAN" in role_str:
        return WriterType.HUMAN
    elif "JUDICIARY" in role_str:
        # JUDICIARY (APEX PRIME / @EYE) maps to APEX_PRIME
        return WriterType.APEX_PRIME
    elif "ENGINE" in role_str:
        # ENGINE (pipeline/system code) maps to SYSTEM
        return WriterType.SYSTEM
    # TOOL is untrusted -> None
    return None


def eureka_can_write(writer_type, target_band: str, human_seal: bool) -> bool:
    """
    Check if a writer can write to a band (EUREKA Phase-1 entrypoint).
    
    Delegates to existing MemoryAuthorityCheck.validate_writer() when possible,
    falls back to Phase-1 rules for new bands (PENDING).
    
    Args:
        writer_type: WriterType enum (result of actor_role_to_writer_type)
        target_band: Band name (VAULT, LEDGER, ACTIVE, etc.)
        human_seal: Whether human seal is present
        
    Returns:
        True if write is allowed, False otherwise
    """
    # Hard invariant: Vault requires human seal
    if target_band == "VAULT":
        if writer_type is None:
            return False
        return str(writer_type).endswith("HUMAN") and human_seal is True
    
    # If tools or unknown role -> forbid
    if writer_type is None:
        return False
    
    # Try existing authority engine first
    try:
        checker = MemoryAuthorityCheck(human_approval_flag=human_seal)
        writer_id = writer_type.value  # Get string value from enum
        decision = checker.validate_writer(writer_id, target_band)
        
        # If old matrix knows about this band and allows it, use that
        if decision.allowed:
            return True
        
        # If old matrix explicitly forbids, we may still allow per Phase-1 for
        # bands intended to be writable by ENGINE/JUDICIARY (PHOENIX/PENDING).
        # So do not hard-stop here; fall through to Phase-1 rules below.
        # Vault is handled above with hard invariant.
    except Exception:
        pass  # Fall through to Phase-1 rules
    
    # Phase-1 rules for bands not in old matrix
    # PENDING is new in v38.3, allow for ENGINE/JUDICIARY/HUMAN
    if target_band == "PENDING":
        return writer_type in {WriterType.SYSTEM, WriterType.APEX_PRIME, WriterType.HUMAN}
    
    # PHOENIX - allow proposals from ENGINE, JUDICIARY, HUMAN in Phase-1
    if target_band == "PHOENIX":
        return writer_type in {WriterType.SYSTEM, WriterType.APEX_PRIME, WriterType.HUMAN}

    # ACTIVE, VOID, LEDGER - allow for known roles
    if target_band in {"ACTIVE", "VOID", "LEDGER"}:
        return writer_type in {WriterType.SYSTEM, WriterType.APEX_PRIME, WriterType.HUMAN}
    
    return False
