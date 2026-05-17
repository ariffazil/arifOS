from __future__ import annotations

import hashlib
import json
import socket
from typing import Any
from urllib.parse import urlparse
import os


def stable_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


def invariant_fields(
    *,
    tool_name: str,
    input_payload: dict[str, Any],
    assumptions: list[str],
    floors_evaluated: list[str],
    confidence: float,
    extra_meta: dict[str, Any] | None = None,
    floors_deferred: list[str] | None = None,
) -> dict[str, Any]:
    input_hash = stable_hash(input_payload)
    reasoning_payload = {
        "tool_name": tool_name,
        "input_hash": input_hash,
        "floors_evaluated": floors_evaluated,
        "assumptions": assumptions,
        "confidence": round(confidence, 3),
    }
    meta = {
        "self_model_present": True,
        "assumption_tracking": True,
        "uncertainty_tracking": True,
        "cross_tool_continuity": True,
    }
    if extra_meta:
        meta.update(extra_meta)
    return {
        "confidence": round(confidence, 3),
        "assumptions": assumptions,
        "uncertainty_acknowledged": True,
        "input_hash": input_hash,
        "reasoning_hash": stable_hash(reasoning_payload),
        "floors_evaluated": floors_evaluated,
        "floors_deferred": floors_deferred or [],
        "meta_intelligence": meta,
    }


def resolve_tcp_endpoint(
    *,
    host_env: str,
    port_env: str,
    url_envs: tuple[str, ...] = (),
    default_port: int | None = None,
) -> dict[str, Any]:
    host = os.getenv(host_env)
    port = os.getenv(port_env)
    if host:
        return {
            "configured": True,
            "host": host,
            "port": int(port or default_port or 0),
            "source": host_env,
        }

    for key in url_envs:
        raw = os.getenv(key)
        if not raw:
            continue
        parsed = urlparse(raw)
        if parsed.hostname:
            return {
                "configured": True,
                "host": parsed.hostname,
                "port": parsed.port or default_port or 0,
                "source": key,
            }

    return {
        "configured": False,
        "host": None,
        "port": default_port,
        "source": "not_configured",
    }


def probe_tcp_endpoint(endpoint: dict[str, Any], *, timeout: float = 2.0) -> dict[str, Any]:
    if not endpoint.get("configured") or not endpoint.get("host") or not endpoint.get("port"):
        return {
            "configured": False,
            "reachable": None,
            "detail": f"{endpoint.get('source', 'unknown')}:not_configured",
        }

    host = str(endpoint["host"])
    port = int(endpoint["port"])
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            return {
                "configured": True,
                "reachable": True,
                "detail": f"{host}:{port} ok via {endpoint.get('source')}",
            }
    except Exception as exc:
        return {
            "configured": True,
            "reachable": False,
            "detail": f"{host}:{port} FAIL({exc}) via {endpoint.get('source')}",
        }

    return {
        "configured": True,
        "reachable": False,
        "detail": f"{host}:{port} FAIL(connect_ex) via {endpoint.get('source')}",
    }
