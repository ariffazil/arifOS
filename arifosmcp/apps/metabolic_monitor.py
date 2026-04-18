"""
arifosmcp/apps/metabolic_monitor.py
══════════════════════════════════════════════════════════════════════════════════════
arifOS Metabolic Monitor — FastMCP Prefab UI (F1-F13 Floor Radar + Live VPS Observability)
══════════════════════════════════════════════════════════════════════════════════════

Renders a real-time constitutional health dashboard showing:

  • Deploy badge — release_tag, source_commit, canonical runtime URL
  • Thermodynamic band — entropy ΔS, Peace², vitality index, shadow, confidence
  • Witness triangle — human·AI·earth tri-witness weights
  • Substrate band — live capability map traffic lights (vault, memory, grounding, etc.)
  • Credential & OPS band — auth wiring and operational controls
  • Restart fragility warning — when server_identity is ephemeral_process_local
  • Operator action cards — concrete "set X" commands for each degraded item
  • F1-F13 constitutional floor grid
  • Recommended next actions
  • Philosophy footer

Data sources (merged):
  • /health endpoint — live thermodynamic + capability map truth
  • Session runtime state — per-session floor stability
  • WELL state.json — biological substrate (optional)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import os
import socket
import subprocess
import time
from typing import Annotated, Any

from fastmcp import FastMCP
from fastmcp.apps.config import PrefabAppConfig
from fastmcp.tools import ToolResult
from prefab_ui.components import (
    Alert,
    AlertDescription,
    AlertTitle,
    Badge,
    Card,
    CardContent,
    Column,
    Grid,
    Heading,
    Metric,
    Muted,
    Progress,
    Ring,
    Row,
    Separator,
    Text,
)
from pydantic import Field

# ── Canonical runtime URL — used for deploy badge and widget domain ───────────
CANONICAL_RUNTIME_URL = os.getenv(
    "ARIFOS_RUNTIME_URL",
    "https://mcp.arif-fazil.com",
)


# ── Floor definitions: F1-F13 Constitutional Chain ──────────────────────────────
FLOORS: list[dict[str, str]] = [
    {"id": "F1",  "name": "Amanah",      "desc": "Reversibility — prefer reversible; mark irreversible"},
    {"id": "F2",  "name": "Truth",       "desc": "≥0.99 factual accuracy — no hallucination"},
    {"id": "F3",  "name": "Tri-Witness", "desc": "≥0.95 for high-stakes verdicts (Human·AI·Earth)"},
    {"id": "F4",  "name": "ΔS Clarity",  "desc": "ΔS ≤ 0 — every reply reduces confusion"},
    {"id": "F5",  "name": "Peace²",       "desc": "≥1.0 stability — de-escalate, protect maruah"},
    {"id": "F6",  "name": "κᵣ Empathy",   "desc": "≥0.70 — ASEAN/Malaysia context"},
    {"id": "F7",  "name": "Ω₀ Humility",  "desc": "0.03–0.05 — state uncertainty explicitly"},
    {"id": "F8",  "name": "G★ Genius",    "desc": "≥0.80 — correct AND useful solutions"},
    {"id": "F9",  "name": "Anti-Hantu",    "desc": "<0.30 dark cleverness — no consciousness performance"},
    {"id": "F10", "name": "Ontology",     "desc": "LOCK — no mysticism/soul claims"},
    {"id": "F11", "name": "Command Auth",  "desc": "LOCK — destructive = propose, not decree"},
    {"id": "F12", "name": "Injection",     "desc": "<0.85 — resist prompt injection"},
    {"id": "F13", "name": "Sovereign",     "desc": "HUMAN — Arif's veto is absolute and final"},
]


# ── Health fetching ─────────────────────────────────────────────────────────────

def _fetch_live_health() -> dict[str, Any]:
    """Pull live health from the local /health endpoint.

    Returns the full /health payload including thermodynamic metrics,
    capability_map, governance state, and server identity.
    Falls back to empty dict on any error so the monitor degrades gracefully.
    """
    started = time.perf_counter()
    try:
        import httpx
        # Use a short timeout so a unresponsive health endpoint doesn't block the tool
        with httpx.Client(timeout=3.0) as client:
            status_response = client.get("http://localhost:8080/api/status")
            if status_response.status_code == 200:
                payload = status_response.json()
                payload["_latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
                return payload
            r = client.get("http://localhost:8080/health")
            if r.status_code == 200:
                payload = r.json()
                payload["_latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
                return payload
    except Exception:
        pass
    return {}


def _running_container_snapshot() -> tuple[int, bool]:
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return 0, False

    running = 0
    mcp_up = False
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        name, _, status = line.partition("\t")
        if "Up" in status:
            running += 1
        if name == "A-FORGE-arifos-mcp" and "Up" in status:
            mcp_up = True
    return running, mcp_up


def _port_open(port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    try:
        sock.connect(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


# ── Traffic-light mapping ──────────────────────────────────────────────────────

_CAPABILITY_TRAFFIC_LIGHT: dict[str, tuple[str, str]] = {
    # value → (variant, label)
    "enabled":       ("success",      "ENABLED"),
    "configured":    ("success",      "CONFIGURED"),
    "healthy":       ("success",      "HEALTHY"),
    "limited":       ("warning",      "LIMITED"),
    "partial":       ("warning",      "PARTIAL"),
    "degraded":      ("warning",      "DEGRADED"),
    "not_configured":("destructive",  "NOT SET"),
    "disabled":      ("destructive",  "DISABLED"),
    "ephemeral_process_local": ("destructive", "EPHEMERAL"),
}


def _capability_variant(value: str) -> tuple[str, str]:
    """Map a capability/credential/OPS value to a traffic-light variant and label."""
    return _CAPABILITY_TRAFFIC_LIGHT.get(
        value,
        ("secondary", value.upper()),
    )


def _capability_row(name: str, value: str, description: str | None = None) -> tuple[str, str, str, str | None]:
    """Return (name, badge_label, variant, description) for a capability row."""
    variant, label = _capability_variant(value)
    return name, label, variant, description


# ── Operator action map ───────────────────────────────────────────────────────

_OPERATOR_ACTIONS: list[tuple[str, str, str, str]] = [
    # (capability_key, display_name, fix_command, severity)
    # RED — must fix before consequential action
    ("api_bearer_auth",          "API Bearer Auth",        "set ARIFOS_BEARER_TOKEN",                       "critical"),
    ("governed_continuity",      "Continuity",              "set ARIFOS_AGENT_ID + restart",                  "critical"),
    ("vault_persistence",        "Vault Persistence",        "set POSTGRES_URL → restart",                     "critical"),
    # AMBER — degraded but functional; fix when convenient
    ("external_grounding",       "External Grounding",      "set BRAVE_API_KEY + JINA_API_KEY",               "advisory"),
    ("provider_access",          "Provider Access",          "set MINIMAX_API_KEY (or other LLM provider)",    "advisory"),
    ("ops_controls",             "OPS Controls",             "set OPS_WEBHOOK_URL",                            "advisory"),
    ("auto_deploy",              "Auto-Deploy",              "set DEPLOY_WEBHOOK_URL",                         "advisory"),
]


# ── Session floor helpers ──────────────────────────────────────────────────────

def _unknown_floors() -> list[dict[str, Any]]:
    return [
        {"id": f["id"], "name": f["name"], "stability": 0.5, "status": "UNKNOWN"}
        for f in FLOORS
    ]


def _live_floor_status(session_id: str) -> list[dict[str, Any]]:
    """Pull live floor status from session continuity; return UNKNOWN when no session state exists."""
    try:
        from arifosmcp.runtime.sessions import get_session_runtime_state
        state = get_session_runtime_state(session_id)
        if not state:
            return _unknown_floors()
        live = (((state.get("activity") or {}).get("floors")) or {})
        result = []
        for f in FLOORS:
            fid = f["id"]
            floor_state = live.get(fid) or {}
            stability = float(floor_state.get("stability", 0.95 if state else 0.5))
            status = floor_state.get("status") or (
                "PASS" if stability >= 0.90 else (
                    "STRAIN" if stability >= 0.70 else "FAIL"
                )
            )
            result.append({"id": fid, "name": f["name"], "stability": stability, "status": status})
        return result
    except Exception:
        return _unknown_floors()


def _stability_variant(stability: float) -> str:
    if stability >= 0.90:
        return "success"
    elif stability >= 0.70:
        return "warning"
    return "destructive"


def _status_text(status: str, stability: float) -> str:
    if status == "UNKNOWN":
        return "UNKNOWN"
    if stability >= 0.90:
        return "PASS"
    elif stability >= 0.70:
        return "STRAIN"
    return "FAIL"


# ── Human-meaning map for F1-F13 ───────────────────────────────────────────────

_HUMAN_MEANINGS: dict[str, str] = {
    "F1":  "Can this be undone? If FAIL: rollback path missing.",
    "F2":  "Is this grounded? If FAIL: claims unverifiable.",
    "F3":  "Do theory, law, and intent agree? If FAIL: divergence detected.",
    "F4":  "Is this reducing confusion? If FAIL: entropy increasing.",
    "F5":  "Is this non-destructive? If FAIL: value or trust at risk.",
    "F6":  "Is the human heard? If FAIL: underlying intent may be missed.",
    "F7":  "Are uncertainties surfaced? If FAIL: confidence overstated.",
    "F8":  "Is systemic health maintained? If FAIL: subsystem under load.",
    "F9":  "No manipulation or dark patterns? If FAIL: interaction suspect.",
    "F10": "No consciousness claims? If FAIL: ontology violated.",
    "F11": "Is everything logged? If FAIL: action not traceable.",
    "F12": "Is the prompt safe? If FAIL: override pressure detected.",
    "F13": "Is human veto intact? If FAIL: sovereign authority at risk.",
}


# ── Status interpretations ─────────────────────────────────────────────────────

_STATUS_INTERPRETATIONS: dict[str, dict[str, str]] = {
    "UNKNOWN":    {"badge": "UNKNOWN",   "posture": "No active session telemetry. Run arifos_init first to populate live state.",          "variant": "secondary"},
    "OPERATIONAL": {"badge": "SEALED",   "posture": "All floors passing. Safe for consequential action.",                                   "variant": "success"},
    "DEGRADED":   {"badge": "DEGRADED", "posture": "Core governance alive. Trust posture degraded. Use for inspection only.",               "variant": "warning"},
    "CRITICAL":   {"badge": "BLOCKED",  "posture": "Hard floor violated. No consequential action permitted. Human required.",              "variant": "destructive"},
}

_SIGNAL_VARIANTS = {
    "positive": "success",
    "neutral": "warning",
    "negative": "destructive",
}


def _derive_signal_matrix(
    health: dict[str, Any],
    floors: list[dict[str, Any]],
) -> list[dict[str, str]]:
    thermo = health.get("thermodynamic") or {}
    gov = health.get("governance") or {}
    caps = (health.get("capability_map") or {}).get("capabilities") or {}
    latency_ms = float(health.get("_latency_ms") or 0.0)
    running_containers, mcp_up = _running_container_snapshot()
    port_3099_open = _port_open(3099)
    verdict = str(thermo.get("verdict") or "UNKNOWN").upper()
    confidence = float(thermo.get("confidence") or 0.0)
    entropy_delta = float(thermo.get("entropy_delta") or 0.0)
    stage = int(thermo.get("metabolic_stage") or 0)
    continuity_enabled = caps.get("governed_continuity") == "enabled"
    all_floors_verified = all(f["status"] in {"PASS", "STRAIN"} for f in floors)
    shadow = float(thermo.get("shadow") or 0.0)

    if not mcp_up or not port_3099_open:
        delta = {
            "axis": "DELTA",
            "title": "Infrastructure",
            "label": "LEBUR (MELTED)",
            "variant": "negative",
            "detail": "MCP container is down or port 3099 is blocked.",
        }
    elif health.get("version") != health.get("release_tag") or latency_ms > 500:
        delta = {
            "axis": "DELTA",
            "title": "Infrastructure",
            "label": "RETAK (CRACKED)",
            "variant": "neutral",
            "detail": "Version drift detected or live latency exceeds 500 ms.",
        }
    elif running_containers >= 21 and entropy_delta < 0:
        delta = {
            "axis": "DELTA",
            "title": "Infrastructure",
            "label": "KUKUH (SOLID)",
            "variant": "positive",
            "detail": f"All {running_containers} containers are up and entropy is cooling.",
        }
    else:
        delta = {
            "axis": "DELTA",
            "title": "Infrastructure",
            "label": "RETAK (CRACKED)",
            "variant": "neutral",
            "detail": "Runtime is up, but the machine layer is not yet fully solid.",
        }

    if shadow >= 0.3 or verdict == "VOID":
        psi = {
            "axis": "PSI",
            "title": "Compliance",
            "label": "KHIANAT (BREACHED)",
            "variant": "negative",
            "detail": "A hard floor is violated or anti-hantu protection is triggered.",
        }
    elif continuity_enabled and all_floors_verified and verdict == "SEAL" and confidence >= 0.99:
        psi = {
            "axis": "PSI",
            "title": "Compliance",
            "label": "AMANAH (TRUSTED)",
            "variant": "positive",
            "detail": "Continuity is persistent and constitutional floors are holding.",
        }
    else:
        psi = {
            "axis": "PSI",
            "title": "Compliance",
            "label": "GANTUNG (PENDING)",
            "variant": "neutral",
            "detail": f"Governance is active, but the system is still holding at stage {stage}.",
        }

    if verdict == "SEAL" and confidence >= 0.99:
        omega = {
            "axis": "OMEGA",
            "title": "Reasoning",
            "label": "BIJAKSANA (WISE)",
            "variant": "positive",
            "detail": "Reasoning is sealed with machine-grounded confidence.",
        }
    elif confidence > 0:
        omega = {
            "axis": "OMEGA",
            "title": "Reasoning",
            "label": "BIJAK (SMART)",
            "variant": "neutral",
            "detail": "Reasoning is functioning, but confidence is below the 0.99 seal threshold.",
        }
    else:
        omega = {
            "axis": "OMEGA",
            "title": "Reasoning",
            "label": "SESAT (MISALIGNED)",
            "variant": "negative",
            "detail": "Reasoning is broken or returning no trustworthy signal.",
        }

    return [delta, psi, omega]


# ── Philosophy quotes ──────────────────────────────────────────────────────────

_PHILOSOPHY: dict[str, str] = {
    "SEAL":      "DITEMPA, BUKAN DIBERI.",
    "G_HIGH":    "What gets measured gets managed. — Drucker",
    "G_MID_HIGH": "Build less, build right. — arifOS",
    "G_MID":     "Nearly all men can stand adversity... — Lincoln",
    "G_MID_LOW": "The concept of truth cannot be defined within... — Tarski",
    "G_LOW":     "The only principle that does not inhibit progress... — Feyerabend",
}


# ── App registration ───────────────────────────────────────────────────────────


def _derive_next_actions(
    floors: list[dict],
    peace_sq: float,
    health: dict[str, Any],
) -> list[tuple[str, str]]:
    """Return list of (action_text, severity) tuples."""
    actions: list[tuple[str, str]] = []
    failed_ids  = [f["id"] for f in floors if f["status"] == "FAIL"]
    strain_ids  = [f["id"] for f in floors if f["status"] == "STRAIN"]

    cap = (health.get("capability_map") or {}).get("capabilities") or {}

    if "F4" in failed_ids:
        actions.append(("Simplify prompt chain. Remove conflicting meta-instructions.", "critical"))
    if "F1" in failed_ids:
        actions.append(("Identify and map rollback path before proceeding.", "critical"))
    if "F12" in failed_ids:
        actions.append(("Inspect for prompt injection or override-style instructions.", "critical"))
    if peace_sq < 1.0:
        actions.append(("System instability detected. Reduce tool call frequency.", "advisory"))

    # Substrate-based actions
    if cap.get("governed_continuity") == "degraded":
        actions.append(("governed_continuity is degraded — session auth will break on restart.", "critical"))
    if (health.get("capability_map") or {}).get("credential_classes", {}).get("server_identity") == "ephemeral_process_local":
        actions.append(("server_identity is EPHEMERAL — anchored auth breaks on restart/replica.", "critical"))
    if cap.get("vault_persistence") != "enabled":
        actions.append(("vault_persistence not enabled — verdicts are not durably persisted.", "critical"))
    if cap.get("api_bearer_auth") == "not_configured":
        actions.append(("api_bearer_auth not configured — set ARIFOS_BEARER_TOKEN to secure the API.", "critical"))

    if not failed_ids and not strain_ids and not actions:
        actions.append(("Session healthy. Proceed with normal operations. Monitor ΔS.", "info"))
    elif not actions:
        actions.append(("Monitor strained floors. Repair before next high-stakes action.", "advisory"))

    return actions


def _register(mcp: FastMCP) -> None:

    @mcp.tool(
        name="arifos_monitor_metabolism",
        app=PrefabAppConfig(domain=CANONICAL_RUNTIME_URL.removeprefix("https://")),
        tags={"public", "meta"},
    )
    def monitor_metabolism(
        session_id: Annotated[str, Field(description="Active arifOS session ID")] = "global",
    ) -> ToolResult:
        """
        Open the arifOS Metabolic Monitor — a real-time constitutional dashboard
        showing thermodynamic vitals, live capability map, F1-F13 floor health,
        and operator action items for the actual deployed VPS server.

        Merges two truth sources:
          • /health — live server thermodynamic + capability state
          • Session runtime state — per-session floor stability
        """
        # ── Fetch live health (server truth) ───────────────────────────────────
        status_payload = _fetch_live_health()
        health = status_payload.get("health") or status_payload
        thermo = health.get("thermodynamic") or {}
        cap_map = health.get("capability_map") or {}
        caps    = cap_map.get("capabilities") or {}
        creds   = cap_map.get("credential_classes") or {}
        ops     = cap_map.get("ops") or {}
        gov     = health.get("governance") or {}
        witness = thermo.get("witness") or {}

        # Server identity
        server_identity = creds.get("server_identity", "unknown")
        is_ephemeral   = server_identity == "ephemeral_process_local"

        # Thermodynamic values (prefer /health; fall back to session telemetry)
        entropy_delta  = float(thermo.get("entropy_delta")  or 0.0)
        peace_sq       = float(thermo.get("peace_squared")  or 0.0)
        vitality       = float(thermo.get("vitality_index") or 0.0)
        shadow         = float(thermo.get("shadow")         or 0.0)
        confidence     = float(thermo.get("confidence")     or 0.0)
        metabolic_stage = int(thermo.get("metabolic_stage") or 0)

        # Witness triangle
        w_human = float(witness.get("human", 0.0))
        w_ai    = float(witness.get("ai",    0.0))
        w_earth = float(witness.get("earth", 0.0))
        witness_total = w_human + w_ai + w_earth

        # Deploy metadata
        source_commit = health.get("source_commit", "unknown")
        release_tag   = health.get("release_tag",   "unknown")
        runtime_url   = CANONICAL_RUNTIME_URL

        # ── Session floor data (session truth) ─────────────────────────────────
        floors = _live_floor_status(session_id)
        avg_stability = sum(f["stability"] for f in floors) / len(floors)
        canonical_matrix = status_payload.get("trinity_matrix") or {}
        if canonical_matrix:
            signal_matrix = []
            for axis, title in [("delta", "Infrastructure"), ("psi", "Compliance"), ("omega", "Reasoning")]:
                entry = canonical_matrix.get(axis) or {}
                signal_matrix.append(
                    {
                        "axis": axis.upper(),
                        "title": title,
                        "label": f"{entry.get('label_bm', '--')} / {entry.get('label_en', '--')}",
                        "variant": (
                            "positive"
                            if entry.get("color") == "teal"
                            else "neutral"
                            if entry.get("color") == "amber"
                            else "negative"
                        ),
                        "detail": " · ".join(
                            [
                                ", ".join(entry.get("evidence") or []),
                                (
                                    f"{(entry.get('metrics') or {}).get('raw_val')} "
                                    f"{(entry.get('metrics') or {}).get('unit', '')}"
                                ).strip(),
                            ]
                        ).strip(" ·"),
                    }
                )
        else:
            signal_matrix = _derive_signal_matrix(health, floors)
        worst_signal = next((signal for signal in signal_matrix if signal["variant"] == "negative"), None)
        if worst_signal is None:
            worst_signal = next((signal for signal in signal_matrix if signal["variant"] == "neutral"), signal_matrix[0])

        # ── Overall status ─────────────────────────────────────────────────────
        if not thermo or not caps:
            overall_status = "UNKNOWN"
        elif peace_sq >= 1.0 and avg_stability >= 0.90:
            overall_status = "OPERATIONAL"
        elif peace_sq >= 0.5 and avg_stability >= 0.70:
            overall_status = "DEGRADED"
        else:
            overall_status = "CRITICAL"

        interpretation = _STATUS_INTERPRETATIONS.get(overall_status, _STATUS_INTERPRETATIONS["UNKNOWN"])
        next_actions   = _derive_next_actions(floors, peace_sq, health)

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

        # ── WELL biological context (optional local state) ─────────────────────
        try:
            from arifosmcp.runtime.well_bridge import get_biological_readiness
            well = get_biological_readiness()
        except ImportError:
            well = {"ok": False, "verdict": "UNKNOWN", "well_score": 0.0}

        # ── BUILD VIEW ──────────────────────────────────────────────────────────
        with Column(gap=6, css_class="p-6 max-w-3xl") as view:

            # ══ 1. DEPLOY BADGE ════════════════════════════════════════════════
            with Card(css_class="border border-muted bg-muted/10"):
                with CardContent(css_class="py-3 px-4"):
                    with Row(gap=3, align="center"):
                        Badge(release_tag, variant="secondary", css_class="font-mono text-xs")
                        Badge(source_commit[:8], variant="outline", css_class="font-mono text-xs")
                        with Column(gap=0):
                            Heading("arifOS Metabolic Monitor", size="sm")
                            Muted(runtime_url, css_class="text-xs font-mono")
                        Badge(
                            worst_signal["label"],
                            variant=_SIGNAL_VARIANTS[worst_signal["variant"]],
                            css_class="ml-auto font-mono text-sm",
                        )

            # ══ 2. OPERATOR INTERPRETATION BANNER ══════════════════════════════
            with Card(css_class="border-2"):
                with CardContent(css_class="py-3 px-5"):
                    with Column(gap=3):
                        Text(
                            "Universal Nine-Signal Matrix · Matriks Sembilan Isyarat Sejagat",
                            css_class="text-sm font-semibold",
                        )
                        for signal in signal_matrix:
                            with Row(gap=4, align="center"):
                                Badge(
                                    signal["axis"],
                                    variant="outline",
                                    css_class="w-16 text-center font-mono text-[10px]",
                                )
                                Badge(
                                    signal["label"],
                                    variant=_SIGNAL_VARIANTS[signal["variant"]],
                                    css_class="w-52 text-center font-mono text-[10px]",
                                )
                                with Column(gap=0, css_class="flex-1"):
                                    Text(signal["title"], css_class="text-xs font-semibold uppercase")
                                    Muted(signal["detail"], css_class="text-xs")

            # ══ 3. RESTART FRAGILITY WARNING ═══════════════════════════════════
            if is_ephemeral:
                with Alert(variant="destructive", css_class="border-2 border-destructive/50"):
                    with AlertTitle(css_class="text-sm font-bold"):
                        Text("⚠ restart fragility — anchored auth will break on restart or replica change")
                    with AlertDescription(css_class="text-xs"):
                        Muted(
                            "server_identity is ephemeral_process_local. "
                            "Set ARIFOS_AGENT_ID with a stable identity to persist across restarts.",
                            css_class="text-xs",
                        )

            # ══ 4. WELL BIOLOGICAL STATUS ═════════════════════════════════════
            if well.get("ok"):
                with Card(css_class="border-2 border-green-500/30 bg-green-500/5"):
                    with CardContent(css_class="py-2 px-4"):
                        with Row(gap=4, align="center"):
                            Badge(
                                f"WELL: {well['well_score']:.1f}",
                                variant="outline",
                                css_class="font-mono font-bold",
                            )
                            Text(f"Biological Substrate: {well['verdict']}", css_class="text-xs font-bold uppercase")
                            if well.get("violations"):
                                Badge("FLOOR VIOLATED", variant="destructive", css_class="text-[8px] h-4")

            # ══ 5. THERMODYNAMIC BAND ════════════════════════════════════════════
            Muted("Thermodynamic Vitals", css_class="text-xs uppercase tracking-wider font-bold")
            with Grid(columns=3, gap=3):
                with Card():
                    with CardContent(css_class="py-3 text-center"):
                        Text(f"{entropy_delta:+.2f}", css_class="text-xl font-bold font-mono")
                        Muted("Entropy trend (ΔS)", css_class="text-[10px]")
                        Badge(
                            "stable" if entropy_delta <= 0 else "confusion ↑",
                            variant="success" if entropy_delta <= 0 else ("warning" if entropy_delta < 0.1 else "destructive"),
                            css_class="text-[8px] h-3 px-1 mt-1",
                        )

                with Card():
                    with CardContent(css_class="py-3 text-center"):
                        Text(f"{peace_sq:.3f}", css_class="text-xl font-bold font-mono")
                        Muted("Stability (Peace²)", css_class="text-[10px]")
                        Badge(
                            "stable" if peace_sq >= 1.0 else ("low" if peace_sq >= 0.5 else "critical"),
                            variant="success" if peace_sq >= 1.0 else ("warning" if peace_sq >= 0.5 else "destructive"),
                            css_class="text-[8px] h-3 px-1 mt-1",
                        )

                with Card():
                    with CardContent(css_class="py-3 text-center"):
                        Text(f"{vitality:.4f}", css_class="text-xl font-bold font-mono")
                        Muted("Vitality Index", css_class="text-[10px]")
                        Badge(
                            "operational" if vitality >= 0.5 else "degraded",
                            variant="success" if vitality >= 0.5 else "warning",
                            css_class="text-[8px] h-3 px-1 mt-1",
                        )

            with Grid(columns=3, gap=3, css_class="mt-3"):
                with Card():
                    with CardContent(css_class="py-2 text-center"):
                        Text(f"{shadow:.2f}", css_class="text-lg font-bold font-mono")
                        Muted("Shadow load", css_class="text-[10px]")

                with Card():
                    with CardContent(css_class="py-2 text-center"):
                        Text(f"{confidence:.2f}", css_class="text-lg font-bold font-mono")
                        Muted("Confidence (Ω₀)", css_class="text-[10px]")

                with Card():
                    with CardContent(css_class="py-2 text-center"):
                        Text(f"S{metabolic_stage}", css_class="text-lg font-bold font-mono")
                        Muted("Metabolic stage", css_class="text-[10px]")

            # ══ 5b. WITNESS TRIANGLE ════════════════════════════════════════════
            with Card(css_class="border border-muted/30"):
                with CardContent(css_class="py-3 px-4"):
                    with Row(gap=4, align="center"):
                        Muted("Tri-Witness", css_class="text-xs uppercase tracking-wider font-bold")
                        with Column(gap=1, css_class="flex-1"):
                            # Three witness bars side by side
                            for label, value in [("human", w_human), ("AI", w_ai), ("earth", w_earth)]:
                                with Row(gap=2, align="center"):
                                    Text(label, css_class="text-xs font-mono w-12")
                                    with Column(gap=0, css_class="flex-1"):
                                        Progress(
                                            value=float(value) * 100,
                                            css_class="h-2",
                                        )
                                    Text(f"{value:.2f}", css_class="text-xs font-mono w-10 text-right")
                        Badge(
                            f"total={witness_total:.2f}",
                            variant="secondary",
                            css_class="text-[9px] font-mono",
                        )

            Separator()

            # ══ 6. SUBSTRATE BAND ════════════════════════════════════════════════
            Muted("Substrate & Capability Map", css_class="text-xs uppercase tracking-wider font-bold")
            with Column(gap=1):

                # Capabilities row
                for cap_key, cap_label in [
                    ("governed_continuity",  "Continuity"),
                    ("vault_persistence",     "Vault"),
                    ("vector_memory",         "Vector Memory"),
                    ("external_grounding",    "Grounding"),
                    ("model_provider_access",  "LLM Providers"),
                    ("local_model_runtime",   "Local Model"),
                    ("auto_deploy",           "Auto-Deploy"),
                ]:
                    cap_val = caps.get(cap_key, "unknown")
                    variant, label = _capability_variant(cap_val)
                    with Card(css_class="py-1 px-3"):
                        with Row(gap=3, align="center"):
                            Badge(label, variant=variant, css_class="w-20 text-center text-[10px]")
                            Text(cap_label, css_class="text-xs flex-1")
                            Text(cap_val, css_class="text-xs font-mono text-muted-foreground")

                Separator()

                # Credential classes
                Muted("Credential Classes", css_class="text-xs uppercase tracking-wider")
                for cred_key in ["server_identity", "storage_access", "provider_access", "ops_controls"]:
                    cred_val = creds.get(cred_key, "unknown")
                    variant, label = _capability_variant(cred_val)
                    with Card(css_class="py-1 px-3"):
                        with Row(gap=3, align="center"):
                            Badge(label, variant=variant, css_class="w-20 text-center text-[10px]")
                            Text(cred_key.replace("_", " ").title(), css_class="text-xs flex-1")
                            Text(cred_val, css_class="text-xs font-mono text-muted-foreground")

                Separator()

                # OPS status
                Muted("OPS Controls", css_class="text-xs uppercase tracking-wider")
                for ops_key in ["webhook_deploy", "grafana_access", "openclaw_restart", "api_bearer_auth"]:
                    ops_val = ops.get(ops_key, "unknown")
                    variant, label = _capability_variant(ops_val)
                    with Card(css_class="py-1 px-3"):
                        with Row(gap=3, align="center"):
                            Badge(label, variant=variant, css_class="w-20 text-center text-[10px]")
                            Text(ops_key.replace("_", " ").title(), css_class="text-xs flex-1")
                            Text(ops_val, css_class="text-xs font-mono text-muted-foreground")

            Separator()

            # ══ 7. OPERATOR ACTIONS ════════════════════════════════════════════════
            critical_actions = [(a, s) for a, s in next_actions if s == "critical"]
            advisory_actions = [(a, s) for a, s in next_actions if s == "advisory"]
            info_actions     = [(a, s) for a, s in next_actions if s == "info"]

            if critical_actions:
                Muted("Critical Actions (fix before consequential use)", css_class="text-xs uppercase tracking-wider font-bold text-destructive")
                with Column(gap=2):
                    for action_text, _ in critical_actions:
                        with Card(css_class="border-l-4 border-destructive bg-destructive/5 py-2 px-3"):
                            with Row(gap=3, align="center"):
                                Badge("ACTION", variant="destructive", css_class="text-[9px] h-4 font-bold")
                                Text(action_text, css_class="text-xs font-medium")

            if advisory_actions:
                with Column(gap=2, css_class="mt-2"):
                    Muted("Advisory (fix when convenient)", css_class="text-xs uppercase tracking-wider")
                    for action_text, _ in advisory_actions:
                        with Card(css_class="border-l-4 border-amber-500/50 bg-amber-500/5 py-2 px-3"):
                            with Row(gap=3, align="center"):
                                Badge("ADVISORY", variant="warning", css_class="text-[9px] h-4 font-bold")
                                Text(action_text, css_class="text-xs font-medium")

            Separator()

            # ══ 8. F1-F13 FLOOR GRID ══════════════════════════════════════════════
            Muted("Constitutional Floors F1-F13", css_class="text-xs uppercase tracking-wider")
            with Column(gap=2):
                for floor in floors:
                    f_id   = floor["id"]
                    status = _status_text(floor["status"], floor["stability"])
                    meaning = _HUMAN_MEANINGS.get(f_id, "")
                    card_css = f"border-l-4 {'border-destructive' if status == 'FAIL' else ('border-amber-500/40' if status == 'STRAIN' else 'border-green-500/30')}"
                    with Card(css_class=card_css):
                        with CardContent(css_class="py-2 px-3"):
                            with Row(gap=4, align="start"):
                                with Column(gap=0, css_class="w-8"):
                                    Text(f_id, css_class="font-mono text-xs font-bold text-muted-foreground")
                                with Column(gap=0, css_class="w-32"):
                                    Text(floor["name"], css_class="text-sm font-medium")
                                    Progress(value=floor["stability"] * 100, css_class="h-1.5 mt-1")
                                with Column(gap=0, css_class="flex-1"):
                                    Muted(meaning, css_class="text-xs italic leading-tight")
                                Badge(status, variant=_stability_variant(floor["stability"]), css_class="w-16 text-center text-[10px]")

            Separator()

            # ══ 9. PHILOSOPHY FOOTER ══════════════════════════════════════════════
            Muted(philosophy, css_class="text-xs italic text-center text-muted-foreground/60")
            with Column(gap=1, align="center", css_class="mt-3"):
                Muted(
                    "Human architect retains sovereign veto. F13 is always alive.",
                    css_class="text-[10px] uppercase tracking-widest font-bold text-primary/40",
                )
                Muted(
                    f"arifOS Metabolic Monitor · {source_commit[:8]} · {release_tag} · DITEMPA BUKAN DIBERI",
                    css_class="text-[9px] text-muted-foreground/60",
                )

        summary = (
            f"arifOS Metabolic Monitor | "
            f"{signal_matrix[0]['label']} | {signal_matrix[1]['label']} | {signal_matrix[2]['label']} | "
            f"ΔS={entropy_delta:+.2f} | Peace²={peace_sq:.3f} | "
            f"Vitality={vitality:.4f} | Actions: {len(next_actions)}"
        )
        return ToolResult(content=summary, structured_content=view)


# ── Module-level FastMCP app registration ─────────────────────────────────────

def get_app() -> FastMCP:
    """Return a FastMCP app with the metabolic monitor registered."""
    mcp = FastMCP("arifOS-Metabolic")
    _register(mcp)
    return mcp
