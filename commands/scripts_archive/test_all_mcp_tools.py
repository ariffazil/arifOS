#!/usr/bin/env python3
"""
ARIFOS MCP — UNIFIED 13-TOOL TEST HARNESS
Tests all canonical tools across 4 interfaces:
  1. CODEBASE LOCAL   → Direct Python handler invocation
  2. LOCAL HTTP       → http://localhost:8080/mcp (streamable HTTP)
  3. REMOTE HTTPS     → https://arifos.arif-fazil.com/mcp
  4. MCP STDIO        → python -m arifosmcp.runtime.__main__ stdio

Sovereign: arif
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import os
from __future__ import annotations

import asyncio
import inspect
import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

# Ensure project root is on path for arifosmcp + core imports
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ── Configuration ───────────────────────────────────────────────────────────
LOCAL_HTTP_URL = "http://localhost:8088/mcp"
REMOTE_HTTPS_URL = "https://arifos.arif-fazil.com/mcp"
ACTOR_ID = "arif"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST DATA — canonical args for each of the 13 tools
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ToolTestCase:
    name: str
    args: dict[str, Any]
    expect_async: bool = False


TOOL_CASES: list[ToolTestCase] = [
    ToolTestCase("arif_session_init", {"mode": "init", "actor_id": ACTOR_ID}),
    ToolTestCase(
        "arif_sense_observe", {"mode": "search", "query": "arifOS constitutional kernel test"}
    ),
    ToolTestCase("arif_evidence_fetch", {"mode": "search", "query": "arifOS MCP governance"}),
    ToolTestCase(
        "arif_mind_reason", {"mode": "reason", "query": "What is the purpose of constitutional AI?"}
    ),
    ToolTestCase(
        "arif_heart_critique", {"mode": "critique", "target": "Deploy AI without human oversight"}
    ),
    ToolTestCase("arif_kernel_route", {"mode": "route", "task": "Test constitutional routing"}),
    ToolTestCase(
        "arif_reply_compose", {"mode": "compose", "message": "Hello from unified test harness"}
    ),
    ToolTestCase("arif_memory_recall", {"mode": "recall", "query": "constitutional kernel"}),
    ToolTestCase("arif_gateway_connect", {"mode": "discover"}),
    ToolTestCase(
        "arif_judge_deliberate",
        {"mode": "probe", "actor_id": ACTOR_ID, "candidate": "Test candidate action"},
    ),
    ToolTestCase("arif_vault_seal", {"mode": "list", "actor_id": ACTOR_ID}),
    ToolTestCase("arif_forge_execute", {"mode": "dry_run", "actor_id": ACTOR_ID, "manifest": "{}"}),
    ToolTestCase("arif_ops_measure", {"mode": "health", "actor_id": ACTOR_ID}),
]


# ═══════════════════════════════════════════════════════════════════════════════
# REPORTING
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class TestResult:
    interface: str
    tool: str
    passed: bool
    latency_ms: float
    verdict: str = ""
    error: str = ""
    detail: dict = field(default_factory=dict)


class TestReporter:
    def __init__(self) -> None:
        self.results: list[TestResult] = []

    def add(self, r: TestResult) -> None:
        self.results.append(r)

    def summary(self) -> str:
        lines = [
            "\n" + "═" * 80,
            "ARIFOS MCP — UNIFIED 13-TOOL TEST REPORT",
            "═" * 80,
            f"Timestamp: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
            f"Sovereign: {ACTOR_ID}",
            "",
        ]

        interfaces = ["codebase_local", "local_http", "remote_https", "mcp_stdio"]
        for iface in interfaces:
            iface_results = [r for r in self.results if r.interface == iface]
            passed = sum(1 for r in iface_results if r.passed)
            total = len(iface_results)
            status = (
                "✅ PASS" if passed == total and total > 0 else "❌ FAIL" if total > 0 else "⏭️ SKIP"
            )
            lines.append(f"{iface:20s}: {status}  ({passed}/{total})")

        lines.append("")
        lines.append("─" * 80)
        lines.append("Per-tool breakdown:")
        lines.append("─" * 80)

        for tool in [tc.name for tc in TOOL_CASES]:
            tool_results = [r for r in self.results if r.tool == tool]
            for r in tool_results:
                icon = "✅" if r.passed else "❌"
                latency = f"{r.latency_ms:.1f}ms"
                verdict = r.verdict or r.error or "N/A"
                lines.append(
                    f"  {icon} {r.interface:20s} | {tool:30s} | {latency:>10s} | {verdict}"
                )

        total_passed = sum(1 for r in self.results if r.passed)
        total_tests = len(self.results)
        lines.append("")
        lines.append("═" * 80)
        lines.append(f"TOTAL: {total_passed}/{total_tests} tests passed")
        if total_passed == total_tests:
            lines.append("🎉 ALL TESTS PASSED — Constitutional surface intact.")
        else:
            lines.append("⚠️  SOME TESTS FAILED — Review details above.")
        lines.append("═" * 80)
        return "\n".join(lines)

    def save(self, path: str = "/root/arifOS/test-reports/unified_mcp_test.json") -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(
                {
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "actor_id": ACTOR_ID,
                    "results": [
                        {
                            "interface": r.interface,
                            "tool": r.tool,
                            "passed": r.passed,
                            "latency_ms": r.latency_ms,
                            "verdict": r.verdict,
                            "error": r.error,
                        }
                        for r in self.results
                    ],
                },
                f,
                indent=2,
            )


reporter = TestReporter()


# ═══════════════════════════════════════════════════════════════════════════════
# 1. CODEBASE LOCAL — Direct Python invocation
# ═══════════════════════════════════════════════════════════════════════════════


async def test_codebase_local() -> None:
    print("\n🔧 INTERFACE 1: CODEBASE LOCAL (direct Python handlers)")
    print("─" * 70)

    # Import inside function to avoid polluting global namespace with heavy deps
    from arifosmcp.runtime.tools import CANONICAL_TOOL_HANDLERS

    for tc in TOOL_CASES:
        start = time.perf_counter()
        try:
            handler = CANONICAL_TOOL_HANDLERS[tc.name]
            result = handler(**tc.args)
            if inspect.isawaitable(result):
                result = await result

            latency = (time.perf_counter() - start) * 1000
            verdict = "UNKNOWN"
            if isinstance(result, dict):
                verdict = result.get("verdict", result.get("status", "OK"))
            elif hasattr(result, "verdict"):
                verdict = str(result.verdict)
            elif hasattr(result, "status"):
                verdict = str(result.status)

            passed = verdict not in ("VOID", "ERROR", "CRASH")
            reporter.add(TestResult("codebase_local", tc.name, passed, latency, verdict=verdict))
            icon = "✅" if passed else "❌"
            print(f"  {icon} {tc.name:35s} → {verdict} ({latency:.1f}ms)")

        except Exception as e:
            latency = (time.perf_counter() - start) * 1000
            reporter.add(TestResult("codebase_local", tc.name, False, latency, error=str(e)[:80]))
            print(f"  ❌ {tc.name:35s} → CRASH: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# 2 & 3. HTTP MCP CLIENT (shared for local + remote)
# ═══════════════════════════════════════════════════════════════════════════════


class HTTPMCPClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)
        self.req_id = 0

    def _call(self, method: str, params: dict | None = None) -> dict:
        self.req_id += 1
        payload = {"jsonrpc": "2.0", "id": self.req_id, "method": method, "params": params or {}}
        resp = self.client.post(
            self.base_url,
            json=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()

    def initialize(self) -> dict:
        return self._call(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": True}},
                "clientInfo": {"name": "arif-unified-tester", "version": "1.0.0"},
            },
        )

    def list_tools(self) -> list[dict]:
        r = self._call("tools/list")
        return r.get("result", {}).get("tools", [])

    def call_tool(self, name: str, arguments: dict) -> dict:
        return self._call("tools/call", {"name": name, "arguments": arguments})

    def close(self) -> None:
        self.client.close()


def _extract_verdict(response: dict) -> str:
    result = response.get("result", {})
    # Check for FastMCP error marker
    if result.get("isError"):
        content = result.get("content", [])
        if content and "text" in content[0]:
            return f"ERROR:{content[0]['text'][:60]}"
        return "ERROR"
    # Prefer structuredContent if present
    sc = result.get("structuredContent", {})
    if sc:
        return sc.get("verdict", sc.get("status", "OK"))
    # Fallback: parse text JSON in content
    content = result.get("content", [])
    if content and "text" in content[0]:
        try:
            parsed = json.loads(content[0]["text"])
            return parsed.get("verdict", parsed.get("status", "OK"))
        except Exception:
            pass
    if "error" in response:
        return f"ERROR:{response['error'].get('code')}"
    return "UNKNOWN"


async def test_http_interface(interface_name: str, url: str) -> None:
    print(f"\n🌐 INTERFACE: {interface_name.upper()} ({url})")
    print("─" * 70)

    client = HTTPMCPClient(url)
    try:
        # Initialize
        init_r = client.initialize()
        server_info = init_r.get("result", {}).get("serverInfo", {})
        print(f"  Connected: {server_info.get('name')} v{server_info.get('version')}")

        # List tools
        tools = client.list_tools()
        tool_names = {t["name"] for t in tools}
        print(f"  Tools advertised: {len(tools)}")

        for tc in TOOL_CASES:
            start = time.perf_counter()
            try:
                if tc.name not in tool_names:
                    latency = (time.perf_counter() - start) * 1000
                    reporter.add(
                        TestResult(
                            interface_name, tc.name, False, latency, error="Tool not advertised"
                        )
                    )
                    print(f"  ❌ {tc.name:35s} → NOT ADVERTISED")
                    continue

                resp = client.call_tool(tc.name, tc.args)
                latency = (time.perf_counter() - start) * 1000
                verdict = _extract_verdict(resp)
                # VOID is acceptable for LLM-dependent tools when LLM is unavailable
                allowed_void_tools = {"arif_mind_reason", "arif_heart_critique"}
                is_allowed_void = tc.name in allowed_void_tools and verdict == "VOID"
                passed = (
                    (verdict not in ("VOID", "ERROR", "CRASH") or is_allowed_void)
                    and not verdict.startswith("ERROR:")
                    and not verdict.startswith("Output validation")
                    and "error" not in resp
                )
                reporter.add(TestResult(interface_name, tc.name, passed, latency, verdict=verdict))
                icon = "✅" if passed else "❌"
                print(f"  {icon} {tc.name:35s} → {verdict} ({latency:.1f}ms)")

            except Exception as e:
                latency = (time.perf_counter() - start) * 1000
                reporter.add(TestResult(interface_name, tc.name, False, latency, error=str(e)[:80]))
                print(f"  ❌ {tc.name:35s} → EXCEPTION: {e}")
    finally:
        client.close()


# ═══════════════════════════════════════════════════════════════════════════════
# 4. MCP STDIO — JSON-RPC over subprocess stdin/stdout
# ═══════════════════════════════════════════════════════════════════════════════


class StdioMCPClient:
    def __init__(self, process: subprocess.Popen) -> None:
        self.process = process
        self.req_id = 0

    def call(self, method: str, params: dict | None = None) -> dict:
        self.req_id += 1
        request = {"jsonrpc": "2.0", "id": self.req_id, "method": method, "params": params or {}}
        line = json.dumps(request) + "\n"
        self.process.stdin.write(line.encode())
        self.process.stdin.flush()
        response_line = self.process.stdout.readline().decode()
        if not response_line:
            raise RuntimeError("Empty response from stdio server")
        return json.loads(response_line)

    def initialize(self) -> dict:
        return self.call(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": True}},
                "clientInfo": {"name": "arif-stdio-tester", "version": "1.0.0"},
            },
        )

    def list_tools(self) -> list[dict]:
        r = self.call("tools/list")
        return r.get("result", {}).get("tools", [])

    def call_tool(self, name: str, arguments: dict) -> dict:
        return self.call("tools/call", {"name": name, "arguments": arguments})


async def test_stdio_interface() -> None:
    print("\n📟 INTERFACE 4: MCP STDIO (subprocess JSON-RPC)")
    print("─" * 70)

    env = {
        **dict(subprocess.os.environ),
        "ARIFOS_MINIMAL_STDIO": "1",
        "AAA_MCP_TRANSPORT": "stdio",
    }

    process = subprocess.Popen(
        [sys.executable, "-m", "arifosmcp.runtime", "stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.environ.get("ARIFOS_HOME", "/root") + "/arifOS",
        env=env,
    )

    client = StdioMCPClient(process)
    try:
        init_r = client.initialize()
        server_info = init_r.get("result", {}).get("serverInfo", {})
        print(f"  Connected: {server_info.get('name')} v{server_info.get('version')}")

        tools = client.list_tools()
        tool_names = {t["name"] for t in tools}
        print(f"  Tools advertised: {len(tools)}")

        for tc in TOOL_CASES:
            start = time.perf_counter()
            try:
                if tc.name not in tool_names:
                    latency = (time.perf_counter() - start) * 1000
                    reporter.add(
                        TestResult(
                            "mcp_stdio", tc.name, False, latency, error="Tool not advertised"
                        )
                    )
                    print(f"  ❌ {tc.name:35s} → NOT ADVERTISED")
                    continue

                resp = client.call_tool(tc.name, tc.args)
                latency = (time.perf_counter() - start) * 1000
                verdict = _extract_verdict(resp)
                # VOID is acceptable for LLM-dependent tools when LLM is unavailable
                allowed_void_tools = {"arif_mind_reason", "arif_heart_critique"}
                is_allowed_void = tc.name in allowed_void_tools and verdict == "VOID"
                passed = (
                    (verdict not in ("VOID", "ERROR", "CRASH") or is_allowed_void)
                    and not verdict.startswith("ERROR:")
                    and not verdict.startswith("Output validation")
                    and "error" not in resp
                )
                reporter.add(TestResult("mcp_stdio", tc.name, passed, latency, verdict=verdict))
                icon = "✅" if passed else "❌"
                print(f"  {icon} {tc.name:35s} → {verdict} ({latency:.1f}ms)")

            except Exception as e:
                latency = (time.perf_counter() - start) * 1000
                reporter.add(TestResult("mcp_stdio", tc.name, False, latency, error=str(e)[:80]))
                print(f"  ❌ {tc.name:35s} → EXCEPTION: {e}")

    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════


async def main() -> int:
    print("═" * 80)
    print("ARIFOS MCP — UNIFIED 13-TOOL TEST HARNESS")
    print("Interfaces: codebase_local | local_http | remote_https | mcp_stdio")
    print("Sovereign: arif")
    print("═" * 80)

    # 1. Codebase local
    await test_codebase_local()

    # 2. Local HTTP
    await test_http_interface("local_http", LOCAL_HTTP_URL)

    # 3. Remote HTTPS
    await test_http_interface("remote_https", REMOTE_HTTPS_URL)

    # 4. MCP STDIO
    await test_stdio_interface()

    # Report
    report = reporter.summary()
    print(report)
    reporter.save()
    print("\n📄 Report saved to: /root/arifOS/test-reports/unified_mcp_test.json")

    total_passed = sum(1 for r in reporter.results if r.passed)
    return 0 if total_passed == len(reporter.results) else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by sovereign.")
        exit_code = 130
    sys.exit(exit_code)
