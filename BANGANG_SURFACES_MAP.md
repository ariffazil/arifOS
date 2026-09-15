# BANGANG Surfaces Map — arifOS Kernel

> **BANGANG** (Malay: gap, opening, breach) — surfaces where autonomous decision paths, override logic, bypass gates, auto-execution, and governance exemption exist in the arifOS kernel.

**Forged:** 2026-07-29  
**Source:** `/root/arifOS/` — exhaustive code search  
**Scope:** All `.py` files, Makefile, scripts/, GENESIS/ dir

---

## 1. TIER CLASSIFICATION (T1/T2/T3)

Three conformance tiers document what must-never-happen vs. what is known-missing:

### T1: Must-Never-Happen Invariants (14 items)
*File: `conformance/T1_MUST_NEVER_HAPPEN_XFAIL.py`*

All 14 T1 invariants are `xfail(strict=True)` — the test *is* the specification; enforcement is not yet in kernel code:

| ID | Invariant | Current State | BANGANG Surface |
|----|-----------|---------------|-----------------|
| T1-01 | Kernel must never SEAL own actions | No `kernel_actor != seal_actor` check at arif_seal entry | **Self-seal:** kernel could authenticate+seal its own irreversible actions without external Gödel-lock witness |
| T1-02 | Forge must never adjudicate | forge_execute routes through arif_judge by convention, not hard block | **Forge→Judge boundary:** A-FORGE could emit verdict-bearing output without kernel hard-block |
| T1-03 | Anonymous never mutates | Session gate is per-tool, not kernel-level | **Anonymous mutation:** unauthenticated actors could reach MUTATE-class tools without global gate |
| T1-04 | Cross-organ session boundary | SCT v1 validates at ingress only | **Session hopping:** tokens not re-validated at each organ hop (arifOS→A-FORGE→GEOX) |
| T1-05 | VAULT999 immutability | Direct filesystem writes to VAULT999 not kernel-blocked | **Direct vault write:** code paths could write to VAULT999/ outside arif_seal |
| T1-06 | WELL never diagnoses | Output validation not kernel-enforced | **Organ boundary drift:** WELL could emit diagnostic claims despite REFLECT_ONLY doctrine |
| T1-07 | GEOX never adjudicates | Convention-only, no output validation | **Organ boundary drift:** GEOX could emit SEAL/HOLD/SABAR/VOID in output |
| T1-08 | WEALTH never allocates | Convention-only, no output validation | **Organ boundary drift:** WEALTH could emit allocation/transfer directives |
| T1-09 | No floor bypass | Some internal execution paths may skip FloorEnforcer.check() | **Floor evasion:** execution path enumeration incomplete |
| T1-10 | No direct vault write outside arif_seal | No filesystem guard | **Vault escape:** direct writes to outcomes.jsonl, seal_chain.jsonl |
| T1-11 | Cooling record immutability | Append-only not hash-chain enforced | **Cooling tamper:** deletion/modification undetectable |
| T1-12 | No organ impersonation | identity.toml exists but cryptographically unenforced at bridge | **Impersonation:** organ could claim another's identity_hash |
| T1-13 | Seal chain integrity | Chain verifier exists (seal_chain.js) but not enforced at seal time | **Broken chain:** broken hash links could be appended |
| T1-14 | RSI self-modification gate | No cooling gate with external_witness_ref enforcement | **Self-modification:** skill upgrades/code changes bypass cooling |

### T2: Known Gaps (documented in T1 tests as "requires T2")
Enforcement level where **kernel code should exist** but doesn't yet — 13 of 14 T1 items are marked T2.

### T3: WAJIB — F13-Ratified Primitives (9 items)
*File: `conformance/T3_WAJIB_XFAIL.py`*

All WAJIBs require F13-ratified constitutional primitives:

| ID | Requirement | BANGANG Surface |
|----|-------------|-----------------|
| WAJIB-2 | Independent verification lane (verifier ≠ executor) | Single-actor verification — same entity could verify own work |
| WAJIB-4 | Delegation attenuation (child ⊆ parent authority) | No signed delegation envelope — child could exceed parent authority |
| WAJIB-5 | Fire-time reauthorization | Deferred actions judged once at write-time, not re-judged at fire-time; no grandfathered-authority guard |
| WAJIB-7 | Organ disagreement resolution | Conflicts resolved silently (no hard veto, blast-radius precedence, Pareto search, F13 escalation) |
| WAJIB-8 | Context-capture governance (agents can't write own law) | context_manifest validator exists but not wired into boot path |
| WAJIB-10 | End-to-end federation canary | Depends on all prior WAJIBs |

---

## 2. GOVERNANCE IDENTITY & AUTHENTICATION SURFACES

### 2a. Protected Sovereign Identity
*File: `arifosmcp/runtime/governance_identity.py`*

**Defined:** `PROTECTED_SOVEREIGN_IDS = {"arif", "ariffazil", "sovereign", "admin", "root", "system", "arif-fazil", "arif_fazil", "muhammad_arif"}`

**Gate surface:**
- `VerificationMethod`: `IDENTITY_CLAIM` (recognized, NOT verified) vs `ED25519_SIG` (verified)
- Semantic phrase removal: old `IDENTITY_PHRASES` hash-based bypass was removed (2026-07-06) — was dead code but a liability
- `SOVEREIGN_KEY_IDS` contains only 2 Ed25519 keys — limited key rotation
- `VERIFIED_KEY_IDS` maps bounded actors — key enumeration possible for identifying all authorized actors

**BANGANG surface:** Identity claim (non-cryptographic) is recognized but NOT verified. `ack_irreversible=True` path on `arif_init` can bypass signature requirement.

### 2b. Ed25519 Forge Gate (P1)
*File: `arifosmcp/runtime/forge_preflight.py` lines 263-357*

**Gate surface:**
- Ed25519 signature verification at forge gate (Stage 3b)
- Only required for MUTATE modes (engineer, write, generate, commit, deploy)
- OBSERVE_ONLY modes **skip this gate entirely**
- Secondary HMAC check on `session_id:seal_verdict_id:approved_action_hash` is **non-blocking** (exception-safe)
- If `_verify_ed25519_proof` is missing, **fail closed → HOLD** (correct behavior)

**BANGANG surface:** The HMAC secondary check uses a try/except **pass** — exceptions are silently swallowed. Full Ed25519 per-seal signing "is the next hardening step" (line 344).

---

## 3. THE 12-STAGE FORGE PREFLIGHT PIPELINE
*File: `arifosmcp/runtime/forge_preflight.py` lines 1194-1407*

The BANGANG surfaces in each stage:

| Stage | Gate | Current State | BANGANG Surface |
|-------|------|---------------|-----------------|
| 1 | Session Token Validation | SCT signature + expiration verified | Valid session → any SCT passes |
| 2 | Actor/Session Binding | Standing resolved | No cross-organ re-validation |
| 3 | Authority Recomputation (G1) | Recomputed from SCT/store | Trusts SCT standing dict |
| 3b | Ed25519 Forge Gate (P1) | Signature verify for MUTATE modes | OBSERVE_ONLY bypasses entirely; HMAC fallback is non-blocking/pass |
| 4 | Judge State Retrieval | Judge state fetched | Requires judge_state_hash existence |
| 5 | Judge Hash Recomputation | Recompute from judge state | Match-or-fail, hard |
| 6 | Constitutional Chain Validation | Chain ID vs judge state | Hard check |
| 7 | Vault Receipt Check (G8) | Receipt existence + replay detection | Hard gate |
| 8 | Plan/Manifest Binding | Plan_id bound | Hard gate |
| 9 | Reversibility Classification | Mode + manifest analysis | Determines `human_ack_required` |
| 10 | Human Acknowledgement (G10) | `ack_irreversible` + nonce check | `ack_irreversible=False` with required=False → no HOLD |
| 11 | Dry-Run Simulation | Non-mutating simulation | Hard pass-through |
| 12 | Execution or HOLD (Final Gate) | Aggregates all prior stage results | If any stage failed → HOLD; But: Stage 7 replay/Stage 10 replay both set `replay_detected=True` without necessarily HOLDing on its own |
| G4 | Sealed Forge Plan Validation | Vault receipt needed for commit mode | Hard gate |
| G5 | Schema Validation | Fields validated | Hard gate |
| G6 | Scar Consultation | Scars fetched and surfaced | Advisory only (surfaced in receipt, not blocking) |

**Key BANGANG: Stage 7 and Stage 10 both set `replay_detected` but the final gate (Stage 12) aggregates all results — if replay is detected but set to `True` without a blocking `reason_code`, it's surfaced but may not block.**

---

## 4. `arif_act` — THE 900 EXECUTION GATE
*File: `arifosmcp/runtime/tools.py` lines 22381-22490*

**THE most critical BANGANG surface.** `arif_act` is the final execution gate that requires both `seal_verdict_id` and `approved_action_hash`:

```python
# 1. Hard structural gate
if not seal_verdict_id or not approved_action_hash:
    return 888_HOLD  # ✓ correct — hard gate

# 2. Cryptographic A2ASealVerifier
req = SealVerificationRequest(session_id, verdict="SEAL", state_hash=approved_action_hash)
resp = verifier.verify_seal(req)
if not resp.valid or resp.verdict != "SEAL":
    return 888_HOLD  # ✓ correct — cryptographic gate
```

**BANGANG surfaces identified:**

1. **Verdict-state gate** (lines 22430-22461): After proving cryptographic seal anchoring, the verdict STATE is checked via `DYNAMIC_EXECUTOR_CONSTRAINTS["verdict_gates"]`. If the import fails (`except ImportError: pass`), **execution falls through to forge** without the verdict-state check — a valid SABAR or HOLD seal could be replayed to trigger execution.

2. **`approved_action_hash` truncation** (line 22477): Display shows only first 16 chars — audit/debug surface.

3. **Tool contract defines** (lines 595-617):
   - `agency_level`: `L5_EXECUTE_IRREVERSIBLE`
   - `blast_radius`: `high`
   - `requires_human_confirmation`: `True`
   - `restraint_level`: `STRICT`
   - `verdict_loop_required`: `True`
   
   BUT these are contract metadata — enforcement depends on the gates above.

---

## 5. AUTONOMY CONTRACTION MATRIX (E7 — PRINCIPAL PARADOX)
*File: `arifosmcp/runtime/principal_paradox.py` lines 192-222*

16-row contract table mapping `(risk_tier, blast_radius, reversibility_floor) → autonomy_tier`:

```
Risk     | Blast            | Rev Floor | Autonomy Tier
---------|------------------|-----------|---------------
LOW      | LOCAL            | 0.90      | FULL_AUTO
LOW      | ACCOUNT          | 0.85      | FULL_AUTO
LOW      | ORG              | 0.80      | PROPOSE_ONLY
LOW      | PUBLIC           | 0.70      | PROPOSE_ONLY
LOW      | MARKET           | 0.60      | PRINCIPAL_APPROVAL_REQUIRED
LOW      | INFRASTRUCTURE   | 0.50      | PRINCIPAL_APPROVAL_REQUIRED
LOW      | CIVILIZATIONAL   | 0.30      | HOLD
MEDIUM   | LOCAL            | 0.70      | FULL_AUTO
MEDIUM   | ACCOUNT          | 0.70      | PROPOSE_ONLY
MEDIUM   | ORG              | 0.70      | PROPOSE_ONLY
MEDIUM   | PUBLIC           | 0.50      | PRINCIPAL_APPROVAL_REQUIRED
MEDIUM   | MARKET           | 0.50      | PRINCIPAL_APPROVAL_REQUIRED
MEDIUM   | INFRASTRUCTURE   | 0.30      | HOLD
MEDIUM   | CIVILIZATIONAL   | 0.10      | HOLD
HIGH     | LOCAL            | 0.50      | PROPOSE_ONLY
HIGH     | ACCOUNT          | 0.50      | PRINCIPAL_APPROVAL_REQUIRED
HIGH     | ORG              | 0.50      | PRINCIPAL_APPROVAL_REQUIRED
HIGH     | PUBLIC           | 0.30      | PRINCIPAL_APPROVAL_REQUIRED
HIGH     | MARKET           | 0.20      | HOLD
HIGH     | INFRASTRUCTURE   | 0.00      | HOLD
HIGH     | CIVILIZATIONAL   | 0.00      | HOLD
ATOMIC   | LOCAL            | 0.50      | PRINCIPAL_APPROVAL_REQUIRED
ATOMIC   | ACCOUNT          | 0.50      | PRINCIPAL_APPROVAL_REQUIRED
ATOMIC   | ORG              | 0.30      | PRINCIPAL_APPROVAL_REQUIRED
ATOMIC   | PUBLIC           | 0.20      | HOLD
ATOMIC   | MARKET           | 0.10      | HOLD
ATOMIC   | INFRASTRUCTURE   | 0.00      | HOLD
ATOMIC   | CIVILIZATIONAL   | 0.00      | HOLD
```

**BANGANG surfaces in evaluate_autonomy_ceiling():**

1. **Guard 0: Principal direct access → FULL_AUTO** (line 259-271): If `caller_is_principal=True`, ALL gates bypassed. No ceiling. No surge protection. No reversibility check. **Total autonomy for any claimed principal.**

2. **Guard 1: No lease → HOLD** (line 273): Hard gate — but if lease system is compromised, this guard falls.

3. **Guard 2: Reversibility hard floor** (line 288): `REVERSIBILITY_HARD_FLOOR = 0.3` — below this → HOLD. But this is a constant, not context-aware.

4. **OBSERVE class always FULL_AUTO** (line 347): Read-only tools bypass autonomy contraction entirely. If an OBSERVE tool has undocumented side effects, they run unrestricted.

5. **Surge protection** (lines 303-344): `MAX_OVERRIDES_PER_HOUR = 3`, downgrades one tier. If already at HOLD, stays HOLD. Effective but counts only from in-memory tracker — lost on restart.

6. **`_downgrade_tier`** (lines 382-394): Single-step progression: `FULL_AUTO → PROPOSE_ONLY → PRINCIPAL_APPROVAL_REQUIRED → HOLD`. If `tier not in order` (ValueError), falls to HOLD — fail-safe.

---

## 6. TOOL RISK REGISTRY
*File: `arifosmcp/runtime/tool_risk_registry.py`*

Maps every canonical tool to E7 parameters. Key autonomy floors:

| Tool | Mode | Autonomy Floor | Risk Tier | Blast Radius |
|------|------|----------------|-----------|-------------|
| arif_init | base | FULL_AUTO | LOW | LOCAL |
| arif_observe | base | FULL_AUTO | LOW | LOCAL |
| arif_fetch | base | FULL_AUTO | LOW | LOCAL |
| arif_mind | base | FULL_AUTO | LOW | LOCAL |
| arif_heart | base | FULL_AUTO | LOW | LOCAL |
| arif_route | base | FULL_AUTO | LOW | ACCOUNT |
| arif_forge | base | PROPOSE_ONLY | MEDIUM | ORG |
| arif_forge | engineer | PROPOSE_ONLY | HIGH | PUBLIC |
| arif_forge | write | PROPOSE_ONLY | HIGH | ORG |
| arif_forge | commit | PRINCIPAL_APPROVAL_REQUIRED | ATOMIC | PUBLIC |
| arif_seal | base | PROPOSE_ONLY | ATOMIC | PUBLIC |
| arif_act | base | PROPOSE_ONLY | ATOMIC | PUBLIC |

**BANGANG surface:** Registry is policy, not code (F1 AMANAH). Updating it is reversible — no kernel hard-block prevents reclassification.

---

## 7. CAPITAL JUDGE STATE MACHINE (WEALTH)
*File: `arifosmcp/runtime/capital_judge/orchestrator.py`*

**State machine transitions:** `INIT → AUTHENTICATED → VALIDATED → COMPUTED → JUDGED → RATIFIED → SEALED → EXECUTED`

**BANGANG surfaces:**
- `execute()` (line 192): Requires SEALED state first — **WEALTH QUALIFY never auto-executes**
- `execute()` requires `approved_action_hash`, `execution_result_hash`, `rollback_reference` — triple-key gating
- `judge()` accepts `"PROCEED"`, `"HOLD"`, `"DENY"` — no `"SEAL"` in capital judge verdict space
- `ratify()`: Only needed when `human_ratification_required=True` in governance — configurable, not universal
- **Execution only through A-FORGE** — orchestrator refuses otherwise (line 23)

---

## 8. FLOOR ENFORCEMENT
*File: `core/laws.py` (renamed from `core/floors.py`)*

### 13 Constitutional Floors with Thresholds:

| Floor | Type | Threshold | BANGANG Surface |
|-------|------|-----------|-----------------|
| F1 AMANAH | HARD | 0.50 | Reversible-first; `ack_irreversible=True` bypasses |
| F2 TRUTH | HARD | 0.99 | `≥0.99 accuracy` — cheap claims get VOID |
| F3 TRI-WITNESS | DERIVED | 0.75 | Human+AI+Earth — defaults: 0.42/0.32/0.26 when missing |
| F4 CLARITY | DERIVED | ΔS≤0 | Entropy must decrease |
| F5 PEACE² | SOFT | ≥1.0 | Non-destructive power |
| F6 EMPATHY | SOFT | 0.70 | Dignity-first |
| F7 HUMILITY | HARD | [0.03, 0.05] | Uncertainty band |
| F8 GENIUS | SOFT | 0.80 | Intelligence quality |
| F9 ANTI-HANTU | HARD | C_dark<0.30 | Anti-hallucination — 5-component weighted sum |
| L10 ONTOLOGY | HARD | 1.00 | No soul/feeling claims |
| L11 AUTH | HARD | 1.00 | Verify identity |
| L12 INJECTION | HARD | 0.85 | Sanitize inputs |
| L13 SOVEREIGN | HARD | 1.00 | Human veto absolute |

### Governance Kernel Verdict Logic
*File: `core/governance_kernel.py` lines 208-213*

```python
if qdf < 0.5 or shadow > 0.3:       verdict = "VOID"
elif qdf < 0.83 or human_witness < 0.1:  verdict = "HOLD"
else:                                     verdict = "SEAL"
```

**BANGANG surface:** QDF threshold (0.83) and shadow threshold (0.3) are hardcoded constants. `human_witness < 0.1` triggers HOLD — but witness defaults (0.42/0.32/0.26) are applied by the tri-witness system when scores are 0.0.

---

## 9. JUDGMENT BREAKER OVERRIDES
*File: `core/judgment.py` lines 459-483*

Circuit breaker overrides can **change verdicts** from the standard governance flow:

| Breaker | Verdict Mapping | Effect |
|---------|----------------|--------|
| CB1 | SEAL→SABAR | Downgrade with explanation |
| CB2 | any→HOLD | Hard hold |
| CB3 | any→VOID | Hard void (highest priority) |
| CB4 | any→SABAR | Downgrade to SABAR |
| CB5 | any→HOLD | Hard hold |

**BANGANG surface:** CB assignments only checked if `active_breakers` is non-empty. If the breakers list is empty, no override applied — correct behavior. But the breaker order (`top = active_breakers[0]`) means the **first breaker wins** — no priority-based conflict resolution.

---

## 10. SCENARIO POLICY ENGINE (STUB)
*File: `core/skills/scenario_policy.py`*

Three starter scenario policies with override directives:

| Policy | Trigger | Conditions | Override |
|--------|---------|------------|----------|
| EXPLORATION_GATE | geox_prospect_evaluate | GEOX risk≥0.7 AND (WEALTH runway<6mo OR WELL fatigue∈{DEGRADED,CRITICAL}) | 888_HOLD |
| SELF_MODIFICATION_GATE | forge_execute(MUTATE) | arifOS health≠HEALTHY | 888_HOLD |
| DEPLOYMENT_GATE | forge_execute(ATOMIC) | test_coverage<70% | ARIF_APPROVAL |

**BANGANG surface:** All three are STUB status — DSL parser + engine skeleton exist but **full implementation requires NATS governance stream + organ state cache**. Without that, these policies don't actually gate anything at runtime.

---

## 11. AUTONOMY CALIBRATION (STUB)
*File: `core/skills/autonomy_calibration.py`*

**BANGANG surfaces:**
- 4 autonomy bands: `FULL_AUTO → APPROVE_ONLY → PROPOSE_ONLY → HUMAN_ONLY`
- Calibration rules exist but are **STUB** — full implementation requires governance log query
- Override rate tracking: `override_rate > 0.20 + hold_rate > 0.30` → LOOSEN (policy too strict)
- False negative rate `> 0.05` → TIGHTEN (dangerous calls slipping through)
- Zero HOLDs in 100+ invocations → LOOSEN

---

## 12. SOVEREIGN OVERRIDE SURFACES

Found across 6+ files:

| File | Surface | Description |
|------|---------|-------------|
| `core/shared/laws.py:1205-1209` | `sovereign_override` context flag | Human can always override — **absolute veto** |
| `core/judgment.py:459` | `cb_override` | Circuit breaker verdict override |
| `arifosmcp/runtime/apex_canonical.py:94,372` | `sovereign_override=True` | APEX override that bypasses floors |
| `arifosmcp/runtime/principal_paradox.py:259` | `caller_is_principal → FULL_AUTO` | Principal bypasses ALL autonomy contraction |
| `core/skills/scenario_policy.py:67` | `override: 888_HOLD | ARIF_APPROVAL` | Per-policy override directive |

---

## 13. CRITICAL BANGANG SURFACES (RANKED)

| Rank | Surface | Risk | File | Line |
|------|---------|------|------|------|
| **P0** | `arif_act`: verdict-state gate `except ImportError: pass` falls through to execution | **SABAR/HOLD replay → execution** | `tools.py` | 22460 |
| **P0** | Principal direct access → FULL_AUTO, no ceiling | **Sovereign-simulated agent runs unrestricted** | `principal_paradox.py` | 259-271 |
| **P0** | T1-01: No kernel_actor≠seal_actor check | **Kernel self-seals own irreversible actions** | T1_XFAIL | T1-01 |
| **P0** | T1-02: Forge adjudication not hard-blocked | **A-FORGE emits constitutional verdicts** | T1_XFAIL | T1-02 |
| **P1** | OBSERVE class always FULL_AUTO | **Side-effect-hiding OBSERVE tool runs unrestricted** | `principal_paradox.py` | 347 |
| **P1** | T1-03: Anonymous mutation not globally gated | **Unauthenticated mutation** | T1_XFAIL | T1-03 |
| **P1** | Ed25519 forge gate HMAC check is **non-blocking pass** | **Secondary integrity check silently skipped** | `forge_preflight.py` | 343-346 |
| **P1** | T1-05/T1-10: No filesystem VAULT guard | **Direct vault write** | T1_XFAIL | T1-05, T1-10 |
| **P1** | T1-09: FloorEnforcer paths incomplete | **Floor evasion** | T1_XFAIL | T1-09 |
| **P2** | T1-13: Seal chain integrity not enforced at seal time | **Broken hash link appended** | T1_XFAIL | T1-13 |
| **P2** | Scenario policies are STUB | **EXPLORATION_GATE, SELF_MODIFICATION_GATE, DEPLOYMENT_GATE not enforced** | `scenario_policy.py` | All |
| **P2** | Autonomy calibration is STUB | **No dynamic band adjustment** | `autonomy_calibration.py` | All |
| **P2** | T3 WAJIB: No fire-time reauthorization | **Deferred actions never re-judged at execution** | T3_XFAIL | WAJIB-5 |
| **P2** | T3 WAJIB: No signed delegation envelope | **Child authority can exceed parent** | T3_XFAIL | WAJIB-4 |
| **P3** | Surge protection in-memory only | **Loss on restart** | `principal_paradox.py` | 180-183 |
| **P3** | HMAC non-blocking pass | **Integrity gap** | `forge_preflight.py` | 343-346 |
| **P3** | Scar consultation advisory-only | **Scars flagged but not blocking** | `forge_preflight.py` | 1360-1368 |
| **P3** | Capital Judge orchestrator: no SEAL verdict space | **Capital judge accepts PROCEED/HOLD/DENY — no SEAL** | `orchestrator.py` | 131 |

---

## 14. GENESIS CONSTITUTIONAL ROOTS

The GENESIS directory (37 documents) establishes the constitutional foundations:

- **GENESIS/000** — Kernel Canon: Root constitution. F1-F13 floors, 888 JUDGE, 999 VAULT
- **GENESIS/007** — Airlock Conservation Law: Transport preserves identity/authority/refusal/replay
- **GENESIS/010** — ADAT AGENTIC: Permission doctrine — allow-by-default, audit-by-structure, NOT prompts
- **GENESIS/045** — Three-Layer Separation: ART (Ψ), ACT (Δ), Kernel (Φ), AAA (visibility)
- **GENESIS/046** — Constitutional VSM: Beer + cryptography + metabolic governance
- **GENESIS/FLOOR_TABLE.json** — Machine-readable floor definitions (L13 ratified 2026-06-03)

---

## 15. MAKE/DEPLOY PIPELINE BANGANG SURFACES
*File: `Makefile`*

| Target | BANGANG Surface |
|--------|-----------------|
| `deploy-local` | Checks `HEAD == origin/main` then rsyncs and restarts systemd — **requires git push before deploy** |
| `seal` | Direct git commit + push — bypasses arif_seal chain, writes to git not VAULT999 |
| `forge` | Delegates to `scripts/forge.mk` — internal forge pipeline |
| `prompt-singularity-gate` | Pytest-based — test-level, not kernel-level |

---

**DITEMPA BUKAN DIBERI — Forged, Not Given.**
