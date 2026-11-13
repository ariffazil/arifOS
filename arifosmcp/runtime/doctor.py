"""arifos doctor — one-command federation diagnostic (human-facing, non-MCP).

Answers in ~1s, for a human in a terminal:
  1. Which of the 13 organs are LIVE vs DOWN right now (per-organ endpoint map —
     NOT a uniform /health sweep; FED :4000 is HAProxy and has no /health, it serves
     /v1/models only).
  2. Three runtime version/attestation states:
     (a) active repo  — /root/arifOS branch + commit (what the running code IS)
     (b) deployed     — the commit stamp build.py trusts (/opt/arifos/releases/...)
     (c) PyPI         — the latest published version (network, 3s timeout)

Exit code: 0 = all organs live; 1 = at least one organ down (script-friendly).

Usage:  arifos doctor [--json]
        arifos doctor   # human-readable table
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

# ── Per-organ endpoint map (verified 2026-11-13 against live JSON bodies) ─────
# Path "models" means probe /v1/models (HAProxy has no /health). "health" = /health.
ORGANS: list[tuple[str, str, str]] = [
    ("arifOS-kernel", "http://127.0.0.1:8088/health", "health"),
    ("A-FORGE-rest", "http://127.0.0.1:7071/health", "health"),
    ("A-FORGE-mcp", "http://127.0.0.1:7072/health", "health"),
    ("arifFlow", "http://127.0.0.1:7073/health", "health"),
    ("GEOX", "http://127.0.0.1:8081/health", "health"),
    ("WEALTH", "http://127.0.0.1:18082/health", "health"),
    ("WELL", "http://127.0.0.1:18083/health", "health"),
    ("FRAME", "http://127.0.0.1:18085/health", "health"),  # NOT 18087
    ("HERMES", "http://127.0.0.1:18087/health", "health"),  # NOT 18085
    ("CHRON", "http://127.0.0.1:18102/health", "health"),
    ("FED", "http://127.0.0.1:4000/v1/models", "models"),  # HAProxy: /v1/models only
    ("fed-router", "http://127.0.0.1:7074/health", "health"),
    ("A2A-gateway", "http://127.0.0.1:3001/health", "health"),
]

TIMEOUT = 3.0


def _fetch(url: str) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": "arifos-doctor/1"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.status, resp.read(32768)


def _probe(name: str, url: str) -> dict[str, str]:
    try:
        code, body = _fetch(url)
        identity = ""
        try:
            data = json.loads(body)
            identity = (
                data.get("organ")
                or data.get("service")
                or data.get("name")
                or data.get("organ_name")
                or ""
            )
        except Exception:
            pass
        return {"name": name, "state": "LIVE", "code": str(code), "identity": identity}
    except urllib.error.HTTPError as e:
        return {"name": name, "state": "LIVE", "code": str(e.code), "identity": ""}
    except Exception:
        return {"name": name, "state": "DOWN", "code": "", "identity": ""}


def _repo_state() -> dict[str, str]:
    try:
        branch = subprocess.run(
            ["git", "-C", "/root/arifOS", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
    except Exception:
        branch = "unknown"
    try:
        commit = subprocess.run(
            ["git", "-C", "/root/arifOS", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
    except Exception:
        commit = "unknown"
    return {"branch": branch, "commit": commit}


def _deployed_state() -> dict[str, str]:
    """The commit stamp build.py trusts (see arifosmcp/runtime/build.py)."""
    for stamp in (
        "/opt/arifos/releases/deployed-commit",
        "/opt/arifos/app/.git_commit",
        "/root/arifOS/.git_commit",
    ):
        p = Path(stamp)
        try:
            v = p.read_text().strip()
            if len(v) >= 7:
                return {"stamp": stamp, "commit": v[:40]}
        except Exception:
            continue
    return {"stamp": "(none found)", "commit": "UNKNOWN"}


def _pypi_version() -> str:
    try:
        with urllib.request.urlopen("https://pypi.org/pypi/arifos/json", timeout=TIMEOUT) as resp:
            data = json.loads(resp.read(1024 * 512))
            return data.get("info", {}).get("version", "UNKNOWN")
    except Exception:
        return "UNREACHABLE"


def run_doctor(args: list[str]) -> int:
    as_json = "--json" in args or "-j" in args

    organs = [_probe(n, u) for n, u, _ in ORGANS]
    live = sum(1 for o in organs if o["state"] == "LIVE")
    down = sum(1 for o in organs if o["state"] == "DOWN")
    repo = _repo_state()
    deployed = _deployed_state()
    pypi = _pypi_version()

    if as_json:
        print(
            json.dumps(
                {
                    "organs": organs,
                    "summary": {"total": len(organs), "live": live, "down": down},
                    "repo": repo,
                    "deployed": deployed,
                    "pypi_version": pypi,
                },
                indent=2,
            )
        )
    else:
        print("arifOS federation — doctor")
        print(f"  organs: {live}/{len(organs)} LIVE" + (f" · {down} DOWN" if down else ""))
        for o in organs:
            mark = "OK " if o["state"] == "LIVE" else "!! "
            ident = f"  ({o['identity']})" if o["identity"] else ""
            print(f"  {mark} {o['name']:<16} {o['state']:<5} {o['code']}{ident}")
        print(f"  repo:     {repo['branch']} @ {repo['commit']}")
        print(f"  deployed: {deployed['commit']}  [{deployed['stamp']}]")
        print(f"  pypi:     {pypi}")

    return 0 if down == 0 else 1


if __name__ == "__main__":
    sys.exit(run_doctor(sys.argv[1:]))
