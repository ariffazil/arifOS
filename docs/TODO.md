# arifOS TODO — Active Work Queue

**Version:** 2026.04.24-KANON
**Authority:** Muhammad Arif bin Fazil (888_APEX)
**SoT:** This file tracks active engineering work.
**Seal ID:** SEAL-20260424-FINAL
**Sealed Commits:** 859b971, ef56a26

---

## ✅ SEALED This Session (2026.04.24)

### Architecture & Ontology
- [x] **Ontological Stack** — Established 7-level hierarchy (L0–L6)
- [x] **Cognitive Trinity** — Formalized AGI / ASI / APEX tiers
- [x] **CRP v1.0** — Defined Conflict Resolution Protocol between tiers
- [x] **Canonical Pruning** — Hard cutover from 22 tools to the Canonical 13

### Fixes
- [x] **rest_routes.py** — Resolved `AttributeError` in `/tools` endpoint
- [x] **contracts.py** — Aligned metadata stages and lanes with SSCT v1.0
- [x] **arifosmcp** — Fixed crash-loop via hotfix image rebuild
- [x] **Caddy** — Resolved path case-sensitivity (AAA vs aaa) and routing 404s

---

## 🔲 Active TODO

### High Priority
- [ ] **Implementation of CRP** — Integrate `resolve_conflict` logic into the kernel spine
- [ ] **W3 Invariant Enforcement** — Validate triple-witness (WELL/WEALTH/GEOX) in `arifos_judge`
- [ ] **999 SEAL Hardening** — Ensure Merkle hashing includes the full AGI/ASI/APEX handshake

### Medium Priority
- [ ] **Documentation Sync** — Propagate new ontology to wiki.arif-fazil.com
- [ ] **Test Coverage** — Add unit tests for the AGI/ASI/APEX authority chain
- [ ] **Subsurface Bridges** — Harden the biochemical "chemical glue" signaling layer

---
**⬡ DITEMPA BUKAN DIBERI — 999 SEAL ALIVE ⬡**

---

## ✅ SEALED This Session (2026.04.24)

### MCP Infrastructure & Alignment
- [x] `mcp-arifos.json` — canonical server manifest created (streamable-http, port 8080)
- [x] OpenClaw gateway — transport fixed to streamable-http (`openclaw.json`)
- [x] `tool_registry.json` — SSCT v1.0 consolidated (13 tools, tiers PSI/DELTA/OMEGA)
- [x] `constitutional_map.py` — canonical enums appended (VerdictCode, SacredStage, FloorId)
- [x] Stage alignment — 7 drifts fixed across `tools.py`, `contracts.py`, `tool_registry.json`
- [x] `AGENTS.md` — Tier A immutable file registry added
- [x] `Dockerfile` — broken sed patches removed, fastapi explicit install
- [x] `pyproject.toml` — fastmcp dependency fixed (`>=3.0,<4.0`)
- [x] `rest_routes.py` — FastMCP v3 tool resolution helpers added
- [x] `constitutional_guard.py` — hard floor evaluation restored (bypass removed)

### Ontology Hardening
- [x] AGI/ASI/APEX Trinity defined and anchored in all clerk protocols
- [x] CRP v1.0 (Conflict Resolution Protocol) formalized in AGENTS.md
- [x] 7-Layer Stack documented (Physics → Sovereign)
- [x] `CLAUDE.md` + `GEMINI.md` clerk protocols created with L3 AGI binding

### Active Blockers Carried Forward
- [ ] `test_constitutional_guard.py` — 3 failures (pre-existing)
- [ ] `test_diag_trace.py` — 1 failure (pre-existing)
- [ ] Dockerfile `server.py` COPY issue — temporary compose override in place
- [ ] Volatile Qdrant/Redis IPs in OpenClaw systemd env

*Seal ID: AR-MCP-ONTOLOGY-SEAL-2026.04.24*
