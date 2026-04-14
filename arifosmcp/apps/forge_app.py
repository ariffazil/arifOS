"""
arifosmcp/apps/forge_app.py
═══════════════════════════════════════════════════════════════════════════════
arifOS ForgeApp — Double-Gated Execution Surface (FORGE)
═══════════════════════════════════════════════════════════════════════════════

Implements the forge execution surface as a FastMCPApp:

  @app.ui()   forge_surface      — entry; shows action, judge verdict, approval gate
  @app.tool() forge_execute      — backend; calls arifos_forge with F13 guard

Double-gate architecture:
  Gate 1: 888_JUDGE must return SEAL (constitutional verdict)
  Gate 2: Human must explicitly APPROVE (F13 Sovereign Veto)
  Only when BOTH gates pass does the forge execute.

UI anatomy:
  ┌── FORGE Execution Surface ────────────────────────────────────────┐
  │  Action: <candidate_action>                                       │
  │  ──────────────────────────────────────────────────────────────── │
  │  Gate 1: 888_JUDGE   ● SEAL / ○ VOID / ○ PENDING                 │
  │  Gate 2: F13 HUMAN   ● APPROVED / ○ PENDING                      │
  │  ──────────────────────────────────────────────────────────────── │
  │  [Run Judge] [Execute Forge]                                       │
  └────────────────────────────────────────────────────────────────────┘

F13 Sovereign: 888_HOLD is a feature, not a bug.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP
from prefab_ui.actions import SetState, ShowToast
from prefab_ui.actions.mcp import CallTool
from prefab_ui.app import PrefabApp
from prefab_ui.components import (
    Alert,
    Badge,
    Button,
    Card,
    CardContent,
    Column,
    Grid,
    Heading,
    If,
    Muted,
    Row,
    Separator,
    Text,
)
from prefab_ui.rx import RESULT, STATE


# ── App definition ────────────────────────────────────────────────────────────

forge_app = FastMCP("ForgeApp")


@forge_app.tool()
async def forge_judge_check(
    candidate_action: str,
    risk_tier: str = "medium",
) -> dict[str, Any]:
    """
    Pre-forge constitutional check — runs 888_JUDGE dry_run.
    Returns verdict for Gate 1 evaluation.
    """
    try:
        from arifosmcp.runtime.tools import arifos_judge
        envelope = await arifos_judge(
            candidate_action=candidate_action,
            risk_tier=risk_tier,
            dry_run=True,
        )
        env_dict = (
            envelope.model_dump()
            if hasattr(envelope, "model_dump")
            else dict(envelope)
        )

        verdict = env_dict.get("verdict") or (
            "SEAL" if env_dict.get("ok") else "VOID"
        )
        floors_failed = (env_dict.get("policy") or {}).get("floors_failed", [])

        return {
            "gate1_verdict": verdict,
            "gate1_ok": verdict == "SEAL",
            "floors_failed": floors_failed,
            "floors_failed_count": len(floors_failed),
            "trace_id": env_dict.get("trace_id", "—"),
        }

    except Exception as exc:
        return {
            "gate1_verdict": "VOID",
            "gate1_ok": False,
            "floors_failed": ["ALL"],
            "floors_failed_count": 13,
            "trace_id": f"error: {exc}",
        }


@forge_app.tool()
async def forge_execute(
    candidate_action: str,
    risk_tier: str = "medium",
) -> dict[str, Any]:
    """
    Execute forge after both gates pass.
    Gate 1 (888_JUDGE SEAL) is re-verified here.
    Gate 2 (human approval) is enforced by this tool returning 888_HOLD
    if the verdict is not SEAL — the human must have clicked APPROVE
    in the UI after seeing the judge result.
    """
    try:
        from arifosmcp.runtime.tools import arifos_forge
        envelope = await arifos_forge(
            candidate_action=candidate_action,
            risk_tier=risk_tier,
        )
        env_dict = (
            envelope.model_dump()
            if hasattr(envelope, "model_dump")
            else dict(envelope)
        )

        verdict = env_dict.get("verdict", "VOID")
        return {
            "forge_verdict": verdict,
            "forge_ok": env_dict.get("ok", False),
            "result": env_dict.get("result", "—"),
            "trace_id": env_dict.get("trace_id", "—"),
        }

    except Exception as exc:
        return {
            "forge_verdict": "VOID",
            "forge_ok": False,
            "result": f"Forge error: {exc}",
            "trace_id": "—",
        }


@forge_app.ui(title="Forge — Double-Gated Execution")
def forge_surface(
    candidate_action: str = "describe the action to forge",
    risk_tier: str = "medium",
) -> PrefabApp:
    """
    Open the arifOS Forge Execution Surface with double-gate architecture.
    Gate 1: 888_JUDGE must SEAL. Gate 2: Human must APPROVE.
    F13 Sovereign Veto: no machine may cross this line alone.
    """

    initial_state: dict[str, Any] = {
        # Gate 1
        "gate1_verdict": "PENDING",
        "gate1_ok": False,
        "floors_failed": [],
        "floors_failed_count": 0,
        # Gate 2
        "gate2_approved": False,
        # Forge result
        "forge_verdict": "—",
        "forge_ok": False,
        "forge_result": "—",
        "forged": False,
        # Meta
        "trace_id": "—",
        "candidate": candidate_action,
    }

    # ── Gate 1: Run Judge ────────────────────────────────────────────────────
    on_judge = CallTool(
        forge_judge_check,
        args={"candidate_action": candidate_action, "risk_tier": risk_tier},
        on_success=[
            SetState("gate1_verdict",      RESULT["gate1_verdict"]),
            SetState("gate1_ok",           RESULT["gate1_ok"]),
            SetState("floors_failed",      RESULT["floors_failed"]),
            SetState("floors_failed_count", RESULT["floors_failed_count"]),
            SetState("trace_id",           RESULT["trace_id"]),
            ShowToast("Gate 1: Judge evaluated", variant="success"),
        ],
        on_error=ShowToast("Judge check failed", variant="destructive"),
    )

    # ── Gate 2: Human Approval ───────────────────────────────────────────────
    on_approve = [
        SetState("gate2_approved", True),
        ShowToast("Gate 2: Human APPROVED — forge unlocked", variant="success"),
    ]

    on_reject = [
        SetState("gate2_approved", False),
        SetState("gate1_verdict", "888_HOLD"),
        SetState("gate1_ok", False),
        ShowToast("Gate 2: Human REJECTED — 888_HOLD", variant="destructive"),
    ]

    # ── Forge Execute ────────────────────────────────────────────────────────
    on_forge = CallTool(
        forge_execute,
        args={"candidate_action": candidate_action, "risk_tier": risk_tier},
        on_success=[
            SetState("forge_verdict", RESULT["forge_verdict"]),
            SetState("forge_ok",      RESULT["forge_ok"]),
            SetState("forge_result",  RESULT["result"]),
            SetState("forged",        True),
            ShowToast("Forge executed — sealed to VAULT999", variant="success"),
        ],
        on_error=ShowToast("Forge execution failed", variant="destructive"),
    )

    # ── Reactive bindings ────────────────────────────────────────────────────
    gate1_ok = STATE["gate1_ok"]
    gate2_ok = STATE["gate2_approved"]
    forged_rx = STATE["forged"]

    with Column(gap=5, css_class="p-5 max-w-2xl") as view:

        # ── Header ──────────────────────────────────────────────────────────
        with Row(gap=3, align="center"):
            Heading("Forge — Execution Surface")
            Badge(
                "F13 Double-Gate",
                variant="secondary",
                css_class="font-mono text-xs",
            )

        Muted("Constitutional forge with dual approval · DITEMPA BUKAN DIBERI")
        Separator()

        # ── Candidate Action ────────────────────────────────────────────────
        with Card(css_class="bg-muted/40"):
            with CardContent(css_class="py-3"):
                Text(
                    f'Action: "{candidate_action}"',
                    css_class="text-sm font-medium",
                )
                Muted(f"Risk: {risk_tier.upper()} · Constitutional forge")

        Separator()

        # ── Gate Status (2-column) ──────────────────────────────────────────
        Muted("Gate Status", css_class="text-xs uppercase tracking-wider")

        with Grid(columns=2, gap=4):
            # Gate 1: Judge
            with Card():
                with CardContent(css_class="py-4 text-center"):
                    Muted(
                        "Gate 1 · 888_JUDGE",
                        css_class="text-xs uppercase tracking-wider mb-2",
                    )
                    Badge(
                        STATE["gate1_verdict"],
                        variant=gate1_ok.then("success", "secondary"),
                        css_class="font-mono text-sm",
                    )
                    with If(gate1_ok):
                        Muted(
                            "✅ Constitutional SEAL granted",
                            css_class="text-xs mt-2",
                        )

            # Gate 2: Human
            with Card():
                with CardContent(css_class="py-4 text-center"):
                    Muted(
                        "Gate 2 · F13 HUMAN",
                        css_class="text-xs uppercase tracking-wider mb-2",
                    )
                    Badge(
                        gate2_ok.then("APPROVED", "PENDING"),
                        variant=gate2_ok.then("success", "secondary"),
                        css_class="font-mono text-sm",
                    )
                    with If(gate2_ok):
                        Muted(
                            "✅ Human authority confirmed",
                            css_class="text-xs mt-2",
                        )

        # ── Floor Failures (if any) ─────────────────────────────────────────
        with If(STATE["floors_failed_count"]):
            with Card(css_class="border-destructive/50"):
                with CardContent(css_class="py-3"):
                    Muted(
                        "Floor Failures Detected",
                        css_class="text-xs uppercase text-destructive",
                    )
                    Text(
                        STATE["floors_failed"],
                        css_class="text-sm font-mono mt-1",
                    )

        Separator()

        # ── Forge Result (after execution) ──────────────────────────────────
        with If(forged_rx):
            with Card(css_class="bg-muted/40"):
                with CardContent(css_class="py-3"):
                    with Row(gap=2, align="center"):
                        Text("Forge Result:", css_class="text-sm font-semibold")
                        Badge(
                            STATE["forge_verdict"],
                            variant=STATE["forge_ok"].then(
                                "success", "destructive"
                            ),
                            css_class="font-mono",
                        )
                    Muted(
                        STATE["forge_result"],
                        css_class="text-xs mt-2 font-mono",
                    )
                    with Row(gap=2):
                        Muted("Trace:", css_class="text-xs")
                        Text(
                            STATE["trace_id"],
                            css_class="text-xs font-mono",
                        )

        Separator()

        # ── Actions ─────────────────────────────────────────────────────────
        Alert(
            title="F13 Sovereign — Double Gate Required",
            description=(
                "Gate 1: 888_JUDGE must return SEAL. "
                "Gate 2: Human must explicitly APPROVE. "
                "Only then does the forge execute. "
                "888_HOLD is a feature, not a bug."
            ),
            variant="warning",
        )

        with Row(gap=3):
            # Step 1: Run Judge
            Button(
                "① Run Judge",
                on_click=on_judge,
                variant="outline",
            )

            # Step 2: Approve / Reject
            Button(
                "② Approve",
                on_click=on_approve,
                variant="outline",
            )
            Button(
                "② Reject",
                on_click=on_reject,
                variant="destructive",
            )

            # Step 3: Execute Forge (only meaningful after both gates)
            Button(
                "③ Execute Forge",
                on_click=on_forge,
                variant="default",
            )

        Muted(
            "Sequence: Judge → Approve → Execute. "
            "No shortcuts permitted.",
            css_class="text-xs",
        )

        Separator()
        Muted(
            "arifOS · DITEMPA BUKAN DIBERI · 888_HOLD is a feature, not a bug",
            css_class="text-xs text-center",
        )

    return PrefabApp(view=view, state=initial_state)


def _register(mcp: FastMCP) -> None:
    """Mount ForgeApp onto the platform FastMCP server."""
    mcp.add_provider(forge_app)
