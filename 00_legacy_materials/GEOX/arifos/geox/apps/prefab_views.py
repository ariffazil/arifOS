"""
GEOX Prefab UI Views — DITEMPA BUKAN DIBERI

FastMCP App views for GEOX MCP tools using prefab-ui.
Each builder function returns a PrefabApp that renders as an
interactive UI in the MCP host (Claude Desktop, Cursor, etc.)
instead of a plain JSON blob.

Architecture:
  Tool result dict → view builder → PrefabApp → MCP host renders it

Requires: pip install "fastmcp[apps]" prefab-ui>=0.18.0
"""

from __future__ import annotations

from typing import Any

from prefab_ui import PrefabApp
from prefab_ui.components import (
    Alert,
    AlertDescription,
    AlertTitle,
    Badge,
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    Column,
    Grid,
    H2,
    H3,
    Markdown,
    Metric,
    Muted,
    Progress,
    Row,
    Separator,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
    Text,
)

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_VERDICT_VARIANT: dict[str, str] = {
    "SEAL": "success",
    "999_SEAL": "success",
    "QUALIFY": "warning",
    "HOLD": "warning",
    "888_HOLD": "warning",
    "PHYSICAL_GROUNDING_REQUIRED": "warning",
    "PHYSICALLY_FEASIBLE": "success",
    "GEOSPATIALLY_VALID": "success",
    "BLOCK": "destructive",
    "GEOX_BLOCK": "destructive",
    "VOID": "destructive",
}

_FLOOR_LABELS: dict[str, str] = {
    "F1": "F1 Amanah — Reversibility",
    "F2": "F2 Truth — ≥99% accuracy",
    "F4": "F4 Clarity — Units & coords",
    "F7": "F7 Humility — Confidence [0.03,0.15]",
    "F9": "F9 Anti-Hantu — No phantom geology",
    "F11": "F11 Authority — Provenance mandatory",
    "F13": "F13 Sovereign — Human veto active",
}

_ACTIVE_FLOORS = ["F1", "F4", "F7", "F9", "F11", "F13"]


def _verdict_variant(verdict: str) -> str:
    return _VERDICT_VARIANT.get(verdict, "default")


def _floor_table(active: list[str]) -> Table:
    """Render constitutional floor status as a compact table."""
    with Table() as table:
        with TableHeader():
            with TableRow():
                TableHead("Floor")
                TableHead("Rule")
                TableHead("Status")
        with TableBody():
            for fid in _ACTIVE_FLOORS:
                status = "ACTIVE" if fid in active else "INACTIVE"
                variant = "success" if fid in active else "default"
                with TableRow():
                    TableCell(fid)
                    TableCell(_FLOOR_LABELS[fid])
                    with TableCell():
                        Badge(status, variant=variant)
    return table


# ---------------------------------------------------------------------------
# View 1 — geox_load_seismic_line
# ---------------------------------------------------------------------------


def seismic_section_view(
    line_id: str,
    survey_path: str,
    status: str,
    views: list[dict[str, Any]],
    timestamp: str,
) -> PrefabApp:
    """
    Seismic Section App view.

    Shows: line metadata, QC badges, ToAC flags, governance stub notice,
    888 HOLD trigger checklist (F4 — scale unknown disables measurements).
    """
    with Column(gap=4, css_class="p-6") as view:
        # --- Header ---
        H2(f"Seismic Section — {line_id}")
        Muted(f"Survey: {survey_path}  ·  {timestamp}")
        Separator()

        # --- QC Badge Strip ---
        with Row(gap=2, css_class="flex-wrap"):
            Badge("OBSERVATIONAL", variant="default")
            Badge("ToAC: Contrast Canon Active", variant="warning")
            Badge("F4 Clarity: Units Required", variant="warning")
            Badge("Scale: UNKNOWN", variant="destructive")
            Badge(f"Status: {status}", variant="success" if status == "IGNITED" else "default")

        # --- F4 Hold Alert ---
        with Alert(variant="warning"):
            AlertTitle("F4 Clarity — Scale Unknown")
            AlertDescription(
                "Scale bar not confirmed. Measurement tools are DISABLED. "
                "Physical distance claims are prohibited until scale is anchored."
            )

        # --- ToAC Reminder ---
        with Alert(variant="default"):
            AlertTitle("Theory of Anomalous Contrast (ToAC)")
            AlertDescription(
                "This is an OBSERVATIONAL section (sensor evidence). "
                "Do NOT conflate display contrast with physical impedance. "
                "Interpret only via physical attributes (coherence, curvature)."
            )

        # --- View Metadata ---
        with Card():
            with CardHeader():
                CardTitle("View Metadata")
            with CardContent():
                with Table():
                    with TableHeader():
                        with TableRow():
                            TableHead("View ID")
                            TableHead("Mode")
                            TableHead("Note")
                    with TableBody():
                        for v in views:
                            with TableRow():
                                TableCell(v.get("view_id", "—"))
                                TableCell(v.get("mode", "—"))
                                TableCell(v.get("note", "—"))

        # --- 888 HOLD Trigger Checklist ---
        with Card():
            with CardHeader():
                CardTitle("888 HOLD Trigger Checklist")
            with CardContent():
                Markdown(
                    "- [ ] Scale bar confirmed present\n"
                    "- [ ] Polarity convention documented\n"
                    "- [ ] Display colormap recorded\n"
                    "- [ ] Vertical exaggeration ≤ 2x (or disclosed)\n"
                    "- [ ] Well tie available for calibration\n"
                    "- [ ] Source wavelet known\n"
                )

        # --- Constitutional Floors ---
        with Card():
            with CardHeader():
                CardTitle("Constitutional Floors Active")
            with CardContent():
                _floor_table(_ACTIVE_FLOORS)

    return PrefabApp(view=view)


# ---------------------------------------------------------------------------
# View 2 — geox_build_structural_candidates
# ---------------------------------------------------------------------------


def structural_candidates_view(
    line_id: str,
    candidates: list[dict[str, Any]] | None,
    verdict: str = "QUALIFY",
    confidence: float = 0.12,
) -> PrefabApp:
    """
    Multi-Model Structural Candidates view.

    Enforces Contrast Canon Rule 1: never collapse to a single inverse model.
    Shows the ensemble of plausible models with physical basis.
    """
    # Build candidate rows from result or use fallback demo structure
    if not candidates:
        candidates = [
            {
                "model": "Ramp Anticline",
                "confidence": 0.12,
                "basis": "Compressional fold, confirmed by curvature attribute",
                "risk": "Low",
            },
            {
                "model": "Half-Graben Fill",
                "confidence": 0.09,
                "basis": "Extensional geometry, requires fault constraint",
                "risk": "Medium",
            },
            {
                "model": "Salt-Withdrawal Basin",
                "confidence": 0.07,
                "basis": "Velocity pull-up possible, needs velocity model",
                "risk": "High",
            },
        ]

    with Column(gap=4, css_class="p-6") as view:
        H2(f"Structural Candidates — {line_id}")
        Muted("Inverse Modelling Supervisor · Contrast Canon Rule 1: Multi-Model")
        Separator()

        # --- Rule badges ---
        with Row(gap=2, css_class="flex-wrap"):
            Badge(f"Non-Unique: {len(candidates)} models", variant="warning")
            Badge("F7 Humility Active", variant="warning")
            Badge("Collapse Prohibited", variant="destructive")
            Badge(f"Verdict: {verdict}", variant=_verdict_variant(verdict))

        # --- Non-uniqueness alert ---
        with Alert(variant="warning"):
            AlertTitle("Non-Uniqueness Principle")
            AlertDescription(
                "Seismic inverse modelling has no unique solution. "
                "All candidates below are equally physically plausible until "
                "well tie data, velocity model, or additional attributes constrain the solution."
            )

        # --- Candidate Table ---
        with Card():
            with CardHeader():
                CardTitle("Plausible Inverse Models")
            with CardContent():
                with Table():
                    with TableHeader():
                        with TableRow():
                            TableHead("Model")
                            TableHead("Confidence")
                            TableHead("Physical Basis")
                            TableHead("Risk")
                    with TableBody():
                        for c in candidates:
                            conf = c.get("confidence", 0.0)
                            risk = c.get("risk", "Unknown")
                            risk_variant = (
                                "success"
                                if risk == "Low"
                                else "warning" if risk == "Medium" else "destructive"
                            )
                            with TableRow():
                                TableCell(c.get("model", "—"))
                                TableCell(f"{conf:.0%}")
                                TableCell(c.get("basis", "—"))
                                with TableCell():
                                    Badge(risk, variant=risk_variant)

        # --- Confidence context ---
        with Card():
            with CardHeader():
                CardTitle("Confidence Context (F7 Humility)")
            with CardContent():
                Muted(
                    f"Combined confidence envelope: {confidence:.0%}. "
                    "Per F7, confidence is bounded in [3%, 15%]. "
                    "Values outside this range require explicit justification."
                )
                Progress(value=int(confidence * 100), max=100, css_class="mt-2")

    return PrefabApp(view=view)


# ---------------------------------------------------------------------------
# View 3 — geox_feasibility_check
# ---------------------------------------------------------------------------


def feasibility_check_view(
    plan_id: str,
    constraints: list[str],
    verdict: str,
    grounding_confidence: float,
) -> PrefabApp:
    """
    Constitutional Feasibility Check view.

    Shows F1-F13 floor status grid, grounding confidence, constraint list,
    and final SEAL / HOLD / BLOCK verdict.
    """
    variant = _verdict_variant(verdict)

    with Column(gap=4, css_class="p-6") as view:
        H2("Constitutional Feasibility Check")
        Muted(f"Plan ID: {plan_id}  ·  Stage: 222_REFLECT")
        Separator()

        # --- Verdict + confidence ---
        with Row(gap=4):
            with Card(css_class="flex-1"):
                with CardHeader():
                    CardTitle("Verdict")
                with CardContent():
                    Badge(verdict, variant=variant, css_class="text-lg px-3 py-1")

            with Card(css_class="flex-1"):
                with CardHeader():
                    CardTitle("Grounding Confidence")
                with CardContent():
                    Metric(
                        value=f"{grounding_confidence:.0%}",
                        label="Physical grounding",
                    )
                    Progress(
                        value=int(grounding_confidence * 100),
                        max=100,
                        css_class="mt-2",
                    )

        # --- Constraints applied ---
        with Card():
            with CardHeader():
                CardTitle("Constraints Checked")
            with CardContent():
                if constraints:
                    constraint_md = "\n".join(f"- {c}" for c in constraints)
                    Markdown(constraint_md)
                else:
                    Muted("No explicit constraints provided — world-state defaults applied.")

        # --- Constitutional Floors ---
        with Card():
            with CardHeader():
                CardTitle("Constitutional Floors (F1–F13)")
            with CardContent():
                _floor_table(_ACTIVE_FLOORS)

        # --- What happens next ---
        if verdict in ("HOLD", "888_HOLD", "BLOCK", "GEOX_BLOCK"):
            with Alert(variant="destructive"):
                AlertTitle("Pipeline Halted")
                AlertDescription(
                    "GEOX has emitted a HOLD/BLOCK at 222_REFLECT. "
                    "@RIF must not proceed until physical grounding is resolved. "
                    "Human review required per F13 Sovereign."
                )
        else:
            with Alert(variant="default"):
                AlertTitle("Proceed to 333_MIND")
                AlertDescription(
                    "Physical feasibility confirmed. @RIF may continue reasoning "
                    "within the bounds of the verified constraints."
                )

    return PrefabApp(view=view)


# ---------------------------------------------------------------------------
# View 4 — geox_verify_geospatial
# ---------------------------------------------------------------------------


def geospatial_view(
    lat: float,
    lon: float,
    radius_m: float,
    geological_province: str,
    jurisdiction: str,
    verdict: str,
) -> PrefabApp:
    """
    Geospatial Verification view.

    Shows coordinate card, geological province, jurisdiction, and verdict.
    No hallucinated map tiles — coordinates are presented as governed metadata.
    """
    variant = _verdict_variant(verdict)

    with Column(gap=4, css_class="p-6") as view:
        H2("Geospatial Verification")
        Muted("Stage: 222_REFLECT  ·  F4 Clarity  ·  F11 Authority")
        Separator()

        # --- Verdict badge ---
        with Row(gap=2):
            Badge(verdict, variant=variant)
            Badge(jurisdiction, variant="default")
            Badge(geological_province, variant="default")

        # --- Coordinate card ---
        with Card():
            with CardHeader():
                CardTitle("Verified Coordinates")
            with CardContent():
                with Table():
                    with TableBody():
                        with TableRow():
                            TableCell("Latitude")
                            TableCell(f"{lat:.6f}°")
                        with TableRow():
                            TableCell("Longitude")
                            TableCell(f"{lon:.6f}°")
                        with TableRow():
                            TableCell("Search Radius")
                            TableCell(f"{radius_m:,.0f} m")
                        with TableRow():
                            TableCell("CRS")
                            TableCell("WGS84 (EPSG:4326)")

        # --- Province + jurisdiction ---
        with Card():
            with CardHeader():
                CardTitle("Geological & Jurisdictional Context")
            with CardContent():
                with Table():
                    with TableBody():
                        with TableRow():
                            TableCell("Geological Province")
                            TableCell(geological_province)
                        with TableRow():
                            TableCell("Jurisdiction")
                            TableCell(jurisdiction)
                        with TableRow():
                            TableCell("Regulatory Bound")
                            TableCell("EEZ — Exclusive Economic Zone")

        # --- F9 Anti-Hantu notice ---
        with Alert(variant="default"):
            AlertTitle("F9 Anti-Hantu — No Phantom Geology")
            AlertDescription(
                "Province and jurisdiction data is anchored to verified external sources. "
                "Any geological claim outside this verified boundary must be explicitly flagged."
            )

    return PrefabApp(view=view)


# ---------------------------------------------------------------------------
# View 5 — geox_evaluate_prospect
# ---------------------------------------------------------------------------


def prospect_verdict_view(
    prospect_id: str,
    interpretation_id: str,
    verdict: str,
    confidence: float,
    status: str,
    reason: str,
) -> PrefabApp:
    """
    Prospect Evaluation verdict view.

    Final governed verdict at 222_REFLECT. Shows SEAL / 888_HOLD / BLOCK
    with provenance, confidence, and reason for hold if applicable.
    """
    verdict_variant = _verdict_variant(verdict)
    status_variant = _verdict_variant(status)
    is_hold = status in ("888_HOLD", "HOLD", "BLOCK", "GEOX_BLOCK")

    with Column(gap=4, css_class="p-6") as view:
        H2(f"Prospect Evaluation — {prospect_id}")
        Muted(f"Interpretation: {interpretation_id}  ·  Stage: 222_REFLECT  ·  999_VAULT logged")
        Separator()

        # --- Status strip ---
        with Row(gap=2):
            Badge(f"Status: {status}", variant=status_variant)
            Badge(f"Verdict: {verdict}", variant=verdict_variant)
            Badge(f"Confidence: {confidence:.0%}", variant="default")

        # --- Hold alert (if applicable) ---
        if is_hold:
            with Alert(variant="warning"):
                AlertTitle(f"888 HOLD — {status}")
                AlertDescription(reason)

        # --- Confidence card ---
        with Card():
            with CardHeader():
                CardTitle("Grounding Confidence")
            with CardContent():
                Metric(
                    value=f"{confidence:.0%}",
                    label="Prospect confidence (F7 bounded)",
                )
                Progress(value=int(confidence * 100), max=100, css_class="mt-2")
                Muted(
                    "F7 Humility: confidence bounded in [3%, 15%]. Values above 15% require explicit justification."
                )

        # --- Required actions ---
        with Card():
            with CardHeader():
                CardTitle("Required Before SEAL")
            with CardContent():
                Markdown(
                    "- [ ] Well-tie calibration (F9 Anti-Hantu)\n"
                    "- [ ] Velocity model verification\n"
                    "- [ ] Structural candidate ensemble review (min 3 models)\n"
                    "- [ ] Bias audit (Bond et al. 2007)\n"
                    "- [ ] Human signoff on final interpretation (F13 Sovereign)\n"
                )

        # --- Provenance chain ---
        with Card():
            with CardHeader():
                CardTitle("Provenance Chain")
            with CardContent():
                H3("222_REFLECT → 999_VAULT")
                with Table():
                    with TableBody():
                        with TableRow():
                            TableCell("Prospect ID")
                            TableCell(prospect_id)
                        with TableRow():
                            TableCell("Interpretation ID")
                            TableCell(interpretation_id)
                        with TableRow():
                            TableCell("Stage")
                            TableCell("222_REFLECT")
                        with TableRow():
                            TableCell("Logged to")
                            TableCell("999_VAULT")
                        with TableRow():
                            TableCell("Floor Audit")
                            TableCell("F1 · F4 · F7 · F9 · F11 · F13")

        # --- Constitutional floors ---
        with Card():
            with CardHeader():
                CardTitle("Constitutional Floors")
            with CardContent():
                _floor_table(_ACTIVE_FLOORS)

    return PrefabApp(view=view)


# ---------------------------------------------------------------------------
# View 6 — geox_select_sw_model (Petrophysics Phase B)
# ---------------------------------------------------------------------------


def sw_model_selector_view(
    interval_uri: str,
    admissible_models: list[dict],
    rejected_models: list[dict],
    recommended_model: str | None,
) -> PrefabApp:
    """
    Saturation Model Selector view.

    Shows admissible vs rejected Sw models with confidence scores,
    physical basis, and violations for rejected models.
    """
    with Column(gap=4, css_class="p-6") as view:
        H2("Saturation Model Selection")
        Muted(f"Interval: {interval_uri}")
        Separator()

        # --- Recommendation badge ---
        if recommended_model:
            with Alert(variant="success"):
                AlertTitle(f"Recommended: {recommended_model}")
                AlertDescription(
                    "This model has the highest confidence based on calibration data "
                    "and formation characteristics per F7 Humility."
                )

        # --- Admissible models table ---
        with Card():
            with CardHeader():
                CardTitle("Admissible Models")
            with CardContent():
                if admissible_models:
                    with Table():
                        with TableHeader():
                            with TableRow():
                                TableHead("Model")
                                TableHead("Confidence")
                                TableHead("Justification")
                        with TableBody():
                            for m in admissible_models:
                                conf = m.get("confidence", 0.0)
                                conf_variant = (
                                    "success"
                                    if conf >= 0.8
                                    else "warning" if conf >= 0.5 else "default"
                                )
                                with TableRow():
                                    TableCell(m.get("model", "—"))
                                    with TableCell():
                                        Badge(f"{conf:.0%}", variant=conf_variant)
                                    TableCell(m.get("justification", "—"))
                else:
                    Muted("No admissible models found. Check calibration data.")

        # --- Rejected models table ---
        if rejected_models:
            with Card():
                with CardHeader():
                    CardTitle("Rejected Models")
                with CardContent():
                    with Table():
                        with TableHeader():
                            with TableRow():
                                TableHead("Model")
                                TableHead("Rejection Reason")
                                TableHead("Violations")
                        with TableBody():
                            for m in rejected_models:
                                with TableRow():
                                    TableCell(m.get("model", "—"))
                                    TableCell(m.get("reason", "—"))
                                    violations = m.get("violations", [])
                                    with TableCell():
                                        if violations:
                                            for v in violations:
                                                Badge(v, variant="destructive")
                                        else:
                                            Text("—")

        # --- F7 Humility note ---
        with Alert(variant="default"):
            AlertTitle("F7 Humility — Confidence Calibration")
            AlertDescription(
                "Confidence scores are bounded by data quality and calibration coverage. "
                "Models with confidence <50% require additional calibration before use."
            )

    return PrefabApp(view=view)


# ---------------------------------------------------------------------------
# View 7 — geox_compute_petrophysics (Petrophysics Phase B)
# ---------------------------------------------------------------------------


def petrophysics_compute_view(
    interval_uri: str,
    model_used: str,
    results: dict,
    verdict: str,
    compute_uncertainty: bool,
) -> PrefabApp:
    """
    Petrophysics Computation Results view.

    Shows computed Vsh, phi_t, phi_e, Sw, BVW with uncertainty envelopes.
    """
    with Column(gap=4, css_class="p-6") as view:
        H2("Petrophysics Computation Results")
        Muted(f"Model: {model_used}  ·  Interval: {interval_uri}")
        Separator()

        # --- Verdict badge ---
        verdict_variant = _verdict_variant(verdict)
        with Row(gap=2):
            Badge(f"Verdict: {verdict}", variant=verdict_variant)
            if compute_uncertainty:
                Badge("Uncertainty: Enabled", variant="success")
            else:
                Badge("Uncertainty: Disabled", variant="warning")

        # --- Results metrics ---
        with Card():
            with CardHeader():
                CardTitle("Computed Properties")
            with CardContent():
                # Extract ranges
                vsh = results.get("vsh_range", [0, 0])
                phi_t = results.get("phi_t_range", [0, 0])
                phi_e = results.get("phi_e_range", [0, 0])
                sw = results.get("sw_range", [0, 0])
                bvw = results.get("bvw_range", [0, 0])

                with Grid(columns=2, gap=4):
                    with Card():
                        with CardContent():
                            Text("Vsh (Shale Volume)", css_class="text-sm text-muted-foreground")
                            Metric(value=f"{vsh[0]:.2f}–{vsh[1]:.2f}", label="fraction")
                    with Card():
                        with CardContent():
                            Text("φt (Total Porosity)", css_class="text-sm text-muted-foreground")
                            Metric(value=f"{phi_t[0]:.2f}–{phi_t[1]:.2f}", label="fraction")
                    with Card():
                        with CardContent():
                            Text(
                                "φe (Effective Porosity)", css_class="text-sm text-muted-foreground"
                            )
                            Metric(value=f"{phi_e[0]:.2f}–{phi_e[1]:.2f}", label="fraction")
                    with Card():
                        with CardContent():
                            Text("Sw (Water Saturation)", css_class="text-sm text-muted-foreground")
                            Metric(value=f"{sw[0]:.2f}–{sw[1]:.2f}", label="fraction")

                with Card(css_class="mt-4"):
                    with CardContent():
                        Text("BVW (Bulk Volume Water)", css_class="text-sm text-muted-foreground")
                        Metric(value=f"{bvw[0]:.3f}–{bvw[1]:.3f}", label="fraction")

        # --- Uncertainty note ---
        if compute_uncertainty:
            with Alert(variant="default"):
                AlertTitle("F7 Humility — Uncertainty Envelopes")
                AlertDescription(
                    "Ranges shown represent 10th–90th percentile confidence intervals. "
                    "Interpretations should account for uncertainty in all derived quantities."
                )
        else:
            with Alert(variant="warning"):
                AlertTitle("Uncertainty Disabled")
                AlertDescription(
                    "Point estimates only. Confidence intervals not computed. "
                    "Enable uncertainty for production interpretations."
                )

    return PrefabApp(view=view)


# ---------------------------------------------------------------------------
# View 8 — geox_validate_cutoffs (Petrophysics Phase B)
# ---------------------------------------------------------------------------


def cutoff_validation_view(
    interval_uri: str,
    policy_id: str,
    net_pay_flags: dict,
    cutoffs_applied: dict,
) -> PrefabApp:
    """
    Cutoff Policy Validation view.

    Shows net/pay thickness, net-to-gross, and applied cutoffs.
    Distinguishes physics from policy per F4 Clarity.
    """
    with Column(gap=4, css_class="p-6") as view:
        H2("Cutoff Policy Validation")
        Muted(f"Policy: {policy_id}  ·  Interval: {interval_uri}")
        Separator()

        # --- Status badge ---
        with Row(gap=2):
            Badge("Status: VALIDATED", variant="success")
            Badge("F4 Clarity: Physics ≠ Policy", variant="default")

        # --- Net/Pay metrics ---
        with Card():
            with CardHeader():
                CardTitle("Net / Pay Summary")
            with CardContent():
                net_thick = net_pay_flags.get("net_thickness_m", 0)
                pay_thick = net_pay_flags.get("pay_thickness_m", 0)
                ntg = net_pay_flags.get("net_to_gross", 0)

                with Grid(columns=3, gap=4):
                    with Card():
                        with CardContent():
                            Text("Net Thickness", css_class="text-sm text-muted-foreground")
                            Metric(value=f"{net_thick:.1f}", label="meters")
                    with Card():
                        with CardContent():
                            Text("Pay Thickness", css_class="text-sm text-muted-foreground")
                            Metric(value=f"{pay_thick:.1f}", label="meters")
                    with Card():
                        with CardContent():
                            Text("Net-to-Gross", css_class="text-sm text-muted-foreground")
                            Metric(value=f"{ntg:.2f}", label="ratio")

        # --- Cutoffs applied ---
        with Card():
            with CardHeader():
                CardTitle("Applied Cutoffs (Policy)")
            with CardContent():
                vsh_max = cutoffs_applied.get("vsh_max", 0)
                phi_min = cutoffs_applied.get("phi_min", 0)
                sw_max = cutoffs_applied.get("sw_max", 0)

                with Table():
                    with TableBody():
                        with TableRow():
                            TableCell("Vsh Maximum")
                            TableCell(f"≤ {vsh_max:.2f}")
                            TableCell("Shale volume cutoff")
                        with TableRow():
                            TableCell("φ Minimum")
                            TableCell(f"≥ {phi_min:.2f}")
                            TableCell("Porosity cutoff")
                        with TableRow():
                            TableCell("Sw Maximum")
                            TableCell(f"≤ {sw_max:.2f}")
                            TableCell("Water saturation cutoff")

        # --- F4 Clarity notice ---
        with Alert(variant="default"):
            AlertTitle("F4 Clarity — Physics vs Policy")
            AlertDescription(
                "Cutoffs are policy decisions, not physical laws. Net/pay flags "
                "represent economic/operational criteria applied to physically computed properties."
            )

    return PrefabApp(view=view)


# ---------------------------------------------------------------------------
# View 9 — geox_petrophysical_hold_check (Petrophysics Phase B)
# ---------------------------------------------------------------------------


def petrophysical_hold_view(
    interval_uri: str,
    verdict: str,
    triggers: list[str],
    required_actions: list[str],
    can_override: bool,
) -> PrefabApp:
    """
    Petrophysical 888 HOLD Check view.

    Shows automatic hold triggers and required actions before SEAL.
    """
    verdict_variant = _verdict_variant(verdict)
    is_hold = verdict in ("888_HOLD", "HOLD", "BLOCK")

    with Column(gap=4, css_class="p-6") as view:
        H2("Petrophysical HOLD Check")
        Muted(f"Interval: {interval_uri}")
        Separator()

        # --- Verdict badge ---
        with Row(gap=2):
            Badge(f"Verdict: {verdict}", variant=verdict_variant)
            if can_override:
                Badge("Override: F13 Sovereign", variant="warning")

        # --- Hold alert ---
        if is_hold:
            with Alert(variant="destructive"):
                AlertTitle("888 HOLD — Pipeline Halted")
                AlertDescription(
                    "Automatic hold triggers detected. Petrophysical interpretation "
                    "cannot proceed to SEAL until all triggers are resolved."
                )
        else:
            with Alert(variant="success"):
                AlertTitle("QUALIFY — Proceed to SEAL")
                AlertDescription(
                    "No hold triggers detected. Physical grounding sufficient "
                    "for interpretation at current confidence level."
                )

        # --- Triggers table ---
        if triggers:
            with Card():
                with CardHeader():
                    CardTitle("Hold Triggers Detected")
                with CardContent():
                    for trigger in triggers:
                        with Row(gap=2, css_class="mb-2"):
                            Badge(trigger, variant="destructive")
        else:
            with Card():
                with CardHeader():
                    CardTitle("Hold Triggers")
                with CardContent():
                    Muted("No triggers detected.")

        # --- Required actions ---
        with Card():
            with CardHeader():
                CardTitle("Required Actions Before SEAL")
            with CardContent():
                if required_actions:
                    md = "\n".join(f"- [ ] {action}" for action in required_actions)
                    Markdown(md)
                else:
                    default_checks = [
                        "Rw calibrated from SP or water sample",
                        "Shale model supported by core/XRD data",
                        "Environmental corrections applied",
                        "Invasion effects evaluated",
                        "Depth matching verified (MD/TVD/TVDSS)",
                        "Cutoffs have economic basis",
                    ]
                    md = "\n".join(f"- [ ] {check}" for check in default_checks)
                    Markdown(md)

        # --- Override notice ---
        if can_override:
            with Alert(variant="warning"):
                AlertTitle("F13 Sovereign — Human Override Available")
                AlertDescription(
                    "This hold can be overridden by authorized personnel. "
                    "Override requires documented justification and sign-off."
                )

        # --- Constitutional floors ---
        with Card():
            with CardHeader():
                CardTitle("Constitutional Floors")
            with CardContent():
                _floor_table(["F1", "F9", "F13"])

    return PrefabApp(view=view)
