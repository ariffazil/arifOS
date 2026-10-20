# INCIDENT_RECEIPT.md

**REFERENCE:** ARIFOS::SCT_ACTOR_CLAIM_MISMATCH::v1
**STATUS:** REPORTED_ONLY | NO_PATCH_APPLIED
**VERDICT:** HOLD
**Date:** 2026-10-20, KVM8, FI-003 (Qwen Code, 333-AGI, DECODER)
**Kernel:** arifos-e32ebbd · drift `false` · canon `2026.10.18-7628a9a` integrity `ok`
**Reported by:** FI-003 · requested by F13 ("file the kernel actor-claim bug")

---

## 1. Summary

`arif_init` mints a session token whose `actor` claim and the `actor_id` it *reports back* are
**different strings**. The verifier compares the two, so echoing the `actor_id` the caller
just supplied is rejected as `TOKEN_INVALID` on the very next call.

Net effect: **an agent that correctly repeats its own identity is refused.** Re-binding does not
help — it reproduces exactly. Only changing the `actor_id` string to the token's own claim
("QWEN") succeeds, which is a workaround, not correct usage.

## 2. Measured evidence (L3 — executed, not inferred)

| Step | Call | `actor_id` sent | Result |
|---|---|---|---|
| 1 | `arif_init` | *(omitted)* | `HOLD` / `MISSING_REQUIRED_INPUT: actor_id`, F4_CLARITY |
| 2 | `arif_init` | `qwen-code/FI-003` | `HOLD`, session `SEAL-53e9d3750c454f76`, SCT minted `token_len=723` |
| 3 | `arif_observe` | `qwen-code/FI-003` | `TOKEN_INVALID` · `L11 AUTH: SCT invalid (signature or actor mismatch)` |
| 4 | `arif_init` (repair) | *(omitted)* | `HOLD`, fresh session `SEAL-40c8dfc726b743ce`, fresh SCT |
| 5 | `arif_observe` | `qwen-code/FI-003` | `TOKEN_INVALID` — **identical failure on a fresh token** |
| 6 | `arif_observe` | `QWEN` | **OK** — live vitals returned |

Token payload as returned by INIT (`act_claims`), decoded:

```json
{"act_v": 1, "actor": "QWEN", "sid": "SEAL-40c8dfc726b743ce", "av": false,
 "lane": "AGI", "kid": "default", "auth": "OBSERVE_ONLY"}
```

INIT response envelope for the *same* call:

```json
"actor": {"actor_id": "qwen-code/FI-003", "source": "envelope_derived"}
```

The signature is valid in every case (only the actor comparison fails). This is **not** an
expiry, not a replay, and not an authority problem — `forge`/`seal` were never in `allowed`.

## 3. Root cause (source-located)

**Comparison site** — `arifosmcp/runtime/act_token.py:897`

```python
claims = verify_act(session_token, expected_actor=actor_id)
```

On `None`, `act_token.py:919` emits the observed message:

```python
reason="L11 AUTH: SCT invalid (signature or actor mismatch)",
```

**Comparison internals** — `verify_act` normalizes both sides then requires equality
(`act_token.py:645-654` for the legacy branch, `695-711` for the ACT branch):

```python
from arifosmcp.runtime.governance_identity import normalize_actor_id
_claim_norm   = normalize_actor_id(claim_actor)     or claim_actor.lower().strip()
_expected_norm= normalize_actor_id(expected_actor) or expected_actor.lower().strip()
```

**Empirically confirmed** (`/opt/arifos/current/venv/bin/python`):

```
token claim : 'QWEN'              -> norm 'QWEN'
requested   : 'qwen-code/FI-003'  -> norm 'qwen-code/FI-003'
MATCH?      False
```

`normalize_actor_id()` (in `runtime/governance_identity.py`) maps only *sovereign* variants
(`Salam ARIF` → `arif`, `ARIF_FAZIL` → `arif`) and **returns unknown inputs unchanged** by design
("this is safe because downstream code already handles unknown actor_ids by defaulting to
OBSERVE_ONLY"). It has no alias table for harness/lane identities, so `QWEN` and
`qwen-code/FI-003` remain two genuinely distinct identifiers. **Case is not the issue** — both
branches already lowercase, so a case-only fix would not close this.

## 4. Open question — NOT yet traced (labelled UNKNOWN)

**Where does the minted `'QWEN'` come from?** I did not establish this.

- `capability_token.build_session_token(actor_id=...)` mints with `actor=actor_id or "anonymous"`
  (`capability_token.py:64`, and it is the *only* `mint_act` call site found by grep) — **but it
  has zero callers in the installed package.** The live INIT therefore mints through some other
  path that substitutes the lane identity before signing.
- `QWEN` is not in `ARIFOS_*` env, not in `/etc/arifos/node.env`, and not in the systemd unit
  `Environment=`. The token carries `"lane":"AGI"`, suggesting a harness/lane-derived default.

**This must be traced before any patch.** A fix that hardcodes `"QWEN"` would paper over the
substitution and break every other harness.

## 5. Secondary finding — inconsistent normalization within `verify_act`

Two normalization paths coexist in one function:

- `act_token.py:645-654` (legacy branch): `.lower().strip()` only
- `act_token.py:695-711` (ACT branch): `normalize_actor_id(...) or .lower().strip()`

Since `normalize_actor_id` returns unknown inputs **verbatim**, the ACT branch can compare
`'QWEN'` (uppercase preserved) where the legacy branch would have produced `'qwen'`. Not the cause
of this incident, but the two branches should agree on one canonical form.

## 6. Impact

- **Any agent whose natural actor_id differs from its lane identity cannot use its own session.**
  Blocks the entire governed loop at SENSE for that harness.
- **Fail-closed, not fail-open** — the gate is doing its job; the defect is the *identity
  contract*, not the security posture. No unauthorized access was observed or implied.
- Diagnosis cost measured: **3 wasted kernel calls** before the actor-string hypothesis, because
  "stale token, re-bind" is the natural and wrong reading.
- Also observed this run (distinct, not filed here): `arif_judge` returned
  `ARIF_SESSION_NOT_FOUND` for session `SEAL-40c8dfc726b743ce`, which `arif_observe` and
  `arif_think` had **just accepted**. Session-store and token-verify disagree about the same
  session id.

## 7. Reproduction (read-only, safe)

```
1. POST arif_init  {actor_id: "qwen-code/FI-003", intent: "..."}        -> HOLD, SCT minted
2. POST arif_observe {actor_id: "qwen-code/FI-003", session_id, session_token} -> TOKEN_INVALID (L11)
3. POST arif_init  {intent: "..."}  (fresh session)
4. POST arif_observe {actor_id: "qwen-code/FI-003", ...}               -> TOKEN_INVALID again
5. POST arif_observe {actor_id: "QWEN", ...}                           -> OK
```

## 8. Fix proposal — NOT APPLIED, requires F13

Suggested direction only; **no patch was written and no service was restarted.**

1. **Make INIT report the actor it minted.** Echo `act_claims.actor` back as `actor_id`, or make
   the response's `actor.actor_id` equal the token claim. The response should never contradict its
   own token.
2. **Unify the normalization** on one canonical form used by both branches of `verify_act`.
3. **Register harness/lane aliases** in `normalize_actor_id` (or a companion table) so
   `QWEN` ↔ `qwen-code/*` resolve, instead of adding a hardcoded special case.
4. **Distinguish the failure modes.** `TOKEN_INVALID` currently conflates *bad signature*,
   *actor mismatch*, and (per §6) a session-store miss. Three distinct causes, one string.
5. Add a regression test: mint with a harness-shaped actor, then verify by echoing back the
   `actor_id` the INIT response reported — it must pass.

**F1/F13 note:** this touches the L11 auth path. Constitutional floor change ⇒ F13-only.
Recommended route: chamber protocol, not a direct patch.

## 9. What was NOT done

- No code patched. No service restarted. No redeploy. No `arif_seal`.
- No change to `/root/.config/federation-models.json` (unrelated QRL finding, held separately).
- `forge`/`seal` were present in the tool registry but excluded from this session's `allowed` set;
  they were not called.

## 10. Cross-references

- Memory: `arifos-sct-actor-claim-must-be-echoed-back` (working note + diagnosis procedure)
- Related: `arif-init-observe-only-binding` — the OBSERVE_ONLY bind is *by design*; this incident
  is an identity-string defect on top of a correctly-restrictive gate.
- Session log: `~/.hermes/logs/qrl/2026-10-20.jsonl` (`qrl-20261020-modelreg`, UNSEALED)
