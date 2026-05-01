"""
GEOX Reporter — Audit Report Generator
DITEMPA BUKAN DIBERI

Generates three types of reports for GeoResponse objects:

  1. Markdown report — full technical report with tables, provenance,
     telemetry, floor compliance, and 888 HOLD notice.

  2. JSON audit — machine-readable dict matching arifOS vault_ledger format.

  3. Human brief — plain-language 3-paragraph summary for non-technical
     stakeholders.

All reports include verdict, confidence, and constitutional floor status.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from arifos.geox.geox_schemas import GeoRequest, GeoResponse


class GeoXReporter:
    """
    Generates audit and communication reports for GEOX pipeline outputs.

    Usage:
        reporter = GeoXReporter()
        md = reporter.generate_markdown_report(response, request)
        audit = reporter.generate_json_audit(response)
        brief = reporter.generate_human_brief(response)
    """

    # ------------------------------------------------------------------
    # generate_markdown_report()
    # ------------------------------------------------------------------

    def generate_markdown_report(
        self, response: GeoResponse, request: GeoRequest
    ) -> str:
        """
        Generate a full Markdown technical report for a GeoResponse.

        Sections:
          - Header / banner
          - Executive summary
          - arifOS Telemetry block
          - 888 HOLD notice (if applicable)
          - Insights table
          - Predictions table
          - Provenance chain
          - Constitutional floor compliance checklist
          - Audit log summary

        Args:
            response: GeoResponse from evaluate_prospect().
            request:  Original GeoRequest.

        Returns:
            Markdown string suitable for rendering in any Markdown viewer.
        """
        lines: list[str] = []
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # --- Header ---
        lines.append("# GEOX Geological Intelligence Report")
        lines.append("> **DITEMPA BUKAN DIBERI** — arifOS Geological Coprocessor v0.1.0")
        lines.append("")
        lines.append(f"**Generated:** {now}")
        lines.append(f"**Response ID:** `{response.response_id}`")
        lines.append(f"**Request ID:** `{response.request_id}`")
        lines.append("")

        # --- 888 HOLD Notice ---
        if response.human_signoff_required:
            lines.append("---")
            lines.append("## ⚠️ 888 HOLD — HUMAN SIGN-OFF REQUIRED")
            lines.append("")
            lines.append(
                "> This response contains one or more insights classified as **high** or "
                "**critical** risk, or contains contradicted evidence. "
                "**No automated action may be taken** on this prospect evaluation without "
                "explicit human approval (arifOS F13 Sovereign)."
            )
            lines.append("")
            lines.append("---")
            lines.append("")

        # --- Executive Summary ---
        lines.append("## Executive Summary")
        lines.append("")
        lines.append("| Field | Value |")
        lines.append("|-------|-------|")
        lines.append(f"| **Prospect** | {request.prospect_name} |")
        lines.append(f"| **Basin** | {request.basin} |")
        lines.append(f"| **Play Type** | {request.play_type} |")
        lines.append(f"| **Location** | Lat {request.location.latitude:.4f}, Lon {request.location.longitude:.4f} |")
        lines.append(f"| **Query** | {request.query[:120]}{'...' if len(request.query) > 120 else ''} |")
        lines.append(f"| **Available Data** | {', '.join(request.available_data) or 'None specified'} |")
        lines.append(f"| **Risk Tolerance** | {request.risk_tolerance} |")
        lines.append(f"| **Requester** | {request.requester_id} |")
        lines.append("")

        # --- Verdict Banner ---
        verdict_emoji = {
            "SEAL": "✅ SEAL",
            "PARTIAL": "🟡 PARTIAL",
            "SABAR": "⏳ SABAR",
            "VOID": "🚫 VOID",
        }
        v_label = verdict_emoji.get(response.verdict, response.verdict)
        lines.append(f"### Overall Verdict: {v_label}")
        lines.append("")
        lines.append(f"**Aggregate Confidence:** {response.confidence_aggregate:.1%}")
        lines.append("")
        lines.append(
            "| SEAL | PARTIAL | SABAR | VOID |\n"
            "|------|---------|-------|------|\n"
            "| supported insights | ambiguous insights | insufficient data | contradicted |"
        )
        lines.append("")

        # --- arifOS Telemetry Block ---
        lines.append("## arifOS Telemetry")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(response.arifos_telemetry, indent=2, default=str))
        lines.append("```")
        lines.append("")

        # --- Insights Table ---
        lines.append("## Geological Insights")
        lines.append("")
        if response.insights:
            lines.append("| # | Risk | Status | Signoff | Insight Text |")
            lines.append("|---|------|--------|---------|--------------|")
            for i, insight in enumerate(response.insights, 1):
                text_short = insight.text[:120].replace("|", "\\|")
                if len(insight.text) > 120:
                    text_short += "…"
                signoff_str = "**YES**" if insight.requires_human_signoff else "No"
                lines.append(
                    f"| {i} | {insight.risk_level.upper()} | {insight.status} "
                    f"| {signoff_str} | {text_short} |"
                )
            lines.append("")
            lines.append("### Full Insight Texts")
            lines.append("")
            for i, insight in enumerate(response.insights, 1):
                lines.append(f"#### Insight {i} — {insight.insight_id[:8]}")
                lines.append(f"**Risk:** {insight.risk_level.upper()} | **Status:** {insight.status}")
                lines.append("")
                lines.append(insight.text)
                lines.append("")
                # Floor verdicts
                if insight.floor_verdicts:
                    passing = [k for k, v in insight.floor_verdicts.items() if v]
                    failing = [k for k, v in insight.floor_verdicts.items() if not v]
                    lines.append(f"**Floors Passed:** {', '.join(passing) or 'None'}")
                    if failing:
                        lines.append(f"**Floors FAILED:** ⚠️ {', '.join(failing)}")
                lines.append("")
        else:
            lines.append("_No insights generated._")
            lines.append("")

        # --- Predictions Table ---
        lines.append("## Predictions")
        lines.append("")
        if response.predictions:
            lines.append("| Target | Range | Units | Confidence | Method |")
            lines.append("|--------|-------|-------|------------|--------|")
            for pred in response.predictions:
                lo, hi = pred.expected_range
                lines.append(
                    f"| {pred.target} | {lo:.3g}–{hi:.3g} | {pred.units} "
                    f"| {pred.confidence:.0%} | {pred.method} |"
                )
            lines.append("")
        else:
            lines.append("_No testable predictions registered._")
            lines.append("")

        # --- Provenance Chain ---
        lines.append("## Provenance Chain")
        lines.append("")
        if response.provenance_chain:
            lines.append("| # | Source ID | Type | Confidence | Timestamp | Citation |")
            lines.append("|---|-----------|------|------------|-----------|----------|")
            for i, prov in enumerate(response.provenance_chain, 1):
                citation = (prov.citation or "—")[:60]
                lines.append(
                    f"| {i} | `{prov.source_id[:20]}` | {prov.source_type} "
                    f"| {prov.confidence:.0%} | {prov.timestamp.strftime('%Y-%m-%d %H:%M') if prov.timestamp else '—'} "
                    f"| {citation} |"
                )
            lines.append("")
        else:
            lines.append("_No provenance records in chain._")
            lines.append("")

        # --- Constitutional Floor Compliance ---
        lines.append("## Constitutional Floor Compliance Checklist")
        lines.append("")
        floor_descriptions = {
            "F1_amanah": "F1 Amanah/Reversibility — Traceability and reversible actions",
            "F2_truth": "F2 Truth ≥ 0.99 — No absolute certainty claims",
            "F4_clarity": "F4 Clarity — Units and labels present",
            "F7_humility": "F7 Humility — Uncertainty in [0.03, 0.15]",
            "F9_anti_hantu": "F9 Anti-Hantu — No phantom data",
            "F11_authority": "F11 Authority — Provenance mandatory",
            "F13_sovereign": "F13 Sovereign — Human veto on high-risk",
        }

        all_floor_checks: dict[str, list[bool]] = {k: [] for k in floor_descriptions}
        for insight in response.insights:
            for floor_id, passed in insight.floor_verdicts.items():
                if floor_id in all_floor_checks:
                    all_floor_checks[floor_id].append(passed)

        lines.append("| Floor | Description | Status |")
        lines.append("|-------|-------------|--------|")
        for floor_id, desc in floor_descriptions.items():
            votes = all_floor_checks.get(floor_id, [])
            if not votes:
                status = "⚪ N/A"
            elif all(votes):
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
            lines.append(f"| `{floor_id}` | {desc} | {status} |")
        lines.append("")

        # --- Audit Log Summary ---
        lines.append("## Audit Log Summary")
        lines.append("")
        if response.audit_log:
            lines.append(f"Total events: {len(response.audit_log)}")
            lines.append("")
            lines.append("| Stage | Event | Timestamp |")
            lines.append("|-------|-------|-----------|")
            for event in response.audit_log:
                stage = event.get("stage", "—")
                ev = event.get("event", "—")
                ts = event.get("timestamp", "—")
                lines.append(f"| {stage} | {ev} | {ts[:19] if isinstance(ts, str) else ts} |")
            lines.append("")
        else:
            lines.append("_No audit events recorded._")
            lines.append("")

        # --- Footer ---
        lines.append("---")
        self._add_macrostrat_attribution(lines, response.metadata)
        lines.append("")
        lines.append(
            "*This report was generated by GEOX v0.1.0 — arifOS Geological Coprocessor. "
            "All geological interpretations are model-assisted estimates and require "
            "expert human review before operational use. "
            "DITEMPA BUKAN DIBERI.*"
        )

        return "\n".join(lines)

    def _add_macrostrat_attribution(self, report: list[str], metadata: dict[str, Any]) -> None:
        """Add Macrostrat attribution if it was used in the assessment."""
        if metadata.get("source") == "macrostrat.org":
            report.append("")
            report.append("*Geological data provided by Macrostrat (macrostrat.org) under CC-BY-4.0 license.*")
            report.append("*Citation: Peters et al. (2018) Macrostrat: a platform for geological data integration.*")

    # ------------------------------------------------------------------
    # generate_json_audit()
    # ------------------------------------------------------------------

    def generate_json_audit(self, response: GeoResponse) -> dict[str, Any]:
        """
        Generate a machine-readable audit dict matching the arifOS
        vault_ledger format.

        Structure mirrors vault_ledger event schema with GEOX-specific
        extensions.

        Args:
            response: GeoResponse to audit.

        Returns:
            dict suitable for vault_ledger.store() or JSON serialisation.
        """
        return {
            "vault_entry_type": "geox_pipeline_response",
            "version": "2.1",
            "response_id": response.response_id,
            "request_id": response.request_id,
            "timestamp": response.timestamp.isoformat() if response.timestamp else None,
            "verdict": response.verdict,
            "confidence_aggregate": response.confidence_aggregate,
            "human_signoff_required": response.human_signoff_required,
            "pipeline": "000→111→333→555→777→888→999",
            "seal": "DITEMPA BUKAN DIBERI",
            "arifos_telemetry": response.arifos_telemetry,
            "insights": [
                {
                    "insight_id": i.insight_id,
                    "text_preview": i.text[:200],
                    "status": i.status,
                    "risk_level": i.risk_level,
                    "requires_human_signoff": i.requires_human_signoff,
                    "floor_verdicts": i.floor_verdicts,
                    "prediction_count": len(i.support),
                }
                for i in response.insights
            ],
            "predictions": [
                {
                    "target": p.target,
                    "expected_range": list(p.expected_range),
                    "units": p.units,
                    "confidence": p.confidence,
                    "method": p.method,
                }
                for p in response.predictions
            ],
            "provenance_chain": [
                {
                    "source_id": prov.source_id,
                    "source_type": prov.source_type,
                    "confidence": prov.confidence,
                    "timestamp": prov.timestamp.isoformat() if prov.timestamp else None,
                    "checksum": prov.checksum,
                    "citation": prov.citation,
                    "floor_check": prov.floor_check,
                }
                for prov in response.provenance_chain
            ],
            "audit_log": response.audit_log,
            "floor_compliance": {
                "F1_amanah": self._aggregate_floor(response, "F1_amanah"),
                "F2_truth": self._aggregate_floor(response, "F2_truth"),
                "F4_clarity": self._aggregate_floor(response, "F4_clarity"),
                "F7_humility": self._aggregate_floor(response, "F7_humility"),
                "F9_anti_hantu": self._aggregate_floor(response, "F9_anti_hantu"),
                "F11_authority": self._aggregate_floor(response, "F11_authority"),
                "F13_sovereign": self._aggregate_floor(response, "F13_sovereign"),
            },
        }

    def _aggregate_floor(self, response: GeoResponse, floor_id: str) -> bool:
        """Return True if all insights pass the given floor check."""
        for insight in response.insights:
            if not insight.floor_verdicts.get(floor_id, True):
                return False
        return True

    # ------------------------------------------------------------------
    # generate_human_brief()
    # ------------------------------------------------------------------

    def generate_human_brief(self, response: GeoResponse) -> str:
        """
        Generate a plain-language 3-paragraph summary for non-technical
        stakeholders (e.g. management, regulators, partners).

        No technical jargon. Focus on: what was assessed, what was found,
        what to do next.

        Args:
            response: GeoResponse from evaluate_prospect().

        Returns:
            3-paragraph plain-language string.
        """
        telemetry = response.arifos_telemetry
        prospect = telemetry.get("prospect", "the evaluated prospect")
        verdict = response.verdict
        confidence = response.confidence_aggregate
        hold = telemetry.get("hold", "CLEAR")

        # Paragraph 1: What was assessed
        insight_count = len(response.insights)
        prediction_count = len(response.predictions)
        para1 = (
            f"Our geological intelligence system evaluated {prospect} using an automated "
            f"multi-tool analysis pipeline. The assessment incorporated data from earth "
            f"physics models, satellite imagery, geological literature, and basin simulation. "
            f"The analysis produced {insight_count} geological insight{'s' if insight_count != 1 else ''} "
            f"and {prediction_count} testable prediction{'s' if prediction_count != 1 else ''}."
        )

        # Paragraph 2: What was found
        verdict_descriptions = {
            "SEAL": (
                f"The results are strongly consistent across all data sources, "
                f"giving us high confidence (approximately {confidence:.0%}) in the findings. "
                f"The prospect shows favourable geological indicators based on currently available data."
            ),
            "PARTIAL": (
                f"The results are partially consistent, with some uncertainty remaining "
                f"(overall confidence approximately {confidence:.0%}). "
                f"Some geological indicators are supportive, while others require additional data "
                f"before a definitive assessment can be made."
            ),
            "SABAR": (
                f"Insufficient data is available to reach a confident conclusion at this time "
                f"(confidence approximately {confidence:.0%}). "
                f"The system recommends gathering additional information — such as seismic surveys, "
                f"well logs, or core samples — before proceeding."
            ),
            "VOID": (
                f"The analysis detected conflicting evidence across data sources "
                f"(confidence approximately {confidence:.0%}). "
                f"This means the current dataset contains internal contradictions that must be resolved. "
                f"No recommendation can be made until data quality issues are addressed."
            ),
        }
        para2 = verdict_descriptions.get(verdict, f"Overall verdict: {verdict}. Confidence: {confidence:.0%}.")

        # Paragraph 3: What to do next
        if hold == "888 HOLD" or response.human_signoff_required:
            para3 = (
                "Important: This assessment is on hold pending human expert review. "
                "One or more findings carry elevated risk and require sign-off from a "
                "qualified geoscientist or relevant authority before any operational decision "
                "or capital commitment is made. Please escalate this report to your technical "
                "lead or governance team immediately."
            )
        elif verdict == "SEAL":
            para3 = (
                "The system recommends proceeding to the next stage of prospect evaluation. "
                "While the automated assessment is favourable, all geological interpretations "
                "should be reviewed by a qualified geoscientist before any investment or "
                "drilling decision is finalised."
            )
        elif verdict == "PARTIAL":
            para3 = (
                "The system recommends targeted data acquisition to resolve the remaining "
                "uncertainties. A qualified geoscientist should review the full technical report "
                "and identify which additional data types would most reduce risk. "
                "Proceed cautiously until ambiguities are resolved."
            )
        elif verdict == "SABAR":
            para3 = (
                "The system recommends pausing this prospect evaluation until additional "
                "data is acquired. A geological data acquisition programme should be scoped "
                "and prioritised. Re-run the assessment once new data is available."
            )
        else:  # VOID
            para3 = (
                "The system recommends a data quality audit before proceeding. "
                "A qualified geoscientist should review the raw data sources to identify "
                "and resolve the conflicting evidence. Do not make any operational decisions "
                "based on this assessment until data consistency is confirmed."
            )

        return "\n\n".join([para1, para2, para3])
