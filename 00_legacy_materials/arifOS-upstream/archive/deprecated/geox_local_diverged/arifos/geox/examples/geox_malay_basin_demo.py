"""
GEOX Demo — Malay Basin Prospect Evaluation
DITEMPA BUKAN DIBERI

Full runnable demonstration of the GEOX geological intelligence pipeline
for a fictional "Blok Selatan" prospect in the Malay Basin.

This demo uses mock tools only — no proprietary PETRONAS data.
All geological values are entirely fictional but scientifically plausible.

What this demo shows:
  1. Building a GeoRequest for Blok Selatan
  2. Running GeoXAgent with mock tools (MockEarthNetTool + MockSeismicVLMTool)
  3. Full pipeline execution:
       000 INIT → 111 THINK → 333 EXPLORE → 555 HEART → 777 REASON → 888 AUDIT → 999 SEAL
  4. Printing GeoResponse with verdict and arifOS telemetry
  5. Printing the full Markdown audit report
  6. Printing the human-readable brief

Prospect details (fictional):
  Name:      Blok Selatan (fictional)
  Basin:     Malay Basin
  Play type: Structural (four-way dip closure, Miocene clastics)
  Location:  ~4.5°N, 103.7°E (central Malay Basin, offshore)
  Target:    Early Miocene sandstone reservoir, ~2500 m depth

Run:
  python examples/geox_malay_basin_demo.py

Requirements:
  pydantic>=2.0.0
  (No additional dependencies for mock mode)
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys

# ---------------------------------------------------------------------------
# Path setup — allow running directly from examples/ or from package root
# ---------------------------------------------------------------------------

# Add parent dirs to path so imports work without pip install
_demo_dir = os.path.dirname(os.path.abspath(__file__))
_pkg_root = os.path.dirname(os.path.dirname(_demo_dir))  # → arifos/
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from datetime import datetime, timezone

from arifos.geox.geox_agent import GeoXAgent, GeoXConfig
from arifos.geox.geox_memory import GeoMemoryStore
from arifos.geox.geox_reporter import GeoXReporter
from arifos.geox.geox_schemas import CoordinatePoint, GeoRequest
from arifos.geox.geox_tools import ToolRegistry
from arifos.geox.geox_validator import GeoXValidator

# Import mock tools
sys.path.insert(0, os.path.join(_demo_dir, "mock_tools"))
from mock_earthnet import MockEarthNetTool
from mock_vlm import MockSeismicVLMTool

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("geox.demo")


# ---------------------------------------------------------------------------
# Demo banner
# ---------------------------------------------------------------------------

BANNER = """
╔══════════════════════════════════════════════════════════════════════╗
║           GEOX — Geological Intelligence Coprocessor                 ║
║           arifOS Domain Coprocessor v0.1.0                           ║
║           DITEMPA BUKAN DIBERI                                        ║
╠══════════════════════════════════════════════════════════════════════╣
║  Demo: Blok Selatan Prospect Evaluation — Malay Basin (Fictional)    ║
║  Pipeline: 000→111→333→555→777→888→999                               ║
║  Verdict vocabulary: SEAL | PARTIAL | SABAR | VOID                   ║
╚══════════════════════════════════════════════════════════════════════╝
"""


# ---------------------------------------------------------------------------
# Build mock tool registry
# ---------------------------------------------------------------------------

def build_mock_registry() -> ToolRegistry:
    """
    Build a ToolRegistry using mock tools for the demo.

    Uses:
      - MockEarthNetTool   (replaces EarthModelTool in mock mode)
      - MockSeismicVLMTool (replaces SeismicVLMTool in mock mode)
      - Standard SimulatorTool, GeoRAGTool, EOFoundationModelTool from package
    """
    from geox.geox_tools import EOFoundationModelTool, GeoRAGTool, SimulatorTool

    registry = ToolRegistry()
    # Mock tools for LEM and VLM
    registry.register(MockEarthNetTool())
    registry.register(MockSeismicVLMTool())
    # Standard mock tools for simulator, EO, and RAG
    registry.register(SimulatorTool())
    registry.register(EOFoundationModelTool())
    registry.register(GeoRAGTool())
    return registry


# ---------------------------------------------------------------------------
# Build GeoXConfig for demo
# ---------------------------------------------------------------------------

def build_demo_config() -> GeoXConfig:
    """Build GeoXConfig for the demo, using mock tool names."""
    return GeoXConfig(
        lem_confidence_threshold=0.70,  # Slightly relaxed for demo
        max_tool_retries=2,
        allowed_tools=[
            "MockEarthNetTool",       # Mock LEM
            "MockSeismicVLMTool",     # Mock VLM
            "SimulatorTool",          # Standard mock basin simulator
            "EOFoundationModelTool",  # Standard mock EO
            "GeoRAGTool",             # Standard mock RAG
        ],
        provenance_required=True,
        auto_risk_levels={
            "low": "auto",
            "medium": "human_signoff",
            "high": "regulator_required",
            "critical": "888_HOLD",
        },
        pipeline_id="geox-v0.1-malay-basin-demo",
    )


# ---------------------------------------------------------------------------
# Build GeoRequest for Blok Selatan
# ---------------------------------------------------------------------------

def build_blok_selatan_request() -> GeoRequest:
    """
    Build a GeoRequest for the fictional Blok Selatan prospect.

    Blok Selatan is a fictional four-way dip closure in the Malay Basin,
    targeting Early Miocene fluvio-deltaic sandstone reservoirs at ~2500 m.
    It has 3D seismic, well log data from one offset well, and no core.
    """
    location = CoordinatePoint(
        latitude=4.5237,
        longitude=103.6892,
        depth_m=2500.0,  # Target depth: Early Miocene reservoir top
        crs="EPSG:4326",
    )

    return GeoRequest(
        query=(
            "Evaluate the hydrocarbon potential of the Blok Selatan four-way "
            "dip closure in the Malay Basin. Assess reservoir quality, "
            "structural integrity, trap security, and charge adequacy for "
            "an Early Miocene fluvio-deltaic sandstone target at approximately "
            "2500 m depth. What is the estimated net pay and HC column height?"
        ),
        prospect_name="Blok Selatan",
        location=location,
        basin="Malay Basin",
        play_type="structural",
        available_data=["seismic_3d", "well_logs"],
        risk_tolerance="medium",
        requester_id="DEMO-GEOLOGIST-001",
        timestamp=datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# Print helpers
# ---------------------------------------------------------------------------

def _section(title: str, width: int = 72) -> None:
    print(f"\n{'='*width}")
    print(f"  {title}")
    print(f"{'='*width}")


def _subsection(title: str) -> None:
    print(f"\n--- {title} ---")


# ---------------------------------------------------------------------------
# Main demo coroutine
# ---------------------------------------------------------------------------

async def run_demo() -> None:
    print(BANNER)

    # ---- Setup ----
    _section("SETUP — Initialising GEOX Components")

    registry = build_mock_registry()
    config = build_demo_config()
    validator = GeoXValidator()
    memory_store = GeoMemoryStore()
    reporter = GeoXReporter()

    print(f"  Tool registry: {registry.list_tools()}")
    print(f"  Pipeline ID:   {config.pipeline_id}")
    print(f"  Allowed tools: {config.allowed_tools}")

    # Health checks
    health = registry.health_check_all()
    print("\n  Tool health checks:")
    for tool_name, ok in health.items():
        status = "✓ READY" if ok else "✗ UNAVAILABLE"
        print(f"    {tool_name}: {status}")

    # Build agent (no LLM planner injected → heuristic mode)
    agent = GeoXAgent(
        config=config,
        tool_registry=registry,
        validator=validator,
        llm_planner=None,   # In production: inject arifOS agi_mind
        audit_sink=None,    # In production: inject arifOS vault_ledger
        memory_store=memory_store,
    )
    print("\n  GeoXAgent initialised (heuristic planner mode).")
    print("  [arifOS integration: inject llm_planner=agi_mind and audit_sink=vault_ledger]")

    # ---- Build Request ----
    _section("STEP 1: GeoRequest — Blok Selatan Prospect")

    request = build_blok_selatan_request()
    print(f"  Request ID:      {request.request_id}")
    print(f"  Prospect:        {request.prospect_name}")
    print(f"  Basin:           {request.basin}")
    print(f"  Play type:       {request.play_type}")
    print(f"  Location:        {request.location.latitude}°N, {request.location.longitude}°E")
    print(f"  Target depth:    {request.location.depth_m} m")
    print(f"  Available data:  {request.available_data}")
    print(f"  Risk tolerance:  {request.risk_tolerance}")
    print(f"\n  Query: {request.query[:200]}...")

    # ---- Run Pipeline ----
    _section("STEP 2: Running Full GEOX Pipeline (000→999)")
    print("  [This runs: plan → execute → synthesise → validate → summarise]")
    print()

    response = await agent.evaluate_prospect(request)

    # ---- Print Results ----
    _section("STEP 3: GeoResponse — Results")

    print(f"  Response ID:     {response.response_id}")
    print(f"  Verdict:         *** {response.verdict} ***")
    print(f"  Confidence:      {response.confidence_aggregate:.1%}")
    print(f"  Insights:        {len(response.insights)}")
    print(f"  Predictions:     {len(response.predictions)}")
    print(f"  Human Signoff:   {'YES — 888 HOLD' if response.human_signoff_required else 'No'}")

    _subsection("arifOS Telemetry Block")
    import json
    print(json.dumps(response.arifos_telemetry, indent=2, default=str))

    _subsection("Insights Summary")
    for i, insight in enumerate(response.insights, 1):
        signoff_flag = "⚠️ SIGNOFF REQUIRED" if insight.requires_human_signoff else ""
        print(f"\n  [{i}] Risk: {insight.risk_level.upper()} | Status: {insight.status} {signoff_flag}")
        print(f"       {insight.text[:300]}{'...' if len(insight.text) > 300 else ''}")

    if response.predictions:
        _subsection("Predictions")
        for pred in response.predictions:
            lo, hi = pred.expected_range
            print(f"  {pred.target}: {lo:.3g}–{hi:.3g} {pred.units} ({pred.confidence:.0%} confidence, method: {pred.method})")

    _subsection("Provenance Chain")
    if response.provenance_chain:
        for i, prov in enumerate(response.provenance_chain, 1):
            print(f"  [{i}] {prov.source_type} | {prov.source_id[:30]} | conf={prov.confidence:.0%}")
            if prov.citation:
                print(f"       Citation: {prov.citation[:80]}")
    else:
        print("  (No provenance records in chain)")

    # ---- Audit Log ----
    _section("STEP 4: Audit Log Summary (888 AUDIT)")
    print(f"  Total audit events: {len(response.audit_log)}")
    for event in response.audit_log:
        stage = event.get("stage", "?")
        ev_type = event.get("event", "?")
        ts = event.get("timestamp", "")
        ts_short = ts[:19] if isinstance(ts, str) else str(ts)
        print(f"  [{ts_short}] {stage} | {ev_type}")

    # ---- Memory Store ----
    _section("STEP 5: Memory Storage")
    entry_id = await memory_store.store(response, request)
    print(f"  Stored response as memory entry: {entry_id}")
    print(f"  Total entries in store: {memory_store.count()}")

    # Retrieve similar prospects
    similar = await memory_store.retrieve("Malay Basin structural closure", basin="Malay Basin")
    print(f"  Similar prospects retrieved: {len(similar)}")
    for entry in similar:
        print(f"    [{entry.entry_id}] {entry.prospect_name} | {entry.verdict} | conf={entry.confidence:.0%}")

    # ---- Markdown Report ----
    _section("STEP 6: Full Markdown Audit Report")
    md_report = reporter.generate_markdown_report(response, request)
    print(f"  Report length: {len(md_report):,} characters")
    print("\n  --- REPORT PREVIEW (first 3000 chars) ---\n")
    print(md_report[:3000])
    if len(md_report) > 3000:
        print(f"\n  ... [{len(md_report)-3000:,} more characters] ...")

    # ---- Human Brief ----
    _section("STEP 7: Human Brief (Non-Technical Stakeholder Summary)")
    brief = reporter.generate_human_brief(response)
    print()
    print(brief)

    # ---- JSON Audit ----
    _section("STEP 8: JSON Audit (vault_ledger format)")
    audit_dict = reporter.generate_json_audit(response)
    print(f"  Audit dict keys: {list(audit_dict.keys())}")
    print(f"  vault_entry_type: {audit_dict['vault_entry_type']}")
    print(f"  version: {audit_dict['version']}")
    print(f"  verdict: {audit_dict['verdict']}")
    print(f"  confidence_aggregate: {audit_dict['confidence_aggregate']}")
    print(f"  floor_compliance: {audit_dict['floor_compliance']}")

    # ---- Demo Complete ----
    _section("DEMO COMPLETE — 999 SEAL")
    print(f"""
  Verdict:    {response.verdict}
  Confidence: {response.confidence_aggregate:.1%}
  Hold:       {response.arifos_telemetry.get('hold', 'UNKNOWN')}
  Pipeline:   {response.arifos_telemetry.get('pipeline', '?')}
  Seal:       {response.arifos_telemetry.get('seal', '?')}

  To wire GEOX into arifOS production:
    1. Run:  uvicorn geox.geox_mcp_server:app --port 8100
    2. Add to arifOS mcp_servers config:
         - name: geox
           url: http://geox-server:8100/mcp
           tools: [geox_evaluate_prospect, geox_query_memory, geox_health]
    3. Inject llm_planner=agi_mind and audit_sink=vault_ledger into GeoXAgent

  DITEMPA BUKAN DIBERI
""")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(run_demo())
