"""
arifos/runtime/server.py — Constitutional MCP HTTP Transport

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import subprocess
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from arifos.adapters.mcp.mcp_server import mcp
from arifos.prompts import PROMPTS
from arifos.resources import RESOURCES
from arifos.adapters.mcp.verify_arifos_tools import (
    PRIMARY_METRIC_NAME,
    VITALITY_JSONL,
    VITALITY_TSV,
)
from arifos.core.governance import VAULT999_LEDGER_PATH

# ── Metadata (F2 Truth — pinned at deploy time) ─────────────
_GIT_SHA = "unknown"
_RELEASE_TAG = "v2026.04.19-UNIFIED"

try:
    _GIT_SHA = subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=Path(__file__).resolve().parents[2],
        stderr=subprocess.DEVNULL,
        text=True,
    ).strip()
except Exception:
    pass

# ── MCP HTTP App with lifespan ──────────────────────────────
_mcp_app = mcp.http_app(stateless_http=True)


@asynccontextmanager
async def _lifespan(app: FastAPI):
    """Combined lifespan: runs MCP task group alongside FastAPI."""
    async with _mcp_app.router.lifespan_context(_mcp_app):
        yield


app = FastAPI(title="arifosmcp NEXT HORIZON", lifespan=_lifespan)


# ── Helpers ─────────────────────────────────────────────────
def _public_base_url(request: Request) -> str:
    proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("x-forwarded-host", request.headers.get("host", request.url.netloc))
    return f"{proto}://{host}".rstrip("/")


def _last_seal() -> str:
    """Read the most recent VAULT999 chain_hash for health telemetry."""
    ledger = Path(VAULT999_LEDGER_PATH)
    if not ledger.exists():
        return "No seal recorded"
    try:
        with ledger.open("r", encoding="utf-8") as fh:
            lines = [ln.strip() for ln in fh if ln.strip()]
            if lines:
                last = json.loads(lines[-1])
                return last.get("chain_hash", last.get("merkle_leaf", "No seal recorded"))
    except Exception:
        pass
    return "No seal recorded"


def _health_payload() -> dict:
    return {
        "status": "healthy",
        "service": "arifosmcp-next-horizon",
        "version": _RELEASE_TAG,
        "source_commit": _GIT_SHA,
        "release_tag": _RELEASE_TAG,
        "last_seal": _last_seal(),
        "tau_system": "Ω=1.0",
        "continuity": "session-alive",
        "tools_loaded": len(PRIMARY_METRIC_NAME),
        "prompts_loaded": len(PROMPTS),
        "resources_loaded": len(RESOURCES),
        "entrypoint": "arifos.mcp_server",
        "vitality": {
            "jsonl": str(VITALITY_JSONL),
            "tsv": str(VITALITY_TSV),
            "jsonl_exists": VITALITY_JSONL.exists(),
            "tsv_exists": VITALITY_TSV.exists(),
        },
    }


def _tools_payload() -> dict:
    tools = []
    tm = mcp._tool_manager._tools
    for name in sorted(PRIMARY_METRIC_NAME):
        tool = tm.get(name)
        schema = None
        if tool is not None:
            schema = getattr(tool, "parameters", None)
        tools.append(
            {
                "name": name,
                "primary_metric": PRIMARY_METRIC_NAME[name],
                "inputSchema": schema or {"type": "object", "properties": {}},
            }
        )
    return {"tools": tools}


def _prompts_payload() -> dict:
    return {"prompts": [{"name": name} for name in sorted(PROMPTS)]}


def _resources_payload() -> dict:
    return {"resources": [{"uri": uri} for uri in sorted(RESOURCES)]}


def _status_payload(request: Request) -> dict:
    health_payload = _health_payload()
    ok = health_payload["status"] == "healthy"
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_ok": ok,
        "health": health_payload,
        "manifest": {
            "base_url": _public_base_url(request),
            "tools_count": len(PRIMARY_METRIC_NAME),
            "prompts_count": len(PROMPTS),
            "resources_count": len(RESOURCES),
        },
        "trinity_matrix": {
            "overall_ok": ok,
            "delta": {
                "state": "HIDUP" if ok else "LEBUR",
                "detail": (
                    "health_ok · 1 reachable_endpoint"
                    if ok
                    else "status_api_unreachable · 0 reachable_endpoints"
                ),
            },
            "psi": {
                "state": "SEAL" if ok else "GANTUNG",
                "detail": (
                    f"manifest_ok · {len(RESOURCES)} verified_domains"
                    if ok
                    else "status_api_unreachable · 0 verified_domains"
                ),
            },
            "omega": {
                "state": "SELARAS" if ok else "SESAT",
                "detail": (
                    f"tool_surface_ok · {len(PRIMARY_METRIC_NAME)} tools"
                    if ok
                    else "status_api_unreachable · 0 tau"
                ),
            },
        },
        "tools": _tools_payload()["tools"],
        "prompts": _prompts_payload()["prompts"],
        "resources": _resources_payload()["resources"],
    }


# ── FastAPI Routes (must be defined BEFORE the mount) ───────


@app.get("/")
async def root() -> dict:
    return {
        "service": "arifosmcp-next-horizon",
        "entrypoint": "arifos.runtime.server:app",
        "mcp_path": "/mcp",
    }


@app.get("/health")
async def health() -> dict:
    return _health_payload()


@app.get("/tools")
async def tools() -> dict:
    return _tools_payload()


@app.get("/prompts")
async def prompts() -> dict:
    return _prompts_payload()


@app.get("/resources")
async def resources() -> dict:
    return _resources_payload()


@app.get("/api/tools")
async def api_tools() -> dict:
    return _tools_payload()


@app.get("/api/telemetry")
async def api_telemetry(request: Request) -> dict:
    payload = _status_payload(request)
    return {
        "timestamp": payload["timestamp"],
        "health": payload["health"],
        "trinity_matrix": payload["trinity_matrix"],
    }


@app.get("/api/status")
@app.get("/status")
async def api_status(request: Request) -> dict:
    return _status_payload(request)


@app.get("/metrics/json")
async def metrics_json(request: Request) -> dict:
    """Telemetry surface — returns same shape as /api/telemetry."""
    payload = _status_payload(request)
    return {
        "timestamp": payload["timestamp"],
        "health": payload["health"],
        "trinity_matrix": payload["trinity_matrix"],
        "tools": payload["tools"],
    }


@app.get("/sse")
async def sse() -> PlainTextResponse:
    """
    SSE transport placeholder.
    FastMCP 2.x streamable-http is the canonical transport;
    SSE fallback is available via the MCP endpoint with proper Accept headers.
    """
    return PlainTextResponse(
        'event: info\ndata: {"message": "SSE transport not standalone -- use /mcp with Accept: text/event-stream"}\n\n',
        media_type="text/event-stream",
    )


@app.get("/llms.txt")
async def llms_txt() -> FileResponse:
    """Serve the canonical llms.txt reference file."""
    path = Path(__file__).resolve().parents[2] / "sites" / "llms.txt"
    if path.exists():
        return FileResponse(path, media_type="text/plain")
    raise HTTPException(status_code=404, detail="llms.txt not found")


@app.get("/.well-known/mcp/server.json")
async def well_known(request: Request) -> JSONResponse:
    base_url = _public_base_url(request)
    payload = {
        "name": "arifosmcp-next-horizon",
        "description": (
            f"Constitutional governance server — {len(PRIMARY_METRIC_NAME)} live runtime tools "
            "with NEXT HORIZON prompts and organ resources."
        ),
        "version": _RELEASE_TAG,
        "protocolVersion": "2025-03-26",
        "url": f"{base_url}/mcp",
        "toolsEndpoint": f"{base_url}/tools",
        "promptsEndpoint": f"{base_url}/prompts",
        "resourcesEndpoint": f"{base_url}/resources",
        "tools": _tools_payload()["tools"],
        "prompts": _prompts_payload()["prompts"],
        "resources": _resources_payload()["resources"],
    }
    return JSONResponse(payload)


# ── WebMCP Dashboard ────────────────────────────────────────
_dashboard_dir = Path(__file__).resolve().parents[2] / "sites" / "dashboard"
if _dashboard_dir.exists():
    app.mount("/webmcp", StaticFiles(directory=str(_dashboard_dir), html=True), name="webmcp")


# ── MCP Mount (must be LAST so /mcp maps to internal /mcp) ─
app.mount("/", _mcp_app)
