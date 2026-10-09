#!/usr/bin/env python3
"""capability_truth_gate.py — hard CI gate (APEX-777 phase 3 · STEP 5) · 333-AGI 2026-09-18

Registry-level (no live kernel required — CI-safe). Enforces:

  phantom_tools   == 0   every advertised public name has a dispatch handler
  missing_tools   == 0   every KERNEL_ABI_8 name has a dispatch handler
  schema_mismatch == 0   advertised mode enum ⊆ handler-declared universe
                         (__dispatch_modes__ — declared by handlers; see
                          _arif_memory_v5_router for the reference pattern)
  alias_conflicts == 0   every ghost alias is hidden from discovery AND its
                         target resolves in CANONICAL_TOOL_HANDLERS

Exit 0 = PASS · 1 = FAIL · 2 = infrastructure error (import failure).
Scar: capability_contract_runtime_divergence.
DITEMPA BUKU DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _ghosts_from_server(server_src: str) -> dict[str, str]:
    """AST-parse _GHOST_ALIASES from server.py — no import side effects."""
    tree = ast.parse(server_src)
    for node in ast.walk(tree):
        target_names: list[str] = []
        value = None
        if isinstance(node, ast.AnnAssign):
            target_names = [getattr(node.target, "id", "")]
            value = node.value
        elif isinstance(node, ast.Assign):
            target_names = [getattr(t, "id", "") for t in node.targets]
            value = node.value
        if "_GHOST_ALIASES" in target_names and isinstance(value, ast.Dict):
            out: dict[str, str] = {}
            for k, v in zip(value.keys, value.values):
                if k is None:
                    continue
                try:
                    out[ast.literal_eval(k)] = ast.literal_eval(v)
                except Exception:  # noqa: BLE001 — skip non-literal entries
                    continue
            return out
    return {}


def _mode_evidence_scan(registry: dict) -> dict:
    """Warning-level scan: every advertised mode should appear as a string
    somewhere in the package. Absence = strong smell of a ghost mode (the
    'audit'-class defect), but delegation/metaprogramming make absence weak
    evidence — so this warns, it never fails the gate."""
    pkg = REPO / "arifosmcp"
    corpus: list[str] = []
    for path in pkg.rglob("*.py"):
        try:
            corpus.append(path.read_text(encoding="utf-8", errors="ignore"))
        except Exception:  # noqa: BLE001
            continue
    blob = "\n".join(corpus)
    out: dict = {"zero_evidence": [], "checked_modes": 0, "scanned_files": len(corpus)}
    for name, spec in registry.items():
        for mode in spec.get("modes") or []:
            out["checked_modes"] += 1
            if f'"{mode}"' not in blob and f"'{mode}'" not in blob:
                out["zero_evidence"].append(f"{name}.{mode}")
    return out


def main() -> int:
    sys.path.insert(0, str(REPO))
    try:
        from arifosmcp.constitutional_map import CANONICAL_TOOLS, DIAGNOSTIC_TOOLS
        from arifosmcp.runtime.public_surface import (
            KERNEL_ABI_8,
            public_tool_names_for_mode,
        )
        from arifosmcp.runtime.tools import CANONICAL_TOOL_HANDLERS as CTH
    except Exception as exc:  # noqa: BLE001
        print(
            json.dumps(
                {
                    "gate": "capability_truth",
                    "verdict": "ERROR",
                    "error": f"{type(exc).__name__}: {exc}",
                },
                indent=2,
            )
        )
        return 2

    registry = {**CANONICAL_TOOLS, **DIAGNOSTIC_TOOLS}
    public = list(public_tool_names_for_mode())
    violations: list[str] = []
    warnings: list[str] = []

    # 1. phantom_tools — advertised public name without a dispatch handler
    phantom = [n for n in public if n not in CTH]
    if phantom:
        violations.append(f"phantom_tools: {phantom}")

    # 2. missing_tools — KERNEL_ABI_8 name without a handler
    missing = [n for n in KERNEL_ABI_8 if n not in CTH]
    if missing:
        violations.append(f"missing_tools: {missing}")

    # 3. schema_mismatch — advertised enum ⊆ handler-declared universe
    schema_mismatch: dict[str, list[str]] = {}
    declared_universes: list[str] = []
    for name, handler in CTH.items():
        universe = getattr(handler, "__dispatch_modes__", None)
        if universe is None:
            continue
        declared_universes.append(name)
        advertised = registry.get(name, {}).get("modes", []) or []
        bad = sorted(m for m in advertised if m not in universe)
        if bad:
            schema_mismatch[name] = bad
    if schema_mismatch:
        violations.append(f"schema_mismatch: {schema_mismatch}")
    if not declared_universes:
        warnings.append("no handlers declare __dispatch_modes__ — schema_mismatch check is dormant")

    # 4. alias_conflicts — ghost aliases hidden + resolvable
    server_py = REPO / "arifosmcp" / "server.py"
    ghosts: dict[str, str] = {}
    if server_py.exists():
        ghosts = _ghosts_from_server(server_py.read_text(encoding="utf-8"))
    else:
        warnings.append("server.py not found — alias check skipped")
    alias_conflicts: list[str] = []
    for ghost, target in ghosts.items():
        if ghost in public:
            alias_conflicts.append(f"{ghost}: visible in discovery (must stay hidden)")
        if target not in CTH:
            alias_conflicts.append(f"{ghost}: target '{target}' not resolvable")
    if alias_conflicts:
        violations.append(f"alias_conflicts: {alias_conflicts}")

    # 5. mode-evidence scan (warning-level, never build-breaking) — every
    # advertised mode should appear as an implementation string somewhere in
    # the package. Zero-evidence = strong smell (the 'audit'-class ghost).
    mode_evidence = _mode_evidence_scan(registry)
    for item in mode_evidence["zero_evidence"]:
        warnings.append(
            f"mode-evidence: {item} — no implementation string found (advertised, unverified)"
        )

    verdict = "PASS" if not violations else "FAIL"
    out = {
        "gate": "capability_truth_gate",
        "verdict": verdict,
        "violations": violations,
        "warnings": warnings,
        "metrics": {
            "public_surface": public,
            "public_count": len(public),
            "kernel_abi_8": list(KERNEL_ABI_8),
            "handler_count": len(CTH),
            "phantom_tools": phantom,
            "missing_tools": missing,
            "schema_mismatch": schema_mismatch,
            "declared_universes": declared_universes,
            "ghost_aliases": len(ghosts),
            "alias_conflicts": alias_conflicts,
            "mode_evidence": mode_evidence,
        },
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main())
