#!/usr/bin/env python3
"""
contract_closure.py — arifOS Contract Epoch Closure (APEX-777 ZEN CLOSURE)
═══════════════════════════════════════════════════════════════════════════

One instrument. Three subcommands:

  measure   Read-only contract epoch report across all surfaces.
  receipt   Emit ONE machine-readable golden receipt (post-restart proof).
  verify    Drift monitor: exit non-zero when the contract is violated.

Canonical OWNER of the public ABI (single source of truth):
    arifosmcp.constitutional_map.CANONICAL_TOOLS  (entries with expose=True)

Every downstream surface must DERIVE its public tool set + mode list from
that owner. This instrument does NOT write anything (F1 reversible) — it
measures and, in `verify` mode, fails loudly on drift (F4: expose the
discrepancy rather than normalizing it away).

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ═══════════════════════════════════════════════════════════════════════════════
# Canonical owner
# ═══════════════════════════════════════════════════════════════════════════════


def canonical_tools() -> dict[str, dict[str, Any]]:
    """Public ABI from the canonical owner (constitutional_map, expose=True)."""
    from arifosmcp.constitutional_map import CANONICAL_TOOLS

    out: dict[str, dict[str, Any]] = {}
    for name, spec in CANONICAL_TOOLS.items():
        if not spec.get("expose", False):
            continue
        out[name] = {
            "modes": list(spec.get("modes", [])),
            "deprecated_aliases": list(spec.get("deprecated_aliases", [])),
            "stage": spec.get("stage", "unknown"),
            "access": spec.get("access", "unknown"),
        }
    return out


def canonical_manifest_hash() -> str:
    canon = canonical_tools()
    raw = json.dumps(
        {name: canon[name]["modes"] for name in sorted(canon)},
        sort_keys=True,
    ).encode()
    return hashlib.sha256(raw).hexdigest()


# ═══════════════════════════════════════════════════════════════════════════════
# Surface loaders — each returns {tool_name: list[str] | None}
#   modes list = public mode enum; None = surface has no mode declaration for it.
# ═══════════════════════════════════════════════════════════════════════════════


def surface_charter() -> dict[str, list[str]]:
    """Authority charter (tool_charter.TOOL_CHARTER) — mode keys per tool."""
    try:
        from arifosmcp.tool_charter import TOOL_CHARTER
    except Exception:
        return {}
    out: dict[str, list[str]] = {}
    for name, spec in TOOL_CHARTER.items():
        modes = spec.get("modes", {})
        if isinstance(modes, dict):
            out[name] = list(modes.keys())
        elif isinstance(modes, (list, tuple)):
            out[name] = list(modes)
        else:
            out[name] = []
    return out


def surface_discovery() -> dict[str, list[str]]:
    """LLM discovery registry (tool_discovery) — advertised modes per tool."""
    try:
        from arifosmcp.tool_discovery import ARIF_TOOL_DISCOVERY
    except Exception:
        return {}
    out: dict[str, list[str]] = {}
    for name, td in ARIF_TOOL_DISCOVERY.items():
        out[name] = list(td.modes) if td.modes else []
    return out


def _parse_tools_sot(path: str) -> dict[str, list[str]]:
    """Parse tools_sot.yaml (regular list-of-blocks) without hard yaml dep."""
    try:
        import yaml  # type: ignore
    except Exception:
        yaml = None
    if yaml is not None:
        try:
            with open(path) as f:
                doc = yaml.safe_load(f)
            return {t["id"]: list(t.get("modes", [])) for t in doc.get("tools", [])}
        except Exception:
            pass
    # Fallback: regex over the block structure.
    text = open(path).read()
    out: dict[str, list[str]] = {}
    for block in re.split(r"\n  - id: ", text)[1:]:
        m_id = re.match(r"(\w+)", block)
        if not m_id:
            continue
        name = m_id.group(1)
        mm = re.search(r"\n    modes:\n((?:      - \w+\n)+)", block)
        modes: list[str] = []
        if mm:
            modes = re.findall(r"- (\w+)", mm.group(1))
        out[name] = modes
    return out


def surface_tools_sot() -> dict[str, list[str]]:
    path = os.path.join(ROOT, "tools_sot.yaml")
    if os.path.exists(path):
        return _parse_tools_sot(path)
    return {}


def surface_runtime() -> dict[str, list[str]]:
    """Live MCP tools/list — the wire truth. {} when unreachable (honest UNKNOWN)."""
    url = os.environ.get("CONTRACT_CLOSURE_MCP_URL", "http://localhost:8088/mcp")
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
        method="POST",
    )
    raw = None
    for attempt in (0, 1):
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                raw = resp.read()
            break
        except Exception:
            if attempt == 0:
                import time

                time.sleep(0.5)
                continue
            return {}
    if raw is None:
        return {}
    # Accept JSON-RPC or SSE framing.
    text = raw.decode("utf-8", "replace")
    try:
        data = json.loads(text)
    except Exception:
        m = re.search(r"data: (\{.*\})\n", text)
        if not m:
            return {}
        data = json.loads(m.group(1))
    tools = data.get("result", {}).get("tools", [])
    out: dict[str, list[str]] = {}
    for t in tools:
        name = t.get("name")
        schema_mode = t.get("inputSchema", {}).get("properties", {}).get("mode", {})
        enum = schema_mode.get("enum")
        if isinstance(enum, list):
            out[name] = list(enum)
        else:
            # No public mode enum on this tool (e.g. arif_route).
            out[name] = []
    return out


# ═══════════════════════════════════════════════════════════════════════════════
# Measurement
# ═══════════════════════════════════════════════════════════════════════════════


def _advertised_discovery() -> dict[str, list[str]]:
    """Discovery surface restricted to advertised (expose=True) tools."""
    full = surface_discovery()
    canon_names = set(canonical_tools())
    # After closure, ARIF_TOOL_DISCOVERY carries an `expose` flag; honor it if
    # present, else fall back to "tools that are canonical public names".
    try:
        from arifosmcp.tool_discovery import ARIF_TOOL_DISCOVERY

        exposed = {
            name: list(td.modes or [])
            for name, td in ARIF_TOOL_DISCOVERY.items()
            if getattr(td, "expose", True)
        }
        if any(getattr(td, "expose", True) is False for td in ARIF_TOOL_DISCOVERY.values()):
            return exposed
    except Exception:
        pass
    return {n: m for n, m in full.items() if n in canon_names}


def measure(local: bool = False) -> dict[str, Any]:
    canon = canonical_tools()
    canon_names = set(canon)

    # Public-advertised surfaces (must be exactly the canonical 8).
    public_surfaces: dict[str, dict[str, list[str]]] = {
        "tools_sot": surface_tools_sot(),
        "discovery": _advertised_discovery(),
    }
    if not local:
        public_surfaces["runtime"] = surface_runtime()
    # Authority charter is a full registry (internal tools expected) — only the
    # 8 public tools' mode COVERAGE is compared (charter must be a superset of
    # canonical public modes; extra internal modes are not drift).
    charter = surface_charter()

    phantom: list[dict[str, str]] = []
    missing: list[dict[str, str]] = []
    schema_mismatch: list[dict[str, Any]] = []

    mode_count_by_tool = {n: len(canon[n]["modes"]) for n in sorted(canon)}
    alias_count = sum(len(canon[n]["deprecated_aliases"]) for n in canon)

    for surf_name, surf in public_surfaces.items():
        surf_tools = set(surf)
        for t in sorted(surf_tools - canon_names):
            phantom.append({"surface": surf_name, "tool": t})
        for t in sorted(canon_names - surf_tools):
            missing.append({"surface": surf_name, "tool": t})
        for t in sorted(canon_names & surf_tools):
            want = set(canon[t]["modes"])
            got = set(surf[t])
            if want != got:
                schema_mismatch.append(
                    {
                        "surface": surf_name,
                        "tool": t,
                        "canonical": sorted(want),
                        "got": sorted(got),
                        "missing_modes": sorted(want - got),
                        "extra_modes": sorted(got - want),
                    }
                )

    # Charter: flag only canonical public modes missing from authority coverage.
    for t in sorted(canon_names):
        want = set(canon[t]["modes"])
        got = set(charter.get(t, []))
        absent = want - got
        if absent:
            schema_mismatch.append(
                {
                    "surface": "charter",
                    "tool": t,
                    "canonical": sorted(want),
                    "got": sorted(got),
                    "missing_modes": sorted(absent),
                    "extra_modes": sorted(got - want),
                }
            )

    canonical_hash = canonical_manifest_hash()
    if local:
        runtime_hash = "local-skip"
    else:
        runtime_hash = hashlib.sha256(
            json.dumps(
                {n: public_surfaces["runtime"].get(n, []) for n in sorted(canon_names)},
                sort_keys=True,
            ).encode()
        ).hexdigest()

    return {
        "contract_epoch": contract_epoch(),
        "canonical_manifest_hash": canonical_hash,
        "runtime_surface_hash": runtime_hash,
        "tool_count": len(canon_names),
        "mode_count_by_tool": mode_count_by_tool,
        "alias_count": alias_count,
        "phantom_count": len(phantom),
        "missing_count": len(missing),
        "schema_mismatch_count": len(schema_mismatch),
        "phantom": phantom,
        "missing": missing,
        "schema_mismatch": schema_mismatch,
        "public_surfaces": {k: sorted(v) for k, v in public_surfaces.items()},
        "charter_surface": sorted(charter),
    }


def contract_epoch() -> str:
    """Contract epoch = git HEAD short sha + commit timestamp."""
    import subprocess

    try:
        sha = (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True
            )
            .strip()
        )
        ts = (
            subprocess.check_output(
                ["git", "show", "-s", "--format=%cI", "HEAD"], cwd=ROOT, text=True
            )
            .strip()
        )
        return f"{sha}@{ts}"
    except Exception:
        return "UNKNOWN"


# ═══════════════════════════════════════════════════════════════════════════════
# Authority falsification pair (OBSERVE_ONLY, no mutation)
# ═══════════════════════════════════════════════════════════════════════════════


def authority_probe() -> dict[str, Any]:
    """
    Prove the authority falsification pair under OBSERVE_ONLY (no mutation):
        arif_forge(mode=query)     → OBSERVE (allowed as observation)
        arif_forge(mode=engineer)  → HOLD/CLAMP (mutation)
    Also test canonical-name vs SDK-alias forms → identical policy outcome.
    Uses the canonical authority engine (risk_classifier.classify_tool); the
    arif_forge tool is never invoked.
    """
    try:
        from arifosmcp.core.enforcement.risk_classifier import classify_tool
    except Exception as e:  # pragma: no cover - honest UNKNOWN
        return {"available": False, "reason": f"risk_classifier import failed: {e}"}

    def _ac(p: Any) -> str:
        return p.action_class.name if hasattr(p.action_class, "name") else str(p.action_class)

    def _policy(ac_name: str) -> str:
        return "OBSERVE_ALLOWED" if ac_name in ("OBSERVE", "PREPARE") else "HOLD"

    cases = {
        "forge_query": ("arif_forge", "query"),
        "forge_engineer": ("arif_forge", "engineer"),
        "forge_query_sdk_alias": ("arifos_arif_forge", "query"),
        "forge_engineer_sdk_alias": ("arifos_arif_forge", "engineer"),
    }
    outcomes: dict[str, dict[str, str]] = {}
    for key, (name, mode) in cases.items():
        p = classify_tool(name, mode=mode)
        a = _ac(p)
        outcomes[key] = {"tool": name, "mode": mode, "action_class": a, "policy": _policy(a)}

    alias_identical = (
        outcomes["forge_query"]["action_class"]
        == outcomes["forge_query_sdk_alias"]["action_class"]
        and outcomes["forge_engineer"]["action_class"]
        == outcomes["forge_engineer_sdk_alias"]["action_class"]
    )
    pair_ok = (
        outcomes["forge_query"]["policy"] == "OBSERVE_ALLOWED"
        and outcomes["forge_engineer"]["policy"] == "HOLD"
    )
    return {
        "available": True,
        "outcomes": outcomes,
        "alias_policy_identical": alias_identical,
        "falsification_pair_ok": pair_ok,
        "note": "OBSERVE_ONLY — classification inspected, arif_forge never invoked",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Golden receipt (Phase 2) + drift verify (Phase 3)
# ═══════════════════════════════════════════════════════════════════════════════


def build_receipt(local: bool = False) -> dict[str, Any]:
    m = measure(local=local)
    test_hash = hashlib.sha256(
        json.dumps(
            {
                "canonical": m["canonical_manifest_hash"],
                "runtime": m["runtime_surface_hash"],
                "epoch": m["contract_epoch"],
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()[:16]
    hash_ok = local or m["runtime_surface_hash"] == m["canonical_manifest_hash"]
    verdict = (
        "PASS"
        if m["phantom_count"] == 0
        and m["missing_count"] == 0
        and m["schema_mismatch_count"] == 0
        and hash_ok
        else "HOLD"
    )
    return {
        "contract_epoch": m["contract_epoch"],
        "commit_sha": m["contract_epoch"].split("@")[0],
        "runtime_hash": m["runtime_surface_hash"],
        "canonical_manifest_hash": m["canonical_manifest_hash"],
        "timestamp": m["contract_epoch"].split("@")[-1],
        "test_hash": test_hash,
        "verdict": verdict,
        "metrics": {
            "tool_count": m["tool_count"],
            "phantom_count": m["phantom_count"],
            "missing_count": m["missing_count"],
            "schema_mismatch_count": m["schema_mismatch_count"],
            "alias_count": m["alias_count"],
        },
        "authority_probe": authority_probe(),
    }


def verify(local: bool = False) -> int:
    """Drift monitor. Exit 0 = green; exit 1 = red (drift detected)."""
    m = measure(local=local)
    canon = canonical_tools()

    failures: list[str] = []
    if m["phantom_count"]:
        failures.append(f"PHANTOM tools appear: {m['phantom']}")
    if m["missing_count"]:
        failures.append(f"public modes/tools disappeared: {m['missing']}")
    if m["schema_mismatch_count"]:
        failures.append(f"mode schema mismatch: {m['schema_mismatch']}")
    if not local and m["runtime_surface_hash"] != m["canonical_manifest_hash"]:
        failures.append(
            "runtime/connector hash divergence: "
            f"{m['runtime_surface_hash']} != {m['canonical_manifest_hash']}"
        )
    if m["tool_count"] != 8:
        failures.append(f"canonical count changed without epoch change: {m['tool_count']} != 8")

    ap = authority_probe()
    if not ap.get("available"):
        failures.append(f"authority probe unavailable: {ap.get('reason')}")
    elif not (ap.get("falsification_pair_ok") and ap.get("alias_policy_identical")):
        failures.append(
            "alias bypasses policy / falsification pair failed: "
            f"{json.dumps(ap.get('outcomes'), sort_keys=True)}"
        )

    out = {"epoch": m["contract_epoch"], "drift": bool(failures), "failures": failures}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 1 if failures else 0


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════


def main() -> int:
    ap = argparse.ArgumentParser(description="arifOS contract closure instrument")
    ap.add_argument(
        "command",
        choices=["measure", "receipt", "verify"],
        default="measure",
        nargs="?",
    )
    ap.add_argument("--json", action="store_true", help="compact JSON output")
    ap.add_argument(
        "--local",
        action="store_true",
        help="repo-side surfaces only (skip live runtime; for CI)",
    )
    args = ap.parse_args()

    if args.command == "measure":
        print(json.dumps(measure(local=args.local), indent=2, sort_keys=True))
        return 0
    if args.command == "receipt":
        print(json.dumps(build_receipt(local=args.local), indent=2, sort_keys=True))
        return 0
    return verify(local=args.local)


if __name__ == "__main__":
    sys.exit(main())
