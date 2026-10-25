# RECEIPT — DEPLOY + SEAL PROPOSAL (arifos-78e32fc)

- 2026-10-20, 21:47–22:04 MYT · claude-code-kvm8 (FI-002)
- Deployed by: `scripts/deploy-release.sh` (sanctioned path, its own flock + health gate)
- Kernel authority during the whole session: **OBSERVE_ONLY**. Seal: **not performed** — proposer never self-seals.

## 1. Deploy — what ran

`bash scripts/deploy-release.sh` → build wheel → pip install into `/opt/arifos/current/venv` →
remove stale global → import-path verify → release manifest → `systemctl restart arifos` → health gate → attestation.

| artefact | value |
|---|---|
| release | `arifos-78e32fc` |
| source / built / deployed | `78e32fca2` / `78e32fca2` / `78e32fca2` |
| wheel sha256 | `9825dab6115ee7fc3b264044f52cdc784ea5d181a8b8e398219e14ed509cdf3a` |
| workflow capability hash | `sha256:8822a4d25bc4a7c0b2a7fe9d37497a1aafbac9a87c0982140ed9b56e90a960d3` |
| attestation | `/opt/arifos/releases/attestations/20261020T140120Z-78e32fc.json` |
| service pid | 4000670 |
| canon | `2026.10.20-78e32fc`, integrity ok, 3/3 files |

Deployed module hashes (equal to git HEAD blobs):

```
  0a622287d9ed37ca693f2cbc6ab1fe0e8b03b5a8aa85419d9cf1849026b51d1a  arifosmcp/runtime/mode_contract_gate.py
  3924a4fbf95fc60e4ef0133582b820f6cba9ddbed603d3198fcd5a8755a4a069  arifosmcp/runtime/pre_execution_gate.py
  6781427093dd176789775c019f2144c1ed16c032b163df581b66f37b64b5207d  arifosmcp/abi/mode_contracts.json
  f0aad38f7fb6810f20891dc564e23b4f4d3bd5ae36479ff4bcbecc884463d0a7  scripts/test_contract_gate.py
  dde606ac6b33042c5e7e86a6b6d6cf242967d1f6ae87610d6f246ffc3c3b7e3c  scripts/test_floor_behaviour.py
```

## 2. Post-deploy behavioural evidence (OBS)

Direct call inside the deployed venv, `/opt/arifos/current/venv`:

| tool.mode (claim OBSERVE) | returned |
|---|---|
| `arif_memory.forget` | **IRREVERSIBLE** |
| `arif_forge.commit` | **IRREVERSIBLE** |
| `arif_report.file` | **MUTATE** |
| `arif_route.metabolize` | **ANALYZE** |
| `arif_memory.recall` | OBSERVE (positive control) |
| `arif_forge.dry_run` | OBSERVE (positive control) |
| `arif_think.axioms` | OBSERVE (positive control) |
| `arif_seal.verify` | OBSERVE (positive control) |

Suites on the live release: `test_contract_gate.py` **26/26** (10 gate-integration),
`test_floor_behaviour.py` **6/6**. Regression subset: **25 pass, 1 fail**, the failure
(`test_sct_fallback_is_process_local_random_and_strict_production_holds`) reproduced on the
unpatched baseline — pre-existing, not introduced here. A second pre-existing failure
(`agi_kernel_readiness/test_002_full_init_bound_session`) also reproduced on baseline.

## 3. Attestation gate result — deploy is live, NOT sealed

`Step 9` returned **rc=2 / WARN(score=2)**: every invariant passed except `status = healthy`.

```
✅ release_id arifos-78e32fc · source==built==deployed · drift False
✅ floors_active 13 · contract_drift False · critical modules 18
❌ status = healthy        (actual: degraded)
```

Cause of `degraded` (OBS, `degraded_reasons`): constitutional layer health = degraded because
federation **FQ = 0.375**. Two thresholds disagree:

- `arifos://flow-state` → `t1_fq_floor: 0.3`, `t1_mutation_gate: PASS` (0.375 > 0.3)
- constitutional layer → threshold 0.5 → degraded

Pre-existing and unchanged by this deploy (baseline before deploy was also `degraded`).
This is a real finding: **two conflicting FQ floors in one kernel.**

System floors at proposal time: **pass 9/13, failing F1, F6, F8, unmeasured F5** (OBS from
three independent kernel responses). Cause not investigated here; reported, not explained away.

## 4. Kernel verdict on the seal proposal

`arif_judge(mode=judge, action_class=MUTATE, claim_class=OBS)` →

- `effective_verdict: HOLD` · `reason_code: NEEDS_REVIEW` · `hold_required: true`
- `seal_allowed: false` · `mutation_allowed: false`
- `constitutional_chain_id: cc_081085b914780bdfea65e35ac593229dfd82f394`
- `call_hash: sha256:b6557686db8a6e18d10418543773d6c6c306360109483c39ceac2b11572704eb`
- reason: effective verdict HOLD dominates the intercept; proposing actor is OBSERVE_ONLY
  and the action class is MUTATE.

A first attempt was refused earlier for F7 overclaim (`Overclaim language detected: verified`).
That refusal was correct and is kept in the record: the word "verified" without a per-claim
proof reference is an overclaim, even when the underlying evidence exists.

Seal proposal filed to the peer lane: `report_id rep-67cf3a1a70ae`
(`arif_report`, claim_state SELF_REPORTED).

## 5. What is proved, and what is not

**Proved (OBS):** the artefact on the live service classifies mutating modes at their true
class; the per-tool over-authorisation defect is closed for the four cases above.

**Not proved (UNMEASURED — must not be read as working):**
grant expiry · grant revocation · action-hash binding · retry idempotency.
No valid grant is obtainable at OBSERVE_ONLY; `arif_forge` refuses at the capability-authority
layer before any `constitutional_chain_id` is examined, so a forged and an empty cc_id produce
the identical `888_HOLD`. The six positive-control grant tests therefore remain **unrun**.

**Also not closed:** `arif_route` still declares `modes: []` in `CANONICAL_TOOLS`;
`arif_report` still absent from it (contract_closure verify → `PHANTOM`).

## 6. The seal itself — MENUNGGU ARIF

I did not seal. Per `propose-seal`: the proposer never self-seals; 999 is witness, not
authority; F13 is final for T3. The kernel already refused my proposal (HOLD), so the
correct next move is yours, not another attempt by me.

```
# after Arif's word, from the sovereign lane:
arif_seal(mode=seal, ...) with the F13 seal token
# then verify from an independent reader:
arif_seal(mode=verify)
```

Rollback if the deploy must be reverted: prior release remains under
`/opt/arifos/releases/`; `git revert 78e32fca2` then re-run `deploy-release.sh`.
