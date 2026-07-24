#!/usr/bin/env python3
"""
recursive_governed_loop.py — INIT→SEAL aligned recursive governed agentic intelligence
═══════════════════════════════════════════════════════════════════════════════════════

One path. Two resolutions of the same constitutional geometry:

  11-stage constitutional pipeline (canon):
    000 INIT → 111 SENSE → 222 EVIDENCE → 333 REASON → 444 ROUTE
    → 555 MEMORY → 666 GOVERN → 777 MEASURE → 888 JUDGE → 889 PROOF → 999 SEAL

  5-stage metabolic pump (runtime compression):
    000 PERCEIVE → 444 PROPOSE → 777 EVALUATE → 888 SOVEREIGN → 999 SEAL

Live public tools (MCP / REST):
  arif_init | arif_observe | arif_think | arif_route | arif_critique
  arif_memory | arif_judge | arif_forge | arif_compose | arif_seal | arif_verify

ART → APA → ACT:
  ART  — classify intent (stage 000–444)
  APA  — affordance / permission / authority (actor_verified + arif_verify)
  ACT  — A-FORGE mutate only after 888 SEAL (never before)

Recursive property:
  If judge returns HOLD/SABAR and --recurse, loop returns to PERCEIVE with
  prior receipt as evidence (max depth, ΔS non-increasing budget).

Usage:
  # Dry metabolic pass (no vault write)
  python3 recursive_governed_loop.py --intent "Assess federation readiness"

  # Crypto-bound sovereign session (Ed25519)
  python3 recursive_governed_loop.py --intent "..." --sign-sovereign

  # Allow VAULT append only if judge SEAL and --ack-irreversible
  python3 recursive_governed_loop.py --intent "..." --sign-sovereign --ack-irreversible

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ARIFOS_HTTP = "http://127.0.0.1:8088"
CONSTITUTION_HASH = "arifos-constitution-v2026.05.05-SSCT"
DEFAULT_ACTOR = "arif"
PRIV_KEY_PATH = Path("/root/.secrets/aaa-identity/keys/arif_private.pem")
RECEIPT_DIR = Path("/root/A-FORGE/forge_work")

# ── Stage map: constitutional → live tool ──────────────────────────────────
STAGE_MAP_11 = [
    ("000", "INIT", "arif_init", "Bind identity + session"),
    ("111", "SENSE", "arif_observe", "Observe reality"),
    ("222", "EVIDENCE", "arif_observe", "mode=fetch / organ evidence"),
    ("333", "REASON", "arif_think", "Hypothesis + epistemic tags"),
    ("444", "ROUTE", "arif_route", "Select organ"),
    ("555", "MEMORY", "arif_memory", "Lineage / recall"),
    ("666", "GOVERN", "arif_critique", "F1–F13 / maruah risk"),
    ("777", "MEASURE", "arif_judge", "embedded in judge measurement"),
    ("888", "JUDGE", "arif_judge", "SEAL | HOLD | SABAR | VOID"),
    ("889", "PROOF", "arif_verify", "SEAL token / lease padlock"),
    ("999", "SEAL", "arif_seal", "VAULT999 append"),
]

# Hermes misaligned aliases → canon
ALIAS_FIX = {
    "arif_session_init": "arif_init",
    "arif_vault_seal": "arif_seal",
    "arif_judge_deliberate": "arif_judge",  # public may expose deliberate as alias
    "kernel_route": "arif_route",
    "heart_critique": "arif_critique",
    "evidence_fetch": "arif_observe",
    "agi_reason": "arif_think",
    "memory_recall": "arif_memory",
}


# ── HTTP tool client ───────────────────────────────────────────────────────


def call_tool(name: str, arguments: dict[str, Any], timeout: float = 45.0) -> dict[str, Any]:
    """POST /tools/{name} on local arifOS REST surface."""
    url = f"{ARIFOS_HTTP}/tools/{name}"
    data = json.dumps(arguments).encode()
    req = urllib.request.Request(
        url, data=data, method="POST", headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"http": r.status, "body": json.loads(r.read().decode())}
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode() or "{}")
        except Exception:
            body = {"error": str(e)}
        return {"http": e.code, "body": body}
    except Exception as e:
        return {"http": 0, "body": {"error": str(e)}}


def dig(obj: Any, *keys: str, default: Any = None) -> Any:
    cur = obj
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
    return default if cur is None else cur


def find_key(obj: Any, key: str, depth: int = 0) -> Any:
    if depth > 12 or obj is None:
        return None
    if isinstance(obj, dict):
        if key in obj and obj[key] is not None:
            return obj[key]
        for v in obj.values():
            r = find_key(v, key, depth + 1)
            if r is not None:
                return r
    if isinstance(obj, list):
        for v in obj:
            r = find_key(v, key, depth + 1)
            if r is not None:
                return r
    return None


# ── Entropy / G estimates (honest labels) ──────────────────────────────────


def estimate_g(evidence_n: int, actor_verified: bool, judge_verdict: str | None) -> dict[str, Any]:
    """Bounded ESTIMATE — not a fake physics seal."""
    A = 0.85 if actor_verified else 0.55
    P = min(0.95, 0.5 + 0.08 * evidence_n)
    E = 0.8 if evidence_n >= 2 else 0.5
    X = {"SEAL": 0.9, "HOLD": 0.4, "SABAR": 0.55, "VOID": 0.1}.get(
        (judge_verdict or "HOLD").upper(), 0.4
    )
    Phi = 0.85
    G = A * P * E * X * Phi
    C_dark = A * (1 - P) * (1 - X)
    return {
        "G": round(G, 4),
        "C_dark": round(C_dark, 4),
        "primitives": {"A": A, "P": P, "E": E, "X": X, "Phi": Phi},
        "epistemic": "ESTIMATE",
        "pass_G": G >= 0.80,
        "pass_C": C_dark < 0.30,
    }


# ── Crypto bind ────────────────────────────────────────────────────────────


def sovereign_sign_bind(intent: str) -> dict[str, Any]:
    """000 INIT with Ed25519 challenge-response for actor=arif."""
    from cryptography.hazmat.primitives.serialization import load_pem_private_key

    if not PRIV_KEY_PATH.is_file():
        return {"ok": False, "error": "private_key_missing", "path": str(PRIV_KEY_PATH)}

    priv = load_pem_private_key(PRIV_KEY_PATH.read_bytes(), password=None)

    # Challenge
    r0 = call_tool(
        "arif_init",
        {
            "mode": "init",
            "actor_id": DEFAULT_ACTOR,
            "intent": intent,
            "requested_authority": "OBSERVE_ONLY",
        },
    )
    body0 = r0["body"]
    nonce = find_key(body0, "challenge_nonce") or find_key(body0, "pending_challenge_nonce")
    if not nonce:
        return {
            "ok": False,
            "error": "no_challenge_nonce",
            "http": r0["http"],
            "body_keys": list(body0.keys()) if isinstance(body0, dict) else None,
        }

    sig = base64.b64encode(priv.sign(f"{DEFAULT_ACTOR}:{nonce}".encode())).decode()
    r1 = call_tool(
        "arif_init",
        {
            "mode": "init",
            "actor_id": DEFAULT_ACTOR,
            "intent": intent,
            "nonce": nonce,
            "actor_signature": sig,
            "requested_authority": "SOVEREIGN",
        },
    )
    body1 = r1["body"]
    return {
        "ok": bool(find_key(body1, "actor_verified")),
        "session_id": find_key(body1, "session_id"),
        "actor_verified": find_key(body1, "actor_verified"),
        "authority": find_key(body1, "authority")
        or dig(body1, "result", "authority")
        or find_key(body1, "authority_mode"),
        "agent_class": find_key(body1, "agent_class"),
        "http": r1["http"],
    }


# ── Loop state ─────────────────────────────────────────────────────────────


@dataclass
class StageReceipt:
    stage: str
    name: str
    tool: str
    status: str
    ms: float
    detail: dict[str, Any] = field(default_factory=dict)
    epistemic: str = "CLAIM"


@dataclass
class LoopReceipt:
    intent: str
    started_at: str
    depth: int
    max_depth: int
    session_id: str | None
    actor_verified: bool
    stages: list[StageReceipt] = field(default_factory=list)
    judge_verdict: str | None = None
    seal_attempted: bool = False
    seal_written: bool = False
    g_estimate: dict[str, Any] = field(default_factory=dict)
    next_action: str | None = None
    recursion_reason: str | None = None
    children: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_metabolic_once(
    intent: str,
    *,
    session_id: str | None,
    actor_id: str,
    actor_verified: bool,
    depth: int,
    max_depth: int,
    ack_irreversible: bool,
    allow_seal: bool,
) -> LoopReceipt:
    """One pass of 5-stage metabolic loop mapped to live tools."""
    receipt = LoopReceipt(
        intent=intent,
        started_at=datetime.now(UTC).isoformat(),
        depth=depth,
        max_depth=max_depth,
        session_id=session_id,
        actor_verified=actor_verified,
    )
    evidence_bits: list[str] = []

    def stage(code: str, name: str, tool: str, args: dict, epistemic: str = "CLAIM") -> dict:
        t0 = time.time()
        # inject session if present
        if session_id and "session_id" not in args:
            args = {**args, "session_id": session_id}
        if actor_id and "actor_id" not in args:
            args = {**args, "actor_id": actor_id}
        res = call_tool(tool, args)
        ms = (time.time() - t0) * 1000
        body = res.get("body") or {}
        status = "OK" if res.get("http") in (200, 201) and not dig(body, "error") else "DEGRADED"
        if res.get("http") == 0:
            status = "FAIL"
        # extract useful text/verdict
        detail = {
            "http": res.get("http"),
            "verdict": find_key(body, "verdict") or dig(body, "result", "verdict"),
            "status": dig(body, "status") or find_key(body, "status"),
            "snippet": str(body)[:400],
        }
        receipt.stages.append(
            StageReceipt(
                stage=code,
                name=name,
                tool=tool,
                status=status,
                ms=round(ms, 1),
                detail=detail,
                epistemic=epistemic,
            )
        )
        return body

    # 000 PERCEIVE = INIT (if needed) + OBSERVE
    if not session_id:
        b = stage(
            "000",
            "INIT",
            "arif_init",
            {
                "mode": "light",
                "actor_id": actor_id,
                "intent": intent,
                "requested_authority": "OBSERVE_ONLY",
            },
        )
        session_id = find_key(b, "session_id")
        receipt.session_id = session_id
        av = find_key(b, "actor_verified")
        if av is not None:
            receipt.actor_verified = bool(av)
            actor_verified = bool(av)

    stage(
        "111",
        "SENSE",
        "arif_observe",
        {"mode": "search", "query": intent, "intent": intent},
        epistemic="CLAIM",
    )
    evidence_bits.append("observe")

    # 222 as route to organs for external evidence (GEOX/WELL/WEALTH via route)
    stage(
        "222",
        "EVIDENCE",
        "arif_route",
        {"intent": f"gather evidence for: {intent}"},
        epistemic="PLAUSIBLE",
    )
    evidence_bits.append("route")

    # 444 PROPOSE = THINK + ROUTE
    stage(
        "333",
        "REASON",
        "arif_think",
        {"mode": "reason", "query": intent, "intent": intent},
        epistemic="HYPOTHESIS",
    )
    stage(
        "444",
        "ROUTE",
        "arif_route",
        {"intent": intent},
        epistemic="CLAIM",
    )

    # 777 EVALUATE = MEMORY + CRITIQUE
    stage(
        "555",
        "MEMORY",
        "arif_memory",
        {"mode": "recall", "query": intent},
        epistemic="PLAUSIBLE",
    )
    stage(
        "666",
        "GOVERN",
        "arif_critique",
        {"mode": "critique", "content": intent, "intent": intent},
        epistemic="CLAIM",
    )

    # 888 JUDGE
    judge_body = stage(
        "888",
        "JUDGE",
        "arif_judge",
        {
            "actor": actor_id,
            "intent": intent,
            "requested_capability": "governed_action",
            "domain": "federation",
            "reversibility_level": "reversible",
            "blast_radius": "low",
            "epistemic_state": "HYPOTHESIS",
        },
        epistemic="CLAIM",
    )
    verdict = (
        find_key(judge_body, "verdict")
        or dig(judge_body, "result", "verdict")
        or dig(judge_body, "result", "decision")
        or "HOLD"
    )
    if isinstance(verdict, dict):
        verdict = verdict.get("state") or verdict.get("verdict") or "HOLD"
    verdict = str(verdict).upper()
    # normalize
    for v in ("SEAL", "HOLD", "SABAR", "VOID", "OBSERVE_ONLY"):
        if v in verdict:
            verdict = v
            break
    receipt.judge_verdict = verdict

    # G estimate
    receipt.g_estimate = estimate_g(
        evidence_n=len(evidence_bits),
        actor_verified=actor_verified,
        judge_verdict=verdict,
    )

    # 889 PROOF — padlock existence check (architectural)
    stage(
        "889",
        "PROOF",
        "arif_verify",
        {"token": "SEAL-dry-run", "command": "true", "actor_id": actor_id},
        epistemic="CLAIM",
    )

    # 999 SEAL — only if judge SEAL + G pass + ack
    can_seal = (
        allow_seal
        and ack_irreversible
        and verdict == "SEAL"
        and receipt.g_estimate.get("pass_G")
        and receipt.g_estimate.get("pass_C")
        and actor_verified
    )
    if can_seal:
        receipt.seal_attempted = True
        payload = {
            "intent": intent,
            "depth": depth,
            "g_estimate": receipt.g_estimate,
            "stages": [s.stage for s in receipt.stages],
            "ts": datetime.now(UTC).isoformat(),
        }
        seal_body = stage(
            "999",
            "SEAL",
            "arif_seal",
            {
                "mode": "seal",
                "payload": json.dumps(payload),
                "ack_irreversible": True,
            },
            epistemic="CLAIM",
        )
        receipt.seal_written = bool(
            find_key(seal_body, "sealed")
            or dig(seal_body, "result", "status") in ("OK", "SEALED", "SEAL")
            or find_key(seal_body, "verdict") == "SEAL"
        )
        receipt.next_action = "SEAL_WRITTEN" if receipt.seal_written else "SEAL_FAILED"
    elif verdict == "SEAL" and not ack_irreversible:
        receipt.next_action = "JUDGE_SEAL_NEEDS_ACK — re-run with --ack-irreversible"
    elif verdict in ("HOLD", "SABAR", "OBSERVE_ONLY"):
        receipt.next_action = f"RECURSE_OR_HOLD ({verdict})"
        receipt.recursion_reason = f"judge={verdict}"
    elif verdict == "VOID":
        receipt.next_action = "STOP_VOID"
    else:
        receipt.next_action = f"HOLD_DEFAULT ({verdict})"

    return receipt


def run_recursive(
    intent: str,
    *,
    max_depth: int = 3,
    sign_sovereign: bool = False,
    ack_irreversible: bool = False,
    allow_seal: bool = True,
) -> dict[str, Any]:
    bind: dict[str, Any] = {"ok": False, "skipped": not sign_sovereign}
    session_id = None
    actor_verified = False
    actor_id = DEFAULT_ACTOR

    if sign_sovereign:
        bind = sovereign_sign_bind(intent)
        session_id = bind.get("session_id")
        actor_verified = bool(bind.get("ok") and bind.get("actor_verified"))

    root: LoopReceipt | None = None
    chain: list[dict[str, Any]] = []
    current_intent = intent

    for depth in range(max_depth):
        rec = run_metabolic_once(
            current_intent,
            session_id=session_id,
            actor_id=actor_id,
            actor_verified=actor_verified,
            depth=depth,
            max_depth=max_depth,
            ack_irreversible=ack_irreversible,
            allow_seal=allow_seal,
        )
        session_id = rec.session_id or session_id
        chain.append(rec.to_dict())
        if root is None:
            root = rec
        else:
            root.children.append(rec.to_dict())

        if rec.seal_written or rec.judge_verdict == "VOID":
            break
        if rec.judge_verdict in ("HOLD", "SABAR", "OBSERVE_ONLY") and depth + 1 < max_depth:
            # recurse with refined intent (entropy reduction target)
            current_intent = (
                f"[recursion d={depth + 1} prior={rec.judge_verdict}] "
                f"Refine and re-evaluate: {intent}"
            )
            continue
        break

    # Alignment table for agents
    alignment = {
        "hermes_aliases_fixed": ALIAS_FIX,
        "public_tools": [t for _, _, t, _ in STAGE_MAP_11],
        "constitutional_11": [
            {"stage": a, "name": b, "tool": c, "role": d} for a, b, c, d in STAGE_MAP_11
        ],
        "metabolic_5": {
            "000_PERCEIVE": ["000", "111", "222"],
            "444_PROPOSE": ["333", "444"],
            "777_EVALUATE": ["555", "666", "777"],
            "888_SOVEREIGN": ["888", "889"],
            "999_SEAL": ["999"],
        },
        "art_apa_act": {
            "ART": "000–444 classify + observe + route",
            "APA": "actor_verified + arif_verify padlock + judge floors",
            "ACT": "arif_forge only after SEAL; arif_seal only with ack_irreversible",
        },
    }

    out = {
        "audit": "RecursiveGovernedLoop_v1",
        "executed_at": datetime.now(UTC).isoformat(),
        "intent": intent,
        "sovereign_bind": bind,
        "passes": chain,
        "final_verdict": chain[-1].get("judge_verdict") if chain else None,
        "final_next_action": chain[-1].get("next_action") if chain else None,
        "seal_written": any(p.get("seal_written") for p in chain),
        "alignment": alignment,
        "invariants": {
            "judge_before_seal": True,
            "no_seal_without_ack": not (
                ack_irreversible is False and any(p.get("seal_written") for p in chain)
            ),
            "hermes_not_sovereign": True,
            "delta_S_target": "non-increasing across recursion",
            "G_threshold": 0.80,
            "C_dark_threshold": 0.30,
        },
    }

    day = datetime.now(UTC).strftime("%Y-%m-%d")
    out_path = RECEIPT_DIR / day / "RECURSIVE_GOVERNED_LOOP_RECEIPT.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    out["receipt_path"] = str(out_path)
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Recursive governed INIT→SEAL loop")
    p.add_argument("--intent", required=True, help="Action / question to govern")
    p.add_argument("--max-depth", type=int, default=2, help="Recursion depth cap")
    p.add_argument(
        "--sign-sovereign",
        action="store_true",
        help="Ed25519 bind actor=arif before loop",
    )
    p.add_argument(
        "--ack-irreversible",
        action="store_true",
        help="F13 ack — required for real VAULT999 append",
    )
    p.add_argument(
        "--no-seal",
        action="store_true",
        help="Never call arif_seal (dry constitutional path only)",
    )
    p.add_argument("--json", action="store_true", help="Print full JSON")
    args = p.parse_args()

    result = run_recursive(
        args.intent,
        max_depth=max(1, args.max_depth),
        sign_sovereign=args.sign_sovereign,
        ack_irreversible=args.ack_irreversible,
        allow_seal=not args.no_seal,
    )

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print("RECURSIVE GOVERNED LOOP")
        print(f"  intent:     {result['intent'][:100]}")
        print(
            f"  bind:       {result['sovereign_bind'].get('ok')} verified={result['sovereign_bind'].get('actor_verified')}"
        )
        print(f"  passes:     {len(result['passes'])}")
        print(f"  verdict:    {result['final_verdict']}")
        print(f"  next:       {result['final_next_action']}")
        print(f"  sealed:     {result['seal_written']}")
        print(f"  receipt:    {result['receipt_path']}")
        if result["passes"]:
            last = result["passes"][-1]
            print(f"  G_est:      {last.get('g_estimate')}")
            print("  stages:")
            for s in last.get("stages", []):
                print(f"    {s['stage']} {s['name']:8} {s['tool']:16} {s['status']:8} {s['ms']}ms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
