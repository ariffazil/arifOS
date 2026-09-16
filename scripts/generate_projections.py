#!/usr/bin/env python3
"""generate_projections.py — G0.4: projections generated from canonical truth.

Every externally-published projection (ai-plugin.json ×2 paths, peer-contract
skills/manifest) is GENERATED from the kernel's canonical tool registry —
never hand-maintained. Kills the stale-projection class (2026-09-17: an
external connector ingested a stale ai-plugin advertising `mode` on
arif_route and a July peer-contract with retired tool names; live surface
was clean, the projection lied).

Sources:
  registry (default, CI-safe) — arifosmcp.runtime.tools.get_public_surface_state
        under ARIFOS_PUBLIC_SURFACE_MODE=forge_next_8 (mirrors deployed profile)
  live   — POST :8088/mcp tools/list with the modern _meta envelope

Modes:
  --write   regenerate all projection files
  --check   diff generated vs on-disk (ignoring the _regenerated stamp);
            exit 1 on drift — the CI projection-diff gate

webmcp.json is NOT regenerated: it is a deliberate browser-native read-only
surface with its own endpoints (G0.3 classification), not a kernel-tool
projection.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLUGIN_PATHS = [
    REPO / "static" / ".well-known" / "ai-plugin.json",
    REPO / "arifosmcp" / "static" / ".well-known" / "ai-plugin.json",
]
PEER_PATH = REPO / "static" / ".well-known" / "peer-contract.json"
VOLATILE_FIELDS = {"_regenerated"}

PLUGIN_TEMPLATE = {
    "schema_version": "v1",
    "name_for_human": "arifOS Constitutional Kernel",
    "name_for_model": "arifos_mcp",
    "description_for_human": (
        "Canonical 8-tool constitutional governance kernel — session init, "
        "observe, think, route, memory, judge, forge, seal."
    ),
    "description_for_model": (
        "8 canonical tools: arif_init (000 session), arif_observe (111 evidence), "
        "arif_think (333 reason), arif_route (444 dispatch), arif_memory (555 recall), "
        "arif_judge (666 constitutional verdict), arif_forge (777 execution gate), "
        "arif_seal (999 VAULT999 immutable append)."
    ),
    "auth": {"type": "none"},
    "api": {"type": "openapi", "url": "https://mcp.arif-fazil.com/openapi.json"},
    "logo_url": "https://mcp.arif-fazil.com/logo.png",
    "contact_email": "arif@arif-fazil.com",
    "legal_info_url": "https://mcp.arif-fazil.com",
    "_source": "generated from kernel canonical tool registry (G0.4)",
    "_drift_check": "scripts/generate_projections.py --check must pass in CI",
}


def canonical_tools(source: str) -> list[str]:
    if source == "live":
        req = urllib.request.Request(
            "http://127.0.0.1:8088/mcp",
            data=json.dumps({
                "jsonrpc": "2.0", "id": 1, "method": "tools/list",
                "params": {"_meta": {
                    "io.modelcontextprotocol/protocolVersion": "2026-07-28",
                    "io.modelcontextprotocol/clientCapabilities": {},
                }},
            }).encode(),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Protocol-Version": "2026-07-28",
                "Mcp-Method": "tools/list",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            tools = json.load(r)["result"]["tools"]
        return sorted(t["name"] for t in tools)
    os.environ["ARIFOS_PUBLIC_SURFACE_MODE"] = "forge_next_8"
    sys.path.insert(0, str(REPO))
    from arifosmcp.runtime.tools import get_public_surface_state

    state = get_public_surface_state()
    return sorted(state.get("tool_names") or [])


def _dump(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def build_plugin(tools: list[str]) -> dict:
    doc = dict(PLUGIN_TEMPLATE)
    doc["tools"] = tools
    doc["_regenerated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return doc


def build_peer(tools: list[str], current: dict) -> dict:
    doc = dict(current)
    card = dict(doc.get("capability_card") or {})
    card["skills"] = tools
    card["tool_manifest_url"] = "https://mcp.arif-fazil.com/mcp"
    card["tool_manifest_sha256"] = "sha256:" + hashlib.sha256(
        json.dumps(tools, separators=(",", ":")).encode()
    ).hexdigest()
    doc["capability_card"] = card
    # Honest attestation: unsigned + explicit pending status (was a literal
    # stub signature string — the 2026-09-17 external audit finding).
    doc["signed_attestation"] = {
        "issuer": "arifOS-888-JUDGE",
        "attestation_status": "pending",
        "signature": None,
        "issued_at": doc.get("signed_attestation", {}).get("issued_at"),
        "expires_at": doc.get("signed_attestation", {}).get("expires_at"),
        "note": "unsigned until G1 release attestation exists — never trust a stub signature",
    }
    doc["_generated"] = (
        "skills/manifest generated from kernel canonical tool registry (G0.4); "
        "governance fields remain hand-ratified"
    )
    return doc


def strip_volatile(doc: dict) -> dict:
    return {k: v for k, v in doc.items() if k not in VOLATILE_FIELDS and k != "_generated"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["registry", "live"], default="registry")
    ap.add_argument("--write", action="store_true",
                    help="Regenerate projection files (default behavior when no flag given)")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    tools = canonical_tools(args.source)
    if len(tools) != 8:
        print(f"FATAL: expected 8 canonical tools, got {len(tools)}: {tools}")
        return 2

    plugin = _dump(build_plugin(tools))
    peer_current = json.loads(PEER_PATH.read_text()) if PEER_PATH.exists() else {}
    peer = _dump(build_peer(tools, peer_current))

    if args.check:
        drift = []
        for p in PLUGIN_PATHS:
            on_disk = json.loads(p.read_text()) if p.exists() else {}
            if strip_volatile(on_disk) != strip_volatile(json.loads(plugin)):
                drift.append(str(p))
        if PEER_PATH.exists():
            on_disk = json.loads(PEER_PATH.read_text())
            if strip_volatile(on_disk) != strip_volatile(json.loads(peer)):
                drift.append(str(PEER_PATH))
        if drift:
            print("PROJECTION DRIFT (regenerate: scripts/generate_projections.py --write):")
            for d in drift:
                print(f"  {d}")
            return 1
        print(f"projections coherent — {len(tools)} canonical tools, all paths match")
        return 0

    for p in PLUGIN_PATHS:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(plugin)
        print(f"wrote {p}")
    PEER_PATH.write_text(peer)
    print(f"wrote {PEER_PATH}")
    print(f"tools: {tools}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
