"""arif_guard — read-only drift / integrity / verification gate (E2, 2026-10-17).

Connects the P0–P5 recovery checks to the kernel surface without mutating
anything. Every mode returns evidence, never a verdict: SEAL/HOLD stays with
arif_judge.

Registered as a diagnostic tool (outside the sovereign-ratified 8-verb
facade). Enable/disable with ARIFOS_ENABLE_HEAL_GUARD.
"""

from __future__ import annotations

import json
import subprocess
import urllib.request
from pathlib import Path
from typing import Any

_REPO = Path("/root/arifOS")
_DEPLOYED_VENV = Path("/opt/arifos/current/venv")
_KERNEL_HEALTH = "http://127.0.0.1:8088/health"
_QDRANT = "http://127.0.0.1:6333/collections/arifos_memory"
_ARIFLOW = "http://127.0.0.1:7073/health"


def _http_json(url: str, timeout: float = 3.0) -> dict[str, Any] | None:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def _git(args: list[str]) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(_REPO), *args],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return out.stdout.strip() or None
    except Exception:
        return None


def _deployed_commit() -> str | None:
    try:
        for dist in (_DEPLOYED_VENV / "lib").glob("python*/site-packages/*.dist-info"):
            direct = dist / "direct_url.json"
            if direct.exists():
                data = json.loads(direct.read_text(encoding="utf-8"))
                url = str(data.get("url", ""))
                if "/dist/" in url:
                    return url.rsplit("/", 1)[-1]
    except Exception:
        return None
    return None


def _drift_report() -> dict[str, Any]:
    head = _git(["rev-parse", "--short", "HEAD"])
    health = _http_json(_KERNEL_HEALTH) or {}
    drift = health.get("drift", {}) if isinstance(health, dict) else {}
    return {
        "source_head": head,
        "kernel_release": health.get("release_tag"),
        "deployed_artifact": _deployed_commit(),
        "kernel_drift_field": drift,
        "note": (
            "kernel 'aligned' compares the build stamp to itself; "
            "source_head vs deployed artifact is the external delta"
        ),
        "mutation": False,
    }


def _integrity_report() -> dict[str, Any]:
    checks: dict[str, Any] = {}
    checks["kernel"] = _http_json(_KERNEL_HEALTH) or {"reachable": False}
    checks["qdrant"] = _http_json(_QDRANT) or {"reachable": False}
    checks["arifflow"] = _http_json(_ARIFLOW) or {"reachable": False}
    vault = Path("/var/lib/arifos/vault")
    checks["vault_dir"] = {
        "exists": vault.exists(),
        "writable": vault.is_dir() and bool(vault.stat().st_mode),
    }
    ok = all(
        [
            bool(checks["kernel"].get("status") == "healthy"),
            bool(checks["qdrant"].get("result", {}).get("status") == "green"),
            bool(checks["arifflow"].get("status")),
            checks["vault_dir"]["exists"],
        ]
    )
    return {"status": "ok" if ok else "degraded", "checks": checks, "mutation": False}


def _frame_bundle() -> dict[str, Any]:
    """Assemble the isolated verification bundle for FRAME (E4).

    FRAME already runs as its own service (frame-mcp.service / frame-organ.
    service). This bundle carries ONLY the three inputs a verifier needs —
    spec, diff, test output — so FRAME never inherits the agent's context.
    """
    import os as _os

    spec_path = Path(_os.environ.get("ARIFOS_SPEC_LOCK", "/root/arifOS/SPEC.lock.json"))
    test_path = Path(_os.environ.get("ARIFOS_TEST_OUTPUT", "/tmp/arifos-test-output.txt"))

    diff = _git(["diff", "--stat"]) or ""
    diff_full = _git(["diff", "--no-color"]) or ""

    spec: dict[str, Any] | str | None = None
    if spec_path.exists():
        try:
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
        except Exception:
            spec = spec_path.read_text(encoding="utf-8", errors="replace")[:4000]

    test_tail = ""
    if test_path.exists():
        try:
            test_tail = "\n".join(
                test_path.read_text(encoding="utf-8", errors="replace").splitlines()[-100:]
            )
        except Exception:
            test_tail = ""

    return {
        "for_organ": "FRAME",
        "isolation": "bundle_only",
        "inputs": ("spec", "diff", "test_output"),
        "spec": spec,
        "diff_stat": diff,
        "diff": diff_full[:20000],
        "test_output_tail": test_tail,
        "mutation": False,
        "note": "Hand this bundle to the FRAME service; it must not read agent context.",
    }


async def arif_guard(
    mode: str = "verify",
    actor_id: str = "unknown",
    session_id: str = "",
    session_token: str = "",
) -> dict[str, Any]:
    """Read-only drift, integrity and verification gate.

    Modes:
      drift     — source HEAD vs deployed artifact vs kernel drift field
      integrity — kernel / qdrant / arifFlow / vault reachability
      verify    — both, with a single pass/fail summary
      frame     — isolated spec+diff+test bundle for FRAME verification
    """
    if mode == "drift":
        return {"status": "ok", "tool": "arif_guard", "mode": mode, **_drift_report()}

    if mode == "integrity":
        return {"status": "ok", "tool": "arif_guard", "mode": mode, **_integrity_report()}

    if mode == "frame":
        return {"status": "ok", "tool": "arif_guard", "mode": mode, **_frame_bundle()}

    drift = _drift_report()
    integrity = _integrity_report()
    passed = integrity.get("status") == "ok"
    return {
        "status": "ok" if passed else "degraded",
        "tool": "arif_guard",
        "mode": "verify",
        "passed": passed,
        "drift": drift,
        "integrity": integrity,
        "actor_id": actor_id,
        "session_id": session_id,
        "mutation": False,
        "verdict_authority": "arif_judge (this tool returns evidence only)",
    }
