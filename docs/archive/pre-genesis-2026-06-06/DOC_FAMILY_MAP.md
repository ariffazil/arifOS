# arifOS DOC_FAMILY_MAP — Root .md Files

> Generated: 2026-05-23T09:19 UTC  
> Scope: `/workspace/arifOS/*.md` (root only, 13 files)  
> Method: git log epoch, grep FLOOR/F13/SOT, cross-ref sampling, Python/sh reference counts

---

## DOC_FAMILY_MAP

| File | Family | Epoch | SOT Status | Bucket | Rationale |
|------|--------|-------|------------|--------|-----------|
| `AGENTS.md` | philosophy | 2026-05-22T16:22:50Z | **YES** | **LIVE** | Defines operational identity (agent onboarding + architecture). References FLOOR/F13. 177 Python/sh refs across codebase. Cross-refs AGENTS/, A000/, EUREKA_COMPENDIUM. SOT-aligned. |
| `ARIF.md` | release_notes | 2026-05-22T16:22:50Z | **YES** | **LIVE** | Canonical SOT state reporter ("METABOLIC KERNEL"). Documents current operational state, topology, and interrupts. FLOOR/F13 + 999 SEAL references. Referenced in ARIFOS_SESSION summaries. |
| `BOUNDARY.md` | architecture | 2026-05-22T16:22:50Z | **YES** | **LIVE** | **SOT-MANIFEST** header (verified 2026-05-22 → 2026-06-22). Defines owns/does-not-own, imports/exports, tool surface (14 canonical). Official authority boundary declaration. |
| `CHANGELOG.md` | release_notes | 2026-05-22T16:22:50Z | **YES** | **LIVE** | Version history v2026.05.21–25. FLOOR/F13 references (NIAT gate, capability membrane, F01–F13 hardening). 206 lines. 137 doc cross-refs. Active release tracking. |
| `FEDERATION.md` | architecture | 2026-05-22T16:22:50Z | **YES** | **LIVE** | Federation topology (arifOS→GEOX/WEALTH/WELL) with FLOOR/F13 governance. MCP contract table (13 tools). Describes 000–999 metabolic loop. 15051 bytes. Canonical. |
| `FEDERATION_CONTRACT.md` | governance | 2026-05-22T16:22:50Z | **YES** | **LIVE** | Sovereign authority map (L1–L6). Interaction rules (1-repo-1-authority, evidence-before-verdict). FLOOR/F13 references. Contracts `contracts/federation.yaml` and `BOUNDARY.md`. |
| `IDENTITY.md` | philosophy | 2026-05-22T16:22:50Z | **YES** | **LIVE** | OPENCLAW identity definition. "Arif Governed Intelligence". Anti-Hantu rule, Prime Directive, instrument framing. References SOUL/F13. Agent identity anchor. |
| `MIGRATE_TO_WSL.md` | archive | 2026-05-22T16:22:50Z | **SUPERSEDED** | **ARCHIVE** | WSL2 migration runbook (Windows→Ubuntu). Zero cross-refs in code or docs. No FLOOR/F13 references. Last git activity: generic forge commit `2ace4ca`. Historical context only. |
| `PUBLIC_SURFACE_CANON.md` | architecture | 2026-05-22T16:22:50Z | **YES** | **LIVE** | **Status: SEALED** (v2026.04.30-KANON). Canonical 13 + 2 probe tools. Public MCP contract. Golden path (init→sense→judge→seal). Official public surface definition. |
| `README.md` | philosophy | 2026-05-22T16:22:50Z | **YES** | **LIVE** | Project overview with **SOT-MANIFEST** header (verified→2026-06-22). FLOOR/F13 + verdict engine (SEAL/HOLD/VOID/SABAR). Links to `docs/MCP_SOURCE_OF_TRUTH.md`. 325 lines. Primary onboarding. |
| `SOUL.md` | philosophy | 2026-05-22T16:22:50Z | **YES** | **LIVE** | Identity, Niat, constitutional spine. "Machine≠Governance≠Intelligence". 000–999 loop. FLOOR/F13 governance anchor. Anti-Hantu + ReAct boundary. 3 cross-refs to other root docs. |
| `SPEC.md` | architecture | 2026-05-23T08:43:00Z | **YES** | **LIVE** | Most recent epoch (by 14h). Portable contract architecture (Layer 1–5). F1–F13 floor definitions, verdict envelope schema, storage abstraction, provider switch. `905f65b` — Stage B machine kernel artifacts. |
| `USER.md` | governance | 2026-05-22T16:22:50Z | **YES** | **LIVE** | Muhammad Arif bin Fazil profile. Sovereign human judge. Telegram ID + role definition. 11 lines. Referenced by session init and identity systems. |

---

## Summary

| Bucket | Count | Files |
|--------|-------|-------|
| **LIVE** | 12 | AGENTS, ARIF, BOUNDARY, CHANGELOG, FEDERATION, FEDERATION_CONTRACT, IDENTITY, PUBLIC_SURFACE_CANON, README, SOUL, SPEC, USER |
| **ARCHIVE** | 1 | MIGRATE_TO_WSL |
| **DELETE** | 0 | — |

| SOT Status | Count |
|------------|-------|
| **YES** | 12 |
| **SUPERSEDED** | 1 |

| Family | Count |
|--------|-------|
| philosophy | 4 (AGENTS, IDENTITY, README, SOUL) |
| architecture | 4 (BOUNDARY, FEDERATION, PUBLIC_SURFACE_CANON, SPEC) |
| release_notes | 2 (ARIF, CHANGELOG) |
| governance | 2 (FEDERATION_CONTRACT, USER) |
| archive | 1 (MIGRATE_TO_WSL) |

---

## Recommendation

- **MIGRATE_TO_WSL.md**: Move to `docs/archive/` or mark for deletion. No active SOT relevance.
- **SPEC.md**: Most recently forged (`905f65b`). Verify if it supersedes parts of `BOUNDARY.md` or `FEDERATION.md` (architectural overlap observed).
- All 12 LIVE files are actively referenced in Python/sh code or doc cross-refs. Confirmed SOT-aligned.