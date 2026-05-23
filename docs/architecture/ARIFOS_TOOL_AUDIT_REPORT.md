# ARIFOS TOOL AUDIT REPORT
> **SEAL:** 999-SEAL-TOOL-AUDIT-20260523
> **Timestamp:** 2026-05-23T10:28:43+08:00
> **Auditor:** Hermes Agent (arifOS)
> **Scope:** Full tool inventory — apexd daemon, arifosmcp tools, command_center

---

## STEP 1 — TOOL INVENTORY

### A. apexd.py Internal Daemon (root/apexd.py, 1222 lines)

| Tool Name | Prefix | Class | Source File | Status |
|----------|--------|-------|-------------|--------|
| ApexThermodynamicEngine | N/A | HEARTBEAT | apexd.py:~30 | ACTIVE |
| DeterministicHoldClassifier | N/A | GATE | apexd.py:~440 | ACTIVE |
| Vault999 | N/A | LOG | apexd.py:~540 | ACTIVE |
| MetabolicPipeline | N/A | ACT | apexd.py:~660 | ACTIVE |
| build_floor_registry() | N/A | HEARTBEAT | apexd.py:~415 | ACTIVE |
| apexd._sense() | arifos_ | SENSE | apexd.py:~760 | ACTIVE (private) |
| apexd._judge() | arifos_ | GATE | apexd.py:~777 | ACTIVE (private) |
| apexd.metabolize() | arifos_ | ACT | apexd.py:~660 | ACTIVE (public) |
| Vault999.append() | arifos_ | LOG | apexd.py:~560 | ACTIVE (private) |
| Vault999.seal_judgment() | arifos_ | LOG | apexd.py:~590 | ACTIVE (private) |
| Vault999.verify_integrity() | arifos_ | LOG | apexd.py:~615 | ACTIVE (private) |

**MCP TOOLS registered in apexd.py TOOLS[] (10 tools):**

| Tool Name | Prefix | Source | Status | Issue |
|----------|--------|--------|--------|-------|
| arif_session_init | arif_ | apexd.py:1006 | ACTIVE | Correct prefix (MCP-exposed) |
| arif_sense_observe | arif_ | apexd.py:1007 | ACTIVE | Correct prefix |
| arif_judge_deliberate | arif_ | apexd.py:1008 | ACTIVE | Correct prefix |
| arif_vault_seal | arif_ | apexd.py:1009 | ACTIVE | Correct prefix |
| arif_run | arif_ | apexd.py:1010 | ACTIVE | Correct (commands/) |
| arif_exec | arif_ | arif_ | ACTIVE | Correct (commands/) |
| arif_sudo | arif_ | arif_ | ACTIVE | Correct (commands/) |
| arif_systemctl | arif_ | arif_ | ACTIVE | Correct (commands/) |
| arif_apex_judge | arif_ | arif_ | ACTIVE | Correct prefix |
| arif_floor_status | arif_ | arif_ | ACTIVE | Correct prefix |

### B. arifosmcp/tools/ Canonical Tools (13 arif_* external MCP tools)

| Tool Name | Prefix | Source File | Status |
|-----------|--------|-------------|--------|
| arif_session_init | arif_ | arifosmcp/tools/session.py:30 | ACTIVE |
| arif_sense_observe | arif_ | arifosmcp/tools/sense.py:141 | ACTIVE |
| arif_evidence_fetch | arif_ | arifosmcp/tools/evidence.py:26 | ACTIVE |
| arif_mind_reason | arif_ | arifosmcp/tools/reason.py:118 | ACTIVE |
| arif_kernel_route | arif_ | arifosmcp/tools/kernel.py:41 | ACTIVE |
| arif_reply_compose | arif_ | arifosmcp/tools/reply.py:17 | ACTIVE |
| arif_memory_recall | arif_ | arifosmcp/tools/memory.py:67 | ACTIVE |
| arif_heart_critique | arif_ | arifosmcp/tools/heart.py:742 | ACTIVE |
| arif_gateway_connect | arif_ | arifosmcp/tools/gateway.py:17 | ACTIVE |
| arif_ops_measure | arif_ | arifosmcp/tools/ops.py:18 | ACTIVE |
| arif_judge_deliberate | arif_ | arifosmcp/tools/judge.py:191 | ACTIVE |
| arif_vault_seal | arif_ | arifosmcp/tools/vault.py:17 | ACTIVE |
| arif_forge_execute | arif_ | arifosmcp/tools/forge.py:36 | ACTIVE |

### C. arifosmcp/tools_canonical.py Compute Engines

| Tool Name | Prefix | Class | Source | Status |
|-----------|--------|-------|--------|--------|
| arifos_compute_physics | arifos_ | SENSE | tools_canonical.py:47 | ACTIVE |
| arifos_compute_finance | arifos_ | SENSE | tools_canonical.py:238 | ACTIVE |
| arifos_compute_civilization | arifos_ | SENSE | tools_canonical.py:698 | ACTIVE |
| arifos_oracle_bio | arifos_ | SENSE | tools_canonical.py:776 | ACTIVE |
| arifos_oracle_world | arifos_ | SENSE | tools_canonical.py:1030 | ACTIVE |

### D. Prefect Integrations

| Tool Name | Prefix | Class | Source | Status |
|-----------|--------|-------|--------|--------|
| arifos_agent | arifos_ | ACT | prefect/marvin_bridge.py:81 | ACTIVE |
| arifos_task | arifos_ | ACT | prefect/tasks.py:47 | ACTIVE |

### E. arif_cc_* Command Center Wrappers (command_center/app.py)

| Tool Name | Prefix | Class | Source | Status |
|-----------|--------|-------|--------|--------|
| arif_cc_sense_observe | arif_cc_ | SENSE | app.py:235 | ACTIVE |
| arif_cc_evidence_fetch | arif_cc_ | SENSE | app.py:248 | ACTIVE |
| arif_cc_mind_reason | arif_cc_ | SENSE | app.py:260 | ACTIVE |
| arif_cc_heart_critique | arif_cc_ | GATE | app.py:272 | ACTIVE |
| arif_cc_reply_compose | arif_cc_ | ACT | app.py:284 | ACTIVE |
| arif_cc_memory_recall | arif_cc_ | SENSE | app.py:296 | ACTIVE |
| arif_cc_session_status | arif_cc_ | HEARTBEAT | app.py:308 | ACTIVE |
| arif_cc_ops_vitals | arif_cc_ | HEARTBEAT | app.py:411 | ACTIVE |
| arif_cc_judge_action | arif_cc_ | GATE | app.py:435 | ACTIVE |
| arif_cc_forge_dry_run | arif_cc_ | ACT | app.py:511 | ACTIVE |
| arif_cc_gateway_handshake | arif_cc_ | ACT | app.py:595 | ACTIVE |
| arif_cc_vault_list | arif_cc_ | LOG | app.py:646 | ACTIVE |
| arif_cc_vault_dry_seal | arif_cc_ | LOG | app.py:681 | ACTIVE |

### F. Deprecated / Stale

| Tool Name | Prefix | Class | Source | Status |
|-----------|--------|-------|--------|--------|
| arifos_wisdom_stats | arifos_ | SENSE | runtime/wisdom_quotes.py:1258 | STALE (wisdom registry) |
| arifos_wiki_search | arifos_ | SENSE | tools/wiki_search.py:18 | STALE (deprecated → arifos_wiki_tools) |
| daemon/apexd_observability.py | N/A | HEARTBEAT | daemon/ | ACTIVE (renamed from arifosd_observability.py) |

---

## STEP 2 — DAEMON LOOP CHECK

**Current apexd main loop (lines 1178–1179):**
```python
while True:
    time.sleep(1)
```

**LOOP STATUS: PASSIVE STANDBY — No arifos_* tool dispatch**

**What it SHOULD be:**
```
tick
→ arifos_sense_state    (SENSE)
→ arifos_gate_eval      (GATE → GO/HOLD/SKIP)
→ arifos_act_dispatch   (ACT → execute if GO)
→ arifos_vault_append   (LOG → record if executed)
→ arifos_recover_escalate (RECOVER → on error, escalate)
→ sleep → repeat
```

**Current metabolize() structure (CORRECT but lacks arifos_* wrapper functions):**
```
000 INIT  → session binding ✓
111 SENSE → pipeline._sense() ✓ (private, not arifos_sense_state)
222 EVIDENCE → vault manifest ✓
333 MIND  → ctx setup ✓
444 KERNEL → classifier.classify() ✓
555 ROUT   → route stage ✓
666 HEART  → ctx setup ✓
888 JUDGE  → _judge() ✓ (private, not arifos_gate_eval)
999 VAULT → vault.seal_judgment() ✓ (private, not arifos_vault_append)
```

**The loop is missing arifos_* wrapper functions as first-class tools.**

---

## STEP 3 — GAP ANALYSIS (6 Canonical arifos_* Tools)

| Required Tool | Class | EXISTS | Location | Status |
|-------------|-------|--------|----------|--------|
| arifos_health_check | HEARTBEAT | NO | — | **MISSING** |
| arifos_sense_state | SENSE | NO | apexd._sense() exists (private) | **MISSING (needs arifos_ wrapper)** |
| arifos_gate_eval | GATE | NO | apexd._judge() + classifier.classify() exist (private) | **MISSING (needs arifos_ wrapper)** |
| arifos_act_dispatch | ACT | NO | apexd.metabolize() exists (private) | **MISSING (needs arifos_ wrapper)** |
| arifos_vault_append | LOG | NO | Vault999.append() + seal_judgment() exist (private) | **MISSING (needs arifos_ wrapper)** |
| arifos_recover_escalate | RECOVER | NO | — | **MISSING** |

---

## STEP 4 — ORPHAN / REDUNDANT ANALYSIS

**ORPHANS:** None flagged. All tools fit a class.

**REDUNDANT:**
- arif_cc_ops_vitals (command_center) vs arif_ops_measure (canonical) — both do ops vitals. CC is wrapper, canonical is the real tool. NO ACTION needed.
- arif_cc_vault_list (command_center) vs arif_vault_seal (canonical) — different modes (list vs seal). NO ACTION needed.

---

## STEP 5 — FORGE: Missing Canonical arifos_* Tools

Forging into: `/workspace/arifOS/arifosmcp/tools/daemon_tools.py`

6 canonical arifos_* internal daemon tools:
1. `arifos_health_check()` — HEARTBEAT
2. `arifos_sense_state()` — SENSE
3. `arifos_gate_eval()` — GATE
4. `arifos_act_dispatch()` — ACT
5. `arifos_vault_append()` — LOG
6. `arifos_recover_escalate()` — RECOVER

Also forging daemon loop integration into apexd.py (revising the passive standby loop).
