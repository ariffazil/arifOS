"""Package-surface consistency checks (ARIFOS::PACKAGE-SURFACE-ALIGNMENT::2026-11-22).

Deterministic, offline checks verifying that:
1. PyPI (`arifos`), npm (`@arifos/mcp`), and hosted MCP (`https://mcp.arif-fazil.com/mcp`)
   roles are consistent across README.md, docs/START_HERE.md, and @arifos/mcp.
2. No stale dead endpoints (`arifosmcp.arif-fazil.com`) or retired PyPI links
   (`pypi.org/project/arifosmcp`) remain in active package surfaces.
3. `@arifos/mcp` mirrors the 9 live wire tools (8 canonical verbs + arif_report),
   carries AGPL-3.0-only license, has no postinstall script, and no server framework dep.
4. `npm-wrapper/package.json` is marked private so only one npm identity exists.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NPM_PKG_DIR = ROOT / "arifosmcp" / "packages" / "npm" / "arifos-mcp"
WRAPPER_PKG = ROOT / "npm-wrapper" / "package.json"

EXPECTED_WIRE_TOOLS = [
    "arif_init",
    "arif_observe",
    "arif_think",
    "arif_route",
    "arif_memory",
    "arif_judge",
    "arif_forge",
    "arif_seal",
    "arif_report",
]


def test_npm_package_metadata_and_security_hygiene() -> None:
    pkg = json.loads((NPM_PKG_DIR / "package.json").read_text(encoding="utf-8"))
    assert pkg["name"] == "@arifos/mcp"
    assert pkg["license"] == "AGPL-3.0-only"
    assert "ariffazil/arifOS" in pkg["repository"]["url"]
    assert "postinstall" not in pkg.get("scripts", {})
    assert "express" not in pkg.get("dependencies", {})


def test_npm_wrapper_is_private_superseded() -> None:
    wrapper = json.loads(WRAPPER_PKG.read_text(encoding="utf-8"))
    assert wrapper.get("private") is True


def test_npm_client_mirrors_nine_live_wire_tools_and_canonical_endpoint() -> None:
    types_ts = (NPM_PKG_DIR / "src" / "types.ts").read_text(encoding="utf-8")
    index_ts = (NPM_PKG_DIR / "src" / "index.ts").read_text(encoding="utf-8")
    client_ts = (NPM_PKG_DIR / "src" / "client.ts").read_text(encoding="utf-8")

    for tool in EXPECTED_WIRE_TOOLS:
        assert f'"{tool}"' in types_ts, f"Missing live wire tool {tool} in src/types.ts"

    assert "https://mcp.arif-fazil.com/mcp" in index_ts
    assert "https://mcp.arif-fazil.com/mcp" in client_ts
    assert "arifosmcp.arif-fazil.com" not in index_ts
    assert "arifosmcp.arif-fazil.com" not in client_ts


def test_public_docs_align_package_hierarchy_and_avoid_stale_endpoints() -> None:
    for rel in (
        "README.md",
        "docs/START_HERE.md",
        "arifosmcp/packages/npm/arifos-mcp/README.md",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "pip install arifos" in text, f"{rel} missing pip install arifos"
        assert "npm install @arifos/mcp" in text, f"{rel} missing npm install @arifos/mcp"
        assert "https://mcp.arif-fazil.com/mcp" in text, f"{rel} missing canonical MCP URL"
        assert "arifosmcp.arif-fazil.com" not in text, f"{rel} still references dead endpoint"
        assert "pypi.org/project/arifosmcp" not in text, f"{rel} still references retired PyPI URL"
