"""
arifosmcp/apps/judge_app.py
═══════════════════════════════════════════════════════════════════════════════
arifOS JudgeApp — FastMCP Constitutional Verdict Surface (888_JUDGE)
═══════════════════════════════════════════════════════════════════════════════

Implements the constitutional verdict surface as a FastMCPApp:

  @app.ui()  judge_surface     — entry point; renders full verdict UI
  @app.tool() execute_judge    — backend; calls arifos_judge, returns structured data

UI anatomy (REACTIVE — all badges/values update after judge runs):
  ┌── Header: candidate action + risk tier ────────────────────────┐
  │  ┌── Floor Grid (F1–F13) — PASS/FAIL per floor (Rx-driven) ──┐ │
  │  │  F1 Amanah         ●  PASS / FAIL / BREACH                 │ │
  │  │  F2 Truth          ●  PASS                                  │ │
  │  │  ...                                                        │ │
  │  └────────────────────────────────────────────────────────────┘ │
  │  ┌── W³ Tri-Witness (Ring gauges) ────────────────────────────┐ │
  │  │  Human: 1.00  |  AI: 0.95  |  Earth: 0.91                 │ │
  │  └────────────────────────────────────────────────────────────┘ │
  │  Verdict: ● SEAL (Rx-driven badge)                              │
  │  Philosophy: "Ditempa bukan diberi..." (Rx-driven from G★ band) │
  │  [Run Judge]                                                     │
  └──────────────────────────────────────────────────────────────────┘

F13 Sovereign — human SEAL/REJECT always required before forge executes.

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
    ForEach,
    Grid,
    Heading,
    If,
    Muted,
    Ring,
    Row,
    Separator,
    Text,
)
from prefab_ui.rx import RESULT, STATE

# ── Constitutional floor registry ─────────────────────────────────────────────
_FLOOR_NAMES: dict[str, str] = {
    "F1": "Amanah",
    "F2": "Truth",
    "F3": "Tri-Witness",
    "F4": "ΔS Clarity",
    "F5": "Peace²",
    "F6": "κᵣ Empathy",
    "F7": "Ω₀ Humility",
    "F8": "G Genius",
    "F9": "Anti-Hantu",
    "F10": "Ontology",
    "F11": "Cmd Auth",
    "F12": "Injection",
    "F13": "Sovereign",
}

_FLOOR_ORDER = [
    "F1", "F2", "F3", "F4", "F5", "F6", "F7",
    "F8", "F9", "F10", "F11", "F12", "F13",
]

_FLOOR_TYPE: dict[str, str] = {
    "F1": "hard", "F2": "hard", "F3": "mirror",
    "F4": "hard", "F5": "soft", "F6": "soft",
    "F7": "hard", "F8": "mirror", "F9": "hard",
    "F10": "wall", "F11": "wall", "F12": "wall",
    "F13": "veto",
}

# ── Philosophy quotes by verdict band ─────────────────────────────────────────
_PHILOSOPHY: dict[str, str] = {
    "SEAL": "Ditempa bukan diberi. The forge makes truth; truth makes the seal.",
    "PARTIAL": "Sabar — the floor strains but does not break. Adjust, then proceed.",
    "VOID": "VOID: the action cannot pass. Repair the floor before the gate opens.",
    "888_HOLD": "888_HOLD: human authority required. No machine may cross this line alone.",
    "SABAR": "SABAR — stop, acknowledge, breathe, adjust, resume. The floor protects.",
    "pending": "Awaiting constitutional evaluation…",
}


# ── App definition ────────────────────────────────────────────────────────────

judge_app = FastMCP("JudgeApp", domain="arifos.fastmcp.app")


@judge_app.tool()
async def execute_judge(
    candidate_action: str,
    risk_tier: str = "medium",
) -> dict[str, Any]:
    """
    Run constitutional verdict evaluation on a candidate action.
    Returns structured Floor results, W³ witness scores, and verdict.
    """
    try:
        from arifosmcp.runtime.tools import arifos_judge
        envelope = await arifos_judge(
            candidate_action=candidate_action,
            risk_tier=risk_tier,
            dry_run=True,
        )
        env_dict = envelope.model_dump() if hasattr(envelope, "model_dump") else dict(envelope)

        policy = env_dict.get("policy") or {}
        floors_checked: list[str] = policy.get("floors_checked", list(_FLOOR_NAMES.keys()))
        floors_failed: list[str] = policy.get("floors_failed", [])
        verdict: str = env_dict.get("verdict") or ("SEAL" if env_dict.get("ok") else "VOID")

        # W³ — try telemetry, fall back to policy fields
        telemetry = env_dict.get("telemetry") or {}
        w3_human = float(telemetry.get("witness_human", 1.0))
        w3_ai = float(telemetry.get("witness_ai", 0.95))
        w3_earth = float(telemetry.get("witness_earth", 0.91))

        # Build floor status list for reactive rendering
        floor_rows = []
        for fid in _FLOOR_ORDER:
            failed = fid in floors_failed
            ftype = _FLOOR_TYPE.get(fid, "hard")
            if failed:
                status_label = "BREACH" if ftype in ("wall", "veto") else "FAIL"
            else:
                status_label = "PASS"
            floor_rows.append({
                "id": fid,
                "name": _FLOOR_NAMES[fid],
                "type": ftype.upper(),
                "status": status_label,
                "failed": failed,
            })

        # Philosophy selection
        philosophy = _PHILOSOPHY.get(verdict, _PHILOSOPHY["pending"])

        return {
            "verdict": verdict,
            "floors_checked": floors_checked,
            "floors_failed": floors_failed,
            "floor_rows": floor_rows,
            "w3_human": w3_human,
            "w3_ai": w3_ai,
            "w3_earth": w3_earth,
            "philosophy": philosophy,
            "requires_human": env_dict.get("requires_human", False),
            "sabar_step": env_dict.get("sabar_step"),
            "trace_id": env_dict.get("trace_id"),
            "floors_pass_count": len(floors_checked) - len(floors_failed),
            "floors_total_count": len(floors_checked),
        }

    except Exception as exc:
        # Build fallback floor rows with all failed
        floor_rows = [
            {
                "id": fid,
                "name": _FLOOR_NAMES[fid],
                "type": _FLOOR_TYPE.get(fid, "hard").upper(),
                "status": "FAIL",
                "failed": True,
            }
            for fid in _FLOOR_ORDER
        ]
        return {
            "verdict": "VOID",
            "floors_checked": [],
            "floors_failed": list(_FLOOR_NAMES.keys()),
            "floor_rows": floor_rows,
            "w3_human": 0.0,
            "w3_ai": 0.0,
            "w3_earth": 0.0,
            "philosophy": f"Judge unavailable: {exc}",
            "requires_human": True,
            "sabar_step": f"Judge unavailable: {exc}",
            "trace_id": None,
            "floors_pass_count": 0,
            "floors_total_count": 13,
        }


@judge_app.ui(title="888 Constitutional Judge")
def judge_surface(
    candidate_action: str = "describe the action to evaluate",
    risk_tier: str = "medium",
) -> PrefabApp:
    """
    Open the arifOS Constitutional Verdict Surface.
    Evaluates a candidate action against all 13 constitutional floors.
    Human SEAL or REJECT required before any forge execution (F13 Sovereign).
    """

    # ── Default floor rows for initial render ────────────────────────────────
    default_floor_rows = [
        {
            "id": fid,
            "name": _FLOOR_NAMES[fid],
            "type": _FLOOR_TYPE.get(fid, "hard").upper(),
            "status": "—",
            "failed": False,
        }
        for fid in _FLOOR_ORDER
    ]

    initial_state: dict[str, Any] = {
        "verdict": "pending",
        "floors_checked": [],
        "floors_failed": [],
        "floor_rows": default_floor_rows,
        "w3_human": 0.0,
        "w3_ai": 0.0,
        "w3_earth": 0.0,
        "philosophy": _PHILOSOPHY["pending"],
        "requires_human": False,
        "sabar_step": None,
        "judged": False,
        "candidate": candidate_action,
        "risk_tier": risk_tier,
        "floors_pass_count": 0,
        "floors_total_count": 13,
    }

    on_judge = CallTool(
        execute_judge,
        args={"candidate_action": candidate_action, "risk_tier": risk_tier},
        on_success=[
            SetState("verdict",            RESULT["verdict"]),
            SetState("floors_checked",     RESULT["floors_checked"]),
            SetState("floors_failed",      RESULT["floors_failed"]),
            SetState("floor_rows",         RESULT["floor_rows"]),
            SetState("w3_human",           RESULT["w3_human"]),
            SetState("w3_ai",              RESULT["w3_ai"]),
            SetState("w3_earth",           RESULT["w3_earth"]),
            SetState("philosophy",         RESULT["philosophy"]),
            SetState("requires_human",     RESULT["requires_human"]),
            SetState("sabar_step",         RESULT["sabar_step"]),
            SetState("floors_pass_count",  RESULT["floors_pass_count"]),
            SetState("floors_total_count", RESULT["floors_total_count"]),
            SetState("judged",             True),
            ShowToast("Constitutional judgment complete", variant="success"),
        ],
        on_error=ShowToast("Judge tool error — 888_HOLD", variant="destructive"),
    )

    # ── Reactive state references ────────────────────────────────────────────
    verdict_rx = STATE["verdict"]
    philosophy_rx = STATE["philosophy"]
    w3_human_rx = STATE["w3_human"]
    w3_ai_rx = STATE["w3_ai"]
    w3_earth_rx = STATE["w3_earth"]
    floor_rows_rx = STATE["floor_rows"]
    judged_rx = STATE["judged"]

    with Column(gap=5, css_class="p-5 max-w-2xl") as view:

        # ── Header ──────────────────────────────────────────────────────────
        with Row(gap=3, align="center"):
            Heading("888 Constitutional Judge")
            Badge("F13 Sovereign", variant="secondary", css_class="font-mono text-xs")

        with Card(css_class="bg-muted/40"):
            with CardContent(css_class="py-3"):
                Text(
                    f'Action: "{candidate_action}"',
                    css_class="text-sm font-medium truncate",
                )
                Muted(f"Risk tier: {risk_tier.upper()} · dry_run=True")

        Separator()

        # ── Floor Grid (F1-F13) — Reactive via ForEach ───────────────────────
        Muted(
            "F1–F13 Constitutional Chain",
            css_class="text-xs uppercase tracking-wider",
        )

        with Column(gap=1):
            with ForEach(floor_rows_rx):
                from prefab_ui.rx import ITEM
                with Card(css_class="border-l-2"):
                    with CardContent(css_class="py-2 px-3"):
                        with Row(gap=2, align="center"):
                            Text(
                                ITEM["id"],
                                css_class="font-mono text-xs font-bold w-8 "
                                          "text-muted-foreground",
                            )
                            Text(ITEM["name"], css_class="text-sm w-28")
                            Badge(
                                ITEM["type"],
                                variant="outline",
                                css_class="text-xs w-14 text-center font-mono",
                            )
                            # Reactive status badge — updates from RESULT
                            Badge(
                                ITEM["status"],
                                variant=ITEM["failed"].then(
                                    "destructive", "success"
                                ),
                                css_class="ml-auto w-16 text-center",
                            )

        Separator()

        # ── W³ Tri-Witness (Ring Gauges) ─────────────────────────────────────
        Muted("W³ Tri-Witness (F3)", css_class="text-xs uppercase tracking-wider")
        with Grid(columns=3, gap=3):
            # Human witness
            with Card():
                with CardContent(css_class="py-3 flex flex-col items-center"):
                    Ring(
                        value=w3_human_rx * 100,
                        label=w3_human_rx,
                        variant=w3_human_rx.then("success", "destructive"),
                        size="sm",
                    )
                    Muted("Human", css_class="mt-1")

            # AI witness
            with Card():
                with CardContent(css_class="py-3 flex flex-col items-center"):
                    Ring(
                        value=w3_ai_rx * 100,
                        label=w3_ai_rx,
                        variant=w3_ai_rx.then("success", "destructive"),
                        size="sm",
                    )
                    Muted("AI", css_class="mt-1")

            # Earth witness
            with Card():
                with CardContent(css_class="py-3 flex flex-col items-center"):
                    Ring(
                        value=w3_earth_rx * 100,
                        label=w3_earth_rx,
                        variant=w3_earth_rx.then("success", "destructive"),
                        size="sm",
                    )
                    Muted("Earth", css_class="mt-1")

        Separator()

        # ── Verdict (Reactive) ───────────────────────────────────────────────
        with Row(gap=3, align="center"):
            Text("Verdict:", css_class="text-sm font-semibold")
            Badge(
                verdict_rx.upper(),
                variant=verdict_rx.then("success", "secondary"),
                css_class="font-mono text-sm",
            )

        # ── Floor Summary Metric ─────────────────────────────────────────────
        with If(judged_rx):
            with Row(gap=3):
                # Using a generic Text instead of Metric if Metric was causing issues,
                # but let's try to keep it if it's there.
                Text(
                    "Floors Passed: ",
                    css_class="text-sm font-semibold",
                )
                Badge(
                    STATE["floors_pass_count"].then(
                        STATE["floors_pass_count"], "0"
                    ),
                    variant="outline",
                )
                Text(" / 13", css_class="text-sm")

        # ── Philosophy (Reactive) ────────────────────────────────────────────
        Muted(
            philosophy_rx,
            css_class="text-xs italic border-l-2 pl-3 border-muted-foreground/30",
        )

        Separator()

        # ── Actions ─────────────────────────────────────────────────────────
        Alert(
            title="F13 Sovereign Gate",
            description=(
                "Human confirmation required before any forge execution. "
                "888_HOLD is a feature, not a bug."
            ),
            variant="warning",
        )
        with Row(gap=3):
            Button(
                "Run Judge",
                on_click=on_judge,
                variant="default",
            )
            Muted(
                "dry_run=True until human SEAL",
                css_class="text-xs self-center",
            )

        Separator()
        Muted(
            "arifOS · DITEMPA BUKAN DIBERI · Constitutional AGI Governance",
            css_class="text-xs text-center",
        )

    return PrefabApp(view=view, state=initial_state)


def _register(mcp: FastMCP) -> None:
    """Mount JudgeApp onto the platform FastMCP server."""
    mcp.add_provider(judge_app)
