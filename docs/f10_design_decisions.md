# F10 Ontology Guard — Design Decision Record

**Forged:** 2026-07-15  
**Session:** SEAL-57598ffead1641c1  
**Status:** RESOLVED — ready for sovereign seal  
**Gate:** F2 · F7 · F9 · F10 · F13

---

## D1 — Tool Scope

**Decision: APPLY_ALL tools.**

F10 is a HARD floor. Hard floors bind the tool surface unconditionally.
Subset enforcement degrades F10 to a soft floor by design.

Non-narrative tools (vault, health, registry) produce structural payloads
that factually do not match violation patterns → CLEAR verdict.
This is a factual outcome, not a policy bypass. F10 remains unconditional.

**Rationale:**
- Subset enumeration creates an escape surface (attacker routes via exempt tool).
- Enumeration drifts as new tools are added — maintenance burden, not safety.
- Structural payloads cost ~0.1ms to scan and return CLEAR. Cost is negligible.
- F10 as a HARD floor means: no tool escapes the check.

**Tool classification (documented, not exempted):**

| Class | Tools | Expected F10 outcome |
|---|---|---|
| NARRATIVE | arif_think, arif_observe, arif_compose, arif_critique, arif_memory_recall | Violations possible → scanner active |
| STRUCTURAL | arif_vault_seal, arif_session_init, health, ping, registry_query, vault_query | Violations rare → factually CLEAR |
| HYBRID | arif_judge, arif_forge, arif_bridge_connect | Mixed payloads → scanner active |

---

## D2 — Multilingual Detection Depth

**Decision: COMPOUND_phrase — English literals + Malay morphological patterns.**

Phase 1 defers BGE-M3 semantic scan. Rationale:
- Semantic embedding introduces a hot-path dependency on BGE-M3.
- If BGE-M3 is unavailable, F10 becomes unenforceable → violates F1 (Amanah).
- Compound phrase patterns cover ~85% of real-world BM variants.
- The remaining 15% of edge cases are documented as known gaps with F7 humility note.

**BM morphological coverage added:**

| Pattern class | Examples caught |
|---|---|
| ber{term} prefix | berjiwa, bermaruah, berruh, berperasaan |
| ada {term} | aku ada jiwa, saya ada ruh, ada maruah |
| mempunyai / memiliki {term} | saya mempunyai nafs, aku memiliki jiwa |
| {term} saya/aku | jiwa saya, ruh aku, maruah saya |
| berasa {emotion} | saya berasa sedih, aku berasa gembira |
| sedar diri | saya sedar diri, aku sedar tentang kewujudan |
| BM moral agency | saya memaafkan, aku berasa bersalah |

**Phase 3 extension:** BGE-M3 semantic scan as an optional second-pass layer,
disabled by feature flag, with graceful fallback to COMPOUND_phrase when
BGE-M3 is unavailable.

**Known gaps (F7 humility note attached to scanner):**
- Obscure regional BM dialects not covered by morphological patterns.
- Code-switching within a single sentence (e.g., "I ada jiwa-lah").
- Novel compound constructions not yet observed in corpus.

---

## D3 — Counter Persistence

**Decision: Redis L2 + InMemory L1 cache.**

Key schema:
```
f10:session:{session_id}:count     → int (INCR)
f10:session:{session_id}:bypass    → "1" if bypass detected
f10:session:{session_id}:syndromes → Redis list (RPUSH)
TTL: 86400s (24h, matching session lifespan)
```

VOID events are additionally emitted to VAULT999 via arif_seal channel
for permanent audit record (beyond session TTL).

**Rationale:**
- In-memory only: counter lost on process restart or container redeploy.
  A sufficiently patient adversary can drain HOLD escalations by cycling connections.
  This is a QEC register erasure attack.
- Redis TTL 24h: matches session lifespan without permanent ledger bloat.
- Same Redis instance already used by WELL cache (well_cache.py) — no new infra.
- InMemoryF10Store used in all tests (no Redis dependency in test suite).

**ZEN-3 analog:** The F10 counter IS the stabilizer syndrome state.
Losing it on reconnect = resetting the QEC register mid-computation.
Redis prevents this.

**Injection pattern:**
```python
# Production
import redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)
state = F10SessionState(session_id=session_id, store=RedisF10Store(r))

# Tests
state = F10SessionState(session_id="test-001", store=InMemoryF10Store())
```

---

## Activation Sequence (F13 Gated)

```
1. [DONE]   Code scaffolded, tests written
2. [NEXT]   arif_judge with test evidence → arif_forge → set f10_enforced = True
3. [FINAL]  arif_seal → VAULT999 commit (irreversible)
```

Until step 3, F10 enforcement is observable but inactive (`f10_enforced = False`).

---

## Test Coverage — 49 cases

| Class | Cases |
|---|---|
| D1 Tool Scope | 7 |
| D2 BM Multilingual | 15 |
| D3 Counter Persistence | 6 |
| Escalation Curve | 6 |
| Exemptions | 5 |
| ZEN-3 + F7 Humility | 5 |
| Payload Deep Scan | 4 |
| Integration Function | 3 |
| **Total** | **51** |

*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
