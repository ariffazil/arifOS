from datetime import datetime, timezone

from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from ..models import MetricsResponse, FloorThreshold

router = APIRouter(prefix="/metrics", tags=["metrics"])


# =============================================================================
# FLOOR THRESHOLD DEFINITIONS
# =============================================================================

FLOOR_THRESHOLDS = [
    FloorThreshold(
        floor_id="F1",
        name="Amanah",
        threshold=True,  # LOCK
        type="hard",
        description="Reversible? Within mandate? No manipulation.",
    ),
    FloorThreshold(
        floor_id="F2",
        name="Truth",
        threshold=0.99,
        type="hard",
        description="Consistent with reality? No confident guessing.",
    ),
    FloorThreshold(
        floor_id="F3",
        name="Tri-Witness",
        threshold=0.95,
        type="hard",
        description="Human-AI-Earth consensus for high-stakes.",
    ),
    FloorThreshold(
        floor_id="F4",
        name="DeltaS (Clarity)",
        threshold=0.0,
        type="hard",
        description="Reduces confusion? Never adds entropy.",
    ),
    FloorThreshold(
        floor_id="F5",
        name="Peace²",
        threshold=1.0,
        type="soft",
        description="Non-destructive? De-escalation.",
    ),
    FloorThreshold(
        floor_id="F6",
        name="κᵣ (Empathy)",
        threshold=0.95,
        type="soft",
        description="Serves weakest stakeholder?",
    ),
    FloorThreshold(
        floor_id="F7",
        name="Ω₀ (Humility)",
        threshold=(0.03, 0.05),  # Range
        type="hard",
        description="States 3-5% uncertainty? No god-mode.",
    ),
    FloorThreshold(
        floor_id="F8",
        name="G (Genius)",
        threshold=0.80,
        type="derived",
        description="Governed intelligence threshold.",
    ),
    FloorThreshold(
        floor_id="F9",
        name="C_dark",
        threshold=0.30,
        type="derived",
        description="Dark cleverness contained? <0.30 required.",
    ),
]


# =============================================================================
# METRICS ENDPOINTS
# =============================================================================

@router.get("/", response_model=MetricsResponse)
async def get_metrics_config() -> MetricsResponse:
    """
    Get system metrics configuration and floor thresholds.
    """
    try:
        from arifos.core.system.runtime_manifest import get_active_epoch
        epoch = get_active_epoch()
    except Exception:
        epoch = "v38"

    return MetricsResponse(
        epoch=epoch,
        floors=FLOOR_THRESHOLDS,
        verdicts=["SEAL", "PARTIAL", "VOID", "SABAR", "888_HOLD", "SUNSET"],
        memory_bands=["VAULT", "LEDGER", "ACTIVE", "PHOENIX", "WITNESS", "VOID"],
    )

@router.get("/prometheus")
@router.get("/scrape") # Alias
async def prometheus_metrics() -> Response:
    """
    Exposes live system metrics in Prometheus format.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@router.get("/json")
async def get_live_metrics_json() -> dict:
    """
    Get LIVE constitutional metrics from the governance pipeline.
    
    Returns real-time computed values from:
    - VAULT999 Cooling Ledger (SEAL/VOID rates)
    - ASI Evaluator (τ, κᵣ, ΔS)
    - Entropy Tracker (thermodynamic compliance)
    - Governance Engine (uptime, vitality Ψ)
    """
    from arifos.core.integration.api.services.live_metrics_service import (
        get_live_metrics_service
    )
    
    try:
        service = get_live_metrics_service()
        metrics = service.get_live_metrics(use_cache=True)
        
        return {
            "status": "live",
            "calibration_mode": False,  # ✅ Real data from VAULT999
            "timestamp": metrics.timestamp,
            # Trinity Scores
            "tau": metrics.tau,                    # τ: Truth accuracy (AGI)
            "kappa_r": metrics.kappa_r,            # κᵣ: Empathy (ASI)
            "psi": metrics.psi,                    # Ψ: Vitality (APEX)
            "entropy_delta": metrics.entropy_delta, # ΔS: Clarity
            # System Health
            "seal_rate": metrics.seal_rate,
            "void_rate": metrics.void_rate,
            "active_sessions": metrics.active_sessions,
            "uptime_hours": metrics.uptime_hours,
            # Truth Distribution
            "truth_score": metrics.truth_percentiles,  # p50, p95, p99
            # Constitutional Compliance
            "constitutional_compliance": {
                "floors_passed": metrics.floors_passed,
                "floors_failed": metrics.floors_failed,
                "sabar_triggered": metrics.sabar_triggered
            }
        }
        
    except Exception as e:
        # Fail transparently - don't serve mock data
        return {
            "status": "error",
            "calibration_mode": True,  # ⚠️ Explicitly flag as synthetic
            "error": str(e),
            "disclaimer": "Serving fallback data due to metrics service error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tau": 0.99,
            "kappa_r": 0.98,
            "psi": 0.00,
            "entropy_delta": -0.042,
            "seal_rate": 0.95,
            "void_rate": 0.05
        }


@router.get("/floors")
async def get_floors() -> dict:
    """
    Get detailed floor information.
    """
    return {
        "floors": [f.model_dump() for f in FLOOR_THRESHOLDS],
        "logic": "All floors AND - every floor must PASS",
        "repair_order": "F1 first, then F2-F9",
        "hard_floors": ["F1", "F2", "F3", "F4", "F7"],
        "soft_floors": ["F5", "F6"],
        "derived_floors": ["F8", "F9"],
    }


@router.get("/verdicts")
async def get_verdicts() -> dict:
    """
    Get verdict definitions.

    Returns all possible verdicts and their meanings.
    """
    return {
        "verdicts": {
            "SEAL": {
                "description": "All floors pass. Approved to execute.",
                "action": "Emit output, log to Cooling Ledger",
            },
            "PARTIAL": {
                "description": "Hard floors pass, soft floors fail.",
                "action": "Emit output with disclaimer/warning",
            },
            "VOID": {
                "description": "Any hard floor fails.",
                "action": "Refuse safely, trigger SABAR",
            },
            "SABAR": {
                "description": "@EYE blocking or uncertainty/cooling needed.",
                "action": "Stop. Acknowledge. Breathe. Adjust. Resume.",
            },
            "888_HOLD": {
                "description": "High-stakes, needs explicit confirmation.",
                "action": "Judiciary hold, request clarification",
            },
            "SUNSET": {
                "description": "Lawful revocation when truth expires.",
                "action": "Move from LEDGER to PHOENIX for re-trial",
            },
        },
        "hierarchy": "SABAR > VOID > 888_HOLD > PARTIAL > SEAL",
    }


@router.get("/genius")
async def get_genius_metrics() -> dict:
    """
    Get GENIUS LAW metrics definitions.

    Returns the formulas and thresholds for G, C_dark, and Psi.
    """
    return {
        "genius_law": {
            "G": {
                "name": "Genius Index",
                "formula": "normalize(A × P × E × X)",
                "threshold": ">= 0.80 SEAL, 0.50-0.80 PARTIAL",
            },
            "C_dark": {
                "name": "Dark Cleverness",
                "formula": "normalize(A × (1-P) × (1-X) × E)",
                "threshold": "< 0.30 SEAL, 0.30-0.60 PARTIAL",
            },
            "Psi": {
                "name": "Vitality",
                "formula": "(ΔS × Peace² × κᵣ × Amanah) / (Entropy + ε)",
                "threshold": ">= 1.00 ALIVE",
            },
        },
        "components": {
            "A": "Amanah (integrity)",
            "P": "Peace² (stability)",
            "E": "Empathy (κᵣ)",
            "X": "Clarity (1 - DeltaS if negative)",
        },
    }
