"""
arifosmcp/apps/init_app.py
═══════════════════════════════════════════════════════════════════════════════
arifOS InitApp — Session Anchoring Surface (000_INIT)
═══════════════════════════════════════════════════════════════════════════════

Implements the session anchoring surface as a FastMCPApp:

  @app.ui()   init_surface      — entry; shows epoch, intent, mode selector
  @app.tool() arifos_anchor_session — backend; calls arifos_init, returns session data

UI anatomy:
  ┌── 000 Session Anchor ─────────────────────────────────────────────┐
  │  Epoch: 2026-04-13                                                │
  │  Declared Intent: [input field]                                   │
  │  Mode: ○ Standard  ● Diagnostic  ○ Sovereign                     │
  │  ──────────────────────────────────────────────────────────────── │
  │  Ω₀ Humility Band: ∈ [0.03, 0.05]                                │
  │  Constitutional Alignment: ● ALIGNED                              │
  │  ──────────────────────────────────────────────────────────────── │
  │  [Anchor Session]                                                  │
  └────────────────────────────────────────────────────────────────────┘

F1 Amanah: session creation is commitment — once anchored, cannot be undone.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Annotated, Any

from fastmcp import FastMCP
from fastmcp.tools import ToolResult
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
    ForEach,
    Grid,
    Heading,
    If,
    Metric,
    Muted,
    Ring,
    Row,
    Select,
    SelectOption,
    Separator,
    Text,
)
from prefab_ui.rx import RESULT, STATE
from pydantic import Field

logger = logging.getLogger(__name__)

# ── Operator interpretation (CHANGE-01) ───────────────────────────────────────
_STATUS_INTERPRETATIONS: dict[str, dict[str, str]] = {
    "ALIGNED": {
        "badge": "SEALED",
        "posture": "All floors passing. Safe for consequential action.",
        "variant": "success",
    },
    "UNALIGNED": {
        "badge": "BLOCKED",
        "posture": "Hard floor violated. No consequential action permitted. Human required.",
        "variant": "destructive",
    },
    "pending": {
        "badge": "PENDING",
        "posture": "Awaiting constitutional evaluation...",
        "variant": "secondary",
    },
}

_PHILOSOPHY: dict[str, str] = {
    "SEAL": "DITEMPA, BUKAN DIBERI.",
    "pending": "Awaiting constitutional evaluation...",
}


# ── App definition ────────────────────────────────────────────────────────────

init_app = FastMCP("InitApp")
if not hasattr(init_app, "ui"):  # fastmcp 3.2.0 compat: ui() removed — no-op passthrough
    init_app.ui = lambda *args, **kwargs: lambda fn: fn


@init_app.tool(name="arifos_anchor_session", tags={"public", "init"})
async def anchor_session(
    declared_intent: Annotated[
        str, Field(description="The goal or purpose of the session. F1 Amanah commitment.")
    ] = "",
    mode: Annotated[
        str, Field(description="Session mode: standard, diagnostic, or sovereign")
    ] = "standard",
) -> ToolResult:
    """
    Anchor a new arifOS session. Calls arifos_init with the declared intent
    and returns session metadata including epoch, session_id, and alignment.
    """
    try:
        from arifosmcp.runtime.tools import arifos_init

        envelope = await arifos_init(
            intent=declared_intent or "General session",
        )
        env_dict = envelope.model_dump() if hasattr(envelope, "model_dump") else dict(envelope)

        session_id = env_dict.get("session_id", "—")
        epoch = env_dict.get("epoch", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        omega0 = float(env_dict.get("telemetry", {}).get("omega_0", 0.04))
        aligned = env_dict.get("ok", True)

        # Next actions (CHANGE-04)
        next_actions = []
        if aligned:
            next_actions.append("Session healthy. Proceed with normal operations. Monitor ΔS.")
        else:
            next_actions.append("Identity incomplete or intent unclear. Refine declaration.")

        # ── Wisdom quote for anchor surface (Logic from forge-ssct-sync) ──────
        try:
            from arifosmcp.runtime.philosophy import select_wisdom_quote

            _wisdom_res = select_wisdom_quote("anchor")
            _philosophy_text = (
                f'"{_wisdom_res["quote"]}" — {_wisdom_res["author"]}'
                if _wisdom_res
                else _PHILOSOPHY["SEAL"]
            )
        except Exception:
            _philosophy_text = _PHILOSOPHY["SEAL"] if aligned else _PHILOSOPHY["pending"]

        return ToolResult(
            content=f"Session anchored successfully: {session_id} (Epoch: {epoch})",
            structured_content={
                "session_id": session_id,
                "epoch": epoch,
                "mode": mode,
                "declared_intent": declared_intent or "General session",
                "omega0": omega0,
                "aligned": aligned,
                "anchored": True,
                "trace_id": env_dict.get("trace_id", "—"),
                "next_actions": next_actions,
                "philosophy": _philosophy_text,
            },
        )

    except Exception as exc:
        logger.warning(f"anchor_session failed: {exc}")
        return ToolResult(
            content=f"Session anchor failed: {exc}",
            structured_content={
                "session_id": "—",
                "epoch": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "mode": mode,
                "declared_intent": declared_intent or "General session",
                "omega0": 0.04,
                "aligned": False,
                "anchored": False,
                "trace_id": f"error: {exc}",
                "next_actions": ["Repair floor state or obtain human veto override."],
                "philosophy": _PHILOSOPHY["pending"],
                "_error": True,
                "_error_message": str(exc),
            },
        )


@init_app.ui(title="000 Session Anchor")
def init_surface(
    declared_intent: str = "",
) -> PrefabApp:
    """
    Open the arifOS Session Anchoring Surface.
    Declares intent, selects mode, and anchors the constitutional session.
    F1 Amanah — session creation is irreversible commitment.
    """
    epoch_now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    initial_state: dict[str, Any] = {
        "session_id": "—",
        "epoch": epoch_now,
        "mode": "standard",
        "declared_intent": declared_intent or "",
        "omega0": 0.04,
        "aligned": False,
        "anchored": False,
        "trace_id": "—",
        "next_actions": ["Awaiting constitutional evaluation..."],
        "philosophy": _PHILOSOPHY["pending"],
    }

    on_anchor = CallTool(
        anchor_session,
        args={
            "declared_intent": declared_intent or "General session",
            "mode": "standard",
        },
        on_success=[
            SetState("session_id", RESULT["session_id"]),
            SetState("epoch", RESULT["epoch"]),
            SetState("mode", RESULT["mode"]),
            SetState("declared_intent", RESULT["declared_intent"]),
            SetState("omega0", RESULT["omega0"]),
            SetState("aligned", RESULT["aligned"]),
            SetState("anchored", RESULT["anchored"]),
            SetState("trace_id", RESULT["trace_id"]),
            SetState("next_actions", RESULT["next_actions"]),
            SetState("philosophy", RESULT["philosophy"]),
            ShowToast("Session anchored — 000_INIT sealed", variant="success"),
        ],
        on_error=ShowToast("Session anchor failed", variant="error"),
    )

    # ── Reactive bindings ────────────────────────────────────────────────────
    anchored_rx = STATE["anchored"]
    aligned_rx = STATE["aligned"]
    omega0_rx = STATE["omega0"]

    with Column(gap=5, css_class="p-5 max-w-2xl") as view:
        # ── Operator Interpretation Banner (CHANGE-01) ────────────────────
        with Card(css_class="border-2 border-primary/20"):
            with CardContent(css_class="py-4 px-6"):
                with Row(gap=4, align="center"):
                    Badge(
                        anchored_rx.then(
                            aligned_rx.then(
                                _STATUS_INTERPRETATIONS["ALIGNED"]["badge"],
                                _STATUS_INTERPRETATIONS["UNALIGNED"]["badge"],
                            ),
                            _STATUS_INTERPRETATIONS["pending"]["badge"],
                        ),
                        variant=anchored_rx.then(
                            aligned_rx.then(
                                _STATUS_INTERPRETATIONS["ALIGNED"]["variant"],
                                _STATUS_INTERPRETATIONS["UNALIGNED"]["variant"],
                            ),
                            _STATUS_INTERPRETATIONS["pending"]["variant"],
                        ),
                        css_class="font-mono text-lg py-1 px-3 h-auto",
                    )
                    with Column(gap=0):
                        Heading("arifOS Metabolic Monitor", size="sm")
                        Text(
                            anchored_rx.then(
                                aligned_rx.then(
                                    _STATUS_INTERPRETATIONS["ALIGNED"]["posture"],
                                    _STATUS_INTERPRETATIONS["UNALIGNED"]["posture"],
                                ),
                                _STATUS_INTERPRETATIONS["pending"]["posture"],
                            ),
                            css_class="text-sm font-medium",
                        )

        Muted("Constitutional session anchoring · DITEMPA BUKAN DIBERI")
        Separator()

        # ── Wisdom strip ─────────────────────────────────────────────────────
        try:
            from arifosmcp.runtime.philosophy import select_wisdom_quote

            _wisdom = select_wisdom_quote("anchor")
            if _wisdom and _wisdom.get("quote"):
                Muted(
                    f'"{_wisdom["quote"]}" — {_wisdom["author"]}',
                    css_class="text-xs italic border-l-2 pl-3 border-muted-foreground/30",
                )
        except Exception:
            pass

        # ── Epoch + Intent ──────────────────────────────────────────────────
        with Card():
            with CardContent(css_class="py-4"):
                with Grid(columns=2, gap=4):
                    with Column(gap=2):
                        Muted("Epoch", css_class="text-xs uppercase tracking-wider")
                        Text(
                            epoch_now,
                            css_class="text-xl font-bold font-mono",
                        )

                    with Column(gap=2):
                        Muted(
                            "Declared Intent",
                            css_class="text-xs uppercase tracking-wider",
                        )
                        Text(
                            declared_intent or "(awaiting declaration)",
                            css_class="text-sm",
                        )

        Separator()

        # ── Constitutional Alignment (CHANGE-03) ────────────────────────────
        Muted(
            "Metabolic Alignment",
            css_class="text-xs uppercase tracking-wider",
        )

        with Grid(columns=3, gap=3):
            # Ω₀ Humility
            with Card():
                with CardContent(css_class="py-3 flex flex-col items-center"):
                    Ring(
                        value=omega0_rx * 100,
                        max=10,
                        label=omega0_rx,
                        variant="success",
                        size="sm",
                    )
                    Muted("Baseline (Ω₀)", css_class="mt-1 text-[10px]")

            # Alignment status
            with Card():
                with CardContent(css_class="py-3 text-center"):
                    Badge(
                        aligned_rx.then("● ALIGNED", "○ UNALIGNED"),
                        variant=aligned_rx.then("success", "destructive"),
                        css_class="font-mono text-xs",
                    )
                    Muted("Alignment", css_class="mt-2 text-[10px]")

            # Session status
            with Card():
                with CardContent(css_class="py-3 text-center"):
                    Badge(
                        anchored_rx.then("ANCHORED", "PENDING"),
                        variant=anchored_rx.then("success", "secondary"),
                        css_class="font-mono text-xs",
                    )
                    Muted("Session", css_class="mt-2 text-[10px]")

        Separator()

        # ── Recommended Next Actions (CHANGE-04) ──────────────────────────
        with If(anchored_rx):
            with Column(gap=3):
                Muted("What to do now", css_class="text-xs uppercase tracking-wider")
                with Card(css_class="bg-primary/5"):
                    with CardContent(css_class="py-4"):
                        with ForEach(STATE["next_actions"]):
                            from prefab_ui.rx import ITEM as ACTION

                            with Row(gap=3, align="center", css_class="py-1"):
                                Badge(
                                    "ACTION",
                                    variant="secondary",
                                    css_class="text-[9px] h-4 font-bold",
                                )
                                Text(ACTION, css_class="text-sm font-medium")
            Separator()

        # ── Post-anchor details ─────────────────────────────────────────────
        with If(anchored_rx):
            with Card(css_class="bg-muted/40"):
                with CardContent(css_class="py-3"):
                    with Row(gap=3):
                        Muted("Session ID:", css_class="text-xs")
                        Text(
                            STATE["session_id"],
                            css_class="text-xs font-mono text-primary/70",
                        )
                    with Row(gap=3):
                        Muted("Trace:", css_class="text-xs")
                        Text(
                            STATE["trace_id"],
                            css_class="text-xs font-mono text-primary/70",
                        )
            Separator()

        # ── Actions ─────────────────────────────────────────────────────────
        with If(anchored_rx.map(lambda x: not x)):
            with Column(gap=4):
                Alert(
                    title="F1 Amanah — Irreversible",
                    description=(
                        "Session anchoring is a commitment. Once sealed, this session cannot be undone."
                    ),
                    variant="warning",
                )

                Button(
                    "Anchor Constitutional Session",
                    on_click=on_anchor,
                    variant="default",
                    css_class="w-full h-12 font-bold",
                )

        # ── Philosophy Footer (CHANGE-05) ─────────────────────────────────
        Muted(
            STATE["philosophy"],
            css_class="text-xs italic text-center text-muted-foreground/50",
        )

        # ── Sovereign Footer (CHANGE-06) ──────────────────────────────────
        with Column(gap=1, align="center", css_class="mt-4"):
            Muted(
                "Human architect retains sovereign veto. F13 is always alive.",
                css_class="text-[10px] uppercase tracking-widest font-bold text-primary/40",
            )
            Muted(
                "arifOS Metabolic Monitor · DITEMPA BUKAN DIBERI",
                css_class="text-[9px] text-muted-foreground/60",
            )

    return PrefabApp(view=view, state=initial_state)


def _register(mcp: FastMCP) -> None:
    """Mount InitApp onto the platform FastMCP server."""
    mcp.add_provider(init_app)
