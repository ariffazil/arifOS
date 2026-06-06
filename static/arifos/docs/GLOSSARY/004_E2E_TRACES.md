# 004 — E2E agent task traces (Wajib #6)

> Real user → agent → tool → judge → vault flows. Proves the federation
> works as a system, not organ-by-organ. Without this, every organ being
> green is a local maximum, not global.

## Canonical trace 1: GEOX claim → vault seal
```text
1. user asks "is prospect A sealable?"
2. agent routes to GEOX via arif_kernel_route (L01-F13 all pass)
3. geox_evidence_reason(abduction=full, evidence_refs=[…])
4. geox_claim_create(claim_text="…", truth_class=INTERPRETATION)
5. geox_claim_seal(claim_id=clm_…, ack_irreversible=True)
   → bridge: /mcp initialize → tools/call arif_vault_seal
   → canonical: VAULT999 line ++
6. user sees: verdict=SEAL, claim_id, seal_receipt
```

## Canonical trace 2: WEALTH deal → vault seal
```text
1. user asks "is this allocation sound?"
2. agent routes to WEALTH
3. wealth_omni_wisdom(mode=omni, decision_context={…})
4. wealth_boundary_governance(maruah_score=0.7)
5. wealth_hysteresis_ledger(path_params={…}) → sealed path
6. arif_vault_seal → VAULT999 line ++
7. user sees: verdict=SEAL, deal_id, hysteresis_path
```

## Canonical trace 3: WELL readiness → 888 decision
```text
1. user asks "am I fit to decide?"
2. well_assess_homeostasis(mode=fatigue, …)
3. well_validate_vitality(decision_class=C4)
4. if well_score < 0.6: arif_judge_deliberate → 888_HOLD
5. arif_vault_seal(hold_reason="low_vitality")
6. user sees: 888_HOLD pending approval
```

## Canonical trace 4: A-FORGE execution
```text
1. user asks "deploy this build"
2. arif_judge_deliberate(candidate=plan, irreversibility=high)
3. arif_forge_execute(ack_irreversible=True, judge_state_hash=…)
4. A-FORGE 4-layer gate: F1 → capability → F3/F6/F9 → approval
5. arif_vault_seal(forge_receipt=…)
6. user sees: SEAL, build_id, vault_entry_id
```

## Canonical trace 5: arifOS self-attestation
```text
1. /health: tools_loaded, runtime_drift, owner_summary
2. /mcp: tools/list returns 13 canonical tools
3. /.well-known/mcp.json returns server card
4. arif_ops_measure: thermodynamic entropy delta
5. arif_vault_seal(state_attestation=…)
6. user sees: GREEN/owner_summary, sealed attestation receipt
```

## Target: 30 canonical traces.
