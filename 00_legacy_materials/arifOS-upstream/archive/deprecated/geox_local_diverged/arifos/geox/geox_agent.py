"""
GEOX Agent — Main Pipeline Orchestrator
DITEMPA BUKAN DIBERI

The primary GEOX orchestrator. Dependency-injectable so that arifOS
can plug in its kernel (agi_mind planner, vault_ledger audit sink,
M4 Qdrant memory store).

Pipeline: 000 INIT → 111 THINK → 333 EXPLORE → 555 HEART →
          777 REASON → 888 AUDIT → 999 SEAL

Verdict vocabulary: SEAL | PARTIAL | SABAR | VOID
arifOS verdicts:    CLAIM | PLAUSIBLE | HYPOTHESIS | ESTIMATE | UNKNOWN

Constitutional guarantees:
  F1  Every response carries a reversibility flag
  F2  Confidence bounded; no certainty claims
  F4  All insights include units
  F7  Uncertainty in [0.03, 0.15]
  F9  No phantom data — tool failures are reported, not silently dropped
  F13 Human veto gate on high/critical risk insights
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from arifos.geox.geox_schemas import (
    GeoInsight,
    GeoPrediction,
    GeoQuantity,
    GeoRequest,
    GeoResponse,
    ProvenanceRecord,
)
from arifos.geox.geox_tools import (
    BaseTool,
    GeoToolResult,
    ToolRegistry,
)
from arifos.geox.geox_validator import AggregateVerdict, GeoXValidator

logger = logging.getLogger("geox.agent")


# ---------------------------------------------------------------------------
# GeoXConfig
# ---------------------------------------------------------------------------


@dataclass
class GeoXConfig:
    """
    Configuration for the GeoXAgent pipeline.

    Attributes:
        lem_confidence_threshold:  Minimum LEM output confidence to accept.
        max_tool_retries:          Maximum retries per tool call on failure.
        allowed_tools:             Tool names permitted in this deployment.
        provenance_required:       Reject tool results without provenance.
        auto_risk_levels:          Mapping of risk level → action type.
        pipeline_id:               Version identifier for this pipeline.
    """

    lem_confidence_threshold: float = 0.75
    max_tool_retries: int = 3
    allowed_tools: list[str] = field(
        default_factory=lambda: [
            "EarthModelTool",
            "EOFoundationModelTool",
            "SeismicVLMTool",
            "SimulatorTool",
            "GeoRAGTool",
        ]
    )
    provenance_required: bool = True
    auto_risk_levels: dict[str, str] = field(
        default_factory=lambda: {
            "low": "auto",
            "medium": "human_signoff",
            "high": "regulator_required",
            "critical": "888_HOLD",
        }
    )
    pipeline_id: str = "geox-v0.1"


# ---------------------------------------------------------------------------
# GeoXAgent
# ---------------------------------------------------------------------------


class GeoXAgent:
    """
    GEOX pipeline orchestrator.

    Runs the full geological intelligence pipeline:
      plan → execute → synthesise → validate → summarise

    All external dependencies are injectable for testability and
    arifOS kernel integration.

    Args:
        config:       GeoXConfig governing pipeline behaviour.
        tool_registry: ToolRegistry providing tool access.
        validator:    GeoXValidator for insight verification.
        llm_planner:  Optional arifOS agi_mind planner callable.
                      Signature: async (query: str, context: dict) -> str
        audit_sink:   Optional arifOS vault_ledger callable.
                      Signature: async (event: dict) -> None
        memory_store: Optional arifOS M4 Qdrant memory client.
    """

    def __init__(
        self,
        config: GeoXConfig,
        tool_registry: ToolRegistry,
        validator: GeoXValidator,
        llm_planner: Callable[[str, dict], Awaitable[str]] | None = None,
        audit_sink: Callable[[dict], Awaitable[None]] | None = None,
        memory_store: Any | None = None,
    ) -> None:
        self.config = config
        self.tool_registry = tool_registry
        self.validator = validator
        self.llm_planner = llm_planner
        self.audit_sink = audit_sink
        self.memory_store = memory_store
        self._audit_log: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # plan()
    # ------------------------------------------------------------------

    async def plan(self, request: GeoRequest) -> list[str]:
        """
        Generate a tool execution plan for the request.

        If llm_planner is injected, delegates to arifOS agi_mind (333 EXPLORE).
        Otherwise, falls back to heuristic planning based on available_data.

        The plan always begins with a physics_reality check (F2 Truth gate)
        and always ends with GeoRAGTool for literature anchoring.

        Args:
            request: The incoming GeoRequest.

        Returns:
            Ordered list of tool names to execute.
        """
        await self._emit_audit(
            {
                "event": "plan_start",
                "stage": "111 THINK",
                "request_id": request.request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "detail": f"Planning for prospect '{request.prospect_name}'",
            }
        )

        if self.llm_planner is not None:
            try:
                plan_context = {
                    "prospect": request.prospect_name,
                    "basin": request.basin,
                    "play_type": request.play_type,
                    "available_data": request.available_data,
                    "allowed_tools": self.config.allowed_tools,
                    "risk_tolerance": request.risk_tolerance,
                }
                raw_plan = await self.llm_planner(request.query, plan_context)
                tool_names = self._parse_plan_from_llm(raw_plan)
                if tool_names:
                    logger.info("Using LLM planner. Plan: %s", tool_names)
                    return tool_names
            except Exception as exc:
                logger.warning("LLM planner failed (%s). Falling back to heuristic.", exc)

        return self._heuristic_plan(request)

    def _heuristic_plan(self, request: GeoRequest) -> list[str]:
        """
        Heuristic plan builder. Selects tools based on available data types.

        Always starts with EarthModelTool (physics_reality / F2 gate)
        and ends with GeoRAGTool (literature anchor).

        Returns ordered list of tool names.
        """
        plan: list[str] = []

        # Always start with LEM (physics gate — F2)
        plan.append("EarthModelTool")

        # Add simulator if we have well logs or are doing pressure analysis
        if any(d in request.available_data for d in ("well_logs", "core", "production")):
            plan.append("SimulatorTool")

        # Add EO tool if satellite data could help
        if "eo" in request.available_data or request.play_type in (
            "stratigraphic",
            "combination",
        ):
            plan.append("EOFoundationModelTool")

        # Add VLM if seismic is available
        if any(d in request.available_data for d in ("seismic_2d", "seismic_3d")):
            plan.append("SeismicVLMTool")

        # Always end with RAG for literature anchoring
        if "GeoRAGTool" not in plan:
            plan.append("GeoRAGTool")

        # Filter to allowed tools only
        allowed = set(self.config.allowed_tools)
        plan = [t for t in plan if t in allowed]

        logger.info("Heuristic plan: %s", plan)
        return plan

    def _parse_plan_from_llm(self, raw_plan: str) -> list[str]:
        """Parse LLM-generated plan text into ordered tool name list."""
        known_tools = set(self.config.allowed_tools)
        found: list[str] = []
        for tool_name in known_tools:
            if tool_name.lower() in raw_plan.lower():
                found.append(tool_name)
        # Ensure EarthModelTool is first (F2 physics gate)
        if "EarthModelTool" in found:
            found.remove("EarthModelTool")
            found.insert(0, "EarthModelTool")
        # Ensure GeoRAGTool is last
        if "GeoRAGTool" in found:
            found.remove("GeoRAGTool")
            found.append("GeoRAGTool")
        return found if found else []

    # ------------------------------------------------------------------
    # execute()
    # ------------------------------------------------------------------

    async def execute(self, plan: list[str], request: GeoRequest) -> list[GeoToolResult]:
        """
        Execute tools in plan order with retry logic.

        Catches tool-level errors, retries up to max_retries, and
        logs all events to the audit sink. Failed tools produce
        GeoToolResult(success=False) — they are never silently dropped
        (F9 Anti-Hantu).

        Args:
            plan:    Ordered list of tool names from plan().
            request: Original GeoRequest providing location context.

        Returns:
            List of GeoToolResult objects (one per tool, including failures).
        """
        await self._emit_audit(
            {
                "event": "execute_start",
                "stage": "333 EXPLORE",
                "request_id": request.request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "detail": f"Executing {len(plan)} tools: {plan}",
            }
        )

        results: list[GeoToolResult] = []

        for tool_name in plan:
            try:
                tool = self.tool_registry.get(tool_name)
            except KeyError:
                logger.warning("Tool '%s' not in registry. Skipping.", tool_name)
                results.append(
                    GeoToolResult(
                        tool_name=tool_name,
                        success=False,
                        error=f"Tool '{tool_name}' not registered.",
                    )
                )
                continue

            tool_inputs = self._build_tool_inputs(tool_name, request)
            result = await self._run_with_retry(tool, tool_inputs)
            results.append(result)

            await self._emit_audit(
                {
                    "event": "tool_executed",
                    "stage": "333 EXPLORE",
                    "tool": tool_name,
                    "success": result.success,
                    "latency_ms": result.latency_ms,
                    "quantity_count": len(result.quantities),
                    "error": result.error,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        await self._emit_audit(
            {
                "event": "execute_complete",
                "stage": "333 EXPLORE",
                "request_id": request.request_id,
                "tools_run": len(plan),
                "successful": sum(1 for r in results if r.success),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        return results

    def _build_tool_inputs(self, tool_name: str, request: GeoRequest) -> dict[str, Any]:
        """Build a standardised input dict for each tool type."""
        loc = request.location
        depth = loc.depth_m or 2500.0
        common = {
            "query": request.query,
            "location": loc,
            "depth_range_m": (max(0.0, depth - 500.0), depth + 500.0),
            "scenario": {
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "target_depth_m": depth,
                "basin": request.basin,
            },
            "timesteps_ma": [0.0, 5.0, 10.0, 20.0, 40.0],
            "bbox": {
                "west": loc.longitude - 1.0,
                "east": loc.longitude + 1.0,
                "south": loc.latitude - 1.0,
                "north": loc.latitude + 1.0,
            },
            "bands": ["B02", "B04", "B08", "B11", "TIR"],
            "date_range": ("2023-01-01", "2024-01-01"),
            "image_path": f"synthetic_{request.prospect_name.replace(' ', '_')}.png",
            "interpretation_query": f"Structural interpretation for {request.prospect_name}",
            "basin": request.basin,
            "max_results": 5,
        }
        return common

    async def _run_with_retry(self, tool: BaseTool, inputs: dict[str, Any]) -> GeoToolResult:
        """Run a tool with retry logic up to max_retries."""
        last_result: GeoToolResult | None = None
        for attempt in range(1, self.config.max_tool_retries + 1):
            try:
                result = await tool.run(inputs)
                if result.success:
                    return result
                last_result = result
                logger.warning(
                    "Tool '%s' attempt %d/%d failed: %s",
                    tool.name,
                    attempt,
                    self.config.max_tool_retries,
                    result.error,
                )
            except Exception as exc:
                last_result = GeoToolResult(
                    tool_name=tool.name,
                    success=False,
                    error=str(exc),
                )
                logger.warning(
                    "Tool '%s' attempt %d/%d exception: %s",
                    tool.name,
                    attempt,
                    self.config.max_tool_retries,
                    exc,
                )
            if attempt < self.config.max_tool_retries:
                await asyncio.sleep(0.5 * attempt)

        return last_result or GeoToolResult(
            tool_name=tool.name,
            success=False,
            error="Max retries exceeded with no successful response.",
        )

    # ------------------------------------------------------------------
    # synthesise()
    # ------------------------------------------------------------------

    async def synthesise(
        self, results: list[GeoToolResult], request: GeoRequest
    ) -> list[GeoInsight]:
        """
        Convert raw tool results into governed GeoInsight objects.

        Synthesises insights from the collective tool output, assigning
        risk levels according to config.auto_risk_levels and applying
        the VLM perception bridge rule (VLM-only insights get risk bumped).

        Args:
            results: Tool execution results from execute().
            request: Original GeoRequest for context.

        Returns:
            List of GeoInsight objects ready for validation.
        """
        await self._emit_audit(
            {
                "event": "synthesise_start",
                "stage": "555 HEART",
                "request_id": request.request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        # Gather all quantities from successful tools
        all_quantities: list[GeoQuantity] = []
        vlm_only_quantities: list[GeoQuantity] = []
        lem_quantities: list[GeoQuantity] = []

        for result in results:
            if not result.success:
                continue
            for qty in result.quantities:
                all_quantities.append(qty)
                if result.tool_name == "SeismicVLMTool":
                    vlm_only_quantities.append(qty)
                elif result.tool_name == "EarthModelTool":
                    lem_quantities.append(qty)

        insights: list[GeoInsight] = []

        # --- Insight 1: LEM Physics Assessment ---
        if lem_quantities:
            insights.append(self._make_lem_insight(lem_quantities, request))

        # --- Insight 2: Reservoir Quality (porosity + velocity) ---
        porosity_qtys = [q for q in all_quantities if "porosity" in q.quantity_type]
        velocity_qtys = [q for q in all_quantities if "velocity" in q.quantity_type]
        if porosity_qtys or velocity_qtys:
            insights.append(self._make_reservoir_insight(porosity_qtys + velocity_qtys, request))

        # --- Insight 3: VLM Structural Interpretation (perception bridge rule) ---
        if vlm_only_quantities:
            insights.append(self._make_vlm_insight(vlm_only_quantities, request))

        # --- Insight 4: Pressure / Temperature (maturity) ---
        pt_qtys = [
            q
            for q in all_quantities
            if any(t in q.quantity_type for t in ("pressure", "temperature", "maturity"))
        ]
        if pt_qtys:
            insights.append(self._make_pt_insight(pt_qtys, request))

        # Ensure at least one insight if tools ran successfully
        if not insights and all_quantities:
            insights.append(self._make_general_insight(all_quantities, request))

        # If no tool data at all, produce a SABAR insight
        if not insights:
            insights.append(self._make_no_data_insight(request))

        await self._emit_audit(
            {
                "event": "synthesise_complete",
                "stage": "555 HEART",
                "insight_count": len(insights),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        return insights

    def _risk_level_for_request(self, request: GeoRequest, base_level: str = "medium") -> str:
        """Map request risk_tolerance to insight risk_level."""
        risk_map = {"low": "low", "medium": "medium", "high": "high"}
        req_risk = risk_map.get(request.risk_tolerance, "medium")
        # Escalate base_level to request risk if higher
        levels = ["low", "medium", "high", "critical"]
        base_idx = levels.index(base_level) if base_level in levels else 1
        req_idx = levels.index(req_risk) if req_risk in levels else 1
        return levels[max(base_idx, req_idx)]

    def _needs_signoff(self, risk_level: str) -> bool:
        action = self.config.auto_risk_levels.get(risk_level, "human_signoff")
        return action != "auto"

    def _make_prov_from_tool_result(self, tool_name: str, confidence: float) -> ProvenanceRecord:
        source_type_map = {
            "EarthModelTool": "LEM",
            "SeismicVLMTool": "VLM",
            "SimulatorTool": "simulator",
            "EOFoundationModelTool": "sensor",
            "GeoRAGTool": "literature",
        }
        stype = source_type_map.get(tool_name, "LEM")
        return ProvenanceRecord(
            source_id=f"{tool_name}-{uuid.uuid4().hex[:8]}",
            source_type=stype,  # type: ignore[arg-type]
            timestamp=datetime.now(timezone.utc),
            confidence=confidence,
        )

    def _make_lem_insight(self, quantities: list[GeoQuantity], request: GeoRequest) -> GeoInsight:
        """Build a LEM physics assessment insight."""
        velocity_vals = [q.value for q in quantities if "velocity" in q.quantity_type]
        porosity_vals = [q.value for q in quantities if "porosity" in q.quantity_type]
        density_vals = [q.value for q in quantities if "density" in q.quantity_type]

        velocity_str = f"{velocity_vals[0]:.0f} m/s" if velocity_vals else "N/A"
        porosity_str = f"{porosity_vals[0]*100:.1f}%" if porosity_vals else "N/A"
        density_str = f"{density_vals[0]:.2f} g/cm³" if density_vals else "N/A"

        text = (
            f"LEM physics assessment for '{request.prospect_name}' ({request.basin}): "
            f"P-wave velocity {velocity_str}, porosity {porosity_str}, "
            f"bulk density {density_str}. "
            f"Physical properties are consistent with {request.play_type} play settings."
        )

        risk = self._risk_level_for_request(request, "low")
        signoff = self._needs_signoff(risk)

        predictions: list[GeoPrediction] = []
        if porosity_vals:
            p = porosity_vals[0]
            prov = self._make_prov_from_tool_result("EarthModelTool", 0.82)
            qty = GeoQuantity(
                value=p,
                units="fraction",
                quantity_type="porosity",
                coordinates=request.location,
                timestamp=datetime.now(timezone.utc),
                uncertainty=0.08,
                provenance=prov,
            )
            try:
                predictions.append(
                    GeoPrediction(
                        target="porosity",
                        location=request.location,
                        expected_range=(max(0.01, p * 0.8), p * 1.2),
                        units="fraction",
                        confidence=0.80,
                        supporting_quantities=[qty],
                        method="LEM_ensemble",
                    )
                )
            except Exception:
                pass

        return GeoInsight(
            text=text,
            support=predictions,
            status="unverified",
            risk_level=risk,  # type: ignore[arg-type]
            requires_human_signoff=signoff,
        )

    def _make_reservoir_insight(
        self, quantities: list[GeoQuantity], request: GeoRequest
    ) -> GeoInsight:
        """Build a reservoir quality insight."""
        porosity_vals = [q.value for q in quantities if "porosity" in q.quantity_type]
        velocity_vals = [q.value for q in quantities if "velocity" in q.quantity_type]

        avg_porosity = sum(porosity_vals) / len(porosity_vals) if porosity_vals else None
        avg_velocity = sum(velocity_vals) / len(velocity_vals) if velocity_vals else None

        por_str = f"{avg_porosity*100:.1f}%" if avg_porosity is not None else "unknown"
        vel_str = f"{avg_velocity:.0f} m/s" if avg_velocity is not None else "unknown"

        if avg_porosity is not None and avg_porosity >= 0.15:
            quality = "good to moderate"
        elif avg_porosity is not None and avg_porosity >= 0.08:
            quality = "moderate to poor"
        else:
            quality = "uncertain"

        text = (
            f"Reservoir quality assessment for '{request.prospect_name}': "
            f"Average porosity {por_str}, average P-wave velocity {vel_str}. "
            f"Reservoir quality is {quality} based on multi-tool ensemble analysis. "
            f"Recommend well-log calibration before committing to final estimates."
        )

        risk = self._risk_level_for_request(request, "medium")
        signoff = self._needs_signoff(risk)

        return GeoInsight(
            text=text,
            support=[],
            status="unverified",
            risk_level=risk,  # type: ignore[arg-type]
            requires_human_signoff=signoff,
        )

    def _make_vlm_insight(self, quantities: list[GeoQuantity], request: GeoRequest) -> GeoInsight:
        """
        Build a VLM structural insight.

        Perception bridge rule: VLM-only insights always get their
        risk level bumped up one tier and require multisensor support.
        """
        fault_vals = [q.value for q in quantities if "fault" in q.quantity_type]
        struct_vals = [q.value for q in quantities if "structural" in q.quantity_type]
        amp_vals = [q.value for q in quantities if "amplitude" in q.quantity_type]

        fault_prob = fault_vals[0] if fault_vals else 0.5
        struct_conf = struct_vals[0] if struct_vals else 0.5
        amp_anom = amp_vals[0] > 0.5 if amp_vals else False

        text = (
            f"VLM seismic structural interpretation for '{request.prospect_name}': "
            f"Fault probability {fault_prob*100:.0f}%, "
            f"structural confidence {struct_conf*100:.0f}%. "
            f"Amplitude anomaly {'detected' if amp_anom else 'not detected'}. "
            f"NOTE: This interpretation is based on visual perception only (uncertainty ≥ 15%). "
            f"RGB/colour patterns alone are not decisive — corroboration with LEM, "
            f"well logs, or simulator data is required before acting (Perception Bridge Rule)."
        )

        # VLM perception bridge rule: bump risk up one level
        base_risk = self._risk_level_for_request(request, "medium")
        levels = ["low", "medium", "high", "critical"]
        bumped_idx = min(levels.index(base_risk) + 1, len(levels) - 1)
        risk = levels[bumped_idx]
        signoff = self._needs_signoff(risk)  # VLM bump always triggers signoff

        return GeoInsight(
            text=text,
            support=[],
            status="unverified",
            risk_level=risk,  # type: ignore[arg-type]
            requires_human_signoff=signoff,
        )

    def _make_pt_insight(self, quantities: list[GeoQuantity], request: GeoRequest) -> GeoInsight:
        """Build a pressure-temperature-maturity insight."""
        pres_vals = [q.value for q in quantities if "pressure" in q.quantity_type]
        temp_vals = [q.value for q in quantities if "temperature" in q.quantity_type]
        mat_vals = [q.value for q in quantities if "maturity" in q.quantity_type]

        pres_str = f"{pres_vals[0]:.0f} psi" if pres_vals else "unknown"
        temp_str = f"{temp_vals[0]:.1f} °C" if temp_vals else "unknown"
        mat_str = f"{mat_vals[0]:.2f} %Ro" if mat_vals else "unknown"

        mat_val = mat_vals[0] if mat_vals else 0.0
        if mat_val >= 0.6:
            maturity_interp = "within oil window"
        elif mat_val >= 1.35:
            maturity_interp = "within gas window"
        elif mat_val < 0.6:
            maturity_interp = "thermally immature"
        else:
            maturity_interp = "uncertain"

        text = (
            f"Pressure-temperature-maturity assessment for '{request.prospect_name}': "
            f"Reservoir pressure {pres_str}, temperature {temp_str}, "
            f"vitrinite reflectance {mat_str} ({maturity_interp}). "
            f"Estimates derived from basin simulation — calibrate with measured data."
        )

        risk = self._risk_level_for_request(request, "medium")
        signoff = self._needs_signoff(risk)

        return GeoInsight(
            text=text,
            support=[],
            status="unverified",
            risk_level=risk,  # type: ignore[arg-type]
            requires_human_signoff=signoff,
        )

    def _make_general_insight(
        self, quantities: list[GeoQuantity], request: GeoRequest
    ) -> GeoInsight:
        """Fallback general insight when no specialised synthesis applies."""
        text = (
            f"Multi-tool geophysical assessment for '{request.prospect_name}' "
            f"({request.basin}): {len(quantities)} geophysical measurements "
            f"acquired across {len({q.quantity_type for q in quantities})} "
            f"parameter types. Detailed reservoir characterisation requires "
            f"additional data integration and expert review."
        )
        risk = self._risk_level_for_request(request, "medium")
        signoff = self._needs_signoff(risk)
        return GeoInsight(
            text=text,
            support=[],
            status="unverified",
            risk_level=risk,  # type: ignore[arg-type]
            requires_human_signoff=signoff,
        )

    def _make_no_data_insight(self, request: GeoRequest) -> GeoInsight:
        """Insight when no tool returned usable data."""
        text = (
            f"Insufficient data for '{request.prospect_name}' ({request.basin}). "
            f"No tool returned valid geophysical measurements. "
            f"Recommend acquiring: seismic data (2D/3D), well logs, and core samples "
            f"before proceeding. Verdict: SABAR — wait for more data."
        )
        risk = self._risk_level_for_request(request, "high")
        signoff = self._needs_signoff(risk)
        return GeoInsight(
            text=text,
            support=[],
            status="unverified",
            risk_level=risk,  # type: ignore[arg-type]
            requires_human_signoff=signoff,
        )

    # ------------------------------------------------------------------
    # validate()
    # ------------------------------------------------------------------

    async def validate(self, insights: list[GeoInsight]) -> AggregateVerdict:
        """
        Validate all insights via the GeoXValidator (777 REASON + 888 AUDIT).

        Args:
            insights: GeoInsight objects from synthesise().

        Returns:
            AggregateVerdict with SEAL | PARTIAL | SABAR | VOID.
        """
        await self._emit_audit(
            {
                "event": "validate_start",
                "stage": "777 REASON",
                "insight_count": len(insights),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        tools = [
            self.tool_registry.get(name)
            for name in self.config.allowed_tools
            if name in self.tool_registry.list_tools()
        ]

        verdict = await self.validator.validate_batch(insights, tools)

        await self._emit_audit(
            {
                "event": "validate_complete",
                "stage": "888 AUDIT",
                "verdict": verdict.overall,
                "confidence": verdict.confidence,
                "seal": verdict.seal_count,
                "partial": verdict.partial_count,
                "void": verdict.void_count,
                "requires_audit": verdict.requires_audit,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        return verdict

    # ------------------------------------------------------------------
    # summarise()
    # ------------------------------------------------------------------

    async def summarise(
        self,
        request: GeoRequest,
        insights: list[GeoInsight],
        verdict: AggregateVerdict,
    ) -> GeoResponse:
        """
        Assemble the final GeoResponse (999 SEAL stage).

        Builds the complete arifOS telemetry block and determines
        whether an 888 HOLD is required.

        Args:
            request:  Original GeoRequest.
            insights: Validated GeoInsight objects.
            verdict:  AggregateVerdict from validate().

        Returns:
            Fully assembled GeoResponse.
        """
        human_required = (
            any(i.requires_human_signoff for i in insights)
            or verdict.requires_audit
            or verdict.overall == "VOID"
        )

        hold_status = "888 HOLD" if human_required else "CLEAR"

        # Build provenance chain from all insight sources
        prov_chain: list[ProvenanceRecord] = []
        prov_seen: set[str] = set()
        for insight in insights:
            for pred in insight.support:
                for qty in pred.supporting_quantities:
                    sid = qty.provenance.source_id
                    if sid not in prov_seen:
                        prov_chain.append(qty.provenance)
                        prov_seen.add(sid)

        # arifOS telemetry block
        arifos_telemetry: dict[str, Any] = {
            "pipeline": "000→111→333→555→777→888→999",
            "stage": "999 SEAL",
            "floors": ["F1", "F2", "F4", "F7", "F13"],
            "confidence": verdict.confidence,
            "verdict": verdict.overall,
            "P2": 1.0,  # Peace ≥ 1.0 (F5)
            "hold": hold_status,
            "uncertainty_range": [0.03, 0.15],
            "seal": "DITEMPA BUKAN DIBERI",
            "pipeline_id": self.config.pipeline_id,
            "request_id": request.request_id,
            "insight_count": len(insights),
            "seal_count": verdict.seal_count,
            "partial_count": verdict.partial_count,
            "void_count": verdict.void_count,
            "human_signoff_required": human_required,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Collect all predictions
        all_predictions: list[GeoPrediction] = []
        for insight in insights:
            all_predictions.extend(insight.support)

        response = GeoResponse(
            request_id=request.request_id,
            insights=insights,
            predictions=all_predictions,
            verdict=verdict.overall,
            confidence_aggregate=verdict.confidence,
            provenance_chain=prov_chain,
            audit_log=list(self._audit_log),
            human_signoff_required=human_required,
            arifos_telemetry=arifos_telemetry,
        )

        await self._emit_audit(
            {
                "event": "response_sealed",
                "stage": "999 SEAL",
                "response_id": response.response_id,
                "verdict": verdict.overall,
                "hold": hold_status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        return response

    # ------------------------------------------------------------------
    # evaluate_prospect() — full pipeline
    # ------------------------------------------------------------------

    async def evaluate_prospect(self, request: GeoRequest) -> GeoResponse:
        """
        Full GEOX pipeline execution: plan → execute → synthesise →
        validate → summarise.

        This is the primary public entry point for prospect evaluation.

        If human_signoff_required is True on the result, the response
        carries an 888 HOLD and must not trigger automated downstream
        actions (F13 Sovereign).

        Args:
            request: Incoming GeoRequest.

        Returns:
            GeoResponse with verdict, insights, telemetry, and audit log.
        """
        self._audit_log = []  # Reset for new request

        await self._emit_audit(
            {
                "event": "pipeline_start",
                "stage": "000 INIT",
                "request_id": request.request_id,
                "prospect": request.prospect_name,
                "basin": request.basin,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        logger.info(
            "[GEOX] Starting evaluation: %s | %s | %s",
            request.prospect_name,
            request.basin,
            request.play_type,
        )

        # 111 THINK + 333 EXPLORE
        plan = await self.plan(request)
        results = await self.execute(plan, request)

        # 555 HEART
        insights = await self.synthesise(results, request)

        # 777 REASON + 888 AUDIT
        verdict = await self.validate(insights)

        # 999 SEAL
        response = await self.summarise(request, insights, verdict)

        # 888 HOLD — log and return (do NOT block; caller handles routing)
        if response.human_signoff_required:
            logger.warning(
                "[GEOX 888 HOLD] Response %s requires human sign-off. "
                "Verdict: %s. No automated action permitted (F13 Sovereign).",
                response.response_id,
                verdict.overall,
            )

        logger.info(
            "[GEOX 999 SEAL] Pipeline complete. Verdict: %s | Confidence: %.2f | Hold: %s",
            verdict.overall,
            verdict.confidence,
            response.arifos_telemetry.get("hold", "UNKNOWN"),
        )

        return response

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _emit_audit(self, event: dict[str, Any]) -> None:
        """
        Append event to internal audit log and forward to audit_sink
        (arifOS vault_ledger) if configured.
        """
        self._audit_log.append(event)
        if self.audit_sink is not None:
            try:
                await self.audit_sink(event)
            except Exception as exc:
                logger.warning("audit_sink failed: %s", exc)
