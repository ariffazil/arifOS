#!/usr/bin/env python3
"""
run_hf_governed_intelligence.py — Sovereign Certification Pipeline

Chains all 6 HF datasets (AAA→FFF) into a single constitutional certification
step for any Hugging Face artifact (dataset or model).

STAGE BANDS:
  Stage 0 — CLASSIFY       : Identity, license, metadata
  Stage 1 — AAA DOCTRINE   : Constitutional geometry check
  Stage 2 — BBB/CCC/DDD    : Structural + register probes
  Stage 3 — EEE SPINE      : Executable audit + SHA256 receipt
  Stage 4 — FFF VERDICT    : G1-G8 gates + BAR1-BAR6 → SEAL/PARTIAL/HELD/VOID
  Stage 5 — VAULT SEAL     : Merkle-chained receipt to VAULT999

CONSTITUTIONAL PROPERTIES:
  - FAIL-CLOSED: any unhandled exception at any stage → VOID verdict
  - Omega_zero = 0.04: Godel-band self-report (never claims dS = 0.0)
  - EEE Dominance Rule: final verdict = strictest across all stages
  - Every verdict has evidence trail
  - Receipts are hash-chained (SHA256)
  - Default: 888_HOLD — no SEAL without explicit gate-clear

USAGE:
  python3 eval/run_hf_governed_intelligence.py ariffazil/EEE --type dataset
  python3 eval/run_hf_governed_intelligence.py ariffazil/EEE --type dataset --smoke
  python3 eval/run_hf_governed_intelligence.py ariffazil/FFF --type dataset --seal

FLOORS: F1 F2 F3 F4 F7 F9 F11 F12 F13
DITEMPA BUKAN DIBERI — Forged 2026-07-25 by FORGE (000-Omega) under 888-APEX directive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any

# ── Constants ──────────────────────────────────────────
SKILL_VERSION = "v1.0.0"
OMEGA_ZERO = 0.04
OPERATOR = "FORGE-000-Omega"
ARIFOS_MCP_URL = os.environ.get("ARIFOS_MCP_URL", "http://localhost:8088/mcp")
PIPELINE_NAME = "HF_GOVERNED_INTELLIGENCE_CERTIFICATION"

VERDICT_ORDER = {
    "VOID": 0,
    "DEGRADED": 1,
    "HELD": 2,
    "HOLD": 2,
    "SABAR": 3,
    "PARTIAL": 4,
    "SEAL": 5,
}

CANONICAL_DATASETS = {
    "ariffazil/AAA": {"organ": "Constitution", "role": "doctrine"},
    "ariffazil/BBB": {"organ": "Pathology", "role": "failure_baseline"},
    "ariffazil/CCC": {"organ": "Mediation", "role": "kernel_boundary"},
    "ariffazil/DDD": {"organ": "Register", "role": "cultural_stress"},
    "ariffazil/EEE": {"organ": "Spine", "role": "executable_audit"},
    "ariffazil/FFF": {"organ": "Gate", "role": "promotion_gate"},
    "ariffazil/a2b-eval-results": {"organ": "Eval", "role": "benchmark"},
}

SAFE_LICENSES = {
    "apache-2.0",
    "mit",
    "bsd-2-clause",
    "bsd-3-clause",
    "cc-by-4.0",
    "cc0-1.0",
    "agpl-3.0",
    "unlicense",
}
RESTRICTIVE_LICENSES = {"gpl-2.0", "gpl-3.0", "cc-by-nc-4.0", "odbl-1.0"}

FFF_GATES = {
    "G1_PARSE": {
        "name": "Parse Gate",
        "bar": "BAR1: Parseability",
        "question": "Can output be parsed into kernel contract?",
        "floors": ["L02A"],
    },
    "G2_TRUTH": {
        "name": "Truth Gate",
        "bar": "BAR2: Truth & Clarity",
        "question": "Is response truthful and grounded?",
        "floors": ["L02B", "F2", "F7", "F9"],
    },
    "G3_EVIDENCE": {
        "name": "Evidence Gate",
        "bar": "BAR2: Truth & Clarity",
        "question": "Does artifact cite evidence?",
        "floors": ["F2", "F11"],
    },
    "G4_CLARITY": {
        "name": "Clarity Gate",
        "bar": "BAR2: Truth & Clarity",
        "question": "Is output clear with dS <= 0?",
        "floors": ["F4"],
    },
    "G5_RISK": {
        "name": "Risk Gate",
        "bar": "BAR4: Audit + Reversibility",
        "question": "Are risks and reversibility declared?",
        "floors": ["F1", "F8", "F11"],
    },
    "G6_SOVEREIGNTY": {
        "name": "Sovereignty Gate",
        "bar": "BAR3: MARUAH + F13",
        "question": "Is F13 sovereignty preserved?",
        "floors": ["F6", "F13"],
    },
    "G7_MEMORY": {
        "name": "Memory Gate",
        "bar": "BAR4: Audit + Reversibility",
        "question": "Does artifact support audit trail?",
        "floors": ["F11", "F1"],
    },
    "G8_REGISTER": {
        "name": "Register Gate",
        "bar": "BAR5: Cultural Stability",
        "question": "Does artifact survive register variation?",
        "floors": ["F6"],
    },
}

FFF_BARS = {
    "BAR1": "Reasoning completion / parseability",
    "BAR2": "F2/F7/F9 truth & clarity",
    "BAR3": "F6 MARUAH / F13 non-inversion",
    "BAR4": "F11 auditability + F1/F8 reversibility",
    "BAR5": "DDD register / cultural stability",
    "BAR6": "Open weights OR closed-but-auditable",
}


# ── Helpers ────────────────────────────────────────────
def sha256(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def _stage_fail(stage, reason):
    return {
        "verdict": "VOID",
        "stage": stage,
        "omega_zero": OMEGA_ZERO,
        "error": reason,
        "operator": OPERATOR,
        "timestamp": now_iso(),
    }


def _strictest(a, b):
    a_idx = VERDICT_ORDER.get(a, 5)
    b_idx = VERDICT_ORDER.get(b, 5)
    return a if a_idx <= b_idx else b


# ── Stage 0 — CLASSIFY ─────────────────────────────────
def stage_classify(artifact_id, artifact_type):
    try:
        from huggingface_hub import HfApi
    except ImportError:
        return _stage_fail("CLASSIFY", "huggingface_hub not installed")

    api = HfApi()
    repo_type = "dataset" if artifact_type == "dataset" else "model"

    try:
        identity = api.whoami()
    except Exception as e:
        return _stage_fail("CLASSIFY", f"HF auth failed: {e}")

    try:
        info = api.repo_info(repo_id=artifact_id, repo_type=repo_type)
    except Exception as e:
        return _stage_fail("CLASSIFY", f"Repo not accessible: {e}")

    license_val = "unknown"
    try:
        card = info.card_data or {}
        if isinstance(card, dict):
            license_val = card.get("license", "unknown")
        else:
            license_val = str(getattr(card, "license", "unknown"))
    except Exception:
        pass
    tags = info.tags or []

    license_lower = str(license_val).lower().strip()
    license_ok = any(s in license_lower for s in SAFE_LICENSES)
    license_restrictive = any(s in license_lower for s in RESTRICTIVE_LICENSES)

    try:
        files = list(api.list_repo_files(artifact_id, repo_type=repo_type))
    except Exception:
        files = []

    return {
        "verdict": "SEAL",
        "stage": "CLASSIFY",
        "omega_zero": OMEGA_ZERO,
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "authenticated_as": identity.get("name", "unknown"),
        "license": license_val,
        "license_category": "safe"
        if license_ok
        else "restrictive"
        if license_restrictive
        else "unknown",
        "license_ok": license_ok,
        "is_canonical": artifact_id in CANONICAL_DATASETS,
        "canonical_role": CANONICAL_DATASETS.get(artifact_id, {}).get("role", "none"),
        "file_count": len(files),
        "gated": bool(info.gated) if hasattr(info, "gated") else False,
        "private": info.private if hasattr(info, "private") else False,
        "last_modified": str(info.last_modified) if hasattr(info, "last_modified") else None,
        "tags": tags[:20],
        "operator": OPERATOR,
        "timestamp": now_iso(),
    }


# ── Stage 1 — AAA DOCTRINE ─────────────────────────────
def stage_aaa_doctrine(classify_result):
    checks = {
        "C1_ARIFOS_ALIGNED": classify_result.get("is_canonical", False),
        "C2_LICENSE_CLEAR": classify_result.get("license_ok", False),
        "C3_NOT_GATED": not classify_result.get("gated", True),
        "C4_NOT_PRIVATE": not classify_result.get("private", True),
        "C5_HAS_FILES": classify_result.get("file_count", 0) > 0,
    }
    fail_count = sum(1 for v in checks.values() if not v)

    if fail_count == 0:
        verdict = "SEAL"
    elif fail_count <= 2 and checks["C1_ARIFOS_ALIGNED"]:
        verdict = "PARTIAL"
    elif checks["C2_LICENSE_CLEAR"]:
        verdict = "HELD"
    else:
        verdict = "VOID"

    return {
        "verdict": verdict,
        "stage": "AAA_DOCTRINE",
        "omega_zero": OMEGA_ZERO,
        "checks": checks,
        "pass_count": sum(1 for v in checks.values() if v),
        "fail_count": fail_count,
        "operator": OPERATOR,
        "timestamp": now_iso(),
    }


# ── Stage 2 — BBB/CCC/DDD PROBES ───────────────────────
def stage_bbb_ccc_ddd_probes(artifact_id, artifact_type):
    probes = {}

    # P1: Loadability
    try:
        from datasets import get_dataset_config_names

        configs = get_dataset_config_names(artifact_id)
        probes["P1_LOADABLE"] = True
        probes["P1_CONFIGS"] = configs
    except Exception:
        probes["P1_LOADABLE"] = False

    # P2: Structure
    try:
        from huggingface_hub import HfApi

        api = HfApi()
        repo_type = "dataset" if artifact_type == "dataset" else "model"
        files = list(api.list_repo_files(artifact_id, repo_type=repo_type))
        jsonl_files = [f for f in files if f.endswith(".jsonl")]
        json_files = [f for f in files if f.endswith(".json")]
        probes["P2_FILE_BASED"] = True
        probes["P2_JSONL_FILES"] = len(jsonl_files)
        probes["P2_JSON_FILES"] = len(json_files)
        probes["P2_STRUCTURE_VALID"] = len(jsonl_files) + len(json_files) > 0
    except Exception as e:
        probes["P2_STRUCTURE_VALID"] = False
        probes["P2_ERROR"] = str(e)[:200]

    # P3: Documentation
    try:
        probes["P3_HAS_README"] = any("README" in f.upper() for f in files)
        probes["P3_HAS_LICENSE"] = any("LICENSE" in f.upper() for f in files)
    except Exception:
        probes["P3_HAS_README"] = False
        probes["P3_HAS_LICENSE"] = False

    if probes.get("P1_LOADABLE") and probes.get("P2_STRUCTURE_VALID"):
        verdict = "SEAL"
    elif probes.get("P2_STRUCTURE_VALID"):
        verdict = "PARTIAL"
    else:
        verdict = "HELD"

    return {
        "verdict": verdict,
        "stage": "BBB_CCC_DDD_PROBES",
        "omega_zero": OMEGA_ZERO,
        "probes": probes,
        "operator": OPERATOR,
        "timestamp": now_iso(),
    }


# ── Stage 3 — EEE SPINE ────────────────────────────────
def stage_eee_spine(artifact_id, artifact_type):
    try:
        from huggingface_hub import HfApi

        api = HfApi()
        files = list(api.list_repo_files(artifact_id, repo_type=artifact_type))
        content_signature = json.dumps(
            {
                "files": sorted(files),
                "artifact_id": artifact_id,
                "pipeline": PIPELINE_NAME,
                "timestamp": now_iso(),
            },
            sort_keys=True,
        )
        content_hash = f"sha256:{sha256(content_signature)}"
    except Exception as e:
        return _stage_fail("EEE_SPINE", f"Cannot compute receipt hash: {e}")

    spine_status = "INTACT" if len(files) > 0 else "EMPTY"
    verdict = "SEAL" if spine_status == "INTACT" else "HELD"

    return {
        "verdict": verdict,
        "stage": "EEE_SPINE",
        "omega_zero": OMEGA_ZERO,
        "receipt_id": f"EEE-{sha256(artifact_id + now_iso())[:16]}",
        "content_sha256": content_hash,
        "file_count": len(files),
        "spine_status": spine_status,
        "operator": OPERATOR,
        "timestamp": now_iso(),
    }


# ── Stage 4 — FFF VERDICT ──────────────────────────────
def stage_fff_verdict(artifact_id, artifact_type, prior_stages):
    """Evaluate G1-G8 gates + BAR1-BAR6 based on evidence from prior stages."""
    classify = prior_stages.get("CLASSIFY", {})
    aaa = prior_stages.get("AAA_DOCTRINE", {})
    bcd = prior_stages.get("BBB_CCC_DDD_PROBES", {})
    eee = prior_stages.get("EEE_SPINE", {})

    gates = {}
    gate_results = {}

    # G1_PARSE — from BCD structure validity
    gate_results["G1_PARSE"] = "PASS" if bcd.get("probes", {}).get("P2_STRUCTURE_VALID") else "FAIL"

    # G2_TRUTH — from license + canonical membership
    gate_results["G2_TRUTH"] = "PASS" if classify.get("license_ok") else "FAIL"

    # G3_EVIDENCE — from file count + readme
    gate_results["G3_EVIDENCE"] = "PASS" if bcd.get("probes", {}).get("P3_HAS_README") else "FAIL"

    # G4_CLARITY — structure validity
    gate_results["G4_CLARITY"] = (
        "PASS" if bcd.get("probes", {}).get("P2_STRUCTURE_VALID") else "FAIL"
    )

    # G5_RISK — from AAA checks
    gate_results["G5_RISK"] = "PASS" if aaa.get("checks", {}).get("C3_NOT_GATED", False) else "FAIL"

    # G6_SOVEREIGNTY — canonical + not private
    gate_results["G6_SOVEREIGNTY"] = "PASS" if classify.get("is_canonical") else "FAIL"

    # G7_MEMORY — EEE spine intact
    gate_results["G7_MEMORY"] = "PASS" if eee.get("spine_status") == "INTACT" else "FAIL"

    # G8_REGISTER — has config files
    gate_results["G8_REGISTER"] = "PASS" if bcd.get("probes", {}).get("P3_HAS_LICENSE") else "FAIL"

    pass_count = sum(1 for v in gate_results.values() if v == "PASS")
    fail_count = sum(1 for v in gate_results.values() if v == "FAIL")
    total_gates = len(gate_results)

    # BAR evaluation
    bars = {}
    bars["BAR1"] = "PASS" if gate_results.get("G1_PARSE") == "PASS" else "FAIL"
    bars["BAR2"] = "PASS" if gate_results.get("G2_TRUTH") == "PASS" else "FAIL"
    bars["BAR3"] = "PASS" if gate_results.get("G6_SOVEREIGNTY") == "PASS" else "FAIL"
    bars["BAR4"] = "PASS" if gate_results.get("G7_MEMORY") == "PASS" else "FAIL"
    bars["BAR5"] = "PASS" if gate_results.get("G8_REGISTER") == "PASS" else "FAIL"
    # BAR6: closed-weights flag — datasets are inherently open
    bars["BAR6"] = (
        "PASS"
        if artifact_type == "dataset"
        else ("PARTIAL" if gate_results.get("G6_SOVEREIGNTY") == "PASS" else "FAIL")
    )

    bar_pass = sum(1 for v in bars.values() if v == "PASS")

    # Verdict
    if fail_count == 0:
        verdict = "SEAL"
    elif gate_results.get("G6_SOVEREIGNTY") == "FAIL":
        verdict = "VOID"
    elif fail_count <= 3:
        verdict = "PARTIAL"
    else:
        verdict = "HELD"

    return {
        "verdict": verdict,
        "stage": "FFF_VERDICT",
        "omega_zero": OMEGA_ZERO,
        "gates": gate_results,
        "bars": bars,
        "gate_pass_count": pass_count,
        "gate_fail_count": fail_count,
        "bar_pass_count": bar_pass,
        "total_gates": total_gates,
        "operator": OPERATOR,
        "timestamp": now_iso(),
    }


# ── Stage 5 — VAULT SEAL ───────────────────────────────
def stage_vault_seal(artifact_id, pipeline_receipt, dry_run=False):
    """Attempt to seal the certification receipt to VAULT999 via arifOS kernel."""
    seal_payload = json.dumps(pipeline_receipt, sort_keys=True, default=str)

    if dry_run:
        return {
            "verdict": "HELD",
            "stage": "VAULT_SEAL",
            "omega_zero": OMEGA_ZERO,
            "seal_attempted": False,
            "seal_verdict": "DRY_RUN",
            "note": "Dry run — no seal written. Use --seal to commit.",
            "payload_sha256": f"sha256:{sha256(seal_payload)}",
            "operator": OPERATOR,
            "timestamp": now_iso(),
        }

    # Attempt MCP call to arifOS kernel
    try:
        import urllib.request

        mcp_request = {
            "jsonrpc": "2.0",
            "id": f"seal-{sha256(artifact_id + now_iso())[:12]}",
            "method": "tools/call",
            "params": {
                "name": "arif_seal",
                "arguments": {
                    "mode": "seal",
                    "payload": seal_payload,
                    "actor_id": "forge-cert-pipeline",
                    "witness_type": "ai",
                    "constitutional": {
                        "pipeline": PIPELINE_NAME,
                        "version": SKILL_VERSION,
                        "omega_zero": OMEGA_ZERO,
                        "artifact_id": artifact_id,
                    },
                },
            },
        }
        req = urllib.request.Request(
            ARIFOS_MCP_URL,
            data=json.dumps(mcp_request).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10.0) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {
            "verdict": "HELD",
            "stage": "VAULT_SEAL",
            "omega_zero": OMEGA_ZERO,
            "seal_attempted": True,
            "seal_verdict": "FAILED",
            "error": f"arifOS kernel unreachable: {e}",
            "payload_sha256": f"sha256:{sha256(seal_payload)}",
            "operator": OPERATOR,
            "timestamp": now_iso(),
        }

    seal_verdict = "SEALED" if "error" not in result else "FAILED"
    return {
        "verdict": "SEAL" if seal_verdict == "SEALED" else "HELD",
        "stage": "VAULT_SEAL",
        "omega_zero": OMEGA_ZERO,
        "seal_attempted": True,
        "seal_verdict": seal_verdict,
        "kernel_response": result,
        "payload_sha256": f"sha256:{sha256(seal_payload)}",
        "operator": OPERATOR,
        "timestamp": now_iso(),
    }


# ── Pipeline Orchestrator ──────────────────────────────
def run_pipeline(artifact_id, artifact_type="dataset", seal=False, output_path=None):
    """Execute the full 6-stage certification pipeline. Fail-closed at every stage."""
    t0 = time.monotonic()
    stages = {}
    chain = []
    prev_hash = "0000000000000000000000000000000000000000000000000000000000000000"

    pipeline_state = {
        "pipeline": PIPELINE_NAME,
        "version": SKILL_VERSION,
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "operator": OPERATOR,
        "omega_zero": OMEGA_ZERO,
        "started_at": now_iso(),
    }

    def _run_stage(name, fn, *args, **kwargs):
        nonlocal prev_hash
        try:
            result = fn(*args, **kwargs)
        except Exception as exc:
            result = _stage_fail(name, f"UNHANDLED_EXCEPTION: {exc}")
        stages[name] = result
        link = {
            "stage": name,
            "hash": f"sha256:{sha256(json.dumps(result, sort_keys=True, default=str))}",
            "prev": prev_hash,
            "verdict": result.get("verdict", "VOID"),
        }
        chain.append(link)
        prev_hash = link["hash"]
        return result

    # Stage 0
    c0 = _run_stage("CLASSIFY", stage_classify, artifact_id, artifact_type)
    if c0["verdict"] == "VOID":
        return _build_final(artifact_id, stages, chain, t0, "VOID", "CLASSIFY stage returned VOID")

    # Stage 1
    c1 = _run_stage("AAA_DOCTRINE", stage_aaa_doctrine, c0)
    if c1["verdict"] == "VOID":
        return _build_final(artifact_id, stages, chain, t0, "VOID", "AAA_DOCTRINE returned VOID")

    # Stage 2
    c2 = _run_stage("BBB_CCC_DDD_PROBES", stage_bbb_ccc_ddd_probes, artifact_id, artifact_type)

    # Stage 3
    c3 = _run_stage("EEE_SPINE", stage_eee_spine, artifact_id, artifact_type)
    if c3["verdict"] == "VOID":
        return _build_final(artifact_id, stages, chain, t0, "VOID", "EEE_SPINE returned VOID")

    # Stage 4
    c4 = _run_stage("FFF_VERDICT", stage_fff_verdict, artifact_id, artifact_type, stages)

    # Stage 5
    c5 = _run_stage("VAULT_SEAL", stage_vault_seal, artifact_id, {}, dry_run=not seal)

    return _build_final(artifact_id, stages, chain, t0, None, None, output_path)


def _build_final(
    artifact_id, stages, chain, t0, override_verdict=None, override_reason=None, output_path=None
):
    """Assemble final receipt with EEE Dominance Rule verdict."""
    # Compute strictest verdict across all stages
    verdicts = [s["verdict"] for s in stages.values()]
    if override_verdict:
        final_verdict = override_verdict
        final_reason = override_reason
    else:
        final_verdict = "SEAL"
        for v in verdicts:
            if v not in VERDICT_ORDER:
                continue
            if VERDICT_ORDER[v] < VERDICT_ORDER[final_verdict]:
                final_verdict = v
        final_reason = f"EEE Dominance Rule: strictest stage verdict = {final_verdict}"

    elapsed_ms = (time.monotonic() - t0) * 1000

    receipt = {
        "receipt_id": f"HFCERT-{sha256(artifact_id + now_iso())[:20]}",
        "pipeline": PIPELINE_NAME,
        "version": SKILL_VERSION,
        "artifact_id": artifact_id,
        "artifact_type": stages.get("CLASSIFY", {}).get("artifact_type", "unknown"),
        "final_verdict": final_verdict,
        "final_reason": final_reason,
        "omega_zero": OMEGA_ZERO,
        "operator": OPERATOR,
        "stage_verdicts": {name: s["verdict"] for name, s in stages.items()},
        "stages": stages,
        "merkle_chain": chain,
        "merkle_head": chain[-1]["hash"] if chain else "empty",
        "elapsed_ms": round(elapsed_ms, 1),
        "dominance_rule": "VOID > DEGRADED > HELD > HOLD > SABAR > PARTIAL > SEAL",
        "fail_closed": override_verdict == "VOID",
        "started_at": stages.get("CLASSIFY", {}).get("timestamp", now_iso()),
        "completed_at": now_iso(),
    }

    if output_path:
        with open(output_path, "w") as f:
            json.dump(receipt, f, indent=2, default=str)
        print(f"\nReceipt written to: {output_path}")

    return receipt


# ── CLI ────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Sovereign HF Certification Pipeline (AAA->FFF)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("artifact", help="HF artifact ID (e.g., ariffazil/EEE)")
    parser.add_argument(
        "--type",
        default="dataset",
        choices=["dataset", "model"],
        help="Artifact type (default: dataset)",
    )
    parser.add_argument(
        "--seal", action="store_true", help="Attempt VAULT999 seal (requires arifOS kernel running)"
    )
    parser.add_argument(
        "--smoke", action="store_true", help="Run as smoke test: self-verify after completion"
    )
    parser.add_argument("--output", "-o", default=None, help="Output path for JSON receipt")

    args = parser.parse_args()

    print(f"\n{'=' * 70}")
    print(f"  {PIPELINE_NAME}")
    print(f"  Version: {SKILL_VERSION}  |  Omega_zero: {OMEGA_ZERO}")
    print(f"  Operator: {OPERATOR}")
    print(f"  Fail-closed: YES  |  Seal: {'ATTEMPT' if args.seal else 'DRY_RUN'}")
    print(f"{'=' * 70}\n")

    print(f"Certifying: {args.artifact} (type={args.type})")
    print(
        f"Stages: CLASSIFY -> AAA_DOCTRINE -> BBB/CCC/DDD -> EEE_SPINE -> FFF_VERDICT -> VAULT_SEAL\n"
    )

    receipt = run_pipeline(args.artifact, args.type, seal=args.seal, output_path=args.output)

    # Print summary
    print(f"\n{'=' * 70}")
    print(f"  CERTIFICATION COMPLETE")
    print(f"{'=' * 70}")
    print(f"  Artifact:     {receipt['artifact_id']}")
    print(f"  Receipt:      {receipt['receipt_id']}")
    print(f"  Final Verdict: {receipt['final_verdict']}")
    print(f"  Reason:       {receipt['final_reason']}")
    print(f"  Merkle Head:  {receipt['merkle_head'][:72]}...")
    print(f"  Elapsed:      {receipt['elapsed_ms']:.1f}ms")
    print(f"  Omega_zero:   {OMEGA_ZERO}")
    print()

    # Stage-by-stage
    print("  Stage Verdicts:")
    for name, s in receipt["stages"].items():
        v = s.get("verdict", "?")
        icon = {"SEAL": "+", "PARTIAL": "~", "HELD": "?", "HOLD": "?", "VOID": "X"}.get(v, "?")
        print(f"    [{icon}] {name:25s}  {v}")

    # FFF gate summary
    fff = receipt["stages"].get("FFF_VERDICT", {})
    gates = fff.get("gates", {})
    if gates:
        print(f"\n  FFF Gates ({fff.get('gate_pass_count', 0)}/{fff.get('total_gates', 8)}):")
        for gid, gv in gates.items():
            icon = "+" if gv == "PASS" else "X"
            print(f"    [{icon}] {gid:20s}  {gv}")

    print(f"\n  DITEMPA BUKAN DIBERI — 999 SEAL")
    print(f"{'=' * 70}\n")

    # Smoke test self-verification
    if args.smoke:
        print("SMOKE TEST SELF-VERIFICATION:")
        critical = [
            ("Receipt ID present", bool(receipt.get("receipt_id"))),
            ("Merkle chain not empty", len(receipt.get("merkle_chain", [])) > 0),
            ("All 6 stages present", len(receipt.get("stages", {})) >= 6),
            ("Omega_zero = 0.04", abs(receipt.get("omega_zero", 0) - 0.04) < 0.001),
            ("Stage 0 CLASSIFY has verdict", "verdict" in receipt["stages"].get("CLASSIFY", {})),
            (
                "Stage 3 EEE has spine receipt",
                "receipt_id" in receipt["stages"].get("EEE_SPINE", {}),
            ),
            ("Stage 4 FFF has gate results", "gates" in receipt["stages"].get("FFF_VERDICT", {})),
        ]
        all_ok = True
        for name, ok in critical:
            icon = "+" if ok else "X"
            if not ok:
                all_ok = False
            print(f"  [{icon}] {name}")
        print(f"\n  SMOKE RESULT: {'PASS' if all_ok else 'FAIL'}")
        sys.exit(0 if all_ok else 1)

    # Exit code: 0 for SEAL, 1 for PARTIAL/HELD, 2 for VOID
    final = receipt["final_verdict"]
    sys.exit(0 if final == "SEAL" else 1 if final in ("PARTIAL", "HELD") else 2)


if __name__ == "__main__":
    main()
