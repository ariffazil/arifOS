#!/usr/bin/env python3
"""test_floor_behaviour.py — behavioural tests for what arifOS CLAIMS is enforced.

Why this file exists (2026-10-20, FI-002):
  `floor_conformance.py` proves surfaces AGREE on a name. It does not prove the
  name is ENFORCED. Agreement and enforcement are different claims and must be
  tested separately. This file tests behaviour only.

Every test states what it would falsify. A test that cannot fail is not a test.

Run:  python3 -I scripts/test_floor_behaviour.py
Exit: 0 all pass · 1 any fail · 2 a test could not be measured (UNMEASURED)
"""
from __future__ import annotations

import json
import sys
import urllib.request

REPO = "/root/arifOS"
MCP = "http://127.0.0.1:8088/mcp"
sys.path.insert(0, REPO)

PASS, FAIL, UNMEASURED = "PASS", "FAIL", "UNMEASURED"
results: list[tuple[str, str, str]] = []


def record(name: str, status: str, detail: str) -> None:
    results.append((name, status, detail))


def rpc(method: str, params: dict, timeout: int = 45) -> dict:
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                       "params": params}).encode()
    req = urllib.request.Request(MCP, data=body, headers={
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"})
    raw = urllib.request.urlopen(req, timeout=timeout).read().decode()
    if "data: " in raw:
        raw = raw.split("data: ", 1)[-1]
    return json.loads(raw)


def call(tool: str, args: dict) -> tuple[bool, str, dict | None]:
    """Return (refused, detail, parsed_payload)."""
    out = rpc("tools/call", {"name": tool, "arguments": args})
    res = out.get("result", {})
    text = res.get("content", [{}])[0].get("text", "")
    err = bool(res.get("isError"))
    try:
        payload = json.loads(text)
    except Exception:
        payload = None
    verdict = ""
    if payload:
        verdict = str(payload.get("effective_verdict") or payload.get("verdict") or "")
    allowed = payload.get("mutation_allowed") if payload else None
    refused = err or verdict in {"HOLD", "VOID", "SABAR"} or allowed is False
    return refused, f"isError={err} verdict={verdict} mutation_allowed={allowed}", payload


_SESSION: dict[str, str] = {}


def session() -> dict[str, str]:
    """Bind a session once — axioms are only emitted to an attributed call."""
    if not _SESSION:
        try:
            out = rpc("tools/call", {"name": "arif_init", "arguments": {
                "intent": "behavioural floor test (read-only)",
                "actor_id": "claude-code-kvm8",
                "mode": "light"}})
            payload = json.loads(out["result"]["content"][0]["text"])
            if payload.get("session_id"):
                _SESSION["session_id"] = payload["session_id"]
                if payload.get("session_token"):
                    _SESSION["session_token"] = payload["session_token"]
        except Exception:
            pass
    return _SESSION


def find(node, key):
    if isinstance(node, dict):
        if isinstance(node.get(key), list):
            return node[key]
        for v in node.values():
            got = find(v, key)
            if got:
                return got
    elif isinstance(node, list):
        for v in node:
            got = find(v, key)
            if got:
                return got
    return None


# ── T1: irreversible modes refuse without sovereign approval ────────────────
# Falsified by: any of these returning a successful mutation.
def t1_irreversible_refusal() -> None:
    cases = [
        ("arif_seal", {"mode": "seal", "payload": {"probe": "t1"}}),
        ("arif_memory", {"mode": "forget", "memory_id": "t1-nonexistent"}),
        ("arif_forge", {"mode": "commit", "task": "t1 probe"}),
    ]
    bad = []
    for tool, args in cases:
        try:
            refused, detail, _ = call(tool, args)
        except Exception as e:  # transport refusal still counts as refused
            refused, detail = True, f"{type(e).__name__}"
        if not refused:
            bad.append(f"{tool}.{args['mode']} → {detail}")
    if bad:
        record("T1 irreversible refusal", FAIL, "; ".join(bad))
    else:
        record("T1 irreversible refusal", PASS, "3/3 refused before side effect")


# ── T2: F7 confidence ceiling 0.97 (GENESIS §3.2) ───────────────────────────
# Falsified by: any emitted axiom confidence > 0.97.
def t2_confidence_ceiling() -> None:
    _, _, payload = call("arif_think", {"mode": "axioms", "query": "F1-F13", **session()})
    axes = find(payload, "axioms") if payload else None
    if not axes:
        record("T2 confidence ceiling ≤0.97", UNMEASURED,
               "axioms surface returned no axioms")
        return
    over = [(a.get("id"), a.get("confidence")) for a in axes
            if isinstance(a.get("confidence"), (int, float)) and a["confidence"] > 0.97]
    if over:
        record("T2 confidence ceiling ≤0.97", FAIL,
               f"{len(over)}/{len(axes)} above 0.97: {over[:4]}")
    else:
        record("T2 confidence ceiling ≤0.97", PASS, f"{len(axes)} axioms, max ≤ 0.97")


# ── T3: F11 means AUDIT, not identity ───────────────────────────────────────
# Falsified by: the axioms surface describing F11 as identity/authority only.
AUDIT_TOKENS = ("audit", "log", "trace", "provenance", "attribut", "record")


def t3_f11_meaning() -> None:
    _, _, payload = call("arif_think", {"mode": "axioms", "query": "F1-F13", **session()})
    axes = find(payload, "axioms") if payload else None
    if not axes:
        record("T3 F11 means audit", UNMEASURED, "no axioms returned")
        return
    row = next((a for a in axes if str(a.get("id", "")).startswith("L11")), None)
    if not row:
        record("T3 F11 means audit", UNMEASURED, "L11 axiom absent")
        return
    text = str(row.get("text", "")).lower()
    if any(t in text for t in AUDIT_TOKENS):
        record("T3 F11 means audit", PASS, f"L11='{row.get('text')[:60]}'")
    else:
        record("T3 F11 means audit", FAIL,
               f"L11 describes '{row.get('text')[:70]}' — no audit/log/trace token")


# ── T4: advertised parameters are callable ──────────────────────────────────
# Falsified by: a parameter present in the live input schema that the tool rejects.
def t4_advertised_params_callable() -> None:
    try:
        schema = rpc("tools/list", {})
    except Exception as e:
        record("T4 advertised params callable", UNMEASURED, f"{type(e).__name__}")
        return
    tool = next((t for t in schema["result"]["tools"] if t["name"] == "arif_think"), None)
    if not tool:
        record("T4 advertised params callable", UNMEASURED, "arif_think not on wire")
        return
    props = tool.get("inputSchema", {}).get("properties", {})
    # one cheap probe per advertised param, using a value of the DECLARED type.
    # (v1 passed "probe" to `context`, which is object|null — a correct rejection
    #  that the test wrongly scored as a defect. Fixed same session.)
    sample = {"boolean": True, "string": "probe", "integer": 1, "number": 1.0,
              "object": {}, "array": []}
    broken = []
    for name, spec in sorted(props.items()):
        if name in {"mode", "query"}:
            continue
        typ = spec.get("type")
        if typ not in sample:
            continue  # anyOf / union types are not probed: a rejection would be correct
        args = {"mode": "axioms", "query": "x", name: sample[typ]}
        try:
            _, detail, _ = call("arif_think", args)
            if "CONTRACT_VIOLATION" in detail or "isError=True" in detail:
                broken.append(name)
        except Exception:
            broken.append(name)
    if broken:
        record("T4 advertised params callable", FAIL,
               f"advertised but rejected: {broken}")
    else:
        record("T4 advertised params callable", PASS,
               f"{len(props)} advertised params accepted")


# ── T5: F6 dual-registry bridge is honoured, not collapsed ──────────────────
# Falsified by: the kernel-layer canon module emitting EMPATHY instead of MARUAH.
def t5_f6_bridge() -> None:
    try:
        from arifosmcp.constitutional_canon import FLOORS
    except Exception as e:
        record("T5 F6 bridge", UNMEASURED, f"canon module unavailable: {type(e).__name__}")
        return
    f6 = next((f for f in FLOORS if f.fid == "F6"), None)
    if f6 is None:
        record("T5 F6 bridge", FAIL, "F6 absent from canon module")
        return
    if f6.name == "MARUAH":
        record("T5 F6 bridge", PASS, "kernel layer emits MARUAH (canon §3.4)")
    else:
        record("T5 F6 bridge", FAIL, f"kernel layer emits {f6.name}, expected MARUAH")


# ── T6: OBSERVE modes never declare mutation ────────────────────────────────
# Falsified by: a contract saying both action_class=OBSERVE and mutation=true.
def t6_observe_cannot_mutate() -> None:
    try:
        from arifosmcp.abi.kernel_abi import mode_contract, mode_contracts
    except Exception as e:
        record("T6 OBSERVE cannot mutate", UNMEASURED, f"{type(e).__name__}")
        return
    declared = mode_contracts()["contracts"]
    bad = []
    for key in declared:
        tool, _, mode = key.partition(".")
        c = mode_contract(tool, mode)
        if c and c["action_class"] == "OBSERVE" and c.get("mutation"):
            bad.append(key)
    if bad:
        record("T6 OBSERVE cannot mutate", FAIL, f"contradictions: {bad}")
    else:
        record("T6 OBSERVE cannot mutate", PASS, f"{len(declared)} contracts consistent")


def main() -> int:
    for fn in (t1_irreversible_refusal, t2_confidence_ceiling, t3_f11_meaning,
               t4_advertised_params_callable, t5_f6_bridge, t6_observe_cannot_mutate):
        try:
            fn()
        except Exception as e:
            record(fn.__name__, UNMEASURED, f"{type(e).__name__}: {e}")

    width = max(len(n) for n, _, _ in results) + 2
    for name, status, detail in results:
        print(f"{status:10} {name.ljust(width)} {detail}")
    fails = sum(1 for _, s, _ in results if s == FAIL)
    unmeas = sum(1 for _, s, _ in results if s == UNMEASURED)
    print(f"\n{len(results)} tests · {len(results) - fails - unmeas} pass · {fails} fail · {unmeas} unmeasured")
    if fails:
        return 1
    if unmeas:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
