#!/usr/bin/env python3
"""
audit_floor_coverage.py — TASK-P0-01
Audit floor enforcer coverage across canonical arifOS tools.

Source of truth: live MCP tools/list (F2 TRUTH beats prose).
Floor enforcer API: arifosmcp.runtime.law.check_laws() (canonical, NOT FloorEnforcer.check()).
Floor classification: canonical via core/laws.py LAW_LEVELS (DB-SOT ratified 2026-06-03).

Hard floors per canon: F1, F2, F4, F7, F9, L10, L11, L12, L13.
Soft floors per canon: F5, F6.
Derived floors per canon: F3, F8.

Task rule 4 also notes: "Hard floors (F1, F2, F9, F11, F13) = VOID on violation"
but that subset is a subset of the canonical HARD list (missing F4, F7, L10, L12).
We surface BOTH classifications.

USAGE:
  python3 scripts/audit_floor_coverage.py [--json] [--out PATH]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ── Constants ────────────────────────────────────────────────────────────────

REPO = Path("/root/arifOS")
RUNTIME = REPO / "arifosmcp" / "runtime" / "tools.py"
KERNEL_CANONICAL = REPO / "arifosmcp" / "tools" / "kernel_canonical.py"

# Canonical 13-tool alias → live 8-tool surface (per F2 TRUTH: live wins)
# Per AGENTS.md truth_rule: live :port/health + MCP tools/list beat prose.
LIVE_CANONICAL_TOOLS = [
    "arif_init",
    "arif_observe",
    "arif_think",
    "arif_route",
    "arif_judge",
    "arif_forge",
    "arif_seal",
    "arif_memory",
]

# Historical 13-tool surface (from constitutional_map.py CANONICAL_TOOLS):
# 9 main verbs + arif_kernel_intercept + arif_fetch + arif_triage + arif_bridge_connect
# Plus internal aliases.
DOCS_CANONICAL_13 = [
    "arif_init",
    "arif_observe",
    "arif_think",
    "arif_route",
    "arif_critique",
    "arif_judge",
    "arif_forge",
    "arif_compose",
    "arif_seal",
    "arif_kernel_intercept",
    "arif_fetch",
    "arif_memory",
    "arif_measure",
]

# All 13 canonical floors
FLOORS = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13"]

# Task rule 4 explicit hard floors (subset of canonical hard set)
TASK_RULE4_HARD = {"F1", "F2", "F9", "F11", "F13"}

# Canonical HARD classification per DB-SOT (L13 RATIFIED 2026-06-03):
# Source: core/laws.py LAW_LEVELS dict
CANONICAL_HARD = {"F1", "F2", "F4", "F7", "F9", "L10", "L11", "L12", "L13"}
CANONICAL_SOFT = {"F5", "F6"}
CANONICAL_DERIVED = {"F3", "F8"}

# Floor enforcer entry points in arifOS codebase
FLOOR_ENFORCER_APIS = [
    "check_laws",
    "check_law",
    "ConstitutionalLaws",
    "core.laws",
    "core.floors",
    "core.governance.governance_kernel",
    "governance_kernel",
    "enforcement.governance_engine",
    "_check_floor",
    "_enforce_law",
    "evaluate_tool_call",
]

# Verdict mapping: tool that returns VOID on hard floor violation
# Per arifosmcp/runtime/law.py: L13 → VOID, L09 → HOLD, L01/L11 → HOLD, others → HOLD
# Per core/laws.py: any HARD violation → VOID
HARD_FLOOR_VERDICT = "VOID"


# ── Helpers ──────────────────────────────────────────────────────────────────


def find_tool_function(tool_name: str) -> tuple[str, int] | None:
    """Locate the canonical handler for a tool. Returns (file_path, line)."""
    if tool_name == "arif_route":
        return (str(KERNEL_CANONICAL.relative_to(REPO)), 631)
    # All other canonical tools: _arif_* in runtime/tools.py
    handler_map = {
        "arif_init": ("_arif_session_init", RUNTIME, 7609),
        "arif_observe": ("_arif_sense_observe", RUNTIME, 9182),
        "arif_think": ("_arif_mind_reason_tool", RUNTIME, 11806),
        "arif_judge": ("_arif_kernel_intercept_tool", RUNTIME, 21058),
        "arif_forge": ("_arif_forge_execute_tool", RUNTIME, 18888),
        "arif_seal": ("_arif_vault_seal_tool", RUNTIME, 17870),
        "arif_memory": ("_arif_memory_v5_router", RUNTIME, 20379),
        "arif_kernel_intercept": ("_arif_kernel_intercept_tool", RUNTIME, 21058),
        "arif_critique": ("_arif_heart_critique", RUNTIME, None),
        "arif_compose": ("_arif_reply_compose_tool", RUNTIME, None),
        "arif_fetch": ("_arif_evidence_fetch", RUNTIME, None),
        "arif_measure": ("_arif_ops_measure", RUNTIME, None),
        "arif_act": ("_arif_act", RUNTIME, 21195),
    }
    if tool_name not in handler_map:
        return None
    fn_name, path, line = handler_map[tool_name]
    if line is None:
        # Find dynamically
        with path.open() as f:
            for i, line in enumerate(f, 1):
                if re.match(rf"^(async )?def {fn_name}\b", line):
                    line = i
                    break
    return (str(path.relative_to(REPO)), line) if line else None


def extract_function_body(file_path: Path, start_line: int) -> str:
    """Extract function body from start_line (1-indexed) until next top-level def.

    Returns the def signature line + body. Stops at the next top-level
    `def`, `async def`, `class`, or `@decorator` line.
    """
    lines = file_path.read_text().splitlines()
    if start_line is None or start_line > len(lines):
        return ""
    # 1-indexed → 0-indexed. start_line points at the def signature line.
    def_idx = start_line - 1
    if def_idx < 0 or def_idx >= len(lines):
        return ""
    if not re.match(r"^(async )?def\s+\w+", lines[def_idx]):
        # Find nearest def above start_line
        while def_idx >= 0 and not re.match(r"^(async )?def\s+\w+", lines[def_idx]):
            def_idx -= 1
        if def_idx < 0:
            return ""
    body = [lines[def_idx]]
    for i in range(def_idx + 1, len(lines)):
        line = lines[i]
        body.append(line)
        # Stop on next top-level def/class/decorator
        if (
            line
            and not line.startswith((" ", "\t", "#"))
            and (
                line.lstrip().startswith("def ")
                or line.lstrip().startswith("async def ")
                or line.lstrip().startswith("class ")
                or line.lstrip().startswith("@")
            )
        ):
            body.pop()
            break
    return "\n".join(body)


def check_floor_enforcer_call(tool_name: str, body: str) -> dict:
    """Check if a function body calls the floor enforcer before any execution."""
    findings = {
        "floor_enforcer_called": False,
        "called_at_line": None,
        "calls_before_execute": False,
        "apis_called": [],
        "verdict_handling": None,
        "delegated_check": None,
        "coverage_quality": "NONE",
    }
    body_lines = body.splitlines()
    first_enforce_idx = None
    first_execute_idx = None
    # Strip import lines so they don't trigger false positives
    for i, line in enumerate(body_lines):
        stripped = line.strip()
        # Skip comments and import statements
        if stripped.startswith(("#", "import ", "from ")):
            continue
        for api in FLOOR_ENFORCER_APIS:
            if api in line:
                if first_enforce_idx is None:
                    first_enforce_idx = i
                    findings["floor_enforcer_called"] = True
                    findings["called_at_line"] = i + 1
                if api not in findings["apis_called"]:
                    findings["apis_called"].append(api)
                break
        # Heuristic: execution patterns
        if first_execute_idx is None:
            if re.search(
                r"\b(exec|eval|subprocess|os\.system|run\(|invoke\(|dispatch\(|do_|commit|deploy|write|seal)\b",
                line,
            ):
                first_execute_idx = i
    findings["calls_before_execute"] = first_enforce_idx is not None and (
        first_execute_idx is None or first_enforce_idx <= first_execute_idx
    )
    # Detect delegation patterns (only when NOT just an import)
    non_import_body = "\n".join(
        line for line in body_lines if not line.strip().startswith(("import ", "from "))
    )
    if "_KERNEL.evaluate_intent" in non_import_body or "_KERNEL.execute_tool" in non_import_body:
        findings["delegated_check"] = "KERNEL_PARTIAL"
    if re.search(r"\b_arif_kernel_intercept\s*\(", non_import_body):
        findings["delegated_check"] = "KERNEL_FULL"
    if "constitutional_chain_id" in non_import_body:
        findings["delegated_check"] = findings.get("delegated_check") or "CHAIN_DELEGATED"
    # Verdict handling
    if re.search(r"^\s*return\s+.*VOID\b", non_import_body, re.MULTILINE):
        findings["verdict_handling"] = "VOID_RETURN"
    if "SABAR" in non_import_body:
        findings["verdict_handling"] = findings.get("verdict_handling") or "SABAR_REFERENCED"
    # Coverage quality
    if findings["floor_enforcer_called"] and "check_laws" in findings["apis_called"]:
        findings["coverage_quality"] = "FULL"
    elif findings["delegated_check"] == "KERNEL_FULL":
        findings["coverage_quality"] = "DELEGATED_FULL"
    elif findings["delegated_check"] in ("KERNEL_PARTIAL", "CHAIN_DELEGATED"):
        findings["coverage_quality"] = "DELEGATED_PARTIAL"
    elif findings["floor_enforcer_called"]:
        findings["coverage_quality"] = "PARTIAL"
    return findings


def tool_audit(tool_name: str) -> dict:
    """Run full audit on one tool. Also audits primary internal delegate."""
    # Map tools to their primary internal delegates (where floor checks may live)
    delegate_map = {
        "arif_forge": [
            ("arifosmcp/runtime/tools.py", 18075, "_arif_forge_execute"),
        ],
        "arif_seal": [
            ("arifosmcp/runtime/tools.py", None, "_arif_vault_seal"),  # find dynamically
        ],
        "arif_memory": [
            ("arifosmcp/runtime/memory_manage.py", None, None),
        ],
        "arif_observe": [
            ("arifosmcp/tools/sense.py", None, None),
            ("arifosmcp/runtime/tools.py", None, None),
        ],
        "arif_think": [
            ("arifosmcp/runtime/tools.py", 15355, "_arif_judge_deliberate"),
        ],
    }

    loc = find_tool_function(tool_name)
    if loc is None:
        return {
            "tool": tool_name,
            "found": False,
            "error": "Handler not located",
        }
    file_rel, start_line = loc
    file_abs = REPO / file_rel
    body = extract_function_body(file_abs, start_line)
    findings = check_floor_enforcer_call(tool_name, body)
    findings["tool"] = tool_name
    findings["file"] = file_rel
    findings["start_line"] = start_line
    findings["body_lines"] = len(body.splitlines())
    # Audit primary delegate(s)
    findings["delegates_audited"] = []
    for delegate in delegate_map.get(tool_name, []):
        del_file, del_line, del_name = delegate
        if del_file == "arifosmcp/runtime/tools.py" and del_line is None and del_name:
            # Find dynamically
            with (REPO / del_file).open() as fh:
                for i, line_text in enumerate(fh, 1):
                    if re.match(rf"^(async )?def {del_name}\b", line_text):
                        del_line = i
                        break
        if del_line is None:
            continue
        del_abs = REPO / del_file
        del_body = extract_function_body(del_abs, del_line)
        del_findings = check_floor_enforcer_call(del_name or "delegate", del_body)
        findings["delegates_audited"].append(
            {
                "delegate": del_name,
                "file": del_file,
                "line": del_line,
                "body_lines": len(del_body.splitlines()),
                "floor_enforcer_called": del_findings["floor_enforcer_called"],
                "apis_called": del_findings["apis_called"],
                "delegated_check": del_findings["delegated_check"],
                "coverage_quality": del_findings["coverage_quality"],
            }
        )
        # Upgrade main findings ONLY if delegate has STRICTLY better coverage
        # (no downgrade) AND the entry-point doesn't already have higher quality.
        delegate_quality_rank = {
            "NONE": 0,
            "PARTIAL": 1,
            "DELEGATED_PARTIAL": 2,
            "DELEGATED_FULL": 3,
            "FULL": 4,
        }
        entry_rank = delegate_quality_rank.get(findings["coverage_quality"], 0)
        delegate_rank = delegate_quality_rank.get(del_findings["coverage_quality"], 0)
        if delegate_rank > entry_rank:
            findings["coverage_quality"] = del_findings["coverage_quality"]
            findings["delegated_check"] = f"DELEGATE:{del_name}"
            findings["apis_called"].extend(del_findings["apis_called"])
    # Per-floor matrix based on best available evidence
    # Normalize keys to canonical F1..F13 (canonical HARD set uses L10/L11/L12/L13)
    findings["per_floor"] = {}
    canonical_floors = [
        "F1",
        "F2",
        "F3",
        "F4",
        "F5",
        "F6",
        "F7",
        "F8",
        "F9",
        "F10",
        "F11",
        "F12",
        "F13",
    ]
    # check_laws() in arifosmcp/runtime/law.py covers all 13 floors
    if "check_laws" in findings["apis_called"]:
        for f in canonical_floors:
            findings["per_floor"][f] = "checked"
    elif findings.get("coverage_quality") == "DELEGATED_FULL":
        # _arif_kernel_intercept checks F11/F13 + pre-trust addendum
        for f in canonical_floors:
            findings["per_floor"][f] = "checked" if f in ("F11", "F13") else "delegated"
    elif findings.get("coverage_quality") == "DELEGATED_PARTIAL":
        # _KERNEL.evaluate_intent checks F1 only (Amanah scorer)
        for f in canonical_floors:
            findings["per_floor"][f] = "checked" if f == "F1" else "delegated"
    elif findings.get("delegated_check") == "CHAIN_DELEGATED":
        # Relies on prior arif_judge SEAL chain_id — F13/F11 checked upstream
        for f in canonical_floors:
            findings["per_floor"][f] = "checked" if f in ("F11", "F13") else "session-only"
    else:
        for f in canonical_floors:
            findings["per_floor"][f] = "unchecked"
    findings["hard_voID_violation_returns"] = "VOID" in body and (
        "return" in body or "raise" in body
    )
    findings["soft_sabar_handling"] = "SABAR" in body
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--out", type=str, help="Write JSON to file")
    args = parser.parse_args()

    results = {
        "audit_task": "TASK-P0-01",
        "audit_target": "arifOS canonical tools floor enforcer coverage",
        "truth_source": "live MCP tools/list (per F2 TRUTH + AGENTS.md truth_rule)",
        "live_tool_count": len(LIVE_CANONICAL_TOOLS),
        "docs_canonical_13": DOCS_CANONICAL_13,
        "floor_enforcer_api": "arifosmcp.runtime.law.check_laws() (canonical)",
        "floor_enforcer_api_alt": (
            "core.laws.ConstitutionalLaws.evaluate() / arifosmcp.tools.base.Tool.check_laws()"
        ),
        "canonical_hard_floors": sorted(CANONICAL_HARD),
        "canonical_soft_floors": sorted(CANONICAL_SOFT),
        "canonical_derived_floors": sorted(CANONICAL_DERIVED),
        "task_rule4_hard_subset": sorted(TASK_RULE4_HARD),
        "tools": {},
    }

    # Audit live 8 + docs-claimed 13
    audited = set()
    for tool in LIVE_CANONICAL_TOOLS + DOCS_CANONICAL_13:
        if tool in audited:
            continue
        audited.add(tool)
        results["tools"][tool] = tool_audit(tool)

    # Compute summary
    coverage_count = sum(1 for t in results["tools"].values() if t.get("floor_enforcer_called"))
    results["summary"] = {
        "total_tools_audited": len(audited),
        "tools_with_floor_enforcer": coverage_count,
        "tools_missing_floor_enforcer": len(audited) - coverage_count,
        "coverage_pct": round(100.0 * coverage_count / len(audited), 1),
    }

    if args.json:
        output = json.dumps(results, indent=2, default=str)
        if args.out:
            Path(args.out).write_text(output)
            print(f"Wrote {args.out}")
        else:
            print(output)
    else:
        # Human-readable
        print("=== TASK-P0-01 Floor Coverage Audit ===")
        print(f"Live tools: {len(LIVE_CANONICAL_TOOLS)} | Docs-canonical: {len(DOCS_CANONICAL_13)}")
        print(f"Coverage: {coverage_count}/{len(audited)} tools call floor enforcer")
        print()
        for tool, t in results["tools"].items():
            status = "✓" if t.get("floor_enforcer_called") else "✗"
            print(f"{status} {tool:25} {t.get('file', 'N/A'):60} line {t.get('start_line', '?')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
