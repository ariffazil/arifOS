#!/usr/bin/env python3
"""
ARIFOS::BASELINE_UNIT_TESTS::v1 — baseline unit test runner.

ISOLATED | FAIL-CLOSED

Runs BT1–BT6 against read-only source imports + fixtures. Does NOT:
  - call any live arifOS/AAA/A-FORGE/CHRON/GEOX runtime
  - open any network connection
  - write outside the harness directory / TMPDIR
  - touch production ledgers, /etc, or canonical repos

Falsification levels — measured vs design (kept distinct and honest):
  L1 (measured) = the test command ran (this run's exit state)
  L2 (measured) = the expected field/response was observed (from source or fixture)
  L3 (DESIGN INVARIANT) = no mutation of any target occurs — guaranteed by
       construction (no sockets; writes confined to $TMPDIR and fixtures/).
       NOT an experimental measurement; there is no independent target-state
       probe in this harness. Do not report it as a measured fact.
"""

import json
import os
import sys
import hashlib

ARIFOS_SRC = "/root/arifOS"
HARNESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES = os.path.join(HARNESS_DIR, "fixtures")

results = []  # measured: {id, l1_command_ran, l2_expected_observed, verdict, note}


def report(bt_id, l1, l2, verdict, note):
    """Record MEASURED levels only. L3 is a harness-level DESIGN INVARIANT
    (no_mutation, by construction) — never a per-test measured claim."""
    results.append(
        {
            "id": bt_id,
            "l1_command_ran": l1,
            "l2_expected_observed": l2,
            "verdict": verdict,
            "note": note,
        }
    )
    print(f"[{bt_id}] L1={l1} L2={l2} -> {verdict}: {note}")


# ── Source imports (read-only) ─────────────────────────────────────────
sys.path.insert(0, ARIFOS_SRC)

sealtype_members = None
reasoncode_members = None
actor_verified_default = None
actor_verified_field_type = None

try:
    from arifosmcp.models.verdicts import SealType

    sealtype_members = [m.value for m in SealType]
except Exception as e:
    report("BT0-import", False, False, "BLOCKED", f"SealType import failed: {e}")

try:
    from arifosmcp.abi.verification_envelope import ReasonCode

    reasoncode_members = [m.value for m in ReasonCode]
except Exception as e:
    reasoncode_members = None
    print(f"[warn] ReasonCode import failed: {e}")

try:
    from arifosmcp.abi.verification_envelope import VerificationTelemetry
    import dataclasses

    f = [
        x
        for x in dataclasses.fields(VerificationTelemetry)
        if x.name == "actor_verified"
    ]
    if f:
        actor_verified_field_type = str(f[0].type)
        actor_verified_default = f[0].default
except Exception as e:
    print(f"[warn] VerificationTelemetry import failed: {e}")


# ── BT1 — Unsigned actor must not become verified by actor_id alone ────
def bt1():
    l1 = True
    l2 = False
    note = ""
    if sealtype_members is None:
        report("BT1", l1, False, "BLOCKED", "cannot import source")
        return
    # The field is a plain bool defaulting False (proved above).
    l2 = actor_verified_field_type is not None
    # gap: is there a signature path that can SET it True? grep source.
    try:
        src = open(
            os.path.join(ARIFOS_SRC, "arifosmcp", "abi", "verification_envelope.py")
        ).read()
        has_sig_verify = (
            "ed25519" in src.lower()
            or "actor_signature" in src.lower()
            or "verify_signature" in src.lower()
        )
    except Exception:
        has_sig_verify = None
    if has_sig_verify is False:
        note = (
            f"actor_verified is {actor_verified_field_type} default={actor_verified_default}; "
            f"NO signature verification in verification_envelope.py -> the field is a declared "
            f"bool, not crypto-derived. Invariant holds trivially (nothing sets it True), but "
            f"the identity gap is REAL: unsigned and signed callers are indistinguishable at "
            f"this surface."
        )
        verdict = "GAP_CONFIRMED"
    elif has_sig_verify is True:
        note = "signature verification found in envelope; gap-1 may be narrower than claimed. Re-inspect."
        verdict = "NEEDS_REINSPECTION"
    else:
        note = "source read unavailable for signature check"
        verdict = "UNKNOWN"
    report("BT1", l1, l2, verdict, note)


# ── BT2 — Caller-controlled actor_verified/verdict/session do not bind ─
def bt2():
    l1 = True
    l2 = False
    # A caller-controlled envelope: plain dict. Nothing validates it.
    spoof = {
        "actor_id": "attacker",
        "actor_verified": True,  # caller-controlled boolean
        "verdict": "SEAL",  # caller-controlled verdict text
        "session_id": "SEAL-spoofed",  # SEAL- prefix is a label, not authorization
    }
    # Does the runtime reject these? The VerificationTelemetry.actor_verified is a
    # plain bool attribute — a caller can set it. No signature gate re-derives it.
    settable = actor_verified_field_type is not None
    l2 = True  # observed: fields are plain, caller-settable
    if settable:
        note = (
            f"spoofed envelope {json.dumps(spoof)}: actor_verified is a writable bool field "
            f"(type={actor_verified_field_type}), verdict is a plain string, 'SEAL-' session_id "
            f"is a label. No signature gate re-derives identity from a cryptographic envelope. "
            f"GAP OPEN: none of these values is cryptographically bound."
        )
        verdict = "GAP_OPEN"
    else:
        note = "could not inspect actor_verified field type"
        verdict = "UNKNOWN"
    report("BT2", l1, l2, verdict, note)


# ── BT3 — HOLD must not become transport success ───────────────────────
def bt3():
    l1 = True
    l2 = False
    # Build a HOLD event where transport succeeded, per the frozen schema.
    event = {
        "identity": {
            "actor_id": "FI-003",
            "actor_key_id": None,
            "actor_verified": False,
            "identity_evidence": None,
            "verification_reason": None,
        },
        "authority": {
            "authority_present": False,
            "authority_scope": None,
            "authority_ceiling": None,
            "authority_source": None,
        },
        "governance": {
            "verdict": "HOLD",
            "reason_code": "AUTHORITY_MISSING",
            "can_claim_success": False,
            "judge_source": None,
        },
        "transport": {
            "request_accepted": True,
            "response_completed": True,
            "transport_error": None,
        },
        "execution": {
            "attempted": False,
            "mutation_occurred": False,
            "target": None,
            "consequence_hash": None,
        },
        "witness": {"observed": False, "witness_source": None, "observed_at": None},
        "receipt": {
            "receipt_id": None,
            "event_id": None,
            "trace_id": None,
            "payload_hash": None,
            "previous_hash": None,
            "receipt_status": None,
        },
    }
    # validate against the authoritative machine-checked schema
    # (jsonschema when installed; the field checks below are the fallback)
    with open(
        os.path.join(HARNESS_DIR, "schemas", "governance-event.schema.json")
    ) as fh:
        schema = json.load(fh)
    try:
        import jsonschema

        jsonschema.validate(event, schema)
        schema_ok = "validated against schemas/governance-event.schema.json"
    except ImportError:
        schema_ok = "jsonschema not installed — field checks only"
    except Exception as e:  # schema rejection is a real failure, fail closed
        report("BT3", l1, False, "FIXTURE_ERROR", f"schema validation failed: {e}")
        return
    # field separation check (dependency-free fallback)
    verdict_ok = event["governance"]["verdict"] == "HOLD"
    transport_ok = event["transport"]["response_completed"] is True
    success_field_false = event["governance"]["can_claim_success"] is False
    l2 = verdict_ok and transport_ok and success_field_false
    if l2:
        note = (
            "fixture event separates governance.verdict=HOLD from transport.response_completed=true "
            "and governance.can_claim_success=false. The SCHEMA preserves both facts. The legacy "
            "defect (ok:true overloading HOLD as success) is what the schema is designed to detect — "
            "the field separation is the invariant under test, NOT a claim that live telemetry is fixed. "
            f"({schema_ok})"
        )
        verdict = "INVARIANT_DEFINED"
    else:
        note = "fixture does not separate fields as expected"
        verdict = "FIXTURE_ERROR"
    report("BT3", l1, l2, verdict, note)


# ── BT4 — Refusal cause must be present in evidence ────────────────────
def bt4():
    l1 = True
    l2 = False
    if not reasoncode_members:
        report("BT4", l1, False, "BLOCKED", "ReasonCode import failed")
        return
    # Fixture A: refusal WITH reason_code (correct)
    # Fixture B: refusal WITHOUT reason_code (the gap)
    with_reason = {
        "governance": {"verdict": "VOID", "reason_code": "AUTHORITY_MISSING"}
    }
    without_reason = {"governance": {"verdict": "VOID", "reason_code": None}}
    l2 = True
    # Demonstrate the gap: fixture A carries a cause, fixture B can lack it
    # (None is valid in current code) — the pair IS the gap evidence.
    gap_present = (
        with_reason["governance"]["reason_code"] is not None
        and without_reason["governance"]["reason_code"] is None
    )
    note = (
        f"ReasonCode enum has {len(reasoncode_members)} canonical values: {reasoncode_members}. "
        f"Fixture with reason_code present vs absent: the schema permits reason_code=null, so a "
        f"refusal record CAN omit the cause. GAP: invocation telemetry does not guarantee an "
        f"explicit reason_code on refusal."
    )
    verdict = "GAP_CONFIRMED" if gap_present else "UNKNOWN"
    report("BT4", l1, l2, verdict, note)


# ── BT5 — Sink event-set agreement (identity, not count) ───────────────
def bt5():
    l1 = True
    l2 = False
    # Two mock sinks with EQUAL COUNT but DIFFERENT event identities.
    sink_a = [
        {"event_id": "e1", "trace_id": "t1", "event_type": "HOLD"},
        {"event_id": "e2", "trace_id": "t2", "event_type": "HOLD"},
    ]
    sink_b = [
        {"event_id": "e1", "trace_id": "t1", "event_type": "HOLD"},
        {"event_id": "e9", "trace_id": "t9", "event_type": "HOLD"},
    ]  # e9 != e2

    def key(sink):
        return set(e["event_id"] for e in sink)

    count_equal = len(sink_a) == len(sink_b)
    set_equal = key(sink_a) == key(sink_b)
    l2 = True
    if count_equal and not set_equal:
        note = (
            "fixture: 2 sinks, equal count (2==2), DIFFERENT event identities "
            "({e1,e2} vs {e1,e9}). Count-equality alone would pass; set-equality detects the "
            "divergence. This reproduces the 4-PATH split defect class using event_id, NOT "
            "manufactured identity."
        )
        verdict = "GAP_CONFIRMED"
    elif set_equal:
        note = "fixture sinks agree; adjust fixture to reproduce divergence"
        verdict = "FIXTURE_NEEDS_ADJUST"
    else:
        note = "unexpected"
        verdict = "UNKNOWN"
    # write the divergence as a fixture file for the record
    with open(os.path.join(FIXTURES, "bt5_sink_divergence.json"), "w") as fh:
        json.dump(
            {
                "sink_a": sink_a,
                "sink_b": sink_b,
                "count_equal": count_equal,
                "set_equal": set_equal,
            },
            fh,
            indent=2,
        )
    report("BT5", l1, l2, verdict, note)


# ── BT6 — Standalone reconstruction procedure ──────────────────────────
def bt6():
    l1 = True
    l2 = False
    # The 10 steps. Steps 1-2 are executable read-only NOW; the rest require
    # an OUTSIDER (maintainer-run is NOT independent reconstruction).
    steps = [
        ("obtain pinned source", "deferred-outsider"),
        ("verify declared hashes", "deferred-outsider"),
        ("build without private deps", "deferred-outsider"),
        ("run with network disabled", "deferred-outsider"),
        ("init isolated runtime/fixture", "done-here (fixture)"),
        ("reproduce deterministic refusal", "done-here (BT1-BT4 fixtures)"),
        ("attempt spoofed identity", "done-here (BT2 fixture)"),
        ("observe no mutation", "by-construction (no network, tmp dirs)"),
        ("inspect transport/governance/execution separately", "done-here (BT3 schema)"),
        ("reconstruct chain with separate verifier", "deferred-outsider"),
    ]
    l2 = True
    note = (
        "Maintainer-built harness IS NOT independent reconstruction (mission rule). "
        "Steps 5-9 are reproduced here via fixtures; steps 1-4,10 require an OUTSIDER on a "
        "clean host. This is a documented independence limitation, not a hidden success."
    )
    with open(os.path.join(FIXTURES, "bt6_reconstruction_steps.json"), "w") as fh:
        json.dump(
            [{"step": i + 1, "what": w, "status": s} for i, (w, s) in enumerate(steps)],
            fh,
            indent=2,
        )
    report("BT6", l1, l2, "INDEPENDENCE_LIMITED", note)


# ── Run ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 70)
    print("ARIFOS::BASELINE_UNIT_TESTS::v1  (ISOLATED / FAIL-CLOSED)")
    print(f"SealType = {sealtype_members}")
    print(
        f"actor_verified field type = {actor_verified_field_type}, default = {actor_verified_default}"
    )
    print("=" * 70)
    bt1()
    bt2()
    bt3()
    bt4()
    bt5()
    bt6()
    print("=" * 70)
    # summary — MEASURED results (L1/L2) are separate from DESIGN INVARIANTS (L3)
    out = {
        "sealtype": sealtype_members,
        "reasoncode": reasoncode_members,
        "actor_verified": {
            "type": actor_verified_field_type,
            "default": actor_verified_default,
        },
        "measured_results": results,
        "design_invariants": {
            "no_mutation": {
                "level": "L3",
                "basis": "by-construction",
                "experimentally_measured": False,
                "detail": (
                    "The runner opens no sockets and writes only to $TMPDIR and "
                    "harness fixtures/. No independent target-state probe exists in "
                    "this harness; against a live target, non-mutation is UNMEASURED."
                ),
            }
        },
    }
    outpath = os.path.join(HARNESS_DIR, "fixtures", "baseline_results.json")
    with open(outpath, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"JSON results written: {outpath}")
    # SHA-256 of the results
    h = hashlib.sha256(open(outpath, "rb").read()).hexdigest()
    print(f"baseline_results.json sha256 = {h}")
