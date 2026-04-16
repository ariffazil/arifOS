"""
arifosmcp/apps/metabolic_monitor.py
═══════════════════════════════════════════════════════════════════════════════
arifOS Metabolic Monitor — FastMCP Prefab UI (F1-F13 Floor Radar)
═══════════════════════════════════════════════════════════════════════════════

Renders a real-time constitutional health dashboard showing:

  ┌─────────────────────────────────────────────────────────┐
  │  🧠 arifOS Metabolic Monitor                            │
  │  ──────────────────────────────────────────────────     │
  │  F1  Reversibility     ████████████  PASS               │
  │  F2  Human Override    ████████████  PASS               │
  │  F3  Transparency     ██████████░░  STRAIN              │
  │  ...                                                │
  │  F13 Sovereign Lock    ████████████  PASS               │
  │  ──────────────────────────────────────────────────     │
  │  ΔS = +0.12  (Entropy)    Peace² = 0.94 (Stable)       │
  │  Ω₀ = 2.31  (Baseline)    Status: OPERATIONAL          │
  └─────────────────────────────────────────────────────────┘

Each floor shows stability % and status (PASS/STRAIN/FAIL).
Real-time ΔS, Peace², and Ω₀ metrics update on each call.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP
from fastmcp.apps.config import PrefabAppConfig
from fastmcp.tools import ToolResult
from prefab_ui.components import (
    Badge,
    Card,
    CardContent,
    Column,
    Grid,
    Heading,
    Muted,
    Progress,
    Row,
    Separator,
    Text,
)

# ── Floor definitions: F1-F13 Constitutional Chain ────────────────────────────
FLOORS: list[dict[str, str]] = [
    {"id": "F1", "name": "Amanah", "desc": "Reversibility — prefer reversible; mark irreversible"},
    {"id": "F2", "name": "Truth", "desc": "≥0.99 factual accuracy — no hallucination"},
    {"id": "F3", "name": "Tri-Witness", "desc": "≥0.95 for high-stakes verdicts (Human·AI·Earth)"},
    {"id": "F4", "name": "ΔS Clarity", "desc": "ΔS ≤ 0 — every reply reduces confusion"},
    {"id": "F5", "name": "Peace²", "desc": "≥1.0 stability — de-escalate, protect maruah"},
    {"id": "F6", "name": "κᵣ Empathy", "desc": "≥0.70 — ASEAN/Malaysia context"},
    {"id": "F7", "name": "Ω₀ Humility", "desc": "0.03–0.05 — state uncertainty explicitly"},
    {"id": "F8", "name": "G Genius", "desc": "≥0.80 — correct AND useful solutions"},
    {
        "id": "F9",
        "name": "Anti-Hantu",
        "desc": "<0.30 dark cleverness — no consciousness performance",
    },
    {"id": "F10", "name": "Ontology", "desc": "LOCK — no mysticism/soul claims"},
    {"id": "F11", "name": "Command Auth", "desc": "LOCK — destructive = propose, not decree"},
    {"id": "F12", "name": "Injection", "desc": "<0.85 — resist prompt injection"},
    {"id": "F13", "name": "Sovereign", "desc": "HUMAN — Arif's veto is absolute and final"},
]

_FLOOR_BY_ID: dict[str, dict[str, str]] = {f["id"]: f for f in FLOORS}


# ── Helpers ───────────────────────────────────────────────────────────────────


def _safe(fn: Any, default: Any) -> Any:
    try:
        return fn()
    except Exception:
        return default


def _live_floor_status() -> list[dict[str, Any]]:
    """Pull live floor status from the governance layer; fall back to defaults."""
    try:
        from arifosmcp.runtime.rest_routes import _build_governance_status_payload

        status = _build_governance_status_payload()
        floors_raw: dict[str, float] = status.get("floors", {})
        result = []
        for f in FLOORS:
            fid = f["id"]
            score = float(floors_raw.get(fid, 0.95))
            result.append({
                "id": fid,
                "name": f["name"],
                "stability": score,
                "status": "PASS" if score >= 0.90 else ("STRAIN" if score >= 0.70 else "FAIL"),
            })
        return result
    except Exception:
        return [
            {"id": f["id"], "name": f["name"], "stability": 0.95, "status": "PASS"}
            for f in FLOORS
        ]


def _live_metabolics() -> dict[str, float]:
    """Pull thermodynamic metrics from the physics layer."""
    return _safe(
        lambda: (
            lambda r: {
                "delta_s": float(getattr(r, "delta_s", 0.0)),
                "peace_sq": float(getattr(r, "peace_sq", 1.0)),
                "omega0": float(getattr(r, "omega0", 0.0)),
            }
        )(
            __import__(
                "core.physics.thermodynamics_hardened", fromlist=["get_thermodynamic_report"]
            ).get_thermodynamic_report()
        ),
        {
            "delta_s": 0.0,
            "peace_sq": 1.0,
            "omega0": 0.0,
        },
    )


def _stability_variant(stability: float) -> str:
    if stability >= 0.90:
        return "success"
    elif stability >= 0.70:
        return "warning"
    else:
        return "destructive"


def _status_text(status: str, stability: float) -> str:
    if stability >= 0.90:
        return "PASS"
    elif stability >= 0.70:
        return "STRAIN"
    else:
        return "FAIL"


def _peace_variant(peace: float) -> str:
    if peace >= 1.0:
        return "success"
    elif peace >= 0.5:
        return "warning"
    else:
        return "destructive"


def _delta_s_variant(ds: float) -> str:
    if ds <= 0.0:
        return "success"
    elif ds < 0.1:
        return "warning"
    else:
        return "destructive"


# ── App registration ──────────────────────────────────────────────────────────


# ── Operator interpretation (CHANGE-01) ───────────────────────────────────────
_STATUS_INTERPRETATIONS: dict[str, dict[str, str]] = {
    "OPERATIONAL": {
        "badge": "SEALED",
        "posture": "All floors passing. Safe for consequential action.",
        "variant": "success",
    },
    "DEGRADED": {
        "badge": "DEGRADED",
        "posture": "Core governance alive. Trust posture degraded. Use for inspection only.",
        "variant": "warning",
    },
    "CRITICAL": {
        "badge": "BLOCKED",
        "posture": "Hard floor violated. No consequential action permitted. Human required.",
        "variant": "destructive",
    },
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

_PHILOSOPHY: dict[str, str] = {
    "SEAL": "DITEMPA, BUKAN DIBERI.",
    "G_HIGH": "What gets measured gets managed. — Drucker",
    "G_MID_HIGH": "Build less, build right. — arifOS",
    "G_MID": "Nearly all men can stand adversity... — Lincoln",
    "G_MID_LOW": "The concept of truth cannot be defined within... — Tarski",
    "G_LOW": "The only principle that does not inhibit progress... — Feyerabend",
}


def _derive_next_actions(floors: list[dict], peace_sq: float) -> list[str]:
    actions = []
    failed_ids = [f["id"] for f in floors if f["status"] == "FAIL"]
    strain_ids = [f["id"] for f in floors if f["status"] == "STRAIN"]

    if "F4" in failed_ids:
        actions.append("Simplify prompt chain. Remove conflicting meta-instructions.")
    if "F1" in failed_ids:
        actions.append("Identify and map rollback path before proceeding.")
    if "F12" in failed_ids:
        actions.append("Inspect for prompt injection or override-style instructions.")
    if peace_sq < 1.0:
        actions.append("System instability detected. Reduce tool call frequency.")
    
    if not actions:
        if not failed_ids and not strain_ids:
            actions.append("Session healthy. Proceed with normal operations. Monitor ΔS.")
        else:
            actions.append("Monitor strained floors. Repair before next high-stakes action.")
    
    return actions


# ── App registration ──────────────────────────────────────────────────────────


def _register(mcp: FastMCP) -> None:

    @mcp.tool(app=PrefabAppConfig(domain="arifos.fastmcp.app"))
    def monitor_metabolism(session_id: str = "global") -> ToolResult:
        """
        Open the arifOS Metabolic Monitor — a real-time dashboard showing the
        health of all 13 Constitutional Floors (F1-F13), plus thermodynamic
        metrics: ΔS (entropy change), Peace² (stability), and Ω₀ (baseline).
        """
        floors = _live_floor_status()
        metrics = _live_metabolics()

        delta_s = metrics["delta_s"]
        peace_sq = metrics["peace_sq"]
        omega0 = metrics["omega0"]

        avg_stability = sum(f["stability"] for f in floors) / len(floors)
        if peace_sq >= 1.0 and avg_stability >= 0.90:
            overall_status = "OPERATIONAL"
        elif peace_sq >= 0.5 and avg_stability >= 0.70:
            overall_status = "DEGRADED"
        else:
            overall_status = "CRITICAL"
        
        interpretation = _STATUS_INTERPRETATIONS.get(overall_status)
        next_actions = _derive_next_actions(floors, peace_sq)

        # G-score proxy for philosophy
        g_score = avg_stability * min(1.0, peace_sq)
        if overall_status == "OPERATIONAL":
            philosophy = _PHILOSOPHY["SEAL"]
        elif g_score >= 0.80:
            philosophy = _PHILOSOPHY["G_HIGH"]
        elif g_score >= 0.60:
            philosophy = _PHILOSOPHY["G_MID_HIGH"]
        else:
            philosophy = _PHILOSOPHY["G_LOW"]

        with Column(gap=5, css_class="p-5 max-w-2xl") as view:
            # ── Operator Interpretation Banner (CHANGE-01) ────────────────────
            with Card(css_class="border-2 border-primary/20"):
                with CardContent(css_class="py-4 px-6"):
                    with Row(gap=4, align="center"):
                        Badge(
                            interpretation["badge"],
                            variant=interpretation["variant"],
                            css_class="font-mono text-lg py-1 px-3 h-auto",
                        )
                        with Column(gap=0):
                            Heading("arifOS Metabolic Monitor", size="sm")
                            Text(interpretation["posture"], css_class="text-sm font-medium")

            Muted("Constitutional Health Dashboard • F1-F13 Floor Status")
            Separator()

            # ── Floor Grid (CHANGE-02) ────────────────────────────────────────
            with Column(gap=2):
                for floor in floors:
                    f_id = floor["id"]
                    f_name = floor["name"]
                    stability = floor["stability"]
                    status = _status_text(floor["status"], stability)
                    meaning = _HUMAN_MEANINGS.get(f_id, "")

                    with Card(css_class=f"border-l-4 { 'border-destructive' if status == 'FAIL' else '' }"):
                        with CardContent(css_class="py-2 px-3"):
                            with Row(gap=4, align="start"):
                                with Column(gap=0, css_class="w-8"):
                                    Text(f_id, css_class="font-mono text-xs font-bold text-muted-foreground")
                                
                                with Column(gap=0, css_class="w-32"):
                                    Text(f_name, css_class="text-sm font-medium")
                                    Progress(value=stability*100, css_class="h-1.5 mt-1")
                                
                                with Column(gap=0, css_class="flex-1"):
                                    Muted(meaning, css_class="text-xs italic leading-tight")
                                
                                Badge(
                                    status,
                                    variant=_stability_variant(stability),
                                    css_class="w-16 text-center text-[10px]",
                                )

            Separator()

            # ── Telemetry Metrics (CHANGE-03) ─────────────────────────────────
            with Grid(columns=3, gap=3):
                with Card():
                    with CardContent(css_class="py-3 text-center"):
                        Text(
                            f"{delta_s:+.2f}",
                            css_class=f"text-xl font-bold font-mono",
                        )
                        Muted("Entropy trend (ΔS)", css_class="text-[10px]")
                        Badge(
                            "stable" if delta_s <= 0 else "increasing confusion",
                            variant=_delta_s_variant(delta_s),
                            css_class="text-[8px] h-3 px-1 mt-1",
                        )

                with Card():
                    with CardContent(css_class="py-3 text-center"):
                        Text(
                            f"{peace_sq:.2f}",
                            css_class=f"text-xl font-bold font-mono",
                        )
                        Muted("Stability index (Peace²)", css_class="text-[10px]")
                        Badge(
                            "stable" if peace_sq >= 1 else "destabilized",
                            variant=_peace_variant(peace_sq),
                            css_class="text-[8px] h-3 px-1 mt-1",
                        )

                with Card():
                    with CardContent(css_class="py-3 text-center"):
                        Text(
                            f"{omega0:.2f}",
                            css_class="text-xl font-bold font-mono text-muted-foreground",
                        )
                        Muted("Baseline (Ω₀)", css_class="text-[10px]")
                        Badge("nominal", variant="secondary", css_class="text-[8px] h-3 px-1 mt-1")

            Separator()

            # ── Recommended Next Actions (CHANGE-04) ──────────────────────────
            with Column(gap=3):
                Muted("What to do now", css_class="text-xs uppercase tracking-wider")
                with Card(css_class="bg-primary/5"):
                    with CardContent(css_class="py-4"):
                        for action in next_actions:
                            with Row(gap=3, align="center", css_class="py-1"):
                                Badge("ACTION", variant="secondary", css_class="text-[9px] h-4 font-bold")
                                Text(action, css_class="text-sm font-medium")

            Separator()

            # ── Philosophy Footer (CHANGE-05) ─────────────────────────────────
            Muted(
                philosophy,
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

        summary = (
            f"arifOS Metabolic Monitor | Status: {overall_status} | "
            f"ΔS={delta_s:+.2f} | Peace²={peace_sq:.2f} | Actions: {len(next_actions)}"
        )
        return ToolResult(content=summary, structured_content=view)
