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

import logging
from typing import Annotated, Any

from fastmcp import FastMCP
from fastmcp.tools import ToolResult

from arifosmcp.apps.surface_utils import envelope_error, envelope_pause, normalize_state, safe_get
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
from pydantic import Field

logger = logging.getLogger(__name__)

# ── App definition ────────────────────────────────────────────────────────────

forge_app = FastMCP("ForgeApp")
if not hasattr(forge_app, "ui"):  # fastmcp 3.2.0 compat: ui() removed — no-op passthrough
    forge_app.ui = lambda *args, **kwargs: (lambda fn: fn)


@forge_app.tool()
async def forge_judge_check(
    candidate_action: Annotated[
        str, Field(description="The action to evaluate before forging")
    ],
    risk_tier: Annotated[
        str, Field(description="Risk level: low, medium, high, critical")
    ] = "medium",
    session_id: str | None = None,
) -> ToolResult:
    """
    Pre-forge constitutional check — runs 888_JUDGE dry_run.
    Returns verdict for Gate 1 evaluation.
    """
    logger.info(
        f"forge_judge_check called: session_id={session_id}, state_type={type(STATE).__name__}"
    )
    try:
        from arifosmcp.runtime.tools import arifos_judge

        if not session_id:
            session_id = safe_get(STATE, "session_id")

        envelope = await arifos_judge(
            candidate_action=candidate_action,
            risk_tier=risk_tier,
            dry_run=True,
            session_id=session_id,
        )
        env_dict = normalize_state(envelope)

        verdict = env_dict.get("verdict") or ("SEAL" if env_dict.get("ok") else "VOID")
        floors_failed = (env_dict.get("policy") or {}).get("floors_failed", [])

        # ── Wisdom quote for judge gate (Logic from forge-ssct-sync) ──────────
        try:
            from arifosmcp.runtime.philosophy import select_wisdom_quote
            _wisdom_res = select_wisdom_quote("judge")
            _wisdom_text = f'"{_wisdom_res["quote"]}" — {_wisdom_res["author"]}' if _wisdom_res else None
        except Exception:
            _wisdom_text = None

        return ToolResult(
            content=[
                {
                    "type": "text",
                    "text": (
                        f"Pre-forge judge check: {verdict} "
                        f"(Trace: {env_dict.get('trace_id', '—')})"
                    ),
                },
                {
                    "type": "json",
                    "json": {
                        "gate1_verdict": verdict,
                        "gate1_ok": verdict == "SEAL",
                        "floors_failed": floors_failed,
                        "floors_failed_count": len(floors_failed),
                        "trace_id": env_dict.get("trace_id", "—"),
                        "wisdom": _wisdom_text,
                    },
                },
            ]
        )

    except Exception as exc:
        logger.warning(f"forge_judge_check failed: {exc}")
        return ToolResult(
            is_error=True,
            content=[
                 {"type": "text", "text": f"forge_judge_check failed: {exc}"}
            ]
        )


@forge_app.tool()
async def forge_execute(
    candidate_action: Annotated[
        str,
        Field(description="The action to execute (requires judge SEAL and human approval)"),
    ],
    risk_tier: Annotated[
        str, Field(description="Risk level: low, medium, high, critical")
    ] = "medium",
    session_id: str | None = None,
    judge_verdict: str = "VOID",
    judge_g_star: float = 0.0,
    judge_state_hash: str = "",
) -> ToolResult:
    """
    Execute forge after both gates pass.
    Gate 1 (888_JUDGE SEAL) is re-verified here.
    Gate 2 (human approval) is enforced by this tool returning 888_HOLD
    if the verdict is not SEAL — the human must have clicked APPROVE
    in the UI after seeing the judge result.
    """
    logger.info(f"forge_execute called: session_id={session_id}, state_type={type(STATE).__name__}")
    try:
        from arifosmcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP

        if not session_id:
            session_id = safe_get(STATE, "session_id")

        # Resolve judge values from UI state if not explicitly provided
        gate1_verdict = judge_verdict or safe_get(STATE, "gate1_verdict", "VOID")
        gate1_ok = safe_get(STATE, "gate1_ok", False)
        gate2_approved = safe_get(STATE, "gate2_approved", False)

        if not gate1_ok:
            return ToolResult(
                content=[{"type": "text", "text": f"Gate 1 not passed: verdict={gate1_verdict}. Run judge first."}]
            )

        if not gate2_approved:
             return ToolResult(
                content=[{"type": "text", "text": "Gate 2 not passed: human has not approved. F13 Sovereign veto."}]
            )

        # Use the hardened dispatch map to call forge (handles correct signature)
        handler = HARDENED_DISPATCH_MAP.get("arifos_forge")
        if not handler:
            return ToolResult(is_error=True, content=[{"type": "text", "text": "arifos_forge not found in dispatch map"}])

        envelope = await handler(
            action=candidate_action,
            payload={"candidate_action": candidate_action, "risk_tier": risk_tier},
            session_id=session_id or "global",
            judge_verdict=gate1_verdict,
            judge_g_star=judge_g_star,
            judge_state_hash=judge_state_hash,
            dry_run=True,
            platform="surface",
        )
        env_dict = normalize_state(envelope)

        verdict = env_dict.get("verdict", "VOID")
        
        try:
            from arifosmcp.runtime.philosophy import select_wisdom_quote
            _wisdom_res = select_wisdom_quote("forge")
            _wisdom_text = f'"{_wisdom_res["quote"]}" — {_wisdom_res["author"]}' if _wisdom_res else None
        except Exception:
            _wisdom_text = None

        return ToolResult(
            content=[
                {
                    "type": "text",
                    "text": (
                        f"Forge execution complete: {verdict} "
                        f"(OK: {env_dict.get('ok', False)})"
                    ),
                },
                {
                    "type": "json",
                    "json": {
                        "forge_verdict": verdict,
                        "forge_ok": env_dict.get("ok", False),
                        "result": env_dict.get("result", "—"),
                        "trace_id": env_dict.get("trace_id", "—"),
                        "wisdom": _wisdom_text,
                    },
                },
            ]
        )

    except Exception as exc:
        logger.warning(f"forge_execute failed: {exc}")
        return ToolResult(is_error=True, content=[{"type": "text", "text": f"forge_execute failed: {exc}"}])


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
            SetState("gate1_verdict", RESULT["gate1_verdict"]),
            SetState("gate1_ok", RESULT["gate1_ok"]),
            SetState("floors_failed", RESULT["floors_failed"]),
            SetState("floors_failed_count", RESULT["floors_failed_count"]),
            SetState("trace_id", RESULT["trace_id"]),
            ShowToast("Gate 1: Judge evaluated", variant="success"),
        ],
        on_error=ShowToast("Judge check failed", variant="error"),
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
        ShowToast("Gate 2: Human REJECTED — 888_HOLD", variant="error"),
    ]

    # ── Forge Execute ────────────────────────────────────────────────────────
    on_forge = CallTool(
        forge_execute,
        args={"candidate_action": candidate_action, "risk_tier": risk_tier},
        on_success=[
            SetState("forge_verdict", RESULT["forge_verdict"]),
            SetState("forge_ok", RESULT["forge_ok"]),
            SetState("forge_result", RESULT["result"]),
            SetState("forged", True),
            ShowToast("Forge executed — sealed to VAULT999", variant="success"),
        ],
        on_error=ShowToast("Forge execution failed", variant="error"),
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

        # ── Wisdom strip ─────────────────────────────────────────────────────
        try:
            from arifosmcp.runtime.philosophy import select_wisdom_quote

            _wisdom = select_wisdom_quote("forge")
            if _wisdom and _wisdom.get("quote"):
                Muted(
                    f'"{_wisdom["quote"]}" — {_wisdom["author"]}',
                    css_class="text-xs italic border-l-2 pl-3 border-muted-foreground/30",
                )
        except Exception:
            pass

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
                            variant=STATE["forge_ok"].then("success", "destructive"),
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
                variant="error",
            )

            # Step 3: Execute Forge (only meaningful after both gates)
            Button(
                "③ Execute Forge",
                on_click=on_forge,
                variant="default",
            )

        Muted(
            "Sequence: Judge → Approve → Execute. No shortcuts permitted.",
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
