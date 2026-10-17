# BASELINE_RESULTS.md

**Reference:** ARIFOS::BASELINE_UNIT_TESTS::v1
**Date measured:** 2026-10-16.

**Execution note:** BT1–BT6 RUN against read-only source imports + fixtures, in
an isolated temporary directory: no network, no live runtime call, no mutation
surface, no production ledger. The only source reads are imports of
`/root/arifOS/arifosmcp/models/verdicts.py` and
`/root/arifOS/arifosmcp/abi/verification_envelope.py`.

## Frozen vocabulary (measured from live source)

- `SealType` = `['VOID', 'HOLD_888', 'HOLD', 'SABAR', 'PARTIAL', 'PROVISIONAL', 'SEAL']` (7)
- `actor_verified` = plain `bool`, default `False` (`verification_envelope.py`)
- `ReasonCode` = 13 canonical values (printed by BT4)
- `can_claim_success` = boolean field in `contradiction_detector.py`, `tools.py`, `verbosity.py`

## Measured results (L1/L2)

| Level | Meaning | Evidence | Status |
|---|---|---|---|
| L1 | test command ran | runner exit state this session | MEASURED — 6/6 |
| L2 | expected field/response observed | source import + fixture inspection | MEASURED — 6/6 |

## Design invariants (NOT measurements)

| Level | Meaning | Status |
|---|---|---|
| L3 | prohibited consequence (mutation) did not occur | **Guaranteed by design** — the runner opens no sockets and writes only to `$TMPDIR` and `fixtures/`. Not experimentally measured; this harness has no independent target-state probe. Against a live target, non-mutation is UNMEASURED. |

L1/L2 evidence is NOT proof of L3. L3 is a property of the harness
construction, recorded here as a design invariant, not as a measured fact.

## BT1 — Unsigned actor

- **Result:** GAP_CONFIRMED (L1, L2 measured)
- **Observation:** `actor_verified` is `bool=False`; grep of
  `verification_envelope.py` finds **no Ed25519 / actor_signature / verify
  path**. The field is a declared boolean, not crypto-derived.
- **Reading:** the invariant "unsigned caller cannot become verified by actor_id
  alone" holds *trivially* (nothing sets it True), but the gap is real: unsigned
  and signed callers are **indistinguishable** at this surface.

## BT2 — Caller-controlled verification

- **Result:** GAP_OPEN (L1, L2 measured)
- **Observation:** a fixture envelope `{actor_id:"attacker", actor_verified:true,
  verdict:"SEAL", session_id:"SEAL-spoofed"}` is just writable bools/strings.
  No signature gate re-derives identity. `SEAL-` prefix is a label, not
  authorization.

## BT3 — Verdict versus transport

- **Result:** INVARIANT_DEFINED (L1, L2 measured)
- **Observation:** fixture event separates `governance.verdict=HOLD` from
  `transport.response_completed=true` and `governance.can_claim_success=false`.
  The frozen schema preserves both facts. This defines the invariant that a
  repair must satisfy; it does **not** claim live telemetry is already fixed.

## BT4 — Refusal cause fidelity

- **Result:** GAP_CONFIRMED (L1, L2 measured)
- **Observation:** `ReasonCode` enum has 13 canonical values. The schema permits
  `reason_code=null`, so a refusal record CAN omit the cause. Invocation
  telemetry does not guarantee an explicit reason_code on refusal.

## BT5 — Sink event-set agreement

- **Result:** GAP_CONFIRMED (L1, L2 measured)
- **Observation:** two mock sinks with equal count (2==2) but different event
  identities (`{e1,e2}` vs `{e1,e9}`) — count-equality alone would pass;
  set-equality detects the divergence. Reproduces the 4-PATH split defect class
  using event_id (not manufactured identity).

## BT6 — Standalone reconstruction

- **Result:** INDEPENDENCE_LIMITED (L1, L2 measured)
- **Observation:** steps 5–9 reproduced via fixtures; steps 1–4 and 10 require an
  OUTSIDER on a clean host. Maintainer-run reproduction is NOT independent
  reconstruction (see HARNESS_CONTRACT.md).

## Summary

| Test | L1 | L2 | Verdict |
|---|---|---|---|
| BT1 | ran | observed | GAP_CONFIRMED |
| BT2 | ran | observed | GAP_OPEN |
| BT3 | ran | observed | INVARIANT_DEFINED |
| BT4 | ran | observed | GAP_CONFIRMED |
| BT5 | ran | observed | GAP_CONFIRMED |
| BT6 | ran | observed | INDEPENDENCE_LIMITED |

**None of the 4 governance gaps is closed.** These results REPRODUCE the gaps
via fixtures; they do not repair them, and they are not independent verification.

## Artifact hash

`fixtures/baseline_results.json` sha256 = `de6c82e69769a80b5d441433df40d6f49d8b8266cae3eb2d9026906e4752d72a`
