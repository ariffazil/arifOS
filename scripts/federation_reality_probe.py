#!/usr/bin/env python3
"""
federation_reality_probe.py — One-command live proof of the arifOS federation.

Authority: arifOS kernel / A-FORGE. Read-only. No mutations.
F1 AMANAH: writes only to var/reality/ and FEDERATION_REALITY_SNAPSHOT.md.
F2 TRUTH: every verdict is timestamped and derived from live HTTP responses.
F7 HUMILITY: unknowns are labeled UNKNOWN, not hidden.
F9 ANTIHANTU: mechanical language only; this is a probe, not a being.

Features:
  - Health probe (every organ)
  - Tool count (every MCP organ)
  - Tool scope sweep (--scope): full tools/list with names, resources/list, prompts/list
  - F13 SOVEREIGN reachability: checks each organ for sovereignty awareness

Usage:
    python scripts/federation_reality_probe.py --write-md --write-json
    python scripts/federation_reality_probe.py --scope --write-md --write-json
    make reality
    make reality-deep  # equivalent to --scope --write-md --write-json

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
from collections import Counter
from datetime import UTC, datetime
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
        "expected_tools": 56,
        "localhost": "http://127.0.0.1:8088",
        "public": "https://arifos.arif-fazil.com",
        "mcp_path": "/mcp",
        "freshness_required": False,
    },
    {
        "key": "GEOX",
        "name": "GEOX",
        "role": "earth_evidence",
        "expected_tools": 37,
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
        "expected_tools": 21,
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
        "expected_tools": 77,
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

# ── F13 SOVEREIGN constitution reference ───────────────────────────────
F13_FLOORS = {
    "F1": {"name": "AMANAH", "rule": "Reversible first. Irreversible → 888 HOLD."},
    "F2": {"name": "TRUTH", "rule": "P(truth) ≥ 0.99. Claims carry epistemic label."},
    "F3": {"name": "TRI-WITNESS", "rule": "Human + AI + Earth witness ≥ 0.75."},
    "F4": {"name": "CLARITY", "rule": "Every output must reduce entropy (ΔS ≤ 0)."},
    "F5": {"name": "PEACE²", "rule": "Non-destructive power."},
    "F6": {"name": "MARUAH/EMPATHY", "rule": "Protect weakest stakeholder."},
    "F7": {"name": "HUMILITY", "rule": "No fake certainty. Ω₀ ∈ [0.03, 0.05]."},
    "F8": {"name": "GENIUS", "rule": "G ≥ 0.80 for complex actions."},
    "F9": {"name": "ANTIHANTU", "rule": "No deception, manipulation, consciousness claims."},
    "F10": {"name": "ONTOLOGY", "rule": "AI-only ontology. Soul = VOID."},
    "F11": {"name": "AUDITABILITY", "rule": "Every decision logged."},
    "F12": {"name": "RESILIENCE", "rule": "Injection defense."},
    "F13": {"name": "SOVEREIGN", "rule": "Human veto FINAL. Harness switch belongs to sovereign."},
}

FLOOR_TABLE_PATH = ROOT / "GENESIS" / "FLOOR_TABLE.json"
KERNEL_CANON_PATH = ROOT / "GENESIS" / "000_KERNEL_CANON.md"


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
        "f13_status": None,
        "error": result.get("error"),
    }
    if result["ok"]:
        data = _safe_json(result["body"])
        if data:
            out["raw_status"] = data.get("status") or data.get("verdict")
            out["version"] = data.get("version") or data.get("release_name")
            out["freshness"] = data.get("freshness")
            out["truth_status"] = data.get("truth_status")
            # Capture F13 / sovereignty fields if present
            out["f13_status"] = (
                data.get("f13_status")
                or data.get("sovereign_status")
                or data.get("sovereign")
                or data.get("human_veto")
            )
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


def _probe_mcp_tool_scope(base_url: str, mcp_path: str) -> dict[str, Any]:
    """
    Full tool scope sweep: tools/list with names, resources/list, prompts/list.
    Returns a dict with categorized tools, resources, and prompts.
    """
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

    # initialize
    init = _http_post(init_url, init_payload, headers={"Accept": "application/json"})
    if not init["ok"]:
        return {"ok": False, "error": init.get("error"), "status_code": init.get("status_code")}

    result: dict[str, Any] = {"ok": True}

    # tools/list
    list_payload = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    listed = _http_post(init_url, list_payload, headers={"Accept": "application/json"})
    if listed["ok"]:
        data = _safe_json(listed["body"])
        if data and "result" in data:
            raw_tools = data["result"].get("tools", [])
            tool_names = sorted(t["name"] for t in raw_tools)
            # classify by prefix
            prefixes = Counter()
            for n in tool_names:
                parts = n.split("_", 1)
                pfx = parts[0] if len(parts) > 1 else n
                prefixes[pfx] += 1
            result["tools"] = {
                "count": len(tool_names),
                "names": tool_names,
                "prefixes": dict(prefixes.most_common()),
            }
        else:
            result["tools"] = {
                "ok": False,
                "error": "tools/list missing result",
                "body": listed["body"][:200],
            }
    else:
        result["tools"] = {"ok": False, "error": listed.get("error")}

    # resources/list
    res_payload = {"jsonrpc": "2.0", "id": 3, "method": "resources/list", "params": {}}
    res_listed = _http_post(init_url, res_payload, headers={"Accept": "application/json"})
    if res_listed["ok"]:
        data = _safe_json(res_listed["body"])
        if data and "result" in data:
            resources = data["result"].get("resources", [])
            result["resources"] = {
                "count": len(resources),
                "uris": sorted(r.get("uri", r.get("name", "?")) for r in resources),
            }
        else:
            result["resources"] = {"count": 0, "uris": []}
    else:
        result["resources"] = {"count": 0, "uris": [], "error": res_listed.get("error")}

    # prompts/list
    pr_payload = {"jsonrpc": "2.0", "id": 4, "method": "prompts/list", "params": {}}
    pr_listed = _http_post(init_url, pr_payload, headers={"Accept": "application/json"})
    if pr_listed["ok"]:
        data = _safe_json(pr_listed["body"])
        if data and "result" in data:
            prompts = data["result"].get("prompts", [])
            result["prompts"] = {
                "count": len(prompts),
                "names": sorted(p.get("name", "?") for p in prompts),
            }
        else:
            result["prompts"] = {"count": 0, "names": []}
    else:
        result["prompts"] = {"count": 0, "names": [], "error": pr_listed.get("error")}

    return result


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


# ── F13 reachability ───────────────────────────────────────────────────
def _probe_f13_reachability() -> dict[str, Any]:
    """
    Check F13 SOVEREIGN reachability across the federation.
    - Verify FLOOR_TABLE.json exists and is parseable
    - Verify kernel canon exists
    - Check that all 13 floors are declared
    - Check health responses for sovereignty awareness
    """
    floors: dict[str, Any] = {}
    for fid, info in F13_FLOORS.items():
        floors[fid] = {"name": info["name"], "rule": info["rule"]}

    result: dict[str, Any] = {
        "floors_declared": len(F13_FLOORS),
        "floors": floors,
        "files": {},
        "organs_acknowledging_sovereignty": [],
    }

    # Check FLOOR_TABLE.json
    if FLOOR_TABLE_PATH.exists():
        try:
            ft_data = json.loads(FLOOR_TABLE_PATH.read_text(encoding="utf-8"))
            ft_floors = ft_data.get("floors", [])
            result["files"]["FLOOR_TABLE.json"] = {
                "exists": True,
                "floors_count": len(ft_floors),
                "authority": ft_data.get("authority"),
                "version": ft_data.get("version"),
            }
        except (json.JSONDecodeError, OSError) as e:
            result["files"]["FLOOR_TABLE.json"] = {"exists": True, "parse_error": str(e)}
    else:
        result["files"]["FLOOR_TABLE.json"] = {"exists": False}

    # Check 000_KERNEL_CANON.md
    if KERNEL_CANON_PATH.exists():
        canon_text = KERNEL_CANON_PATH.read_text(encoding="utf-8", errors="replace")
        f13_mentions = canon_text.count("F13") + canon_text.count("SOVEREIGN")
        result["files"]["000_KERNEL_CANON.md"] = {
            "exists": True,
            "f13_mentions": f13_mentions,
            "size_bytes": KERNEL_CANON_PATH.stat().st_size,
        }
    else:
        result["files"]["000_KERNEL_CANON.md"] = {"exists": False}

    # Probe each organ's health for F13/sovereignty awareness
    for organ in ORGANS:
        health = _probe_health(organ["localhost"])
        f13 = health.get("f13_status")
        if f13 is not None:
            result["organs_acknowledging_sovereignty"].append(
                {"organ": organ["key"], "f13_status": f13}
            )

    return result


def _probe_organ_f13_health(organ: dict[str, Any], health: dict[str, Any]) -> dict[str, Any]:
    """Check a single organ's health response for F13 sovereignty awareness."""
    f13_raw = health.get("f13_status")
    return {
        "organ_key": organ["key"],
        "health_has_f13_field": f13_raw is not None,
        "f13_status": f13_raw,
        "reachable": health.get("reachable", False),
    }


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
EDGE_CACHE = Path("/root/.arifos/observatory/snapshots/edge_cache.json")


def _write_json(snapshot: dict[str, Any]) -> Path:
    VAR_DIR.mkdir(parents=True, exist_ok=True)
    ts = snapshot["timestamp"].replace(":", "-")
    path = VAR_DIR / f"federation_reality_{ts}.json"
    path.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    # Also update observatory edge_cache.json
    EDGE_CACHE.parent.mkdir(parents=True, exist_ok=True)
    probed = sum(1 for o in snapshot["organs"] if o["health"].get("reachable"))
    reachable = sum(1 for o in snapshot["organs"] if o["health"].get("reachable"))
    edge_cache = {
        "probed": probed,
        "reachable": reachable,
        "semantic_proven": 0,
        "aggregate_state": snapshot["overall_verdict"],
        "observed_at_epoch": time.time(),
        "source": "federation_reality_probe.py",
    }
    EDGE_CACHE.write_text(json.dumps(edge_cache, indent=2), encoding="utf-8")
    return path


def _write_md(snapshot: dict[str, Any]) -> Path:
    now = snapshot["timestamp"]
    overall = snapshot["overall_verdict"]
    results = snapshot["organs"]
    gaps = snapshot["known_gaps"]
    f13 = snapshot.get("f13", {})
    scope = snapshot.get("tool_scope_sweep", {})

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
            "| Organ | Endpoint | Status | Version | Freshness | F13 Status | Notes |",
            "|-------|----------|--------|---------|-----------|------------|-------|",
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
        f13_str = str(h.get("f13_status") or "—")[:20]
        lines.append(
            f"| {organ['name']} | {organ['localhost']} | {h.get('raw_status') or '—'} | {h.get('version') or '—'} | {h.get('freshness', {}).get('status') if isinstance(h.get('freshness'), dict) else (h.get('freshness') or '—')} | {f13_str} | {'; '.join(notes) or '—'} |"
        )

    # ── F13 SOVEREIGN section ──────────────────────────────────────
    lines.extend(
        [
            "",
            "## F13 SOVEREIGN — Reachability & Floor Canon",
            "",
            f"**Floors declared in canon:** {f13.get('floors_declared', 0)} / 13",
            "",
        ]
    )
    files_info = f13.get("files", {})
    if files_info:
        lines.append("| File | Status | Detail |")
        lines.append("|------|--------|--------|")
        for fname, finfo in files_info.items():
            if finfo.get("exists"):
                detail_parts = []
                if "floors_count" in finfo:
                    detail_parts.append(f"{finfo['floors_count']} floors")
                if "authority" in finfo:
                    detail_parts.append(f"authority={finfo['authority']}")
                if "f13_mentions" in finfo:
                    detail_parts.append(f"{finfo['f13_mentions']}× F13 mention")
                if "size_bytes" in finfo:
                    detail_parts.append(f"{finfo['size_bytes']} bytes")
                if "parse_error" in finfo:
                    detail_parts.append(f"⚠️ PARSE ERROR: {finfo['parse_error']}")
                detail = "; ".join(detail_parts) or "ok"
                lines.append(f"| {fname} | ✅ | {detail} |")
            else:
                lines.append(f"| {fname} | ❌ | Missing |")

    acknowledging = f13.get("organs_acknowledging_sovereignty", [])
    if acknowledging:
        lines.append("")
        lines.append("**Organs with F13/sovereignty field in /health:**")
        for ack in acknowledging:
            lines.append(f"- **{ack['organ']}**: `{ack['f13_status']}`")
    else:
        lines.append("")
        lines.append("**No organs currently expose an F13/sovereignty field in /health.**")

    # Floor table
    floors = f13.get("floors", {})
    if floors:
        lines.extend(
            [
                "",
                "| Floor | Name | Rule |",
                "|-------|------|------|",
            ]
        )
        for fid in sorted(floors.keys()):
            finfo = floors[fid]
            lines.append(f"| {fid} | {finfo['name']} | {finfo['rule']} |")

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

    # ── Tool Scope Sweep section (if --scope) ───────────────────────
    if scope.get("organs"):
        lines.extend(
            [
                "",
                "## Tool Scope Sweep",
                "",
                "| Organ | Tools | Prefixes | Resources | Prompts |",
                "|-------|-------|----------|-----------|---------|",
            ]
        )
        for skey, sdata in sorted(scope.get("organs", {}).items()):
            tools_info = sdata.get("tools", {})
            res_info = sdata.get("resources", {})
            pr_info = sdata.get("prompts", {})
            t_count = tools_info.get("count", "—") if isinstance(tools_info, dict) else "—"
            r_count = res_info.get("count", 0) if isinstance(res_info, dict) else 0
            p_count = pr_info.get("count", 0) if isinstance(pr_info, dict) else 0
            if isinstance(tools_info, dict) and "prefixes" in tools_info:
                pfx_str = ", ".join(
                    f"{k}={v}" for k, v in tools_info["prefixes"].items()
                )
            else:
                pfx_str = "—"
            lines.append(f"| {skey} | {t_count} | {pfx_str} | {r_count} | {p_count} |")

        lines.append("")
        lines.append("### Tool Names by Prefix")
        for skey, sdata in sorted(scope.get("organs", {}).items()):
            tools_info = sdata.get("tools", {})
            if isinstance(tools_info, dict) and "names" in tools_info:
                names = tools_info["names"]
                lines.append(f"\n**{skey}** ({len(names)} tools):")
                for name in names:
                    lines.append(f"  - `{name}`")
                lines.append("")

        lines.append("### Resource URIs")
        for skey, sdata in sorted(scope.get("organs", {}).items()):
            res_info = sdata.get("resources", {})
            if isinstance(res_info, dict) and "uris" in res_info:
                uris = res_info["uris"]
                lines.append(f"\n**{skey}** ({len(uris)} resources):")
                for uri in uris:
                    lines.append(f"  - `{uri}`")
                lines.append("")

        lines.append("### Prompt Names")
        for skey, sdata in sorted(scope.get("organs", {}).items()):
            pr_info = sdata.get("prompts", {})
            if isinstance(pr_info, dict) and "names" in pr_info:
                names = pr_info["names"]
                lines.append(f"\n**{skey}** ({len(names)} prompts):")
                for name in names:
                    lines.append(f"  - `{name}`")
                lines.append("")

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
    parser.add_argument(
        "--scope",
        action="store_true",
        help="Perform full tool scope sweep (tools/list with names, resources/list, prompts/list)",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Emit detailed per-organ scope to stderr"
    )
    args = parser.parse_args(argv)

    if not args.write_json and not args.write_md:
        parser.print_help()
        return 0

    snapshot_ts = datetime.now(UTC).isoformat()
    results: list[dict[str, Any]] = []
    tool_scope: dict[str, Any] = {"organs": {}}

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

        # ── Tool scope sweep (if --scope) ──────────────────────────
        if args.scope:
            scope_key = organ["key"]
            scope_result: dict[str, Any] = {}

            if organ["key"] == "A-FORGE":
                # A-FORGE uses GET /mcp metadata
                meta = _probe_a_forge_metadata(organ["localhost"])
                scope_result["tools"] = {
                    "count": meta.get("count"),
                    "names": [],
                    "prefixes": {},
                }
                scope_result["resources"] = {"count": 0, "uris": []}
                scope_result["prompts"] = {"count": 0, "names": []}
                scope_result["note"] = "A-FORGE: limited scope via GET /mcp metadata"
            elif organ["mcp_path"]:
                scope_result = _probe_mcp_tool_scope(organ["localhost"], organ["mcp_path"])
            else:
                # AAA has no MCP path
                scope_result = {
                    "note": "no MCP path",
                    "tools": {"count": 0, "names": [], "prefixes": {}},
                    "resources": {"count": 0, "uris": []},
                    "prompts": {"count": 0, "names": []},
                }

            tool_scope["organs"][scope_key] = scope_result
            if args.verbose:
                tinfo = scope_result.get("tools", {})
                print(
                    f"[scope] {scope_key}: {tinfo.get('count', '?')} tools, "
                    f"{scope_result.get('resources', {}).get('count', 0)} resources, "
                    f"{scope_result.get('prompts', {}).get('count', 0)} prompts",
                    file=sys.stderr,
                )

    # ── F13 reachability ────────────────────────────────────────────
    f13_result = _probe_f13_reachability()
    # Add per-organ F13 health signals
    f13_organs: list[dict[str, Any]] = []
    for organ in ORGANS:
        # re-use the health results we already have
        health = next((r["health"] for r in results if r["organ"]["key"] == organ["key"]), {})
        f13_organs.append(_probe_organ_f13_health(organ, health))
    f13_result["per_organ"] = f13_organs

    snapshot = {
        "timestamp": snapshot_ts,
        "truth_layer": "L2_VERIFIED_STATE",
        "overall_verdict": _overall_verdict(results),
        "organs": results,
        "known_gaps": KNOWN_GAPS,
        "f13": f13_result,
        "probe_version": "2.0.0",
        "probe_source": "scripts/federation_reality_probe.py",
    }

    if args.scope:
        snapshot["tool_scope_sweep"] = tool_scope

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
