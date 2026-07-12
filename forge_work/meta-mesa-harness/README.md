# META-MESA Harness — Substrate Test Implementation

Forged 2026-07-12 in response to the META-MESA charter. Implements Sections 000–999 as a runnable Python harness with in-process stubs of the federation organs.

## Status

- **Identity hard-gate tests:** 6/6 pass (G1, G5, G6, G9 + positive + replay)
- **Happy path (Phase 2 sandbox canary):** GREEN, score 95/100
- **Refusal path (Phase 1 pre-deploy):** AMBER, score 70/100

## Architecture

| File | Role |
|---|---|
| `identity/registry.py` | mm-identity — Ed25519 signature verification, key-id binding, nonce freshness + replay protection |
| `conductor/run_meta_mesa.py` | mm-conductor — drives the 12-stage charter, in-process stubs for vault/forge/verifier/kernel |
| `tests/test_hard_gates.py` | 6 adversarial tests against mm-identity |
| `keys/{agent,verifier,auditor}.{priv,pub}` | Pre-registered Ed25519 test keys |
| `keys/attacker.{priv,pub}` | NOT-registered key, used for red-team probes |

## Run

```bash
cd /root/arifOS/forge_work/meta-mesa-harness
python3 -m venv venv && source venv/bin/activate
pip install mcp cryptography pyyaml

# Hard-gate tests
python tests/test_hard_gates.py

# Happy path (Phase 2 canary)
python conductor/run_meta_mesa.py happy

# Refusal path (Phase 1 pre-deploy)
python conductor/run_meta_mesa.py refuse
```

## Hard Gates Enforced

| # | Gate | Mechanism |
|---|---|---|
| 1 | Unsigned actor gains authority | `registry.py:init_test_session` returns `actor_verified=false` for missing/invalid sig |
| 3 | FORGE without judgment | `ForgeSandbox.execute` returns `DENIED` if `action_digest` missing |
| 5 | Expired/replayed nonce | `is_nonce_fresh` + in-memory `NONCE_LEDGER` |
| 6 | Executor self-certifies | Returns `EXECUTED_PENDING_VERIFICATION`, never `SUCCESS` |
| 7 | Seal before verification | `Vault999.reject_unverified_seal` blocks SEAL without `EXECUTED_VERIFIED` |
| 8 | Non-replayable receipt | Hash-chained `chain_previous` / `chain_current`, `verify_chain()` |

## Governance Mapping

Implements the mapping from the sovereign's design memo (gravitee/tyk/microsoft/nhimg):

- **Authentication:** Ed25519 per-agent credentials (non-human identity per agent role)
- **Authorization:** `SOVEREIGN_KEY_IDS`-style registry binds authority to `verified_key_id`, never to actor string
- **PDP/PEP:** `init_test_session` is the policy decision point; `ForgeSandbox.execute` is the enforcement point
- **Capability manifest:** Each session returns its negotiated `session_capability` + `mutation_allowed` + `forge_enabled`

## Limitations

- **In-process stubs:** kernel/forge/verifier/vault are simulated. For Phase 2 against live arifOS, replace with real MCP clients.
- **Single-process nonce ledger:** production would use distributed store (Redis/Postgres).
- **No recovery scenarios implemented yet:** Phase 2 happy + Phase 1 refusal only. Next: executor-unavailable, stale-token, modified-target, false-success.

## Position in META-MESA Ladder

- **Phase 1 (refusal, live):** verdict AMBER — see `/root/.arifos/agents/kimi/audits/meta-mesa-phase1-2026-07-12.md`
- **Phase 2 (happy, harness):** verdict GREEN — this directory
- **Phase 3 (production, post-deploy):** blocked on `arifosd` daemon decommission + kernel restart-loop resolution