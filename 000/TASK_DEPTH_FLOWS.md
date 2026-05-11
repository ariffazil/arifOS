# arifOS Task Depth Flows (T0–T4)

> **Kernel doctrine:** MIND may think. KERNEL may route. HEART may warn. OPS may meter. EVIDENCE may verify. JUDGE may decide. FORGE may execute. VAULT may remember.

---

## T0 — Simple

**Trigger:** Low stakes, no ambiguity, no external dependencies.

**Flow:**
```
111_SENSE (intake + classify)
→ 444_KERNEL(depth_select=T0)
→ 333_MIND(mode=reason)
→ 555_REPLY (compress + format)
```

**Budget:** ~1K tokens, <1s latency.
**Authority:** Operator.
**Vault:** Optional.

---

## T1 — Normal

**Trigger:** Standard reasoning, mild ambiguity, reversible.

**Flow:**
```
111_SENSE (intake + classify)
→ 444_KERNEL(depth_select=T1)
→ 444_KERNEL(budget_gate)
→ 333_MIND(mode=plan)   [optional for simple T1]
→ 333_MIND(mode=reason)
→ 555_REPLY (compress + format)
```

**Budget:** ~2–4K tokens, <3s latency.
**Authority:** Operator.
**Vault:** Optional.

---

## T2 — Architecture / Important

**Trigger:** Design decisions, consequential but reversible, multi-step.

**Flow:**
```
111_SENSE (intake + classify)
→ 444_KERNEL(depth_select=T2)
→ 444_KERNEL(route + budget_gate)
→ 333_MIND(mode=plan)
→ 333_MIND(mode=reason)
→ 666_HEART(mode=critique)   [dignity + consequence scan]
→ 333_MIND(mode=synthesize)
→ 555_REPLY (compress + format)
→ 999_VAULT(mode=seal_trace) [optional]
```

**Budget:** ~4–8K tokens, <6s latency.
**Authority:** Operator + HEART warning if risk detected.
**Vault:** Trace summary recommended.

---

## T3 — Evidence-Heavy

**Trigger:** Fact-dependent, source verification required, uncertain terrain.

**Flow:**
```
111_SENSE (intake + classify)
→ 444_KERNEL(depth_select=T3)
→ 444_KERNEL(route)
→ 222_EVIDENCE_FETCH (source + verify)
→ 333_MIND(mode=reason)
→ 333_MIND(mode=verify)
→ 555_REPLY (compress + format)
→ 999_VAULT(mode=seal_trace) [optional]
```

**Budget:** ~6–12K tokens, <10s latency.
**Authority:** Operator.
**Vault:** Evidence receipts + trace summary.

---

## T4 — Consequential / Irreversible

**Trigger:** Deployment, seal, commit, legal/medical/financial high stakes.

**Flow:**
```
111_SENSE (intake + classify)
→ 444_KERNEL(depth_select=T4)
→ 444_KERNEL(authority_gate + reversibility_gate)
→ 333_MIND(mode=plan)
→ 666_HEART(mode=critique)        [dignity + consequence scan]
→ 222_EVIDENCE_FETCH(mode=verify) [external verification]
→ 888_JUDGE(mode=judge)           [sovereign decision boundary]
→ 1212_FORGE(mode=dry_run)        [simulate only unless approved]
→ 999_VAULT(mode=seal_decision)   [immutable audit record]
```

**Rules:**
- `plan_approve` must be **deterministic**, never LLM-adjudicated.
- `888_JUDGE` is mandatory for irreversible actions.
- `ack_irreversible` required before FORGE executes.
- Full `reasoning_trace` + `scars` + `normalization_events` sealed to VAULT.

**Budget:** >12K tokens, >10s latency acceptable.
**Authority:** Sovereign (Arif) — JUDGE boundary decides.
**Vault:** Mandatory seal of decision + trace + scars.

---

## Kernel Routing Matrix

| Task Keyword | depth_select | risk_gate | authority_gate | reversibility_gate |
|-------------|--------------|-----------|----------------|--------------------|
| simple, quick, hello, status | T0 | low | OPERATOR | reversible |
| normal, analyze, compare | T1 | low | OPERATOR | reversible |
| architecture, design, important | T2 | medium | OPERATOR | reversible |
| evidence, verify, source | T3 | medium | OPERATOR | reversible |
| deploy, migrate, seal, commit | T4 | high/critical | SOVEREIGN | irreversible |
| delete, rm -rf, destroy | T4 | critical | SOVEREIGN | irreversible |

---

## 13-Tool Canonical Mapping

| # | Tool | Modes (current + added) |
|---|------|------------------------|
| 000 | `arif_session_init` | init, resume, validate, epoch_open, epoch_seal |
| 111 | `arif_sense_observe` | search, ingest, compass, atlas, entropy_dS, vitals |
| 222 | `arif_evidence_fetch` | fetch, search, archive, verify |
| 333 | `arif_mind_reason` | plan, plan_review, plan_approve, reason, reflect, forge, debate, socratic, verify, critique, axioms, **sequential**, synthesize |
| 444 | `arif_kernel_route` | route, stage, lane, list, status, telemetry, **depth_select**, **risk_gate**, **budget_gate**, **authority_gate**, **reversibility_gate**, **workflow_select** |
| 555 | `arif_reply_compose` | compose, style, format, nudge, cite, summary |
| 666 | `arif_heart_critique` | critique, simulate, empathize, redteam, maruah, deescalate, summary |
| 777 | `arif_ops_measure` | health, vitals, cost, predict, genius, psi_le, omega, landauer, **budget_estimate**, **token_guard**, **latency_guard**, **cost_guard**, **entropy_delta**, **calibration_report** |
| 888 | `arif_judge_deliberate` | judge, compare, history, explain |
| 999 | `arif_vault_seal` | seal, commit, dry_run, verify, ledger, changelog, audit, list, chain, **seal_trace**, **seal_receipt**, **seal_scar**, **seal_decision**, **retrieve_audit** |
| 1010 | `arif_memory_recall` | recall, store, get, list, prune, search, context, dry_run |
| 1111 | `arif_gateway_connect` | route, discover, handshake, relay, seal |
| 1212 | `arif_forge_execute` | engineer, write, generate, commit, recall, dry_run, query |

---

## Governance Invariants

1. **plan_approve** is deterministic — LLM must never adjudicate sovereign approval.
2. **888_JUDGE** is the only floor with human veto authority.
3. **666_HEART** warnings are advisory unless combined with JUDGE.
4. **777_OPS** guards budget — MIND does not grade its own budget alone.
5. **999_VAULT** seals are append-only — no mutable audit records.
6. **T4 flows** always require `ack_irreversible` before FORGE executes.

---

*Sealed: 2026-04-29 | Authority: 000_IMMUTABLE_LAW | F13 SOVEREIGN*
