#!/usr/bin/env python3
"""
judge_eval_run3_verified.py — RUN 3 on the verified path

Sign arif_init with the sovereign key (now ACL-readable by the arifos
user after SEAL-8KERNEL-AUDIT-4a28129) and run the same byte-identical
50-item corpus through arif_judge. Compute the confusion matrix.

The corpus hash and ordering are pinned to the harness's CORPUS list.
Reversible: this script touches only runtime/tools.py patch sites and
/root/forge_work/ outputs.
"""

from __future__ import annotations

import ast
import base64
import json
import os
import re
import sys
import time
import urllib.request
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

sys.path.insert(0, "/root/arifOS/commands/scripts_deploy")
import judge_eval_harness as h  # type: ignore

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

KEY_PATH = "/root/.secrets/jwks/ed25519-private.key"
CONSTITUTION_HASH = "arifos-constitution-v2026.05.05-SSCT"
ACTOR = "ARIF"

# ---------------------------------------------------------------------------
# 1) Verify the corpus is byte-identical to run 1 / run 2.
# ---------------------------------------------------------------------------
_HARNESS = open("/root/arifOS/commands/scripts_deploy/judge_eval_harness.py").read()
_BLOCK = re.search(r"CORPUS:\s*list\[dict\[str,\s*str\]\]\s*=\s*(\[.*?\n\])", _HARNESS, re.S).group(1)
CORPUS = ast.literal_eval(_BLOCK)
assert len(CORPUS) == 50
assert sum(1 for c in CORPUS if c["truth"] == "BLOCK") == 25
assert sum(1 for c in CORPUS if c["truth"] == "PASS") == 25
import hashlib

CORPUS_HASH = hashlib.sha256(
    json.dumps(CORPUS, sort_keys=True, ensure_ascii=False).encode()
).hexdigest()
print(f"[run3] corpus: 50 (25/25) sha256={CORPUS_HASH}")
assert CORPUS_HASH == "9b6185d3b7c77a7bd9bb79986d4b3511c08ad5498c4a7b610898af99eba85389"
print("[run3] corpus hash matches run 1 / run 2 (byte-identical)")


# ---------------------------------------------------------------------------
# 2) Sign arif_init with the sovereign private key (raw 32-byte Ed25519).
# ---------------------------------------------------------------------------
def _sign_init() -> dict[str, Any]:
    raw = open(KEY_PATH, "rb").read()
    assert len(raw) == 32, f"expected 32 raw bytes, got {len(raw)}"
    sk = Ed25519PrivateKey.from_private_bytes(raw)
    nonce = base64.b64encode(os.urandom(16)).decode()
    msg = f"{ACTOR}:{CONSTITUTION_HASH}:{nonce}".encode()
    sig = base64.b64encode(sk.sign(msg)).decode()
    body = {
        "mode": "init",
        "actor_id": ACTOR,
        "ack_irreversible": True,
        "nonce": nonce,
        "actor_signature": sig,
        "intent": "judge_eval_run3 — classify the 50-item corpus on verified path",
        "verbose": "standard",
    }
    r = h._jsonrpc_post("tools/call", {"name": "arif_init", "arguments": body})
    b = r.get("body", {}) or {}
    c = (b.get("result") or {}).get("content") or []
    t = "".join(x.get("text", "") for x in c if x.get("type") == "text")
    try:
        p = json.loads(t)
    except Exception:
        p = {"raw_text": t[:500]}
    return p


# ---------------------------------------------------------------------------
# 3) Per-item arif_judge call signed with the same key, bound to the session.
# ---------------------------------------------------------------------------
VERDICT_TO_BLOCK = {"VOID", "HOLD"}
VERDICT_TO_PASS = {"SEAL", "SABAR"}


def _normalize(verdict: Any) -> str:
    if isinstance(verdict, dict):
        v = verdict.get("state") or verdict.get("verdict") or verdict.get("dominant")
    else:
        v = verdict
    s = (str(v) if v is not None else "").upper()
    if s in VERDICT_TO_BLOCK:
        return "BLOCK"
    if s in VERDICT_TO_PASS:
        return "PASS"
    return "UNKNOWN"


def _judge(sk: Ed25519PrivateKey, session_id: str | None, session_token: str | None, candidate: str) -> dict[str, Any]:
    nonce = base64.b64encode(os.urandom(16)).decode()
    msg = f"{ACTOR}:{CONSTITUTION_HASH}:{nonce}".encode()
    sig = base64.b64encode(sk.sign(msg)).decode()
    args = {
        "mode": "judge",
        "candidate": candidate,
        "actor_id": ACTOR,
        "action_tier": "standard",
        "session_id": session_id,
        "session_token": session_token,
        "nonce": nonce,
        "actor_signature": sig,
    }
    r = h._jsonrpc_post("tools/call", {"name": "arif_judge", "arguments": args})
    if not r.get("_ok"):
        return {"verdict": "MCP_ERROR", "raw": None, "error": r.get("error")}
    jb = r.get("body", {}) or {}
    jc = (jb.get("result") or {}).get("content") or []
    jt = "".join(x.get("text", "") for x in jc if x.get("type") == "text")
    try:
        parsed = json.loads(jt) if jt else {}
    except Exception:
        parsed = {"raw_text": jt}
    inner = (parsed.get("result") if isinstance(parsed, dict) else None) or {}
    verdict = (
        parsed.get("verdict")
        or inner.get("verdict")
        or (parsed.get("status") if isinstance(parsed.get("status"), str) else None)
        or "UNKNOWN"
    )
    return {"verdict": verdict, "raw": parsed, "error": None}


# ---------------------------------------------------------------------------
# 4) Main
# ---------------------------------------------------------------------------
def main() -> int:
    print("\n[run3] signing arif_init with sovereign key…")
    init = _sign_init()
    actor = init.get("actor") or {}
    print(f"  status: {init.get('status')}  verdict: {init.get('verdict')}")
    print(f"  actor_verified: {actor.get('actor_verified')}")
    print(f"  authority_level: {actor.get('authority_level')}")
    sid = init.get("session_id")
    tok = init.get("session_token")
    print(f"  session_id: {sid}  has_token: {bool(tok)}")
    if not tok:
        print("[run3] FAILED: no session_token issued. Cannot proceed to arif_judge.")
        return 1

    # Reload signing key (we used it for init; we need it again for the per-item sig)
    raw = open(KEY_PATH, "rb").read()
    sk = Ed25519PrivateKey.from_private_bytes(raw)

    # Run all 50
    items: list[dict[str, Any]] = []
    for c in CORPUS:
        out = _judge(sk, sid, tok, c["candidate"])
        items.append({
            "id": c["id"],
            "truth": c["truth"],
            "candidate": c["candidate"],
            "predicted": _normalize(out["verdict"]),
            "raw_verdict": out["verdict"],
            "error": out.get("error"),
        })

    tp = fp = tn = fn = unk = 0
    for it in items:
        if it["predicted"] == "UNKNOWN":
            unk += 1
            continue
        if it["truth"] == "BLOCK" and it["predicted"] == "BLOCK":
            tp += 1
        elif it["truth"] == "PASS" and it["predicted"] == "PASS":
            tn += 1
        elif it["truth"] == "BLOCK" and it["predicted"] == "PASS":
            fn += 1
        elif it["truth"] == "PASS" and it["predicted"] == "BLOCK":
            fp += 1

    p = tp / (tp + fp) if (tp + fp) else None
    r = tp / (tp + fn) if (tp + fn) else None
    f = (2 * p * r / (p + r)) if (p is not None and r is not None and (p + r) > 0) else None
    acc = (tp + tn) / max(1, tp + tn + fp + fn)

    # Δ vs run 1
    run1_path = "/root/forge_work/judge_eval_20260801.json"
    run1 = json.load(open(run1_path)) if os.path.exists(run1_path) else None
    run1_by_id = {it["id"]: it for it in (run1 or {}).get("items", [])}
    delta_lines: list[str] = []
    block_changed = 0
    for it in items:
        prev = run1_by_id.get(it["id"], {})
        if prev and prev.get("raw_verdict") != it["raw_verdict"]:
            block_changed += 1 if it["truth"] == "BLOCK" else 0
            delta_lines.append(
                f"  {it['id']}  truth={it['truth']:5s}  run1={prev.get('raw_verdict')!r:24s} → run3={it['raw_verdict']!r}"
            )

    # Wilson 95% lower bound on F1
    def _wilson(s: int, n: int) -> tuple[float, float]:
        if n == 0:
            return (0.0, 0.0)
        z = 1.96
        phat = s / n
        denom = 1 + z * z / n
        centre = (phat + z * z / (2 * n)) / denom
        margin = (z * ((phat * (1 - phat) / n + z * z / (4 * n * n)) ** 0.5)) / denom
        return (max(0.0, centre - margin), min(1.0, centre + margin))

    tp_lo, _ = _wilson(tp, tp + fn)
    fp_total = fp + tn
    fp_lo, _ = _wilson(fp, fp_total) if fp_total else (0.0, 0.0)
    p_lo = (tp_lo) / (tp_lo + fp_lo) if (tp_lo + fp_lo) else None
    r_lo = tp_lo / max(1e-9, (tp + fn))
    f1_lo = (2 * p_lo * r_lo / (p_lo + r_lo)) if (p_lo is not None and r_lo is not None and (p_lo + r_lo) > 0) else None

    report = {
        "schema": "arifos.judge_eval_run3_verified/v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "actor_id": ACTOR,
        "corpus_sha256": CORPUS_HASH,
        "session_id": sid,
        "metrics": {
            "tp": tp, "tn": tn, "fp": fp, "fn": fn, "unknown": unk,
            "precision": p, "recall": r, "f1": f, "accuracy": acc,
            "f1_wilson95_lowerbound": f1_lo,
        },
        "delta_vs_run1": {
            "block_rows_changed": block_changed,
            "items_changed": len(delta_lines),
            "lines": delta_lines,
        },
        "items": items,
    }
    out_path = "/root/forge_work/judge_eval_run3.json"
    json.dump(report, open(out_path, "w"), indent=2, default=str)

    print("\n========== arif_judge RUN 3 (signed, sovereign actor) ==========")
    print(f"  corpus: 50  (25 BLOCK / 25 PASS)  sha256={CORPUS_HASH[:16]}…  IDENTICAL")
    print(f"  actor_verified@init: {actor.get('actor_verified')}")
    print(f"  TP={tp}  TN={tn}  FP={fp}  FN={fn}  UNK={unk}")
    print(f"  precision: {p}    recall: {r}    F1: {f}")
    print(f"  accuracy:   {acc}")
    print(f"  F1 lower 95% Wilson bound: {f1_lo}")
    print(f"  Δ-block-rows-changed (truth=BLOCK): {block_changed}")
    print(f"  Δ-items-changed: {len(delta_lines)}")
    if delta_lines:
        print("  --- verdict changes (run1 → run3) ---")
        for ln in delta_lines[:25]:
            print(ln)
    if r == 0.0:
        print("\nDIAGNOSIS: CLASSIFIER LOGIC ABSENT.")
    print("===============================================================\n")
    print(f"  report → {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
