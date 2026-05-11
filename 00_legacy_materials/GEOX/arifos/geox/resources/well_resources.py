"""
GEOX MCP Resources — Well and Log Data
DITEMPA BUKAN DIBERI

MCP resources provide application-controlled context with stable URIs.
These are NOT tools — they are data that both UI and LLMs can reference.

URI Schemes:
- geox://well/{well_id}/las/bundle
- geox://well/{well_id}/logs/canonical
- geox://well/{well_id}/interval/{top}-{base}/rock-state
- geox://well/{well_id}/cutoff-policy/{policy_id}
- geox://well/{well_id}/qc/report
"""

from __future__ import annotations

from typing import Any

from arifos.geox.tools.petrophysics.log_bundle_loader import (
    load_bundle_from_store,
    apply_environmental_corrections,
)
from arifos.geox.tools.petrophysics.qc_engine import (
    load_qc_report,
)


class Resource:
    """Base class for MCP resources."""

    uri_template: str = ""

    async def read(self, **kwargs) -> dict[str, Any]:
        raise NotImplementedError


class WellLogBundleResource(Resource):
    """
    URI: geox://well/{well_id}/las/bundle

    Canonical LAS/DLIS bundle with parsed header, curves, and QC status.
    Provenance: RAW
    """

    uri_template = "geox://well/{well_id}/las/bundle"

    async def read(self, well_id: str) -> dict[str, Any]:
        """Return the log bundle for this well."""
        bundle = await load_bundle_from_store(well_id)

        return {
            "uri": f"geox://well/{well_id}/las/bundle",
            "well_id": well_id,
            "well_name": bundle.well_name,
            "source_files": bundle.source_files,
            "bundle_created": bundle.bundle_created.isoformat(),
            "header": bundle.header,
            "curves": [
                {
                    "mnemonic": c.mnemonic,
                    "name": c.name,
                    "units": c.units,
                    "depth_points": len(c.depth),
                    "min_value": c.min_value,
                    "max_value": c.max_value,
                }
                for c in bundle.curves.values()
            ],
            "depth_range": {
                "min": bundle.min_depth,
                "max": bundle.max_depth,
                "unit": bundle.depth_unit,
                "reference": bundle.depth_reference,
            },
            "location": (
                {
                    "latitude": bundle.latitude,
                    "longitude": bundle.longitude,
                    "elevation": bundle.elevation,
                }
                if bundle.latitude
                else None
            ),
            "qc_summary": bundle.qc_summary,
            "provenance": "RAW",
            "floor_check": {
                "F4_clarity": all(c.units for c in bundle.curves.values()),
                "F9_anti_hantu": len(bundle.source_files) > 0,
            },
        }


class CanonicalLogsResource(Resource):
    """
    URI: geox://well/{well_id}/logs/canonical

    Curves with environmental corrections applied.
    Provenance: CORRECTED
    """

    uri_template = "geox://well/{well_id}/logs/canonical"

    async def read(self, well_id: str) -> dict[str, Any]:
        """Return environmentally-corrected curves."""
        bundle = await load_bundle_from_store(well_id)
        corrected = await apply_environmental_corrections(bundle)

        return {
            "uri": f"geox://well/{well_id}/logs/canonical",
            "well_id": well_id,
            "well_name": bundle.well_name,
            "corrections_applied": corrected.get("corrections", []),
            "depth_reference": bundle.depth_reference,
            "curves": {
                c.mnemonic: {
                    "values": c.values[:100],  # Truncate for MCP transport
                    "depth": c.depth[:100],
                    "units": c.units,
                    "min": c.min_value,
                    "max": c.max_value,
                }
                for c in corrected.get("curves", bundle.curves.values())
            },
            "provenance": "CORRECTED",
            "note": "Full data available via geox_load_well_log_bundle tool",
        }


class IntervalRockStateResource(Resource):
    """
    URI: geox://well/{well_id}/interval/{top}-{base}/rock-state

    Petrophysical interpretation for a specific interval.
    Provenance: DERIVED
    """

    uri_template = "geox://well/{well_id}/interval/{top}-{base}/rock-state"

    async def read(self, well_id: str, top: float, base: float) -> dict[str, Any]:
        """Return rock state for interval."""
        # Import here to avoid circular dependency
        from arifos.geox.tools.petrophysics.property_calculator import load_rock_state

        state = await load_rock_state(well_id, top, base)

        if state is None:
            return {
                "uri": f"geox://well/{well_id}/interval/{top}-{base}/rock-state",
                "error": "No rock state found for this interval",
                "available_actions": ["Run geox_compute_petrophysics tool"],
            }

        return {
            "uri": f"geox://well/{well_id}/interval/{top}-{base}/rock-state",
            "well_id": well_id,
            "interval": {"top_m": top, "base_m": base},
            "state_id": state.state_id,
            "porosity": (
                {
                    "value": (state.effective_porosity.value if state.effective_porosity else None),
                    "units": (state.effective_porosity.units if state.effective_porosity else None),
                    "ci_95": [
                        (
                            state.effective_porosity.confidence_95_low
                            if state.effective_porosity
                            else None
                        ),
                        (
                            state.effective_porosity.confidence_95_high
                            if state.effective_porosity
                            else None
                        ),
                    ],
                    "model": state.porosity_model_used,
                }
                if state.effective_porosity
                else None
            ),
            "water_saturation": (
                {
                    "value": (state.water_saturation.value if state.water_saturation else None),
                    "model": (
                        state.water_saturation.model_family if state.water_saturation else None
                    ),
                    "ci_95": [
                        (
                            state.water_saturation.confidence_95_low
                            if state.water_saturation
                            else None
                        ),
                        (
                            state.water_saturation.confidence_95_high
                            if state.water_saturation
                            else None
                        ),
                    ],
                    "assumption_violations": (
                        state.water_saturation.assumption_violations
                        if state.water_saturation
                        else []
                    ),
                }
                if state.water_saturation
                else None
            ),
            "permeability": (
                {
                    "value_md": (state.permeability.value_md if state.permeability else None),
                    "method": state.permeability.method if state.permeability else None,
                }
                if state.permeability
                else None
            ),
            "classification": {
                "net_reservoir": state.is_net_reservoir,
                "net_pay": state.is_net_pay,
                "net_to_gross": state.net_to_gross,
                "cutoff_policy": state.cutoff_policy_id,
            },
            "verdict": state.verdict,
            "hold_reasons": state.hold_reasons,
            "floor_check": state.floor_check,
            "provenance": "DERIVED",
            "created_at": state.created_at.isoformat() if state.created_at else None,
        }


class CutoffPolicyResource(Resource):
    """
    URI: geox://well/{well_id}/cutoff-policy/{policy_id}

    Active cutoff policy for this well/formation.
    Provenance: POLICY
    """

    uri_template = "geox://well/{well_id}/cutoff-policy/{policy_id}"

    async def read(self, well_id: str, policy_id: str) -> dict[str, Any]:
        """Return cutoff policy."""
        from arifos.geox.tools.petrophysics.cutoff_validator import load_cutoff_policy

        policy = await load_cutoff_policy(policy_id)

        if policy is None:
            return {
                "uri": f"geox://well/{well_id}/cutoff-policy/{policy_id}",
                "error": "Policy not found",
            }

        return {
            "uri": f"geox://well/{well_id}/cutoff-policy/{policy_id}",
            "policy_id": policy_id,
            "policy_name": policy.policy_name,
            "version": policy.version,
            "cutoffs": {
                "porosity": {
                    "threshold": (
                        policy.porosity_cutoff.threshold_value if policy.porosity_cutoff else None
                    ),
                    "rationale": (
                        policy.porosity_cutoff.physics_justification
                        if policy.porosity_cutoff
                        else None
                    ),
                },
                "vsh": {
                    "threshold": (policy.vsh_cutoff.threshold_value if policy.vsh_cutoff else None),
                    "rationale": (
                        policy.vsh_cutoff.calibration_basis if policy.vsh_cutoff else None
                    ),
                },
                "sw_oil": {
                    "threshold": (
                        policy.sw_cutoff_oil.threshold_value if policy.sw_cutoff_oil else None
                    ),
                },
            },
            "applicable_scope": {
                "basins": policy.applicable_basins,
                "formations": policy.applicable_formations,
                "fluid_systems": policy.applicable_fluid_systems,
            },
            "governance": {
                "defined_by": (
                    policy.porosity_cutoff.defined_by if policy.porosity_cutoff else None
                ),
                "approved_by": policy.approved_by,
                "approval_date": (
                    policy.approval_date.isoformat() if policy.approval_date else None
                ),
            },
            "is_active": policy.is_active,
            "provenance": "POLICY",
        }


class QCReportResource(Resource):
    """
    URI: geox://well/{well_id}/qc/report

    Quality control findings for all well data.
    """

    uri_template = "geox://well/{well_id}/qc/report"

    async def read(self, well_id: str) -> dict[str, Any]:
        """Return QC report."""
        report = await load_qc_report(well_id)

        if report is None:
            return {
                "uri": f"geox://well/{well_id}/qc/report",
                "error": "No QC report found",
                "available_actions": ["Run geox_qc_logs tool"],
            }

        return {
            "uri": f"geox://well/{well_id}/qc/report",
            "well_id": well_id,
            "generated": (report.report_generated.isoformat() if report.report_generated else None),
            "overall_status": report.overall,
            "curve_count": len(report.curve_reports),
            "curves": [
                {
                    "mnemonic": c.mnemonic,
                    "completeness": c.completeness,
                    "flags": c.flags,
                    "usable": c.usable_for_petrophysics,
                }
                for c in report.curve_reports
            ],
            "issues": {
                "depth": report.depth_issues,
                "units": report.unit_inconsistencies,
                "missing_critical": report.missing_critical_curves,
            },
            "recommendations": report.recommendations,
        }


# Resource registry for MCP server
RESOURCE_REGISTRY = {
    "well_bundle": WellLogBundleResource,
    "canonical_logs": CanonicalLogsResource,
    "rock_state": IntervalRockStateResource,
    "cutoff_policy": CutoffPolicyResource,
    "qc_report": QCReportResource,
}


async def get_resource(uri: str) -> dict[str, Any]:
    """
    Route a URI to the appropriate resource handler.

    Parses URI pattern: geox://well/{well_id}/...
    """
    if not uri.startswith("geox://well/"):
        return {"error": f"Invalid GEOX URI: {uri}"}

    # Parse URI
    parts = uri.replace("geox://well/", "").split("/")
    well_id = parts[0]
    resource_type = parts[1] if len(parts) > 1 else ""

    # Route to handler
    if resource_type == "las" and len(parts) > 2 and parts[2] == "bundle":
        return await WellLogBundleResource().read(well_id)

    elif resource_type == "logs" and len(parts) > 2 and parts[2] == "canonical":
        return await CanonicalLogsResource().read(well_id)

    elif resource_type == "interval" and len(parts) > 2:
        # Parse interval/top-base/rock-state
        interval_part = parts[2]
        if "-" in interval_part:
            top_str, base_str = interval_part.split("-", 1)
            top, base = float(top_str), float(base_str)
            return await IntervalRockStateResource().read(well_id, top, base)

    elif resource_type == "cutoff-policy" and len(parts) > 2:
        policy_id = parts[2]
        return await CutoffPolicyResource().read(well_id, policy_id)

    elif resource_type == "qc" and len(parts) > 2 and parts[2] == "report":
        return await QCReportResource().read(well_id)

    return {"error": f"Unknown resource path: {uri}"}
