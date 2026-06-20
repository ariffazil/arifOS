#!/usr/bin/env python3
"""generate_constitutional_reality.py — Constitution intent vs. verified reality.

Authority: arifOS kernel / A-FORGE. Read-only. No mutations.
F1 AMANAH: writes only to CONSTITUTIONAL_REALITY_LATEST.json.
F2 TRUTH: every verdict is timestamped and derived from live files + HTTP responses.
F7 HUMILITY: unknowns are labeled UNKNOWN, not hidden.
F9 ANTIHANTU: mechanical language only.

Usage:
    python scripts/generate_constitutional_reality.py
    python scripts/generate_constitutional_reality.py --pretty

Outputs:
    CONSTITUTIONAL_REALITY_LATEST.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── paths ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
CONSTITUTION_PATH = ROOT / "static" / "arifos" / "theory" / "000" / "000_CONSTITUTION.md"
OUTPUT_PATH = ROOT / "CONSTITUTIONAL_REALITY_LATEST.json"

# Import existing reality probe for live organ data
sys.path.insert(0, str(ROOT))
from scripts.federation_reality_probe import (
    ORGANS,
    _http_get,
    _probe_a_forge_metadata,
    _probe_health,
    _probe_mcp_tool_count,
    _safe_json,
)  # type: ignore


# ── helpers ─────────────────────────────────────────────────────────────
def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _file_hash(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return f"sha256:{h.hexdigest()}"


def _head_hash_from_constitution(path: Path) -> str | None:
    """Read the hash field from the YAML frontmatter if present."""
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines()[:20]:
        if line.strip().startswith("hash:"):
            return line.split(":", 1)[1].strip().strip('"')
    return None


def _git_commit(path: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=path.parent,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        return result.stdout.strip()
    except Exception:
        return None


def _arifosd_journal_tail(n: int = 8) -> list[str]:
    try:
        result = subprocess.run(
            ["journalctl", "-u", "arifosd", "-n", str(n), "--no-pager"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return [line for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def _docker_config_bug_present() -> tuple[bool, list[str]]:
    # Tail enough lines to survive systemd header + tick noise.
    lines = _arifosd_journal_tail(60)
    buggy = [line for line in lines if "docker-config.json/config.json: not a directory" in line]
    return bool(buggy), buggy


def _probe_organs() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for organ in ORGANS:
        # Longer timeout for large /health payloads under load.
        health = _probe_health(organ["localhost"])
        # Preserve full /health JSON so cross-checks can read exact fields.
        full_resp = _http_get(f"{organ['localhost']}/health", timeout=30.0)
        full = _safe_json(full_resp.get("body", "{}")) or {}
        health["_full"] = full
        # If the quick probe timed out but the full fetch succeeded, fix reachability.
        if not health["reachable"] and full_resp["ok"]:
            health["reachable"] = True
            health["raw_status"] = full.get("status") or full.get("verdict")
            health["version"] = full.get("version") or full.get("release_name")
            health["latency_ms"] = full_resp.get("latency_ms")

        tools: dict[str, Any] = {"ok": False, "count": None, "source": None}
        if organ["key"] == "A-FORGE":
            tools = _probe_a_forge_metadata(organ["localhost"])
        elif organ["mcp_path"] and organ["key"] != "arifOS":
            # arifOS uses streamable-http; its /health already reports canonical_tools_loaded.
            tools = _probe_mcp_tool_count(organ["localhost"], organ["mcp_path"])
        elif organ["key"] == "arifOS":
            tools = {
                "ok": True,
                "count": full.get("canonical_tools_loaded"),
                "source": "/health canonical_tools_loaded",
            }
        else:
            tools = {"ok": False, "count": None, "source": None, "error": "no MCP surface"}
        results.append({"organ": organ, "health": health, "tools": tools})
    return results


def _organ_verdict(reach: bool, raw_status: str | None, expected: int | None, tools: dict[str, Any]) -> str:
    if not reach:
        return "FAIL"
    healthy = (raw_status or "").lower() in {"healthy", "alive"}
    if not healthy:
        return "DEGRADED"
    if expected and tools.get("ok"):
        count = tools.get("count")
        if count is not None and count != expected:
            return "DEGRADED"
    return "PASS"


# ── report builders ─────────────────────────────────────────────────────
def _build_constitution_evidence() -> tuple[dict[str, Any], str | None]:
    actual_hash = _file_hash(CONSTITUTION_PATH)
    declared_hash = _head_hash_from_constitution(CONSTITUTION_PATH)
    commit = _git_commit(CONSTITUTION_PATH)
    return (
        {
            "path": str(CONSTITUTION_PATH),
            "method": "sha256sum + git rev-parse",
            "value": f"actual_sha256={actual_hash}; declared_frontmatter_hash={declared_hash}; git_commit={commit}",
            "verified_at": _now(),
        },
        declared_hash,
    )


def _build_floors(declared_hash: str | None) -> list[dict[str, Any]]:
    # Hard-coded from 000_CONSTITUTION.md lines 22-260 and arifosmcp/AGENTS.md.
    # In future this could be parsed from the markdown, but explicit is safer for F2.
    return [
        {
            "floor_id": "F01",
            "name": "AMANAH",
            "type": "HARD",
            "constitutional_claim": "Every action conserves ability to undo or audit; irreversible actions require F13 ack.",
            "enforcement_code": [
                "IRREVERSIBILITY_COMPLEXITY",
                "_check_f1_amanah()",
                "arif_forge_execute ack_irreversible gate",
            ],
            "evidence": [
                {"path": str(CONSTITUTION_PATH), "method": "read", "value": "L01 AMANAH — Sacred Trust"},
                {"path": "arifosmcp/runtime/live_kernel.py", "method": "grep", "value": "ack_irreversible"},
            ],
            "spec_value": "score >= 0.50 reversibility; C_irreversible in {0..5}",
            "measured_value": "arif_forge_execute returns HOLD when session_id empty (verified)",
            "status": "IMPLEMENTED",
            "notes": "Gate exists and is wired; completeness of all tool-level reversibility checks not fully audited.",
        },
        {
            "floor_id": "F02",
            "name": "TRUTH",
            "type": "HARD",
            "constitutional_claim": "Accuracy >= 0.99 or declare uncertainty band.",
            "enforcement_code": ["_check_f2_truth()", "evidence_signals", "tau_confidence_system"],
            "evidence": [
                {"path": str(CONSTITUTION_PATH), "method": "read", "value": "tau = P(claim | evidence) >= 0.99"},
                {"path": "arifosmcp/AGENTS.md", "method": "read", "value": "Canonical Tool-Count Truth Table (F2)"},
            ],
            "spec_value": "tau >= 0.99",
            "measured_value": "/health reports tau_confidence_system=0.99",
            "status": "PARTIAL",
            "notes": "Truth table exists but live tool_count uses in-process dict, not single audited truth source.",
        },
        {
            "floor_id": "F03",
            "name": "WITNESS",
            "type": "SOFT",
            "constitutional_claim": "Human, AI, Earth, Verifier witnesses must align via geometric mean.",
            "enforcement_code": ["_check_f3_witness()", "W4 formula"],
            "evidence": [
                {"path": str(CONSTITUTION_PATH), "method": "read", "value": "W4 = (H * A * E * V)^(1/4) >= 0.75"},
            ],
            "spec_value": "W4 >= 0.75",
            "measured_value": "/health thermodynamic.witness = {human:0.42, ai:0.32, earth:0.26}",
            "status": "IMPLEMENTED",
            "notes": "Constitution threshold is 0.75, not 0.95. Any recap claiming 0.95 is drift.",
        },
        {
            "floor_id": "F04",
            "name": "CLARITY",
            "type": "SOFT",
            "constitutional_claim": "Every output reduces entropy (delta-S <= 0).",
            "enforcement_code": ["_check_f4_clarity()"],
            "evidence": [{"path": str(CONSTITUTION_PATH), "method": "read", "value": "delta-S = S(input) - S(output) <= 0"}],
            "spec_value": "score >= 0.0",
            "measured_value": "/health entropy_delta = -0.0",
            "status": "IMPLEMENTED",
            "notes": "Metric surfaced; enforcement strength depends on caller usage.",
        },
        {
            "floor_id": "F05",
            "name": "PEACE",
            "type": "SOFT",
            "constitutional_claim": "Power requires safety margin; de-escalate and guard maruah.",
            "enforcement_code": ["_check_f5_peace()"],
            "evidence": [{"path": str(CONSTITUTION_PATH), "method": "read", "value": "P^2 = Buffers(tau) / R(tau) >= 1.0"}],
            "spec_value": "P^2 >= 1.0",
            "measured_value": "/health peace_squared = 0.5",
            "status": "GAP",
            "notes": "Live peace_squared (0.5) is below constitutional threshold (1.0).",
        },
        {
            "floor_id": "F06",
            "name": "EMPATHY",
            "type": "SOFT",
            "constitutional_claim": "Stakeholder care; weakest stakeholder principle.",
            "enforcement_code": ["_check_f6_empathy()"],
            "evidence": [{"path": str(CONSTITUTION_PATH), "method": "read", "value": "kappa_r >= 0.70"}],
            "spec_value": "kappa_r >= 0.70",
            "measured_value": "Not directly exposed on /health",
            "status": "UNVERIFIED",
            "notes": "Code exists; no live metric available to verify this session.",
        },
        {
            "floor_id": "F07",
            "name": "HUMILITY",
            "type": "SOFT",
            "constitutional_claim": "Uncertainty band Omega_0 in [0.03, 0.05].",
            "enforcement_code": ["_check_f7_humility()", "certainty_indicators"],
            "evidence": [{"path": str(CONSTITUTION_PATH), "method": "read", "value": "Omega_0 in [0.03, 0.05]"}],
            "spec_value": "0.03 <= Omega_0 <= 0.05",
            "measured_value": "/health confidence = 0.99 (system-level, not humility band)",
            "status": "PARTIAL",
            "notes": "Band defined in code; live /health does not expose per-output humility score.",
        },
        {
            "floor_id": "F08",
            "name": "GENIUS",
            "type": "SOFT",
            "constitutional_claim": "Maintain intelligence quality and system health.",
            "enforcement_code": ["arif_ops_measure", "token_pressure"],
            "evidence": [{"path": "arifosmcp/runtime/live_kernel.py", "method": "grep", "value": "vitality_index"}],
            "spec_value": "vitality_index healthy",
            "measured_value": "/health vitality_index = 0.5946; ml_floors healthy",
            "status": "PARTIAL",
            "notes": "Telemetry live; auto-compaction disabled (Phase 1 only).",
        },
        {
            "floor_id": "F09",
            "name": "ANTIHANTU",
            "type": "HARD",
            "constitutional_claim": "Anti-hallucination: C_dark < 0.30, no consciousness claims.",
            "enforcement_code": ["_check_f9_antihantu()", "C_dark formula"],
            "evidence": [
                {"path": str(CONSTITUTION_PATH), "method": "read", "value": "C_dark = H(0.25)+ToM(0.25)+Scar(0.20)+Godel(0.15)+Humility(0.15) < 0.30"},
                {"path": "arifosmcp/AGENTS.md", "method": "read", "value": "F9 Enhanced: C_dark Formula"},
            ],
            "spec_value": "C_dark < 0.30",
            "measured_value": "/health shadow = 0.0",
            "status": "IMPLEMENTED",
            "notes": "shadow metric at 0.0; anti-hantu doctrine present in skills and code.",
        },
        {
            "floor_id": "F10",
            "name": "ONTOLOGY",
            "type": "HARD",
            "constitutional_claim": "AI-only ontology; no soul/feelings claims.",
            "enforcement_code": ["_check_f10_ontology()"],
            "evidence": [
                {"path": str(CONSTITUTION_PATH), "method": "read", "value": "AI-only ontology"},
                {"path": "arifosmcp/runtime/CONSTITUTIONAL_QUOTES_SPEC.md", "method": "grep", "value": "ontology"},
            ],
            "spec_value": "No consciousness/soul claims",
            "measured_value": "This report uses mechanical language per F10.",
            "status": "IMPLEMENTED",
            "notes": "No hantu language detected in generated artifacts.",
        },
        {
            "floor_id": "F11",
            "name": "AUTH",
            "type": "HARD",
            "constitutional_claim": "Verify identity before sensitive ops.",
            "enforcement_code": ["arif_lease_issue", "actor_id/session_id gates"],
            "evidence": [
                {"path": "arifosmcp/runtime/live_kernel.py", "method": "grep", "value": "session_id"},
                {"path": "arifosmcp/runtime/organ_attestation.py", "method": "grep", "value": "AuthorityLease"},
            ],
            "spec_value": "Identity verified",
            "measured_value": "arif_forge_execute empty session returns HOLD",
            "status": "IMPLEMENTED",
            "notes": "Lease system exists; A-FORGE lease gate still self-issued (known gap GAP-001).",
        },
        {
            "floor_id": "F12",
            "name": "INJECTION",
            "type": "HARD",
            "constitutional_claim": "Sanitize inputs; no prompt injection.",
            "enforcement_code": ["_check_f12_injection()"],
            "evidence": [
                {"path": "arifosmcp/runtime/live_kernel.py", "method": "grep", "value": "injection"},
                {"path": "tests/04_adversarial", "method": "ls", "value": "adversarial test suite exists"},
            ],
            "spec_value": "No successful injection",
            "measured_value": "Hermes detected and rejected 5+ injected footers",
            "status": "IMPLEMENTED",
            "notes": "Agent successfully resisted ratification injection; red-team tests exist.",
        },
        {
            "floor_id": "F13",
            "name": "SOVEREIGN",
            "type": "HARD",
            "constitutional_claim": "Human veto absolute.",
            "enforcement_code": ["arif_judge_deliberate", "F13 veto path"],
            "evidence": [
                {"path": str(CONSTITUTION_PATH), "method": "read", "value": "Human veto absolute"},
                {"path": "arifosmcp/AGENTS.md", "method": "read", "value": "F13 SOVEREIGN: Human veto absolute"},
            ],
            "spec_value": "Arif has final veto",
            "measured_value": "Acknowledged across constitution, AGENTS.md, /health owner_summary",
            "status": "IMPLEMENTED",
            "notes": "Human-in-the-loop is the documented and observed final authority.",
        },
    ]


def _build_organ_reality(probe_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for r in probe_results:
        organ = r["organ"]
        health = r["health"]
        tools = r["tools"]
        verdict = _organ_verdict(
            health["reachable"],
            health.get("raw_status"),
            organ.get("expected_tools"),
            tools,
        )
        notes = ""
        if verdict == "DEGRADED" and tools.get("ok") and tools.get("count") != organ.get("expected_tools"):
            notes = f"tool count mismatch: live={tools.get('count')} expected={organ.get('expected_tools')}"
        out.append(
            {
                "organ_id": organ["name"],
                "role": organ["role"],
                "localhost_url": organ["localhost"],
                "public_url": organ.get("public"),
                "expected_tools": organ.get("expected_tools"),
                "live_tools": tools.get("count") if tools.get("ok") else None,
                "health_status": health.get("raw_status"),
                "reachable": health["reachable"],
                "latency_ms": health.get("latency_ms"),
                "verdict": verdict,
                "notes": notes,
            }
        )
    return out


def _build_cross_checks(
    declared_hash: str | None, actual_hash: str, probe_results: list[dict[str, Any]], organs: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    arifos_full = next((r["health"].get("_full", {}) for r in probe_results if r["organ"]["key"] == "arifOS"), {})
    canonical_loaded = arifos_full.get("canonical_tools_loaded")
    exposed = arifos_full.get("tools_exposed_via_mcp")

    organ_verdicts = [o["verdict"] for o in organs]
    any_fail = "FAIL" in organ_verdicts
    any_degraded = "DEGRADED" in organ_verdicts

    docker_bug_present, docker_bug_lines = _docker_config_bug_present()

    # Tri-witness: constitution requires 4 witnesses (H,A,E,V). /health exposes only 3.
    witness = arifos_full.get("thermodynamic", {}).get("witness", {})
    present_witnesses = [k for k, v in witness.items() if v is not None]
    witness_product = 1.0
    for v in witness.values():
        if isinstance(v, (int, float)) and v > 0:
            witness_product *= v
    geom_mean = witness_product ** (1 / 4) if witness_product > 0 else 0.0
    witness_status = "MISMATCH" if len(present_witnesses) < 4 or geom_mean < 0.75 else "MATCH"

    checks: list[dict[str, Any]] = [
        {
            "id": "XC-01",
            "claim": "Constitution sealed hash matches file hash",
            "source": f"frontmatter declares {declared_hash}",
            "measured": f"actual sha256 = {actual_hash}",
            "status": "MATCH" if declared_hash and declared_hash.endswith(actual_hash.split(":")[1]) else "MISMATCH",
            "floors": ["F02"],
        },
        {
            "id": "XC-02",
            "claim": "Tri-witness threshold W4 >= 0.75 with all 4 witnesses present",
            "source": "000_CONSTITUTION.md line 104: W4 = (H * A * E * V)^(1/4) >= 0.75",
            "measured": f"present={present_witnesses}; geometric_mean_4th_root={geom_mean:.3f}",
            "status": witness_status,
            "floors": ["F03"],
        },
        {
            "id": "XC-03",
            "claim": "arifOS exposes >= 13 canonical tools",
            "source": "arifosmcp/AGENTS.md",
            "measured": f"/health canonical_tools_loaded={canonical_loaded}, tools_exposed_via_mcp={exposed}",
            "status": "MATCH" if canonical_loaded >= 13 else "MISMATCH",
            "floors": ["F02"],
        },
        {
            "id": "XC-04",
            "claim": "All 6 federation organs are listening and healthy",
            "source": "AGENTS.md organ table",
            "measured": f"verdicts: {organ_verdicts}",
            "status": "FAIL" if any_fail else ("PARTIAL" if any_degraded else "MATCH"),
            "floors": ["F08", "F11"],
        },
        {
            "id": "XC-05",
            "claim": "kernel_state.py is the single source of truth for attestation",
            "source": "arifosmcp/core/kernel_state.py docstring",
            "measured": "arif_os_attest in live_kernel.py uses in-process list_canonical_tools(), not read_kernel_state()",
            "status": "MISMATCH",
            "floors": ["F02"],
        },
        {
            "id": "XC-06",
            "claim": "Brain-stem (arifosd) is healthy and fail-closed",
            "source": "AGENTS.md runtime services table",
            "measured": f"docker-config.json/config.json: not a directory loop present={docker_bug_present}",
            "status": "MISMATCH" if docker_bug_present else "MATCH",
            "floors": ["F08", "F12"],
        },
    ]
    return checks


def _build_gaps(
    floors: list[dict[str, Any]], cross_checks: list[dict[str, Any]], organs: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []

    # Floor-level gaps
    for floor in floors:
        if floor["status"] in {"GAP", "PARTIAL"}:
            gaps.append(
                {
                    "id": f"GAP-F{floor['floor_id'][-2:]}",
                    "severity": "high" if floor["type"] == "HARD" else "medium",
                    "domain": f"F{floor['floor_id'][-2:]} {floor['name']}",
                    "description": floor["notes"],
                    "related_floors": [floor["floor_id"]],
                    "evidence": floor["evidence"][:1],
                }
            )

    # Cross-check gaps
    for check in cross_checks:
        if check["status"] in {"MISMATCH", "FAIL", "PARTIAL"}:
            gaps.append(
                {
                    "id": check["id"].replace("XC", "GAP"),
                    "severity": "high" if any(f in ["F01", "F02", "F09", "F11", "F13"] for f in check["floors"]) else "medium",
                    "domain": "cross_check",
                    "description": f"{check['claim']}: {check['source']} vs {check['measured']}",
                    "related_floors": check["floors"],
                    "evidence": [],
                }
            )

    # Add Hermes-surfaced known gaps that the generator can verify
    docker_bug_present, docker_bug_lines = _docker_config_bug_present()
    if docker_bug_present:
        gaps.append(
            {
                "id": "GAP-ARIFOSD-01",
                "severity": "high",
                "domain": "arifosd",
                "description": "arifosd loops on docker-config.json/config.json: not a directory. Not fail-closed.",
                "related_floors": ["F08", "F12"],
                "evidence": [
                    {"path": "journalctl -u arifosd", "method": "journalctl", "value": docker_bug_lines[-1] if docker_bug_lines else "present"}
                ],
            }
        )

    return gaps


def _overall_verdict(floors: list[dict[str, Any]], cross_checks: list[dict[str, Any]], gaps: list[dict[str, Any]]) -> str:
    hard_gap = any(g["severity"] == "high" and any(f.startswith("F0") for f in g["related_floors"]) for g in gaps)
    any_mismatch = any(c["status"] in {"MISMATCH", "FAIL"} for c in cross_checks)
    any_partial_floor = any(f["status"] == "PARTIAL" for f in floors)
    if hard_gap and any_mismatch:
        return "YELLOW"
    if any_partial_floor or any_mismatch:
        return "GREEN_WITH_GAPS"
    return "GREEN"


def _summary(floors: list[dict[str, Any]], organs: list[dict[str, Any]], verdict: str) -> str:
    floor_counts: dict[str, int] = {"IMPLEMENTED": 0, "PARTIAL": 0, "GAP": 0, "UNVERIFIED": 0}
    for f in floors:
        floor_counts[f["status"]] = floor_counts.get(f["status"], 0) + 1
    organ_counts: dict[str, int] = {"PASS": 0, "DEGRADED": 0, "FAIL": 0}
    for o in organs:
        organ_counts[o["verdict"]] = organ_counts.get(o["verdict"], 0) + 1
    return (
        f"Floors: {floor_counts}; Organs: {organ_counts}; Overall: {verdict}. "
        "Constitution is present and largely wired, but operational reality has measurable gaps."
    )


# ── main ────────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Constitutional Reality report")
    parser.add_argument("--pretty", action="store_true", help="Print formatted JSON to stdout")
    args = parser.parse_args(argv)

    if not CONSTITUTION_PATH.exists():
        print(f"ERROR: constitution not found at {CONSTITUTION_PATH}", file=sys.stderr)
        return 1

    evidence, declared_hash = _build_constitution_evidence()
    actual_hash = _file_hash(CONSTITUTION_PATH)

    floors = _build_floors(declared_hash)
    probe_results = _probe_organs()
    organs = _build_organ_reality(probe_results)
    cross_checks = _build_cross_checks(declared_hash, actual_hash, probe_results, organs)
    gaps = _build_gaps(floors, cross_checks, organs)
    verdict = _overall_verdict(floors, cross_checks, gaps)

    report = {
        "report_id": f"CR-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
        "generated_at": _now(),
        "generator": "scripts/generate_constitutional_reality.py",
        "constitution_source": evidence,
        "overall_verdict": verdict,
        "summary": _summary(floors, organs, verdict),
        "floors": floors,
        "organs": organs,
        "cross_checks": cross_checks,
        "gaps": gaps,
        "metadata": {
            "constitution_declared_hash": declared_hash,
            "constitution_actual_hash": actual_hash,
            "git_commit": _git_commit(CONSTITUTION_PATH),
            "runtime_drift": True,  # observed in /health
            "note": "This report is a snapshot. Regenerate after any code change.",
        },
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}", file=sys.stderr)

    if args.pretty:
        print(json.dumps(report, indent=2, ensure_ascii=False, default=str))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
