"""
arifOS API Metrics Routes - System metrics and floor thresholds.

Provides information about the constitutional floors and thresholds.
"""

from __future__ import annotations

from fastapi import APIRouter

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
async def get_metrics() -> MetricsResponse:
    """
    Get system metrics and floor thresholds.

    Returns the current configuration of constitutional floors,
    verdicts, and memory bands.
    """
    try:
        from arifos_core.runtime_manifest import get_active_epoch
        epoch = get_active_epoch()
    except Exception:
        epoch = "v38"

    return MetricsResponse(
        epoch=epoch,
        floors=FLOOR_THRESHOLDS,
        verdicts=["SEAL", "PARTIAL", "VOID", "SABAR", "888_HOLD", "SUNSET"],
        memory_bands=["VAULT", "LEDGER", "ACTIVE", "PHOENIX", "WITNESS", "VOID"],
    )


@router.get("/floors")
async def get_floors() -> dict:
    """
    Get detailed floor information.

    Returns all 9 constitutional floors with their thresholds and types.
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
