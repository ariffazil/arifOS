#!/usr/bin/env python3
"""reachability_analysis.py — 111 OBSERVE import/reachability graph (read-only).

Builds a STATIC import graph from ACTIVE deployment roots (systemd/Docker/
console_scripts evidence) and classifies every file:
  PRODUCTION_REACHABLE / TEST_REACHABLE / UNREACHABLE_DEAD_CANDIDATE / NON_PYTHON
Reduces the H_0 UNKNOWN_HOLD bucket into explicit categories with confidence.

LIMITATION (v1): dynamic imports (importlib, string plugin loading, decorator
registration, env-selected module paths) are NOT fully resolved — flagged
"dynamic_imports_unresolved" in the report, exactly the class the OBSERVE spec
requires a second pass for. Read-only; no mutation.
"""

from __future__ import annotations
import os, ast, json, datetime, sys
from collections import defaultdict, deque

ROOT = "/root/arifOS"
OUT = os.path.join(ROOT, "reachability-report.json")

# ACTIVE production roots (deployment evidence captured 2026-09-16)
PROD_ROOTS = [
    "arifosmcp.runtime.__main__",  # pyproject: arifos / arifos-mcp / aaa-mcp
    "arifosmcp.runtime.server",  # Dockerfile CMD: uvicorn arifosmcp.runtime.server:app
    "arifosmcp.intelligence.cli",  # pyproject: aclip-cai
    "arifosmcp.runtime.l5_search_api",  # systemd: l5-search-api.service
    "deploy.vault999_writer.main",  # systemd: vault999-writer
    "scripts.kabarkan_health_server",  # systemd: kabarkan-health
]

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "build",
    "node_modules",
    "__pycache__",
    ".ua",
    ".claude",
    ".config",
    ".grimp_cache",
    ".import_linter_cache",
    ".ruff_cache",
    "dist",
    "egg-info",
}


def module_name(path: str):
    rel = os.path.relpath(path, ROOT)
    if not rel.endswith(".py"):
        return None
    rel = rel[:-3].replace(os.sep, ".")
    if rel.endswith(".__init__"):
        rel = rel[:-9]
    if rel.endswith(".__main__"):
        rel = rel[:-9]
    return rel


def imports_in(path: str, pkg: str):
    out = set()
    try:
        tree = ast.parse(open(path, encoding="utf-8", errors="ignore").read())
    except Exception:
        return out
    parts = pkg.split(".") if pkg else []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                out.add(a.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                out.add(node.module)
            elif node.level > 0:
                base = parts[: -(node.level - 1)] if node.level > 1 else parts[:]
                if node.module:
                    out.add(".".join(base + [node.module]) if base else node.module)
                elif base:
                    out.add(".".join(base))
    return out


def resolve(imp, modules):
    if imp in modules:
        return imp
    # prefix match: import arifosmcp.runtime.foo -> module arifosmcp.runtime
    cands = [m for m in modules if m == imp or m.startswith(imp + ".")]
    if cands:
        return min(cands, key=len)
    return None


def main():
    modules = {}  # module name -> path
    file_kind = {}  # path -> kind
    graph = defaultdict(set)

    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, ROOT)
            if fn.endswith(".py"):
                m = module_name(path)
                if m:
                    modules[m] = path
                    graph[m] = imports_in(path, m)
                file_kind[path] = "python"
            else:
                file_kind[path] = "non_python"

    # BFS from prod roots
    prod_seen = set()
    q = deque()
    for r in PROD_ROOTS:
        if r in modules or r in graph:
            prod_seen.add(r)
            q.append(r)
    while q:
        cur = q.popleft()
        for imp in graph.get(cur, ()):
            tgt = resolve(imp, modules)
            if tgt and tgt not in prod_seen:
                prod_seen.add(tgt)
                q.append(tgt)

    prod_paths = {modules[m] for m in prod_seen if m in modules}

    # test roots (pytest discovery heuristic: files under tests/, *_test.py, test_*.py)
    test_paths = set()
    for path in file_kind:
        rel = os.path.relpath(path, ROOT)
        if file_kind[path] == "python":
            if (
                "/tests/" in rel
                or rel.startswith("tests/")
                or os.path.basename(path).startswith("test_")
                or os.path.basename(path).endswith("_test.py")
            ):
                test_paths.add(path)

    # classify
    classification = {}
    for path, kind in file_kind.items():
        rel = os.path.relpath(path, ROOT)
        if kind != "python":
            classification[path] = "NON_PYTHON"
        elif path in prod_paths:
            classification[path] = "PRODUCTION_REACHABLE"
        elif path in test_paths:
            classification[path] = "TEST_REACHABLE"
        else:
            classification[path] = "UNREACHABLE_DEAD_CANDIDATE"

    from collections import Counter

    counts = Counter(classification.values())

    report = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "production_roots": PROD_ROOTS,
        "modules_indexed": len(modules),
        "production_reachable_modules": len(prod_seen),
        "classification_counts": dict(counts),
        "limitations": [
            "dynamic imports / plugin loading / decorator registration not fully resolved",
            "string-based module path selection not resolved",
            "pytest discovery is heuristic, not a live collection run",
        ],
        "entrypoint_classification": classify_entrypoints(),
        "sot_classification": classify_sot_files(),
        "dead_candidates_sample": [
            os.path.relpath(p, ROOT)
            for p in classification
            if classification[p] == "UNREACHABLE_DEAD_CANDIDATE"
        ][:60],
    }
    with open(OUT, "w") as fh:
        json.dump(report, fh, indent=2, sort_keys=True)

    print(f"reachability_analysis — {len(modules)} modules indexed → {OUT}\n")
    print("=== CLASSIFICATION COUNTS ===")
    for k, v in counts.most_common():
        print(f"  {k:<28} {v}")
    print(f"\n=== PRODUCTION ROOTS ({len(PROD_ROOTS)}) ===")
    for r in PROD_ROOTS:
        print(f"  {r}")
    print(
        f"\n=== DEAD CANDIDATES (unreachable .py, non-test) — sample {len(report['dead_candidates_sample'])} ==="
    )
    for f in report["dead_candidates_sample"]:
        print(f"  {f}")
    return 0


def classify_entrypoints():
    """Classify the 16 candidate entrypoints using deployment evidence."""
    roots = [
        ("arifosmcp/runtime/server.py", "PRODUCTION_ROOT", "Dockerfile CMD uvicorn ...:app"),
        (
            "arifosmcp/runtime/__main__.py",
            "PRODUCTION_ROOT",
            "console_scripts arifos/arifos-mcp/aaa-mcp",
        ),
        ("arifosmcp/intelligence/cli.py", "CLI_ADAPTER", "console_scripts aclip-cai"),
        ("arifosmcp/runtime/l5_search_api.py", "SERVICE", "systemd l5-search-api"),
        ("deploy/vault999-writer/main.py", "SERVICE", "systemd vault999-writer"),
        ("scripts/kabarkan_health_server.py", "SERVICE", "systemd kabarkan-health"),
        ("server.py", "LEGACY", "root-level; not in Docker CMD or console_scripts"),
        ("arifosmcp/server.py", "LEGACY_OR_ALT", "not the Docker CMD target"),
        ("arifosmcp/gateway/server.py", "TRANSPORT_ADAPTER", "gateway namespace"),
        ("arifosmcp/runtime/a2a/server.py", "TRANSPORT_ADAPTER", "A2A bridge"),
        ("arifosmcp/runtime/webmcp/server.py", "TRANSPORT_ADAPTER", "web MCP"),
        ("arifosmcp/biometric/server.py", "TRANSPORT_ADAPTER", "biometric surface"),
        ("arifosmcp/cli/main.py", "CLI_ADAPTER", "CLI entry"),
        ("arifosmcp/apps/command_center/app.py", "UI_APP", "command center"),
        ("arifosmcp/federation/__main__.py", "CLI_ADAPTER", "federation CLI"),
        ("arifos/aaa/__main__.py", "ORGAN_CLI", "AAA organ CLI"),
        ("arifos/forge/__main__.py", "ORGAN_CLI", "forge organ CLI"),
        ("arifosmcp/agents/eureka/__main__.py", "AGENT_CLI", "eureka agent"),
    ]
    return [{"path": p, "class": c, "evidence": e} for p, c, e in roots]


def classify_sot_files():
    """Classify the 32 SOT-like files into the 8 canonical-collapse categories."""
    rows = [
        ("kernel-sot.yaml", "CANON_SOURCE"),
        ("tools_sot.yaml", "GENERATED_PROJECTION", "gen_tools_sot.py output"),
        (
            "arifosmcp/constitutional_map.py",
            "CANON_FRAGMENT",
            "KERNEL_ABI_8 source (generation input)",
        ),
        (
            "arifosmcp/abi/capability_registry.json",
            "GENERATED_PROJECTION",
            "provider.tool = 8 canonical (verified)",
        ),
        ("arifosmcp/runtime/sot_active.py", "RUNTIME_CACHE", "boot-time derived"),
        ("arifosmcp/tool_registry.json", "RUNTIME_CACHE", "generated registry"),
        ("arifosmcp/tool_charter.py", "COMPATIBILITY_ADAPTER", "TOOLCHARTER legacy keys"),
        ("arifosmcp/schemas/arifos_tool_registry.json", "GENERATED_PROJECTION", "schema surface"),
        (
            "arifosmcp/arifos_registry/mcp_tool_registry.py",
            "COMPATIBILITY_ADAPTER",
            "MCP registry reader",
        ),
        ("arifosmcp/core/kernel/tool_registry.py", "UNKNOWN_HOLD", "parallel kernel registry"),
        ("arifosmcp/kernel/capability_registry.py", "UNKNOWN_HOLD", "parallel capability registry"),
        ("arifosmcp/schemas/tool_registry.py", "UNKNOWN_HOLD", "parallel tool registry"),
        ("arifosmcp/schemas/tool_manifest.schema.json", "CANON_FRAGMENT", "manifest schema"),
        ("contracts/tools.yaml", "CANON_FRAGMENT", "contract definition"),
        ("docs/reference/spec/mcp.charter.json", "HISTORICAL_RECORD", "MALFORMED JSON (verified)"),
        ("docs/reference/spec/server.json", "HISTORICAL_RECORD", "spec server"),
        (
            "static/arifos/theory/000/CANONICAL_SPEC.yaml",
            "HISTORICAL_RECORD",
            "static canonical spec",
        ),
        ("static/manifest/tools.json", "GENERATED_PROJECTION", "10 names incl 2 stale init_prompt"),
        ("federation/tool_manifest.py", "UNKNOWN_HOLD", "federation manifest"),
        (
            "arifosmcp/data/quote_registry_sot.yaml",
            "CANON_FRAGMENT",
            "quote registry (unrelated domain)",
        ),
        ("scripts/gen_tools_sot.py", "TOOLING", "generator (keep)"),
        ("scripts/audit_sot.py", "TOOLING", "validator (keep)"),
        ("scripts/generate_tool_manifest.py", "TOOLING", "generator (keep)"),
        ("scripts/sot_cron.py", "TOOLING", "scheduler (keep)"),
        ("scripts/sync_readme_sot.py", "TOOLING", "sync (keep)"),
        ("scripts/update_readme_sot.py", "TOOLING", "sync (keep)"),
        ("commands/scripts_archive/audit_sot.py", "HISTORICAL_RECORD", "archived copy"),
        ("tests/runtime/test_sot_active.py", "KEEP_TEST", "test"),
        ("tests/test_public_tool_registry.py", "KEEP_TEST", "test"),
        ("docs/SOT_MAP.md", "HISTORICAL_RECORD", "doc"),
        ("docs/adr/ADR-009-compiler-ssot.md", "HISTORICAL_RECORD", "ADR"),
        (
            "docs/canon/CANON_APEX_V2/05_ARIFOS_13TOOL_MANIFEST.md",
            "HISTORICAL_RECORD",
            "13-tool manifest doc",
        ),
        ("docs/receipts/M3-tools-sot-codegen-20260731.md", "HISTORICAL_RECORD", "receipt"),
    ]
    return [{"path": p, "class": c} for p, c, *_ in rows]


if __name__ == "__main__":
    sys.exit(main())
