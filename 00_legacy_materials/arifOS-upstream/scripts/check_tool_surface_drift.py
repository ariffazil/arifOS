#!/usr/bin/env python3
"""
Drift checker for arifOS tool surfaces.

Mission:
- treat arifosmcp/runtime/tool_specs.py as canonical truth
- detect drift across runtime, transport, compatibility, and wiki surfaces
- exit non-zero when surface drift is found
"""

from __future__ import annotations

import importlib.util
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOOL_SPECS_PATH = ROOT / "arifosmcp" / "runtime" / "tool_specs.py"

TOKEN_PATTERN = re.compile(r"\barifos(?:_[a-z][a-z0-9_]*|\.[a-z][a-z0-9_]*)\b")
COUNT_PATTERN = re.compile(r"\bEXPECTED_TOOL_COUNT\s*=\s*(\d+)")


@dataclass(frozen=True)
class SurfaceCheck:
    label: str
    path: Path
    mode: str  # full | count_hint | permissive


FULL_SURFACES: tuple[SurfaceCheck, ...] = (
    SurfaceCheck("runtime.handlers", ROOT / "arifosmcp" / "runtime" / "tools.py", "full"),
    SurfaceCheck("runtime.stdio", ROOT / "arifosmcp" / "runtime" / "__main__.py", "full"),
    SurfaceCheck("runtime.hardened_dispatch", ROOT / "arifosmcp" / "runtime" / "tools_hardened_dispatch.py", "full"),
    SurfaceCheck("transport.resources", ROOT / "arifosmcp" / "runtime" / "resources.py", "full"),
    SurfaceCheck("transport.registry_json", ROOT / "arifosmcp" / "tool_registry.json", "full"),
    SurfaceCheck("wiki.mcp_inventory", ROOT / "wiki" / "pages" / "MCP_Tools.md", "full"),
    SurfaceCheck("wiki.surface_architecture", ROOT / "wiki" / "pages" / "Tool_Surface_Architecture.md", "full"),
)

COUNT_HINT_SURFACES: tuple[SurfaceCheck, ...] = (
    SurfaceCheck("transport.public_registry", ROOT / "arifosmcp" / "runtime" / "public_registry.py", "count_hint"),
)

AUDITED_CODE_SURFACES: tuple[Path, ...] = (
    TOOL_SPECS_PATH,
    ROOT / "arifosmcp" / "runtime" / "tools.py",
    ROOT / "arifosmcp" / "runtime" / "__main__.py",
    ROOT / "arifosmcp" / "runtime" / "tools_hardened_dispatch.py",
    ROOT / "arifosmcp" / "runtime" / "kernel_router.py",
    ROOT / "arifosmcp" / "runtime" / "server.py",
    ROOT / "arifosmcp" / "runtime" / "rest_routes.py",
    ROOT / "arifosmcp" / "runtime" / "resources.py",
    ROOT / "arifosmcp" / "runtime" / "public_registry.py",
    ROOT / "arifosmcp" / "runtime" / "megaTools" / "__init__.py",
    ROOT / "arifosmcp" / "runtime" / "compatibility" / "memory_backend.py",
    ROOT / "arifosmcp" / "runtime" / "compatibility" / "vault_backend.py",
    ROOT / "arifosmcp" / "tool_registry.json",
)

APPROVED_DOTTED_COMPATIBILITY_FILES: tuple[Path, ...] = (
    TOOL_SPECS_PATH,
    ROOT / "arifosmcp" / "runtime" / "tools_hardened_dispatch.py",
    ROOT / "arifosmcp" / "runtime" / "megaTools" / "__init__.py",
    ROOT / "arifosmcp" / "runtime" / "compatibility" / "memory_backend.py",
    ROOT / "arifosmcp" / "runtime" / "compatibility" / "vault_backend.py",
)


def _load_tool_specs_module() -> Any:
    spec = importlib.util.spec_from_file_location("arifos_tool_specs", TOOL_SPECS_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load canonical module from {TOOL_SPECS_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _extract_tokens_from_text(text: str) -> set[str]:
    return set(TOKEN_PATTERN.findall(text))


def _extract_tokens(path: Path) -> set[str]:
    if path.suffix.lower() == ".json":
        data = json.loads(_read_text(path))
        strings: list[str] = []

        def walk(value: Any) -> None:
            if isinstance(value, dict):
                for inner in value.values():
                    walk(inner)
            elif isinstance(value, list):
                for inner in value:
                    walk(inner)
            elif isinstance(value, str):
                strings.append(value)

        walk(data)
        return _extract_tokens_from_text("\n".join(strings))

    return _extract_tokens_from_text(_read_text(path))


def _extract_expected_count(path: Path) -> int | None:
    match = COUNT_PATTERN.search(_read_text(path))
    return int(match.group(1)) if match else None


def _format_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\", "/")
    except ValueError:
        return str(path).replace("\", "/")


def main() -> int:
    module = _load_tool_specs_module()
    canonical_ids = tuple(module.tool_names())
    canonical_set = set(canonical_ids)
    canonical_count = len(canonical_ids)
    legacy_aliases = dict(module.LEGACY_NAME_MAP)
    dotted_aliases = tuple(name.replace("arifos_", "arifos.") for name in canonical_ids)
    dotted_alias_set = set(dotted_aliases)

    print("== Canonical Tool Contract ==")
    print(f"source: {_format_path(TOOL_SPECS_PATH)}")
    print(f"count: {canonical_count}")
    print("ids:")
    for tool_id in canonical_ids:
        print(f"  - {tool_id}")

    drift_found = False

    print("\n== Full Surface Checks ==")
    for surface in FULL_SURFACES:
        tokens = _extract_tokens(surface.path)
        canonical_tokens = {token for token in tokens if token in canonical_set}
        missing = sorted(canonical_set - canonical_tokens)
        extra_dotted = sorted(token for token in tokens if token in dotted_alias_set)
        print(f"* {surface.label}: {_format_path(surface.path)}")
        print(f"  canonical_seen={len(canonical_tokens)}/{canonical_count}")
        if missing:
            drift_found = True
            print(f"  missing={missing}")
        if extra_dotted:
            print(f"  dotted_refs={extra_dotted}")
        if not missing and not extra_dotted:
            print("  status=ok")

    print("\n== Count Hint Checks ==")
    for surface in COUNT_HINT_SURFACES:
        expected_count = _extract_expected_count(surface.path)
        print(f"* {surface.label}: {_format_path(surface.path)}")
        if expected_count is None:
            print("  expected_count=absent")
            continue
        print(f"  expected_count={expected_count} canonical_count={canonical_count}")
        if expected_count != canonical_count:
            drift_found = True
            print("  status=drift")
        else:
            print("  status=ok")

    print("\n== Dotted Name Leakage ==")
    approved = {_format_path(path) for path in APPROVED_DOTTED_COMPATIBILITY_FILES}
    print("approved compatibility files:")
    for path in sorted(approved):
        print(f"  - {path}")
    for path in AUDITED_CODE_SURFACES:
        dotted = sorted(token for token in _extract_tokens(path) if token in dotted_alias_set)
        if not dotted:
            continue
        rel = _format_path(path)
        status = "approved" if path in APPROVED_DOTTED_COMPATIBILITY_FILES else "DRIFT"
        print(f"* {rel}: {status} -> {dotted}")
        if status == "DRIFT":
            drift_found = True

    print("\n== Deprecated Alias Registry ==")
    print("legacy aliases:")
    for alias, target in sorted(legacy_aliases.items()):
        print(f"  - {alias} -> {target}")
    print("generated dotted compatibility aliases:")
    for alias in dotted_aliases:
        print(f"  - {alias}")

    print("\n== Alias Usage ==")
    for path in AUDITED_CODE_SURFACES:
        text = _read_text(path)
        hits = sorted(alias for alias in legacy_aliases if re.search(rf"\b{re.escape(alias)}\b", text))
        if hits:
            print(f"* {_format_path(path)} -> {hits}")

    print("\n== Verdict ==")
    if drift_found:
        print("DRIFT DETECTED")
        return 1
    print("NO DRIFT DETECTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
