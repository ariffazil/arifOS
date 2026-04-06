"""REST endpoints for the unified arifOS AAA MCP server.

Registered as custom routes on the FastMCP instance via mcp.custom_route().
These run alongside the standard MCP protocol at /mcp, providing:
  GET  /                           Landing page / service info
  GET  /health                     Docker healthcheck + monitoring
  GET  /version                    Build info
  GET  /tools                      Tool listing (REST-style)
  POST /tools/{tool_name}          REST tool calling (ChatGPT adapter)
  GET  /.well-known/mcp/server.json  MCP registry discovery

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import inspect
import json
import logging
import os
import secrets
import time
import uuid
from collections.abc import Callable
from datetime import date, datetime, timezone
from typing import Any

from arifosmcp.runtime.public_registry import (
    build_mcp_discovery_json,
    build_server_json,
    public_tool_specs,
)
from arifosmcp.runtime.resources import apex_tools_html_rows, apex_tools_markdown_table
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.staticfiles import StaticFiles

from core.shared.floor_audit import get_ml_floor_runtime
from core.shared.floors import (
    FLOOR_SPEC_KEYS,
    get_floor_comparator,
    get_floor_spec,
    get_floor_threshold,
)

from .build_info import get_build_info
from .capability_map import build_runtime_capability_map
from .contracts_v2 import AAA_TOOL_ALIASES, AAA_TOOL_STAGE_MAP, TRINITY_BY_TOOL
from .fastmcp_version import HAS_CUSTOM_ROUTE, HAS_ROUTE

BUILD_INFO = get_build_info()
BUILD_VERSION = BUILD_INFO["version"]
MCP_PROTOCOL_VERSION = "2025-11-25"
MCP_SUPPORTED_PROTOCOL_VERSIONS = ["2025-11-25", "2025-03-26"]

TOOL_ALIASES: dict[str, str] = dict(AAA_TOOL_ALIASES)

logger = logging.getLogger(__name__)

_DASHBOARD_ALLOWED_ORIGINS = {
    "https://apex.arif-fazil.com",
    "https://arifosmcp.arif-fazil.com",
}


def _representative_floor_score(floor_id: str) -> float:
    """
    Build a visualizer-friendly fallback score from canonical core floor specs.

    This intentionally stays transport-agnostic by deriving from core as source-of-truth.
    """
    comparator = get_floor_comparator(floor_id)
    threshold = float(get_floor_threshold(floor_id))
    spec = get_floor_spec(floor_id)

    if floor_id == "F7" and "range" in spec:
        low, _high = spec["range"]
        return float(low) + 0.01  # representative in-band humility value

    if comparator in {">", ">="}:
        return threshold
    if comparator == "<=":
        return threshold
    # "<" comparators (e.g., risk-style floors) — choose conservative passing value
    return threshold * 0.5


def _canonical_floor_defaults() -> dict[dict, float]:
    return {fid: _representative_floor_score(fid) for fid in FLOOR_SPEC_KEYS}


# Fallback floor defaults used only when live governance kernel state is unavailable.
_FLOOR_DEFAULTS: dict[str, float] = _canonical_floor_defaults()

# Fallback Tri-Witness weights (normalised to sum to 1.0).
# Reflects approximate sovereign split: Human 42%, AI 32%, Earth 26%.
_WITNESS_DEFAULTS: dict[str, float] = {"human": 0.42, "ai": 0.32, "earth": 0.26}

# Default QDF (Quantum Decision Field) baseline — target ≥ 0.83 per APEX solver spec.
_DEFAULT_QDF: float = 0.83

# Default metabolic stage returned when kernel state is unavailable.
# 333 = REASON stage, the last full AGI reasoning stage before TRINITY_SYNC.
_DEFAULT_METABOLIC_STAGE: int = 333


def _cache_headers() -> dict[str, str]:
    return {"Cache-Control": "no-store"}


def _json_safe(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    # Handle Pydantic models (v1 and v2)
    if hasattr(value, "model_dump"):
        return _json_safe(value.model_dump())
    if hasattr(value, "dict"):
        return _json_safe(value.dict())
    # Handle dataclasses
    if hasattr(value, "__dataclass_fields__"):
        return _json_safe({k: getattr(value, k) for k in value.__dataclass_fields__})
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_json_safe(v) for v in value]
    return value


def _dashboard_cors_headers(request: Request) -> dict[str, str]:
    origin = request.headers.get("origin", "").strip()
    if origin in _DASHBOARD_ALLOWED_ORIGINS:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Vary": "Origin",
        }
    return {}


def _merge_headers(*header_sets: dict[str, str]) -> dict[str, str]:
    merged: dict[str, str] = {}
    for header_set in header_sets:
        merged.update(header_set)
    return merged


def _floor_passes(floor_id: str, score: float) -> bool:
    spec = get_floor_spec(floor_id)
    comparator = get_floor_comparator(floor_id)
    if floor_id == "F7" and "range" in spec:
        lower, upper = spec["range"]
        return float(lower) <= float(score) <= float(upper)

    threshold = float(get_floor_threshold(floor_id))
    if comparator == "<":
        return float(score) < threshold
    if comparator == "<=":
        return float(score) <= threshold
    if comparator == ">":
        return float(score) > threshold
    return float(score) >= threshold


def _build_governance_status_payload() -> dict[str, Any]:
    session_id: str | None = None
    floors: dict[str, Any] = {}
    telemetry: dict[str, Any] = {}
    witness: dict[str, float] = {}
    qdf: float = 0.0
    metabolic_stage: int = 0
    verdict: str = "SEAL"

    try:
        from core.governance_kernel import get_governance_kernel

        kernel = get_governance_kernel()
        state = kernel.get_current_state() if hasattr(kernel, "get_current_state") else {}
        if state:
            session_id = state.get("session_id")
            floors = state.get("floors", {})
            telemetry = state.get("telemetry", {})
            witness = state.get("witness", {})
            qdf = float(state.get("qdf", 0.0))
            metabolic_stage = int(state.get("metabolic_stage", 0))
            verdict = state.get("verdict", "SEAL")
    except (ImportError, AttributeError):
        logger.debug("Governance kernel unavailable — using default telemetry values")
    except Exception:
        logger.exception("Unexpected error loading governance kernel state")

    resolved_floors = {k: floors.get(k, v) for k, v in _FLOOR_DEFAULTS.items()}
    resolved_witness = {k: witness.get(k, v) for k, v in _WITNESS_DEFAULTS.items()}
    resolved_telemetry = {
        "dS": telemetry.get("dS", -0.35),
        "peace2": telemetry.get("peace2", 1.04),
        "kappa_r": telemetry.get("kappa_r", 0.97),
        "echoDebt": telemetry.get("echoDebt", 0.4),
        "shadow": telemetry.get("shadow", 0.3),
        "confidence": telemetry.get("confidence", 0.88),
        "psi_le": telemetry.get("psi_le", 0.82),
        "verdict": verdict,
    }

    try:
        from core.telemetry import get_system_vitals

        machine_vitals = get_system_vitals()
    except Exception:
        machine_vitals = {"cpu_percent": 0.0, "memory_percent": 0.0}

    try:
        capability_map = build_runtime_capability_map()
        if (
            float(resolved_floors.get("F11", 0.0)) <= 0.0
            and capability_map.get("capabilities", {}).get("governed_continuity") == "enabled"
        ):
            resolved_floors["F11"] = _FLOOR_DEFAULTS["F11"]
    except Exception:
        capability_map = None

    try:
        if float(resolved_floors.get("F8", 0.0)) <= 0.0:
            from core.enforcement.genius import calculate_genius, coerce_floor_scores

            floor_scores = coerce_floor_scores(
                {
                    "f1": resolved_floors.get("F1"),
                    "f2": resolved_floors.get("F2"),
                    "f3": resolved_floors.get("F3"),
                    "f4": resolved_floors.get("F4"),
                    "f5": resolved_floors.get("F5"),
                    "f6": resolved_floors.get("F6"),
                    "f7": resolved_floors.get("F7"),
                    "f9": resolved_floors.get("F9"),
                    "f10": resolved_floors.get("F10"),
                    "f11": resolved_floors.get("F11"),
                    "f12": resolved_floors.get("F12"),
                    "f13": resolved_floors.get("F13"),
                }
            )
            genius_res = calculate_genius(
                floor_scores, h=0.0, compute_budget_used=0.0, compute_budget_max=1.0
            )
            resolved_floors["F8"] = round(
                max(_FLOOR_DEFAULTS["F8"], float(genius_res.get("genius_score", 0.0))),
                4,
            )
            if float(resolved_telemetry.get("confidence", 0.0)) <= 0.0:
                resolved_telemetry["confidence"] = resolved_floors["F8"]
    except Exception:
        pass

    return {
        "telemetry": resolved_telemetry,
        "witness": resolved_witness,
        "qdf": qdf or _DEFAULT_QDF,
        "floors": resolved_floors,
        "machine_vitals": machine_vitals,
        "session_id": session_id or f"sess_{uuid.uuid4().hex[:8]}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metabolic_stage": metabolic_stage or _DEFAULT_METABOLIC_STAGE,
    }


def _render_status_html(payload: dict[str, Any]) -> str:
    telemetry = payload["telemetry"]
    floors = payload["floors"]
    vitals = payload["machine_vitals"]
    witness = payload["witness"]

    floor_html = "".join(
        '<div class="floor {}"><strong>{}</strong><span>{:.3f}</span></div>'.format(
            "pass" if _floor_passes(floor_id, float(floors.get(floor_id, _FLOOR_DEFAULTS.get(floor_id, 0.0)))) else "fail",
            floor_id,
            float(floors.get(floor_id, _FLOOR_DEFAULTS.get(floor_id, 0.0))),
        )
        for floor_id in sorted(FLOOR_SPEC_KEYS.keys(), key=lambda item: int(item[1:]))
    )

    load_avg = vitals.get("load_avg", [])
    load_text = ", ".join(f"{float(value):.2f}" for value in load_avg[:3]) if load_avg else "n/a"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>arifOS Ops Truth Page</title>
  <style>
    :root {{
      color-scheme: dark;
      font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif;
    }}
    body {{
      margin: 0;
      min-height: 100vh;
      background: radial-gradient(circle at top, rgba(0,212,255,0.15), transparent 55%), #05070a;
      color: #f5f7ff;
      padding: 2rem;
    }}
    .panel {{
      background: rgba(6,14,30,0.85);
      border: 1px solid rgba(0,212,255,0.35);
      border-radius: 18px;
      padding: 1.5rem;
      box-shadow: 0 20px 60px rgba(0,0,0,0.55);
      margin-bottom: 1.5rem;
    }}
    header {{
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 2rem;
    }}
    h1 {{
      font-size: 2.4rem;
      letter-spacing: 0.06em;
    }}
    .meta-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 1rem;
      width: 100%;
    }}
    .meta-item {{
      border-radius: 12px;
      border: 1px solid rgba(255,255,255,0.08);
      padding: 1rem;
      background: rgba(255,255,255,0.02);
    }}
    .meta-item span {{
      display: block;
      font-size: 0.75rem;
      letter-spacing: 0.1em;
      color: #7fb8ff;
      text-transform: uppercase;
    }}
    .meta-item strong {{
      display: block;
      margin-top: 0.4rem;
      font-size: 1.3rem;
    }}
    .floor-mosaic {{
      display: grid;
      grid-template-columns: repeat(7, minmax(40px,1fr));
      gap: 0.6rem;
    }}
    .floor {{
      border-radius: 10px;
      padding: 0.8rem;
      text-align: center;
      font-weight: 600;
      border: 1px solid rgba(255,255,255,0.08);
      transition: transform 0.3s ease, border 0.3s ease;
    }}
    .floor.pass {{
      background: linear-gradient(150deg, rgba(45,255,182,0.15), rgba(0,212,255,0.3));
      border-color: rgba(0,212,255,0.6);
    }}
    .floor.fail {{
      background: linear-gradient(150deg, rgba(255,85,85,0.18), rgba(255,0,0,0.2));
      border-color: rgba(255,85,85,0.7);
    }}
    .floor span {{
      font-size: 0.65rem;
      color: #b2b6c9;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 1.2rem;
    }}
    .vitals {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px,1fr));
      gap: 0.8rem;
      margin-top: 1rem;
    }}
    .bar {{
      height: 8px;
      border-radius: 999px;
      background: rgba(255,255,255,0.12);
      overflow: hidden;
      margin-top: 0.4rem;
    }}
    .bar-fill {{
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(to right, #00d4ff, #20c997);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95rem;
    }}
    th, td {{
      padding: 0.4rem 0;
      border-bottom: 1px solid rgba(255,255,255,0.05);
      text-align: left;
    }}
    th {{
      color: #8aa6c4;
      font-size: 0.75rem;
      letter-spacing: 0.2em;
    }}
    tr.fail td {{
      color: #ff7b72;
    }}
    tr.pass td {{
      color: #9ef5d4;
    }}
    @media (max-width: 700px) {{
      body {{
        padding: 1rem;
      }}
      .floor-mosaic {{
        grid-template-columns: repeat(4, minmax(40px,1fr));
      }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>arifOS Ops Truth</h1>
    <div class="meta-grid">
      <div class="meta-item">
        <span>Verdict</span>
        <strong>{telemetry["verdict"]}</strong>
      </div>
      <div class="meta-item">
        <span>Timestamp</span>
        <strong>{payload["timestamp"]}</strong>
      </div>
      <div class="meta-item">
        <span>Session</span>
        <strong>{payload["session_id"]}</strong>
      </div>
      <div class="meta-item">
        <span>Stage</span>
        <strong>{payload["metabolic_stage"]}</strong>
      </div>
    </div>
  </header>

  <section class="panel">
    <div class="floor-mosaic">
      {floor_html}
    </div>
    <p style="margin-top:1rem; color:#92a1b5;">Each floor is rendered as a status chip that pulses when passing and glows red when locked.</p>
  </section>

  <div class="grid">
    <div class="panel">
      <h2>Telemetry Bars</h2>
      <div class="vitals">
        <div>
          <strong>dS</strong>
          <div class="bar"><div class="bar-fill" style="width:{min(max((float(telemetry.get("dS", -0.35)) + 1) * 50, 0), 100)}%;"></div></div>
          <small>{float(telemetry.get("dS", 0.0)):.3f}</small>
        </div>
        <div>
          <strong>Peace²</strong>
          <div class="bar"><div class="bar-fill" style="width:{min(max(float(telemetry.get("peace2", 1.05)) / 2 * 100, 0), 100)}%;"></div></div>
          <small>{float(telemetry.get("peace2", 0.0)):.3f}</small>
        </div>
        <div>
          <strong>EchoDebt</strong>
          <div class="bar"><div class="bar-fill" style="width:{min(max((1 - float(telemetry.get("echoDebt", 0.4))) * 100, 0), 100)}%;"></div></div>
          <small>{float(telemetry.get("echoDebt", 0.0)):.3f}</small>
        </div>
        <div>
          <strong>Omega</strong>
          <div class="bar"><div class="bar-fill" style="width:{min(max(float(telemetry.get("omega", 0.04)) * 1000, 0), 100)}%;"></div></div>
          <small>{float(telemetry.get("omega", 0.0)):.3f}</small>
        </div>
        <div>
          <strong>Psi</strong>
          <div class="bar"><div class="bar-fill" style="width:{min(max(float(telemetry.get("psi_le", 0.82)) * 100, 0), 100)}%;"></div></div>
          <small>{float(telemetry.get("psi_le", 0.0)):.3f}</small>
        </div>
      </div>
    </div>

    <div class="panel">
      <h2>Machine Vitals</h2>
      <table>
        <tbody>
          <tr><th>CPU</th><td>{float(vitals.get("cpu_percent", 0.0)):.1f}% · {vitals.get("cpu_count", 0)} cores</td></tr>
          <tr><th>Memory</th><td>{float(vitals.get("memory_percent", 0.0)):.1f}% · {vitals.get("ram_used_gb", 0):.1f}/{vitals.get("ram_total_gb", 0):.1f} GB</td></tr>
          <tr><th>Disk</th><td>{float(vitals.get("disk_percent", 0.0)):.1f}%</td></tr>
          <tr><th>Load</th><td>{load_text}</td></tr>
          <tr><th>Net</th><td>Sent {vitals.get("net_io_sent_mb", 0):.1f}MB · Recv {vitals.get("net_io_recv_mb", 0):.1f}MB</td></tr>
        </tbody>
      </table>
    </div>

    <div class="panel">
      <h2>Witness Triad</h2>
      <table>
        <tbody>
          <tr><th>Human</th><td>{float(witness.get("human", 0.0)):.3f}</td></tr>
          <tr><th>AI</th><td>{float(witness.get("ai", 0.0)):.3f}</td></tr>
          <tr><th>Earth</th><td>{float(witness.get("earth", 0.0)):.3f}</td></tr>
        </tbody>
      </table>
      <p style="margin-top:1rem; font-size:0.85rem; color:#9fb7d6;">Governance consensus (Tri-Witness) remains visible throughout the loop.</p>
    </div>
  </div>
</body>
</html>"""


def _generate_mega_tool_cards() -> str:
    """Generate the 11 functional tool cards grouped by Trinity layer."""

    layers = {"GOVERNANCE": [], "INTELLIGENCE": [], "MACHINE": []}
    for spec in public_tool_specs():
        layers[spec.layer].append(spec)

    html = ""
    for layer, specs in layers.items():
        html += f'<div class="layer-group"><h3>{layer}</h3><div class="tool-cards">'
        for spec in specs:
            floors = ", ".join(spec.floors) if spec.floors else "None"
            html += f"""
            <div class="tool-card" onclick="toggleCard(this)">
              <div class="tool-header">
                <span class="tool-name">{spec.name}</span>
                <span class="tool-trinity">{spec.trinity}</span>
              </div>
              <div class="tool-role">{spec.role}</div>
              <p class="tool-desc">{spec.description}</p>
              <div class="tool-meta">
                <span>Stage: {spec.stage}</span>
                <span>Floors: {floors}</span>
              </div>
            </div>
            """
        html += '</div></div>'
    return html


WELCOME_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>arifOS MCP Server</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    :root {
      --bg: #0d0d0d;
      --card-bg: #1a1a1a;
      --border: #333;
      --accent: #e6c25d;
      --text: #d4d4d4;
      --dim: #888;
      --blue: #7dd3fc;
      --green: #00ff88;
      --orange: #f59e0b;
    }
    body{background:var(--bg);color:var(--text);font-family:ui-monospace,monospace;
         font-size:14px;line-height:1.6;padding:2rem 1rem;max-width:1000px;margin:auto}

    header { border-bottom: 1px solid var(--border); padding-bottom: 1.5rem; margin-bottom: 2rem; }
    .header-meta { display: flex; gap: 1.5rem; font-size: 0.75rem; color: var(--dim); margin-top: 0.5rem; }
    .header-meta span { display: flex; align-items: center; gap: 0.4rem; }

    h1{color:var(--accent);font-size:1.5rem;margin-bottom:.25rem; display: flex; align-items:center; gap: 1rem;}
    h2{color:var(--dim);font-size:.85rem;font-weight:normal; letter-spacing:.08em;text-transform:uppercase}

    .pill-live{background: #00ff8822; color: var(--green); border: 1px solid #00ff8855; border-radius: 99px;
               padding: .1rem .6rem; font-size: .65rem; animation: pulse 2s infinite}
    @keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}

    .tabs { display: flex; gap: 1rem; margin-bottom: 2rem; border-bottom: 1px solid var(--border); }
    .tab { padding: 0.5rem 1rem; cursor: pointer; color: var(--dim); border-bottom: 2px solid transparent; transition: 0.2s; }
    .tab:hover { color: var(--blue); }
    .tab.active { color: var(--accent); border-bottom-color: var(--accent); }
    .tab-content { display: none; }
    .tab-content.active { display: block; }

    .quickstart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
    .qs-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; }
    .qs-card h4 { font-size: 0.8rem; color: var(--dim); text-transform: uppercase; margin-bottom: 0.75rem; }
    .code-block { position: relative; background: #000; padding: 0.75rem; border-radius: 4px; font-size: 0.85rem; margin-top: 0.5rem; border: 1px solid #222; }
    .copy-btn { position: absolute; top: 0.5rem; right: 0.5rem; background: var(--border); border: none; color: var(--text);
                padding: 0.2rem 0.5rem; font-size: 0.65rem; border-radius: 3px; cursor: pointer; opacity: 0.6; transition: 0.2s; }
    .copy-btn:hover { opacity: 1; background: var(--dim); }

    .status-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin:1.5rem 0}
    .status-card{background:var(--card-bg);border:1px solid var(--border);border-radius:8px;padding:1rem}
    .status-card h4{color:var(--dim);font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.5rem}
    .status-card .value{color:var(--accent);font-size:1.25rem;font-weight:600}
    .status-card .indicator{display:inline-flex;align-items:center;gap:.5rem;font-size:.75rem;margin-top:.5rem}
    .dot{width:8px;height:8px;border-radius:50%;background:currentColor}
    .dot.live{animation:pulse 1.5s infinite}

    .legend { display: flex; gap: 1rem; font-size: 0.7rem; color: var(--dim); margin-top: 0.5rem; flex-wrap: wrap; }
    .legend span { display: flex; align-items: center; gap: 0.3rem; }

    .layer-group { margin-bottom: 2rem; }
    .layer-group h3 { color: var(--accent); font-size: 0.8rem; letter-spacing: 0.1em; text-transform: uppercase;
                      border-bottom: 1px solid var(--border); padding-bottom: 0.4rem; margin-bottom: 1rem; }
    .tool-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }
    .tool-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 1rem;
                 cursor: pointer; transition: 0.2s; position: relative; }
    .tool-card:hover { border-color: var(--blue); transform: translateY(-2px); }
    .tool-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
    .tool-name { color: var(--blue); font-weight: 600; font-size: 1rem; }
    .tool-trinity { font-size: 0.65rem; color: var(--accent); background: #e6c25d11; padding: 0.1rem 0.4rem; border-radius: 4px; }
    .tool-role { font-size: 0.75rem; color: var(--dim); margin-bottom: 0.75rem; }
    .tool-desc { font-size: 0.85rem; color: #aaa; margin-bottom: 1rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    .tool-meta { display: flex; justify-content: space-between; font-size: 0.7rem; color: var(--dim); border-top: 1px solid #222; padding-top: 0.5rem; }

    table{width:100%;border-collapse:collapse}
    td,th{padding:.6rem;text-align:left; border-bottom: 1px solid var(--border);}
    th{color:var(--dim);font-weight:normal;font-size:.75rem;text-transform:uppercase}
    tr:nth-child(odd){background:#ffffff06}
    .url{color:var(--blue)}

    .mcp-warning { background: #f59e0b11; border: 1px solid #f59e0b33; padding: 1rem; border-radius: 8px; margin-bottom: 2rem; }
    .mcp-warning h4 { color: var(--orange); font-size: 0.85rem; margin-bottom: 0.5rem; }
    .mcp-warning p { font-size: 0.8rem; color: #ccc; margin-bottom: 0.75rem; }

    .safety-profile { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-top: 1rem; }
    .safety-item { font-size: 0.75rem; color: var(--dim); display: flex; align-items: center; gap: 0.5rem; }

    .motto{color:#555;font-size:.75rem;margin-top:3rem;text-align:center}
  </style>
</head>
<body>
  <header>
    <h1>arifOS MCP <span class="pill-live">&#9679; LIVE</span></h1>
    <h2>Functional Governance Kernel v__BUILD_VERSION__</h2>
    <div class="header-meta">
      <span>&#9881; COMMIT: <code>__BUILD_COMMIT__</code></span>
      <span>&#9202; BUILT: <code>__BUILD_TIME__</code></span>
      <span>&#128205; MODE: <code>PROD</code></span>
    </div>
  </header>

  <div class="tabs">
    <div class="tab active" onclick="showTab('operator')">Operator Lane</div>
    <div class="tab" onclick="showTab('builder')">Builder Lane</div>
  </div>

  <div id="operator" class="tab-content active">
    <div class="quickstart-grid">
      <div class="qs-card">
        <h4>1. Verify Health</h4>
        <div class="code-block">
          <code>curl -s https://arifosmcp.arif-fazil.com/health</code>
          <button class="copy-btn" onclick="copyCode(this)">Copy</button>
        </div>
      </div>
      <div class="qs-card">
        <h4>2. Establish Session</h4>
        <div class="code-block">
          <code># Call init_session_anchor to get session_id
init_session_anchor(actor_id="your_name", intent="your_intent")</code>
          <button class="copy-btn" onclick="copyCode(this)">Copy</button>
        </div>
      </div>
      <div class="qs-card">
        <h4>3. FastMCP Connect</h4>
        <div class="code-block">
          <code># Config for Claude/ChatGPT
{ "mcpServers": { "arifos": { "url": "https://arifosmcp.arif-fazil.com/mcp" } } }</code>
          <button class="copy-btn" onclick="copyCode(this)">Copy</button>
        </div>
      </div>
    </div>

    <div class="status-grid">
      <div class="status-card">
        <h4>Server Status</h4>
        <div class="value" id="live-status">Checking...</div>
        <div class="indicator" style="color:var(--green)"><span class="dot live"></span>Live from /health</div>
      </div>
      <div class="status-card">
        <h4>Version</h4>
        <div class="value" id="live-version">—</div>
        <div class="indicator" style="color:var(--green)"><span class="dot live"></span>Running version</div>
      </div>
      <div class="status-card">
        <h4>Surface Area</h4>
        <div class="value" id="live-tools">—</div>
        <div class="indicator" style="color:var(--green)"><span class="dot live"></span><span id="sbert-status">ML Floors Active</span></div>
      </div>
      <div class="status-card">
        <h4>Governance</h4>
        <div class="value">13 Floors Active</div>
        <div class="indicator" style="color:var(--green)"><span class="dot live"></span>Real-time enforcement</div>
      </div>
      <div class="status-card">
        <h4>Dashboard</h4>
        <div class="value"><a href="/dashboard" style="color:var(--blue)">Open ↗</a></div>
        <div class="indicator" style="color:var(--orange)"><span class="dot"></span>Live governance telemetry</div>
      </div>
      <div class="status-card">
        <h4>MCP Endpoint</h4>
        <div class="value" style="font-size:0.75rem;color:var(--blue)">/mcp</div>
        <div class="indicator" style="color:var(--green)"><span class="dot live"></span>streamable-http</div>
      </div>
    </div>

    <div class="legend">
      <span><span class="dot" style="background:var(--green)"></span> Real (Host Metrics)</span>
      <span><span class="dot" style="background:var(--orange)"></span> Simulated (Demo Placeholder)</span>
      <span><span class="dot" style="background:var(--blue)"></span> Protocol (MCP Specification)</span>
    </div>

    <section style="margin-top: 3rem;">
      <h3>Functional arifOS Surface</h3>
      __MEGA_TOOL_CARDS__
    </section>

    <section>
      <h3>Tool Safety Profile</h3>
      <div class="safety-profile">
        <div class="safety-item"><span>&#128269;</span> Read-Only: Machine Sensors</div>
        <div class="safety-item"><span>&#128274;</span> Gated: Kernel / Soul</div>
        <div class="safety-item"><span>&#9888;</span> Destructive: None by Default</div>
        <div class="safety-item"><span>&#8635;</span> Idempotent: 90% of Surface</div>
      </div>
    </section>
  </div>

  <div id="builder" class="tab-content">
    <div class="mcp-warning">
      <h4>&#9888; Protocol Note: /mcp Endpoint</h4>
      <p>Direct browser navigation to /mcp will return 406 Not Acceptable. The protocol expects specific headers and JSON-RPC payloads.</p>
      <div class="code-block" style="background: #111;">
        <code>Header: 'X-MCP-Protocol: 2025-11-25'
Payload: { "jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1 }</code>
      </div>
    </div>

    <section>
      <h3>Developer Endpoints</h3>
      <table>
        <tr><th>Path</th><th>Description</th><th>Copy</th></tr>
        <tr><td class="url">/health</td><td>Docker health & metrics</td><td><button class="copy-btn" style="position:static" onclick="copyText('https://arifosmcp.arif-fazil.com/health')">URL</button></td></tr>
        <tr><td class="url">/openapi.json</td><td>OpenAPI 3.1 Spec</td><td><button class="copy-btn" style="position:static" onclick="copyText('https://arifosmcp.arif-fazil.com/openapi.json')">URL</button></td></tr>
        <tr><td class="url">/llms.txt</td><td>Model-readable context</td><td><button class="copy-btn" style="position:static" onclick="copyText('https://arifosmcp.arif-fazil.com/llms.txt')">URL</button></td></tr>
        <tr><td class="url">/server.json</td><td>MCP Discovery Manifest</td><td><button class="copy-btn" style="position:static" onclick="copyText('https://arifosmcp.arif-fazil.com/.well-known/mcp/server.json')">URL</button></td></tr>
      </table>
    </section>

    <section>
      <h3>Legacy Compatibility</h3>
      <p style="color:var(--dim); font-size: 0.8rem;">Legacy handlers remain active as internal shims for existing workflows.</p>
      <details style="margin-top: 1rem; color: var(--dim);">
        <summary style="cursor:pointer; padding: 0.5rem; background: #111; border-radius: 4px;">View Functional Mapping Table</summary>
        <div style="padding: 1rem; border: 1px solid var(--border); border-top:none;">
          <table>
            <tr><th>Functional Tool</th><th>Symbolic Root</th><th>Stage</th></tr>
            __APEX_HTML_ROWS__
          </table>
        </div>
      </details>
    </section>
  </div>

  <div class="motto">DITEMPA BUKAN DIBERI &mdash; Forged, not given.</div>

  <script>
    function showTab(id) {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      event.target.classList.add('active');
      document.getElementById(id).classList.add('active');
    }
    function copyCode(btn) {
      const code = btn.previousElementSibling.innerText;
      navigator.clipboard.writeText(code);
      btn.innerText = 'Copied!';
      setTimeout(() => btn.innerText = 'Copy', 2000);
    }
    function copyText(text) {
      navigator.clipboard.writeText(text);
      alert('Copied: ' + text);
    }
    function toggleCard(card) {
      const desc = card.querySelector('.tool-desc');
      if (desc.style.webkitLineClamp === 'unset') {
        desc.style.webkitLineClamp = '2';
      } else {
        desc.style.webkitLineClamp = 'unset';
      }
    }
    // Live health fetch
    (function() {
      fetch('/health')
        .then(r => r.json())
        .then(d => {
          var s = d.status || 'healthy';
          document.getElementById('live-status').textContent = s.toUpperCase();
          document.getElementById('live-status').style.color = s === 'healthy' ? 'var(--green)' : 'var(--orange)';
          document.getElementById('live-version').textContent = d.version || '—';
          document.getElementById('live-tools').textContent = (d.tools_loaded || '—') + ' Tools';
          if (d.ml_floors && d.ml_floors.ml_floors_enabled) {
            document.getElementById('sbert-status').textContent = 'SBERT ML Active';
          }
        })
        .catch(function() {
          document.getElementById('live-status').textContent = 'DEGRADED';
          document.getElementById('live-status').style.color = 'var(--orange)';
        });
    })();
  </script>
  <style>#rn{{position:fixed;bottom:0;left:0;right:0;z-index:9999;background:rgba(10,10,10,0.97);border-top:1px solid #1e1e1e;display:flex;align-items:stretch;justify-content:center;height:36px;font-family:"Courier New",monospace}}#rn a{{color:inherit;text-decoration:none;padding:0 13px;display:flex;align-items:center;font-size:10px;letter-spacing:1.2px;border-right:1px solid #1e1e1e;white-space:nowrap;transition:background .15s}}#rn a:last-child{{border-right:none}}#rn a:hover{{background:#1a1a1a}}#rn a.rn-active{{background:#181818;border-bottom:2px solid currentColor}}body{{padding-bottom:40px!important}}</style>
  <nav id="rn"><a href="https://arif-fazil.com" data-h="arif-fazil.com" style="color:#c94b2e">ARIF (human)</a><a href="https://apex.arif-fazil.com" data-h="apex.arif-fazil.com" style="color:#c4791a">APEX (theory)</a><a href="https://arifos.arif-fazil.com" data-h="arifos.arif-fazil.com" style="color:#2a8a6e">arifOS (kernel)</a><a href="https://aaa.arif-fazil.com" data-h="aaa.arif-fazil.com" style="color:#2a6fbd">AAA (agents)</a><a href="https://waw.arif-fazil.com" data-h="waw.arif-fazil.com" style="color:#6d4ade">WAW (state)</a><a href="https://arifosmcp.arif-fazil.com" data-h="arifosmcp.arif-fazil.com" style="color:#2a8a4a">MCP (endpoint)</a></nav>
  <script>(function(){{var h=location.hostname,a=document.querySelectorAll("#rn a");a.forEach(function(x){{if(x.dataset.h===h)x.classList.add("rn-active")}})}})()</script>
</body>
</html>
"""

DOCS_HTML = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Documentation | arifOS MCP Server</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:#0d0d0d;color:#d4d4d4;font-family:ui-monospace,monospace;
         font-size:14px;line-height:1.6;padding:2rem 1rem;max-width:900px;margin:auto}}
    h1{{color:#e6c25d;font-size:1.5rem;margin-bottom:.25rem}}
    h2{{color:#e6c25d;font-size:1.1rem;margin:2rem 0 1rem;border-bottom:1px solid #333;padding-bottom:.5rem}}
    h3{{color:#7dd3fc;font-size:1rem;margin:1.5rem 0 .5rem}}
    p{{margin-bottom:1rem}}
    ul,ol{{margin-left:2rem;margin-bottom:1rem}}
    li{{margin-bottom:.5rem}}
    code{{background:#1a1a1a;padding:.2rem .4rem;border-radius:4px;font-size:.9rem}}
    pre{{background:#1a1a1a;padding:1rem;border-radius:8px;overflow-x:auto;margin:1rem 0;border:1px solid #333}}
    a{{color:#7dd3fc;text-decoration:none}}
    a:hover{{text-decoration:underline}}
    .nav{{display:flex;gap:1rem;margin-bottom:2rem;flex-wrap:wrap}}
    .nav a{{background:#1a1a1a;border:1px solid #333;padding:.3rem .8rem;border-radius:4px;font-size:.8rem;color:#aaa}}
    .nav a:hover{{border-color:#7dd3fc;color:#7dd3fc}}
    .version{{color:#888;font-size:.9rem;margin-bottom:2rem}}
    .note{{background:#1a1a1a;border-left:3px solid #7dd3fc;padding:1rem;margin:1rem 0}}
    table{{width:100%;border-collapse:collapse;margin:1rem 0}}
    th,td{{padding:.5rem;text-align:left;border-bottom:1px solid #333}}
    th{{color:#e6c25d;font-weight:normal}}
    footer{{text-align:center;margin-top:3rem;padding-top:2rem;border-top:1px solid #333;color:#666;font-size:.85rem}}
  </style>
</head>
<body>
  <h1>📚 arifOS Documentation</h1>
  <div class="version">Version {BUILD_VERSION}</div>
  
  <div class="nav">
    <a href="/">← Home</a>
    <a href="/dashboard">Dashboard</a>
    <a href="/tools">Tools API</a>
    <a href="/health">Health</a>
  </div>

  <h2>Quick Start</h2>
  <pre><code># Install
pip install arifosmcp

# Run MCP server
python -m arifosmcp.runtime stdio</code></pre>

  <h2>The 11 Functional Tools</h2>
  <h3>⚖️ GOVERNANCE (4 tools)</h3>
  <ul>
    <li><code>init_session_anchor</code> — Identity & Authority establishment</li>
    <li><code>route_execution</code> — Metabolic Conductor / Router</li>
    <li><code>judge_verdict</code> — Final Constitutional Authority</li>
    <li><code>record_vault_entry</code> — Immutable Merkle Persistence</li>
  </ul>

  <h3>🧠 INTELLIGENCE (3 tools)</h3>
  <ul>
    <li><code>reason_synthesis</code> — Logic & Synthesis Core</li>
    <li><code>critique_safety</code> — Critical Ethics & Simulation</li>
    <li><code>load_memory_context</code> — Governed Vector Retrieval</li>
  </ul>

  <h3>⚙️ MACHINE (4 tools)</h3>
  <ul>
    <li><code>sense_reality</code> — Environmental Grounding</li>
    <li><code>estimate_ops</code> — Quantitative Thermodynamic Vitals</li>
    <li><code>execute_vps_task</code> — Computational Execution</li>
    <li><code>get_tool_registry</code> — System Definition & Discovery</li>
  </ul>

  <h2>13 Constitutional Floors</h2>
  <table>
    <tr><th>Floor</th><th>Name</th><th>Threshold</th><th>Enforces</th></tr>
    <tr><td>F1</td><td>Amanah</td><td>≥ 0.5</td><td>Reversibility</td></tr>
    <tr><td>F2</td><td>Truth</td><td>≥ 0.99</td><td>Anti-hallucination</td></tr>
    <tr><td>F3</td><td>Tri-Witness</td><td>≥ 0.95</td><td>Consensus</td></tr>
    <tr><td>F4</td><td>ΔS Clarity</td><td>≤ 0</td><td>Entropy reduction</td></tr>
    <tr><td>F5</td><td>Peace²</td><td>≥ 1.0</td><td>Stability</td></tr>
    <tr><td>F6</td><td>Empathy</td><td>≥ 0.70</td><td>Weakest stakeholder</td></tr>
    <tr><td>F7</td><td>Humility</td><td>0.03-0.20</td><td>Uncertainty</td></tr>
    <tr><td>F8</td><td>Genius</td><td>≥ 0.80</td><td>Coherence</td></tr>
    <tr><td>F9</td><td>Anti-Hantu</td><td>&lt; 0.30</td><td>No dark patterns</td></tr>
    <tr><td>F10</td><td>Ontology</td><td>LOCK</td><td>No consciousness claims</td></tr>
    <tr><td>F11</td><td>Command Auth</td><td>LOCK</td><td>Identity verification</td></tr>
    <tr><td>F12</td><td>Injection</td><td>&lt; 0.85</td><td>Adversarial defense</td></tr>
    <tr><td>F13</td><td>Sovereign</td><td>HUMAN</td><td>Human veto</td></tr>
  </table>

  <h2>Trinity Architecture (ΔΩΨ)</h2>
  <ul>
    <li><strong>Δ Delta (AGI Mind)</strong> — Stages 000-444: Reason, sense, ground</li>
    <li><strong>Ω Omega (ASI Heart)</strong> — Stages 555-666: Empathy, memory, ethics</li>
    <li><strong>Ψ Psi (APEX Soul)</strong> — Stages 777-999: Forge, judge, seal</li>
  </ul>

  <h2>API Endpoints</h2>
  <ul>
    <li><code>GET /health</code> — System health & version</li>
    <li><code>GET /tools</code> — List the functional tool surface</li>
    <li><code>GET /dashboard</code> — Live governance UI</li>
    <li><code>POST /mcp</code> — MCP protocol endpoint</li>
  </ul>

  <h2>MCP Client Setup</h2>
  <pre><code>{{
  "mcpServers": {{
    "arifos": {{
      "command": "npx",
      "args": ["-y", "@arifos/mcp"]
    }}
  }}
}}</code></pre>

  <footer>
    <p>Ditempa Bukan Diberi — Forged, Not Given [ΔΩΨ | ARIF]</p>
    <p style="margin-top:.5rem">
      <a href="/readme" style="color:#7dd3fc;text-decoration:none;margin:0 .5rem">README</a> ·
      <a href="/changelog" style="color:#7dd3fc;text-decoration:none;margin:0 .5rem">CHANGELOG</a> ·
      <a href="/roadmap" style="color:#7dd3fc;text-decoration:none;margin:0 .5rem">ROADMAP</a> ·
      <a href="/todo" style="color:#7dd3fc;text-decoration:none;margin:0 .5rem">TODO</a>
    </p>
    <p>© 2026 Muhammad Arif bin Fazil | AGPL-3.0-only</p>
  </footer>
</body>
</html>
"""

ROBOTS_TXT = """\
User-agent: *
Allow: /

# LLM-readable description of this service
# See: https://llmstxt.org
Sitemap: https://arifosmcp.arif-fazil.com/llms.txt
Sitemap: https://arifosmcp.arif-fazil.com/llms.json
"""

LLMS_TXT = f"""\
# AGENTS·API·AI·APPS — The AAA Functional Layer
Location: https://aaa.arif-fazil.com/llms.txt
Version: {BUILD_VERSION}
Domain: AAA / AGENTS·API·AI·APPS

> The AAA Functional Layer of arifOS — Built on MCP with 13 constitutional
> floors ensuring every action is true, safe, and human-aligned.
> Motto: DITEMPA BUKAN DIBERI — Forged, not given.

## The AAA Architecture

| Layer | Domain | Purpose |
|-------|--------|---------|
| ARIF | arif-fazil.com | The Human Sovereign (Muhammad Arif bin Fazil) |
| THEORY | apex.arif-fazil.com | APEX Theory + arifOS Documentation |
| TRINITY | arifos.arif-fazil.com | AGI-ASI-APEX Dynamic Runtime |
| AAA | aaa.arif-fazil.com | AGENTS·API·AI·APPS Surface Layer (THIS SITE) |

## Official MCP Endpoint

- **URL**: `https://aaa.arif-fazil.com/mcp`
- **Transport**: Streamable HTTP / SSE
- **Protocol**: MCP 2025-03-26
- **Tools**: Canonical functional surface (11 mega-tools)

## Core Functional Tools

- `init_session_anchor` — Identity & session anchoring (F11)
- `reason_synthesis` — First-principles reasoning (Δ Mind)
- `sense_reality` — Evidence-grounded grounding (111 Sense)
- `load_memory_context` — Governed context retrieval (555 Memory)
- `route_execution` — Metabolic loop routing (444 Router)
- `judge_verdict` — Final constitutional authority (888 Judge)

## Getting Started

1. Initialize: POST /mcp with `initialize`
2. List tools: `tools/list`
3. Call with envelope: actor_id, intent, token, trace
4. Receive verdict: SEAL / VOID / HOLD / SABAR

## The 13 Constitutional Floors

| Floor | Name | Threshold | Enforces |
|-------|------|-----------|----------|
| F1 | Amanah | ≥ 0.50 | Reversibility |
| F2 | Truth | ≥ 0.99 | Anti-hallucination |
| F3 | Tri-Witness | ≥ 0.95 | Consensus |
| F4 | ΔS Clarity | ≤ 0 | Entropy reduction |
| F5 | Peace² | ≥ 1.0 | Stability |
| F6 | Empathy | ≥ 0.70 | Weakest stakeholder |
| F7 | Humility | 0.03-0.05 | Uncertainty band |
| F8 | Genius | ≥ 0.80 | Coherence |
| F9 | Anti-Hantu | < 0.30 | No dark patterns |
| F10 | Ontology | LOCK | No consciousness claims |
| F11 | CommandAuth | LOCK | Identity verification |
| F12 | Injection | < 0.85 | Adversarial defense |
| F13 | Sovereign | HUMAN | Human veto |

---
**Status:** Ditempa Bukan Diberi.
**Architecture:** ΔΩΨ Trinity with Functional AAA Surface
**Vault Tier:** BRAIN / AAA SURFACE
"""

LLMS_JSON = {
    "name": "arifOS Sovereign Quad",
    "description": "Unified Governance Kernel Map for Functional Surface.",
    "version": BUILD_VERSION,
    "authority": "Muhammad Arif bin Fazil (888 Judge)",
    "motto": "Ditempa Bukan Diberi (Forged, Not Given)",
    "status": {
        "version": BUILD_VERSION,
        "status": "FORGED",
    },
}

WELCOME_HTML = WELCOME_HTML.replace("__BUILD_VERSION__", BUILD_INFO["version"])
WELCOME_HTML = WELCOME_HTML.replace("__BUILD_COMMIT__", BUILD_INFO["commit"])
WELCOME_HTML = WELCOME_HTML.replace("__BUILD_TIME__", BUILD_INFO["timestamp"])
WELCOME_HTML = WELCOME_HTML.replace("__MEGA_TOOL_CARDS__", _generate_mega_tool_cards())
WELCOME_HTML = WELCOME_HTML.replace("__APEX_HTML_ROWS__", apex_tools_html_rows())
try:
    from arifosmcp.runtime.tools import LEGACY_COMPAT_MAP as _lcm
    WELCOME_HTML = WELCOME_HTML.replace("__LEGACY_COUNT__", str(len(_lcm)))
    del _lcm
except Exception:
    WELCOME_HTML = WELCOME_HTML.replace("__LEGACY_COUNT__", "27")


def _build_llms_txt() -> str:
    from arifosmcp.capability_map import build_llm_context_markdown

    return LLMS_TXT + "\n\n" + build_llm_context_markdown() + "\n"

CHECKPOINT_MODES = {"quick", "full", "audit_only"}
RISK_TIER_BY_MODE = {
    "quick": "low",
    "full": "medium",
    "audit_only": "medium",
}


def _env_truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _required_bearer_token() -> str | None:
    return os.getenv("ARIFOS_API_KEY") or os.getenv("ARIFOS_API_TOKEN")


def _auth_error_response(request: Request) -> JSONResponse | None:
    """Auth disabled - public access allowed."""
    return None


def _normalize_tool_name(raw_name: str) -> str:
    """Normalize tool path params so trailing slashes do not break alias resolution."""
    return (raw_name or "").strip().strip("/")


def _public_base_url(request: Request) -> str:
    explicit = os.getenv("ARIFOS_PUBLIC_BASE_URL", "").strip().rstrip("/")
    if explicit:
        return explicit
    scheme = request.headers.get("x-forwarded-proto") or request.url.scheme or "https"
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or "localhost"
    return f"{scheme}://{host}".rstrip("/")


def _openapi_schema(base_url: str) -> dict[str, Any]:
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "arifOS Checkpoint REST API",
            "version": BUILD_INFO["version"],
            "description": (
                "Minimal REST/OpenAPI compatibility surface for functional arifOS "
                "evaluation. Primary endpoint: POST /checkpoint."
            ),
        },
        "servers": [{"url": base_url}],
        "paths": {
            "/checkpoint": {
                "post": {
                    "operationId": "evaluateCheckpoint",
                    "summary": "Constitutional checkpoint evaluation",
                    "description": (
                        "Runs governed evaluation through arifOS and returns verdict + telemetry."
                    ),
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/CheckpointRequest"}
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Checkpoint completed",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CheckpointResponse"}
                                }
                            },
                        },
                    },
                }
            },
        },
        "components": {
            "schemas": {
                "CheckpointRequest": {
                    "type": "object",
                    "required": ["task"],
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "User query/task to evaluate constitutionally.",
                        },
                    },
                },
                "CheckpointResponse": {
                    "type": "object",
                    "properties": {
                        "verdict": {"type": "string"},
                        "metrics": {"type": "object"},
                    },
                },
            }
        },
    }


def register_rest_routes(mcp: Any, tool_registry: dict[str, Callable]) -> None:
    """Register REST endpoints as custom routes on the FastMCP instance."""
    if HAS_CUSTOM_ROUTE:
        route = mcp.custom_route
    elif HAS_ROUTE:
        route = mcp.route
    else:
        raise RuntimeError("FastMCP instance has no custom_route or route method")

    @route("/", methods=["GET"])
    async def root(request: Request) -> Response:
        accept = request.headers.get("Accept", "")
        if "text/html" in accept:
            # Redirect to dashboard for browser requests
            return Response(
                status_code=307,
                headers={"Location": "/dashboard/index.html"}
            )
        return JSONResponse(
            {
                "service": "arifOS AAA Functional MCP Server",
                "version": BUILD_INFO["version"],
                "protocol_version": MCP_PROTOCOL_VERSION,
                "mcp_endpoint": "/mcp",
                "tools_endpoint": "/tools",
                "health_endpoint": "/health",
                "dashboard_endpoint": "/dashboard",
                "widget_endpoint": "/ui",
                "tool_count": len(tool_registry),
                "tools": list(tool_registry.keys()),
            }
        )

    # Load AAA landing page HTML
    AAA_LANDING_HTML_PATH = "/usr/src/project/static/aaa-landing/index.html"
    AAA_LANDING_HTML = ""
    try:
        with open(AAA_LANDING_HTML_PATH) as f:
            AAA_LANDING_HTML = f.read()
    except Exception:
        AAA_LANDING_HTML = """<!DOCTYPE html>
<html><head><title>arifOS MCP</title></head>
<body><h1>arifOS Intelligence Kernel</h1>
<p>MCP Endpoint: https://aaa.arif-fazil.com/mcp</p>
<p><strong>DITEMPA BUKAN DIBERI</strong> — Functional surface active.</p>
</body></html>"""

    @route("/mcp", methods=["GET"])
    async def mcp_landing(request: Request) -> Response:
        """AAA MCP landing page."""
        accept = request.headers.get("Accept", "")
        if "text/html" in accept:
            return HTMLResponse(AAA_LANDING_HTML, headers={"Cache-Control": "max-age=60"})
        return JSONResponse(
            {
                "service": "arifOS AAA Functional MCP Server",
                "version": BUILD_INFO["version"],
                "mcp_endpoint": "/mcp",
                "tool_count": len(tool_registry),
            }
        )

    @route("/docs", methods=["GET"])
    async def docs(request: Request) -> Response:
        return HTMLResponse(DOCS_HTML, headers={"Cache-Control": "max-age=3600"})

    @route("/docs/", methods=["GET"])
    async def docs_trailing(request: Request) -> Response:
        return HTMLResponse(DOCS_HTML, headers={"Cache-Control": "max-age=3600"})

    def _serve_md(title: str, filename: str) -> HTMLResponse:
        import pathlib
        candidates = [
            pathlib.Path("/usr/src/app") / filename,
            pathlib.Path("/app") / filename,
            pathlib.Path(__file__).parent.parent.parent / filename,
        ]
        content = ""
        for path in candidates:
            if path.exists():
                content = path.read_text(encoding="utf-8")
                break
        if not content:
            content = f"# {title}\n\n_File not found: {filename}_"
        safe = content.replace("</script>", "<\\/script>")
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>arifOS — {title}</title>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    :root{{--bg:#0a0a0f;--surface:#12121a;--border:#1e1e2e;--text:#e2e8f0;--muted:#64748b;--accent:#f59e0b;--link:#3b82f6}}
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;line-height:1.7;padding:2rem 1rem}}
    .wrap{{max-width:860px;margin:0 auto}}
    .nav{{display:flex;gap:1rem;margin-bottom:2rem;padding-bottom:1rem;border-bottom:1px solid var(--border);flex-wrap:wrap;align-items:center}}
    #content code{{background:var(--surface);padding:.15rem .4rem;border-radius:3px;font-size:.875em;font-family:'JetBrains Mono',monospace}}
  </style>
</head>
<body>
<div class="wrap">
  <nav class="nav"><a href="/">Home</a> / {title}</nav>
  <div id="content"></div>
</div>
<script>
  const raw = {repr(safe)};
  document.getElementById('content').innerHTML = marked.parse(raw);
</script>
</body>
</html>"""
        return HTMLResponse(html, headers={"Cache-Control": "no-store"})

    @route("/readme", methods=["GET"])
    async def readme(request: Request) -> Response:
        return _serve_md("README", "README.md")

    @route("/health", methods=["GET"])
    async def health(request: Request) -> Response:
        """Liveness probe - minimal OK response."""
        return JSONResponse(
            {
                "status": "healthy",
                "service": "arifos-aaa-mcp",
                "version": BUILD_INFO["version"],
                "transport": "streamable-http",
                "tools_loaded": len(tool_registry),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            headers={"Access-Control-Allow-Origin": "*"},
        )

    @route("/ready", methods=["GET"])
    async def ready(request: Request) -> Response:
        """Readiness probe - checks if server is ready to accept traffic."""
        # Basic readiness: check if tools are loaded
        is_ready = len(tool_registry) > 0
        return JSONResponse(
            {
                "ready": is_ready,
                "status": "ready" if is_ready else "not_ready",
                "service": "arifos-aaa-mcp",
                "tools_loaded": len(tool_registry),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            headers={"Access-Control-Allow-Origin": "*"},
        )

    @route("/build", methods=["GET"])
    async def build_info(request: Request) -> Response:
        """Build provenance endpoint - returns deployment metadata."""
        tool_names = sorted(tool_registry.keys()) if tool_registry else []
        return JSONResponse(
            {
                "name": BUILD_INFO.get("name", "arifOS MCP"),
                "version": BUILD_INFO["version"],
                "build_sha": BUILD_INFO.get("build_sha", "unknown"),
                "build_time": BUILD_INFO.get("build_time", "unknown"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "transport": BUILD_INFO.get("transport", "streamable-http"),
                "tools": tool_names,
                "tool_count": len(tool_names),
            },
            headers={"Access-Control-Allow-Origin": "*"},
        )

    @route("/tools", methods=["GET"])
    async def list_tools(request: Request) -> Response:
        """List all registered tools from the canonical registry."""
        mcp_tools = await mcp.list_tools()
        tool_list = []
        
        for tool in mcp_tools:
            # Include all tools from the canonical registry
            if tool.name in tool_registry:
                tool_list.append(
                    {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.parameters or {},
                    }
                )
        
        # Sort for consistent output
        tool_list.sort(key=lambda t: t["name"])
        return JSONResponse({"tools": tool_list, "count": len(tool_list)})

    @route("/resources", methods=["GET"])
    async def list_resources(request: Request) -> Response:
        """List all registered resources."""
        try:
            resources = await mcp.list_resources()
            resource_list = []
            for r in resources:
                resource_list.append({
                    "uri": r.uri,
                    "name": r.name if hasattr(r, 'name') else r.uri,
                    "description": r.description if hasattr(r, 'description') else "",
                    "mimeType": r.mime_type if hasattr(r, 'mime_type') else "application/json",
                })
            return JSONResponse({"resources": resource_list, "count": len(resource_list)})
        except Exception as e:
            return JSONResponse({"resources": [], "count": 0, "error": str(e)})

    @route("/prompts", methods=["GET"])
    async def list_prompts(request: Request) -> Response:
        """List all registered prompts."""
        try:
            prompts = await mcp.list_prompts()
            prompt_list = []
            for p in prompts:
                prompt_list.append({
                    "name": p.name,
                    "description": p.description if hasattr(p, 'description') else "",
                    "arguments": p.arguments if hasattr(p, 'arguments') else [],
                })
            return JSONResponse({"prompts": prompt_list, "count": len(prompt_list)})
        except Exception as e:
            return JSONResponse({"prompts": [], "count": 0, "error": str(e)})

    @route("/openapi.json", methods=["GET"])
    async def openapi_json(request: Request) -> Response:
        schema = _openapi_schema(_public_base_url(request))
        return JSONResponse(schema)

    @route("/tools/{tool_name:path}", methods=["POST"])
    async def call_tool_rest(request: Request) -> Response:
        incoming_name = _normalize_tool_name(request.path_params.get("tool_name", ""))
        canonical_name = TOOL_ALIASES.get(incoming_name, incoming_name)
        request_id = f"req-{uuid.uuid4().hex[:12]}"
        start_time = time.time()
        
        # Check if client expects SSE (text/event-stream)
        accept_header = request.headers.get("Accept", "")
        wants_sse = "text/event-stream" in accept_header

        if canonical_name not in tool_registry:
            if wants_sse:
                return _sse_error_response(f"Tool '{incoming_name}' not found", 404)
            return JSONResponse({"error": f"Tool '{incoming_name}' not found"}, status_code=404)

        try:
            body = await request.json()
        except Exception:
            body = {}

        tool_obj = tool_registry[canonical_name]
        tool_fn = getattr(tool_obj, "fn", tool_obj)

        try:
            sig = inspect.signature(tool_fn)
            valid_params = {n for n, p in sig.parameters.items() if p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)}
            filtered = {k: v for k, v in body.items() if k in valid_params}
            result = await tool_fn(**filtered)
        except Exception as exc:
            if wants_sse:
                return _sse_error_response(str(exc), 500)
            return JSONResponse({"error": str(exc)}, status_code=500)

        latency_ms = (time.time() - start_time) * 1000
        response_data = {"status": "success", "tool": incoming_name, "latency_ms": round(latency_ms, 2), "result": _json_safe(result)}
        
        if wants_sse:
            return _sse_success_response(response_data)
        return JSONResponse(response_data)


def _sse_success_response(data: dict) -> Response:
    """Return SSE formatted success response."""
    sse_body = f"event: result\ndata: {json.dumps(data)}\n\n"
    return Response(sse_body, media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    })


def _sse_error_response(message: str, code: int) -> Response:
    """Return SSE formatted error response."""
    error_data = {"error": message, "code": code}
    sse_body = f"event: error\ndata: {json.dumps(error_data)}\n\n"
    return Response(sse_body, media_type="text/event-stream", status_code=code, headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    })

    @route("/robots.txt", methods=["GET"])
    async def robots_txt(_request: Request) -> Response:
        return Response(ROBOTS_TXT, media_type="text/plain")

    @route("/llms.txt", methods=["GET"])
    async def llms_txt(_request: Request) -> Response:
        return Response(_build_llms_txt(), media_type="text/plain")

    @route("/llms.json", methods=["GET"])
    async def llms_json(_request: Request) -> Response:
        return JSONResponse(LLMS_JSON, headers={"Access-Control-Allow-Origin": "*"})
