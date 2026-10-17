# HARNESS_FIXTURE_PLAN.md

**REFERENCE:** ARIFOS::REALITY_LOOP_RECEIPT_INTEGRITY_REPAIR::v1
**STATUS:** READ_ONLY | EVIDENCE_REPAIR_ONLY
**VERDICT:** HOLD

## Per the user's classification of this incident as baseline evidence

The user identified 4 baseline evidence points in this incident. Corrected per the integrity-repair directive:

### BT1: Actor identity
- `actor_id = "FI-003"`
- `actor_verified = false`
- **Lesson:** An actor_id label does not produce verified identity. The arif_init response had `actor_verified=false` regardless of how "FI-003" is formatted or repeated.

### BT2: Session label
- session_id carried `SEAL-` prefix
- `verdict = HOLD`, `autonomy_band = OBSERVE_ONLY`
- **Lesson:** A `SEAL-` prefix on the session_id does not grant execution authority. The actual verdict (HOLD) and autonomy band (OBSERVE_ONLY) are what matter.

### BT3: Authority separation
- `arif_init` succeeded at the transport layer
- Mutation was refused
- **Lesson:** `transport success ≠ governance authorization`. Per `feedback/three-level-falsification-before-pipeline.md` and the user's own correction of R1: transport ok does not mean governance success.

### BT4: Consequence (corrected)
- **mutation-class requests observed:** 2, verified from INVOCATION_LEDGER.json
- **accepted execution observed:** 0 in caller responses
- **target mutation count:** UNKNOWN (no independent target-state probe)
- **Level 3 result:** UNMEASURED

The previous "2 execution requests, 0 mutations" was too strong — it implied L3 evidence (target mutation = 0). The corrected statement admits the target mutation count is UNKNOWN; the only L2 evidence is "0 accepted executions in caller responses."

## Fixture plan (per the directive)

> "Describe how this incident can become a sanitized fixture for: unsigned actor remains unverified; HOLD does not authorize execution; SEAL-prefixed identifiers do not grant authority; rejected transport call does not mutate target state. Do not copy production tokens or private payloads into fixtures."

### Fixture 1: BT1 — actor_id does not produce verified identity
- Sanitize: `actor_id = "fixture-actor"` or a UUID placeholder.
- Expected behavior: `actor_verified = false`, no authority to execute.

### Fixture 2: BT2 — SEAL-prefix session_id is not a SEAL verdict
- Sanitize: `session_prefix = "SEAL-"`, `session_id_hash = "<actual sha256 of synthetic session_id>"`.
- DO NOT include the production `session_id` or its `verdict` or `autonomy_band` values.
- Expected behavior: P0.2 SEAL-* format rejection holds regardless of prefix length or content after the dash.

### Fixture 3: BT3 — transport success ≠ governance authorization
- Sanitize: synthetic `arif_init` response where `transport.accepted = true` and `governance.verdict = HOLD`.
- DO NOT include the production `verdict` value or the production `intent` field.
- Expected behavior: A synthetic success on the transport layer does not unlock EXECUTE_REVERSIBLE on the loop tool.

### Fixture 4: BT4 — 2 mutation-class requests do not mutate target state (corrected)
- Sanitize: represent the 2 attempts as a fixture with 2 calls, both returning SESSION_REQUIRED.
- DO NOT include the production SESSION_REQUIRED response verbatim (it is a real error, not synthetic).
- Expected behavior: A reproduction harness exercising this fixture can verify that the loop state owner is NOT mutated by 2 rejected calls — IF AND ONLY IF the harness has independent target-state read access.
- The fixture must record: "target mutation count: UNKNOWN; Level 3 result: UNMEASURED" — not "0 mutations" without L3 evidence.

## Minimized token metadata (per the directive)

Per the user's correction, the reusable fixture must NOT include:
- The raw `act_token` (722 chars was a token fingerprint, not a needed fact)
- The full production `session_id` (SEAL-prefix + 8 hex chars)
- Any implementation fingerprint of the token

Instead, the fixture exposes only:
- `token_present: true` (a boolean, not the token itself)
- `token_redacted: true` (a boolean)
- `session_prefix: "SEAL-"` (the prefix, not the full id)
- `session_id_hash: "<sha256 of synthetic session_id>"` (computed from the synthetic id, not the production id)

## What this fixture is NOT

- It is NOT a reproduction of the live incident (per `feedback/agent-must-not-buy-progress-by-destroying-truth.md`).
- It is NOT a sanitized payload of the live session_token (per the directive, no production tokens).
- It is NOT a substitute for a third-party reproduction (per `feedback/INDEPENDENCE_LIMITS.md` in the prior harness design).
- It is NOT a closure claim for any of the 4 governance gaps (per the public-surface federation principles, claim discipline).

## Where the fixture would live (if activated)

Per the prior harness design at `/root/forge_work/2026-10-16/ARIFOS-REPRO-HARNESS/BASELINE_RESULTS.md`:

- BT1 → `fixtures/bt1_unsigned_actor.json` (DESIGN ONLY — not produced in PREPARE_ONLY)
- BT2 → `fixtures/bt2_caller_controlled.json` (DESIGN ONLY)
- BT3 → `fixtures/bt3_hold_ok.json` (DESIGN ONLY)
- BT4 → `fixtures/bt4_refusal.json` (DESIGN ONLY)

The fixture PLAN is here. The fixture FILES are not produced in this task.
