"""
GEOX 000 INIT ANCHOR — Earth Physics Intelligence Kernel
======================================================

DITEMPA BUKAN DIBERI — Forged, not given.

This module initializes the GEOX kernel with the constitutional grounding
required for all Earth physics operations. It must be called before any
geox.* tool is invoked.

Usage:
    from geox.init_000_anchor import GEOXAnchor
    anchor = GEOXAnchor.forge()
    anchor.verify()  # raises if not forged
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# =============================================================================
# VERSION CONSTANTS
# =============================================================================

GEOX_VERSION = "0.4.3"
ARIFOS_VERSION = "2026.3.24"
INIT_ANCHOR_VERSION = "000"
BOND_REF = "Bond et al. 2007, GSA Today 17(11)"
BOND_FAIL_RATE = 0.79  # 79% expert failure on synthetic seismic

# =============================================================================
# EPISTEMIC LEVELS
# =============================================================================

class EpistemicLevel(Enum):
    """
    GEOX epistemic classification — mandatory on all outputs.

    Collapsing epistemic levels is a F9 Anti-Hantu violation.
    """
    OBSERVATIONAL = "OBS"   # Raw sensor data
    DERIVED = "DER"         # Computed from observations (porosity, saturation)
    INTERPRETED = "INT"     # Inferred from derived data (lithology, fluid type, pay)
    SPECULATED = "SPEC"     # Proposed but unverified (prospect risk, OOIP)

    def __str__(self) -> str:
        return f"[{self.value}]"

    def can_proceed_without_human(self) -> bool:
        """OBS and DER can proceed. INT and SPEC require human review above medium risk."""
        return self in (EpistemicLevel.OBSERVATIONAL, EpistemicLevel.DERIVED)


# =============================================================================
# HOLD CONDITIONS
# =============================================================================

HOLD_TRIGGERS: dict[str, str] = {
    "borehole_spacing_10km": "Borehole spacing > 10km — continuity unreliable",
    "correlation_confidence_06": "Correlation confidence < 0.6 — high stratigraphic uncertainty",
    "vertical_exaggeration_2x": "Vertical exaggeration > 2× undisclosed — misleading display",
    "fault_geometry_unconstrained": "Fault geometry not seismic-constrained",
    "pinchout_in_interpreted": "Pinchout/truncation in interpreted zone — high risk",
    "zero_well_control": "Zero well control in interval of interest — no ground truth",
    "scale_unknown": "Scale unknown or unverified — F4 violation",
    "omega_band_exceeded": "Uncertainty band exceeds Ω₀ max — F7 violation",
}


@dataclass
class GEOXHoldStatus:
    """Result of hold condition check."""
    is_held: bool
    triggers: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def __str__(self) -> str:
        if not self.is_held:
            return "[CLEAR]"
        return f"[888_HOLD: {', '.join(self.triggers)}]"


# =============================================================================
# WELL LOG CONSTANTS (Sandstone Matrix)
# =============================================================================

class WellLogConstants:
    """
    Standard matrix and fluid properties for sandstone interpretation.
    All values must be overridden with regional calibration data.
    """

    # Sandstone matrix
    RHO_MATRIX_SANDSTONE = 2.65   # g/cc
    DT_MATRIX_SANDSTONE = 55.5    # µs/ft
    RHO_MATRIX_LIMESTONE = 2.71   # g/cc
    DT_MATRIX_LIMESTONE = 47.6    # µs/ft
    RHO_MATRIX_DOLOMITE = 2.87    # g/cc
    DT_MATRIX_DOLOMITE = 43.5     # µs/ft

    # Fluids
    RHO_FLUID_WATER = 1.00        # g/cc (at surface; adjust for pressure)
    RHO_FLUID_OIL = 0.85          # g/cc (live oil)
    RHO_FLUID_GAS = 0.25          # g/cc (at surface; highly pressure-dependent)
    DT_FLUID = 189.0              # µs/ft (water at surface)

    # Archie parameters (default; calibrate with local data)
    ARCHIE_A = 1.0
    ARCHIE_M = 2.0
    ARCHIE_N = 2.0
    RW_DEFAULT = 0.02             # ohm·m (North Sea formation water; adjust)

    # Cutoffs (default; regional calibration may override)
    VSHALE_CUTOFF_NET = 0.40      # v/v
    PHI_CUTOFF_PAY = 0.10         # v/v
    SW_CUTOFF_PAY = 0.60          # v/v (water saturation)


@dataclass
class GEOXInterpretationResult:
    """
    Standard return type for all GEOX interpretation outputs.
    Every field is mandatory for F2 Truth compliance.
    """
    epistemic_level: EpistemicLevel
    summary: str
    confidence: float            # τ, 0.0–1.0; F2 requires τ ≥ 0.99
    uncertainty_explicit: bool    # F2: must be declared if confidence < 0.99
    hold_status: GEOXHoldStatus
    toac_warning: bool           # True if ToAC (Bond 2007) concerns apply
    bond_reference: str = BOND_REF
    provenance: list[str] = field(default_factory=list)
    derived_from: list[str] = field(default_factory=list)  # curve mnemonics
    omega_band: tuple[float, float] = (0.03, 0.08)  # uncertainty band
    metadata: dict = field(default_factory=dict)

    def verdict(self) -> str:
        """SEAL if clear, 888_HOLD if held."""
        if self.hold_status.is_held:
            return "888_HOLD"
        return "999_SEAL"

    def __str__(self) -> str:
        return (
            f"{self.epistemic_level.value} · "
            f"τ={self.confidence:.3f} · "
            f"Δ={self.uncertainty_explicit} · "
            f"{self.hold_status} · "
            f"{self.verdict()}"
        )


# =============================================================================
# GEOX ANCHOR
# =============================================================================

class GEOXAnchor:
    """
    000 INIT ANCHOR — Must be forged before GEOX tools can operate.

    This is the constitutional grounding layer. It establishes:
    1. Epistemic discipline (no level collapse)
    2. Hold condition checking
    3. ToAC awareness
    4. F2 confidence declaration
    5. Provenance tracking
    """

    _instance: Optional["GEOXAnchor"] = None
    _forged: bool = False
    _forge_time: float = 0.0

    def __new__(cls) -> "GEOXAnchor":
        # Singleton — only one GEOX kernel anchor per process
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if GEOXAnchor._forged:
            return
        self.version = GEOX_VERSION
        self.arifos_version = ARIFOS_VERSION
        self.init_version = INIT_ANCHOR_VERSION
        self.well_constants = WellLogConstants()
        self._forge_time = 0.0

    @classmethod
    def forge(cls) -> "GEOXAnchor":
        """
        Forge the GEOX anchor. Must be called once at initialization.
        Verifies constitutional state before enabling any tool operation.
        """
        instance = cls()
        if not cls._forged:
            cls._forged = True
            instance._forge_time = time.time()
            # Constitutional self-check — reference module-level constants
            assert GEOX_VERSION, "GEOX_VERSION must be set"
            assert ARIFOS_VERSION, "ARIFOS_VERSION must be set"
            assert INIT_ANCHOR_VERSION == "000", "Must be INIT anchor version 000"
        return instance

    def verify(self) -> None:
        """
        Raise AssertionError if anchor is not forged.
        Call this at the start of every geox.* tool function.
        """
        assert GEOXAnchor._forged, (
            "GEOXAnchor not forged. Call GEOXAnchor.forge() before using geox.* tools."
        )

    def check_hold(self, **conditions) -> GEOXHoldStatus:
        """
        Check all provided conditions against the hold trigger list.
        Pass keyword arguments as condition_name=bool.
        """
        self.verify()
        triggers = [
            desc for name, triggered in conditions.items()
            if triggered
            for name_key, desc in HOLD_TRIGGERS.items()
            if name_key in name
        ]
        return GEOXHoldStatus(is_held=len(triggers) > 0, triggers=triggers)

    def log_to_audit(
        self,
        action: str,
        epistemic_level: EpistemicLevel,
        result: GEOXInterpretationResult,
        context: Optional[dict] = None,
    ) -> None:
        """
        Log to 999_VAULT (audit trail).
        F11 AUDITABILITY requires 100% logging.
        """
        self.verify()
        # In production: write to immutable audit store
        # Stub here; actual implementation uses vault_postgres.py
        entry = {
            "timestamp": time.time(),
            "action": action,
            "epistemic_level": epistemic_level.value,
            "result": str(result),
            "verdict": result.verdict(),
            "context": context or {},
        }
        # vault_postgres.py handles actual write
        return entry

    def declare_output(
        self,
        epistemic_level: EpistemicLevel,
        confidence: float,
        uncertainty_explicit: bool,
        derived_from: Optional[list[str]] = None,
        provenance: Optional[list[str]] = None,
        hold_status: Optional[GEOXHoldStatus] = None,
        toac_warning: bool = False,
    ) -> GEOXInterpretationResult:
        """
        Standard output declaration for all GEOX tools.
        Enforces F2 (confidence declaration) and epistemic labeling.
        """
        self.verify()

        # F2: Confidence must be declared
        if confidence < 0.99 and not uncertainty_explicit:
            uncertainty_explicit = True

        # Omega band check
        omega_band = (0.03, 0.08)
        if confidence < 0.97:
            omega_band = (0.05, 0.15)  # Wider band for lower confidence

        hold = hold_status or GEOXHoldStatus(is_held=False)

        return GEOXInterpretationResult(
            epistemic_level=epistemic_level,
            summary="",
            confidence=confidence,
            uncertainty_explicit=uncertainty_explicit,
            hold_status=hold,
            toac_warning=toac_warning,
            provenance=provenance or [],
            derived_from=derived_from or [],
            omega_band=omega_band,
        )

    def __repr__(self) -> str:
        return (
            f"GEOXAnchor(v{GEOX_VERSION}, arifOS {ARIFOS_VERSION}, "
            f"INIT {INIT_ANCHOR_VERSION}, "
            f"forge_time={self._forge_time:.0f})"
        )


# =============================================================================
# TOAC — THEORY OF ANOMALOUS CONTRAST
# =============================================================================

class ToACWarning(Enum):
    """
    Theory of Anomalous Contrast warning types.
    See Bond et al. (2007) — 79% expert failure rate on synthetic data.
    """
    POLARITY_CONVENTION = "Wrong impedance assumption → misidentified fluid contact"
    AGC_GAIN_ARTIFACT = "AGC distortion → false amplitude anomaly"
    MIGRATION_SMILE = "Processing artifact → phantom structure"
    DISPLAY_STRETCH = "Vertical exaggeration → misinterpreted dip angle"
    SINGLE_MODEL_COLLAPSE = "Premature collapse to single inverse solution"


@dataclass
class ToACCheckResult:
    """Result of ToAC compliance check on a seismic display."""
    passed: bool
    warnings: list[ToACWarning] = field(default_factory=list)
    bond_reference: str = BOND_REF
    bond_fail_rate: float = BOND_FAIL_RATE

    def __str__(self) -> str:
        if self.passed:
            return "[ToAC: PASS]"
        return f"[ToAC: WARN — {', '.join(w.value for w in self.warnings)}]"


def check_toac(display_mode: str = "arbitrary") -> ToACCheckResult:
    """
    Check if a seismic display or interpretation passes ToAC filter.
    Must be called before any visual interpretation is accepted.
    """
    warnings: list[ToACWarning] = []

    # In production: actual QC checks against display metadata
    # Stub here returns pass for arbitrary display
    if display_mode == "arbitrary":
        return ToACCheckResult(passed=True, warnings=[])

    return ToACCheckResult(
        passed=len(warnings) == 0,
        warnings=warnings,
    )


# =============================================================================
# QUICK HELPER FUNCTIONS
# =============================================================================

def porosity_density(rhob: float, matrix: float = 2.65, fluid: float = 1.00) -> float:
    """
    Compute density porosity.
    PHI_RH = (ρ_matrix − ρ_bulk) / (ρ_matrix − ρ_fluid)

    Args:
        rhob: Bulk density reading (g/cc)
        matrix: Matrix density (default sandstone 2.65 g/cc)
        fluid: Fluid density (default water 1.00 g/cc)

    Returns:
        Porosity as fraction (0–1), clipped to [-0.1, 0.5]

    F2: This is DERIVED, not OBSERVATIONAL.
    """
    phi = (matrix - rhob) / (matrix - fluid)
    return max(-0.1, min(0.5, phi))


def saturation_archie(
    rw: float,
    rt: float,
    phi: float,
    a: float = 1.0,
    m: float = 2.0,
    n: float = 2.0,
) -> float:
    """
    Archie water saturation.
    Sw = (a * Rw / (Rt * φ^m))^1/n

    Args:
        rw: Formation water resistivity (ohm·m)
        rt: True formation resistivity (ohm·m)
        phi: Porosity as fraction (0–1)
        a, m, n: Archie parameters (default a=1, m=2, n=2)

    Returns:
        Water saturation as fraction (0–1), clipped to [0, 1]

    F2: This is DERIVED. Rw must be calibrated or declared as assumed.
    """
    if phi <= 0 or rt <= 0:
        return 1.0
    sw = (a * rw / (rt * (phi ** m))) ** (1 / n)
    return max(0.0, min(1.0, sw))


def bulk_volume_water(porosity: float, sw: float) -> float:
    """
    Bulk Volume Water = porosity × water saturation.
    VBW = Φ × Sw

    Returns fraction of bulk volume occupied by water.
    F2: This is DERIVED.
    """
    return max(0.0, min(1.0, porosity * sw))


def bulk_volume_hydrocarbon(porosity: float, sw: float) -> float:
    """
    Bulk Volume Hydrocarbon = porosity × (1 − water saturation).
    VHC = Φ × (1 − Sw)

    Returns fraction of bulk volume occupied by hydrocarbon.
    F2: This is DERIVED.
    """
    return max(0.0, min(1.0, porosity * (1.0 - sw)))


def vshale_gr(gr_log: float, gr_clean: float, gr_shale: float) -> float:
    """
    Vshale from Gamma Ray using linear method.

    Vshale = (GR_log − GR_clean) / (GR_shale − GR_clean)

    Args:
        gr_log: GR reading at point of interest (GAPI)
        gr_clean: GR of clean formation (use GR_min, 5th percentile)
        gr_shale: GR of shale (use GR_max, 95th percentile)

    Returns:
        Shale volume as fraction (0–1)

    F2: This is DERIVED. Larionov or Clavier methods more accurate for old logs.
    F4: GR_clean and GR_shale must be from local calibration.
    """
    if gr_shale <= gr_clean:
        return 1.0
    vsh = (gr_log - gr_clean) / (gr_shale - gr_clean)
    return max(0.0, min(1.0, vsh))


# =============================================================================
# MODULE __INIT__.py
# =============================================================================

__all__ = [
    "GEOX_VERSION",
    "ARIFOS_VERSION",
    "INIT_ANCHOR_VERSION",
    "BOND_REF",
    "EpistemicLevel",
    "GEOXHoldStatus",
    "HOLD_TRIGGERS",
    "WellLogConstants",
    "GEOXInterpretationResult",
    "GEOXAnchor",
    "ToACWarning",
    "ToACCheckResult",
    "check_toac",
    "porosity_density",
    "saturation_archie",
    "bulk_volume_water",
    "bulk_volume_hydrocarbon",
    "vshale_gr",
]
