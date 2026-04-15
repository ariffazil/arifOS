"""
arifosmcp/apps/init_app.py
═══════════════════════════════════════════════════════════════════════════════
arifOS InitApp — Session Anchoring Surface (000_INIT)
═══════════════════════════════════════════════════════════════════════════════

Implements the session anchoring surface as a FastMCPApp:

  @app.ui()   init_surface      — entry; shows epoch, intent, mode selector
  @app.tool() anchor_session    — backend; calls arifos_init, returns session data

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
from typing import Any

from fastmcp import FastMCP, FastMCPApp

from arifosmcp.apps.surface_utils import envelope_error, normalize_state

logger = logging.getLogger(__name__)
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


# ── App definition ────────────────────────────────────────────────────────────

init_app = FastMCPApp("InitApp")


@init_app.tool()
async def anchor_session(
    declared_intent: str = "",
    mode: str = "standard",
) -> dict[str, Any]:
    """
    Anchor a new arifOS session. Calls arifos_init with the declared intent
    and returns session metadata including epoch, session_id, and alignment.
    """
    try:
        from arifosmcp.runtime.tools import arifos_init

        envelope = await arifos_init(
            declared_intent=declared_intent or "General session",
        )
        env_dict = envelope.model_dump() if hasattr(envelope, "model_dump") else dict(envelope)

        session_id = env_dict.get("session_id", "—")
        epoch = env_dict.get("epoch", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        omega0 = float(env_dict.get("telemetry", {}).get("omega_0", 0.04))
        aligned = env_dict.get("ok", True)

        # ── Wisdom quote for anchor surface ───────────────────────────────────
        try:
            from arifosmcp.runtime.philosophy import select_wisdom_quote

            _wisdom = select_wisdom_quote("anchor")
        except Exception:
            _wisdom = None

        return {
            "session_id": session_id,
            "epoch": epoch,
            "mode": mode,
            "declared_intent": declared_intent or "General session",
            "omega0": omega0,
            "aligned": aligned,
            "anchored": True,
            "trace_id": env_dict.get("trace_id", "—"),
            "wisdom": _wisdom,
        }

    except Exception as exc:
        logger.warning(f"anchor_session failed: {exc}")
        return envelope_error(
            tool_name="anchor_session",
            stage="000_INIT",
            verdict="VOID",
            detail=f"anchor_session failed: {exc}",
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
            ShowToast("Session anchored — 000_INIT sealed", variant="success"),
        ],
        on_error=ShowToast("Session anchor failed", variant="error"),
    )

    # ── Reactive bindings ────────────────────────────────────────────────────
    anchored_rx = STATE["anchored"]
    aligned_rx = STATE["aligned"]
    omega0_rx = STATE["omega0"]

    with Column(gap=5, css_class="p-5 max-w-2xl") as view:
        # ── Header ──────────────────────────────────────────────────────────
        with Row(gap=3, align="center"):
            Heading("000 Session Anchor")
            Badge(
                "F1 Amanah",
                variant="secondary",
                css_class="font-mono text-xs",
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

        # ── Constitutional Alignment ────────────────────────────────────────
        Muted(
            "Constitutional Alignment",
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
                    Muted("Ω₀ Humility", css_class="mt-1 text-xs")

            # Alignment status
            with Card():
                with CardContent(css_class="py-3 text-center"):
                    Badge(
                        aligned_rx.then("● ALIGNED", "○ UNALIGNED"),
                        variant=aligned_rx.then("success", "destructive"),
                        css_class="font-mono",
                    )
                    Muted("Alignment", css_class="mt-2 text-xs")

            # Session status
            with Card():
                with CardContent(css_class="py-3 text-center"):
                    Badge(
                        anchored_rx.then("ANCHORED", "PENDING"),
                        variant=anchored_rx.then("success", "secondary"),
                        css_class="font-mono",
                    )
                    Muted("Session", css_class="mt-2 text-xs")

        Separator()

        # ── Post-anchor details ─────────────────────────────────────────────
        with If(anchored_rx):
            with Card(css_class="bg-muted/40"):
                with CardContent(css_class="py-3"):
                    with Row(gap=3):
                        Muted("Session ID:", css_class="text-xs")
                        Text(
                            STATE["session_id"],
                            css_class="text-xs font-mono",
                        )
                    with Row(gap=3):
                        Muted("Trace:", css_class="text-xs")
                        Text(
                            STATE["trace_id"],
                            css_class="text-xs font-mono",
                        )

        # ── Actions ─────────────────────────────────────────────────────────
        Alert(
            title="F1 Amanah — Irreversible",
            description=(
                "Session anchoring is a commitment. Once sealed, this session cannot be undone."
            ),
            variant="warning",
        )

        Button(
            "Anchor Session",
            on_click=on_anchor,
            variant="default",
            css_class="w-full",
        )

        Separator()
        Muted(
            "arifOS · 000_INIT · Constitutional Session Anchoring",
            css_class="text-xs text-center",
        )

    return PrefabApp(view=view, state=initial_state)


def _register(mcp: FastMCP) -> None:
    """Mount InitApp onto the platform FastMCP server."""
    mcp.add_provider(init_app)
