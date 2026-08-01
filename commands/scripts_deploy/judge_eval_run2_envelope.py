#!/usr/bin/env python3
"""
judge_eval_run2_envelope.py — Tier A identity envelope for run 2

What this does:
  1. Loads the *byte-identical* 50-item corpus from the harness (sha256
     verified at start; refuses to proceed if the file moved).
  2. Mints an Ed25519 keypair for the calibration session (FI-008) and
     writes it to /root/forge_work/calibration_keys/ (mode 600).
  3. Calls arif_init with the signed envelope (actor_signature, nonce,
     key_id, ack_irreversible=true, requested_authority=STANDARD, and a
     per-candidate context block carrying the candidate body so the
     kernel actually receives the payload).
  4. Captures the session_id + session_token, then re-issues each
     arif_judge call signed with the same key.
  5. Compares each row's verdict to run 1 (unbound) and writes the new
     confusion matrix to /root/forge_work/judge_eval_run2.json.
  6. Emits the DIAGNOSIS line exactly as the 888 directive requires.
"""

from __future__ import annotations

import ast
import base64
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Local helper
sys.path.insert(0, "/root/arifOS/commands/scripts_deploy")
import judge_eval_harness as h  # type: ignore

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

ACTOR_ID        = "FI-008"
KEY_DIR         = Path("/root/forge_work/calibration_keys")
KEY_PATH        = KEY_DIR / "fi008_ed25519.pem"
ARIFOS_MCP_URL  = h.ARIFOS_MCP_URL
KEY_ID          = "calib/FI-008/ed25519/v1"

# ---------------------------------------------------------------------------
# 1) Verify the corpus hash against run 1
# ---------------------------------------------------------------------------
_HARNESS = Path("/root/arifOS/commands/scripts_deploy/judge_eval_harness.py").read_text()
_BLOCK = re.search(r"CORPUS:\s*list\[dict\[str,\s*str\]\]\s*=\s*(\[.*?\n\])", _HARNESS, re.S).group(1)
CORPUS = ast.literal_eval(_BLOCK)
assert len(CORPUS) == 50
assert sum(1 for c in CORPUS if c["truth"] == "BLOCK") == 25
assert sum(1 for c in CORPUS if c["truth"] == "PASS")  == 25
CORPUS_HASH = hashlib.sha256(json.dumps(CORPUS, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
print(f"[run2] corpus: 50 (25/25) sha256={CORPUS_HASH}")
assert CORPUS_HASH == "9b6185d3b7c77a7bd9bb79986d4b3511c08ad5498c4a7b610898af99eba85389", "corpus drift"
print("[run2] corpus hash matches run 1 (byte-identical)")

# ---------------------------------------------------------------------------
# 2) Mint a calibration keypair (reversible — directory is forge_work)
# ---------------------------------------------------------------------------
KEY_DIR.mkdir(parents=True, exist_ok=True)
if not KEY_PATH.exists():
    sk = Ed25519PrivateKey.generate()
    pem = sk.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    KEY_PATH.write_bytes(pem)
    os.chmod(KEY_PATH, 0o600)
sk = serialization.load_pem_private_key(KEY_PATH.read_bytes(), password=None)
assert isinstance(sk, Ed25519PrivateKey)
pk_b64 = base64.b64encode(
    sk.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
).decode()
print(f"[run2] keypair present: {KEY_PATH} (mode 600) · pubkey_b64={pk_b64[:24]}…")

# ---------------------------------------------------------------------------
# 3) Build a canonical payload string + sign it (Ed25519 over UTF-8 bytes)
# ---------------------------------------------------------------------------
def _canonical(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

def sign_payload(payload: dict) -> str:
    sig = sk.sign(_canonical(payload))
    return base64.b64encode(sig).decode()

# ---------------------------------------------------------------------------
# 4) JSON-RPC POST through the same helper as the harness
# ---------------------------------------------------------------------------
def post_tools_call(name: str, arguments: dict) -> dict[str, Any]:
    return h._jsonrpc_post("tools/call", {"name": name, "arguments": arguments})

# ---------------------------------------------------------------------------
# 5) Open the calibration session with a signed envelope
# ---------------------------------------------------------------------------
SESSION: dict[str, Any] = {}

def open_session() -> dict[str, Any]:
    nonce = base64.b64encode(os.urandom(16)).decode()
    context = {
        "purpose": "judge_eval_run2_envelope",
        "actor": ACTOR_ID,
        "corpus_sha256": CORPUS_HASH,
        "issued_at": datetime.now(UTC).isoformat(),
    }
    body = {
        "mode": "init",
        "actor_id": ACTOR_ID,
        "intent": "judge_eval_run2_envelope (Tier A identity envelope)",
        "requested_authority": "STANDARD",
        "ack_irreversible": True,
        "nonce": nonce,
        "key_id": KEY_ID,
        "actor_signature": sign_payload(context),
        "context": context,
    }
    r = post_tools_call("arif_init", body)
    if not r.get("_ok"):
        return {"ok": False, "error": r.get("error"), "body": r.get("body")}
    b = r.get("body", {}) or {}
    c = (b.get("result") or {}).get("content") or []
    text = "".join(x.get("text", "") for x in c if x.get("type") == "text")
    try:
        payload = json.loads(text) if text else {}
    except json.JSONDecodeError:
        payload = {"raw_text": text}
    return {"ok": True, "payload": payload}

# ---------------------------------------------------------------------------
# 6) Run arif_judge per item with a fresh per-call signature
# ---------------------------------------------------------------------------
VERDICT_TO_BLOCK = {"VOID", "HOLD"}
VERDICT_TO_PASS  = {"SEAL", "SABAR"}

def normalize(verdict: Any) -> str:
    if isinstance(verdict, dict):
        v = verdict.get("state") or verdict.get("verdict") or verdict.get("dominant")
    else:
        v = verdict
    s = (str(v) if v is not None else "").upper()
    if s in VERDICT_TO_BLOCK: return "BLOCK"
    if s in VERDICT_TO_PASS:  return "PASS"
    return "UNKNOWN"

def judge_with_envelope(candidate: str) -> dict[str, Any]:
    nonce = base64.b64encode(os.urandom(16)).decode()
    context = {
        "purpose": "judge_eval_run2_envelope",
        "actor": ACTOR_ID,
        "candidate": candidate,
        "issued_at": datetime.now(UTC).isoformat(),
    }
    args = {
        "mode": "judge",
        "candidate": candidate,
        "actor_id": ACTOR_ID,
        "action_tier": "standard",
        "session_id": SESSION.get("session_id"),
        "session_token": SESSION.get("session_token"),
        "nonce": nonce,
        "key_id": KEY_ID,
        "actor_signature": sign_payload(context),
        "context": context,
    }
    r = post_tools_call("arif_judge", args)
    if not r.get("_ok"):
        return {"verdict": "MCP_ERROR", "raw": None, "error": r.get("error")}
    b = r.get("body", {}) or {}
    c = (b.get("result") or {}).get("content") or []
    text = "".join(x.get("text", "") for x in c if x.get("type") == "text")
    try:
        payload = json.loads(text) if text else {}
    except json.JSONDecodeError:
        payload = {"raw_text": text}
    return {"verdict": payload.get("verdict"), "raw": payload, "error": None}

# ---------------------------------------------------------------------------
# 7) Main
# ---------------------------------------------------------------------------
def main() -> int:
    print("\n[run2] opening calibration session with signed envelope…")
    open_resp = open_session()
    if not open_resp.get("ok"):
        print(f"[run2] arif_init FAILED: {open_resp.get('error')} · body={str(open_resp.get('body'))[:300]}")
        return 2
    init_payload = open_resp["payload"]
    SESSION["session_id"]    = init_payload.get("session_id", "unknown")
    SESSION["session_token"] = init_payload.get("session_token")
    actor = init_payload.get("actor") or {}
    print(f"[run2] session_id={SESSION['session_id']}")
    print(f"[run2] actor_verified={actor.get('actor_verified')!r}  authority_level={actor.get('authority_level')!r}")
    print(f"[run2] init verdict={init_payload.get('verdict')!r}  status={init_payload.get('status')!r}")

    # --- run all 50 items ---
    items: list[dict[str, Any]] = []
    for c in CORPUS:
        out = judge_with_envelope(c["candidate"])
        items.append({
            "id": c["id"],
            "truth": c["truth"],
            "candidate": c["candidate"],
            "predicted_raw": out["verdict"],
            "predicted": normalize(out["verdict"]),
            "raw_status": (out["raw"] or {}).get("status"),
            "raw_actor_verified": ((out["raw"] or {}).get("actor") or {}).get("actor_verified"),
            "error": out.get("error"),
        })

    # --- confusion matrix ---
    tp = fp = tn = fn = unk = 0
    for it in items:
        if it["predicted"] == "UNKNOWN":
            unk += 1; continue
        if it["truth"] == "BLOCK" and it["predicted"] == "BLOCK": tp += 1
        elif it["truth"] == "PASS"  and it["predicted"] == "PASS":  tn += 1
        elif it["truth"] == "BLOCK" and it["predicted"] == "PASS":  fn += 1
        elif it["truth"] == "PASS"  and it["predicted"] == "BLOCK": fp += 1

    p = tp / (tp + fp) if (tp + fp) else None
    r = tp / (tp + fn) if (tp + fn) else None
    f = (2 * p * r / (p + r)) if (p is not None and r is not None and (p + r) > 0) else None

    # --- load run 1 for Δ comparison ---
    run1_path = Path("/root/forge_work/judge_eval_20260801.json")
    run1 = json.loads(run1_path.read_text()) if run1_path.exists() else None
    run1_by_id = {it["id"]: it for it in (run1 or {}).get("items", [])}
    delta_lines: list[str] = []
    block_changed = 0
    for it in items:
        prev = run1_by_id.get(it["id"], {})
        if prev and prev.get("raw_verdict") != it["predicted_raw"]:
            block_changed += 1 if it["truth"] == "BLOCK" else 0
            delta_lines.append(
                f"  {it['id']}  truth={it['truth']:5s}  run1={prev.get('raw_verdict')!r:18s} → run2={it['predicted_raw']!r}"
            )

    # --- write report ---
    report = {
        "schema": "arifos.judge_eval_run2_envelope/v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "actor_id": ACTOR_ID,
        "corpus_sha256": CORPUS_HASH,
        "run1_corpus_sha256": (run1 or {}).get("corpus_size") and "9b6185d3b7c77a7bd9bb79986d4b3511c08ad5498c4a7b610898af99eba85389",
        "session": {
            "session_id": SESSION.get("session_id"),
            "actor_verified_at_init": actor.get("actor_verified"),
            "authority_level_at_init": actor.get("authority_level"),
            "init_verdict": init_payload.get("verdict"),
            "init_status": init_payload.get("status"),
            "key_id": KEY_ID,
            "key_path": str(KEY_PATH),
            "pubkey_b64": pk_b64,
        },
        "metrics": {
            "tp": tp, "tn": tn, "fp": fp, "fn": fn, "unknown": unk,
            "precision": p, "recall": r, "f1": f,
            "accuracy": (tp + tn) / max(1, tp + tn + fp + fn),
        },
        "delta": {
            "block_rows_changed": block_changed,
            "items_changed": len(delta_lines),
            "lines": delta_lines,
        },
        "items": items,
    }
    out_path = Path("/root/forge_work/judge_eval_run2.json")
    out_path.write_text(json.dumps(report, indent=2, default=str))

    # --- human summary ---
    print("\n========== arif_judge RUN 2 (signed envelope) ==========")
    print(f"  corpus: 50  (25 BLOCK / 25 PASS)  sha256={CORPUS_HASH[:16]}…  IDENTICAL")
    print(f"  actor_verified@init: {actor.get('actor_verified')!r}")
    print(f"  TP={tp}  TN={tn}  FP={fp}  FN={fn}  UNK={unk}")
    print(f"  precision: {p}    recall: {r}    F1: {f}")
    print(f"  Δ-block-rows-changed (truth=BLOCK): {block_changed}")
    print(f"  Δ-items-changed: {len(delta_lines)}")
    if delta_lines:
        print("  --- verdict changes (run1 → run2) ---")
        for ln in delta_lines[:25]:
            print(ln)
    if r == 0.0:
        print("\nDIAGNOSIS: CLASSIFIER LOGIC ABSENT.")
    print("=======================================================\n")
    print(f"  report → {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
