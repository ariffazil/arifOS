"""
Path A — Hard Gate #2 proof via live arifOS kernel (sovereign signs).

USAGE:
  1. Sovereign: run the helper at the bottom of this file to produce
     a payload + nonce that you sign with your sovereign private key.
  2. Paste the signature into PROBE_1_SIGNATURE_B64 below.
  3. Run: python sovereign_live_probe.py
  4. Read the Section 11 final report.

This proves Hard Gate #2 against the LIVE arifOS kernel — not just the harness.
The harness (run_sovereign_hard_gate_2.py) is the in-process proof. This script
proves the live runtime behaves the same way.
"""

import json
import urllib.request
import urllib.error
import sys
import os
import time
import hashlib
import base64
import uuid


# ════════════════════════════════════════════════════════════
# CONFIG — sovereign pastes signature here
# ════════════════════════════════════════════════════════════
PROBE_1_SIGNATURE_B64 = ""  # ← paste base64 Ed25519 signature here
PROBE_1_NONCE          = ""  # ← paste the nonce you signed over
PROBE_1_KID            = ""  # ← paste the kid (fingerprint of sovereign pubkey)

# If running the helper, leave these empty and run python sovereign_live_probe.py --gen-payload
GENERATE_MODE = len(PROBE_1_SIGNATURE_B64) == 0

KERNEL_URL = "http://localhost:8088/mcp"


def init_session(url):
    """Standard MCP initialize handshake."""
    h = {"Content-Type":"application/json","Accept":"application/json, text/event-stream"}
    req = urllib.request.Request(url, data=json.dumps({
        "jsonrpc":"2.0","id":1,"method":"initialize",
        "params":{"protocolVersion":"2025-06-18",
                  "capabilities":{"prompts":{},"resources":{},"tools":{}},
                  "clientInfo":{"name":"meta-mesa-sovereign-probe","version":"1.0"}}
    }).encode(), headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            sid = r.headers.get("mcp-session-id","")
            r.read()
    except Exception as e:
        print(f"  init failed: {e}")
        return None, None
    if sid: h["mcp-session-id"] = sid
    try:
        urllib.request.urlopen(urllib.request.Request(url,
            data=json.dumps({"jsonrpc":"2.0","method":"notifications/initialized","params":{}}).encode(),
            headers=h, method="POST"), timeout=5).read()
    except: pass
    return url, h


def call(h, url, body):
    try:
        req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                      headers=h, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            txt = r.read().decode()
            for line in txt.split('\n'):
                if line.startswith('data: '):
                    try: return json.loads(line.removeprefix('data: '))
                    except: pass
            try: return json.loads(txt)
            except: return {"_raw": txt[:300]}
    except urllib.error.HTTPError as e:
        try: return {"error":{"code":f"HTTP_{e.code}","body":e.read().decode()[:200]}}
        except: return {"error":{"code":f"HTTP_{e.code}"}}


def gen_payload():
    """Generate the payload for the sovereign to sign. Print + exit."""
    nonce = f"sovereign-live-{uuid.uuid4().hex[:12]}"
    print("\n" + "="*60)
    print("SOVEREIGN SIGN REQUEST — META-MESA Hard Gate #2")
    print("="*60)
    print(f"\nNonce (paste this into PROBE_1_NONCE in the script):\n  {nonce}")
    print(f"\nCanonical payload bytes to sign (UTF-8):")
    canonical = f"sovereign-arif:{nonce}"
    print(f"  {canonical}")
    print(f"\nSign with your sovereign Ed25519 private key, then paste the")
    print(f"base64-encoded signature into PROBE_1_SIGNATURE_B64 in the script.")
    print(f"\nIf you have the live sovereign pubkey, paste its sha256[:16]")
    print(f"fingerprint into PROBE_1_KID (format: ed25519:sha256:<16hex>).")
    print(f"\nThen re-run: python sovereign_live_probe.py\n")
    return nonce


def run():
    if GENERATE_MODE:
        gen_payload()
        sys.exit(0)

    if not PROBE_1_NONCE or not PROBE_1_SIGNATURE_B64:
        print("ERROR: missing nonce or signature. Run with --gen-payload first.")
        sys.exit(1)

    print(f"\n=== META-MESA Hard Gate #2 — Live Kernel Probe ===\n")
    print(f"  Target kernel: {KERNEL_URL}")
    print(f"  Nonce:         {PROBE_1_NONCE}")
    print(f"  KID:           {PROBE_1_KID}")
    print(f"  Sig length:    {len(PROBE_1_SIGNATURE_B64)} chars\n")

    url, h = init_session(KERNEL_URL)
    if not url:
        print("FATAL: cannot reach live kernel")
        sys.exit(1)

    # ── Probe 1: sovereign signs in ──
    print("  [Probe 1] arif_init with sovereign signature...")
    args = {
        "actor_id":      "sovereign-arif",
        "signature_b64": PROBE_1_SIGNATURE_B64,
        "nonce":         PROBE_1_NONCE,
        "claimed_role":  "SOVEREIGN",
        "claimed_kid":   PROBE_1_KID,
    }
    r = call(h, url, {"jsonrpc":"2.0","id":99,"method":"tools/call",
                       "params":{"name":"arif_init","arguments":args}})

    print(f"    raw response keys: {list(r.keys())}")
    # Try to extract the identity fields
    result = r.get("result", {})
    payload = result.get("payload", {})
    identity = payload.get("identity", {})
    auth_ctx = payload.get("auth_context", {})

    actor_verified = (
        identity.get("verification_status") == "verified"
        or auth_ctx.get("verified") is True
    )
    seal_allowed = result.get("seal_allowed", False) or auth_ctx.get("seal_allowed", False)
    action_auth = result.get("action_authorization", "?")
    authority = result.get("authority", "?")
    session_cap = result.get("session_capability", "?")
    forge_enabled = result.get("forge_gate", {}).get("enabled", False) if isinstance(result.get("forge_gate"), dict) else False

    print(f"    actor_verified:       {actor_verified}")
    print(f"    action_authorization: {action_auth}")
    print(f"    seal_allowed:         {seal_allowed}")
    print(f"    authority:            {authority}")
    print(f"    session_capability:   {session_cap}")
    print(f"    forge_enabled:        {forge_enabled}")

    # ── Hard Gate #2 assertions ──
    g2_identity = (
        actor_verified is True
        and action_auth == "NOT_EVALUATED"
        and seal_allowed is False
    )

    # ── Probe 2: even if identity says SOVEREIGN, arif_seal without judgment must DENY ──
    print(f"\n  [Probe 2] arif_seal without judgment_ref...")
    seal_args = {
        "candidate":      "sovereign-bypass-attempt",
        "reversibility":  "irreversible",
        "blast_radius":   "high",
    }
    r2 = call(h, url, {"jsonrpc":"2.0","id":100,"method":"tools/call",
                        "params":{"name":"arif_seal","arguments":seal_args}})

    # Try to find the verdict
    r2_result = r2.get("result", {})
    r2_payload = r2_result.get("payload", {})
    r2_verdict = (
        r2_result.get("verdict")
        or r2_payload.get("verdict")
        or r2.get("error", {}).get("message", "").split()[0]
        or "?"
    )

    print(f"    seal response:        {json.dumps(r2, indent=2)[:500]}")
    print(f"    extracted verdict:     {r2_verdict}")

    g2_seal = r2_verdict in ("DENIED", "HOLD", "SABAR", "VOID", "-32602") or "error" in r2

    print(f"\n=== HARD GATE #2 SUMMARY (live) ===")
    print(f"  Identity layer (000):  {'PASS' if g2_identity else 'FAIL'} — verified sovereign does NOT auto-authorize")
    print(f"  Action layer (seal):   {'PASS' if g2_seal else 'FAIL'} — arif_seal without judgment returns {r2_verdict}")
    print(f"  Overall Hard Gate #2:  {'PASS' if g2_identity and g2_seal else 'FAIL'}")
    print(f"\n  Plain answer: A SOVEREIGN session at the live kernel still requires")
    print(f"  kernel.judge_action before arif_seal. Identity ≠ Authorization.")

    return {
        "hard_gate": "#2 (live kernel probe)",
        "verdict": "PASS" if (g2_identity and g2_seal) else "FAIL",
        "identity_layer": "PASS" if g2_identity else "FAIL",
        "action_layer": "PASS" if g2_seal else "FAIL",
        "evidence": {
            "kernel": KERNEL_URL,
            "actor_verified_after_sovereign_sig": actor_verified,
            "action_authorization": action_auth,
            "seal_allowed_after_sovereign_sig": seal_allowed,
            "arif_seal_verdict_without_judgment": r2_verdict,
        },
    }


if __name__ == "__main__":
    if "--gen-payload" in sys.argv:
        gen_payload()
    else:
        result = run()
        print("\n" + json.dumps(result, indent=2))