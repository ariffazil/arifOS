# PATCH PROPOSAL — Staged Patch Sets P0–P6
**Date:** 2026-07-28 | **Session:** SEAL-ff91ae20f90a4985
**Authority:** OBSERVE_ONLY | **Status:** Proposed (not applied)

---

## Execution Rule

Do not apply patches until F13 says:

```
SEAL: EXECUTE PATCH SET [Px]
```

Each patch set is atomic — execute all or none. Rollback procedure documented per set.

---

## P0 — Authority and Drift (1 item remaining)

| Item | P0-1: Identity verification |
|---|---|
| **Status** | Identity unverified. Nonce: `BwmPIyZSgFneSYAnOT1JdF_W8EmD7sBwQ-L4EqSuFnc` |
| **Action** | Sign nonce with your Ed25519 private key, re-init with signature |
| **Files** | None — kernel protocol only |
| **Command** | `arif_init(mode='init', actor_signature=<sig>, nonce="BwmPIyZSgFneSYAnOT1JdF_W8EmD7sBwQ-L4EqSuFnc")` |
| **Risk** | LOW — kernel validates signature before granting authority |
| **Rollback** | Re-init without signature → OBSERVE_ONLY restored |
| **Requires F13** | ✅ YES — only you hold the private key |

---

## P1 — Canonical Contracts (5 items)

### P1-1: AGENTS.md consolidation

| Field | Value |
|---|---|
| **Action** | Reduce 9 copies of AGENTS.md to 1 canonical + 8 pointers |
| **Files** | `/root/{A-FORGE,AAA,GEOX,WEALTH,WELL,arifFlow,HERMES,arif-sites}/AGENTS.md` |
| **Type** | Doc edit — replace 29KB copy with 3-line pointer |
| **Command** | `patch each AGENTS.md to: > **Canonical:** /root/AGENTS.md · This file is a pointer, not a constitution.` |
| **Risk** | LOW — doc-only |
| **Rollback** | `git checkout main -- AGENTS.md` |
| **Requires F13** | ✅ YES — structural |

### P1-2: F7 HARD/SOFT alignment

| Field | Value |
|---|---|
| **Action** | Update `arifosmcp/AGENTS.md` floor table — F7 = HARD |
| **Files** | `/root/arifOS/arifosmcp/AGENTS.md` |
| **Type** | Doc edit — one cell change |
| **Risk** | LOW |
| **Requires F13** | No |

### P1-3: Federation contract unification

| Field | Value |
|---|---|
| **Action** | Merge FEDERATION.md + FEDERATION_CONTRACT.md → single SOT |
| **Files** | `/root/FEDERATION_CONTRACT.md` |
| **Type** | Doc restructure |
| **Risk** | LOW |
| **Requires F13** | No |

### P1-4: Dual arifOS install cleanup

| Field | Value |
|---|---|
| **Action** | `pip uninstall arifos` — remove system-level install, keep .venv |
| **Type** | Package management |
| **Risk** | LOW — .venv is authoritative |
| **Requires F13** | ✅ YES — mutation |

### P1-5: Source .git_commit sync

| Field | Value |
|---|---|
| **Action** | `git rev-parse HEAD > /root/arifOS/.git_commit` |
| **Type** | Single-line file write |
| **Risk** | LOW — cosmetic |
| **Requires F13** | No |

---

## P2 — Gödel Lock / F7 Bridge (3 items)

### P2-1: Ω₀ confidence band enforcement

| Field | Value |
|---|---|
| **Action** | Add Ω₀ range gate in floor evaluator (`arif_judge`). Reject SEAL if Ω₀ ∉ [0.03, 0.05] |
| **Files** | `/root/arifOS/arifosmcp/runtime/kernel/judge.py` |
| **Type** | Code mutation — add floor check |
| **Risk** | MEDIUM — may block legitimate SEALs if Ω₀ computed incorrectly |
| **Tests** | `test_floor_f7_omega_band` |
| **Rollback** | `git revert` + systemctl restart arifos |
| **Requires F13** | No |

### P2-2: Overclaim phrase detection

| Field | Value |
|---|---|
| **Action** | Add output filter for absolute-certainty phrases without proof reference |
| **Files** | `/root/arifOS/arifosmcp/runtime/kernel/interceptor.py` |
| **Type** | Code mutation — add output gate |
| **Risk** | MEDIUM — may produce false positives on legitimate certainty |
| **Tests** | `test_interceptor_overclaim_blocked`, `test_interceptor_legitimate_certainty_passes` |
| **Requires F13** | No |

### P2-3: Self-certification blocker

| Field | Value |
|---|---|
| **Action** | Ensure `arif_judge` cannot pass when caller == actor |
| **Files** | `/root/arifOS/arifosmcp/runtime/governance_pipeline.py` |
| **Type** | Code mutation — identity check |
| **Risk** | LOW — existing identity check can be extended |
| **Requires F13** | No |

---

## P3 — arifFlow Metabolism (2 items)

### P3-1: Receipt persistence

| Field | Value |
|---|---|
| **Action** | Add receipt persistence to arifFlow daemon (file-backed or postgres) |
| **Files** | `/root/arifFlow/src/` (Rust) |
| **Type** | Code mutation — Rust daemon |
| **Risk** | MEDIUM — restart-survival changes may affect BSP scheduling |
| **Tests** | `test_receipt_survives_restart` |
| **Rollback** | Revert + cargo build --release + restart arifflow |
| **Requires F13** | ✅ YES — Rust code mutation |

### P3-2: FQ telemetry surfacing

| Field | Value |
|---|---|
| **Action** | Expose FQ history (last 100 values) via arifFlow health endpoint |
| **Files** | `/root/arifFlow/src/` (Rust) |
| **Type** | Code mutation — endpoint data |
| **Risk** | LOW — read-only endpoint |
| **Requires F13** | ✅ YES — code mutation |

---

## P4 — A-FORGE Execution Governance (2 items)

### P4-1: Gate docs aligned to code

| Field | Value |
|---|---|
| **Action** | Update AGENTS.md §6 gate table to match actual 2-gate pipeline |
| **Files** | `/root/AGENTS.md` (canonical) |
| **Type** | Doc edit |
| **Risk** | LOW |
| **Requires F13** | No |

### P4-2: Dry-run default documentation

| Field | Value |
|---|---|
| **Action** | Add `dry_run` as default mode in arif_forge tool description and A-FORGE README |
| **Files** | `/root/A-FORGE/README.md`, arif_forge tool docs |
| **Type** | Doc edit |
| **Risk** | LOW |
| **Requires F13** | No |

---

## P5 — AAA Coordination Hygiene (1 item)

### P5-1: No-self-seal enforcement

| Field | Value |
|---|---|
| **Action** | Add `no-seal` ACL to AAA agent card. Verify at A2A gateway. |
| **Files** | `/root/AAA/contracts/agent-cards/` |
| **Type** | Config/doc |
| **Risk** | LOW |
| **Requires F13** | No |

---

## P6 — Integration Tests (5 items)

| Item | Test | Organs | Type |
|---|---|---|---|
| P6-1 | Federation e2e: init→observe→think→judge→forge→seal→verify | arifOS, A-FORGE | E2E test |
| P6-2 | Receipt e2e: A-FORGE→arifFlow→persist→recover | A-FORGE, arifFlow | E2E test |
| P6-3 | Rollback e2e: seal reversion→verify state | arifOS | E2E test |
| P6-4 | Identity e2e: challenge→sign→verify→F13 authority | arifOS | E2E test |
| P6-5 | Overclaim blocker e2e: certainty phrase→HOLD | arifOS | E2E test |

**All P6 items:** Test files only. No production mutation. LOW risk.

---

## Patch Summary

| Set | Items | Type | Risk | F13 Required |
|---|---|---|---|---|
| P0 | 1 | Protocol (identity) | LOW | ✅ |
| P1 | 5 | Doc + config | LOW | ✅ (1 of 5) |
| P2 | 3 | Code mutation | MEDIUM | No |
| P3 | 2 | Code mutation (Rust) | MEDIUM | ✅ |
| P4 | 2 | Doc | LOW | No |
| P5 | 1 | Config | LOW | No |
| P6 | 5 | Test files | LOW | No |
| **Total** | **19** | | | |

---

*Nothing applied. Nothing pushed. Awaiting F13 SEAL per patch set.*
