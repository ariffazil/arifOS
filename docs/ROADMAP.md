# arifOS Development Roadmap

**Version:** v43.1.0 | **Last Updated:** 2025-12-19

**Focus**: CRITICAL TASKS ONLY. No nice-to-haves.

---

## Current Status

- **v43.1.0** — RELEASED (GitHub)
- **Tests:** 2156+ passing
- **Runtime Law:** v42 (7 conceptual layers)
- **Trinity:** v43.1.0 (Universal Git Governance) ✅

---

## Completed ✅

### Trinity (v43.0 - v43.1.0)

- [x] `/gitforge` - State mapper (hot zones, entropy prediction, risk scoring)
- [x] `/gitQC` - Constitutional F1-F9 validator
- [x] `/gitseal` - Human authority gate + atomic bundling
- [x] Housekeeper - Auto-doc engine
- [x] Vault-999 integration
- [x] Universal CLI - 3 commands (forge/qc/seal)
- [x] AI-agnostic interface (ChatGPT, Claude, Gemini, any AI)
- [x] Platform wrappers (trinity.ps1, trinity.sh)
- [x] Complete documentation
- [x] Self-sealed (v43.1.0 tag)

### Infrastructure (v37-v42)

- [x] All 9 constitutional floors (F1-F9)
- [x] W@W Federation (@WELL, @RIF, @WEALTH, @GEOX, @PROMPT)
- [x] @EYE Sentinel (12 views)
- [x] GENIUS LAW metrics (G, C_dark, Ψ)
- [x] Cooling Ledger with hash-chain
- [x] Phoenix-72 metabolism
- [x] v38 Memory Write Policy (EUREKA)
- [x] v41 FAG (File Access Governance)
- [x] v42 Federated agent architecture
- [x] Architecture overview (`ARCHITECTURE_v42.md`)
- [x] Promptfoo configs (in archive)
- [x] Mypy type checking configured

---

## CRITICAL Tasks (Priority Order)

### 🔴 P0 — BLOCKING (Security/Stability)

**DO THESE FIRST. SYSTEM UNSAFE WITHOUT THEM.**

#### 1. Fail-Closed Governance Audit 🚨

**Problem**: System may fail-open (allow unsafe outputs by defaulting to SEAL) instead of fail-closed (default to VOID/SABAR).

**Risk**: **CRITICAL** - Could allow harmful outputs if floor validation breaks

**Evidence**: No explicit fail-closed enforcement found in codebase

**Action Required**:

- [ ] Audit all verdict paths in `apex_prime.py`, `pipeline.py`
- [ ] Ensure default verdict = VOID (not SEAL) on errors
- [ ] Add explicit `try/except` → VOID for floor validation
- [ ] Test: Break F1 check, verify system VOIDs (not SEALs)
- [ ] Document fail-closed guarantee in SECURITY.md

**Timeframe**: **IMMEDIATE** (v43.2.0)  
**Owner**: Human authority required for approval

---

#### 2. Cooling Ledger Schema Consolidation

**Problem**: Multiple ledger schemas exist (`v35Ω` in code, vault999 schema, Trinity gitseal schema)

**Risk**: **HIGH** - Data integrity, audit trail inconsistency

**Evidence**:

- `ledger.py` uses `v35Ω`
- `vault999.py` has different schema
- `trinity/seal.py` writes `gitseal_audit_trail.jsonl` with own schema

**Action Required**:

- [ ] Define ONE canonical ledger schema (v43 or upgrade v35Ω)
- [ ] Align Trinity ledger with canonical schema
- [ ] Align Vault-999 with canonical schema
- [ ] Migration script for existing ledgers
- [ ] Update all writers to use canonical schema
- [ ] Verify with integration tests

**Timeframe**: **HIGH PRIORITY** (v43.3.0)  
**Depends On**: P0-1 (fail-closed audit)

---

### 🟡 P1 — HIGH (Performance/Quality)

**DO THESE AFTER P0. IMPROVE RELIABILITY.**

#### 3. Trinity → FAG Integration

**Problem**: Trinity bypasses FAG and writes files directly (violates INV-3: all writes must be auditable)

**Risk**: **MEDIUM** - Security gap, no file governance on Trinity ops

**Status**: **Phoenix-72 cooling** (see `TRINITY_ROADMAP.md`)

**Action Required**:

- [ ] Wait 72 hours (cooling end: 2025-12-22)
- [ ] Review integration proposal
- [ ] Human approval decision
- [ ] If approved: Replace Trinity direct I/O with FAGsafe_read/write/append()`
- [ ] Test atomic bundle creation with FAG
- [ ] Document FAG dependency

**Timeframe**: **Q1 2026** (conditional on cooling review)  
**Depends On**: P0-1, P0-2 complete

---

#### 4. Trinity Production Validation (30 days)

**Problem**: Trinity untested in real-world use

**Risk**: **MEDIUM** - Unknown edge cases, bugs, UX issues

**Action Required**:

- [ ] Use Trinity for all arifOS commits (30-day trial)
- [ ] Log all issues, friction points, failures
- [ ] Gather feedback on 3-command interface
- [ ] Identify integration pain points
- [ ] Document learnings

**Timeframe**: **Dec 2025 - Jan 2026**  
**Triggers**: Decision on Trinity integrations (FAG, W@W, AAA)

---

### 🟢 P2 — DEFERRED (Technical Debt)

**DO THESE ONLY IF TIME/ENERGY ALLOWS. NOT BLOCKING.**

#### 5. Extract Stakes Classifier Module

**Problem**: Stakes classification logic in `pipeline.py` (should be separate module)

**Risk**: **LOW** - Technical debt, maintainability

**Action**: **DEFERRED** to v44+  
**Reason**: Not urgent, no functional impact

---

#### 6. Trinity → W@W Delegation

**Problem**: Trinity duplicates F1-F9 validation logic

**Risk**: **LOW** - Maintenance burden, but Trinity works

**Status**: **Phoenix-72 cooling** (see `TRINITY_ROADMAP.md`)

**Action**: **DEFERRED** to Q2 2026  
**Reason**: Wait for production feedback first

---

## Future (Phoenix-72 Proposals)

**Protocol**: All future work follows Phoenix-72 (72-hour cooling minimum)

See [TRINITY_ROADMAP.md](./TRINITY_ROADMAP.md) for detailed proposals:

- 🔮 **Trinity → FAG** (File governance) - **P1**, cooling since 2025-12-19
- 🔮 **Trinity → W@W** (Floor delegation) - **P2**, cooling since 2025-12-19
- 🔮 **Trinity → AAA** (Verdict hierarchy) - **P2**, deferred to 2026+
- 🔮 **Trinity → Pipeline** (000→999 integration) - **P2**, deferred to 2026+

**Next Review**: 2026-01-19 (after 30 days Trinity production use)

---

## Development Tracks

### Track A — LAW (L1_THEORY/canon/)

Only modify canon when explicitly requested.  
Master index: `L1_THEORY/canon/_INDEX/00_MASTER_INDEX_v42.md`

### Track B — SPEC (spec/v42/)

Only modify specs when explicitly requested.  
Spec files parameterize canon thresholds.

### Track C — CODE_FORGE (arifos_core/)

Default track for day-to-day work. Keep tests green.

**Rule of thumb:** Canon > Spec > Code. If conflict, mark as PARADOX_HOTSPOT.

---

## What We Removed (Waste of Energy)

**From old roadmap P2 (all deferred/deleted)**:

- ~~Architecture overview~~ (DONE - `ARCHITECTURE_v42.md` exists)
- ~~Expand mypy coverage~~ (DONE - already configured)
- ~~Link whitepaper from README~~ (NOT CRITICAL - marketing, not safety)
- ~~SEA-LION in-model GENIUS LAW~~ (FUTURE - if ever needed)
- ~~Multi-modal @GEOX~~ (FUTURE - not urgent)
- ~~Hardware-backed KMS~~ (FUTURE - current stubs work fine)

**Philosophy**: If it doesn't make the system safer or faster, it waits.

---

## Contributing

1. Check this roadmap for **CRITICAL** priorities
2. Follow [AGENTS.md](../AGENTS.md) governance rules
3. All changes must pass 9 constitutional floors
4. Run `pytest -v` before committing
5. For Trinity, see [TRINITY_ROADMAP.md](./TRINITY_ROADMAP.md)

---

## Critical Path Summary

```
v43.1.0 (NOW)
    ↓
P0-1: Fail-Closed Audit (IMMEDIATE)
    ↓
P0-2: Ledger Schema Consolidation (v43.2.0)
    ↓
P1-3: Trinity → FAG Integration (v43.3.0, conditional)
    ↓
P1-4: Trinity Production Validation (30 days)
    ↓
2026-01-19: Review, decide on W@W/AAA integrations
```

**Next Milestone**: v43.2.0 with fail-closed guarantee

---

**Ditempa, bukan diberi.** No waste. Only what matters.
