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

from typing import Annotated, Any

from fastmcp import FastMCP
from fastmcp.tools import ToolResult
from prefab_ui.actions import SetState, ShowToast
from prefab_ui.actions.mcp import CallTool
from prefab_ui.app import PrefabApp
from prefab_ui.components import (
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
from pydantic import Field

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
    "F9": "Ethics",
    "F10": "Conscience",
    "F11": "Audit",
    "F12": "Injection",
    "F13": "Sovereign",
}

_HUMAN_MEANINGS: dict[str, str] = {
    "F1": "Can this be undone? If FAIL: rollback path missing.",
    "F2": "Is this grounded? If FAIL: claims unverifiable.",
    "F3": "Do theory, law, and intent agree? If FAIL: divergence detected.",
    "F4": "Is this reducing confusion? If FAIL: entropy increasing.",
    "F5": "Is this non-destructive? If FAIL: value or trust at risk.",
    "F6": "Is the human heard? If FAIL: underlying intent may be missed.",
    "F7": "Are uncertainties surfaced? If FAIL: confidence overstated.",
    "F8": "Is systemic health maintained? If FAIL: subsystem under load.",
    "F9": "No manipulation or dark patterns? If FAIL: interaction suspect.",
    "F10": "No consciousness claims? If FAIL: ontology violated.",
    "F11": "Is everything logged? If FAIL: action not traceable.",
    "F12": "Is the prompt safe? If FAIL: override pressure detected.",
    "F13": "Is human veto intact? If FAIL: sovereign authority at risk.",
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

# ── Operator interpretation (CHANGE-01) ───────────────────────────────────────
_VERDICT_INTERPRETATIONS: dict[str, dict[str, str]] = {
    "SEAL": {
        "badge": "SEALED",
        "posture": "All floors passing. Safe for consequential action.",
        "variant": "success",
    },
    "PARTIAL": {
        "badge": "DEGRADED",
        "posture": "Core governance alive. Trust posture degraded. Use for inspection only.",
        "variant": "warning",
    },
    "HOLD": {
        "badge": "HOLD",
        "posture": "Session alive. Identity incomplete. Inspect before proceeding.",
        "variant": "warning",
    },
    "888_HOLD": {
        "badge": "HOLD",
        "posture": "Session alive. Identity incomplete. Inspect before proceeding.",
        "variant": "warning",
    },
    "VOID": {
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

# ── Philosophy quotes by verdict band (CHANGE-05) ─────────────────────────────
_PHILOSOPHY: dict[str, str] = {
    "SEAL": "DITEMPA, BUKAN DIBERI.",
    "G_HIGH": "What gets measured gets managed. — Drucker",
    "G_MID_HIGH": "Build less, build right. — arifOS",
    "G_MID": "Nearly all men can stand adversity... — Lincoln",
    "G_MID_LOW": "The concept of truth cannot be defined within... — Tarski",
    "G_LOW": "The only principle that does not inhibit progress... — Feyerabend",
    "pending": "Awaiting constitutional evaluation...",
}


# ── App definition ────────────────────────────────────────────────────────────

judge_app = FastMCP("JudgeApp")


@judge_app.tool()
async def execute_judge(
    candidate_action: Annotated[str, Field(description="The action or proposal to evaluate")],
    risk_tier: Annotated[str, Field(description="Risk level: low, medium, high, critical")] = "medium",
) -> ToolResult:
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

        # Telemetry & Metrics (CHANGE-03)
        telemetry = env_dict.get("telemetry") or {}
        w3_human = float(telemetry.get("witness_human", 1.0))
        w3_ai = float(telemetry.get("witness_ai", 0.95))
        w3_earth = float(telemetry.get("witness_earth", 0.91))
        
        # Extended metrics
        ds = float(telemetry.get("delta_s", 0.0))
        peace2 = float(telemetry.get("peace2", 1.0))
        kappa_r = float(telemetry.get("kappa_r", 0.97))
        shadow = float(telemetry.get("shadow", 0.05))
        confidence = float(telemetry.get("confidence", 0.85))
        witness_score = float(telemetry.get("witness_score", 0.95))
        g_score = float(telemetry.get("g_score", 0.88))

        # Build floor status list for reactive rendering (CHANGE-02)
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
                "human_meaning": _HUMAN_MEANINGS.get(fid, ""),
                "failed": failed,
            })

        # Philosophy selection (CHANGE-05)
        if verdict == "SEAL":
            philosophy = _PHILOSOPHY["SEAL"]
        else:
            if g_score >= 0.80:
                philosophy = _PHILOSOPHY["G_HIGH"]
            elif g_score >= 0.60:
                philosophy = _PHILOSOPHY["G_MID_HIGH"]
            elif g_score >= 0.40:
                philosophy = _PHILOSOPHY["G_MID"]
            elif g_score >= 0.20:
                philosophy = _PHILOSOPHY["G_MID_LOW"]
            else:
                philosophy = _PHILOSOPHY["G_LOW"]

        # Next actions (CHANGE-04)
        next_actions = []
        if floors_failed:
            if "F4" in floors_failed:
                next_actions.append("Simplify prompt chain. Remove conflicting meta-instructions.")
            if "F1" in floors_failed:
                next_actions.append("Identify and map rollback path before proceeding.")
            if "F7" in floors_failed:
                next_actions.append("Audit recent outputs for unsurfaced uncertainty.")
            if "F12" in floors_failed:
                next_actions.append("Inspect for prompt injection or override-style instructions.")
            if "F2" in floors_failed:
                next_actions.append("Verify claims with external evidence before trusting session output.")
        
        if not next_actions:
            if verdict == "SEAL":
                next_actions.append("Session healthy. Proceed with normal operations. Monitor ΔS.")
            else:
                next_actions.append("Repair floor state or obtain human veto override.")

        return ToolResult(
            content=[
                {
                    "type": "text",
                    "text": f"Judgment complete for action: {candidate_action[:50]}... Verdict: {verdict}",
                },
                {
                    "type": "json",
                    "json": {
                        "verdict": verdict,
                        "floors_checked": floors_checked,
                        "floors_failed": floors_failed,
                        "floor_rows": floor_rows,
                        "w3_human": w3_human,
                        "w3_ai": w3_ai,
                        "w3_earth": w3_earth,
                        "ds": ds,
                        "peace2": peace2,
                        "kappa_r": kappa_r,
                        "shadow": shadow,
                        "confidence": confidence,
                        "witness_score": witness_score,
                        "next_actions": next_actions,
                        "philosophy": philosophy,
                        "requires_human": env_dict.get("requires_human", False),
                        "sabar_step": env_dict.get("sabar_step"),
                        "trace_id": env_dict.get("trace_id"),
                        "floors_pass_count": len(floors_checked) - len(floors_failed),
                        "floors_total_count": len(floors_checked),
                    },
                },
            ]
        )

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
        return ToolResult(
            is_error=True,
            content=[
                {"type": "text", "text": f"Judge unavailable: {exc}"},
                {
                    "type": "json",
                    "json": {
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
                    },
                },
            ],
        )


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
            "human_meaning": _HUMAN_MEANINGS.get(fid, ""),
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
        "ds": 0.0,
        "peace2": 1.0,
        "kappa_r": 0.0,
        "shadow": 0.0,
        "confidence": 0.0,
        "witness_score": 0.0,
        "next_actions": ["Awaiting constitutional evaluation..."],
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
            SetState("ds",                 RESULT["ds"]),
            SetState("peace2",             RESULT["peace2"]),
            SetState("kappa_r",            RESULT["kappa_r"]),
            SetState("shadow",             RESULT["shadow"]),
            SetState("confidence",         RESULT["confidence"]),
            SetState("witness_score",      RESULT["witness_score"]),
            SetState("next_actions",       RESULT["next_actions"]),
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

        # ── Operator Interpretation Banner (CHANGE-01) ────────────────────────
        with Card(css_class="border-2 border-primary/20"):
            with CardContent(css_class="py-4 px-6"):
                with Row(gap=4, align="center"):
                    Badge(
                        STATE["verdict"].map(lambda v: _VERDICT_INTERPRETATIONS.get(v, _VERDICT_INTERPRETATIONS["pending"])["badge"]),
                        variant=STATE["verdict"].map(lambda v: _VERDICT_INTERPRETATIONS.get(v, _VERDICT_INTERPRETATIONS["pending"])["variant"]),
                        css_class="font-mono text-lg py-1 px-3 h-auto",
                    )
                    with Column(gap=0):
                        Heading("arifOS Metabolic Monitor", size="sm")
                        Text(
                            STATE["verdict"].map(lambda v: _VERDICT_INTERPRETATIONS.get(v, _VERDICT_INTERPRETATIONS["pending"])["posture"]),
                            css_class="text-sm font-medium",
                        )

        with Card(css_class="bg-muted/20 border-none"):
            with CardContent(css_class="py-2 px-4"):
                with Row(gap=2, justify="between", align="center"):
                    Text(
                        f'Action: "{candidate_action}"',
                        css_class="text-xs font-mono truncate max-w-[70%]",
                    )
                    Badge(risk_tier.upper(), variant="outline", css_class="text-[10px] h-4")

        Separator()

        # ── Floor Grid (F1-F13) — Reactive via ForEach (CHANGE-02) ───────────
        with Row(justify="between", align="center"):
            Muted(
                "F1–F13 Constitutional Chain",
                css_class="text-xs uppercase tracking-wider",
            )
            with If(judged_rx):
                Badge(
                    f"{STATE['floors_pass_count']} / 13 Floors Passed",
                    variant="outline",
                    css_class="text-[10px]",
                )

        with Column(gap=1):
            with ForEach(floor_rows_rx):
                from prefab_ui.rx import ITEM
                with Card(css_class=ITEM["failed"].then("border-l-4 border-destructive", "border-l-2")):
                    with CardContent(css_class="py-2 px-3"):
                        with Row(gap=4, align="start"):
                            with Column(gap=0, css_class="w-8"):
                                Text(ITEM["id"], css_class="font-mono text-xs font-bold text-muted-foreground")
                            
                            with Column(gap=0, css_class="w-24"):
                                Text(ITEM["name"], css_class="text-sm font-medium")
                                Badge(ITEM["type"], variant="outline", css_class="text-[9px] w-fit font-mono")
                            
                            with Column(gap=0, css_class="flex-1"):
                                Muted(ITEM["human_meaning"], css_class="text-xs italic leading-tight")
                            
                            Badge(
                                ITEM["status"],
                                variant=ITEM["failed"].then("destructive", "success"),
                                css_class="w-16 text-center text-xs",
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

        # ── Telemetry Metrics (CHANGE-03) ────────────────────────────────────
        with If(judged_rx):
            with Column(gap=3):
                Muted("Metabolic Telemetry", css_class="text-xs uppercase tracking-wider")
                with Grid(columns=3, gap=3):
                    with Card():
                        with CardContent(css_class="p-3"):
                            Muted("ΔS Entropy", css_class="text-[10px]")
                            with Row(gap=1, align="center"):
                                Text(STATE["ds"].map(lambda v: f"{v:+.2f}"), css_class="font-mono text-sm font-bold")
                                Badge(
                                    STATE["ds"].map(lambda v: "⚠ high entropy" if v > 0.3 else "stable"),
                                    variant=STATE["ds"].map(lambda v: "destructive" if v > 0.3 else "success"),
                                    css_class="text-[8px] h-3 px-1"
                                )

                    with Card():
                        with CardContent(css_class="p-3"):
                            Muted("Peace² Stability", css_class="text-[10px]")
                            with Row(gap=1, align="center"):
                                Text(STATE["peace2"].map(lambda v: f"{v:.2f}"), css_class="font-mono text-sm font-bold")
                                Badge(
                                    STATE["peace2"].map(lambda v: "⚠ unstable" if v < 1.0 else "stable"),
                                    variant=STATE["peace2"].map(lambda v: "destructive" if v < 1.0 else "success"),
                                    css_class="text-[8px] h-3 px-1"
                                )

                    with Card():
                        with CardContent(css_class="p-3"):
                            Muted("κᵣ Empathy", css_class="text-[10px]")
                            with Row(gap=1, align="center"):
                                Text(STATE["kappa_r"].map(lambda v: f"{v:.2f}"), css_class="font-mono text-sm font-bold")
                                Badge(
                                    STATE["kappa_r"].map(lambda v: "⚠ low empathy" if v < 0.7 else "aligned"),
                                    variant=STATE["kappa_r"].map(lambda v: "warning" if v < 0.7 else "success"),
                                    css_class="text-[8px] h-3 px-1"
                                )

                with Grid(columns=3, gap=3):
                    with Card():
                        with CardContent(css_class="p-3"):
                            Muted("Shadow Pattern", css_class="text-[10px]")
                            with Row(gap=1, align="center"):
                                Text(STATE["shadow"].map(lambda v: f"{v:.2f}"), css_class="font-mono text-sm font-bold")
                                Badge(
                                    STATE["shadow"].map(lambda v: "⚠ manipulation" if v > 0.3 else "clean"),
                                    variant=STATE["shadow"].map(lambda v: "destructive" if v > 0.3 else "success"),
                                    css_class="text-[8px] h-3 px-1"
                                )

                    with Card():
                        with CardContent(css_class="p-3"):
                            Muted("Constitutional Conf.", css_class="text-[10px]")
                            with Row(gap=1, align="center"):
                                Text(STATE["confidence"].map(lambda v: f"{v:.2f}"), css_class="font-mono text-sm font-bold")
                                Badge(
                                    STATE["confidence"].map(lambda v: "⚠ low conf" if v < 0.5 else "solid"),
                                    variant=STATE["confidence"].map(lambda v: "warning" if v < 0.5 else "success"),
                                    css_class="text-[8px] h-3 px-1"
                                )

                    with Card():
                        with CardContent(css_class="p-3"):
                            Muted("Witness Alignment", css_class="text-[10px]")
                            with Row(gap=1, align="center"):
                                Text(STATE["witness_score"].map(lambda v: f"{v:.2f}"), css_class="font-mono text-sm font-bold")
                                Badge(
                                    STATE["witness_score"].map(lambda v: "⚠ divergence" if v < 0.9 else "aligned"),
                                    variant=STATE["witness_score"].map(lambda v: "destructive" if v < 0.9 else "success"),
                                    css_class="text-[8px] h-3 px-1"
                                )

        Separator()

        # ── Recommended Next Actions (CHANGE-04) ────────────────────────────
        with If(judged_rx):
            with Column(gap=3):
                Muted("Recommended Operator Actions", css_class="text-xs uppercase tracking-wider")
                with Card(css_class="bg-primary/5"):
                    with CardContent(css_class="py-4"):
                        with ForEach(STATE["next_actions"]):
                            from prefab_ui.rx import ITEM as ACTION
                            with Row(gap=3, align="center", css_class="py-1"):
                                Badge("ACTION", variant="secondary", css_class="text-[9px] h-4 font-bold")
                                Text(ACTION, css_class="text-sm font-medium")
            Separator()

        # ── Philosophy (Reactive) ────────────────────────────────────────────
        Muted(
            philosophy_rx,
            css_class="text-xs italic border-l-2 pl-3 border-muted-foreground/30",
        )

        Separator()

        # ── Actions ─────────────────────────────────────────────────────────
        with Row(gap=3, align="center"):
            Button(
                "Run Constitutional Judge",
                on_click=on_judge,
                variant="default",
                css_class="w-full h-10 font-bold",
            )
        
        Muted(
            "dry_run=True until human SEAL. 888_HOLD is a feature, not a bug.",
            css_class="text-[10px] text-center",
        )

        Separator()
        
        # ── Sovereign Footer (CHANGE-06) ────────────────────────────────────
        with Column(gap=1, align="center"):
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
    """Mount JudgeApp onto the platform FastMCP server."""
    mcp.add_provider(judge_app)
