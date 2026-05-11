"""
GEOX Constitutional Services — Floor checking logic.
Pure domain logic for F1-F13 constitutional enforcement.
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ═══════════════════════════════════════════════════════════════════════════════
# Data Classes
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ConstitutionalCheckResult:
    """Result from constitutional floor checks."""

    passed: bool
    violated_floors: list[str] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
    remediation: list[str] = field(default_factory=list)
    confidence: float = 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# Individual Floor Checks
# ═══════════════════════════════════════════════════════════════════════════════


def check_f2_truth(
    sw_value: float | None = None,
    phi_value: float | None = None,
    vcl_value: float | None = None,
) -> ConstitutionalCheckResult:
    """
    Check F2 Truth: Physical possibility.

    - Sw must be <= 1.0
    - PHI must be <= 0.50 (physical max for clastic)
    - Vcl must be in [0, 1]
    """
    violations = []
    remediation = []

    if sw_value is not None and sw_value > 1.0:
        violations.append(f"Sw ({sw_value:.4f}) > 1.0 — physically impossible.")
        remediation.append("Re-check Rw, Rt, and PHIe inputs; verify LAS data quality.")

    if phi_value is not None and phi_value > 0.50:
        violations.append(
            f"PHIe ({phi_value:.4f}) > 0.50 — above physical maximum for clastic reservoir."
        )
        remediation.append(
            "Review NPHI-RHOB crossplot; check matrix density assumption."
        )

    if vcl_value is not None and not (0.0 <= vcl_value <= 1.0):
        violations.append(
            f"Vcl ({vcl_value:.4f}) outside [0, 1] — physical impossibility."
        )
        remediation.append("Re-compute Vsh from GR using calibrated GR_min / GR_max.")

    return ConstitutionalCheckResult(
        passed=len(violations) == 0,
        violated_floors=["F2"] if violations else [],
        violations=violations,
        remediation=remediation,
    )


def check_f4_clarity(
    has_deep_resistivity: bool = True,
    has_crs: bool = True,
    crs_defined: bool = True,
) -> ConstitutionalCheckResult:
    """
    Check F4 Clarity: Measurement basis and CRS.

    - Must have deep resistivity for Sw calculation
    - CRS must be defined for geospatial data
    """
    violations = []
    remediation = []

    if not has_deep_resistivity:
        violations.append(
            "No deep resistivity available — Sw has no physical measurement basis."
        )
        remediation.append("Acquire ILD/LLD before computing Sw.")

    if not has_crs:
        violations.append("CRS not specified — geospatial coordinates ambiguous.")
        remediation.append("Define CRS (e.g., EPSG:4326) for all coordinates.")

    if not crs_defined:
        violations.append("CRS defined but not validated — potential misalignment.")
        remediation.append("Validate CRS against known survey control points.")

    return ConstitutionalCheckResult(
        passed=len(violations) == 0,
        violated_floors=["F4"] if violations else [],
        violations=violations,
        remediation=remediation,
    )


def check_f7_humility(
    uncertainty: float,
    humility_band: tuple[float, float] = (0.03, 0.15),
) -> ConstitutionalCheckResult:
    """
    Check F7 Humility: Uncertainty quantification.

    - Uncertainty must be in [0.03, 0.15]
    - Values outside indicate overconfidence or unquantified uncertainty
    """
    violations = []
    remediation = []

    min_uncertainty, max_uncertainty = humility_band

    if not (min_uncertainty <= uncertainty <= max_uncertainty):
        violations.append(
            f"Uncertainty ({uncertainty:.3f}) outside F7 humility band "
            f"[{min_uncertainty}, {max_uncertainty}]. "
            "Overconfident or unquantified uncertainty detected."
        )
        remediation.append("Run Monte Carlo to obtain calibrated uncertainty.")

    return ConstitutionalCheckResult(
        passed=len(violations) == 0,
        violated_floors=["F7"] if violations else [],
        violations=violations,
        remediation=remediation,
        confidence=uncertainty,
    )


def check_f9_anti_hantu(
    borehole_quality: str = "good",
    sw_model: str | None = None,
    valid_models: tuple[str, ...] = ("archie", "simandoux", "indonesia"),
    has_verification: bool = True,
) -> ConstitutionalCheckResult:
    """
    Check F9 Anti-Hantu: Data integrity and verification.

    - Borehole quality must be adequate
    - Sw model must be from verified set
    - Results must have physical verification basis
    """
    violations = []
    remediation = []

    if borehole_quality == "poor":
        violations.append(
            "Borehole quality 'poor' — log data integrity compromised; "
            "Sw derived from unverified inputs."
        )
        remediation.append(
            "Collect repeat / backup resistivity pass; cross-check with nearby wells."
        )

    if sw_model is not None and sw_model not in valid_models:
        violations.append(
            f"Unknown Sw model '{sw_model}' — unverified computation path."
        )
        remediation.append(f"Use one of: {valid_models}.")

    if not has_verification:
        violations.append("No physical verification basis — interpretation ungrounded.")
        remediation.append("Add well tie or core calibration before finalizing.")

    return ConstitutionalCheckResult(
        passed=len(violations) == 0,
        violated_floors=["F9"] if violations else [],
        violations=violations,
        remediation=remediation,
    )


def check_f11_authority(
    has_permission: bool = True,
    data_source_verified: bool = True,
) -> ConstitutionalCheckResult:
    """
    Check F11 Authority: Audit trail and permissions.

    - User must have permission for operation
    - Data source must be verified and documented
    """
    violations = []
    remediation = []

    if not has_permission:
        violations.append("Insufficient permissions for this operation.")
        remediation.append("Request elevated access from administrator.")

    if not data_source_verified:
        violations.append("Data source not verified — audit trail incomplete.")
        remediation.append("Document data provenance and verify source authority.")

    return ConstitutionalCheckResult(
        passed=len(violations) == 0,
        violated_floors=["F11"] if violations else [],
        violations=violations,
        remediation=remediation,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Composite Checks
# ═══════════════════════════════════════════════════════════════════════════════


def run_constitutional_checks(
    checks: dict[str, ConstitutionalCheckResult],
) -> ConstitutionalCheckResult:
    """
    Aggregate multiple constitutional checks into a single result.

    Args:
        checks: Dict of check name -> check result

    Returns:
        Aggregated result (passed only if all checks passed)
    """
    all_violated = []
    all_violations = []
    all_remediation = []

    for check in checks.values():
        all_violated.extend(check.violated_floors)
        all_violations.extend(check.violations)
        all_remediation.extend(check.remediation)

    # Deduplicate floors
    all_violated = sorted(set(all_violated))

    return ConstitutionalCheckResult(
        passed=len(all_violated) == 0,
        violated_floors=all_violated,
        violations=all_violations,
        remediation=all_remediation,
    )


def check_sw_model_admissibility(
    has_deep_resistivity: bool,
    has_shale: bool,
    has_washout: bool,
    washout_fraction: float,
    vsh_max: float,
    borehole_quality: str,
) -> dict[str, ConstitutionalCheckResult]:
    """
    Check admissibility of Sw models based on data quality.

    Returns per-model admissibility results.
    """
    results = {}

    # Archie: clean sand, deep resistivity required
    archie_violations = []
    if not has_deep_resistivity:
        archie_violations.append("No deep resistivity curve — Rt unavailable.")
    if has_washout and washout_fraction > 0.30:
        archie_violations.append(
            f"Washout fraction {washout_fraction:.0%} > 30% — resistivity unreliable."
        )
    if has_shale and vsh_max > 0.20:
        archie_violations.append(
            f"Vsh_max {vsh_max:.2f} > 0.20 — Archie invalid for shaly sand."
        )

    results["archie"] = ConstitutionalCheckResult(
        passed=len(archie_violations) == 0,
        violated_floors=["F4", "F9"] if archie_violations else [],
        violations=archie_violations,
        remediation=(
            ["Use Simandoux or Indonesia for shaly sands."] if archie_violations else []
        ),
    )

    # Simandoux / Indonesia: require shale indicators
    for model in ["simandoux", "indonesia"]:
        violations = []
        if not has_deep_resistivity:
            violations.append("No deep resistivity — Rt unavailable.")
        if not has_shale:
            violations.append(f"No shale detected — {model} over-parameterised.")
        if has_washout and washout_fraction > 0.40:
            violations.append(
                f"Washout fraction {washout_fraction:.0%} > 40% — shaly-sand model unreliable."
            )

        results[model] = ConstitutionalCheckResult(
            passed=len(violations) == 0,
            violated_floors=["F4", "F9"] if violations else [],
            violations=violations,
            remediation=["Use Archie for clean sands."] if violations else [],
        )

    # Overall borehole quality check
    if borehole_quality == "poor":
        for model in results:
            results[model].passed = False
            results[model].violated_floors.append("F9")
            results[model].violations.append(
                "Borehole quality 'poor' — all resistivity-based Sw models unreliable."
            )

    return results
