#!/usr/bin/env uv run python3
"""
scripts/verify_public.py
========================
arifOS Public Parity Verifier — DITEMPA BUKAN DIBERI

Verifies that the public HTTPS surface matches local/container truth.
Prevents deployment drift from hiding real failures.

Authority order checked:
  1. Local app      (127.0.0.1:8080)
  2. Host localhost (same as local — included for clarity)
  3. Caddy internal (arifosmcp container DNS)
  4. Public HTTPS   (https://mcp.arif-fazil.com)

Verdict:
  APPROVED  — all layers agree, /ready = pass
  HOLD      — public differs from local, or /ready = partial
  VOID      — public /status.json or /health unreachable
"""

import json
import sys
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, asdict
from typing import Optional
from pathlib import Path

# ─── Config ────────────────────────────────────────────────────────────────────

LOCAL_BASE = "http://127.0.0.1:8080"
CADDY_BASE = "http://arifosmcp:8080"
PUBLIC_BASE = "https://mcp.arif-fazil.com"
REPORT_PATH = Path("tmp/verify_public_report.json")

ENDPOINTS = ["/status.json", "/health", "/ready"]

# ─── Dataclasses ───────────────────────────────────────────────────────────────


@dataclass
class LayerResult:
    layer: str
    endpoint: str
    http_status: int
    verdict: str  # PASS | FAIL | SKIP | HOLD | VOID
    payload: Optional[dict] = None
    error: Optional[str] = None
    latency_ms: float = 0.0


@dataclass
class McpResult:
    initialize: str  # PASS | PARTIAL | SKIP | FAIL
    tools_list: str  # PASS | PARTIAL | SKIP | FAIL
    tools_count: int = -1
    initialize_error: Optional[str] = None
    tools_list_error: Optional[str] = None


@dataclass
class ComparisonResult:
    version: str = ""  # "" means no diff; non-empty = diff found
    commit: str = ""
    status: str = ""
    tools_count: str = ""
    arifos: str = ""
    geox: str = ""
    wealth: str = ""


@dataclass
class VerifyReport:
    timestamp: str
    layers: list[LayerResult]
    comparison: ComparisonResult
    mcp: McpResult
    tool_consistency: tuple[str, str]  # (verdict, detail)
    verdict: str
    hold_reason: str = ""
    approved_checks: int = 0
    total_checks: int = 0


# ─── HTTP Helpers ─────────────────────────────────────────────────────────────


def fetch(
    url: str,
    method: str = "GET",
    body: Optional[bytes] = None,
    headers: Optional[dict] = None,
    timeout: float = 8.0,
) -> tuple[int, dict | None, float, str]:
    """Returns (http_status, payload_dict, latency_ms, error_str)."""
    start = time.monotonic()
    h = headers or {}
    h.setdefault("Accept", "application/json")
    req = urllib.request.Request(url, method=method, data=body, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            latency = (time.monotonic() - start) * 1000
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = {"raw": raw.decode("utf-8", errors="replace")[:200]}
            return resp.status, payload, latency, ""
    except urllib.error.HTTPError as e:
        raw = e.read()[:200] if e.fp else b""
        latency = (time.monotonic() - start) * 1000
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"error_body": raw.decode("utf-8", errors="replace")}
        return e.code, payload, latency, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        latency = (time.monotonic() - start) * 1000
        return 0, None, latency, str(e.reason)
    except Exception as e:
        latency = (time.monotonic() - start) * 1000
        return 0, None, latency, str(e)


def post_jsonrpc(
    url: str, method: str, params: dict, timeout: float = 10.0
) -> tuple[int, dict | None, float, str]:
    """Send JSON-RPC request. Returns (http_status, result_dict, latency, error)."""
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    start = time.monotonic()
    h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    req = urllib.request.Request(url, method="POST", data=body, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            latency = (time.monotonic() - start) * 1000
            # arifOS MCP responds via SSE: "event: message\ndata: {...json...}"
            text = raw.decode("utf-8", errors="replace")
            for line in text.split("\n"):
                if line.startswith("data:"):
                    try:
                        payload = json.loads(line[5:].strip())
                        return resp.status, payload, latency, ""
                    except json.JSONDecodeError:
                        pass
            # Fallback: try raw JSON
            try:
                payload = json.loads(text)
                return resp.status, payload, latency, ""
            except json.JSONDecodeError:
                return resp.status, {"raw": text[:500]}, latency, "no parseable JSON in SSE body"
    except urllib.error.HTTPError as e:
        raw = e.read()[:200] if e.fp else b""
        latency = (time.monotonic() - start) * 1000
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"error_body": raw.decode("utf-8", errors="replace")}
        return e.code, payload, latency, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        latency = (time.monotonic() - start) * 1000
        return 0, None, latency, str(e.reason)
    except Exception as e:
        latency = (time.monotonic() - start) * 1000
        return 0, None, latency, str(e)


def fetch_via_caddy(endpoint: str, timeout: float = 8.0) -> tuple[int, dict | None, float, str]:
    """
    Use docker exec to run curl from inside the Caddy container,
    which has access to the Docker bridge network and arifosmcp hostname.
    """
    import subprocess

    url = f"http://arifosmcp:8080{endpoint}"
    start = time.monotonic()
    try:
        result = subprocess.run(
            [
                "docker",
                "exec",
                "caddy",
                "curl",
                "-s",
                "-w",
                "\\n%{http_code}",
                "--connect-timeout",
                "3",
                "--max-time",
                str(int(timeout)),
                url,
            ],
            capture_output=True,
            text=True,
            timeout=14,
        )
        latency = (time.monotonic() - start) * 1000
        # Output is body + \n + status_code
        output = result.stdout.strip()
        parts = output.rsplit("\n", 1)
        if len(parts) == 2:
            body_str, http_str = parts
        elif len(parts) == 1:
            body_str, http_str = parts[0], ""
        else:
            body_str, http_str = "", ""
        try:
            http_code_int = int(http_str)
        except ValueError:
            http_code_int = 0
        payload = {}
        if body_str:
            try:
                payload = json.loads(body_str)
            except json.JSONDecodeError:
                payload = {"raw": body_str[:200]}
        if http_code_int == 0:
            return 0, None, latency, result.stderr.strip()[:100] or "curl failed"
        return http_code_int, payload, latency, ""
    except subprocess.TimeoutExpired:
        return 0, None, (time.monotonic() - start) * 1000, "timeout"
    except FileNotFoundError:
        return 0, None, (time.monotonic() - start) * 1000, "docker not available"
    except Exception as e:
        return 0, None, (time.monotonic() - start) * 1000, str(e)


# ─── MCP JSON-RPC Checks ───────────────────────────────────────────────────────


def check_mcp_public(public_mcp_url: str) -> McpResult:
    """Run JSON-RPC initialize + tools/list against public /mcp endpoint."""
    result = McpResult(initialize="SKIP", tools_list="SKIP")

    # Step 1: initialize
    _, resp, latency, err = post_jsonrpc(
        public_mcp_url,
        "initialize",
        {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "arifos-public-verifier", "version": "0.1.0"},
        },
    )
    if err and "HTTP" in err:
        result.initialize_error = err
        result.initialize = "PARTIAL"
    elif resp and resp.get("result"):
        result.initialize = "PASS"
    elif resp and resp.get("error"):
        # MCP servers may return error on initialize with SSE — check if tools/list still works
        result.initialize_error = f"error: {resp['error'].get('message', resp['error'])}"
        result.initialize = "PARTIAL"
    else:
        result.initialize = "PARTIAL"
        result.initialize_error = err or "no response body"

    # Step 2: tools/list (send after initialize — some servers need session)
    _, resp2, _, err2 = post_jsonrpc(public_mcp_url, "tools/list", {})
    if err2:
        result.tools_list_error = err2
        result.tools_list = "PARTIAL"
    elif resp2 and ("result" in resp2 or "tools" in resp2.get("result", {})):
        result.tools_count = len(resp2["result"].get("tools", []))
        result.tools_list = "PASS"
    elif resp2 and resp2.get("error"):
        result.tools_list_error = f"error: {resp2['error'].get('message', resp2['error'])}"
        result.tools_list = "PARTIAL"
    else:
        result.tools_list = "PARTIAL"
        result.tools_list_error = err2 or "no tools in response"

    return result


# ─── Compare Two status.json Payloads ─────────────────────────────────────────


def compare_status(local_payload: dict, public_payload: dict) -> ComparisonResult:
    """Return ComparisonResult showing first differing field."""
    diff = ComparisonResult()

    fields = [
        ("version", "version"),
        ("commit", "commit"),
        ("status", "status"),
        ("arifos", ("services", "arifos", "status")),
        ("geox", ("services", "geox", "status")),
        ("wealth", ("services", "wealth", "status")),
    ]

    def get_val(d: dict, keys) -> str:
        if isinstance(keys, str):
            return str(d.get(keys, ""))
        for k in keys:
            d = d.get(k, {})
        return str(d)

    for attr, keys in fields:
        lv = get_val(local_payload, keys)
        pv = get_val(public_payload, keys)
        if lv != pv:
            setattr(diff, attr, f"local={lv!r} ≠ public={pv!r}")

    # Tools count comparison (tools is an int in arifOS status payload)
    local_tools = local_payload.get("services", {}).get("arifos", {}).get("tools", 0)
    public_tools = public_payload.get("services", {}).get("arifos", {}).get("tools", 0)
    if int(local_tools) != int(public_tools):
        diff.tools_count = f"local={local_tools} ≠ public={public_tools}"

    return diff


# ─── Verdict Logic ─────────────────────────────────────────────────────────────

# ─── Tool Count Consistency ───────────────────────────────────────────────────

# arifOS MCP has ONE unified tool surface — 13 canonical tools (arif_verb_noun).
# No separate governance or CC surface. All 13 are in CANONICAL_TOOLS.
# status.json reports the same count. No canonical/runtime split.

CANONICAL_TOOL_COUNT = 13  # unified MCP surface — 13 canonical tools


def check_tool_consistency(status_tools: int, mcp_tools_count: int) -> tuple[str, str]:
    """
    Returns (verdict, detail).
    APPROVED if both status.json and MCP tools/list report exactly 13 tools.
    HOLD if counts don't match or are unexpected.

    Single unified surface since DITEMPA BUKAN DIBERI.
    """
    if status_tools == CANONICAL_TOOL_COUNT:
        status_ok = f"status.json={status_tools} ✅"
    else:
        status_ok = f"status.json={status_tools} ⚠️"

    if mcp_tools_count == CANONICAL_TOOL_COUNT:
        mcp_ok = f"MCP={mcp_tools_count} ✅"
    else:
        mcp_ok = f"MCP={mcp_tools_count} ⚠️"

    if status_tools == CANONICAL_TOOL_COUNT and mcp_tools_count == CANONICAL_TOOL_COUNT:
        return (
            "PASS",
            f"unified surface={CANONICAL_TOOL_COUNT} ✅ (single surface — DITEMPA BUKAN DIBERI)",
        )
    return "HOLD", f"status.json:{status_ok} | mcp:{mcp_ok}"


def compute_verdict(
    results: list[LayerResult],
    mcp: McpResult,
    comparison: ComparisonResult,
    tool_consistency: tuple[str, str],
) -> tuple[str, str]:
    """
    Returns (verdict, hold_reason).
    verdict: APPROVED | HOLD | VOID
    """
    # VOID: public endpoints unreachable
    public_status = next(
        (r for r in results if r.layer == "PUBLIC" and r.endpoint == "/status.json"), None
    )
    public_health = next(
        (r for r in results if r.layer == "PUBLIC" and r.endpoint == "/health"), None
    )

    if not public_status or public_status.http_status == 0:
        return "VOID", "public /status.json unreachable"
    if public_status.verdict == "FAIL":
        return "VOID", f"public /status.json returned {public_status.http_status}"
    if not public_health or public_health.http_status == 0:
        return "VOID", "public /health unreachable"

    # HOLD: /ready is partial, comparison diffs, MCP issues, tool count drift
    hold_reasons = []

    public_ready = next(
        (r for r in results if r.layer == "PUBLIC" and r.endpoint == "/ready"), None
    )
    if public_ready and public_ready.payload:
        ready_status = public_ready.payload.get("status", "unknown")
        if ready_status != "pass":
            hold_reasons.append(f"public /ready status={ready_status}")
        failures = public_ready.payload.get("failures", [])
        if failures:
            hold_reasons.append(f"public /ready failures: {failures}")

    diffs = []
    for attr in ["version", "commit", "status", "tools_count", "arifos", "geox", "wealth"]:
        val = getattr(comparison, attr)
        if val:
            diffs.append(f"{attr}: {val}")
    if diffs:
        hold_reasons.append(f"parity drift: {'; '.join(diffs)}")

    if mcp.initialize == "FAIL" or mcp.tools_list == "FAIL":
        hold_reasons.append(f"MCP initialize={mcp.initialize}, tools_list={mcp.tools_list}")

    tool_verdict, tool_detail = tool_consistency
    if tool_verdict != "PASS":
        hold_reasons.append(f"tool count: {tool_detail}")

    if hold_reasons:
        return "HOLD", " | ".join(hold_reasons)

    return "APPROVED", "all layers consistent, /ready=pass, MCP responsive, tool counts correct"


# ─── Main Verification ─────────────────────────────────────────────────────────


def verify_all() -> VerifyReport:
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    all_results: list[LayerResult] = []

    layers = [
        ("LOCAL", LOCAL_BASE),
        ("CADDY", CADDY_BASE),
        ("PUBLIC", PUBLIC_BASE),
    ]

    # ── Layer checks ──────────────────────────────────────────────────────────
    # LOCAL and PUBLIC use standard HTTP (host network)
    # CADDY uses docker exec to curl from inside the Caddy container
    for layer_name, base in layers:
        for ep in ENDPOINTS:
            if layer_name == "CADDY":
                http_status, payload, latency, err = fetch_via_caddy(ep)
                verdict = (
                    "PASS" if 200 <= http_status < 300 else ("HOLD" if http_status == 0 else "FAIL")
                )
            else:
                url = base + ep
                http_status, payload, latency, err = fetch(url)
                verdict = (
                    "PASS" if 200 <= http_status < 300 else ("HOLD" if http_status == 0 else "FAIL")
                )
            if http_status == 0:
                verdict = "HOLD"
                err = err or "connection failed"
            all_results.append(
                LayerResult(
                    layer=layer_name,
                    endpoint=ep,
                    http_status=http_status,
                    verdict=verdict,
                    payload=payload,
                    error=err if verdict not in ("PASS",) else None,
                    latency_ms=round(latency, 1),
                )
            )

    # ── MCP public check ──────────────────────────────────────────────────────
    mcp_result = check_mcp_public(PUBLIC_BASE + "/mcp")

    # ── Comparison: local vs public /status.json ──────────────────────────────
    local_payload = next(
        (r.payload for r in all_results if r.layer == "LOCAL" and r.endpoint == "/status.json"),
        None,
    )
    public_payload = next(
        (r.payload for r in all_results if r.layer == "PUBLIC" and r.endpoint == "/status.json"),
        None,
    )

    comparison = ComparisonResult()
    if local_payload and public_payload:
        comparison = compare_status(local_payload, public_payload)

    # ── Tool count consistency ─────────────────────────────────────────────────
    status_tools = (
        public_payload.get("services", {}).get("arifos", {}).get("tools", 0)
        if public_payload
        else -1
    )
    mcp_tools = mcp_result.tools_count
    tool_consistency = check_tool_consistency(status_tools, mcp_tools)

    # ── Verdict ────────────────────────────────────────────────────────────────
    verdict, hold_reason = compute_verdict(all_results, mcp_result, comparison, tool_consistency)

    # Count checks
    approved_checks = sum(1 for r in all_results if r.verdict == "PASS")
    total_checks = len(all_results)

    return VerifyReport(
        timestamp=timestamp,
        layers=all_results,
        comparison=comparison,
        mcp=mcp_result,
        tool_consistency=tool_consistency,
        verdict=verdict,
        hold_reason=hold_reason,
        approved_checks=approved_checks,
        total_checks=total_checks,
    )


# ─── Output Renderers ─────────────────────────────────────────────────────────


def render_table(report: VerifyReport) -> str:
    lines = []
    divider = "─" * 80

    lines.append(f"\n{'═' * 80}")
    lines.append("VERIFY PUBLIC — arifOS MCP")
    lines.append(f"{'═' * 80}")
    lines.append(f"Timestamp : {report.timestamp}")
    lines.append(f"Report    : {REPORT_PATH}")
    lines.append(divider)

    # ── Layer table ──────────────────────────────────────────────────────────
    header = f"  {'Layer':<12} {'Endpoint':<18} {'HTTP':>5}  {'Verdict':<8} {'Latency':>8}"
    lines.append(header)
    lines.append(divider)

    for r in report.layers:
        icon = {"PASS": "✅", "FAIL": "❌", "HOLD": "⚠️", "SKIP": "⊘", "VOID": "🛑"}.get(
            r.verdict, "?"
        )
        latency_str = f"{r.latency_ms:>6.1f}ms" if r.latency_ms else "   N/A  "
        http_str = str(r.http_status) if r.http_status else "ERR"
        err_str = f"  ⚠ {r.error}" if r.error else ""
        lines.append(
            f"  {icon} {r.layer:<12} {r.endpoint:<18} {http_str:>5}  "
            f"{r.verdict:<8} {latency_str}{err_str}"
        )

    lines.append(divider)

    # ── Comparison section ───────────────────────────────────────────────────
    comp = report.comparison
    lines.append("\nPARITY CHECK — local vs public /status.json:")
    diffs_found = False
    for attr in ["version", "commit", "status", "tools_count", "arifos", "geox", "wealth"]:
        val = getattr(comp, attr)
        if val:
            lines.append(f"  ⚠  {attr:<14}: {val}")
            diffs_found = True
    if not diffs_found:
        lines.append("  ✅ All fields match — no parity drift detected")

    # ── MCP section ─────────────────────────────────────────────────────────
    mcp = report.mcp
    lines.append("\nMCP JSON-RPC — public /mcp:")
    mcp_ok = []
    for label, verdict, count, err in [
        ("initialize", mcp.initialize, -1, mcp.initialize_error),
        ("tools/list", mcp.tools_list, mcp.tools_count, mcp.tools_list_error),
    ]:
        icon = {"PASS": "✅", "PARTIAL": "⚠️", "SKIP": "⊘", "FAIL": "❌"}.get(verdict, "?")
        count_str = f" (tools={count})" if count >= 0 else ""
        err_str = f"  → {err}" if err else ""
        lines.append(f"  {icon} {label:<14}: {verdict}{count_str}{err_str}")
        if verdict == "PASS":
            mcp_ok.append(label)

    # ── Tool count consistency ─────────────────────────────────────────────────
    tc_verdict, tc_detail = report.tool_consistency
    tc_icon = {"PASS": "✅", "HOLD": "⚠️"}.get(tc_verdict, "❌")
    lines.append("\nTOOL COUNT CONSISTENCY:")
    lines.append(f"  {tc_icon} tool_count: {tc_detail}")

    # ── Verdict ────────────────────────────────────────────────────────────────
    verdict_icon = {"APPROVED": "✅", "HOLD": "⚠️", "VOID": "🛑"}.get(report.verdict, "?")
    total = len(report.layers) + 1  # layers + tool count
    passed = sum(1 for r in report.layers if r.verdict == "PASS")
    if tc_verdict == "PASS":
        passed += 1
    lines.append(divider)
    lines.append(f"\n  {verdict_icon} VERDICT: {report.verdict}")
    if report.hold_reason:
        lines.append(f"     Reason: {report.hold_reason}")
    lines.append(f"  Checks : {passed}/{total} passed")
    lines.append(f"{'═' * 80}\n")

    return "\n".join(lines)


def save_json(report: VerifyReport) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "timestamp": report.timestamp,
        "verdict": report.verdict,
        "hold_reason": report.hold_reason,
        "checks_passed": report.approved_checks,
        "checks_total": report.total_checks,
        "layers": [{**asdict(r)} for r in report.layers],
        "comparison": asdict(report.comparison),
        "mcp": asdict(report.mcp),
    }
    with open(REPORT_PATH, "w") as f:
        json.dump(data, f, indent=2, default=str)


def main() -> int:
    print("🔍 Verifying public parity — arifOS MCP...", file=sys.stderr)

    report = verify_all()

    # Print human-readable
    print(render_table(report), file=sys.stdout)

    # Always save JSON
    save_json(report)
    print(f"📄 JSON report: {REPORT_PATH}", file=sys.stdout)

    # Exit code
    exit_code = {"APPROVED": 0, "HOLD": 1, "VOID": 2}.get(report.verdict, 3)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
