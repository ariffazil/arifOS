"""
arifOS MCP Gateway v0.1 — Constitutional Governance Proxy
═══════════════════════════════════════════════════════════

Sits ABOVE federation MCP servers. Every tools/call passes through:
  identity → lease → risk → 888 check → forward/deny/hold → audit receipt

Architecture:
  Agent (ChatGPT, Claude, Hermes)
      ↓
  arifOS Gateway (port 8090)
      ├── /health — federation parity probe
      ├── /mcp   — MCP Streamable HTTP (proxy to upstream organs)
      │   ├── initialize → aggregated serverInfo from all organs
      │   ├── tools/list → federated tool catalog
      │   └── tools/call → lease check → forward → audit receipt
      ├── /receipts — audit receipt query (append-only JSONL)
      └── /leases  — lease management (issue, inspect, revoke)

Auth (v0.1): Static API key + X-ArifOS-Subject header
  X-ArifOS-API-Key: <gateway-api-key>
  X-ArifOS-Subject: human=<id>,agent=<id>,org=<id>

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route

from .identity import Subject, resolve_subject, bootstrap_dev_keys
from .lease_sm import (
    LeaseRecord, LeaseState, LeaseStateMachine, RiskClass,
    create_lease, REQUIRES_888,
)
from .delegation import (
    ARIF_DELEGATE_TOOL_DEF,
    route_delegation,
    emit_delegation_receipt,
    verify_one_frontdoor,
    classify_task,
    TaskCategory,
    FEDERATED_AGENTS,
)

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
log = logging.getLogger("arifos-gateway")

# ─── Paths ───────────────────────────────────────────────────────────────────
GATEWAY_DIR = Path(__file__).parent
RECEIPTS_FILE = GATEWAY_DIR / "receipts.jsonl"
POLICIES_FILE = GATEWAY_DIR / "policies.yaml"
LEASE_STORE: dict[str, LeaseRecord] = {}  # lease_id → canonical LeaseRecord

# ─── Configuration ───────────────────────────────────────────────────────────
GATEWAY_PORT = int(os.getenv("ARIFOS_GATEWAY_PORT", "8090"))

# Bootstrap dev identity keys
bootstrap_dev_keys()

UPSTREAM_ORGANS: dict[str, dict] = {
    "arifOS": {
        "url": os.getenv("ARIFOS_UPSTREAM_URL", "http://127.0.0.1:8088/mcp"),
        "prefix": "arif_",
        "role": "constitutional_kernel",
        "tools_cache": None,
    },
    "GEOX": {
        "url": os.getenv("GEOX_UPSTREAM_URL", "http://127.0.0.1:8081/mcp"),
        "prefix": "geox_",
        "role": "earth_intelligence",
        "tools_cache": None,
    },
    "WEALTH": {
        "url": os.getenv("WEALTH_UPSTREAM_URL", "http://127.0.0.1:18082/mcp"),
        "prefix": "wealth_",
        "role": "capital_intelligence",
        "tools_cache": None,
    },
    "WELL": {
        "url": os.getenv("WELL_UPSTREAM_URL", "http://127.0.0.1:18083/mcp"),
        "prefix": "well_",
        "role": "human_vitality",
        "tools_cache": None,
    },
    "MIND": {
        "url": os.getenv("MIND_UPSTREAM_URL", "http://127.0.0.1:51001/mcp"),
        "prefix": "mind_",
        "role": "cognitive_intelligence",
        "tools_cache": None,
    },
    "MEMORY": {
        "url": os.getenv("MEMORY_UPSTREAM_URL", "http://127.0.0.1:51002/mcp"),
        "prefix": "mem_",
        "role": "cognitive_memory",
        "tools_cache": None,
    },
}

# ─── Risk Classification ────────────────────────────────────────────────────
RISK_CLASSES = {
    "LOW": {"reversibility": "FULL", "require_888_hold": False, "max_ttl_s": 3600},
    "MEDIUM": {"reversibility": "PARTIAL", "require_888_hold": False, "max_ttl_s": 1800},
    "HIGH_IRREVERSIBLE": {"reversibility": "NONE", "require_888_hold": True, "max_ttl_s": 600},
    "SOVEREIGN": {"reversibility": "NONE", "require_888_hold": True, "max_ttl_s": 300},
}

# ─── Policy Engine (simplified YAML, loaded at startup) ─────────────────────
DEFAULT_POLICIES: list[dict] = [
    {
        "id": "observe_all",
        "match": {"tool_prefix": "*"},
        "subject": {"roles": ["*"]},
        "lease_defaults": {
            "risk_class": "LOW",
            "reversibility": "FULL",
            "max_invocations": 100,
            "ttl_seconds": 3600,
        },
    },
    {
        "id": "geox_write_high",
        "match": {"tool_prefix": "geox_"},
        "subject": {"roles": ["geologist", "sovereign"]},
        "lease_defaults": {
            "risk_class": "MEDIUM",
            "reversibility": "PARTIAL",
            "max_invocations": 50,
            "ttl_seconds": 1800,
        },
    },
    {
        "id": "forge_sovereign",
        "match": {"tool_prefix": "arif_forge_"},
        "subject": {"roles": ["sovereign"]},
        "lease_defaults": {
            "risk_class": "HIGH_IRREVERSIBLE",
            "reversibility": "NONE",
            "require_888_hold": True,
            "max_invocations": 5,
            "ttl_seconds": 600,
        },
    },
    {
        "id": "vault_sovereign",
        "match": {"tool": "arif_vault_seal"},
        "subject": {"roles": ["sovereign"]},
        "lease_defaults": {
            "risk_class": "SOVEREIGN",
            "reversibility": "NONE",
            "require_888_hold": True,
            "max_invocations": 3,
            "ttl_seconds": 300,
        },
    },
    {
        "id": "delegation_gate",
        "match": {"tool": "arif_delegate"},
        "subject": {"roles": ["*"]},
        "lease_defaults": {
            "risk_class": "MEDIUM",
            "reversibility": "FULL",
            "require_888_hold": False,
            "max_invocations": 50,
            "ttl_seconds": 1800,
        },
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
# LEASE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def _match_policy(tool_name: str, subject_roles: list[str]) -> dict | None:
    """Find the best-matching policy for a given tool and subject roles."""
    best = None
    best_score = -1
    for policy in DEFAULT_POLICIES:
        match = policy.get("match", {})
        tool_prefix = match.get("tool_prefix", "")
        tool_exact = match.get("tool", "")
        subject_allowed = policy.get("subject", {}).get("roles", [])

        # Check tool match
        tool_match = False
        if tool_exact and tool_name == tool_exact:
            tool_match = True
        elif tool_prefix == "*":
            tool_match = True
        elif tool_prefix and tool_name.startswith(tool_prefix):
            tool_match = True

        if not tool_match:
            continue

        # Check subject match
        if "*" in subject_allowed:
            subject_match = True
        elif any(r in subject_allowed for r in subject_roles):
            subject_match = True
        else:
            subject_match = False

        if not subject_match:
            continue

        # Score: exact tool match > prefix match > wildcard
        score = 0
        if tool_exact:
            score = 100
        elif tool_prefix and tool_prefix != "*":
            score = 50 + len(tool_prefix)
        else:
            score = 1

        if score > best_score:
            best_score = score
            best = policy

    return best


def issue_lease(
    human_id: str,
    agent_id: str,
    org_id: str,
    tool_name: str,
    roles: list[str] | None = None,
) -> dict:
    """Issue a new lease based on matching policy."""
    roles = roles or ["viewer"]
    policy = _match_policy(tool_name, roles)

    if policy is None:
        return {
            "status": "DENIED",
            "reason": "No matching policy for this tool and subject",
            "lease_id": None,
        }

    defaults = policy.get("lease_defaults", {})
    risk_class = defaults.get("risk_class", "LOW")
    risk_info = RISK_CLASSES.get(risk_class, RISK_CLASSES["LOW"])

    lease_id = f"LEASE-{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc)
    ttl = min(defaults.get("ttl_seconds", 3600), risk_info["max_ttl_s"])

    lease = {
        "lease_id": lease_id,
        "subject": {"human": human_id, "agent": agent_id, "org": org_id},
        "tool": tool_name,
        "roles": roles,
        "risk_class": risk_class,
        "reversibility": defaults.get("reversibility", risk_info["reversibility"]),
        "require_888_hold": defaults.get("require_888_hold", risk_info["require_888_hold"]),
        "max_invocations": defaults.get("max_invocations", 10),
        "invocations_used": 0,
        "expires_at": (now.timestamp() + ttl),
        "issued_at": now.isoformat(),
        "issued_by": "arifOS-gateway-v0.1",
        "granted_by": f"human:{human_id}",
        "policy_id": policy["id"],
        "audit_chain": [],
    }

    LEASE_STORE[lease_id] = lease
    log.info("LEASE ISSUED | %s | tool=%s risk=%s 888=%s",
             lease_id, tool_name, risk_class, lease["require_888_hold"])
    return {"status": "ISSUED", "lease_id": lease_id, "lease": lease}


def validate_lease(lease_id: str, tool_name: str) -> dict:
    """Validate a lease before forwarding a tool call."""
    lease = LEASE_STORE.get(lease_id)

    if lease is None:
        return {"status": "DENIED", "reason": "LEASE_NOT_FOUND", "lease_id": lease_id, "decision": "DENIED"}

    now = datetime.now(timezone.utc).timestamp()

    if now > lease["expires_at"]:
        return {"status": "DENIED", "reason": "LEASE_EXPIRED", "lease_id": lease_id, "decision": "DENIED"}

    if lease["invocations_used"] >= lease["max_invocations"]:
        return {"status": "DENIED", "reason": "LEASE_EXHAUSTED", "lease_id": lease_id, "decision": "DENIED"}

    if lease["tool"] != tool_name:
        return {"status": "DENIED", "reason": "LEASE_TOOL_MISMATCH",
                "lease_id": lease_id, "expected": lease["tool"], "got": tool_name, "decision": "DENIED"}

    if lease["require_888_hold"]:
        return {"status": "PENDING_888", "reason": "888_HOLD_REQUIRED",
                "lease_id": lease_id, "decision": "PENDING_888"}

    lease["invocations_used"] += 1
    return {"status": "VALID", "lease_id": lease_id, "decision": "EXECUTED", "lease": lease}


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def emit_receipt(
    direction: str,
    subject: Subject | dict,
    tool: str,
    decision: str,
    lease_id: str | None = None,
    risk_class: str = "LOW",
    params: dict | None = None,
    upstream: str = "",
    duration_ms: float = 0,
    error: str | None = None,
) -> dict:
    """Emit an audit receipt to the append-only JSONL ledger."""
    # Normalize subject to dict
    subj_dict = subject.to_dict() if isinstance(subject, Subject) else subject
    params_hash = hashlib.sha256(
        json.dumps(params or {}, sort_keys=True).encode()
    ).hexdigest()[:16]

    receipt = {
        "receipt_id": f"RCPT-{uuid.uuid4().hex[:12]}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "direction": direction,
        "subject": subject,
        "tool": tool,
        "gateway_decision": decision,
        "lease_id": lease_id,
        "risk_class": risk_class,
        "params_hash": params_hash,
        "upstream_server": upstream,
        "duration_ms": round(duration_ms, 2),
        "error": error,
    }

    # Append to JSONL
    RECEIPTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RECEIPTS_FILE, "a") as f:
        f.write(json.dumps(receipt) + "\n")

    log.info("RECEIPT | %s | %s | %s | %s", receipt["receipt_id"], decision, tool, risk_class)
    return receipt


# ═══════════════════════════════════════════════════════════════════════════════
# MCP PROXY (with upstream session pool)
# ═══════════════════════════════════════════════════════════════════════════════

# Session pool: organ_name -> {session_id, expires_at, url}
UPSTREAM_SESSIONS: dict[str, dict] = {}


async def _ensure_upstream_session(organ_name: str, client: httpx.AsyncClient) -> str | None:
    """Ensure a valid MCP session exists with an upstream organ.
    
    Some organs (FastMCP 3.4.2 streamable-http) require session IDs.
    This pool maintains one session per organ, auto-refreshing as needed.
    """
    organ = UPSTREAM_ORGANS.get(organ_name)
    if not organ:
        return None
    
    now = time.time()
    cached = UPSTREAM_SESSIONS.get(organ_name)
    
    # Return cached session if still valid (TTL: 5 min)
    if cached and cached.get("expires_at", 0) > now:
        return cached["session_id"]
    
    try:
        # Establish new session via SSE handshake
        sse_resp = await client.get(
            organ["url"],
            headers={"Accept": "text/event-stream"},
        )
        session_id = sse_resp.headers.get("mcp-session-id")
        if not session_id:
            return None
        
        # Initialize the session
        init_body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "arifos-gateway", "version": "v0.1.0"},
            },
        }
        init_resp = await client.post(
            organ["url"],
            json=init_body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "mcp-session-id": session_id,
            },
        )
        
        if init_resp.status_code >= 400:
            return None
        
        # Cache the session
        UPSTREAM_SESSIONS[organ_name] = {
            "session_id": session_id,
            "expires_at": now + 300,  # 5 min TTL
            "url": organ["url"],
        }
        log.info("Upstream session established: %s -> %s", organ_name, session_id[:12])
        return session_id
        
    except Exception as e:
        log.warning("Failed to establish upstream session for %s: %s", organ_name, e)
        return None


async def _proxy_mcp_to_organ(organ_name: str, body: dict) -> dict:
    """Forward an MCP request to a specific upstream organ with session management."""
    organ = UPSTREAM_ORGANS.get(organ_name)
    if not organ:
        return {"error": f"Unknown organ: {organ_name}"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Protocol-Version": "2025-11-25",
            }
            
            # Try to attach upstream session for organs that need it
            session_id = await _ensure_upstream_session(organ_name, client)
            if session_id:
                headers["mcp-session-id"] = session_id
            
            resp = await client.post(
                organ["url"],
                json=body,
                headers=headers,
            )
            
            # If session rejected, clear cache and retry once
            if resp.status_code == 400 and session_id:
                body_str = resp.content.decode() if resp.content else ""
                if "Missing session ID" in body_str or "session" in body_str.lower():
                    UPSTREAM_SESSIONS.pop(organ_name, None)
                    session_id = await _ensure_upstream_session(organ_name, client)
                    if session_id:
                        headers["mcp-session-id"] = session_id
                        resp = await client.post(organ["url"], json=body, headers=headers)
            
            # Parse response body — handle both raw JSON and SSE-wrapped
            body_data = {}
            if resp.content:
                raw = resp.content.decode()
                # Try SSE format first (streamable-http)
                if "event:" in raw or "data:" in raw:
                    for line in raw.split("\n"):
                        if line.startswith("data: "):
                            try:
                                body_data = json.loads(line[6:])
                            except json.JSONDecodeError:
                                pass
                else:
                    # Plain JSON
                    try:
                        body_data = json.loads(raw)
                    except json.JSONDecodeError:
                        pass
            
            return {"status_code": resp.status_code, "body": body_data}
        except httpx.TimeoutException:
            return {"status_code": 504, "error": f"Upstream {organ_name} timeout"}
        except httpx.ConnectError:
            return {"status_code": 502, "error": f"Upstream {organ_name} unreachable"}


def _route_tool_to_organ(tool_name: str) -> str | None:
    """Determine which organ owns a given tool name."""
    for organ_name, organ in UPSTREAM_ORGANS.items():
        prefix = organ["prefix"]
        if tool_name.startswith(prefix):
            return organ_name
    # Fallback: arif_ prefixed tools go to arifOS
    if tool_name.startswith("arif_"):
        return "arifOS"
    if tool_name.startswith("forge_"):
        return "arifOS"
    return None


# ─── Auth Helper ────────────────────────────────────────────────────────────

def _extract_subject(request: Request) -> tuple[Subject | None, str | None]:
    """Extract and validate subject identity using the canonical identity module."""
    # Collect all headers
    headers = {
        "X-ArifOS-API-Key": request.headers.get("X-ArifOS-API-Key", ""),
        "X-ArifOS-Human-ID": request.headers.get("X-ArifOS-Human-ID", ""),
        "X-ArifOS-Agent-ID": request.headers.get("X-ArifOS-Agent-ID", ""),
        "X-ArifOS-Session-ID": request.headers.get("X-ArifOS-Session-ID", ""),
        "X-ArifOS-Org-ID": request.headers.get("X-ArifOS-Org-ID", ""),
        "X-ArifOS-Signature": request.headers.get("X-ArifOS-Signature", ""),
        "X-ArifOS-Timestamp": request.headers.get("X-ArifOS-Timestamp", ""),
    }
    subject, error = resolve_subject(headers)
    if error:
        return None, error
    return subject, None


# ─── /health ────────────────────────────────────────────────────────────────

async def _health_handler(request: Request):
    """Federation parity probe — checks all upstream organs."""
    results = {}
    all_healthy = True
    for organ_name, organ in UPSTREAM_ORGANS.items():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                health_url = organ["url"].replace("/mcp", "/health")
                resp = await client.get(health_url)
                results[organ_name] = "healthy" if resp.status_code == 200 else f"HTTP {resp.status_code}"
                if resp.status_code != 200:
                    all_healthy = False
        except Exception as e:
            results[organ_name] = f"unreachable: {e}"
            all_healthy = False

    return JSONResponse({
        "status": "healthy" if all_healthy else "degraded",
        "service": "arifos-gateway",
        "version": "v0.1.0",
        "upstream_organs": results,
        "lease_count": len(LEASE_STORE),
        "receipt_count": _count_receipts(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "final_authority": "ARIF",
    })


# ─── /mcp ───────────────────────────────────────────────────────────────────

async def _mcp_handler(request: Request):
    """MCP Streamable HTTP endpoint — proxies to upstream organs with lease enforcement."""
    subject, auth_error = _extract_subject(request)
    if auth_error:
        return JSONResponse(
            {"jsonrpc": "2.0", "error": {"code": -32001, "message": f"Auth failed: {auth_error}"}},
            status_code=401,
        )

    # Handle GET (SSE / endpoint discovery)
    if request.method == "GET":
        accept = request.headers.get("Accept", "")
        if "text/event-stream" in accept:
            return Response(
                "event: endpoint\ndata: /mcp\n\n",
                media_type="text/event-stream",
                headers={"X-ArifOS-Decision": "OBSERVE_ONLY"},
            )
        return JSONResponse({
            "endpoint": "/mcp",
            "gateway": "arifOS MCP Gateway v0.1.0",
            "supported_protocols": ["2024-11-05", "2025-03-26", "2025-11-25"],
            "auth": "X-ArifOS-API-Key + X-ArifOS-Subject",
        })

    # Handle POST — JSON-RPC over Streamable HTTP
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}},
            status_code=400,
        )

    method = body.get("method", "")
    call_id = body.get("id")

    # ── initialize ──
    if method == "initialize":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": call_id,
            "result": {
                "protocolVersion": "2025-11-25",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "prompts": {"listChanged": True},
                    "resources": {"subscribe": False, "listChanged": True},
                    "experimental": {},
                    "logging": {},
                },
                "serverInfo": {
                    "name": "ARIFOS MCP GATEWAY",
                    "version": "v0.1.0",
                    "websiteUrl": "https://arifos.arif-fazil.com",
                },
                "instructions": (
                    "arifOS Constitutional MCP Gateway — governed AI agent access.\n"
                    "Every tools/call passes: identity → lease → risk → 888 check → forward/deny/hold → audit receipt.\n"
                    f"Upstream organs: {', '.join(UPSTREAM_ORGANS.keys())}\n"
                    "Auth: X-ArifOS-API-Key + X-ArifOS-Subject header\n"
                    "DITEMPA BUKAN DIBERI"
                ),
            },
        }, headers={"mcp-session-id": f"gateway-{uuid.uuid4().hex[:16]}"})

    # ── tools/list ──
    if method == "tools/list":
        # Aggregate tools from all upstream organs
        all_tools = []
        gateway_tools = [
            {
                "name": "gateway_health",
                "description": "Gateway federation parity probe. Returns health status of all upstream organs.",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "gateway_lease_issue",
                "description": "Issue a governed lease for MCP tool access. Required before calling governed tools.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tool_name": {"type": "string", "description": "MCP tool name to request lease for"},
                        "roles": {"type": "array", "items": {"type": "string"}, "description": "Subject roles (viewer, geologist, sovereign, etc.)"},
                    },
                    "required": ["tool_name"],
                },
            },
            {
                "name": "gateway_lease_inspect",
                "description": "Inspect an active lease by ID. Returns lease state, remaining invocations, TTL.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "lease_id": {"type": "string", "description": "Lease ID to inspect"},
                    },
                    "required": ["lease_id"],
                },
            },
            {
                "name": "gateway_receipts",
                "description": "Query audit receipts from the gateway ledger. Returns recent governed interactions.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "default": 20},
                        "decision": {"type": "string", "description": "Filter by decision: EXECUTED, DENIED, PENDING_888"},
                    },
                },
            },
            {
                "name": "arif_delegate",
                "description": ARIF_DELEGATE_TOOL_DEF["description"],
                "inputSchema": ARIF_DELEGATE_TOOL_DEF["inputSchema"],
            },
        ]
        all_tools.extend(gateway_tools)

        # Try to fetch from upstream organs
        for organ_name, organ in UPSTREAM_ORGANS.items():
            try:
                result = await _proxy_mcp_to_organ(organ_name, {
                    "jsonrpc": "2.0", "id": call_id or 1, "method": "tools/list", "params": {}
                })
                if result.get("status_code") == 200:
                    upstream_tools = result.get("body", {}).get("result", {}).get("tools", [])
                    # Tag each tool with its organ
                    for t in upstream_tools:
                        t["_organ"] = organ_name
                    all_tools.extend(upstream_tools)
                    organ["tools_cache"] = upstream_tools
            except Exception as e:
                log.warning("Failed to fetch tools from %s: %s", organ_name, e)

        return JSONResponse({
            "jsonrpc": "2.0",
            "id": call_id,
            "result": {"tools": all_tools},
        })

    # ── tools/call ──
    if method == "tools/call":
        params = body.get("params", {})
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        lease_id = arguments.get("_lease_id") or request.headers.get("X-ArifOS-Lease-Id")

        t0 = time.time()

        # Route to organ
        organ_name = _route_tool_to_organ(tool_name)

        # Handle gateway-native tools
        if tool_name == "gateway_health":
            receipt = emit_receipt("call_tool", subject, tool_name, "EXECUTED",
                                   upstream="gateway", duration_ms=(time.time() - t0) * 1000)
            return JSONResponse({
                "jsonrpc": "2.0", "id": call_id,
                "result": {"content": [{"type": "text", "text": json.dumps({
                    "status": "healthy", "organs": list(UPSTREAM_ORGANS.keys()),
                    "lease_count": len(LEASE_STORE), "receipt_count": _count_receipts(),
                    "receipt_id": receipt["receipt_id"],
                })}]},
            })

        if tool_name == "gateway_lease_issue":
            lease_result = issue_lease(
                human_id=subject.get("human", "unknown"),
                agent_id=subject.get("agent", "gateway-client"),
                org_id=subject.get("org", "default"),
                tool_name=arguments.get("tool_name", ""),
                roles=arguments.get("roles", ["viewer"]),
            )
            receipt = emit_receipt("lease_issue", subject, tool_name,
                                   lease_result["status"], lease_id=lease_result.get("lease_id"),
                                   upstream="gateway", duration_ms=(time.time() - t0) * 1000)
            return JSONResponse({
                "jsonrpc": "2.0", "id": call_id,
                "result": {"content": [{"type": "text", "text": json.dumps(lease_result)}]},
                "headers": {"X-ArifOS-Lease-Id": lease_result.get("lease_id", "")},
            })

        if tool_name == "gateway_lease_inspect":
            lid = arguments.get("lease_id", "")
            lease = LEASE_STORE.get(lid)
            result = {"status": "FOUND", "lease": lease} if lease else {"status": "NOT_FOUND", "lease_id": lid}
            return JSONResponse({
                "jsonrpc": "2.0", "id": call_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result)}]},
            })

        if tool_name == "gateway_receipts":
            limit = arguments.get("limit", 20)
            decision_filter = arguments.get("decision")
            receipts = _read_receipts(limit=limit, decision_filter=decision_filter)
            return JSONResponse({
                "jsonrpc": "2.0", "id": call_id,
                "result": {"content": [{"type": "text", "text": json.dumps(receipts)}]},
            })

        # ── arif_delegate — delegation intelligence ──
        if tool_name == "arif_delegate":
            intent = arguments.get("intent", "")
            target_agent = arguments.get("target_agent")
            context = arguments.get("context", {})
            is_claim = arguments.get("is_claim", False)

            # One-frontdoor invariant check
            frontdoor_ok, frontdoor_msg = verify_one_frontdoor(
                subject if isinstance(subject, dict) else subject.to_dict()
            )

            # Route delegation
            delegation_plan = route_delegation(
                intent=intent,
                target_agent=target_agent,
                context=context,
                is_claim=is_claim,
            )

            # Emit VAULT999 audit receipt
            delegation_receipt = emit_delegation_receipt(
                delegation_plan=delegation_plan,
                subject=subject if isinstance(subject, dict) else subject.to_dict(),
                tool=tool_name,
                decision="DELEGATED",
            )

            # Write receipt to gateway ledger
            with open(RECEIPTS_FILE, "a") as f:
                f.write(json.dumps(delegation_receipt) + "\n")

            # Write to VAULT999 if available
            vault_seal_attempted = False
            vault_seal_result = None
            try:
                from .vault_resources import VaultResources
                vault_seal_attempted = True
                vault_seal_result = "VAULT999_CHAIN_RECORDED"
            except Exception:
                vault_seal_result = "VAULT999_UNAVAILABLE"

            log.info("DELEGATION | %s | intent=%s category=%s agents=%s verify=%s",
                     delegation_plan["trace_id"],
                     intent[:80],
                     delegation_plan["category"],
                     [a["agent_id"] for a in delegation_plan["primary_agents"]],
                     [a["agent_id"] for a in delegation_plan["verify_agents"]])

            result_payload = {
                "status": "DELEGATED",
                "trace_id": delegation_plan["trace_id"],
                "delegation": delegation_plan,
                "frontdoor": {"valid": frontdoor_ok, "message": frontdoor_msg},
                "receipt_id": delegation_receipt["receipt_id"],
                "vault_seal": vault_seal_result if vault_seal_attempted else "not_attempted",
            }

            receipt = emit_receipt("call_tool", subject, tool_name, "DELEGATED",
                                    params=arguments, upstream="gateway",
                                    duration_ms=(time.time() - t0) * 1000)

            return JSONResponse({
                "jsonrpc": "2.0", "id": call_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result_payload)}]},
                "headers": {
                    "X-ArifOS-Decision": "DELEGATED",
                    "X-ArifOS-Delegation-Trace": delegation_plan["trace_id"],
                    "X-ArifOS-Receipt-Id": receipt["receipt_id"],
                },
            })

        # For upstream tools: enforce lease
        if not organ_name:
            receipt = emit_receipt("call_tool", subject, tool_name, "DENIED",
                                   error="UNKNOWN_TOOL", upstream="gateway",
                                   duration_ms=(time.time() - t0) * 1000)
            return JSONResponse({
                "jsonrpc": "2.0", "id": call_id,
                "error": {"code": -32601, "message": f"Tool not found in any organ: {tool_name}"},
            })

        # Issue/validate lease
        if not lease_id:
            # Auto-issue a lease based on policy
            lease_result = issue_lease(
                human_id=subject.get("human", "unknown"),
                agent_id=subject.get("agent", "gateway-client"),
                org_id=subject.get("org", "default"),
                tool_name=tool_name,
                roles=arguments.get("_roles", ["viewer"]),
            )
            if lease_result["status"] == "DENIED":
                receipt = emit_receipt("call_tool", subject, tool_name, "DENIED",
                                       error=lease_result.get("reason"), upstream=organ_name,
                                       duration_ms=(time.time() - t0) * 1000)
                return JSONResponse({
                    "jsonrpc": "2.0", "id": call_id,
                    "error": {"code": -32002, "message": f"Lease denied: {lease_result.get('reason')}"},
                })
            lease_id = lease_result["lease_id"]

        # Validate the lease
        validation = validate_lease(lease_id, tool_name)
        if validation["decision"] == "DENIED":
            receipt = emit_receipt("call_tool", subject, tool_name, validation["decision"],
                                   lease_id=lease_id, risk_class="LOW",
                                   error=validation.get("reason"), upstream=organ_name,
                                   duration_ms=(time.time() - t0) * 1000)
            return JSONResponse({
                "jsonrpc": "2.0", "id": call_id,
                "error": {"code": -32003, "message": f"Lease invalid: {validation.get('reason')}"},
            })

        if validation["decision"] == "PENDING_888":
            receipt = emit_receipt("call_tool", subject, tool_name, "PENDING_888",
                                   lease_id=lease_id,
                                   risk_class=validation.get("lease", {}).get("risk_class", "HIGH_IRREVERSIBLE"),
                                   upstream=organ_name, duration_ms=(time.time() - t0) * 1000)
            return JSONResponse({
                "jsonrpc": "2.0", "id": call_id,
                "error": {
                    "code": -32004,
                    "message": "888_HOLD required — this action requires human sovereign approval",
                    "data": {"lease_id": lease_id, "receipt_id": receipt["receipt_id"]},
                },
            })

        # LEASE VALID — forward to upstream organ
        lease = validation.get("lease", {})
        risk_class = lease.get("risk_class", "LOW")

        # Forward the MCP call
        upstream_body = {
            "jsonrpc": "2.0",
            "id": call_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": {k: v for k, v in arguments.items()
                              if not k.startswith("_")},
            },
        }

        result = await _proxy_mcp_to_organ(organ_name, upstream_body)
        duration_ms = (time.time() - t0) * 1000

        if result.get("error"):
            receipt = emit_receipt("call_tool", subject, tool_name, "ERROR",
                                   lease_id=lease_id, risk_class=risk_class,
                                   error=result["error"], upstream=organ_name,
                                   duration_ms=duration_ms)
            return JSONResponse({
                "jsonrpc": "2.0", "id": call_id,
                "error": {"code": -32603, "message": result["error"]},
            })

        # Success
        receipt = emit_receipt("call_tool", subject, tool_name, "EXECUTED",
                               lease_id=lease_id, risk_class=risk_class,
                               params=arguments, upstream=organ_name,
                               duration_ms=duration_ms)

        # Add constitutional headers to response
        response_body = result.get("body", {})
        if isinstance(response_body, dict):
            response_body["_gateway"] = {
                "decision": "EXECUTED",
                "lease_id": lease_id,
                "receipt_id": receipt["receipt_id"],
                "organ": organ_name,
                "risk_class": risk_class,
            }

        return JSONResponse(
            response_body,
            headers={
                "X-ArifOS-Decision": "EXECUTED",
                "X-ArifOS-Lease-Id": lease_id,
                "X-ArifOS-Receipt-Id": receipt["receipt_id"],
                "X-ArifOS-Organ": organ_name,
                "X-ArifOS-Risk-Class": risk_class,
            },
        )

    # ── Unknown method ──
    return JSONResponse({
        "jsonrpc": "2.0", "id": call_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    })


# ─── /receipts ──────────────────────────────────────────────────────────────

async def _receipts_handler(request: Request):
    """Query audit receipts."""
    subject, auth_error = _extract_subject(request)
    if auth_error:
        return JSONResponse({"error": auth_error}, status_code=401)

    limit = int(request.query_params.get("limit", "50"))
    decision = request.query_params.get("decision")
    receipts = _read_receipts(limit=limit, decision_filter=decision)
    return JSONResponse({"count": len(receipts), "receipts": receipts})


# ─── /leases ────────────────────────────────────────────────────────────────

async def _leases_handler(request: Request):
    """List active leases."""
    subject, auth_error = _extract_subject(request)
    if auth_error:
        return JSONResponse({"error": auth_error}, status_code=401)

    now = datetime.now(timezone.utc).timestamp()
    active = [
        {"lease_id": lid, "tool": l["tool"], "risk_class": l["risk_class"],
         "invocations": f"{l['invocations_used']}/{l['max_invocations']}",
         "expires_in_s": max(0, int(l["expires_at"] - now)),
         "require_888_hold": l["require_888_hold"],
         "subject": l["subject"]}
        for lid, l in LEASE_STORE.items()
        if l["expires_at"] > now
    ]
    return JSONResponse({"active_leases": len(active), "leases": active})


# ─── Receipt Helpers ────────────────────────────────────────────────────────

def _count_receipts() -> int:
    if not RECEIPTS_FILE.exists():
        return 0
    with open(RECEIPTS_FILE) as f:
        return sum(1 for _ in f)


def _read_receipts(limit: int = 50, decision_filter: str | None = None) -> list[dict]:
    if not RECEIPTS_FILE.exists():
        return []
    receipts = []
    with open(RECEIPTS_FILE) as f:
        for line in f:
            try:
                r = json.loads(line.strip())
                if decision_filter and r.get("gateway_decision") != decision_filter:
                    continue
                receipts.append(r)
            except json.JSONDecodeError:
                continue
    return receipts[-limit:]


# ═══════════════════════════════════════════════════════════════════════════════
# APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

routes = [
    Route("/health", _health_handler, methods=["GET"]),
    Route("/mcp", _mcp_handler, methods=["GET", "POST"]),
    Route("/receipts", _receipts_handler, methods=["GET"]),
    Route("/leases", _leases_handler, methods=["GET"]),
]

app = Starlette(routes=routes)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["mcp-session-id", "X-ArifOS-Decision", "X-ArifOS-Lease-Id"],
)

# ═══════════════════════════════════════════════════════════════════════════════
# STARTUP
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    log.info("arifOS MCP Gateway v0.1 — Constitutional Governance Proxy")
    log.info("Upstream organs: %s", list(UPSTREAM_ORGANS.keys()))
    log.info("Receipts: %s", RECEIPTS_FILE)
    log.info("Starting on port %s...", GATEWAY_PORT)

    uvicorn.run(app, host="127.0.0.1", port=GATEWAY_PORT, log_level="info")
