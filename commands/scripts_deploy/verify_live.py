#!/usr/bin/env uv run python3
"""
scripts/verify_live.py
======================
arifOS live observatory verifier.

Checks the deployed arifOS runtime against current git HEAD and verifies the
public Observatory surface does not report stale gaps or tool drift.
"""

from __future__ import annotations

import json
import subprocess  # nosec B404
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

LOCAL_BASE = "http://127.0.0.1:8080"
PUBLIC_BASE = "https://arifos.arif-fazil.com"
AAA_BASE = "https://aaa.arif-fazil.com"
REPORT_PATH = Path("tmp/verify_live_report.json")


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class LiveReport:
    head_sha: str
    checks: list[CheckResult]
    verdict: str


def _git_sha() -> str:
    result = subprocess.run(
        ["/usr/bin/git", "rev-parse", "--short=7", "HEAD"],  # nosec B603
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _fetch(url: str, timeout: float = 10.0) -> tuple[int, dict[str, Any] | None, str]:
    cmd = [
        "/usr/bin/curl",
        "-fsS",
        "--compressed",
        "--connect-timeout",
        "5",
        "--max-time",
        str(int(timeout)),
        url,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)  # nosec B603
    except Exception as exc:
        return 0, None, str(exc)
    if result.returncode != 0:
        detail = result.stderr.strip() or f"curl exit {result.returncode}"
        status = 0
        if result.stderr:
            for token in result.stderr.split():
                if token.isdigit():
                    status = int(token)
                    break
        return status, None, detail
    try:
        return 200, json.loads(result.stdout), ""
    except json.JSONDecodeError:
        return 200, {"raw": result.stdout[:500]}, "non-json response"


def _fetch_text(url: str, timeout: float = 10.0) -> tuple[int, str, str]:
    cmd = [
        "/usr/bin/curl",
        "-fsS",
        "--compressed",
        "--connect-timeout",
        "5",
        "--max-time",
        str(int(timeout)),
        url,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)  # nosec B603
    except Exception as exc:
        return 0, "", str(exc)
    if result.returncode != 0:
        detail = result.stderr.strip() or f"curl exit {result.returncode}"
        status = 0
        if result.stderr:
            for token in result.stderr.split():
                if token.isdigit():
                    status = int(token)
                    break
        return status, "", detail
    return 200, result.stdout, ""


def _tool_names(payload: dict[str, Any]) -> list[str]:
    raw_tools = payload.get("tools", [])
    names: list[str] = []
    for tool in raw_tools:
        if isinstance(tool, str):
            names.append(tool)
        elif isinstance(tool, dict) and isinstance(tool.get("name"), str):
            names.append(tool["name"])
    return names


def _record(checks: list[CheckResult], name: str, ok: bool, detail: str = "") -> None:
    checks.append(CheckResult(name=name, ok=ok, detail=detail))


def main() -> int:
    head_sha = _git_sha()
    checks: list[CheckResult] = []

    status, payload, err = _fetch(f"{LOCAL_BASE}/health")
    _record(checks, "local_health_http", status == 200, err or f"HTTP {status}")
    if status == 200 and payload:
        _record(
            checks,
            "local_health_commit",
            payload.get("git_commit") == head_sha,
            f"git_commit={payload.get('git_commit')} expected={head_sha}",
        )
        _record(
            checks,
            "local_health_tools",
            payload.get("tools_loaded") == 13,
            f"tools_loaded={payload.get('tools_loaded')}",
        )
        _record(
            checks,
            "local_health_drift",
            payload.get("runtime_drift") is False,
            f"runtime_drift={payload.get('runtime_drift')}",
        )

    status, payload, err = _fetch(f"{PUBLIC_BASE}/health")
    _record(checks, "public_health_http", status == 200, err or f"HTTP {status}")
    if status == 200 and payload:
        _record(
            checks,
            "public_health_commit",
            payload.get("git_commit") == head_sha,
            f"git_commit={payload.get('git_commit')} expected={head_sha}",
        )
        _record(
            checks,
            "public_health_tools",
            payload.get("tools_loaded") == 13,
            f"tools_loaded={payload.get('tools_loaded')}",
        )
        _record(
            checks,
            "public_health_drift",
            payload.get("runtime_drift") is False,
            f"runtime_drift={payload.get('runtime_drift')}",
        )

    status, payload, err = _fetch(f"{PUBLIC_BASE}/tools")
    _record(checks, "public_tools_http", status == 200, err or f"HTTP {status}")
    if status == 200 and payload:
        names = _tool_names(payload)
        _record(checks, "public_tools_count", len(names) == 13, f"count={len(names)}")
        _record(
            checks,
            "public_tools_no_daily_brief",
            "arif_daily_intelligence_brief" not in names,
            (
                "arif_daily_intelligence_brief present"
                if "arif_daily_intelligence_brief" in names
                else ""
            ),
        )

    status, payload, err = _fetch(f"{PUBLIC_BASE}/inspector/sot")
    _record(checks, "public_sot_http", status == 200, err or f"HTTP {status}")
    if status == 200 and payload:
        _record(
            checks,
            "public_sot_verdict",
            payload.get("verdict") == "SEAL",
            f"verdict={payload.get('verdict')}",
        )
        _record(
            checks,
            "public_sot_live_count",
            payload.get("live_count") == 13,
            f"live_count={payload.get('live_count')}",
        )
        _record(
            checks,
            "public_sot_main_count",
            payload.get("main_count") == 13,
            f"main_count={payload.get('main_count')}",
        )

    status, payload, err = _fetch(f"{PUBLIC_BASE}/api/status")
    _record(checks, "public_status_http", status == 200, err or f"HTTP {status}")
    if status == 200 and payload:
        known_gaps = payload.get("known_gaps") or []
        _record(
            checks,
            "public_status_known_gaps_empty",
            len(known_gaps) == 0,
            f"known_gaps_len={len(known_gaps)}",
        )

    status, text, err = _fetch_text(f"{AAA_BASE}/")
    _record(checks, "aaa_home_http", status == 200, err or f"HTTP {status}")
    _record(
        checks, "aaa_home_nonempty", bool(text.strip()), "empty body" if not text.strip() else ""
    )

    status, payload, err = _fetch(f"{AAA_BASE}/a2a/agents.json")
    _record(checks, "aaa_agents_http", status == 200, err or f"HTTP {status}")
    if status == 200 and payload:
        agents = payload.get("agents")
        ok = isinstance(agents, list) and len(agents) > 0
        _record(
            checks,
            "aaa_agents_present",
            ok,
            f"agents={len(agents) if isinstance(agents, list) else 'missing'}",
        )

    ok_count = sum(1 for c in checks if c.ok)
    verdict = "APPROVED" if ok_count == len(checks) else "HOLD"
    report = LiveReport(head_sha=head_sha, checks=checks, verdict=verdict)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(
            {
                "head_sha": report.head_sha,
                "verdict": report.verdict,
                "checks": [asdict(check) for check in report.checks],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {"head_sha": head_sha, "verdict": verdict, "passed": ok_count, "total": len(checks)},
            indent=2,
        )
    )

    failures = [c for c in checks if not c.ok]
    if failures:
        for failure in failures:
            print(f"FAIL {failure.name}: {failure.detail}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
