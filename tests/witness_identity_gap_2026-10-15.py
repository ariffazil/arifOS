"""witness_identity_gap_2026-10-15.py — 333-AGI WITNESS run (read-only probe), branch witness/identity.

Each test re-runs a probe from the witness pass of 2026-10-15T15:06Z against the
LIVE kernel at http://127.0.0.1:8088/mcp (and the public door). Expected values
are the witness RULE (what the kernel must do), not a prediction of current
behaviour — these tests are KNOWN FAILING against commit de1b916c0.

Defect measured 2026-10-15 (raw values in /root/AAA/audits/witness-2026-10-15.md):
  D1  arif_judge accepts UNBOUND calls and returns status="completed"
      (actor_id=anonymous, session_id=anonymous).
  D2  arif_seal accepts UNBOUND calls and returns status="completed"
      (call_hash e68bbab4… / 3a6debd1…, verdict OBSERVE_ONLY, no receipt).
      Asymmetry: arif_observe correctly REFUSES unbound calls
      (ARIF_SESSION_NOT_FOUND, -32001).
  D3  arif_seal with a wrong-typed payload leaks Pydantic internals
      ("1 validation errors for call[arif_seal] … errors.pydantic.dev/2.14/v/string_type").
  D4  No state_version / state counter is exposed on any verdict envelope, so a
      band/scope flip cannot be correlated with a version bump (only
      kernel_epoch "2026-07-03" exists, which never moves inside a run).

Run:  python3 -m pytest tests/witness_identity_gap_2026-10-15.py -v
Scope: tests only. No kernel code touched (witness rule).
"""

import json
import urllib.request

import pytest

LOCAL = "http://127.0.0.1:8088/mcp"
PUBLIC = "https://arifos.arif-fazil.com/mcp"
PROTO = "2025-03-26"


def call(url, tool, args, timeout=25):
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {"name": tool, "arguments": args},
        }
    ).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": PROTO,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode()
    except Exception as e:  # noqa: BLE001 — probe helper
        pytest.skip(f"kernel unreachable at {url}: {e}")
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("data:"):
            raw = line[5:].strip()
            break
    return json.loads(raw)


def tool_result(resp):
    """Return (text, error_code). text is '' when the call was refused."""
    if "error" in resp:
        return "", resp["error"].get("code")
    content = (resp.get("result") or {}).get("content") or []
    if not content:
        return "", None
    return content[0].get("text", ""), None


def status_of(text):
    try:
        return json.loads(text).get("status")
    except Exception:  # noqa: BLE001
        return None


# ── D1 · unbound arif_judge must be refused ────────────────────────────────
@pytest.mark.parametrize("door", [LOCAL, PUBLIC], ids=["local", "public"])
def test_d1_unbound_judge_is_refused_not_completed(door):
    """An unbound caller must NOT get a completed verdict envelope.

    Measured 2026-10-15T15:06Z: status="completed", actor_id="anonymous",
    session_id="anonymous", verdict HOLD. arif_observe refuses the same caller
    with ARIF_SESSION_NOT_FOUND — judge must match that bar.
    """
    text, err = tool_result(
        call(
            door,
            "arif_judge",
            {"mode": "verdict", "candidate": "witness unbound probe", "action_tier": "T0"},
        )
    )
    assert err is not None or status_of(text) != "completed", (
        "arif_judge served a COMPLETED verdict to an unbound caller: "
        f"err={err} status={status_of(text)} head={text[:160]}"
    )


# ── D2 · unbound arif_seal must be refused ─────────────────────────────────
@pytest.mark.parametrize("door", [LOCAL, PUBLIC], ids=["local", "public"])
def test_d2_unbound_seal_is_refused_not_completed(door):
    """An unbound caller must NOT get a completed seal envelope.

    Measured 2026-10-15T15:07Z (payload as JSON string): status="completed",
    actor_id="anonymous", call_hash=sha256:e68bbab4… (local) / 3a6debd1… (public),
    signature=null. No vault entry was written — a success-shaped hollow reply.
    """
    payload = json.dumps({"note": "witness unbound seal probe"})
    text, err = tool_result(call(door, "arif_seal", {"mode": "verify", "payload": payload}))
    assert err is not None or status_of(text) != "completed", (
        "arif_seal served a COMPLETED envelope to an unbound caller: "
        f"err={err} status={status_of(text)} head={text[:160]}"
    )


# ── control · the bar the other verbs already clear ────────────────────────
@pytest.mark.parametrize("door", [LOCAL, PUBLIC], ids=["local", "public"])
def test_d2_control_unbound_observe_is_already_refused(door):
    """Control (PASSING): arif_observe refuses unbound callers.

    Measured 2026-10-15T15:07Z: jsonrpc error -32001 ARIF_SESSION_NOT_FOUND.
    This is the exact bar D1/D2 must reach — it is asserted so the asymmetry is
    on the record inside the test file itself.
    """
    text, err = tool_result(
        call(door, "arif_observe", {"mode": "vitals", "query": "witness probe"})
    )
    assert err is not None, (
        "arif_observe accepted an unbound caller — the asymmetry anchor itself "
        f"moved: status={status_of(text)}"
    )


# ── D3 · validation errors must not leak library internals ────────────────
def test_d3_type_error_does_not_leak_pydantic_internals():
    """A wrong-typed argument must yield a contract error, not a stack vendor URL.

    Measured 2026-10-15T15:06Z: 'Input should be a valid string [type=string_type
    … For further information visit https://errors.pydantic.dev/2.14/v/string_type'
    — library name + version exposed on both doors.
    """
    text, err = tool_result(call(LOCAL, "arif_seal", {"mode": "verify", "payload": {"note": "x"}}))
    combined = text + json.dumps(err)
    assert "pydantic" not in combined.lower(), (
        f"validation error leaks Pydantic identity/version: {combined[:200]}"
    )


# ── D4 · a state counter must exist so flips are correlatable ──────────────
def test_d4_init_exposes_state_version():
    """arif_init must expose a monotonic state counter.

    Measured 2026-10-15T15:05Z: result keys carry kernel_epoch ('2026-07-03')
    but no state_version / state counter; band-scope flips therefore cannot be
    tied to a version bump (WITNESS RULE: record state_version at every hop).
    """
    text, err = tool_result(
        call(
            LOCAL,
            "arif_init",
            {
                "mode": "init",
                "actor_id": "333-agi-opencode",
                "intent": "witness state-version probe",
            },
        )
    )
    assert err is None, f"arif_init refused: {err}"
    body = json.loads(text)
    result = body.get("result", body)
    assert any(k in result for k in ("state_version", "session_state_version")), (
        "no state counter on the init envelope — flip-vs-bump correlation is "
        f"impossible; keys={sorted(result)[:20]}"
    )
