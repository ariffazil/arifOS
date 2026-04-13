"""
arifosmcp/apps/judge_app.py
═══════════════════════════════════════════════════════════════════════════════
arifOS JudgeApp — FastMCP Constitutional Verdict Surface (888_JUDGE)
═══════════════════════════════════════════════════════════════════════════════

Implements the constitutional verdict surface as a FastMCPApp:

  @app.ui()  judge_surface     — entry point; renders full verdict UI
  @app.tool() execute_judge    — backend; calls arifos_judge, returns structured data

UI anatomy:
  ┌── Header: candidate action + risk tier ────────────────────────┐
  │  ┌── Floor Grid (F1–F13) — PASS/FAIL per floor ─────────────┐ │
  │  │  F1 Amanah         ●  PASS                                │ │
  │  │  F2 Truth          ●  PASS                                │ │
  │  │  ...                                                      │ │
  │  └───────────────────────────────────────────────────────────┘ │
  │  ┌── W³ Tri-Witness ──────────────────────────────────────────┐ │
  │  │  Human: 1.00  |  AI: 0.95  |  Earth: 0.91               │ │
  │  └───────────────────────────────────────────────────────────┘ │
  │  Verdict: ● SEAL                                               │
  │  Philosophy: "Ditempa bukan diberi..."                         │
  │  [Run Judge]   [Request 888_HOLD Approval]                     │
  └────────────────────────────────────────────────────────────────┘

F13 Sovereign — human SEAL/REJECT always required before forge executes.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

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
    Muted,
    Row,
    Separator,
    Text,
)
from prefab_ui.rx import RESULT

from fastmcp import FastMCP, FastMCPApp

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

_FLOOR_ORDER = ["F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12","F13"]

_FLOOR_TYPE: dict[str, str] = {
    "F1": "hard", "F2": "hard", "F3": "mirror",
    "F4": "hard", "F5": "soft", "F6": "soft",
    "F7": "hard", "F8": "mirror", "F9": "hard",
    "F10": "wall", "F11": "wall", "F12": "wall",
    "F13": "veto",
}

# ── Philosophy quotes by verdict band ─────────────────────────────────────────
_PHILOSOPHY: dict[str, str] = {
    "SEAL":     "Ditempa bukan diberi. The forge makes truth; truth makes the seal.",
    "PARTIAL":  "Sabar — the floor strains but does not break. Adjust, then proceed.",
    "VOID":     "VOID: the action cannot pass. Repair the floor before the gate opens.",
    "888_HOLD": "888_HOLD: human authority required. No machine may cross this line alone.",
    "SABAR":    "SABAR — stop, acknowledge, breathe, adjust, resume. The floor protects.",
    "pending":  "Awaiting constitutional evaluation…",
}

# ── Variant helpers ───────────────────────────────────────────────────────────

def _verdict_variant(verdict: str) -> str:
    return {
        "SEAL": "success",
        "PARTIAL": "warning",
        "VOID": "destructive",
        "888_HOLD": "warning",
        "SABAR": "secondary",
    }.get(verdict, "secondary")


def _floor_variant(fid: str, failed: list[str]) -> str:
    ftype = _FLOOR_TYPE.get(fid, "hard")
    if fid in failed:
        return "destructive"
    if ftype == "wall":
        return "success"
    if ftype == "veto":
        return "success"
    return "success"


def _floor_label(fid: str, failed: list[str]) -> str:
    if fid in failed:
        ftype = _FLOOR_TYPE.get(fid, "hard")
        return "BREACH" if ftype in ("wall", "veto") else "FAIL"
    return "PASS"


# ── App definition ────────────────────────────────────────────────────────────

judge_app = FastMCPApp("JudgeApp")


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
        w3 = {
            "human": float(telemetry.get("witness_human", 1.0)),
            "ai":    float(telemetry.get("witness_ai", 0.95)),
            "earth": float(telemetry.get("witness_earth", 0.91)),
        }

        return {
            "verdict": verdict,
            "floors_checked": floors_checked,
            "floors_failed": floors_failed,
            "w3": w3,
            "requires_human": env_dict.get("requires_human", False),
            "sabar_step": env_dict.get("sabar_step"),
            "trace_id": env_dict.get("trace_id"),
        }

    except Exception as exc:
        return {
            "verdict": "VOID",
            "floors_checked": [],
            "floors_failed": list(_FLOOR_NAMES.keys()),
            "w3": {"human": 0.0, "ai": 0.0, "earth": 0.0},
            "requires_human": True,
            "sabar_step": f"Judge unavailable: {exc}",
            "trace_id": None,
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
    initial_state: dict[str, Any] = {
        "verdict": "pending",
        "floors_checked": [],
        "floors_failed": [],
        "w3": {"human": 0.0, "ai": 0.0, "earth": 0.0},
        "requires_human": False,
        "sabar_step": None,
        "judged": False,
        "candidate": candidate_action,
        "risk_tier": risk_tier,
    }

    on_judge = CallTool(
        execute_judge,
        args={"candidate_action": candidate_action, "risk_tier": risk_tier},
        on_success=[
            SetState("verdict",        RESULT["verdict"]),
            SetState("floors_checked", RESULT["floors_checked"]),
            SetState("floors_failed",  RESULT["floors_failed"]),
            SetState("w3",             RESULT["w3"]),
            SetState("requires_human", RESULT["requires_human"]),
            SetState("sabar_step",     RESULT["sabar_step"]),
            SetState("judged",         True),
            ShowToast("Judgment complete", variant="success"),
        ],
        on_error=ShowToast("Judge tool error", variant="destructive"),
    )

    with Column(gap=5, css_class="p-5 max-w-2xl") as view:

        # ── Header ──────────────────────────────────────────────────────────
        with Row(gap=3, align="center"):
            Heading("888 Constitutional Judge")
            Badge("F13 Sovereign", variant="secondary", css_class="font-mono text-xs")

        with Card(css_class="bg-muted/40"):
            with CardContent(css_class="py-3"):
                Text(f'Action: "{candidate_action}"', css_class="text-sm font-medium truncate")
                Muted(f"Risk tier: {risk_tier.upper()} · dry_run=True")

        Separator()

        # ── Floor Grid ──────────────────────────────────────────────────────
        Muted("F1–F13 Constitutional Chain", css_class="text-xs uppercase tracking-wider")
        with Column(gap=1):
            for fid in _FLOOR_ORDER:
                fname = _FLOOR_NAMES[fid]
                ftype = _FLOOR_TYPE[fid]
                with Card(css_class="border-l-2"):
                    with CardContent(css_class="py-2 px-3"):
                        with Row(gap=2, align="center"):
                            Text(fid, css_class="font-mono text-xs font-bold w-8 text-muted-foreground")
                            Text(fname, css_class="text-sm w-28")
                            Badge(
                                ftype.upper(),
                                variant="outline",
                                css_class="text-xs w-14 text-center font-mono",
                            )
                            # Static placeholder — updates reactively after judge runs
                            Badge("—", variant="secondary", css_class="ml-auto w-14 text-center")

        Separator()

        # ── W³ Tri-Witness ──────────────────────────────────────────────────
        Muted("W³ Tri-Witness (F3)", css_class="text-xs uppercase tracking-wider")
        with Grid(columns=3, gap=3):
            for label, key in [("Human", "human"), ("AI", "ai"), ("Earth", "earth")]:
                with Card():
                    with CardContent(css_class="py-3 text-center"):
                        Text("—", css_class="text-xl font-bold font-mono")
                        Muted(label)

        Separator()

        # ── Verdict ─────────────────────────────────────────────────────────
        with Row(gap=3, align="center"):
            Text("Verdict:", css_class="text-sm font-semibold")
            Badge("PENDING", variant="secondary", css_class="font-mono")

        # Philosophy
        Muted(
            _PHILOSOPHY["pending"],
            css_class="text-xs italic border-l-2 pl-3 border-muted-foreground/30",
        )

        Separator()

        # ── Actions ─────────────────────────────────────────────────────────
        Alert(
            title="F13 Sovereign",
            description="Human confirmation required before any forge execution.",
            variant="warning",
        )
        with Row(gap=3):
            Button(
                "Run Judge",
                on_click=on_judge,
                variant="default",
            )
            Muted(
                "Then use request_approval for forge gate",
                css_class="text-xs self-center",
            )

        Separator()
        Muted(
            "arifOS · DITEMPA BUKAN DIBERI · dry_run=True until human SEAL",
            css_class="text-xs text-center",
        )

    return PrefabApp(view=view, state=initial_state)


def _register(mcp: FastMCP) -> None:
    """Mount JudgeApp onto the platform FastMCP server."""
    mcp.add_provider(judge_app)
