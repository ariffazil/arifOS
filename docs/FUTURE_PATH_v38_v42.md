# arifOS Future Path (v38 → v42)

**Architect:** Muhammad Arif Fazil
**Date:** 13 December 2025
**Principle:** *DITEMPA BUKAN DIBERI* — Forged, not given

---

## Executive Snapshot

arifOS has completed its **Cortex & Governance** phase (v37–v38). The core judiciary, safety floors, and memory law are forged and test-proven. The next 18–24 months focus on **giving arifOS a body, hands, and verifiable trust**, without rushing cryptography or diluting authority boundaries.

**Hard rule:** each phase is **blocked** until the previous phase is complete, audited, and stable.

---

## Where We Are Now (Baseline)

* **Mind / Cortex:** COMPLETE (v37 production, ~97% red-team safety)
* **Governance:** COMPLETE (9 Floors, APEX PRIME, Anti-Hantu, Amanah)
* **Memory Law:** COMPLETE (v38 Memory Write Policy, 6 bands, authority boundary)
* **Tests:** 1,250+ passing across core, memory, and integration

**What is intentionally missing:**

* No public API body yet
* No IDE integration yet
* No filesystem access yet
* No zero-knowledge proofs shipped

This is correct. arifOS is law-first, not feature-first.

---

## Phase Map (High Level)

| Phase   | Version | Focus                       | Timeframe       | Status        |
| ------- | ------- | --------------------------- | --------------- | ------------- |
| Phase 1 | **v38** | Memory as Law               | Q1 2026         | ✅ SHIPPED    |
| Phase 2 | **v39** | Body (FastAPI Grid)         | Q2 2026         | ✅ SHIPPED    |
| Phase 3 | **v40** | Hands (MCP + IDE)           | Q3 2026         | ✅ SHIPPED    |
| Phase 4 | **v41** | FAG (File Access Governance) | Q4 2025–Q1 2026 | ✅ v41.0.0 SHIPPED |
| Phase 5 | **v42** | Cryptographic Optimization  | Q2 2027+        | CONDITIONAL   |

---

## Phase 1 — v38: Memory as Law (FOUNDATION)

**Status:** ✅ SHIPPED (13 December 2025)

**Purpose:** Ensure arifOS never learns the wrong thing.

**What v38 establishes:**

* Verdict-gated memory writes
* 6 memory bands (Vault, Ledger, Active, Phoenix, Witness, Void)
* Authority boundary (AI proposes, humans seal)
* Hash-chained auditability

**Non-negotiables:**

* VOID verdicts never become precedent
* Memory recall is advisory, not factual

**Outcome:** arifOS can now remember **safely**.

---

## Phase 2 — v39: Body API (FASTAPI GRID)

**Purpose:** Give arifOS a controlled mouth.

**What ships:**

* Minimal FastAPI service wrapping the governed pipeline
* Read-only, append-only design
* Docker-deployable, single-tenant friendly

**What is deliberately excluded:**

* No streaming
* No auto-approval of amendments
* No dashboards

**Why this order matters:**
Without lawful memory (v38), an API body would amplify mistakes. v39 only exists because v38 holds.

**Expected deliverables:**

```
arifos_api/
  __init__.py         - Package init
  server.py           - FastAPI app
  models.py           - Request/response schemas
  routes.py           - Endpoints (/govern, /ledger, /health, /propose)
tests/test_api.py     - Integration tests
docker/Dockerfile     - Deployment container
```

**Endpoints (minimal):**

```
POST /govern          - Input: {text, high_stakes} → Output: {verdict, response, proof}
GET  /ledger          - Read-only ledger entries (JSON)
GET  /health          - System status + floor summary
POST /propose         - Amendment proposal (AI proposes, human seals via CLI)
```

---

## Phase 3 — v40: Hands (MCP + IDE Integration)

**Purpose:** Make governance visible at the point of work.

**What ships:**

* MCP server wrapping v39 API
* VS Code as the arifOS cockpit
* Inline audits, verdict explanations, ledger visibility

**Key design choice:**

* Use MCP standard
* Avoid LangChain / AutoGen
* Preserve arifOS sovereignty

**Expected deliverables:**

```
arifos_mcp/
  __init__.py         - Package init
  server.py           - MCP protocol implementation
  tools.py            - Tool definitions for IDE
tests/test_mcp.py     - Integration tests
```

**Capabilities:**

* Audit selected code/text inline
* Explain why something is PARTIAL / SABAR
* Show ledger entries in editor
* Propose (not seal) amendments
* View governance telemetry

**Outcome:** Engineers interact with governance **where decisions are made**, not after the fact.

---

## Phase 4 — v41: FAG (File Access Governance) ✅

### A. FAG v41.0.0-alpha (SHIPPED — January 2025)

**Problem:** Ungoverned input is as dangerous as ungoverned output.

**Solution (SHIPPED):**

* ✅ Root-jailed, read-only filesystem wrapper (`FAG` class)
* ✅ 50+ forbidden patterns: .env, SSH keys, credentials, git internals
* ✅ 5 constitutional floors: F1 (root jail), F2 (exists), F4 (text only), F9 (no secrets)
* ✅ 3 interfaces: Python API, CLI (`arifos-safe-read`), MCP (`arifos_fag_read`)
* ✅ Cooling Ledger integration (every read audited)
* ✅ 12/12 core tests + 11/11 MCP integration tests passing

**Result:** AI agents cannot read secrets or escape root jail.

**Documentation:**
- Quick Start: `docs/FAG_QUICK_START.md`
- v41.1 Roadmap: `docs/FAG_v41_1_ROADMAP.md`
- Core Implementation: `arifos_core/fag.py`
- Test Suite: `tests/test_fag.py`, `tests/test_mcp_fag_integration.py`

### B. FAG v41.1 (PLANNED — Q1 2026)

**Next:** Write operations with Phoenix-72 approval.

* Write proposals → 888_HOLD verdict
* Human approval via `arifos-seal-canon`
* Delete operations → Move to `.arifos_trash/` (recoverable for 90 days)
* Git auto-commit on seal

**Blocked Until:** v41.0.0 MCP validation complete (✅ 11/11 tests passing)

### C. zkPC (Design Only)

**What it is:**

* Cryptographic proof that all floors passed
* Proof of *process*, not content

**Why design-only:**

* Requires formal verification
* Needs academic scrutiny
* Too dangerous to rush

**Shipping decision deferred until peer review passes.**

---

## Phase 5 — v42: Cryptographic Backend (CONDITIONAL)

**Ships only if v41 research succeeds.**

Possible outcomes:

* Optimized zk-SNARK backend
* Or non-zero-knowledge witness layer only

**No promises. No hype.**

---

## Hard Gates (Sequential)

| Gate | Condition | Blocked Until | Status |
|------|-----------|---------------|--------|
| v39 | Memory invariants hold | v38 audited + stable | ✅ PASSED |
| v40 | API is audited | v39 tested + deployed | ✅ PASSED |
| v41.0 FAG | MCP is stable | v40 integration complete | ✅ PASSED |
| v41.1 FAG | v41.0 validated | 12/12 + 11/11 tests passing | ✅ READY |
| zkPC | Peer review passes | Academic validation | ⏳ PENDING |

**If a gate fails → pause, fix, retest.**

---

## Success Vision (18–24 Months)

By late 2027, arifOS becomes:

* A **complete governance kernel** (input → cognition → output)
* Fully auditable, human-sovereign, non-custodial
* IDE-native, API-deployable
* Cryptographically provable *if and only if* safe

Built in Malaysia. Designed for the world.

---

## What Each Agent Should Know

### For Claude Code agents:

1. **Current state:** v38 SHIPPED. Memory law is active.
2. **Next work:** v39 Body API (FastAPI Grid)
3. **Do not:** Skip gates, rush zkPC, auto-approve amendments
4. **Always:** Check floors, audit writes, preserve authority boundary

### For Codex / Cursor / Copilot agents:

1. **Read:** AGENTS.md Section 10 for phase gates
2. **Respect:** Canon > Spec > Code hierarchy
3. **Never:** Modify canon without explicit human approval
4. **Always:** Keep tests green, document changes

---

## Final Law

**Do not rush intelligence.**

Law must harden before scale.
Memory must obey judgment.
Authority must never drift.

*Forged, not given.*

---

**Version:** v38.0.0 | **Status:** PRODUCTION | **Next:** v39 Body API (Q2 2026)

**Author:** Muhammad Arif bin Fazil
**Location:** Seri Kembangan, Selangor, Malaysia
**Repository:** https://github.com/ariffazil/arifOS
