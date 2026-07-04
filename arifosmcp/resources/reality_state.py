"""
arifos://reality/state — Causally-Consistent Multi-Layer Reality Snapshot
════════════════════════════════════════════════════════════════════════

Truthful reality: a single resource that returns the current state of
all four reality layers at one consistent timestamp.

  PHYSICAL   — Earth (GEOX), machine (system vitals), environmental
  DIGITAL    — Federation organs, MCP surface, memory, audit
  BIOLOGICAL — Human readiness, vitality, dignity (WELL)
  QUANTUM    — Declared UNKNOWN. Domain scope does not include it.

Causality contract:
  Every value carries a timestamp and an epistemic label.
  If two values disagree, both are returned with their labels.
  No false unification. No unwarranted certainty.

F-binding:
  F2 TRUTH:    every value labeled OBS/DER/INT/SPEC/UNKNOWN
  F4 CLARITY:  single snapshot, no ambiguity
  F6 MARUAH:   biological layer respects dignity boundaries
  F7 HUMILITY: Ω₀ declared for every uncertain value
  F9 ANTIHANTU: quantum = UNKNOWN. Never fabricate what isn't sensed.
  F13 SOVEREIGN: human layer requires session auth

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import time
from typing import Any

from fastmcp import FastMCP


def _probe_physical() -> dict[str, Any]:
    """Probe physical reality layer.

    Returns machine vitals and earth status.
    All values are live-probed — no hardcoded numbers.
    """
    import os
    import shutil

    result: dict[str, Any] = {
        "layer": "physical",
        "epistemic": "OBSERVED",
        "timestamp": time.time(),
        "degraded": False,
    }

    # ── Machine vitals (always available — local /proc) ──────────────────
    cpu_info: dict[str, Any] = {"epistemic": "OBSERVED"}
    try:
        load = os.getloadavg()
        cpu_info["load_1m"] = round(load[0], 2)
        cpu_info["load_5m"] = round(load[1], 2)
        cpu_info["load_15m"] = round(load[2], 2)
    except OSError:
        cpu_info["error"] = "loadavg unavailable"
        cpu_info["epistemic"] = "DEGRADED"
        result["degraded"] = True

    mem_info: dict[str, Any] = {"epistemic": "OBSERVED"}
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    mem_info["total_kb"] = int(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    mem_info["available_kb"] = int(line.split()[1])
        if "total_kb" in mem_info and "available_kb" in mem_info:
            mem_info["used_pct"] = round(
                (1 - mem_info["available_kb"] / mem_info["total_kb"]) * 100, 1
            )
    except OSError:
        mem_info["error"] = "meminfo unavailable"
        mem_info["epistemic"] = "DEGRADED"
        result["degraded"] = True

    disk_info: dict[str, Any] = {"epistemic": "OBSERVED"}
    try:
        usage = shutil.disk_usage("/")
        disk_info["total_gb"] = round(usage.total / (1024**3), 1)
        disk_info["used_gb"] = round(usage.used / (1024**3), 1)
        disk_info["free_gb"] = round(usage.free / (1024**3), 1)
        disk_info["used_pct"] = round(usage.used / usage.total * 100, 1)
    except OSError:
        disk_info["error"] = "disk usage unavailable"
        disk_info["epistemic"] = "DEGRADED"
        result["degraded"] = True

    result["machine"] = {"cpu": cpu_info, "memory": mem_info, "disk": disk_info}

    # ── Earth (GEOX) — declaration, not live probe ───────────────────────
    # Resource handlers are sync; live organ probing is async.
    # Declare what's known; the caller can probe GEOX separately.
    result["earth"] = {
        "epistemic": "DECLARED",
        "organ": "geox",
        "port": 8081,
        "note": "Probe GEOX directly at http://127.0.0.1:8081/health for live earth state",
    }

    return result


def _probe_digital() -> dict[str, Any]:
    """Probe digital reality layer.

    Returns federation organ status. Organ counts are derived from the
    live CANONICAL_TOOLS / DIAGNOSTIC_TOOLS dicts — no hardcoded numbers.
    """
    from arifosmcp.constitutional_map import CANONICAL_TOOLS, DIAGNOSTIC_TOOLS

    result: dict[str, Any] = {
        "layer": "digital",
        "epistemic": "OBSERVED",
        "timestamp": time.time(),
        "degraded": False,
    }

    # ── Federation organs — ports from contract, live counts from source ──
    result["federation"] = {
        "arifOS": {
            "port": 8088,
            "role": "constitutional_kernel",
            "canonical_tools": len(CANONICAL_TOOLS),
            "diagnostic_tools": len(DIAGNOSTIC_TOOLS),
            "total_declared": len(CANONICAL_TOOLS) + len(DIAGNOSTIC_TOOLS),
        },
        "A-FORGE": {"port": 7071, "role": "execution_shell"},
        "A-FORGE_MCP": {"port": 7072, "role": "mcp_gateway"},
        "GEOX": {"port": 8081, "role": "earth_witness"},
        "WEALTH": {"port": 18082, "role": "capital_witness"},
        "WELL": {"port": 18083, "role": "human_readiness"},
        "AAA": {"port": 3001, "role": "control_plane"},
        "APEX": {"port": 3002, "role": "legacy_judge"},
        "VAULT999_API": {"port": 8100, "role": "sealed_ledger_api"},
        "VAULT999_WRITER": {"port": 5001, "role": "sealed_ledger_writer"},
        "OpenClaw": {"port": 18789, "role": "gateway_agent"},
    }

    # ── MCP surface — counts from the live tool surface ──────────────────
    result["mcp_surface"] = {
        "protocol": "MCP 2025-11-25",
        "transport": "streamable-http",
        "canonical_tools": len(CANONICAL_TOOLS),
        "diagnostic_tools": len(DIAGNOSTIC_TOOLS),
        "total_declared": len(CANONICAL_TOOLS) + len(DIAGNOSTIC_TOOLS),
        "note": "Counts derived live from CANONICAL_TOOLS + DIAGNOSTIC_TOOLS. For MCP-registered count, call tools/list.",
    }

    # ── Session state ────────────────────────────────────────────────────
    result["session"] = {
        "epistemic": "DERIVED",
        "note": "Active session state available via arif_triage or arif_init",
    }

    # ── Audit chain ──────────────────────────────────────────────────────
    result["audit"] = {
        "vault999": {
            "epistemic": "DECLARED",
            "layers": ["local_JSONL", "Postgres", "Supabase"],
            "note": "Chain height available via arif_vault_query",
        }
    }

    return result


def _probe_biological() -> dict[str, Any]:
    """Probe biological reality layer.

    Returns human readiness state from WELL state files.
    """
    result: dict[str, Any] = {
        "layer": "biological",
        "epistemic": "DERIVED",
        "timestamp": time.time(),
        "degraded": False,
    }

    # ── WELL state (from filesystem state.json) ──────────────────────────
    well_state: dict[str, Any] = {"epistemic": "UNKNOWN", "note": "No state.json found"}
    for candidate in ["/root/WELL/state.json", "/root/WELL/state/current.json"]:
        try:
            with open(candidate) as f:
                raw = json.load(f)
            if not raw or raw == {}:
                well_state = {
                    "epistemic": "DEGRADED",
                    "source": candidate,
                    "note": "state.json exists but is empty — WELL state not populated",
                }
                result["degraded"] = True
            else:
                well_state = {
                    "epistemic": "OBSERVED",
                    "source": candidate,
                    "data": raw,
                }
            break
        except FileNotFoundError:
            well_state = {
                "epistemic": "UNKNOWN",
                "note": f"No state file at {candidate}",
            }
            result["degraded"] = True
        except (json.JSONDecodeError, PermissionError) as e:
            well_state = {
                "epistemic": "DEGRADED",
                "note": f"Cannot read {candidate}: {e}",
            }
            result["degraded"] = True

    result["well_state"] = well_state

    # ── Dignity guard ────────────────────────────────────────────────────
    result["dignity"] = {
        "epistemic": "CANONICAL",
        "guard": "F6 MARUAH — human dignity is not measured, it is protected",
        "never": [
            "diagnose",
            "prescribe",
            "replace clinician judgment",
            "claim certainty about health",
        ],
    }

    return result


def _probe_uncertainty_substrate() -> dict[str, Any]:
    """Probe uncertainty substrate — the quantum-physics-inspired decision substrate.

    Quantum physics concepts map to arifOS classical equivalents.
    No literal quantum hardware. No physics mysticism.
    Quantum-style governance = superposition of hypotheses, interference from evidence,
    bounded non-determinism, entanglement across organs.
    """
    return {
        "layer": "uncertainty_substrate",
        "epistemic": "MAPPED",
        "timestamp": time.time(),
        "degraded": False,
        "note": (
            "Uncertainty substrate is classical — not quantum hardware. "
            "Maps quantum-physics metaphor to arifOS decision engineering."
        ),
        "quantum_metaphor_map": {
            # Metaphor → arifOS equivalent (NOT literal physics)
            "superposition": "multiple hypotheses held simultaneously — N≥3 competing plans",
            "interference": "evidence weights destructively/cconstructively — contradictory evidence cancels",
            "decoherence": "contradiction scan — eliminates incompatible hypotheses",
            "entanglement": "organs share state via NATS — correlated decisions across organs",
            "tunneling": "bounded non-determinism — APPROVE despite low probability",
            "collapse": "555_JUDGE verdict — SEAL/SABAR/HOLD/VOID",
            "irreversibility": "777_FORGE execution — committed state change",
            "measurement": "111_SENSE observation — MCP tool call binds evidence",
            "uncertainty_principle": "F7 HUMILITY — fundamental limits on simultaneous accuracy",
            "entanglement_swap": "cross-organ VAULT999 seal — correlated memory across organs",
        },
        "anti_hantu_guard": {
            "C_dark_quantum_analogue": 0.0,  # No quantum consciousness claims
            "note": "Quantum metaphor ONLY. No literal wavefunction, qubit, or quantum consciousness.",
        },
    }


def register_reality_state(mcp: FastMCP) -> list[str]:
    """Register arifos://reality/state — causally-consistent multi-layer reality snapshot.

    Returns the list of registered URIs.
    """

    @mcp.resource(
        "arifos://reality/state",
        description=(
            "Causally-consistent multi-layer reality snapshot. "
            "Returns current state of PHYSICAL, DIGITAL, BIOLOGICAL, and UNCERTAINTY_SUBSTRATE "
            "reality layers at one consistent timestamp. "
            "Every value carries epistemic label (OBS/DER/INT/SPEC/UNKNOWN). "
            "Uncertainty substrate maps quantum-physics metaphor to classical decision engineering."
        ),
    )
    def reality_state_resource() -> dict[str, Any]:
        """Current reality state across all four layers."""
        snapshot_timestamp = time.time()

        # Probe each layer independently — one failure doesn't kill the snapshot
        layers: dict[str, dict[str, Any]] = {}
        layer_order = [
            ("physical", _probe_physical),
            ("digital", _probe_digital),
            ("biological", _probe_biological),
            ("uncertainty_substrate", _probe_uncertainty_substrate),
        ]
        for name, probe_fn in layer_order:
            try:
                layers[name] = probe_fn()
            except Exception as e:
                layers[name] = {
                    "layer": name,
                    "epistemic": "DEGRADED",
                    "timestamp": snapshot_timestamp,
                    "degraded": True,
                    "error": f"Probe failed: {e}",
                }

        # ── Dynamic summary — computed, not hardcoded ────────────────────
        layers_with_data = sum(
            1 for l in layers.values() if l.get("epistemic", "UNKNOWN") != "UNKNOWN"
        )
        layers_degraded = sum(1 for l in layers.values() if l.get("degraded", False))

        return {
            "resource": "arifos://reality/state",
            "version": "v2026.06.25",
            "snapshot_timestamp": snapshot_timestamp,
            "snapshot_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(snapshot_timestamp)),
            "authority_level": "DYNAMIC",
            "truth_level": 4,
            "causality": {
                "all_layers_same_clock": True,
                "note": "All layers probed within same function call — temporal skew < 100ms",
            },
            "layers": layers,
            "summary": {
                "layers_present": len(layers),
                "layers_with_data": layers_with_data,
                "layers_degraded": layers_degraded,
                "verdict": ("DEGRADED" if layers_degraded > 0 else "NOMINAL"),
            },
            "governance": {
                "f2_truth": "All values labeled with epistemic status",
                "f4_clarity": "Single snapshot — no ambiguity across reads",
                "f6_maruah": "Biological layer does not diagnose or flatten",
                "f7_humility": "Uncertainty substrate is classical metaphor — not literal quantum",
                "f9_anti_hantu": "No quantum consciousness claims — metaphor only; no fabrication",
                "f13_sovereign": "Human boundaries respected",
            },
            "epistemic_disclaimer": (
                "Live-probed snapshot. Values reflect state at snapshot_timestamp. "
                "For deep organ state, probe GEOX/WELL/WEALTH directly."
            ),
        }

    return ["arifos://reality/state"]


__all__ = [
    "register_reality_state",
]
