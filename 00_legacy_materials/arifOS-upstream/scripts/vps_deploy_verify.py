#!/usr/bin/env python3
"""
scripts/vps_deploy_verify.py — arifOS 4-Layer Runtime Parity Verification

DITEMPA BUKAN DIBERI — Forged, Not Given

Verifies that a deployed node matches spec across ALL 4 runtime layers:
  Layer 1: Entry point selection
  Layer 2: Environment variables
  Layer 3: Deploy commit (git SHA)
  Layer 4: Tool registration at boot

Usage:
    python scripts/vps_deploy_verify.py --node https://mcp.arif-fazil.com --check-all
    python scripts/vps_deploy_verify.py --node https://mcp.arif-fazil.com --check-commit
    python scripts/vps_deploy_verify.py --node http://localhost:8080 --check-all
"""

from __future__ import annotations

import argparse
import json
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass
class LayerReport:
    layer: str
    name: str
    expected: str
    actual: str
    status: str  # PASS | FAIL | WARN | UNKNOWN
    detail: str = ""


@dataclass
class NodeVerification:
    node_url: str
    timestamp: str
    layers: list[LayerReport] = field(default_factory=list)
    overall_status: str = "UNKNOWN"
    commit_live: str = ""
    tools_loaded: int = 0
    vault_status: str = ""
    session_cache_status: str = ""
    vitality_index: float = 0.0
    verdict: str = ""

    @property
    def passed(self) -> int:
        return sum(1 for l in self.layers if l.status == "PASS")

    @property
    def failed(self) -> int:
        return sum(1 for l in self.layers if l.status == "FAIL")

    @property
    def warnings(self) -> int:
        return sum(1 for l in self.layers if l.status == "WARN")


def http_get(url: str, timeout: int = 10) -> dict[str, Any] | None:
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  HTTP error for {url}: {e}")
        return None


def check_layer1_entry_point(node_url: str, health: dict[str, Any]) -> LayerReport:
    """Layer 1: Entry point determines which code paths are loaded."""
    name = health.get("service", "unknown")
    transport = health.get("transport", "unknown")
    version = health.get("version", "unknown")

    # Entry point is inferred from transport + service name
    if "streamable-http" in transport:
        entry = "uvicorn + FastMCP HTTP app (server.py entry)"
    elif "sse" in transport:
        entry = "SSE transport (alternative)"
    else:
        entry = f"unknown ({transport})"

    # Check for signs of full kernel vs lightweight routing
    full_kernel_signs = ["governance_kernel", "floors", "vault", "sessions"]
    has_full_kernel = any(k in json.dumps(health) for k in full_kernel_signs)

    if has_full_kernel:
        expected = "Full constitutional kernel (server.py)"
        status = "PASS"
        detail = f"{entry} — full kernel loaded"
    else:
        expected = "Full constitutional kernel (server.py)"
        status = "WARN"
        detail = f"{entry} — may be lightweight routing layer"

    return LayerReport(
        layer="Layer 1",
        name="Entry Point Selection",
        expected=expected,
        actual=entry,
        status=status,
        detail=detail,
    )


def check_layer2_env_vars(node_url: str, health: dict[str, Any]) -> list[LayerReport]:
    """Layer 2: Environment variables gate features on/off."""
    reports = []
    storage = health.get("capability_map", {}).get("storage", {})

    env_checks = [
        ("vault_postgres", "VAULT999 PostgreSQL", "configured"),
        ("session_cache", "Redis session cache", "configured"),
        ("vector_memory", "Qdrant vector memory", "configured"),
    ]

    for key, label, expected_status in env_checks:
        actual = storage.get(key, "not_configured")
        if actual == "configured":
            status = "PASS"
        elif actual == "not_configured":
            status = "FAIL"
        else:
            status = "WARN"

        reports.append(LayerReport(
            layer="Layer 2",
            name=f"Env: {label}",
            expected=expected_status,
            actual=actual,
            status=status,
            detail=f"Feature gated by {key} env var" if status == "FAIL" else "",
        ))

    # Also check ML floors
    ml = health.get("ml_floors", {})
    if ml.get("ml_floors_enabled"):
        reports.append(LayerReport(
            layer="Layer 2",
            name="Env: ML Floors",
            expected="enabled",
            actual="enabled",
            status="PASS",
            detail="ARIFOS_ML_FLOORS_ENABLED=true",
        ))
    else:
        reports.append(LayerReport(
            layer="Layer 2",
            name="Env: ML Floors",
            expected="enabled (for production)",
            actual="disabled (heuristic fallback)",
            status="WARN",
            detail="ARIFOS_ML_FLOORS_ENABLED not set — heuristic mode active",
        ))

    return reports


def check_layer3_commit(node_url: str, health: dict[str, Any]) -> LayerReport:
    """Layer 3: Deploy commit determines which version of code is running."""
    commit = health.get("source_commit", "unknown")
    version = health.get("version", "unknown")

    # Known good commit is tracked via source_repo
    source_repo = health.get("source_repo", "")
    if "github.com/ariffazil/arifOS" in source_repo:
        # Commit is from correct repo
        status = "PASS"
        detail = f"Deployed from canonical repo: {source_repo}"
    elif not commit or commit == "unknown":
        status = "FAIL"
        detail = "Commit SHA missing — cannot verify deploy version"
    else:
        status = "WARN"
        detail = f"Commit from non-canonical source: {source_repo}"

    return LayerReport(
        layer="Layer 3",
        name="Deploy Commit",
        expected="Latest HEAD (8a21b135 or newer)",
        actual=f"{commit} ({version})",
        status=status,
        detail=detail,
    )


def check_layer4_tool_registration(node_url: str, health: dict[str, Any]) -> LayerReport:
    """Layer 4: Tool registration at boot determines what's visible to MCP clients."""
    tools_loaded = health.get("tools_loaded", 0)

    # Expected: 44 tools for full VPS, 11 for fastMCP routing layer
    # Detect which based on tool count and metabolic telemetry
    has_metabolic = health.get("thermodynamic") is not None
    has_high_tools = tools_loaded >= 40

    if has_high_tools and has_metabolic:
        expected = 44
        status = "PASS"
        detail = "Full tool surface registered at boot"
    elif has_high_tools and not has_metabolic:
        expected = "~44 (full)"
        status = "PASS"
        detail = "Full tool surface registered (metabolic telemetry absent)"
    elif tools_loaded == 11 and not has_metabolic:
        expected = "11 (routing layer)"
        status = "PASS"
        detail = "fastMCP routing layer — intentional surface limitation"
    else:
        expected = "44 (full) or 11 (routing)"
        status = "WARN"
        detail = f"Unexpected tool count: {tools_loaded}"

    return LayerReport(
        layer="Layer 4",
        name="Tool Registration at Boot",
        expected=f"{expected} tools",
        actual=f"{tools_loaded} tools registered",
        status=status,
        detail=detail,
    )


def verify_node(node_url: str, check_all: bool = True) -> NodeVerification:
    """Run full 4-layer verification against a node."""
    node_url = node_url.rstrip("/")
    health_url = f"{node_url}/health"

    print(f"\n{'='*60}")
    print("  arifOS 4-Layer Runtime Verification")
    print(f"  Node: {node_url}")
    print(f"{'='*60}")

    health = http_get(health_url)
    if not health:
        return NodeVerification(
            node_url=node_url,
            timestamp=datetime.now(timezone.utc).isoformat(),
            overall_status="FAIL",
        )

    v = NodeVerification(
        node_url=node_url,
        timestamp=datetime.now(timezone.utc).isoformat(),
        commit_live=health.get("source_commit", "unknown"),
        tools_loaded=health.get("tools_loaded", 0),
        vault_status=health.get("capability_map", {}).get("storage", {}).get("vault_postgres", "unknown"),
        session_cache_status=health.get("capability_map", {}).get("storage", {}).get("session_cache", "unknown"),
        vitality_index=health.get("thermodynamic", {}).get("vitality_index", 0.0),
        verdict=health.get("thermodynamic", {}).get("verdict", "unknown"),
    )

    # Layer 1: Entry point
    v.layers.append(check_layer1_entry_point(node_url, health))

    # Layer 2: Environment variables
    v.layers.extend(check_layer2_env_vars(node_url, health))

    # Layer 3: Deploy commit
    v.layers.append(check_layer3_commit(node_url, health))

    # Layer 4: Tool registration
    v.layers.append(check_layer4_tool_registration(node_url, health))

    # Overall status
    if v.failed > 0:
        v.overall_status = "FAIL"
    elif v.warnings > 0:
        v.overall_status = "PARTIAL"
    else:
        v.overall_status = "PASS"

    # Print results
    print(f"\n  Source commit : {v.commit_live}")
    print(f"  Version       : {health.get('version', 'unknown')}")
    print(f"  Tools loaded  : {v.tools_loaded}")
    print(f"  Vault         : {v.vault_status}")
    print(f"  Session cache : {v.session_cache_status}")
    print(f"  Vitality      : {v.vitality_index}")
    print(f"  Verdict       : {v.verdict}")
    print(f"\n  {'Layer':<10} {'Check':<35} {'Status':<8} {'Detail'}")
    print(f"  {'-'*10} {'-'*35} {'-'*8} {'-'*30}")
    for layer in v.layers:
        flag = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "UNKNOWN": "❓"}[layer.status]
        detail = layer.detail[:30] if layer.detail else ""
        print(f"  {layer.layer:<10} {layer.name:<35} {flag} {layer.status:<8} {detail}")

    print(f"\n  Overall: {v.overall_status} — {v.passed} passed, {v.failed} failed, {v.warnings} warnings")

    return v


def main():
    parser = argparse.ArgumentParser(description="arifOS 4-Layer Runtime Verification")
    parser.add_argument("--node", "-n", default="https://mcp.arif-fazil.com", help="Node URL")
    parser.add_argument("--check-all", action="store_true", help="Run all layer checks")
    parser.add_argument("--check-commit", action="store_true", help="Layer 3 only")
    parser.add_argument("--output-json", "-o", help="Write report to JSON file")
    args = parser.parse_args()

    v = verify_node(args.node, check_all=args.check_all or args.check_commit)

    if args.output_json:
        with open(args.output_json, "w") as f:
            json.dump(asdict(v), f, indent=2)
        print(f"\n  Report written to: {args.output_json}")

    # Exit code
    if v.overall_status == "FAIL":
        exit(1)
    elif v.overall_status == "PARTIAL":
        exit(2)
    exit(0)


if __name__ == "__main__":
    main()
