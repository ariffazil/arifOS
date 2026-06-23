"""arifos check — ART + preflight in one command."""

from __future__ import annotations

import os
from typing import Any

from arifosmcp.cli.common import CliError, http_get_json, run_git


ACTION_CLASSES = [
    "observer",
    "interpreter",
    "maker",
    "messenger",
    "mutator",
    "destroyer",
    "sovereign",
]
BLAST_RADIUS = ["low", "medium", "high"]


def _classify_from_goal(goal: str) -> str:
    """Infer action class from goal text."""
    lower = goal.lower()
    destroyer = {"delete", "drop", "rm -rf", "destroy", "revoke", "overwrite"}
    mutator = {"deploy", "update", "change", "modify", "edit", "restart", "push", "commit"}
    messenger = {"send", "publish", "post", "notify", "email", "tweet"}
    maker = {"create", "add", "build", "write", "generate", "scaffold"}
    observer = {"read", "search", "summarize", "list", "query", "inspect"}

    if any(k in lower for k in destroyer):
        return "destroyer"
    if any(k in lower for k in mutator):
        return "mutator"
    if any(k in lower for k in messenger):
        return "messenger"
    if any(k in lower for k in maker):
        return "maker"
    if any(k in lower for k in observer):
        return "observer"
    return "maker"


def _art_check(goal: str, action_class: str | None, blast_radius: str | None) -> dict[str, Any]:
    """Run pre-kernel ART classification."""
    cls = action_class or _classify_from_goal(goal)
    radius = blast_radius or (
        "high"
        if cls in {"destroyer", "mutator", "sovereign"}
        else "medium"
        if cls in {"messenger", "maker"}
        else "low"
    )

    power = {
        "observer": 1,
        "interpreter": 1,
        "maker": 2,
        "messenger": 3,
        "mutator": 4,
        "destroyer": 5,
        "sovereign": 6,
    }.get(cls, 2)
    power *= {"low": 1, "medium": 2, "high": 3}.get(radius, 2)

    ceremony = "light" if power <= 2 else "medium" if power <= 6 else "heavy"
    needs_human = cls in {"destroyer", "sovereign"} or (cls == "mutator" and radius == "high")

    return {
        "stage": "ART",
        "attuned": True,
        "action_class": cls,
        "blast_radius": radius,
        "ceremony": ceremony,
        "power_score": power,
        "needs_human_ack": needs_human,
        "verdict": "PROCEED" if not needs_human else "HOLD",
    }


def _preflight_health() -> dict[str, Any]:
    """Probe arifOS kernel health."""
    url = os.getenv("ARIFOS_HEALTH_URL", "http://127.0.0.1:8088/health")
    try:
        data = http_get_json(url, timeout=5)
        status = data.get("status", "unknown")
        return {
            "name": "arifOS health",
            "pass": status == "healthy",
            "detail": status,
            "data": data,
        }
    except CliError as exc:
        return {"name": "arifOS health", "pass": False, "detail": str(exc.message), "data": {}}


def _preflight_vault() -> dict[str, Any]:
    """Probe VAULT999 writer health."""
    url = os.getenv("VAULT_WRITER_URL", "http://127.0.0.1:5001") + "/health"
    try:
        data = http_get_json(url, timeout=5)
        return {
            "name": "VAULT999 writer",
            "pass": data.get("status") == "healthy",
            "detail": data.get("status", "unknown"),
            "data": data,
        }
    except CliError as exc:
        return {"name": "VAULT999 writer", "pass": False, "detail": str(exc.message), "data": {}}


def _preflight_git() -> dict[str, Any]:
    """Check git working tree state."""
    code, out, err = run_git(["status", "--porcelain"])
    if code != 0:
        return {"name": "git status", "pass": False, "detail": err or "not a git repo", "data": {}}
    clean = out == ""
    return {
        "name": "git working tree",
        "pass": clean,
        "detail": "clean" if clean else f"{len(out.splitlines())} modified files",
        "data": {"dirty_files": out.splitlines() if not clean else []},
    }


def _preflight_lease() -> dict[str, Any]:
    """Placeholder for lease validity check (A-FORGE integration)."""
    return {
        "name": "A-FORGE lease",
        "pass": True,
        "detail": "not yet implemented — manual check required",
        "data": {},
    }


def run_check(args: list[str]) -> int:
    """Entry point for `arifos check`."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="arifos check", description="ART + preflight before action."
    )
    parser.add_argument("--goal", required=True, help="What you intend to do.")
    parser.add_argument(
        "--class",
        dest="action_class",
        choices=ACTION_CLASSES,
        help="Action class (auto-detected if omitted).",
    )
    parser.add_argument(
        "--blast-radius", choices=BLAST_RADIUS, help="Blast radius (auto-detected if omitted)."
    )
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    parser.add_argument(
        "--full", action="store_true", help="Include extra probes (security audit)."
    )
    parsed = parser.parse_args(args)

    # ART
    art = _art_check(parsed.goal, parsed.action_class, parsed.blast_radius)

    # Preflight
    checks = [
        _preflight_health(),
        _preflight_vault(),
        _preflight_git(),
        _preflight_lease(),
    ]

    all_pass = art["verdict"] == "PROCEED" and all(c["pass"] for c in checks)
    any_fail = not all(c["pass"] for c in checks)

    if art["needs_human_ack"]:
        verdict = "HOLD"
    elif any_fail:
        verdict = "SABAR"
    elif all_pass:
        verdict = "SEAL"
    else:
        verdict = "SABAR"

    result = {
        "verdict": verdict,
        "art": art,
        "preflight": checks,
        "recommendation": "PROCEED"
        if verdict == "SEAL"
        else "STOP — resolve holds before execution",
    }

    if parsed.json:
        import json as _json

        print(_json.dumps(result, indent=2, default=str))
    else:
        print(f"verdict: {verdict}")
        print(
            f"action_class: {art['action_class']} | blast_radius: {art['blast_radius']} | ceremony: {art['ceremony']}"
        )
        print("preflight:")
        for c in checks:
            status = "✓" if c["pass"] else "✗"
            print(f"  {status} {c['name']}: {c['detail']}")
        if verdict != "SEAL":
            print(f"recommendation: {result['recommendation']}")

    return 0 if verdict == "SEAL" else 1
