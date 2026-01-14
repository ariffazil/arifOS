"""
phoenix72_controller.py — Phoenix-72 Amendment Controller for arifOS v37

Implements the Phoenix-72 amendment protocol per:
- archive/versions/v36_3_omega/v36.3O/canon/VAULT_999_AMENDMENTS_v36.3O.md
- archive/versions/v36_3_omega/v36.3O/spec/phoenix72_amendment_spec_v36.3O.json

Key responsibilities:
- Compute floor pressure P(F) from scars and ledger entries
- Propose amendments when pressure exceeds thresholds
- Enforce safety constraints (|ΔF| ≤ 0.05, cooldown, evidence requirements)
- Finalize amendments with cryptographic signature

Only the Phoenix-72 path can finalize amendments — this is the single
authority for constitutional floor modifications.

Author: arifOS Project
Version: v37
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .scar_manager import ScarManager, ScarRecord
    from .vault_manager import VaultManager, AmendmentRecord, AmendmentEvidence
    from .cooling_ledger import CoolingLedgerV37


logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

# Safety cap: |ΔF| ≤ MAX_THRESHOLD_DELTA per amendment cycle
MAX_THRESHOLD_DELTA: float = 0.05  # Canon value (hard law)

# Cooldown window in hours
# TODO(Arif): Confirm canonical cooldown window. Draft suggests 24 hours.
COOLDOWN_WINDOW_HOURS: int = 24

# Minimum evidence entries required for an amendment
MIN_EVIDENCE_ENTRIES: int = 3

# Pressure thresholds
# TODO(Arif): Confirm recommended P_min, P_max bands
PRESSURE_MIN: float = 5.0   # Below this, no amendment considered
PRESSURE_MAX: float = 50.0  # Above this, saturation (prefer scar curation)

# Pressure-to-delta mapping coefficients
# TODO(Arif): Confirm T (temperature) and w1, w2 weights
PRESSURE_TEMPERATURE: float = 10.0  # T in the formula
PRESSURE_W1: float = 0.5   # Weight for scar severity component
PRESSURE_W2: float = 0.5   # Weight for ledger failure component

# Protected floors that require explicit override
PROTECTED_FLOORS = {"F6", "F9"}  # Amanah, Anti-Hantu


# =============================================================================
# PRESSURE COMPUTATION
# =============================================================================

@dataclass
class PressureReport:
    """
    Report of floor pressure computation.

    Pressure combines:
    - Scar severity (weighted sum of active scars affecting the floor)
    - Ledger failure rate (recent failures involving the floor)
    """
    floor_id: str
    scar_pressure: float
    ledger_pressure: float
    total_pressure: float
    scar_count: int
    failure_count: int
    scars_considered: List[str]
    ledger_hashes_considered: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "floor_id": self.floor_id,
            "scar_pressure": self.scar_pressure,
            "ledger_pressure": self.ledger_pressure,
            "total_pressure": self.total_pressure,
            "scar_count": self.scar_count,
            "failure_count": self.failure_count,
            "scars_considered": self.scars_considered,
            "ledger_hashes_considered": self.ledger_hashes_considered,
        }


def compute_floor_pressure(
    floor_id: str,
    scar_manager: "ScarManager",
    ledger: "CoolingLedgerV37",
    window_hours: float = 72.0,
    w1: float = PRESSURE_W1,
    w2: float = PRESSURE_W2,
) -> PressureReport:
    """
    Compute pressure P(F) for a given floor.

    Formula per canon:
        P(F) = w1 * S_severity(F) + w2 * L_failures(F)

    Where:
        S_severity(F) = sum of severity weights of active scars affecting F
        L_failures(F) = count of ledger entries with failures on F in window

    Args:
        floor_id: Floor identifier (F1-F9)
        scar_manager: ScarManager instance
        ledger: CoolingLedgerV37 instance
        window_hours: Lookback window for ledger failures
        w1: Weight for scar component
        w2: Weight for ledger component

    Returns:
        PressureReport with computed values
    """
    # Scar pressure
    scars = scar_manager.list_active_scars(floor=floor_id)
    scar_pressure = sum(s.get_pressure_weight() for s in scars)
    scar_ids = [s.scar_id for s in scars]

    # Ledger pressure (failures in window)
    failure_count = 0
    ledger_hashes: List[str] = []

    for entry in ledger.iter_recent(hours=window_hours):
        floor_failures = entry.get("floor_failures", [])
        floor_warnings = entry.get("floor_warnings", [])

        # Check if this floor is mentioned in failures/warnings
        affected = False
        for ff in floor_failures:
            if floor_id in str(ff):
                affected = True
                break

        if not affected:
            for fw in floor_warnings:
                if floor_id in str(fw):
                    affected = True
                    break

        if affected:
            failure_count += 1
            entry_hash = entry.get("entry_hash") or entry.get("hash")
            if entry_hash:
                ledger_hashes.append(entry_hash)

    ledger_pressure = float(failure_count)
    total_pressure = w1 * scar_pressure + w2 * ledger_pressure

    return PressureReport(
        floor_id=floor_id,
        scar_pressure=scar_pressure,
        ledger_pressure=ledger_pressure,
        total_pressure=total_pressure,
        scar_count=len(scars),
        failure_count=failure_count,
        scars_considered=scar_ids,
        ledger_hashes_considered=ledger_hashes,
    )


def compute_all_floor_pressures(
    scar_manager: "ScarManager",
    ledger: "CoolingLedgerV37",
    window_hours: float = 72.0,
) -> Dict[str, PressureReport]:
    """
    Compute pressure for all floors.

    Returns:
        Dict mapping floor_id to PressureReport
    """
    floors = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]
    return {
        f: compute_floor_pressure(f, scar_manager, ledger, window_hours)
        for f in floors
    }


# =============================================================================
# DELTA COMPUTATION
# =============================================================================

def compute_suggested_delta(
    pressure: float,
    current_threshold: float,
    direction: Literal["tighten", "relax"],
    temperature: float = PRESSURE_TEMPERATURE,
    max_delta: float = MAX_THRESHOLD_DELTA,
) -> float:
    """
    Compute suggested threshold delta based on pressure.

    Uses a sigmoid-like mapping that respects the safety cap:
        raw_delta = (pressure / temperature) * max_delta
        capped_delta = min(raw_delta, max_delta)

    Args:
        pressure: P(F) value
        current_threshold: Current floor threshold
        direction: "tighten" (increase safety) or "relax" (decrease safety)
        temperature: Scaling temperature T
        max_delta: Maximum allowed delta

    Returns:
        Suggested delta value (always positive, direction handled by caller)
    """
    if pressure <= PRESSURE_MIN:
        return 0.0

    # Normalize pressure to [0, 1] range between P_min and P_max
    normalized = (pressure - PRESSURE_MIN) / (PRESSURE_MAX - PRESSURE_MIN)
    normalized = max(0.0, min(1.0, normalized))

    # Apply sigmoid-like curve
    raw_delta = normalized * max_delta

    # Cap at safety limit
    return min(raw_delta, max_delta)


# =============================================================================
# PHOENIX-72 CONTROLLER
# =============================================================================

@dataclass
class Phoenix72Config:
    """Configuration for Phoenix-72 controller."""
    max_delta: float = MAX_THRESHOLD_DELTA
    cooldown_hours: int = COOLDOWN_WINDOW_HOURS
    min_evidence_entries: int = MIN_EVIDENCE_ENTRIES
    pressure_min: float = PRESSURE_MIN
    pressure_max: float = PRESSURE_MAX
    pressure_window_hours: float = 72.0
    # HMAC key for signing (stub - in production use KMS)
    # TODO(Arif): Replace with hardware-backed keys in v37+
    hmac_key: bytes = field(default_factory=lambda: b"phoenix72_stub_key_v37")


@dataclass
class ProposalResult:
    """Result of an amendment proposal."""
    success: bool
    amendment_id: Optional[str] = None
    pressure_report: Optional[PressureReport] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class FinalizeResult:
    """Result of an amendment finalization."""
    success: bool
    amendment_id: Optional[str] = None
    signature: Optional[str] = None
    errors: List[str] = field(default_factory=list)


class Phoenix72Controller:
    """
    Phoenix-72 Amendment Controller.

    This is the SOLE authority for finalizing amendments to constitutional floors.
    All amendments must pass through this controller's finalize() method.

    Workflow:
    1. analyze_pressure() - Compute pressure for all floors
    2. suggest_amendment() - Get suggested amendment based on pressure
    3. propose() - Create amendment proposal (validates constraints)
    4. finalize() - Sign and seal the amendment (applies to Vault)

    Safety constraints enforced:
    - |ΔF| ≤ 0.05 per cycle
    - Cooldown window between amendments to same floor
    - Minimum evidence requirements
    - Protected floor checks (F6/Amanah, F9/Anti-Hantu)

    Usage:
        controller = Phoenix72Controller(
            vault_manager=vault_mgr,
            scar_manager=scar_mgr,
            ledger=ledger_v37,
        )

        # Analyze and propose
        pressures = controller.analyze_pressure()
        suggestion = controller.suggest_amendment(pressures)

        if suggestion:
            result = controller.propose(
                floor_id=suggestion["floor_id"],
                new_threshold=suggestion["new_threshold"],
                reason="Threshold drift detected",
            )

            if result.success:
                finalize_result = controller.finalize(result.amendment_id)
    """

    def __init__(
        self,
        vault_manager: "VaultManager",
        scar_manager: "ScarManager",
        ledger: "CoolingLedgerV37",
        config: Optional[Phoenix72Config] = None,
    ):
        self.vault = vault_manager
        self.scars = scar_manager
        self.ledger = ledger
        self.config = config or Phoenix72Config()

        # Track cooldown timestamps
        self._cooldown_timestamps: Dict[str, float] = {}

        # Current cycle ID
        self._cycle_counter = 0

    def _generate_cycle_id(self) -> str:
        """Generate a unique Phoenix-72 cycle ID."""
        self._cycle_counter += 1
        ts = int(time.time())
        return f"PHX72-{ts}-{self._cycle_counter:04d}"

    def _sign_amendment(self, amendment_data: Dict[str, Any]) -> str:
        """
        Sign an amendment record using HMAC-SHA256.

        In production, this should use hardware-backed keys via KMS.
        """
        # Canonicalize the data
        canonical = json.dumps(amendment_data, sort_keys=True, separators=(",", ":"))

        # HMAC-SHA256
        sig = hmac.new(
            self.config.hmac_key,
            canonical.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return sig

    # =========================================================================
    # PRESSURE ANALYSIS
    # =========================================================================

    def analyze_pressure(self) -> Dict[str, PressureReport]:
        """
        Analyze pressure across all floors.

        Returns:
            Dict mapping floor_id to PressureReport
        """
        return compute_all_floor_pressures(
            self.scars,
            self.ledger,
            self.config.pressure_window_hours,
        )

    def get_floors_above_threshold(
        self,
        pressures: Dict[str, PressureReport],
        threshold: Optional[float] = None,
    ) -> List[PressureReport]:
        """
        Get floors with pressure above the proposal threshold.

        Args:
            pressures: Dict of pressure reports
            threshold: Override threshold (defaults to pressure_min)

        Returns:
            List of PressureReports above threshold, sorted by pressure descending
        """
        threshold = threshold or self.config.pressure_min

        above = [p for p in pressures.values() if p.total_pressure >= threshold]
        above.sort(key=lambda p: p.total_pressure, reverse=True)

        return above

    # =========================================================================
    # AMENDMENT SUGGESTION
    # =========================================================================

    def suggest_amendment(
        self,
        pressures: Dict[str, PressureReport],
    ) -> Optional[Dict[str, Any]]:
        """
        Suggest a single amendment based on pressure analysis.

        Returns the highest-pressure floor that is:
        - Above P_min threshold
        - Not in cooldown
        - Not a protected floor (unless explicit override)

        Args:
            pressures: Dict of pressure reports from analyze_pressure()

        Returns:
            Suggestion dict with floor_id, current_threshold, suggested_delta,
            new_threshold, direction, pressure_report
            Or None if no amendment suggested
        """
        candidates = self.get_floors_above_threshold(pressures)

        if not candidates:
            return None

        floors = self.vault.get_floors()
        now = time.time()

        for report in candidates:
            floor_id = report.floor_id

            # Check cooldown
            last_sealed = self._cooldown_timestamps.get(floor_id, 0)
            cooldown_end = last_sealed + (self.config.cooldown_hours * 3600)

            if now < cooldown_end:
                hours_remaining = (cooldown_end - now) / 3600
                logger.debug(
                    f"Floor {floor_id} in cooldown ({hours_remaining:.1f}h remaining)"
                )
                continue

            # Skip protected floors in automatic suggestions
            if floor_id in PROTECTED_FLOORS:
                logger.info(
                    f"Floor {floor_id} is protected; skipping automatic suggestion"
                )
                continue

            # Get current threshold
            field_map = self._floor_to_field(floor_id)
            current_threshold = floors.get(field_map)

            if current_threshold is None:
                logger.warning(f"No threshold found for {floor_id}")
                continue

            # Compute suggested delta (tighten = increase safety)
            suggested_delta = compute_suggested_delta(
                pressure=report.total_pressure,
                current_threshold=current_threshold,
                direction="tighten",
                max_delta=self.config.max_delta,
            )

            if suggested_delta == 0.0:
                continue

            # New threshold (tighten = increase for min thresholds)
            new_threshold = current_threshold + suggested_delta

            return {
                "floor_id": floor_id,
                "field": field_map,
                "current_threshold": current_threshold,
                "suggested_delta": suggested_delta,
                "new_threshold": new_threshold,
                "direction": "tighten",
                "pressure_report": report,
            }

        return None

    def _floor_to_field(self, floor_id: str) -> str:
        """Map floor ID to constitution field name."""
        # This mapping depends on the constitution schema
        floor_field_map = {
            "F1": "truth_min",
            "F2": "delta_s_min",
            "F3": "peace_squared_min",
            "F4": "kappa_r_min",
            "F5": "omega_0_min",
            "F6": "amanah_lock",
            "F7": "rasa_required",
            "F8": "tri_witness_min",
            "F9": "anti_hantu_required",
        }
        return floor_field_map.get(floor_id, f"{floor_id.lower()}_threshold")

    # =========================================================================
    # PROPOSAL
    # =========================================================================

    def propose(
        self,
        floor_id: str,
        new_threshold: Any,
        reason: str,
        evidence_ledger_hashes: Optional[List[str]] = None,
        evidence_scar_ids: Optional[List[str]] = None,
        override_protected: bool = False,
    ) -> ProposalResult:
        """
        Propose an amendment to a floor threshold.

        This creates a PROPOSED amendment in the VaultManager.
        The amendment must still be finalized via finalize() to take effect.

        Args:
            floor_id: Floor identifier (F1-F9)
            new_threshold: New threshold value
            reason: Justification for the amendment
            evidence_ledger_hashes: Ledger entry hashes as evidence
            evidence_scar_ids: Scar IDs as evidence
            override_protected: If True, allow amendments to F6/F9

        Returns:
            ProposalResult with success status and amendment_id
        """
        from .vault_manager import AmendmentEvidence

        errors: List[str] = []
        warnings: List[str] = []

        # Check protected floors
        if floor_id in PROTECTED_FLOORS and not override_protected:
            errors.append(
                f"Floor {floor_id} is protected (Amanah/Anti-Hantu). "
                "Requires override_protected=True and explicit human approval."
            )
            return ProposalResult(success=False, errors=errors)

        # Check cooldown
        now = time.time()
        last_sealed = self._cooldown_timestamps.get(floor_id, 0)
        cooldown_end = last_sealed + (self.config.cooldown_hours * 3600)

        if now < cooldown_end:
            hours_remaining = (cooldown_end - now) / 3600
            errors.append(
                f"Floor {floor_id} is in cooldown. "
                f"{hours_remaining:.1f} hours remaining."
            )
            return ProposalResult(success=False, errors=errors)

        # Get pressure report for evidence
        pressure_report = compute_floor_pressure(
            floor_id,
            self.scars,
            self.ledger,
            self.config.pressure_window_hours,
        )

        # Build evidence
        ledger_hashes = evidence_ledger_hashes or []
        scar_ids = evidence_scar_ids or []

        # If no explicit evidence provided, use pressure report
        if not ledger_hashes:
            ledger_hashes = pressure_report.ledger_hashes_considered[:10]
        if not scar_ids:
            scar_ids = pressure_report.scars_considered[:10]

        evidence = AmendmentEvidence(
            ledger_hashes=ledger_hashes,
            scar_ids=scar_ids,
        )

        # Check evidence requirements
        total_evidence = len(evidence.ledger_hashes) + len(evidence.scar_ids)
        if total_evidence < self.config.min_evidence_entries:
            errors.append(
                f"Insufficient evidence: {total_evidence} < "
                f"{self.config.min_evidence_entries} required. "
                "Provide more ledger hashes or scar IDs."
            )
            return ProposalResult(
                success=False,
                errors=errors,
                pressure_report=pressure_report,
            )

        # Get field name
        field = self._floor_to_field(floor_id)

        # Propose via VaultManager
        success, record, proposal_errors = self.vault.propose_amendment(
            target_floor=floor_id,
            target_field=field,
            new_value=new_threshold,
            rationale=reason,
            evidence=evidence,
            proposed_by="Phoenix72",
        )

        if proposal_errors:
            errors.extend(proposal_errors)

        if not success:
            return ProposalResult(
                success=False,
                errors=errors,
                pressure_report=pressure_report,
            )

        return ProposalResult(
            success=True,
            amendment_id=record.amendment_id,
            pressure_report=pressure_report,
            warnings=warnings,
        )

    # =========================================================================
    # FINALIZATION (THE SOLE AUTHORITY)
    # =========================================================================

    def finalize(
        self,
        amendment_id: str,
    ) -> FinalizeResult:
        """
        Finalize and seal an amendment.

        This is the SOLE PATH to modify constitutional floors.

        Steps:
        1. Verify amendment exists and is PROPOSED
        2. Re-validate safety constraints
        3. Generate cryptographic signature
        4. Apply to Vault via VaultManager.finalize_amendment()
        5. Update cooldown timestamp

        Args:
            amendment_id: ID of the proposed amendment

        Returns:
            FinalizeResult with success status and signature
        """
        errors: List[str] = []

        # Get amendment record
        record = self.vault.get_amendment(amendment_id)
        if record is None:
            return FinalizeResult(
                success=False,
                errors=[f"Amendment not found: {amendment_id}"],
            )

        if record.status != "PROPOSED":
            return FinalizeResult(
                success=False,
                errors=[f"Amendment status is {record.status}, expected PROPOSED"],
            )

        # Re-validate delta cap
        if record.delta_value > self.config.max_delta:
            return FinalizeResult(
                success=False,
                errors=[
                    f"Delta {record.delta_value:.4f} exceeds safety cap "
                    f"{self.config.max_delta}"
                ],
            )

        # Re-check cooldown (may have been invalidated since proposal)
        now = time.time()
        last_sealed = self._cooldown_timestamps.get(record.target_floor, 0)
        cooldown_end = last_sealed + (self.config.cooldown_hours * 3600)

        if now < cooldown_end:
            hours_remaining = (cooldown_end - now) / 3600
            return FinalizeResult(
                success=False,
                errors=[
                    f"Floor {record.target_floor} is in cooldown. "
                    f"{hours_remaining:.1f} hours remaining."
                ],
            )

        # Generate cycle ID
        cycle_id = self._generate_cycle_id()

        # Sign the amendment
        sign_data = {
            "amendment_id": record.amendment_id,
            "target_floor": record.target_floor,
            "target_field": record.target_field,
            "old_value": record.old_value,
            "new_value": record.new_value,
            "delta_value": record.delta_value,
            "cycle_id": cycle_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        signature = self._sign_amendment(sign_data)

        # Finalize via VaultManager
        success, finalize_errors = self.vault.finalize_amendment(
            amendment_id=amendment_id,
            phoenix72_signature=signature,
            phoenix72_cycle_id=cycle_id,
        )

        if finalize_errors:
            errors.extend(finalize_errors)

        if not success:
            return FinalizeResult(
                success=False,
                errors=errors,
            )

        # Update cooldown timestamp
        self._cooldown_timestamps[record.target_floor] = now

        logger.info(
            f"Phoenix-72 sealed amendment {amendment_id}: "
            f"{record.target_floor}.{record.target_field} = {record.new_value} "
            f"(cycle={cycle_id})"
        )

        return FinalizeResult(
            success=True,
            amendment_id=amendment_id,
            signature=signature,
        )

    # =========================================================================
    # CONVENIENCE METHODS
    # =========================================================================

    def run_cycle(self) -> Optional[FinalizeResult]:
        """
        Run a complete Phoenix-72 cycle.

        1. Analyze pressure
        2. Suggest amendment (if any)
        3. Propose
        4. Finalize

        Returns:
            FinalizeResult if an amendment was sealed, None if no action taken
        """
        pressures = self.analyze_pressure()
        suggestion = self.suggest_amendment(pressures)

        if suggestion is None:
            logger.info("Phoenix-72 cycle: No amendment suggested")
            return None

        proposal = self.propose(
            floor_id=suggestion["floor_id"],
            new_threshold=suggestion["new_threshold"],
            reason=f"Automatic threshold adjustment based on pressure "
                   f"P({suggestion['floor_id']})={suggestion['pressure_report'].total_pressure:.2f}",
        )

        if not proposal.success:
            logger.warning(
                f"Phoenix-72 proposal failed: {proposal.errors}"
            )
            return None

        result = self.finalize(proposal.amendment_id)

        if not result.success:
            logger.warning(f"Phoenix-72 finalization failed: {result.errors}")

        return result

    def get_cooldown_status(self) -> Dict[str, Any]:
        """
        Get cooldown status for all floors.

        Returns:
            Dict with floor_id -> {in_cooldown, hours_remaining, last_sealed}
        """
        now = time.time()
        status = {}

        for floor_id in ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]:
            last_sealed = self._cooldown_timestamps.get(floor_id, 0)
            cooldown_end = last_sealed + (self.config.cooldown_hours * 3600)

            in_cooldown = now < cooldown_end
            hours_remaining = max(0, (cooldown_end - now) / 3600) if in_cooldown else 0

            status[floor_id] = {
                "in_cooldown": in_cooldown,
                "hours_remaining": round(hours_remaining, 2),
                "last_sealed": datetime.fromtimestamp(last_sealed, timezone.utc).isoformat()
                    if last_sealed > 0 else None,
                "protected": floor_id in PROTECTED_FLOORS,
            }

        return status


# =============================================================================
# PUBLIC EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "MAX_THRESHOLD_DELTA",
    "COOLDOWN_WINDOW_HOURS",
    "MIN_EVIDENCE_ENTRIES",
    "PRESSURE_MIN",
    "PRESSURE_MAX",
    "PROTECTED_FLOORS",
    # Pressure
    "PressureReport",
    "compute_floor_pressure",
    "compute_all_floor_pressures",
    "compute_suggested_delta",
    # Controller
    "Phoenix72Config",
    "ProposalResult",
    "FinalizeResult",
    "Phoenix72Controller",
]
