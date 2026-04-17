"""
arifOS Federation — 66 Cognitive Primitives
============================================
6 axes × 11 dimensions = 66 irreducible agents

Implementation: FastMCP with strict I/O contracts
Philosophy: Mathematically orthogonal. No overlapping authority.

Usage:
    from agents_66 import create_agents_mcp

    mcp = FastMCP("arifOS-66")
    agents = create_agents_mcp(mcp)
    mcp.run()
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict
from dataclasses import dataclass
from enum import Enum

from fastmcp import FastMCP
from pydantic import BaseModel, Field

import os
import sys
import inspect
from pathlib import Path
from .memory_engine import MemoryEngine

# Add arifOS root to path for core imports
sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.shared.governed_tool import governed_tool

# Global Memory Engine instance
memory_engine = MemoryEngine(
    postgres_url=os.getenv("ARIFOS_VAULT_URL", os.getenv("DATABASE_URL")),
    qdrant_url=os.getenv("QDRANT_URL", "http://qdrant:6333"),
    ollama_url=os.getenv("OLLAMA_EMBEDDING_URL", "http://A-FORGE-ollama:11434"),
    embedding_model=os.getenv("EMBEDDING_MODEL", "bge-m3"),
)

# =============================================================================
# AXIS DEFINITIONS
# =============================================================================


class Axis(str, Enum):
    PERCEPTION = "P"
    TRANSFORMATION = "T"
    VALUATION = "V"
    GOVERNANCE = "G"
    EXECUTION = "E"
    META = "M"


class AgentTag(str, Enum):
    PUBLIC = "public"
    SCAFFOLD = "scaffold"
    INTERNAL = "internal"
    PERCEPTION = "perception"
    TRANSFORMATION = "transformation"
    VALUATION = "valuation"
    GOVERNANCE = "governance"
    EXECUTION = "execution"
    META = "meta"


# =============================================================================
# I/O CONTRACTS (TypedDict for each agent family)
# =============================================================================


# Perception Contracts (P01-P11)
class P01_WELLStateInput(TypedDict):
    pass


class P01_WELLStateOutput(TypedDict):
    score: float
    floors: dict[str, str]
    dimensions: dict[str, Any]


class P02_WELLReadinessInput(TypedDict):
    pass


class P02_WELLReadinessOutput(TypedDict):
    score: float
    floor_status: dict[str, str]
    verdict: str


class P03_WELLFloorScannerInput(TypedDict):
    pass


class P03_WELLFloorScannerOutput(TypedDict):
    per_floor: dict[str, dict[str, str]]
    overall_verdict: str
    bandwidth_recommendation: str


class P04_MacroSnapshotInput(TypedDict):
    geography: str


class P04_MacroSnapshotOutput(TypedDict):
    macro: dict[str, Any]
    energy: dict[str, Any]
    carbon: dict[str, Any]


class P05_SeriesFetcherInput(TypedDict):
    source: str
    series_id: str


class P05_SeriesFetcherOutput(TypedDict):
    series: list[Any]
    metadata: dict[str, Any]


class P06_VintageFetcherInput(TypedDict):
    series_id: str
    vintage_date: str


class P06_VintageFetcherOutput(TypedDict):
    series: list[Any]
    vintage: str


class P07_SourceReconcilerInput(TypedDict):
    geography: str


class P07_SourceReconcilerOutput(TypedDict):
    divergences: list[dict[str, Any]]


class P08_IngestHealthInput(TypedDict):
    pass


class P08_IngestHealthOutput(TypedDict):
    latency_ms: float
    cache_age: int
    completeness: float
    stale_flags: list[str]


class P09_GeospatialVerifierInput(TypedDict):
    query: str


class P09_GeospatialVerifierOutput(TypedDict):
    grounded: bool
    evidence: list[str]


class P10_SpatialContextExtractorInput(TypedDict):
    bounds: dict[str, float]


class P10_SpatialContextExtractorOutput(TypedDict):
    context_summary: dict[str, Any]


class P11_VaultLedgerReaderInput(TypedDict):
    filters: dict[str, Any] | None


class P11_VaultLedgerReaderOutput(TypedDict):
    seal_card: dict[str, Any]
    ledger_rows: list[dict[str, Any]]


# Transformation Contracts (T01-T11)
class T01_PetrophysicsInput(TypedDict):
    well_id: str
    logs: list[dict[str, Any]]


class T01_PetrophysicsOutput(TypedDict):
    volumes: dict[str, float]
    saturations: dict[str, float]
    porosity: dict[str, float]


class T02_StratigraphicCorrelatorInput(TypedDict):
    wells: list[str]
    section_id: str


class T02_StratigraphicCorrelatorOutput(TypedDict):
    correlation_map: dict[str, Any]


class T03_SeismicHorizonPickerInput(TypedDict):
    volume_id: str
    mode: Literal["auto", "manual"]


class T03_SeismicHorizonPickerOutput(TypedDict):
    horizons: list[dict[str, Any]]


class T04_GeometryBuilderInput(TypedDict):
    horizons: list[dict[str, Any]]


class T04_GeometryBuilderOutput(TypedDict):
    geometries: dict[str, Any]


class T05_AttributeAuditInput(TypedDict):
    scene_id: str


class T05_AttributeAuditOutput(TypedDict):
    permeability_proxy: dict[str, float]
    audit: dict[str, Any]


class T06_TimingVerificationInput(TypedDict):
    trap_id: str
    charge_id: str


class T06_TimingVerificationOutput(TypedDict):
    timing_result: dict[str, Any]


class T07_MonteCarloInput(TypedDict):
    portfolio: dict[str, Any]
    iterations: int


class T07_MonteCarloOutput(TypedDict):
    distribution: dict[str, Any]
    confidence_intervals: dict[str, tuple[float, float]]


class T08_IRRCalculatorInput(TypedDict):
    cashflows: list[float]


class T08_IRRCalculatorOutput(TypedDict):
    irr: float
    mirr: float


class T09_GrowthRunwayInput(TypedDict):
    cashflows: list[float]
    burn_rate: float


class T09_GrowthRunwayOutput(TypedDict):
    cagr: float
    runway_months: int


class T10_EntropyCashflowInput(TypedDict):
    cashflows: list[float]


class T10_EntropyCashflowOutput(TypedDict):
    entropy_score: float
    multiple_IRRs: bool


class T11_EconomicAuditInput(TypedDict):
    proposal: dict[str, Any]


class T11_EconomicAuditOutput(TypedDict):
    audit_result: dict[str, Any]


# Valuation Contracts (V01-V11)
class V01_NPVInput(TypedDict):
    cashflows: list[float]
    discount_rate: float


class V01_NPVOutput(TypedDict):
    npv: float


class V02_ProfitabilityIndexInput(TypedDict):
    investment: dict[str, Any]


class V02_ProfitabilityIndexOutput(TypedDict):
    pi: float


class V03_EMVRiskInput(TypedDict):
    outcomes: list[float]
    probabilities: list[float]


class V03_EMVRiskOutput(TypedDict):
    emv: float
    distribution: dict[str, Any]


class V04_DSCREvaluatorInput(TypedDict):
    net_operating_income: float
    debt_service: float


class V04_DSCREvaluatorOutput(TypedDict):
    dscr: float


class V05_PaybackEvaluatorInput(TypedDict):
    cashflows: list[float]


class V05_PaybackEvaluatorOutput(TypedDict):
    payback_period: float


class V06_NetWorthStateInput(TypedDict):
    assets: list[dict[str, float]]
    liabilities: list[dict[str, float]]


class V06_NetWorthStateOutput(TypedDict):
    networth: float


class V07_CashflowFlowInput(TypedDict):
    inflows: list[float]
    outflows: list[float]


class V07_CashflowFlowOutput(TypedDict):
    liquidity_ratio: float


class V08_PersonalDecisionInput(TypedDict):
    alternatives: list[dict[str, Any]]
    constraints: dict[str, Any]


class V08_PersonalDecisionOutput(TypedDict):
    ranked_list: list[dict[str, Any]]


class V09_AgentBudgetInput(TypedDict):
    tasks: list[dict[str, Any]]
    resources: dict[str, Any]


class V09_AgentBudgetOutput(TypedDict):
    optimal_sequence: list[str]


class V10_CivilizationSustainabilityInput(TypedDict):
    current_state: dict[str, Any]


class V10_CivilizationSustainabilityOutput(TypedDict):
    sustainability_score: float
    path: list[str]


class V11_AllocationScoreInput(TypedDict):
    proposal: dict[str, Any]


class V11_AllocationScoreOutput(TypedDict):
    score: float
    verdict: str


# Governance Contracts (G01-G11)
class G01_SessionInitInput(TypedDict):
    intent: str
    mode: Literal["init", "probe", "state", "status"]


class G01_SessionInitOutput(TypedDict):
    session_id: str
    epoch: int
    alignment: str


class G02_KernelRouterInput(TypedDict):
    task: dict[str, Any]
    risk_level: Literal["low", "medium", "high", "critical"]


class G02_KernelRouterOutput(TypedDict):
    lane: str
    target_agent: str


class G03_ConstitutionalMindInput(TypedDict):
    prompt: str
    mode: Literal["reason", "sequential", "step", "branch", "merge"]


class G03_ConstitutionalMindOutput(TypedDict):
    reasoning_packet: dict[str, Any]
    audit_packet: dict[str, Any]


class G04_EthicalHeartInput(TypedDict):
    candidate_action: dict[str, Any]
    context: dict[str, Any]


class G04_EthicalHeartOutput(TypedDict):
    ethical_assessment: dict[str, Any]


class G05_FinalJudgeInput(TypedDict):
    candidate_action: dict[str, Any]


class G05_FinalJudgeOutput(TypedDict):
    verdict: Literal["SEAL", "PARTIAL", "VOID", "HOLD"]
    floor_results: dict[str, Any]
    w3_scores: dict[str, float]


class G07_WealthFloorCheckerInput(TypedDict):
    proposal: dict[str, Any]


class G07_WealthFloorCheckerOutput(TypedDict):
    floor_results: dict[str, Any]


class G08_WELLFloorAuthorityInput(TypedDict):
    pass


class G08_WELLFloorAuthorityOutput(TypedDict):
    per_floor: dict[str, dict[str, str]]
    overall_verdict: str


class G09_OrthogonalityGuardInput(TypedDict):
    tool_outputs: list[Any]
    model_traces: list[Any]


class G09_OrthogonalityGuardOutput(TypedDict):
    omega_ortho: float
    verdict: Literal["PASS", "HOLD", "VOID"]


class G10_PolicyAuditorInput(TypedDict):
    proposal: dict[str, Any]
    policy: dict[str, Any]


class G10_PolicyAuditorOutput(TypedDict):
    audit_result: dict[str, Any]


class G11_HOLDAuthorityInput(TypedDict):
    action: dict[str, Any]


class G11_HOLDAuthorityOutput(TypedDict):
    requires_hold: bool
    reason: str


# Execution Contracts (E01-E11)
class E01_ForgeBridgeInput(TypedDict):
    plan: dict[str, Any]
    verdict: Literal["SEAL", "PARTIAL", "VOID", "HOLD"]


class E01_ForgeBridgeOutput(TypedDict):
    manifest: dict[str, Any]
    execution_receipt: dict[str, Any]


class E04_WealthTransactionRecorderInput(TypedDict):
    transaction: dict[str, Any]


class E04_WealthTransactionRecorderOutput(TypedDict):
    seal_id: str


class E05_PortfolioSnapshotRecorderInput(TypedDict):
    portfolio_data: dict[str, Any]


class E05_PortfolioSnapshotRecorderOutput(TypedDict):
    snapshot_id: str


class E06_WELLLogWriterInput(TypedDict):
    dimensions: dict[str, Any]


class E06_WELLLogWriterOutput(TypedDict):
    updated_state: dict[str, Any]


class E07_WELLPressureSignalInput(TypedDict):
    pressure_level: float
    source: str


class E07_WELLPressureSignalOutput(TypedDict):
    fatigue_delta: float


class E08_WELLAnchorInput(TypedDict):
    pass


class E08_WELLAnchorOutput(TypedDict):
    seal_id: str


class E09_SessionAnchorInput(TypedDict):
    session_id: str


class E09_SessionAnchorOutput(TypedDict):
    anchor_record: dict[str, Any]


class E10_VaultSealerInput(TypedDict):
    record: dict[str, Any]


class E10_VaultSealerOutput(TypedDict):
    merkle_hash: str
    seal_id: str


class E11_MemoryStoreInput(TypedDict):
    memory: dict[str, Any]
    tier: Literal["ephemeral", "working", "canon", "sacred", "quarantine"]


class E11_MemoryStoreOutput(TypedDict):
    store_result: dict[str, Any]


# E03 — Unified Memory (canonical interface, delegates to MemoryEngine)
# Single entry point for all memory operations: store / retrieve / forget
class E03_MemoryInput(TypedDict):
    operation: Literal["store", "retrieve", "forget"]
    memory: dict[str, Any]
    tier: Literal["ephemeral", "working", "canon", "sacred", "quarantine"]


class E03_MemoryOutput(TypedDict):
    result: dict[str, Any]


# Meta Contracts (M01-M11)
class M01_MemoryRetrieverInput(TypedDict):
    query: str
    tier: str | None


class M01_MemoryRetrieverOutput(TypedDict):
    memories: list[dict[str, Any]]


class M02_SkillDiscoveryInput(TypedDict):
    query: str
    domain: str | None


class M02_SkillDiscoveryOutput(TypedDict):
    skills: list[dict[str, Any]]


class M03_SkillMetadataInput(TypedDict):
    skill_id: str


class M03_SkillMetadataOutput(TypedDict):
    metadata: dict[str, Any]


class M04_SkillDependencyMapperInput(TypedDict):
    skill_id: str


class M04_SkillDependencyMapperOutput(TypedDict):
    dependencies: list[str]


class M05_RiskComputationInput(TypedDict):
    scenario: dict[str, Any]


class M05_RiskComputationOutput(TypedDict):
    toac_risk_score: float


class M06_ProspectJudgeRouterInput(TypedDict):
    prospect_id: str


class M06_ProspectJudgeRouterOutput(TypedDict):
    routing_result: dict[str, Any]


class M07_CrossEvidenceSynthesizerInput(TypedDict):
    scene_id: str


class M07_CrossEvidenceSynthesizerOutput(TypedDict):
    synthesized_scene: dict[str, Any]


class M08_CoordinationEquilibriumInput(TypedDict):
    agents: list[dict[str, Any]]
    resources: dict[str, Any]


class M08_CoordinationEquilibriumOutput(TypedDict):
    equilibrium_state: dict[str, Any]


class M09_GameTheorySolverInput(TypedDict):
    agents: list[dict[str, Any]]
    payoff_matrix: dict[str, Any]


class M09_GameTheorySolverOutput(TypedDict):
    solution: dict[str, Any]


class M10_CivilizationCoordinationInput(TypedDict):
    state: dict[str, Any]


class M10_CivilizationCoordinationOutput(TypedDict):
    coordination_plan: dict[str, Any]


class M11_MetabolicMonitorInput(TypedDict):
    pass


class M11_MetabolicMonitorOutput(TypedDict):
    floors: dict[str, dict[str, Any]]
    thermodynamics: dict[str, float]


# =============================================================================
# AGENT IMPLEMENTATIONS (Stub — replace with actual logic)
# =============================================================================


def _stub_perception(agent_id: str, input_data: Any) -> Any:
    """Stub for Perception agents — replace with actual implementation."""
    return {"status": "stub", "agent": agent_id, "input": input_data}


def _stub_transformation(agent_id: str, input_data: Any) -> Any:
    """Stub for Transformation agents — replace with actual implementation."""
    return {"status": "stub", "agent": agent_id, "input": input_data}


def _stub_valuation(agent_id: str, input_data: Any) -> Any:
    """Stub for Valuation agents — replace with actual implementation."""
    return {"status": "stub", "agent": agent_id, "input": input_data}


def _stub_governance(agent_id: str, input_data: Any) -> Any:
    """Stub for Governance agents — replace with actual implementation."""
    return {"status": "stub", "agent": agent_id, "input": input_data}


def _stub_execution(agent_id: str, input_data: Any) -> Any:
    """Stub for Execution agents — replace with actual implementation."""
    return {"status": "stub", "agent": agent_id, "input": input_data}


def _stub_meta(agent_id: str, input_data: Any) -> Any:
    """Stub for Meta agents — replace with actual implementation."""
    return {"status": "stub", "agent": agent_id, "input": input_data}


async def _handler_e11_memory_store(agent_id: str, input_data: Any) -> Any:
    """E11 Memory Store implementation."""
    memory = input_data.get("memory", {})
    tier = input_data.get("tier", "working")
    result = await memory_engine.execute("store", memory, tier)
    return {"store_result": result}


async def _handler_e03_memory(agent_id: str, input_data: Any) -> Any:
    """E03 Unified Memory — canonical store/retrieve/forget interface.

    Single entry point for all MemoryContract operations.
    Delegates to MemoryEngine which handles dual-write to Postgres + Qdrant.

    Supported operations:
      - store: Write memory to postgres first, Qdrant async (fire-and-forget)
      - retrieve: Semantic search via BGE-M3 embeddings + Qdrant
      - forget: Soft-delete in postgres, move to quarantine in Qdrant (888_HOLD for sacred)
    """
    operation = input_data.get("operation", "retrieve")
    memory = input_data.get("memory", {})
    tier = input_data.get("tier", "working")
    result = await memory_engine.execute(operation, memory, tier)
    return {"result": result}


async def _handler_m01_memory_retriever(agent_id: str, input_data: Any) -> Any:
    """M01 Memory Retriever implementation."""
    query = input_data.get("query", "")
    tier = input_data.get("tier")
    result = await memory_engine.execute("retrieve", {"query": query}, tier)
    return result


# =============================================================================
# TOOL REGISTRY
# =============================================================================

PERCEPTION_TOOLS: list[tuple[str, str, list[str], callable, type, type]] = [
    # (name, description, tags, handler, input_model, output_model)
    (
        "P01_well_state_reader",
        "Expose current WELL biological telemetry snapshot",
        ["perception", "public"],
        _stub_perception,
        P01_WELLStateInput,
        P01_WELLStateOutput,
    ),
    (
        "P02_well_readiness_reflector",
        "Reflect biological readiness verdict for arifOS JUDGE",
        ["perception", "public"],
        _stub_perception,
        P02_WELLReadinessInput,
        P02_WELLReadinessOutput,
    ),
    (
        "P03_well_floor_scanner",
        "Scan W-Floor status across all dimensions",
        ["perception", "public"],
        _stub_perception,
        P03_WELLFloorScannerInput,
        P03_WELLFloorScannerOutput,
    ),
    (
        "P04_macro_snapshot_fetcher",
        "Fetch cross-source macro/energy/carbon snapshot for geography",
        ["perception", "public"],
        _stub_perception,
        P04_MacroSnapshotInput,
        P04_MacroSnapshotOutput,
    ),
    (
        "P05_series_fetcher",
        "Fetch live data series from open public source",
        ["perception", "public"],
        _stub_perception,
        P05_SeriesFetcherInput,
        P05_SeriesFetcherOutput,
    ),
    (
        "P06_vintage_fetcher",
        "Fetch specific vintage of series (FRED/ALFRED)",
        ["perception", "public"],
        _stub_perception,
        P06_VintageFetcherInput,
        P06_VintageFetcherOutput,
    ),
    (
        "P07_source_reconciler",
        "Cross-source divergence detection for geography",
        ["perception", "public"],
        _stub_perception,
        P07_SourceReconcilerInput,
        P07_SourceReconcilerOutput,
    ),
    (
        "P08_ingest_health_monitor",
        "Return bus health: latency, cache age, field completeness, stale flags",
        ["perception", "public"],
        _stub_perception,
        P08_IngestHealthInput,
        P08_IngestHealthOutput,
    ),
    (
        "P09_geospatial_verifier",
        "Ground query in physical reality via 8-stage constitutional sensing",
        ["perception", "public"],
        _stub_perception,
        P09_GeospatialVerifierInput,
        P09_GeospatialVerifierOutput,
    ),
    (
        "P10_spatial_context_extractor",
        "Extract spatial context within bounds",
        ["perception", "public"],
        _stub_perception,
        P10_SpatialContextExtractorInput,
        P10_SpatialContextExtractorOutput,
    ),
    (
        "P11_vault_ledger_reader",
        "Read VAULT999 ledger, build current BLS seal card",
        ["perception", "public"],
        _stub_perception,
        P11_VaultLedgerReaderInput,
        P11_VaultLedgerReaderOutput,
    ),
]

TRANSFORMATION_TOOLS: list[tuple[str, str, list[str], callable, type, type]] = [
    (
        "T01_petrophysics_engine",
        "Execute physics-grounded petrophysical calculations",
        ["transformation", "public"],
        _stub_transformation,
        T01_PetrophysicsInput,
        T01_PetrophysicsOutput,
    ),
    (
        "T02_stratigraphic_correlator",
        "Correlate stratigraphic units across multiple wells",
        ["transformation", "public"],
        _stub_transformation,
        T02_StratigraphicCorrelatorInput,
        T02_StratigraphicCorrelatorOutput,
    ),
    (
        "T03_seismic_horizon_picker",
        "Automatically or manually pick horizons within 3D volume",
        ["transformation", "public"],
        _stub_transformation,
        T03_SeismicHorizonPickerInput,
        T03_SeismicHorizonPickerOutput,
    ),
    (
        "T04_geometry_builder",
        "Build architectural geometries from interpreted horizons",
        ["transformation", "public"],
        _stub_transformation,
        T04_GeometryBuilderInput,
        T04_GeometryBuilderOutput,
    ),
    (
        "T05_attribute_audit_engine",
        "Compute Kozeny-Carman permeability proxy and transform-chain audit",
        ["transformation", "public"],
        _stub_transformation,
        T05_AttributeAuditInput,
        T05_AttributeAuditOutput,
    ),
    (
        "T06_timing_verification_engine",
        "Check temporal relationship between trap formation and charge",
        ["transformation", "public"],
        _stub_transformation,
        T06_TimingVerificationInput,
        T06_TimingVerificationOutput,
    ),
    (
        "T07_monte_carlo_simulator",
        "Stochastic forecast with probability-weighted outcomes",
        ["transformation", "public"],
        _stub_transformation,
        T07_MonteCarloInput,
        T07_MonteCarloOutput,
    ),
    (
        "T08_irr_mirr_calculator",
        "Compute Internal Rate of Return and Modified IRR",
        ["transformation", "public"],
        _stub_transformation,
        T08_IRRCalculatorInput,
        T08_IRRCalculatorOutput,
    ),
    (
        "T09_growth_runway_calculator",
        "Compute compound growth rate and runway",
        ["transformation", "public"],
        _stub_transformation,
        T09_GrowthRunwayInput,
        T09_GrowthRunwayOutput,
    ),
    (
        "T10_entropy_cashflow_auditor",
        "Audit project cash flows for noise and multiple IRRs",
        ["transformation", "public"],
        _stub_transformation,
        T10_EntropyCashflowInput,
        T10_EntropyCashflowOutput,
    ),
    (
        "T11_economic_audit_calculator",
        "Perform constitutional economic audit",
        ["transformation", "public"],
        _stub_transformation,
        T11_EconomicAuditInput,
        T11_EconomicAuditOutput,
    ),
]

VALUATION_TOOLS: list[tuple[str, str, list[str], callable, type, type]] = [
    (
        "V01_npv_evaluator",
        "Compute Net Present Value",
        ["valuation", "public"],
        _stub_valuation,
        V01_NPVInput,
        V01_NPVOutput,
    ),
    (
        "V02_profitability_index",
        "Compute Profitability Index (concentration)",
        ["valuation", "public"],
        _stub_valuation,
        V02_ProfitabilityIndexInput,
        V02_ProfitabilityIndexOutput,
    ),
    (
        "V03_emv_risk_evaluator",
        "Compute Expected Monetary Value (probability density)",
        ["valuation", "public"],
        _stub_valuation,
        V03_EMVRiskInput,
        V03_EMVRiskOutput,
    ),
    (
        "V04_dscr_evaluator",
        "Compute Debt Service Coverage Ratio",
        ["valuation", "public"],
        _stub_valuation,
        V04_DSCREvaluatorInput,
        V04_DSCREvaluatorOutput,
    ),
    (
        "V05_payback_evaluator",
        "Compute Payback Period (recovery velocity)",
        ["valuation", "public"],
        _stub_valuation,
        V05_PaybackEvaluatorInput,
        V05_PaybackEvaluatorOutput,
    ),
    (
        "V06_networth_state_evaluator",
        "Compute portfolio balance sheet (accumulated mass)",
        ["valuation", "public"],
        _stub_valuation,
        V06_NetWorthStateInput,
        V06_NetWorthStateOutput,
    ),
    (
        "V07_cashflow_flow_evaluator",
        "Compute metabolic liquidity",
        ["valuation", "public"],
        _stub_valuation,
        V07_CashflowFlowInput,
        V07_CashflowFlowOutput,
    ),
    (
        "V08_personal_decision_ranker",
        "Rank personal alternatives under constraints",
        ["valuation", "public"],
        _stub_valuation,
        V08_PersonalDecisionInput,
        V08_PersonalDecisionOutput,
    ),
    (
        "V09_agent_budget_optimizer",
        "Optimal action sequence for AI agent under resource constraints",
        ["valuation", "public"],
        _stub_valuation,
        V09_AgentBudgetInput,
        V09_AgentBudgetOutput,
    ),
    (
        "V10_civilization_sustainability_allocator",
        "Long-term civilization sustainability path",
        ["valuation", "public"],
        _stub_valuation,
        V10_CivilizationSustainabilityInput,
        V10_CivilizationSustainabilityOutput,
    ),
    (
        "V11_allocation_score_kernel",
        "Final Sovereign Allocation Verdict",
        ["valuation", "public"],
        _stub_valuation,
        V11_AllocationScoreInput,
        V11_AllocationScoreOutput,
    ),
]

GOVERNANCE_TOOLS: list[tuple[str, str, list[str], callable, type, type]] = [
    (
        "G01_session_initializer",
        "Initialize constitutional session with identity binding",
        ["governance", "public"],
        _stub_governance,
        G01_SessionInitInput,
        G01_SessionInitOutput,
    ),
    (
        "G02_kernel_router",
        "Route request to correct metabolic lane based on risk and task type",
        ["governance", "public"],
        _stub_governance,
        G02_KernelRouterInput,
        G02_KernelRouterOutput,
    ),
    (
        "G03_constitutional_mind",
        "Structured reasoning with typed cognitive pipeline",
        ["governance", "public"],
        _stub_governance,
        G03_ConstitutionalMindInput,
        G03_ConstitutionalMindOutput,
    ),
    (
        "G04_ethical_heart",
        "Red-team proposal: simulate consequences, evaluate F5/F6/F9",
        ["governance", "public"],
        _stub_governance,
        G04_EthicalHeartInput,
        G04_EthicalHeartOutput,
    ),
    (
        "G05_final_judge",
        "Final constitutional verdict: SEAL, PARTIAL, VOID, HOLD",
        ["governance", "public"],
        _stub_governance,
        G05_FinalJudgeInput,
        G05_FinalJudgeOutput,
    ),
    (
        "G07_wealth_floor_checker",
        "Evaluate F1-F13 constitutional floors for wealth proposal",
        ["governance", "public"],
        _stub_governance,
        G07_WealthFloorCheckerInput,
        G07_WealthFloorCheckerOutput,
    ),
    (
        "G08_well_floor_authority",
        "Check WELL floor status against all W-Floors",
        ["governance", "public"],
        _stub_governance,
        G08_WELLFloorAuthorityInput,
        G08_WELLFloorAuthorityOutput,
    ),
    (
        "G09_orthogonality_guard",
        "Enforce Ω_ortho >= 0.95 across tool outputs and model traces",
        ["governance", "public"],
        _stub_governance,
        G09_OrthogonalityGuardInput,
        G09_OrthogonalityGuardOutput,
    ),
    (
        "G10_policy_auditor",
        "Audit allocation proposal against configurable policy constraints",
        ["governance", "public"],
        _stub_governance,
        G10_PolicyAuditorInput,
        G10_PolicyAuditorOutput,
    ),
    (
        "G11_hold_authority",
        "Check if action requires 888_HOLD human approval",
        ["governance", "public"],
        _stub_governance,
        G11_HOLDAuthorityInput,
        G11_HOLDAuthorityOutput,
    ),
]

EXECUTION_TOOLS: list[tuple[str, str, list[str], callable, type, type]] = [
    (
        "E01_forge_bridge",
        "Delegated Execution Bridge — validates JUDGE SEAL, constructs manifest",
        ["execution", "public"],
        _stub_execution,
        E01_ForgeBridgeInput,
        E01_ForgeBridgeOutput,
    ),
    (
        "E04_wealth_transaction_recorder",
        "Record financial transaction to VAULT999",
        ["execution", "public"],
        _stub_execution,
        E04_WealthTransactionRecorderInput,
        E04_WealthTransactionRecorderOutput,
    ),
    (
        "E05_portfolio_snapshot_recorder",
        "Snapshot tool computation result to VAULT999",
        ["execution", "public"],
        _stub_execution,
        E05_PortfolioSnapshotRecorderInput,
        E05_PortfolioSnapshotRecorderOutput,
    ),
    (
        "E06_well_log_writer",
        "Log biological telemetry update for operator Arif",
        ["execution", "public"],
        _stub_execution,
        E06_WELLLogWriterInput,
        E06_WELLLogWriterOutput,
    ),
    (
        "E07_well_pressure_signal",
        "Signal cognitive pressure from external source",
        ["execution", "public"],
        _stub_execution,
        E07_WELLPressureSignalInput,
        E07_WELLPressureSignalOutput,
    ),
    (
        "E08_well_anchor",
        "Anchor current WELL state to arifOS VAULT999",
        ["execution", "public"],
        _stub_execution,
        E08_WELLAnchorInput,
        E08_WELLAnchorOutput,
    ),
    (
        "E09_session_anchor",
        "Anchor session to VAULT999 with identity binding",
        ["execution", "public"],
        _stub_execution,
        E09_SessionAnchorInput,
        E09_SessionAnchorOutput,
    ),
    (
        "E10_vault_sealer",
        "Append immutable verdict record to Merkle-hashed ledger",
        ["execution", "public"],
        _stub_execution,
        E10_VaultSealerInput,
        E10_VaultSealerOutput,
    ),
    (
        "E03_memory",
        "Unified memory: store/retrieve/forget via MemoryContract (BGE-M3 + Qdrant + Postgres dual-write)",
        ["execution", "public"],
        _handler_e03_memory,
        E03_MemoryInput,
        E03_MemoryOutput,
    ),
    (
        "E11_memory_store",
        "Store memory in MemoryContract (5-tier governed)",
        ["execution", "public"],
        _handler_e11_memory_store,
        E11_MemoryStoreInput,
        E11_MemoryStoreOutput,
    ),
]

META_TOOLS: list[tuple[str, str, list[str], callable, type, type]] = [
    (
        "M01_memory_retriever",
        "Query memories from MemoryContract across tiers",
        ["meta", "public"],
        _handler_m01_memory_retriever,
        M01_MemoryRetrieverInput,
        M01_MemoryRetrieverOutput,
    ),
    (
        "M02_skill_discovery_agent",
        "Search available skills by keyword/domain/substrate",
        ["meta", "public"],
        _stub_meta,
        M02_SkillDiscoveryInput,
        M02_SkillDiscoveryOutput,
    ),
    (
        "M03_skill_metadata_agent",
        "Get detailed metadata for specific skill",
        ["meta", "public"],
        _stub_meta,
        M03_SkillMetadataInput,
        M03_SkillMetadataOutput,
    ),
    (
        "M04_skill_dependency_mapper",
        "Map skill dependencies",
        ["meta", "public"],
        _stub_meta,
        M04_SkillDependencyMapperInput,
        M04_SkillDependencyMapperOutput,
    ),
    (
        "M05_risk_computation_toac",
        "Calculate Theory of Anomalous Contrast (ToAC) risk score",
        ["meta", "public"],
        _stub_meta,
        M05_RiskComputationInput,
        M05_RiskComputationOutput,
    ),
    (
        "M06_prospect_judge_router",
        "Route prospect evaluation through arifOS for VAULT999 sealing",
        ["meta", "public"],
        _stub_meta,
        M06_ProspectJudgeRouterInput,
        M06_ProspectJudgeRouterOutput,
    ),
    (
        "M07_cross_evidence_synthesizer",
        "Synthesize causal scene for 888_JUDGE from spatial elements",
        ["meta", "public"],
        _stub_meta,
        M07_CrossEvidenceSynthesizerInput,
        M07_CrossEvidenceSynthesizerOutput,
    ),
    (
        "M08_coordination_equilibrium_solver",
        "Multi-agent resource coordination and equilibrium analysis",
        ["meta", "public"],
        _stub_meta,
        M08_CoordinationEquilibriumInput,
        M08_CoordinationEquilibriumOutput,
    ),
    (
        "M09_game_theory_solver",
        "Multi-agent allocation via LP welfare, Shapley/core, Nash",
        ["meta", "public"],
        _stub_meta,
        M09_GameTheorySolverInput,
        M09_GameTheorySolverOutput,
    ),
    (
        "M10_civilization_coordination_analyzer",
        "Analyze long-term civilization sustainability coordination",
        ["meta", "public"],
        _stub_meta,
        M10_CivilizationCoordinationInput,
        M10_CivilizationCoordinationOutput,
    ),
    (
        "M11_metabolic_monitor",
        "Real-time dashboard: F1-F13 + ΔS + Peace² + Ω₀",
        ["meta", "public"],
        _stub_meta,
        M11_MetabolicMonitorInput,
        M11_MetabolicMonitorOutput,
    ),
]

ALL_TOOL_FAMILIES = [
    PERCEPTION_TOOLS,
    TRANSFORMATION_TOOLS,
    VALUATION_TOOLS,
    GOVERNANCE_TOOLS,
    EXECUTION_TOOLS,
    META_TOOLS,
]

ALL_TOOLS = (
    PERCEPTION_TOOLS
    + TRANSFORMATION_TOOLS
    + VALUATION_TOOLS
    + GOVERNANCE_TOOLS
    + EXECUTION_TOOLS
    + META_TOOLS
)


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def create_agents_mcp(mcp: FastMCP | None = None, name: str = "arifOS-66") -> FastMCP:
    """
    Create FastMCP server with all 66 cognitive primitives.

    Usage:
        mcp = create_agents_mcp()
        mcp.run()

    Or with existing FastMCP:
        mcp = FastMCP("my-server")
        create_agents_mcp(mcp)
    """
    if mcp is None:
        mcp = FastMCP(name=name)

    for tool_family in ALL_TOOL_FAMILIES:
        for tool_name, description, tags, handler, input_model, output_model in tool_family:
            _register_tool(mcp, tool_name, description, tags, handler, input_model, output_model)

    return mcp


def _register_tool(
    mcp: FastMCP,
    name: str,
    description: str,
    tags: list[str],
    handler: callable,
    input_model: type,
    output_model: type,
) -> None:
    """Register a single tool with FastMCP."""
    tags_set = set(tags)

    @governed_tool
    async def governed_wrapped_handler(**kwargs):
        if inspect.iscoroutinefunction(handler):
            return await handler(name, kwargs)
        return handler(name, kwargs)

    # In FastMCP 3.x, we should use the decorator or set the name explicitly
    mcp.tool(name=name, description=description, tags=tags_set)(governed_wrapped_handler)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    mcp = create_agents_mcp()
    mcp.run()
