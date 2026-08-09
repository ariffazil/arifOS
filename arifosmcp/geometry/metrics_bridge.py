"""
metrics_bridge.py — Wire MAP · ATLAS · ECHO into ATLAS333 activation (not content).

Two ATLAS entities (do not merge):
  ATLAS333  = 35 paradoxes, cognitive geometry (333 reasoning substrate)
  ATLAS metric = Authority-to-Landscape compression (governance telemetry)

Wiring only:
  1. ECHO → tension weights on paradox activation (live vectors, static content)
  2. MAP  → top_k / density of paradox injection
  3. Surface both via arifos://atlas333/metrics (read-only, deterministic)

F2: read computed state file or recompute via map-atlas-echo — no fabrication.
F8: read-only bridge; does not mutate paradox catalog.
F4: single module, structured output.

Future (post noise-floor): ECHO honest_observations may read Kabarkan/PG
tool traces — not manual ledgers alone. FREEZE: do not auto-mutate paradox
content from Kabarkan; tension weights only after calibration.
Double helix: ECHO=right strand agent learning; SCAR=left strand human.
See /root/AAA/governance/DOUBLE_HELIX_ECHO_SCAR.md

DITEMPA BUKAN DIBERI — 2026-08-09
"""
from __future__ import annotations

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger("arifosmcp.metrics_bridge")

METRICS_PATH = Path("/root/AAA/state/map_atlas_echo.json")
MAP_ATLAS_ECHO_SCRIPT = Path("/root/scripts/map-atlas-echo.py")

# Axis clusters (IDs only — never rewrite paradox text)
MEMORY_IDS = list(range(1, 12))  # P1–P11
MIND_IDS = list(range(12, 23))  # P12–P22
JUDGE_IDS = list(range(23, 34))  # P23–P33
CONTOUR_IDS = [34, 35]  # P34–P35
# Compression-critical memory pole (Remember ↔ Forget)
P_REMEMBER_FORGET = 2


def load_institutional_metrics(*, recompute: bool = False) -> dict[str, Any]:
    """Load MAP/ATLAS/ECHO. Prefer written state; optional recompute.

    Returns empty shell with epistemic=UNMEASURED if unavailable (never fake).
    """
    if recompute and MAP_ATLAS_ECHO_SCRIPT.exists():
        try:
            subprocess.run(
                [sys.executable, str(MAP_ATLAS_ECHO_SCRIPT), "--write", "--quiet"],
                check=False,
                timeout=60,
                capture_output=True,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("metrics recompute failed: %s", exc)

    if METRICS_PATH.exists():
        try:
            data = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("schema", "").startswith("map_atlas_echo"):
                data["_source"] = str(METRICS_PATH)
                data["_epistemic"] = "OBS"
                return data
        except Exception as exc:  # noqa: BLE001
            logger.warning("metrics read failed: %s", exc)

    return {
        "schema": "map_atlas_echo.v1",
        "MAP": {"value": None, "band": "UNMEASURED"},
        "ATLAS": {"value": None, "band": "UNMEASURED"},
        "ECHO": {"value": None, "band": "UNMEASURED", "honest_observations": 0},
        "HERMES": {"value": None, "band": "UNMEASURED"},
        "_source": None,
        "_epistemic": "UNMEASURED",
        "note": "No map_atlas_echo state; run map-atlas-echo --write",
    }


def map_calibrate_top_k(base_k: int = 5, metrics: dict[str, Any] | None = None) -> dict[str, Any]:
    """MAP → paradox selection density.

    Low MAP (poor reality compression / thrash) → inject MORE paradoxes (force tension).
    High MAP → FEWER paradoxes (avoid over-thinking).
    """
    m = metrics if metrics is not None else load_institutional_metrics()
    map_block = m.get("MAP") or {}
    map_val = map_block.get("value")
    band = str(map_block.get("band") or "UNMEASURED")

    if map_val is None:
        return {
            "top_k": base_k,
            "map_value": None,
            "map_band": band,
            "rule": "UNMEASURED → default top_k",
            "delta": 0,
        }

    if map_val < 0.35 or band == "LOW":
        top_k = min(12, base_k + 4)
        rule = "MAP_LOW → denser paradox injection (force reasoning)"
        delta = top_k - base_k
    elif map_val < 0.7 or band == "MID":
        top_k = base_k + 1
        rule = "MAP_MID → slight denser injection"
        delta = 1
    else:
        top_k = max(3, base_k - 1)
        rule = "MAP_HIGH → sparser paradox injection (avoid over-thinking)"
        delta = top_k - base_k

    return {
        "top_k": top_k,
        "map_value": map_val,
        "map_band": band,
        "rule": rule,
        "delta": delta,
        "base_k": base_k,
    }


def echo_tension_weights(metrics: dict[str, Any] | None = None) -> dict[str, Any]:
    """ECHO → live tension weights on paradox IDs (content unchanged).

    Honest Observations (HO) and ECHO band steer which axes heat up:
      - Memory HO / low retain → heat Memory cluster, especially P2 Remember/Forget
      - Governance / gate hits → heat Judge cluster
      - Blind ECHO → heat Contour (P34/P35) lightly — need visibility before seal

    Returns multipliers defaulting to 1.0; never deletes paradoxes.
    """
    m = metrics if metrics is not None else load_institutional_metrics()
    echo = m.get("ECHO") or {}
    band = str(echo.get("band") or "UNMEASURED")
    components = echo.get("components") or {}
    weights: dict[int, float] = {i: 1.0 for i in range(1, 36)}

    # Visibility reward path: more HO on memory-ish signals → live P2
    vault_anom = float(components.get("vault_anomaly_tags_capped") or 0)
    gate_hits = float(components.get("gate_honest_hits") or 0)
    diagnose = float(components.get("rsi_diagnose_obs") or 0)
    ri = float(echo.get("retained_improvements") or 0)
    ho = float(echo.get("honest_observations") or 0)

    # Memory axis heat from anomaly visibility without retention
    memory_heat = 1.0
    if ho > 0 and ri / ho < 0.15:
        memory_heat = 1.35  # sees but weak retain
    if vault_anom > 50 or diagnose > 10:
        memory_heat = max(memory_heat, 1.25)
    if band in ("SEEN_NO_RETAIN", "LOW"):
        memory_heat = max(memory_heat, 1.4)
    if band == "BLIND":
        # Blind: do not fake heat on memory; push contour visibility
        memory_heat = 1.0
        for pid in CONTOUR_IDS:
            weights[pid] = 1.3

    for pid in MEMORY_IDS:
        weights[pid] = memory_heat
    # P2 Remember/Forget — Compression + ECHO doctrine exemplar
    weights[P_REMEMBER_FORGET] = max(weights[P_REMEMBER_FORGET], memory_heat + 0.15)

    # Judge heat from gate honesty (institution seeing governance tension)
    if gate_hits > 0:
        judge_heat = 1.0 + min(0.4, gate_hits / 50.0)
        for pid in JUDGE_IDS:
            weights[pid] = max(weights[pid], judge_heat)

    # ATLAS metric (governance compression) — if LOW, heat Judge more
    atlas = m.get("ATLAS") or {}
    if str(atlas.get("band") or "") == "LOW":
        for pid in JUDGE_IDS:
            weights[pid] = max(weights[pid], 1.25)

    return {
        "weights": weights,
        "echo_band": band,
        "echo_value": echo.get("value"),
        "honest_observations": ho,
        "retained_improvements": ri,
        "memory_heat": memory_heat,
        "p2_weight": weights[P_REMEMBER_FORGET],
        "rule": "ECHO honest observations heat axes; paradox text immutable",
    }


def apply_tension_to_paradoxes(
    paradoxes: list[dict[str, Any]],
    metrics: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Re-rank active paradox list by score × ECHO tension weight.

    Does not invent paradoxes. Only reorders / annotates.
    """
    if not paradoxes:
        return paradoxes
    if paradoxes and isinstance(paradoxes[0], dict) and paradoxes[0].get("error"):
        return paradoxes

    tw = echo_tension_weights(metrics)
    weights: dict[int, float] = tw["weights"]

    enriched: list[dict[str, Any]] = []
    for p in paradoxes:
        if not isinstance(p, dict):
            continue
        raw_id = p.get("paradox_id") or p.get("id") or "?"
        try:
            # ids may be "P2" or 2
            sid = str(raw_id).lstrip("Pp")
            pid = int(sid) if sid.isdigit() else None
        except (TypeError, ValueError):
            pid = None
        base = float(p.get("score") or 0.5)
        w = weights.get(pid, 1.0) if pid is not None else 1.0
        q = dict(p)
        q["tension_weight"] = round(w, 4)
        q["tension_score"] = round(base * w, 4)
        q["tension_live"] = w > 1.01
        if pid == P_REMEMBER_FORGET:
            q["echo_wire"] = "P2_REMEMBER_FORGET ← ECHO visibility"
        enriched.append(q)

    enriched.sort(key=lambda x: float(x.get("tension_score") or 0), reverse=True)
    return enriched


def metrics_resource_payload(*, recompute: bool = False) -> dict[str, Any]:
    """Deterministic read-only payload for arifos://atlas333/metrics."""
    m = load_institutional_metrics(recompute=recompute)
    cal = map_calibrate_top_k(5, m)
    tw = echo_tension_weights(m)
    # compact weights for wire (only heated axes)
    heated = {str(k): v for k, v in tw["weights"].items() if v > 1.01}
    return {
        "uri": "arifos://atlas333/metrics",
        "schema": "atlas333_metrics_bridge.v1",
        "epistemic": m.get("_epistemic", "OBS"),
        "f_binding": {
            "F2": "deterministic from map_atlas_echo state or recompute",
            "F8": "read-only — no paradox mutation",
            "F4": "wiring layer only; 35 paradoxes immutable",
        },
        "disambiguation": {
            "ATLAS333": "35 paradoxes · cognitive geometry · 333 substrate",
            "ATLAS_metric": "Authority-to-Landscape · governance telemetry",
            "same_name": False,
            "connected_via": "this bridge",
        },
        "MAP": m.get("MAP"),
        "ATLAS": m.get("ATLAS"),
        "ECHO": m.get("ECHO"),
        "HERMES": m.get("HERMES"),
        "wiring": {
            "map_to_paradox_selection": cal,
            "echo_to_tension": {
                "echo_band": tw["echo_band"],
                "echo_value": tw["echo_value"],
                "honest_observations": tw["honest_observations"],
                "memory_heat": tw["memory_heat"],
                "p2_weight": tw["p2_weight"],
                "heated_axes": heated,
                "rule": tw["rule"],
            },
        },
        "source": m.get("_source"),
        "ts": m.get("ts"),
        "seal": "DITEMPA BUKAN DIBERI",
    }
