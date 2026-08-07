#!/usr/bin/env python3
"""
Path A Defect Detectors — 3 standalone checks (no pytest dependency).

Each function calls live :8088/mcp via stdlib urllib and checks for
known defects. Prints ✅/❌ with payload snippets showing the defect.

Usage:
    python tests/verify_fix_path_a.py

Defects:
  A1 — L11 AUTH identity rewrite: session_birth.actor_id vs result.actor_id
  A2 — substrate DEGRADED dual-source desync: constitutional vs effective
  A3 — entropy_dS swallowed: delta_S key absent or silently defaulted

Constraint: stdlib only (urllib.request). actor_id='opencode-e2e-probe'.
"""

import json
import sys
import urllib.error
import urllib.request

KERNEL_MCP_URL = "http://127.0.0.1:8088/mcp"
ACTOR_ID = "opencode-e2e-probe"
TIMEOUT_S = 12


def mcp_call(name: str, args: dict) -> dict:
    """Call arifOS MCP tool, return structuredContent."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": name, "arguments": args},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        KERNEL_MCP_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    result = body.get("result", {})
    return result.get("structuredContent", result)


def check_l11_auth() -> bool:
    """
    A1 — L11 AUTH identity rewrite.

    Expected bug: arif_init returns session_birth.actor_id != result.actor_id
    AND session_birth.actor_verified != effective_state.actor_verified.

    Code site: arifosmcp/runtime/tools.py:250-263 — two independent paths
    populate session_birth vs effective_state without synchronization.
    """
    sc = mcp_call("arif_init", {"actor_id": ACTOR_ID, "mode": "init"})

    # The defect manifests at the structuredContent level.
    # In the live kernel, session_birth and effective_state are nested within
    # the result object or may be absent if the kernel was patched.

    actor_obj = sc.get("actor", {})
    result_obj = sc.get("result", {})
    constitutional = sc.get("constitutional_check", {})

    actor_id_outer = sc.get("actor_id") or actor_obj.get("actor_id")
    actor_id_result = result_obj.get("actor_id") or result_obj.get("actor")
    actor_verified_cc = constitutional.get("actor_verified")

    # Check for session-level identity rewrite
    # The original defect: session_birth.actor_id = "ARIF" (hardcoded uppercase)
    # while result.actor_id = "arif-fazil" (actual caller)
    # Look for evidence of this split

    # Try to find session_birth anywhere in the response
    session_birth_actor_id = None
    session_birth_verified = None

    # Search nested objects
    def _search(d, path="", depth=0):
        nonlocal session_birth_actor_id, session_birth_verified
        if depth > 5:
            return
        if isinstance(d, dict):
            for k, v in d.items():
                if k == "session_birth" and isinstance(v, dict):
                    session_birth_actor_id = v.get("actor_id")
                    session_birth_verified = v.get("actor_verified")
                elif k == "effective_state" and isinstance(v, dict):
                    session_birth_verified = session_birth_verified or v.get("actor_verified")
                _search(v, f"{path}.{k}", depth + 1)
        elif isinstance(d, list):
            for i, item in enumerate(d[:5]):
                _search(item, f"{path}[{i}]", depth + 1)

    _search(sc)

    # Decision logic
    has_defect = False
    findings = []

    if session_birth_actor_id is not None and actor_id_result is not None:
        if session_birth_actor_id.upper() != actor_id_result:
            has_defect = True
            findings.append(
                f"session_birth.actor_id='{session_birth_actor_id}' "
                f"!= result.actor_id='{actor_id_result}'"
            )

    if session_birth_verified is not None and actor_verified_cc is not None:
        if session_birth_verified != actor_verified_cc:
            has_defect = True
            findings.append(
                f"session_birth.actor_verified={session_birth_verified} "
                f"!= effective_state.actor_verified={actor_verified_cc}"
            )

    # If session_birth/effective_state are entirely missing,
    # that may mean the bug was patched — but the absence is itself notable
    if session_birth_actor_id is None and session_birth_verified is None:
        # The fields may have been restructured. Check if the current
        # actor_id is consistent across actor and result objects.
        if actor_id_outer and actor_id_result and actor_id_outer != actor_id_result:
            has_defect = True
            findings.append(
                f"actor.actor_id='{actor_id_outer}' != result.actor_id='{actor_id_result}'"
            )
        else:
            # No detectable identity split — bug may be fixed
            pass

    # Check verdicts for actor_verified signal
    verdicts = sc.get("verdicts", {})
    session_v = verdicts.get("session", {})
    ev_ref = session_v.get("evidence_reference", "")
    if "actor_verified=False" in ev_ref:
        has_defect = True
        findings.append(f"verdicts.session signals actor_verified=False: {ev_ref}")

    if has_defect:
        print(f"❌ A1 L11_AUTH: IDENTITY REWRITE DETECTED")
        for f in findings:
            print(f"   {f}")
        print(
            f"   payload: actor={actor_obj}, result_actor={result_obj.get('actor_id', result_obj.get('actor'))}"
        )
        return False
    else:
        print(f"✅ A1 L11_AUTH: no identity rewrite detected")
        print(
            f"   actor_id={actor_id_outer}, result_actor={actor_id_result}, "
            f"session_birth_present={'yes' if session_birth_actor_id else 'no'}"
        )
        return True


def check_substrate_degraded() -> bool:
    """
    A2 — substrate DEGRADED dual-source desync.

    Expected bug: arif_observe returns constitutional_check.substrate_state="DEGRADED"
    BUT effective_state.substrate_state="HEALTHY" (or absent).

    Two sources: _build_governance_status_payload vs runtime_attestation_injected.
    """
    sc = mcp_call("arif_observe", {"mode": "entropy_dS"})

    cc = sc.get("constitutional_check", {})
    cc_substrate = cc.get("substrate_state")  # expected: "DEGRADED"

    # effective_state may be at top level, in result, or absent
    eff_substrate = (
        sc.get("effective_state", {}).get("substrate_state")
        if isinstance(sc.get("effective_state"), dict)
        else None
    )

    # Also check authority.computed_from.substrate
    auth = sc.get("authority", {})
    auth_substrate = (
        auth.get("computed_from", {}).get("substrate")
        if isinstance(auth.get("computed_from"), dict)
        else None
    )

    # Also check verdicts.substrate
    verdicts = sc.get("verdicts", {})
    verdict_substrate = verdicts.get("substrate", {}).get("evidence_reference", "")

    has_defect = False

    if cc_substrate == "DEGRADED" and eff_substrate is None:
        has_defect = True
        print(f"❌ A2 SUBSTRATE: DUAL-SOURCE DESYNC DETECTED")
        print(f"   constitutional_check.substrate_state = '{cc_substrate}'")
        print(f"   effective_state = MISSING (not in response)")
        print(f"   authority.computed_from.substrate = '{auth_substrate}'")
        print(f"   verdicts.substrate = '{verdict_substrate}'")
        return False

    if cc_substrate is not None and eff_substrate is not None and cc_substrate != eff_substrate:
        has_defect = True
        print(f"❌ A2 SUBSTRATE: DUAL-SOURCE DESYNC DETECTED")
        print(f"   constitutional_check.substrate_state = '{cc_substrate}'")
        print(f"   effective_state.substrate_state = '{eff_substrate}'")
        return False

    if not has_defect:
        print(f"✅ A2 SUBSTRATE: substrate states consistent")
        print(f"   cc={cc_substrate}, effective={eff_substrate}, auth={auth_substrate}")
        return True

    return False


def check_entropy_ds_swallowed() -> bool:
    """
    A3 — entropy_dS swallowed (None != measurable).

    Expected bug: arif_observe mode=entropy_dS returns delta_S=None
    because the inner handler no longer sets delta_S (STAB-e/f/i killed
    all 0.0 fabrications), so the propagation at line 8497 sees no key
    and delta_S stays at default.

    The fix: when inner handler omits delta_S, propagate as None explicitly.

    Test: delta_S must be present in response (key exists) and NOT 0.0.
    None is acceptable — it means "not measured".
    """
    sc = mcp_call("arif_observe", {"mode": "entropy_dS"})

    delta_s_present = "delta_S" in sc
    delta_s_value = sc.get("delta_S")

    if not delta_s_present:
        print(f"❌ A3 ENTROPY_DS: SWALLOWED — delta_S key MISSING from response")
        print(f"   Response keys: {sorted(sc.keys())}")
        print(f"   Defect: caller cannot distinguish 'not measured' from 'key absent'")
        return False

    if delta_s_value == 0.0:
        print(f"❌ A3 ENTROPY_DS: FABRICATED ZERO — delta_S=0.0 (K-series violation)")
        print(f"   Defect: 0.0 is fabricated; STAB-e/f/i killed all 0.0 fabrications but")
        print(f"   a propagation path still defaults to 0.0 instead of None.")
        return False

    # delta_S is present and NOT 0.0 — either None (correct: not measured)
    # or a real float (correct: actually measured).
    if delta_s_value is None:
        print(f"✅ A3 ENTROPY_DS: delta_S=None — correctly signals 'not measured'")
        print(f"   No fabrication. STAB-e/f/i fix is working.")
    else:
        print(f"✅ A3 ENTROPY_DS: delta_S={delta_s_value} — real measurement present")
        print(f"   No fabrication. Entropy measurement is live.")

    return True


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("Path A Defect Detectors — arifOS Kernel E2E")
    print(f"Target: {KERNEL_MCP_URL}")
    print(f"Actor:  {ACTOR_ID}")
    print("=" * 60)
    print()

    results = {}
    for name, fn in [
        ("A1 L11_AUTH", check_l11_auth),
        ("A2 SUBSTRATE", check_substrate_degraded),
        ("A3 ENTROPY_DS", check_entropy_ds_swallowed),
    ]:
        try:
            results[name] = fn()
        except urllib.error.URLError as e:
            print(f"❌ {name}: KERNEL UNREACHABLE — {e}")
            results[name] = False
        except Exception as e:
            print(f"❌ {name}: ERROR — {type(e).__name__}: {e}")
            results[name] = False
        print()

    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"SUMMARY: {passed}/{total} checks passed")
    if passed == total:
        print("✅ ALL PATH A CHECKS PASSED")
    else:
        print("❌ SOME PATH A DEFECTS REMAIN")
    print("=" * 60)

    sys.exit(0 if passed == total else 1)
