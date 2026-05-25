#!/usr/bin/env python3
"""Audit arifOS source-of-truth alignment.

This is a fast local guard for documentation and metadata drift. It checks the
code-derived runtime surface against package metadata, Docker labels, Makefile
health port, README claims, and the JSON tool registry.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def fail(message: str) -> None:
    print(f"FAIL: {message}")


def ok(message: str) -> None:
    print(f"OK: {message}")


def check_contains(label: str, text: str, needle: str, failures: list[str]) -> None:
    if needle in text:
        ok(f"{label} contains {needle!r}")
        return
    failures.append(f"{label} missing {needle!r}")
    fail(failures[-1])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        default=None,
        metavar="URL",
        help="Optional live health URL to compare, for example http://127.0.0.1:8088/health",
    )
    args = parser.parse_args()

    failures: list[str] = []

    sys.path.insert(0, str(ROOT))
    from arifosmcp.constitutional_map import (  # noqa: PLC0415
        CANONICAL_TOOLS,
        list_constitutional_tools,
        list_probe_tools,
    )
    from arifosmcp.prompts import CANONICAL_PROMPTS  # noqa: PLC0415
    from arifosmcp.resources import CANONICAL_RESOURCES  # noqa: PLC0415
    from arifosmcp.server import mcp, v2_tools_registered  # noqa: PLC0415

    package = tomllib.loads(read_text("pyproject.toml"))["project"]
    package_version = package["version"]
    runtime_version = str(mcp.version)
    total_tools = len(CANONICAL_TOOLS)
    registered_tools = len(v2_tools_registered)
    constitutional_tools = len(list_constitutional_tools())
    probe_tools = len(list_probe_tools())
    prompt_count = len(CANONICAL_PROMPTS)
    resource_count = len(CANONICAL_RESOURCES)

    expected_summary = (
        f"package={package_version} runtime={runtime_version} "
        f"tools={registered_tools}/{total_tools} constitutional={constitutional_tools} "
        f"probes={probe_tools} prompts={prompt_count} resources={resource_count}"
    )
    print(f"== arifOS SOT audit: {expected_summary}")

    if registered_tools != total_tools:
        failures.append(f"registered tool count {registered_tools} != map count {total_tools}")
        fail(failures[-1])
    else:
        ok("registered tool count matches constitutional map")

    if constitutional_tools != 13 or probe_tools != 2 or total_tools != 15:
        failures.append("tool partition mismatch: expected 15 total, 13 constitutional, 2 probes")
        fail(failures[-1])
    else:
        ok("tool partition is 15 total / 13 constitutional / 2 probes")

    registry = json.loads(read_text("arifosmcp/tool_registry.json"))
    registry_tools = registry.get("tools", {})
    registry_names = set(registry_tools)
    map_names = set(CANONICAL_TOOLS)
    if registry_names != map_names:
        failures.append(
            "tool_registry.json names differ from constitutional_map.py: "
            f"missing={sorted(map_names - registry_names)} extra={sorted(registry_names - map_names)}"
        )
        fail(failures[-1])
    else:
        ok("tool_registry.json names match constitutional_map.py")

    registry_expectations = {
        "canonical_count": constitutional_tools,
        "probe_count": probe_tools,
        "total_surface": total_tools,
    }
    for key, expected in registry_expectations.items():
        actual = registry.get(key)
        if actual != expected:
            failures.append(f"tool_registry.json {key}={actual!r}, expected {expected!r}")
            fail(failures[-1])
        else:
            ok(f"tool_registry.json {key}={actual}")

    dockerfile = read_text("Dockerfile")
    makefile = read_text("Makefile")
    readme = read_text("README.md")
    pyproject = read_text("pyproject.toml")
    server = read_text("arifosmcp/server.py")

    check_contains("README.md", readme, f"Package version | `{package_version}`", failures)
    check_contains("README.md", readme, f"Runtime version | `{runtime_version}`", failures)
    check_contains("README.md", readme, "13 canonical MCP capability tools", failures)
    check_contains("README.md", readme, "Canonical prompts | 8", failures)
    check_contains("README.md", readme, "Canonical resources | 5", failures)
    check_contains("pyproject.toml", pyproject, "13 canonical MCP capability tools", failures)
    check_contains("Dockerfile", dockerfile, f"ARIFOS_VERSION={runtime_version}", failures)
    check_contains("Dockerfile", dockerfile, f'server.version="{runtime_version}"', failures)
    check_contains("Dockerfile", dockerfile, "13 canonical MCP capability tools", failures)
    check_contains("Makefile", makefile, "http://localhost:8088/health", failures)
    check_contains("Makefile", makefile, "python scripts/audit_sot.py", failures)
    check_contains("arifosmcp/server.py", server, "13 canonical MCP capability tools", failures)

    if re.search(r"localhost:8000/health", makefile):
        failures.append("Makefile still references localhost:8000/health")
        fail(failures[-1])

    if args.live:
        import urllib.request

        try:
            with urllib.request.urlopen(args.live, timeout=5) as response:
                live = json.loads(response.read().decode("utf-8"))
            live_tools = live.get("tools") or live.get("tools_loaded")
            live_version = live.get("version")
            print(f"INFO: live version={live_version!r} live_tools={live_tools!r}")
            if live_tools is not None and int(live_tools) != total_tools:
                failures.append(f"live tool count {live_tools!r} != source total {total_tools}")
                fail(failures[-1])
        except Exception as exc:  # noqa: BLE001
            failures.append(f"live check failed for {args.live}: {exc}")
            fail(failures[-1])

    print("== Verdict ==")
    if failures:
        print(f"DRIFT DETECTED ({len(failures)} issue(s))")
        return 1
    print("NO DRIFT DETECTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
