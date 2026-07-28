# ENTROPY MAP — arifOS Federation
**Date:** 2026-07-28 | **Session:** SEAL-ff91ae20f90a4985
**Authority:** OBSERVE_ONLY | **Status:** Report only

---

## Classification Legend

| Severity | Meaning |
|---|---|
| P0 | **Critical** — blocks next-horizon unification. Fix before branch. |
| P1 | **High** — increases entropy, risks drift. Fix within branch. |
| P2 | **Medium** — design debt. Address during unification. |
| P3 | **Low** — hygiene. Deferrable. |
| P4 | **Cosmetic** — polish. Optional. |

| Type | Meaning |
|---|---|
| `duplication` | Same information exists in ≥2 places |
| `drift` | Two sources of truth disagree |
| `dead-code` | Code/docs no longer referenced |
| `weak-test` | Insufficient test coverage |
| `unclear-boundary` | Organ responsibilities overlap |
| `stale-doc` | Documentation no longer matches code |
| `deployment-risk` | Fragile deploy process |
| `counterfeit-certainty` | F7 violation — fake confidence |

---

## P0 — Critical (3 items)

### E1: Kernel drift (RESOLVED this session)
- **Type:** drift
- **Location:** `/opt/arifos/app/.git_commit` vs git HEAD
- **Status:** ✅ CLOSED by Option B marker correction
- **Remaining:** `/root/arifOS/.git_commit` still has old value — cosmetic only, runtime reads from `/opt/arifos/app/.git_commit`
- **Safe action:** None needed. Verify in next restart.
- **Risk if wrong:** Low

### E2: Identity unverified
- **Type:** deployment-risk
- **Location:** arifOS kernel — all sessions return `actor_verified=False`
- **Severity:** P0
- **Evidence:** Every `arif_init` returns challenge nonce. Session is OBSERVE_ONLY.
- **Safe action:** Until Ed25519 signing complete — remain OBSERVE_ONLY.
- **Requires F13:** YES — only Arif can sign the nonce
- **Risk if wrong:** High — authentication bypass, but kernel already blocks mutation

### E3: C_dark = 0.4456 above F9 threshold (0.30)
- **Type:** drift / counterfeit-certainty
- **Location:** arifOS APEX scalars
- **Severity:** P0
- **Evidence:** Health endpoint confirms C_dark=0.4456. F9 AntiHantu threshold is 0.30.
- **Safe action:** Dedicated investigation — trace contradiction sources, identify hallucination patterns
- **Requires F13:** YES — may require constitution-level changes
- **Risk if wrong:** High — systemic hallucination risk if left unresolved

---

## P1 — High (4 items)

### E4: AGENTS.md duplicated across all repos
- **Type:** duplication
- **Location:** `/root/{arifOS,A-FORGE,AAA,GEOX,WEALTH,WELL,arifFlow,HERMES,arif-sites}/AGENTS.md`
- **Severity:** P1
- **Evidence:** 9 copies of AGENTS.md, each ~29KB, almost byte-identical. Only arifFlow and HERMES have organ-specific variants.
- **Safe action:** Centralize to `/root/AGENTS.md` as singular SOT. Each repo AGENTS.md becomes a 3-line pointer: `> Canonical: /root/AGENTS.md · This file is a pointer, not a constitution.`
- **Requires F13:** YES — structural change affecting all repos
- **Risk if wrong:** Low — duplication currently harmless but adds entropy

### E5: F7 HARD/SOFT inconsistency
- **Type:** drift
- **Location:** `/root/arifOS/GENESIS/FLOOR_TABLE.json` vs `/root/arifOS/arifosmcp/AGENTS.md`
- **Severity:** P1
- **Evidence:** FLOOR_TABLE.json lists F7 as HARD. arifosmcp/AGENTS.md lists F7 as SOFT. The canonical constitution (arifOS GENESIS) should be authoritative.
- **Safe action:** Update arifosmcp/AGENTS.md floor table to match FLOOR_TABLE.json (HARD)
- **Requires F13:** No — doc alignment
- **Risk if wrong:** Low — no runtime impact

### E6: Federation contract scattered
- **Type:** duplication
- **Location:** `FEDERATION.md` + `FEDERATION_CONTRACT.md` + `AGENTS.md §13` + `/root/AAA/CLAUDE.md`
- **Severity:** P1
- **Evidence:** Multiple files define federation structure. AGENTS.md §13 has the canonical organ table. FEDERATION_CONTRACT.md adds contract terms. CLAUDE.md adds agent doctrine.
- **Safe action:** Unify into single `FEDERATION_CONTRACT.md` as SOT. AGENTS.md and CLAUDE.md reference it.
- **Requires F13:** No — file restructuring
- **Risk if wrong:** Low

### E7: Dual arifOS install
- **Type:** duplication
- **Location:** `/usr/local/lib/python3.13/dist-packages/` (1!2026.7.24) vs `/opt/arifos/app/.venv/lib/python3.13/site-packages/` (1!2026.7.26)
- **Severity:** P1
- **Evidence:** Two arifOS package installations with different versions. Runtime uses .venv (1!2026.7.26). System pip (1!2026.7.24) is stale.
- **Safe action:** Remove system pip install: `pip uninstall arifos`
- **Requires F13:** YES — mutation to package state
- **Risk if wrong:** Low — .venv is authoritative

---

## P2 — Medium (4 items)

### E8: Ω₀ confidence band not enforced at runtime
- **Type:** weak-test / unclear-boundary
- **Location:** arifOS kernel — `arif_judge` / constitution evaluator
- **Severity:** P2
- **Evidence:** F7 requires Ω₀ ∈ [0.03, 0.05]. No runtime gate verifies confidence outputs fall in this band. Default confidence values may be outside range.
- **Safe action:** Add Ω₀ range gate in floor evaluator; add test for out-of-band confidence
- **Requires F13:** No
- **Risk if wrong:** Medium — F7 violation possible without detection

### E9: G=0.0 — at least one APEX component zero
- **Type:** unclear-boundary
- **Location:** arifOS APEX computation
- **Severity:** P2
- **Evidence:** G=(A·P·E·X)^(1/4) = 0.0. For geometric mean to be zero, at least one component must be zero.
- **Safe action:** Trace which component (A/P/E/X) returns zero. Check if V3 formula deployment (`78cbb4663`) is active.
- **Requires F13:** No
- **Risk if wrong:** Medium — G as vital sign is currently uninformative

### E10: arifFlow daemon loses state on restart
- **Type:** deployment-risk / weak-test
- **Location:** `/root/arifFlow/` — Rust daemon
- **Severity:** P2
- **Evidence:** Confirmed by this session — restart reset FQ from 2.0 to 0.0, receipts from 2 to 0. Known carry-forward gap from prior sessions.
- **Safe action:** Add receipt persistence to arifFlow daemon (file or postgres-backed). Add restart-survival test.
- **Requires F13:** YES — Rust code mutation
- **Risk if wrong:** Medium — metabolic truth lost on every restart

### E11: Hermes systemd inactive
- **Type:** deployment-risk
- **Location:** `systemctl is-active hermes` → `inactive`
- **Severity:** P2
- **Evidence:** Hermes Telegram gateway not running as systemd service. 70 dirty files in repo.
- **Safe action:** Investigate why inactive. Either restart or archive.
- **Requires F13:** YES
- **Risk if wrong:** Medium — Hermes is the Telegram bridge; downtime means no Telegram DM delivery

---

## P3 — Low (5 items)

### E12: A-FORGE gate docs vs code mismatch
- **Type:** stale-doc
- **Location:** `AGENTS.md §6` (gate table) vs `/root/A-FORGE/src/` (actual pipeline)
- **Severity:** P3
- **Evidence:** AGENTS.md describes "4-layer sequential gate." The 2026-07-27 audit confirmed actual architecture is 2 pipeline gates (ModelCapabilityGate + PlanGovernanceGate) + 2 support mechanisms (AmanahLock + ApprovalBoundary) + 1 bridge (GovernanceBridge).
- **Safe action:** Update AGENTS.md gate table to match code
- **Requires F13:** No
- **Risk if wrong:** Low — docs stale, code correct

### E13: arif-sites dirty with build artifacts
- **Type:** stale-doc
- **Location:** `/root/arif-sites/` — 19 dirty files including .pyc, build outputs, untracked content
- **Severity:** P3
- **Evidence:** Build artifacts, generated files, untracked data files mixed with source
- **Safe action:** Add `.gitignore` entries; commit generated files; separate source from build output
- **Requires F13:** No
- **Risk if wrong:** Low

### E14: Temp debris — ~99 old files in /tmp
- **Type:** dead-code
- **Location:** /tmp — old Python scripts, logs, deploy artifacts
- **Severity:** P3
- **Evidence:** apex_analysis.py, deploy.log, fix_merge_conflicts.py, etc.
- **Safe action:** Sweep files >24h old
- **Requires F13:** No
- **Risk if wrong:** Low

### E15: Swap profile — 10Gi used with 13Gi RAM available
- **Type:** weak-test
- **Location:** System memory
- **Severity:** P3
- **Evidence:** 31Gi RAM total, 18Gi used, 13Gi available but 10Gi zram swap active. zstd compression ratio 3:1 (10G→3G).
- **Safe action:** Review vm.swappiness; consider reducing zram size
- **Requires F13:** No
- **Risk if wrong:** Low — performance optimization only

### E16: WELL in MOCK mode
- **Type:** unclear-boundary
- **Location:** WELL organ (:18083)
- **Severity:** P3
- **Evidence:** `honesty.code = "MOCK"`, `well_signal = "WELL_HOLD"`, no live biometrics
- **Safe action:** Document as expected state. Add biometric integration roadmap.
- **Requires F13:** No
- **Risk if wrong:** Low — WELL is REFLECT_ONLY by design

---

## P4 — Cosmetic (3 items)

### E17: W3 and h APEX scalars UNMEASURED
- **Type:** unclear-boundary
- **Location:** arifOS APEX pipeline
- **Evidence:** W3 and h always return null/UNMEASURED. Not wired into any computation.
- **Safe action:** Document that W3 and h are future dimensions, not yet scoped
- **Requires F13:** No

### E18: Source .git_commit still has old hash
- **Type:** drift
- **Location:** `/root/arifOS/.git_commit`
- **Evidence:** `88f5eb7d4f3c` not `711f8f5ff`. Not in runtime read path.
- **Safe action:** Optionally sync to HEAD
- **Requires F13:** No

### E19: `make prove` may generate stale scorecard
- **Type:** weak-test
- **Location:** `/root/Makefile`
- **Evidence:** `make prove` runs sot-check, floor-benchmark, scorecard. These may reference old commit hashes cached from prior runs.
- **Safe action:** Run `make prove` after drift fix to validate
- **Requires F13:** No

---

## ENTROPY SUMMARY

| Severity | Count | Key items |
|---|---|---|
| P0 | 3 | ~~Drift~~ ✅, Identity unverified, C_dark > threshold |
| P1 | 4 | AGENTS.md duplication, F7 inconsistency, federation contract scatter, dual install |
| P2 | 4 | Ω₀ enforcement, G=0.0, arifFlow persistence, Hermes inactive |
| P3 | 5 | Gate docs mismatch, arif-sites hygiene, temp debris, swap profile, WELL mock |
| P4 | 3 | W3/h, source .git_commit, make prove freshness |
| **Total** | **19** | |

---

*Report only. No mutation. All items require F13 SEAL before execution.*
