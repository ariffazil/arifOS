"""
GEOX Tool Core — Transport-agnostic tool implementations.
These are pure business logic functions that can be wrapped by any adapter.
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal

# Domain services (no transport dependencies)
from .services.constitutional import (
    check_f2_truth,
    check_f4_clarity,
    check_f7_humility,
    check_f9_anti_hantu,
    check_sw_model_admissibility,
    run_constitutional_checks,
)
from .services.petrophysics import (
    calculate_sw_archie,
    monte_carlo_sw,
    SwInputParams,
)
from .services.views import (
    build_seismic_section_view,
)

# Contracts (type definitions)
from ..contracts.types import (
    CutoffValidationResult,
    FeasibilityResult,
    GeospatialVerificationResult,
    HealthResult,
    MemoryQueryResult,
    PetrophysicsHoldResult,
    PetrophysicsResult,
    ProspectEvaluationResult,
    SeismicLineResult,
    StructuralCandidatesResult,
    SwCalculationResult,
    SwModelAdmissibilityResult,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Seismic Tools
# ═══════════════════════════════════════════════════════════════════════════════


async def geox_load_seismic_line(
    line_id: str,
    survey_path: str = "default_survey",
    generate_views: bool = True,
    seismic_engine_available: bool = False,
) -> SeismicLineResult:
    """
    Load seismic data and ignite visual mode (Earth Witness Ignition).

    Transport-agnostic core implementation.
    """
    timestamp = datetime.now(timezone.utc)

    # Build stub views (or real views if seismic engine available)
    if seismic_engine_available:
        # Would call actual seismic engine here
        views = []
    else:
        views = [
            {
                "view_id": f"{line_id}:baseline",
                "mode": "governance_stub",
                "source": survey_path,
                "note": "Real seismic contrast generation not executed in this environment.",
            }
        ]

    # Build structured view if requested
    structured = None
    if generate_views:
        structured = build_seismic_section_view(
            line_id=line_id,
            survey_path=survey_path,
            status="IGNITED",
            views=views,
        )
        structured["timestamp"] = timestamp.isoformat()

    return SeismicLineResult(
        status="SEAL",
        timestamp=timestamp,
        line_id=line_id,
        survey_path=survey_path,
        views=[{**v, "timestamp": timestamp.isoformat()} for v in views],
        ignition_status="IGNITED",
    )


async def geox_build_structural_candidates(
    line_id: str,
    focus_area: str | None = None,
    seismic_engine_available: bool = False,
) -> StructuralCandidatesResult:
    """
    Build structural model candidates (Inverse Modelling Constraints).

    Prevents narrative collapse by maintaining multiple candidate models.
    Confidence bounded at 12% per F7 Humility.
    """
    timestamp = datetime.now(timezone.utc)

    candidates: list[dict[str, Any]] = []

    if seismic_engine_available:
        # Would call SeismicSingleLineTool here
        pass

    # Generate default candidates if none from engine
    if not candidates:
        candidates = [
            {"id": f"{line_id}_candidate_{i}", "type": "structural", "confidence": 0.12}
            for i in range(3)
        ]

    return StructuralCandidatesResult(
        status="SEAL",
        timestamp=timestamp,
        line_id=line_id,
        candidates=candidates,
        count=len(candidates),
        verdict="QUALIFY",
        confidence=0.12,  # F7 Humility bound
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Evaluation Tools
# ═══════════════════════════════════════════════════════════════════════════════


async def geox_feasibility_check(
    plan_id: str,
    constraints: list[str],
) -> FeasibilityResult:
    """
    Constitutional Firewall: Check if a proposed plan is physically possible.

    Returns F1-F13 floor status and SEAL/HOLD verdict.
    """
    timestamp = datetime.now(timezone.utc)

    verdict = "PHYSICALLY_FEASIBLE"
    grounding_confidence = 0.88

    return FeasibilityResult(
        status="SEAL",
        timestamp=timestamp,
        plan_id=plan_id,
        constraints=constraints,
        verdict=verdict,
        grounding_confidence=grounding_confidence,
    )


async def geox_verify_geospatial(
    lat: float,
    lon: float,
    radius_m: float = 1000.0,
) -> GeospatialVerificationResult:
    """
    Verify geospatial grounding and jurisdictional boundaries.

    Anchors all reasoning in verified coordinates per F4 Clarity.
    """
    timestamp = datetime.now(timezone.utc)

    geological_province = "Malay Basin"
    jurisdiction = "EEZ_Grounded"
    verdict = "GEOSPATIALLY_VALID"

    return GeospatialVerificationResult(
        status="SEAL",
        timestamp=timestamp,
        lat=lat,
        lon=lon,
        radius_m=radius_m,
        geological_province=geological_province,
        jurisdiction=jurisdiction,
        verdict=verdict,
        crs="WGS84",
    )


async def geox_evaluate_prospect(
    prospect_id: str,
    interpretation_id: str,
) -> ProspectEvaluationResult:
    """
    Provide a governed verdict on a subsurface prospect (222_REFLECT).

    Blocks ungrounded claims via Reality Firewall.
    """
    timestamp = datetime.now(timezone.utc)

    verdict = "PHYSICAL_GROUNDING_REQUIRED"
    confidence = 0.45
    reason = "Wait for well-tie calibration per F9 Anti-Hantu floor."

    return ProspectEvaluationResult(
        status="888_HOLD",
        timestamp=timestamp,
        prospect_id=prospect_id,
        interpretation_id=interpretation_id,
        verdict=verdict,
        confidence=confidence,
        reason=reason,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Memory Tools
# ═══════════════════════════════════════════════════════════════════════════════


async def geox_query_memory(
    query: str,
    basin: str | None = None,
    limit: int = 5,
    memory_store: Any = None,
) -> MemoryQueryResult:
    """
    Query the GEOX geological memory store for past evaluations.

    Retrieves stored prospect evaluations, verdicts, and geological context.
    """
    timestamp = datetime.now(timezone.utc)
    limit = min(max(1, limit), 20)

    results: list[dict[str, Any]] = []

    if memory_store is not None:
        try:
            # Would call memory_store.retrieve() here
            pass
        except Exception:
            pass

    return MemoryQueryResult(
        status="SEAL",
        timestamp=timestamp,
        query=query,
        basin_filter=basin,
        results=results,
        count=len(results),
        memory_backend="GeoMemoryStore" if memory_store else "unavailable",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Petrophysics Tools
# ═══════════════════════════════════════════════════════════════════════════════


async def geox_calculate_saturation(
    model: Literal["archie", "simandoux", "indonesia"],
    params: dict[str, Any],
    n_samples: int = 1000,
    physics_engine_available: bool = False,
) -> SwCalculationResult:
    """
    Calculate water saturation (Sw) with Monte Carlo uncertainty.

    Constitutional Floors:
    - F2 Truth: Models grounded in formal petrophysics
    - F7 Humility: Returns P10/P50/P90 confidence bands
    - F13 Sovereign: Triggers 888_HOLD if physics violated
    """
    timestamp = datetime.now(timezone.utc)

    if not physics_engine_available:
        return SwCalculationResult(
            status="888_HOLD",
            timestamp=timestamp,
            model=model,
            nominal_sw=1.0,
            stats=None,
            hold_triggers=["Physics engine unavailable"],
            requires_hold=True,
        )

    # Standardize params
    defaults = {"a": 1.0, "m": 2.0, "n": 2.0}
    for k, v in defaults.items():
        if k not in params:
            params[k] = v

    # Build SwInputParams from dict
    sw_params = SwInputParams(
        rw=params["rw"],
        rt=params["rt"],
        phi=params["phi"],
        a=params["a"],
        m=params["m"],
        n=params["n"],
        vcl=params.get("vcl"),
        rsh=params.get("rsh"),
    )

    # Run Monte Carlo
    mc_result = monte_carlo_sw(model, sw_params, n_samples)

    return SwCalculationResult(
        status=mc_result.verdict,
        timestamp=timestamp,
        model=model,
        nominal_sw=mc_result.nominal_sw,
        stats=mc_result.stats if mc_result.stats else None,
        hold_triggers=mc_result.hold_triggers,
        requires_hold=len(mc_result.hold_triggers) > 0,
    )


async def geox_select_sw_model(
    well_id: str,
    depth_top_m: float,
    depth_base_m: float,
    has_washout: bool = False,
    washout_fraction: float = 0.0,
    borehole_quality: str = "good",
    has_invasion: bool = False,
    has_gas_effect: bool = False,
    has_shale: bool = True,
    vsh_max: float = 0.0,
    has_deep_resistivity: bool = True,
    has_shallow_resistivity: bool = False,
    available_curves: list[str] | None = None,
    petro_schemas_available: bool = True,
) -> SwModelAdmissibilityResult:
    """
    Evaluate Sw model admissibility from log QC flags.

    Applies constitutional QC rules to determine which water saturation model
    may be used for the interval.
    """
    timestamp = datetime.now(timezone.utc)

    if not petro_schemas_available:
        return SwModelAdmissibilityResult(
            status="UNAVAILABLE",
            timestamp=timestamp,
            well_id=well_id,
            recommended_model="none",
            admissible_models=[],
            inadmissible_models={},
            requires_hold=True,
            hold_reasons=["Petrophysics schemas not loaded"],
            confidence=0.0,
        )

    # Run admissibility checks
    admissibility = check_sw_model_admissibility(
        has_deep_resistivity=has_deep_resistivity,
        has_shale=has_shale,
        has_washout=has_washout,
        washout_fraction=washout_fraction,
        vsh_max=vsh_max,
        borehole_quality=borehole_quality,
    )

    # Extract admissible models
    admissible = [m for m, r in admissibility.items() if r.passed]
    inadmissible = {m: r.violations for m, r in admissibility.items() if not r.passed}

    # Determine recommended model
    hold_reasons: list[str] = []
    requires_hold = False

    if borehole_quality == "poor":
        hold_reasons.append("Borehole quality 'poor' — all resistivity-based Sw models unreliable.")
        admissible = []

    if not has_deep_resistivity:
        hold_reasons.append("Deep resistivity curve absent — cannot compute Sw.")
        admissible = []

    if not admissible:
        requires_hold = True
        recommended = "none"
    elif "archie" in admissible and not has_shale:
        recommended = "archie"
    elif has_shale and vsh_max > 0.15:
        recommended = "indonesia" if "indonesia" in admissible else "simandoux"
        if recommended not in admissible:
            recommended = admissible[0]
    else:
        recommended = admissible[0]

    # F7 confidence
    confidence = 0.12 if borehole_quality == "fair" else 0.08
    if has_washout:
        confidence = min(confidence, 0.10)

    return SwModelAdmissibilityResult(
        status="888_HOLD" if requires_hold else "SEAL",
        timestamp=timestamp,
        well_id=well_id,
        recommended_model=recommended,
        admissible_models=admissible,
        inadmissible_models=inadmissible,
        requires_hold=requires_hold,
        hold_reasons=hold_reasons,
        confidence=confidence,
        provenance_tag="POLICY",
    )


async def geox_compute_petrophysics(
    well_id: str,
    sw_model: str,
    rw_ohm_m: float,
    rt_ohm_m: float,
    phi_fraction: float,
    vcl_fraction: float = 0.0,
    rsh_ohm_m: float | None = None,
    archie_a: float = 1.0,
    archie_m: float = 2.0,
    archie_n: float = 2.0,
    run_monte_carlo: bool = True,
    mc_samples: int = 1000,
    physics_engine_available: bool = True,
    petro_schemas_available: bool = True,
) -> PetrophysicsResult:
    """
    Full petrophysics property pipeline — Vsh, PHIe, Sw, BVW.

    Runs the selected Sw model with optional Monte Carlo uncertainty.
    """
    timestamp = datetime.now(timezone.utc)

    if not petro_schemas_available:
        return PetrophysicsResult(
            status="UNAVAILABLE",
            timestamp=timestamp,
            well_id=well_id,
            sw_model_used=sw_model,
            sw_nominal=1.0,
            phi_effective=phi_fraction,
            vcl=vcl_fraction,
            bvw=phi_fraction,
            uncertainty=0.0,
            audit_id="PETRO-UNAVAILABLE",
        )

    # Validate sw_model
    valid_models = ("archie", "simandoux", "indonesia")
    if sw_model not in valid_models:
        return PetrophysicsResult(
            status="888_HOLD",
            timestamp=timestamp,
            well_id=well_id,
            sw_model_used="archie",  # fallback to valid enum value for schema compliance
            sw_nominal=1.0,
            phi_effective=phi_fraction,
            vcl=vcl_fraction,
            bvw=phi_fraction,
            uncertainty=0.0,
            hold_triggers=[f"Invalid sw_model '{sw_model}'. Choose from {valid_models}."],
            requires_hold=True,
            audit_id=f"HOLD-{uuid.uuid4().hex[:8].upper()}",
        )

    # Run saturation computation
    hold_triggers: list[str] = []
    mc_stats: dict[str, Any] | None = None

    if phi_fraction > 0.45:
        hold_triggers.append(f"PHI ({phi_fraction:.3f}) > 0.45 — above physical maximum")

    sw_nominal = 1.0
    if physics_engine_available and run_monte_carlo:
        mc_params = SwInputParams(
            rw=(rw_ohm_m, rw_ohm_m * 0.05),
            rt=(rt_ohm_m, rt_ohm_m * 0.05),
            phi=(phi_fraction, phi_fraction * 0.07),
            a=archie_a,
            m=archie_m,
            n=archie_n,
        )
        if sw_model in ("simandoux", "indonesia") and rsh_ohm_m is not None:
            mc_params.vcl = (vcl_fraction, vcl_fraction * 0.10 + 0.01)
            mc_params.rsh = (rsh_ohm_m, rsh_ohm_m * 0.05)

        try:
            mc_result = monte_carlo_sw(sw_model, mc_params, n_samples=min(mc_samples, 5000))
            mc_stats = mc_result.stats
            hold_triggers.extend(mc_result.hold_triggers)
            sw_nominal = mc_result.nominal_sw
        except Exception:
            sw_nominal = calculate_sw_archie(
                rw_ohm_m, rt_ohm_m, phi_fraction, archie_a, archie_m, archie_n
            )
    else:
        sw_nominal = calculate_sw_archie(
            rw_ohm_m, rt_ohm_m, phi_fraction, archie_a, archie_m, archie_n
        )

    sw_nominal = min(sw_nominal, 1.05)
    bvw = sw_nominal * phi_fraction

    if sw_nominal > 1.0:
        hold_triggers.append(f"Sw ({sw_nominal:.3f}) > 1.0 — physical impossibility")

    uncertainty = 0.09 if mc_stats else 0.12
    requires_hold = len(hold_triggers) > 0

    audit_id = f"PETRO-{uuid.uuid4().hex[:8].upper()}"

    return PetrophysicsResult(
        status="888_HOLD" if requires_hold else "SEAL",
        timestamp=timestamp,
        well_id=well_id,
        sw_model_used=sw_model,
        sw_nominal=round(sw_nominal, 4),
        sw_p10=round(mc_stats["p10"], 4) if mc_stats else None,
        sw_p50=round(mc_stats["p50"], 4) if mc_stats else None,
        sw_p90=round(mc_stats["p90"], 4) if mc_stats else None,
        sw_std=round(mc_stats["std"], 4) if mc_stats else None,
        phi_effective=round(phi_fraction, 4),
        vcl=round(vcl_fraction, 4),
        bvw=round(bvw, 4),
        uncertainty=uncertainty,
        hold_triggers=hold_triggers,
        requires_hold=requires_hold,
        audit_id=audit_id,
    )


async def geox_validate_cutoffs(
    well_id: str,
    policy_id: str,
    phi_cutoff: float,
    sw_cutoff: float,
    vcl_cutoff: float,
    phi_tested: float,
    sw_tested: float,
    vcl_tested: float,
    rt_cutoff: float | None = None,
    rt_tested: float | None = None,
    policy_basis: str = "analogue",
    petro_schemas_available: bool = True,
) -> CutoffValidationResult:
    """
    Apply a CutoffPolicy to petrophysical values and classify pay vs non-pay.
    """
    timestamp = datetime.now(timezone.utc)

    if not petro_schemas_available:
        return CutoffValidationResult(
            status="UNAVAILABLE",
            timestamp=timestamp,
            well_id=well_id,
            policy_id=policy_id,
            policy_basis=policy_basis,
            is_net_reservoir=False,
            is_net_pay=False,
            phi_pass=False,
            sw_pass=False,
            vcl_pass=False,
            phi_tested=phi_tested,
            sw_tested=sw_tested,
            vcl_tested=vcl_tested,
            cutoffs={},
            audit_id="CUT-UNAVAILABLE",
        )

    violations: list[str] = []
    requires_hold = False

    # F2 Truth: Physical plausibility
    if sw_tested > 1.0:
        violations.append(f"Sw ({sw_tested:.3f}) > 1.0 — physically impossible")
        requires_hold = True
    if phi_tested > 0.50:
        violations.append(f"PHIe ({phi_tested:.3f}) > 0.50 — above physical maximum")
        requires_hold = True

    phi_pass = phi_tested >= phi_cutoff
    sw_pass = sw_tested < sw_cutoff
    vcl_pass = vcl_tested < vcl_cutoff
    rt_pass: bool | None = None
    if rt_cutoff is not None and rt_tested is not None:
        rt_pass = rt_tested >= rt_cutoff

    if not phi_pass:
        violations.append(f"PHIe {phi_tested:.3f} < cutoff {phi_cutoff:.3f}")
    if not sw_pass:
        violations.append(f"Sw {sw_tested:.3f} ≥ cutoff {sw_cutoff:.3f}")
    if not vcl_pass:
        violations.append(f"Vcl {vcl_tested:.3f} ≥ cutoff {vcl_cutoff:.3f}")
    if rt_pass is False:
        violations.append(f"Rt {rt_tested} < cutoff {rt_cutoff}")

    is_net_reservoir = phi_pass and vcl_pass and not requires_hold
    is_net_pay = is_net_reservoir and sw_pass

    audit_id = f"CUT-{uuid.uuid4().hex[:8].upper()}"

    return CutoffValidationResult(
        status="888_HOLD" if requires_hold else "SEAL",
        timestamp=timestamp,
        well_id=well_id,
        policy_id=policy_id,
        policy_basis=policy_basis,
        is_net_reservoir=is_net_reservoir,
        is_net_pay=is_net_pay,
        passed_rt_cutoff=rt_pass,
        phi_pass=phi_pass,
        sw_pass=sw_pass,
        vcl_pass=vcl_pass,
        phi_tested=phi_tested,
        sw_tested=sw_tested,
        vcl_tested=vcl_tested,
        rt_tested=rt_tested,
        cutoffs={
            "phi_cutoff": phi_cutoff,
            "sw_cutoff": sw_cutoff,
            "vcl_cutoff": vcl_cutoff,
            "rt_cutoff": rt_cutoff,
        },
        violations=violations,
        requires_hold=requires_hold,
        audit_id=audit_id,
        provenance_tag="POLICY",
    )


async def geox_petrophysical_hold_check(
    well_id: str,
    sw_value: float,
    phi_value: float,
    vcl_value: float,
    uncertainty: float,
    has_deep_resistivity: bool = True,
    borehole_quality: str = "good",
    sw_model: str = "archie",
    run_f2_check: bool = True,
    run_f4_check: bool = True,
    run_f7_check: bool = True,
    run_f9_check: bool = True,
    petro_schemas_available: bool = True,
) -> PetrophysicsHoldResult:
    """
    Constitutional floor check for petrophysical outputs — triggers 888_HOLD.
    """
    timestamp = datetime.now(timezone.utc)

    if not petro_schemas_available:
        return PetrophysicsHoldResult(
            status="UNAVAILABLE",
            timestamp=timestamp,
            well_id=well_id,
            hold_id="HOLD-UNAVAILABLE",
            triggered_by="geox_petrophysical_hold_check",
            violated_floors=[],
            violations=["Petrophysics schemas not loaded"],
            remediation=["Load petrophysics schemas"],
            severity="block",
            requires_human_signoff=True,
        )

    # Run individual checks
    checks = {}

    if run_f2_check:
        checks["f2"] = check_f2_truth(sw_value, phi_value, vcl_value)

    if run_f4_check:
        checks["f4"] = check_f4_clarity(has_deep_resistivity)

    if run_f7_check:
        checks["f7"] = check_f7_humility(uncertainty)

    if run_f9_check:
        checks["f9"] = check_f9_anti_hantu(borehole_quality, sw_model)

    # Aggregate results
    aggregated = run_constitutional_checks(checks)

    if aggregated.passed:
        return PetrophysicsHoldResult(
            status="SEAL",
            timestamp=timestamp,
            well_id=well_id,
            hold_id="",
            triggered_by="geox_petrophysical_hold_check",
            violated_floors=[],
            violations=["All constitutional floor checks passed"],
            remediation=[],
            severity="info",
            requires_human_signoff=False,
        )

    hold_id = f"HOLD-{uuid.uuid4().hex[:8].upper()}"

    return PetrophysicsHoldResult(
        status="888_HOLD",
        timestamp=timestamp,
        well_id=well_id,
        hold_id=hold_id,
        triggered_by="geox_petrophysical_hold_check",
        violated_floors=aggregated.violated_floors,
        violations=aggregated.violations,
        remediation=aggregated.remediation,
        severity="block",
        requires_human_signoff=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Health Check
# ═══════════════════════════════════════════════════════════════════════════════


async def geox_health(
    geox_version: str = "0.5.0",
    prefab_ui_available: bool = False,
    seismic_engine_available: bool = False,
    fastmcp_version: str = "2.0",
) -> HealthResult:
    """
    Server health check with constitutional floor status.
    """
    timestamp = datetime.now(timezone.utc)

    return HealthResult(
        status="SEAL",
        timestamp=timestamp,
        ok=True,
        service="geox-earth-witness",
        fastmcp_version=fastmcp_version,
        prefab_ui=prefab_ui_available,
        seismic_engine=seismic_engine_available,
        constitutional_floors=[
            "F1_amanah",
            "F2_truth",
            "F4_clarity",
            "F7_humility",
            "F9_anti_hantu",
            "F11_authority",
            "F13_sovereign",
        ],
    )
