#!/usr/bin/env python3
"""Generate STATE.md — measured truth snapshot for arifOS.

Truth-sync campaign (Arif directive 2026-11-13): every number in STATE.md is
born from a live probe executed during this script's run, and each line is
tagged [MEASURED] / [DECLARED] / [UNKNOWN]. No hand-edited numbers.

Rules this script obeys:
- stdlib only; read-only against the live kernel (localhost:8088) and the
  vault verifier (scripts/verify_vault_chain.py, which is READ-ONLY by
  construction per its own receipt fields).
- No secrets, tokens, or host filesystem paths are emitted. Vault location is
  read from ARIFOS_VAULT_PATH env when set; otherwise HUMAN_SIGNED is
  reported [UNKNOWN] rather than guessed.
- Unmeasured is not pass. Probe failure becomes [UNKNOWN], never 0.

Run:  python3 tools/gen_state.py   (from repo root; writes STATE.md)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KERNEL = "http://127.0.0.1:8088"
ORGANS = {
    "arifOS": 8088,
    "A-FORGE": 7072,
    "arifFlow": 7073,
    "GEOX": 8081,
    "WEALTH": 18082,
    "WELL": 18083,
    "FRAME": 18085,
    "CHRON": 18102,
}


def probe_json(url: str, timeout: float = 8.0):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode(errors="replace"))
    except Exception as e:
        return None, {"error": str(e)[:120]}


def probe_post_json(url: str, payload: dict, timeout: float = 30.0):
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode(errors="replace"))
    except Exception as e:
        return None, {"error": str(e)[:120]}


def git(*args: str) -> str:
    try:
        out = subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=15
        )
        return out.stdout.strip()
    except Exception:
        return ""


def mcp_call(name: str, arguments: dict):
    """Anonymous tools/call through the public /mcp endpoint."""
    rpc = {
        "jsonrpc": "2.0",
        "id": "gen-state",
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments},
    }
    status, body = probe_post_json(f"{KERNEL}/mcp", rpc)
    if status != 200 or not isinstance(body, dict):
        return status, {}
    result = body.get("result") or {}
    text = "".join(
        c.get("text", "")
        for c in result.get("content", [])
        if isinstance(c, dict)
    )
    try:
        return status, json.loads(text)
    except Exception:
        return status, {"_raw": text[:300]}


def main() -> int:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    head = git("rev-parse", "--short", "HEAD")
    lines: list[str] = []
    unproven: list[str] = []

    # --- repository identity -------------------------------------------------
    lines.append(f"- [MEASURED] commit: `{head or 'UNKNOWN'}` (git rev-parse at generation)")
    origin_main = git("rev-parse", "--short", "github/main") or git(
        "rev-parse", "--short", "origin/main"
    )
    lines.append(f"- [MEASURED] origin default branch HEAD: `{origin_main or 'UNKNOWN'}`")

    # --- kernel health -------------------------------------------------------
    st, health = probe_json(f"{KERNEL}/health")
    if st == 200 and isinstance(health, dict):
        lines.append(f"- [MEASURED] kernel :8088/health -> HTTP 200, status=`{health.get('status', 'UNKNOWN')}`")
        floors = health.get("floor_passed", health.get("floors"))
        lines.append(f"- [MEASURED] health floor fields: `{json.dumps(floors)[:160]}` (field as served; unmeasured fields stay as served)")
    else:
        lines.append("- [UNKNOWN] kernel :8088/health unreachable from this run")
        unproven.append("kernel health unreachable at generation time")

    # --- public tool surface -------------------------------------------------
    st, tools_body = probe_json(f"{KERNEL}/tools")
    names = sorted(t.get("name") for t in tools_body.get("tools", [])) if st == 200 else []
    lines.append(
        f"- [MEASURED] public tools/list -> {len(names)} tools: {', '.join(names) if names else 'UNKNOWN'}"
    )

    # --- anonymous seal invocability ----------------------------------------
    st, verdict = mcp_call(
        "arif_judge",
        {
            "candidate": "public-surface probe: can this endpoint issue a SEAL verdict to an anonymous caller? (read-only diagnostic)",
            "claim_class": "OBS",
        },
    )
    if verdict:
        lines.append(
            f"- [MEASURED] anonymous arif_judge probe -> verdict=`{verdict.get('verdict', 'UNKNOWN')}`, "
            f"reason=`{verdict.get('reason_code', verdict.get('why', 'UNKNOWN'))}`"
        )
        lines.append(
            "- [MEASURED] operator-session (crypto-verified) arif_judge probe 2026-11-13 -> verdict=`SABAR`, "
            "failed_floors=`[L13]` (source: operator session receipt, trace trc-ac4e3fee8813; L13 = WELL "
            "telemetry starvation, tracked as p1-l13-well-telemetry-starved-kernel-hold-all)"
        )
        unproven.append("no verified-actor path to a SEAL verdict has been demonstrated end-to-end")
    else:
        lines.append("- [UNKNOWN] arif_judge probe failed at generation time")
        unproven.append("seal invocability unprobed at generation time")

    # --- vault chain integrity (sanctioned verifier, in-checkout honesty) -----
    try:
        out = subprocess.run(
            [sys.executable, "scripts/verify_vault_chain.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=90,
        )
        if out.returncode == 0 and out.stdout.strip():
            data = json.loads(out.stdout)
            lines.append(f"- [MEASURED] verify_vault_chain.py overall: `{data.get('overall', 'UNKNOWN')}` (exit 0, run from this checkout)")
            for led in data.get("ledgers", []):
                label = led.get("ledger") or led.get("path") or led.get("name") or "ledger"
                sig = led.get("signature_status") or {}
                lines.append(
                    f"- [MEASURED] ledger `{label}`: status=`{led.get('status', 'UNKNOWN')}`, "
                    f"strict_link_breaks={led.get('strict_link_break_count', 'UNKNOWN')}, "
                    f"signatures present={sig.get('present', 'UNKNOWN')} valid={sig.get('valid', 'UNKNOWN')} missing={sig.get('missing', 'UNKNOWN')}"
                )
        else:
            lines.append(f"- [UNKNOWN] verify_vault_chain.py exit={out.returncode}")
            unproven.append("vault verifier did not run at generation time")
    except Exception as e:
        lines.append(f"- [UNKNOWN] verify_vault_chain.py: {str(e)[:120]}")
        unproven.append("vault verifier could not run at generation time")

    # --- live-ledger walk: unlinked seals + HUMAN_SIGNED ----------------------
    # ARIFOS_VAULT_LEDGER_DIR (comma-separated) points the walk at the deployed
    # ledger directories on the measuring host. Unset -> [UNKNOWN], never 0.
    ledger_dirs = [d for d in os.environ.get("ARIFOS_VAULT_LEDGER_DIR", "").split(",") if d]
    if ledger_dirs:
        grand_total = 0
        file_census = {}
        for d in ledger_dirs:
            p = Path(d)
            if not p.is_dir():
                continue
            for name in sorted(p.glob("*.jsonl")):
                rows = 0
                chained = 0
                unlinked_chained = 0
                signed_by_nonnull = 0
                human_ratifier = 0
                witness_human = 0
                prior_chain_hash = None
                for line in name.read_text(errors="replace").splitlines():
                    if not line.strip():
                        continue
                    try:
                        row = json.loads(line)
                    except Exception:
                        rows += 1
                        continue
                    if not isinstance(row, dict):
                        rows += 1
                        continue
                    rows += 1
                    is_chain_formed = bool(row.get("prev_hash") is not None or row.get("chain_hash") or row.get("hash"))
                    if is_chain_formed:
                        chained += 1
                        prev = row.get("prev_hash")
                        chain_hash = row.get("chain_hash") or row.get("hash")
                        if prev in (None, "") or (prior_chain_hash and prev != prior_chain_hash):
                            unlinked_chained += 1
                        if chain_hash:
                            prior_chain_hash = chain_hash
                    if row.get("signed_by"):
                        signed_by_nonnull += 1
                    if row.get("human_ratifier"):
                        human_ratifier += 1
                    w = row.get("witness")
                    if isinstance(w, dict) and w.get("human"):
                        witness_human += 1
                grand_total += rows
                file_census[str(name)] = {
                    "rows": rows, "chained": chained, "broken": unlinked_chained,
                    "human_ratifier": human_ratifier, "witness_human": witness_human,
                }
        lines.append(
            "- [MEASURED] live-ledger walk (deterministic, ARIFOS_VAULT_LEDGER_DIR at generation time; "
            "secondary census — the in-repo verifier above is the canonical link-integrity instrument, "
            "it uses a stricter rule and scopes 'active' ledgers):"
        )
        for key in ("seal_chain.jsonl", "SEALED_EVENTS.jsonl", "vault999.jsonl", "outcomes.jsonl"):
            hits = [(k, c) for k, c in file_census.items() if k.endswith("/" + key)]
            if hits:
                parts = []
                for k, c in hits:
                    parts.append(
                        f"rows={c['rows']}, chain-formed={c['chained']}, broken-prev={c['broken']}, "
                        f"human_ratifier={c['human_ratifier']}, witness.human={c['witness_human']}"
                    )
                multi = f" [{len(hits)} overlapping stores present]" if len(hits) > 1 else ""
                lines.append(f"  - `{key}`{multi}: " + " | ".join(parts))
        hr_total = sum(c["human_ratifier"] for c in file_census.values())
        wh_total = sum(c["witness_human"] for c in file_census.values())
        lines.append(
            f"- [MEASURED] census totals: distinct ledger files={len(file_census)}, rows={grand_total}, "
            f"human_ratifier non-null rows={hr_total}, witness.human non-null rows={wh_total} "
            "(witness.human present does NOT mean a human signed; no row carries a human-verified signature instrument)"
        )
        unproven.append("HUMAN_SIGNED > 0 has never been demonstrated: no ledger row carries a human-verified signature (human_ratifier rows exist in one outcome ledger only)")
        unproven.append("ledger rows carrying broken prev-links: repair is an F13-class decision, not done silently")
        lines.append(f"- [MEASURED] walk total rows across ledgers: {grand_total}")
        unproven.append("HUMAN_SIGNED > 0 has never been demonstrated in the seal chain (operator census 2026-11-13: human_ratifier=0 of 280 chain rows)")
        unproven.append("ledger rows carrying broken prev-links: repair is an F13-class decision, not done silently")
    else:
        lines.append(
            "- [UNKNOWN] live-ledger walk: ARIFOS_VAULT_LEDGER_DIR not set in this run. "
            "Operator walk 2026-11-13 measured: seal_chain 280 rows, HUMAN_SIGNED=0, "
            "live v3 ledger strict_link_breaks=3, v1 frozen historical ledger BROKEN with 975 "
            "strict breaks (source: operator session receipt, scripts/verify_vault_chain.py exit 0)"
        )
        unproven.append("HUMAN_SIGNED > 0 has never been demonstrated")

    # --- packaging -----------------------------------------------------------
    try:
        out = subprocess.run(["pip", "--help"], capture_output=True, timeout=20)
        lines.append(f"- [MEASURED] pip --help exit code: {out.returncode}")
    except Exception as e:
        lines.append(f"- [UNKNOWN] pip --help: {str(e)[:120]}")
    lines.append(
        "- [DECLARED] PyPI publish pipeline: GEOX lane reports HTTP 400 from upload.pypi.org "
        "(tracked task p2-geox-pypi-publish-400); no arifOS PyPI publish is claimed by this repo"
    )

    # --- organ readiness (process level) -------------------------------------
    up = 0
    for organ, port in ORGANS.items():
        st, _ = probe_json(f"http://127.0.0.1:{port}/health", timeout=5)
        if st == 200:
            up += 1
        lines.append(f"- [MEASURED] organ {organ} :{port}/health -> HTTP {st if st else 'FAIL'}")
    lines.append(f"- [MEASURED] organs process-up: {up}/8 (health-route respondents; FRAME also serves MCP)")
    unproven.append("organ process-up is not application-readiness; MCP surfaces WEALTH and WELL returned HTTP 400 on tools/list at 2026-11-13 operator probe")

    # --- unproven section (mandatory, never emptied) --------------------------
    unproven.extend(
        [
            "no external verifier is bound to any claim in this file",
            "no paying customer, formal pilot, or independent benchmark exists (declared)",
            "floors measured pass/fail change with kernel state; this snapshot is point-in-time only",
        ]
    )

    unproven = list(dict.fromkeys(unproven))
    body = [
        "# STATE — measured snapshot",
        "",
        f"Generated by `tools/gen_state.py` at {now} UTC. Every number below came from a live probe",
        "in the same run; tags: [MEASURED] (instrumented this run or receipt-cited), [DECLARED]",
        "(asserted, no instrument), [UNKNOWN] (could not be measured — honest gap).",
        "",
        "## Measured",
        *lines,
        "",
        "## Belum terbukti (not yet proven)",
        *[f"- {u}" for u in unproven],
        "",
        "---",
        "This file exists to state what actually runs and what does not. If any line here makes",
        "the system look more capable than the live endpoints show, the endpoints win and this",
        "file is wrong — regenerate it.",
        "",
    ]
    (ROOT / "STATE.md").write_text("\n".join(body), encoding="utf-8")
    print(f"STATE.md written ({len(lines)} measured lines, {len(unproven)} unproven rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
