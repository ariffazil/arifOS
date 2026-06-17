#!/usr/bin/env python3
"""
federation_reality_probe.py — One-command live proof of the arifOS federation.

Authority: arifOS kernel / A-FORGE. Read-only. No mutations.
F1 AMANAH: writes only to var/reality/ and FEDERATION_REALITY_SNAPSHOT.md.
F2 TRUTH: every verdict is timestamped and derived from live HTTP responses.
F7 HUMILITY: unknowns are labeled UNKNOWN, not hidden.
F9 ANTIHANTU: mechanical language only; this is a probe, not a being.

Usage:
    python scripts/federation_reality_probe.py --write-md --write-json
    make reality

Outputs:
    var/reality/federation_reality_<timestamp>.json
    FEDERATION_REALITY_SNAPSHOT.md
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── paths ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
VAR_DIR = ROOT / "var" / "reality"
MD_PATH = ROOT / "FEDERATION_REALITY_SNAPSHOT.md"

# ── canonical federation organ manifest ────────────────────────────────
ORGANS: list[dict[str, Any]] = [
    {
        "key": "arifOS",
        "name": "arifOS",
        "role": "constitutional_kernel",
        "expected_tools": 13,
        "localhost": "http://127.0.0.1:8088",
        "public": "https://arifos.arif-fazil.com",
        "mcp_path": "/mcp",
        "freshness_required": False,
    },
    {
        "key": "GEOX",
        "name": "GEOX",
        "role": "earth_evidence",
        "expected_tools": 40,
        "localhost": "http://127.0.0.1:8081",
        "public": "https://geox.arif-fazil.com",
        "mcp_path": "/mcp/",
        "freshness_required": False,
    },
    {
        "key": "WEALTH",
        "name": "WEALTH",
        "role": "capital_compute",
        "expected_tools": 20,
        "localhost": "http://127.0.0.1:18082",
        "public": "https://wealth.arif-fazil.com",
        "mcp_path": "/mcp",
        "freshness_required": False,
    },
    {
        "key": "WELL",
        "name": "WELL",
        "role": "human_readiness_reflect_only",
        "expected_tools": 17,
        "localhost": "http://127.0.0.1:18083",
        "public": "https://well.arif-fazil.com",
        "mcp_path": "/mcp",
        "freshness_required": True,
    },
    {
        "key": "AAA",
        "name": "AAA",
        "role": "cockpit_a2a",
        "expected_tools": None,
        "localhost": "http://127.0.0.1:3001",
        "public": "https://aaa.arif-fazil.com",
        "mcp_path": None,
        "freshness_required": False,
    },
    {
        "key": "A-FORGE",
        "name": "A-FORGE",
        "role": "governed_execution",
        "expected_tools": 59,
        "localhost": "http://127.0.0.1:7071",
        "public": None,
        "mcp_path": "/mcp",
        "freshness_required": False,
    },
]

KNOWN_GAPS = [
    {
        "id": "GAP-001",
        "severity": "high",
        "domain": "A-FORGE",
        "description": "A-FORGE lease gate is self-issued; must become kernel-issued before broad autonomous mutation.",
    },
    {
        "id": "GAP-002",
        "severity": "medium",
        "domain": "WELL",
        "description": "WELL live human-state telemetry is stale / INSUFFICIENT_DATA.",
    },
    {
        "id": "GAP-003",
        "severity": "medium",
        "domain": "arifOS",
        "description": "arifOS CONTEXT.md and RUNBOOK.md created from probe output.",
    },
    {
        "id": "GAP-004",
        "severity": "low",
        "domain": "A-FORGE",
        "description": "A-FORGE public HTTPS ingress is not configured (public endpoint unavailable).",
    },
]


# ── HTTP helpers ───────────────────────────────────────────────────────
def _http_get(
    url: str, headers: dict[str, str] | None = None, timeout: float = 10.0
) -> dict[str, Any]:
    """GET url and return a structured result. Never raises."""
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url, headers=headers or {}, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            return {
                "ok": True,
                "status_code": resp.status,
                "latency_ms": latency_ms,
                "body": body,
            }
    except urllib.error.HTTPError as e:
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "ok": False,
            "status_code": e.code,
            "latency_ms": latency_ms,
            "body": e.read().decode("utf-8", errors="replace"),
            "error": str(e),
        }
    except Exception as e:
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "ok": False,
            "status_code": None,
            "latency_ms": latency_ms,
            "body": "",
            "error": str(e),
        }


def _http_post(
    url: str, payload: dict[str, Any], headers: dict[str, str] | None = None, timeout: float = 10.0
) -> dict[str, Any]:
    """POST JSON payload. Never raises."""
    start = time.perf_counter()
    data = json.dumps(payload).encode("utf-8")
    req_headers = {"Content-Type": "application/json", "Accept": "application/json"}
    req_headers.update(headers or {})
    try:
        req = urllib.request.Request(url, data=data, headers=req_headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            return {"ok": True, "status_code": resp.status, "latency_ms": latency_ms, "body": body}
    except urllib.error.HTTPError as e:
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        body = e.read().decode("utf-8", errors="replace")
        return {
            "ok": False,
            "status_code": e.code,
            "latency_ms": latency_ms,
            "body": body,
            "error": str(e),
        }
    except Exception as e:
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "ok": False,
            "status_code": None,
            "latency_ms": latency_ms,
            "body": "",
            "error": str(e),
        }


def _safe_json(body: str) -> dict[str, Any] | None:
    try:
        return json.loads(body)
    except Exception:
        return None


# ── organ-specific probes ──────────────────────────────────────────────
def _probe_health(base_url: str) -> dict[str, Any]:
    """GET /health and return normalized fields."""
    result = _http_get(f"{base_url}/health", headers={"Accept": "application/json"})
    out = {
        "reachable": result["ok"],
        "status_code": result.get("status_code"),
        "latency_ms": result.get("latency_ms"),
        "raw_status": None,
        "version": None,
        "freshness": None,
        "truth_status": None,
        "error": result.get("error"),
    }
    if result["ok"]:
        data = _safe_json(result["body"])
        if data:
            out["raw_status"] = data.get("status") or data.get("verdict")
            out["version"] = data.get("version") or data.get("release_name")
            out["freshness"] = data.get("freshness")
            out["truth_status"] = data.get("truth_status")
    return out


def _probe_mcp_tool_count(base_url: str, mcp_path: str) -> dict[str, Any]:
    """Run initialize → tools/list and return tool count."""
    init_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "federation-reality-probe", "version": "1.0.0"},
        },
    }
    init_url = f"{base_url}{mcp_path}"
    init = _http_post(init_url, init_payload, headers={"Accept": "application/json"})
    if not init["ok"]:
        return {
            "ok": False,
            "count": None,
            "error": init.get("error"),
            "status_code": init.get("status_code"),
        }

    list_payload = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    listed = _http_post(init_url, list_payload, headers={"Accept": "application/json"})
    if not listed["ok"]:
        return {
            "ok": False,
            "count": None,
            "error": listed.get("error"),
            "status_code": listed.get("status_code"),
        }

    data = _safe_json(listed["body"])
    if not data or "result" not in data:
        return {
            "ok": False,
            "count": None,
            "error": "tools/list missing result",
            "body": listed["body"][:200],
        }

    tools = data["result"].get("tools", [])
    return {"ok": True, "count": len(tools), "source": "mcp_tools/list"}


def _probe_a_forge_metadata(base_url: str) -> dict[str, Any]:
    """A-FORGE GET /mcp returns JSON metadata including tool_count."""
    result = _http_get(f"{base_url}/mcp", headers={"Accept": "text/event-stream,application/json"})
    if not result["ok"]:
        return {
            "ok": False,
            "count": None,
            "error": result.get("error"),
            "status_code": result.get("status_code"),
        }
    data = _safe_json(result["body"])
    if not data:
        return {
            "ok": False,
            "count": None,
            "error": "non-JSON metadata response",
            "body": result["body"][:200],
        }
    return {
        "ok": True,
        "count": data.get("tool_count"),
        "source": "forge_metadata",
        "metadata": data,
    }


def _probe_public(public_url: str | None) -> dict[str, Any]:
    if not public_url:
        return {"reachable": None, "note": "no public endpoint configured"}
    result = _http_get(f"{public_url}/health", headers={"Accept": "application/json"})
    out = {
        "reachable": result["ok"],
        "status_code": result.get("status_code"),
        "latency_ms": result.get("latency_ms"),
        "raw_status": None,
        "error": result.get("error"),
    }
    if result["ok"]:
        data = _safe_json(result["body"])
        if data:
            out["raw_status"] = data.get("status") or data.get("verdict")
    return out


# ── verdict engine ─────────────────────────────────────────────────────
def _organ_verdict(
    organ: dict[str, Any], health: dict[str, Any], tools: dict[str, Any], public: dict[str, Any]
) -> str:
    if not health["reachable"]:
        return "FAIL"

    raw = (health.get("raw_status") or "").lower()
    healthy = raw in {"healthy", "alive"}
    if not healthy:
        return "DEGRADED"

    expected = organ.get("expected_tools")
    if expected and tools.get("ok"):
        count = tools.get("count")
        if count is not None and count != expected:
            return "DEGRADED"

    if organ.get("freshness_required"):
        truth = (health.get("truth_status") or "").upper()
        if truth in {"INSUFFICIENT_DATA", "STALE", "EXPIRED", "DEGRADED"}:
            return "DEGRADED"

    return "PASS"


def _overall_verdict(results: list[dict[str, Any]]) -> str:
    verdicts = [r["verdict"] for r in results]
    if "FAIL" in verdicts:
        return "RED"
    if "DEGRADED" in verdicts:
        return "GREEN_WITH_GAPS"
    if "PASS" in verdicts:
        return "GREEN"
    return "UNKNOWN"


# ── reporters ──────────────────────────────────────────────────────────
def _write_json(snapshot: dict[str, Any]) -> Path:
    VAR_DIR.mkdir(parents=True, exist_ok=True)
    ts = snapshot["timestamp"].replace(":", "-")
    path = VAR_DIR / f"federation_reality_{ts}.json"
    path.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    return path


def _write_md(snapshot: dict[str, Any]) -> Path:
    now = snapshot["timestamp"]
    overall = snapshot["overall_verdict"]
    results = snapshot["organs"]
    gaps = snapshot["known_gaps"]

    lines = [
        "# Federation Reality Snapshot",
        "",
        f"**Last verified:** `{now}`",
        f"**Overall verdict:** `{overall}`",
        "**Truth layer:** `L2_VERIFIED_STATE`",
        "",
        "## Organ Status",
        "",
        "| Organ | Role | Localhost | Public | Tools (expected) | Latency (ms) | Verdict |",
        "|-------|------|-----------|--------|------------------|--------------|---------|",
    ]
    for r in results:
        organ = r["organ"]
        local = "✅" if r["health"]["reachable"] else "❌"
        pub = r["public"]
        pub_str = "✅" if pub.get("reachable") else ("—" if pub.get("reachable") is None else "❌")
        tools = r["tools"]
        tools_str = f"{tools.get('count') if tools.get('ok') else '—'} / {organ.get('expected_tools') or '—'}"
        latency = r["health"].get("latency_ms")
        latency_str = f"{latency}" if latency is not None else "—"
        lines.append(
            f"| {organ['name']} | {organ['role']} | {local} | {pub_str} | {tools_str} | {latency_str} | {r['verdict']} |"
        )

    lines.extend(
        [
            "",
            "## Endpoint Detail",
            "",
            "| Organ | Endpoint | Status | Version | Freshness | Notes |",
            "|-------|----------|--------|---------|-----------|-------|",
        ]
    )
    for r in results:
        organ = r["organ"]
        h = r["health"]
        notes = []
        if h.get("error"):
            notes.append(h["error"])
        if r["tools"].get("error"):
            notes.append(f"tools: {r['tools']['error']}")
        if organ.get("freshness_required") and h.get("truth_status"):
            notes.append(f"truth={h['truth_status']}")
        lines.append(
            f"| {organ['name']} | {organ['localhost']} | {h.get('raw_status') or '—'} | {h.get('version') or '—'} | {h.get('freshness', {}).get('status') if isinstance(h.get('freshness'), dict) else (h.get('freshness') or '—')} | {'; '.join(notes) or '—'} |"
        )

    lines.extend(
        [
            "",
            "## Known Gaps",
            "",
        ]
    )
    for gap in gaps:
        lines.append(
            f"- **{gap['id']}** [{gap['severity']}] *{gap['domain']}*: {gap['description']}"
        )

    lines.extend(
        [
            "",
            "## Score Impact",
            "",
            "This snapshot converts *declared* operational status into *observed* operational status. "
            "It is the first step toward an institution-grade audit trail for the federation.",
            "",
            "---",
            "*Generated by scripts/federation_reality_probe.py — DITEMPA BUKAN DIBERI*",
        ]
    )

    MD_PATH.write_text("\n".join(lines), encoding="utf-8")
    return MD_PATH


# ── main ───────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Federation Reality Probe")
    parser.add_argument("--write-json", action="store_true", help="Write timestamped JSON artifact")
    parser.add_argument(
        "--write-md", action="store_true", help="Write FEDERATION_REALITY_SNAPSHOT.md"
    )
    parser.add_argument("--public", action="store_true", help="Also probe public HTTPS endpoints")
    args = parser.parse_args(argv)

    if not args.write_json and not args.write_md:
        parser.print_help()
        return 0

    snapshot_ts = datetime.now(timezone.utc).isoformat()
    results: list[dict[str, Any]] = []

    for organ in ORGANS:
        health = _probe_health(organ["localhost"])
        public = (
            _probe_public(organ["public"])
            if args.public
            else {"reachable": None, "note": "skipped"}
        )

        tools: dict[str, Any] = {"ok": False, "count": None, "source": None}
        if organ["key"] == "A-FORGE":
            tools = _probe_a_forge_metadata(organ["localhost"])
        elif organ["mcp_path"]:
            tools = _probe_mcp_tool_count(organ["localhost"], organ["mcp_path"])
        else:
            tools = {
                "ok": False,
                "count": None,
                "source": None,
                "error": "organ has no MCP tool surface",
            }

        verdict = _organ_verdict(organ, health, tools, public)
        results.append(
            {"organ": organ, "health": health, "tools": tools, "public": public, "verdict": verdict}
        )

    snapshot = {
        "timestamp": snapshot_ts,
        "truth_layer": "L2_VERIFIED_STATE",
        "overall_verdict": _overall_verdict(results),
        "organs": results,
        "known_gaps": KNOWN_GAPS,
        "probe_version": "1.0.0",
        "probe_source": "scripts/federation_reality_probe.py",
    }

    written: list[str] = []
    if args.write_json:
        path = _write_json(snapshot)
        written.append(str(path))
        print(f"Wrote JSON: {path}", file=sys.stderr)

    if args.write_md:
        path = _write_md(snapshot)
        written.append(str(path))
        print(f"Wrote MD:   {path}", file=sys.stderr)

    print(json.dumps(snapshot, indent=2, ensure_ascii=False, default=str))
    return 0 if snapshot["overall_verdict"] != "RED" else 1


if __name__ == "__main__":
    sys.exit(main())
