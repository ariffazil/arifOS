# CANONICAL_REGISTRY_GOVERNANCE.md

> **Single Source of Truth for the arifOS Federation**
> Every organ reads the same reality at the same time.
> Drift = constitutional breach (F2, F4, F8, F11).
>
> Authority: F13 SOVEREIGN (Arif) — refined 2026-07-05
> Supersedes: ad-hoc merges, multiple static sources, manual reconciliation.
> DITEMPA BUKAN DIBERI

## Core Principle

**Shared substrate. Strict namespaces. One canonical write path per registry type.**

Organs (GEOX, WEALTH, WELL, A-FORGE, AAA, arifOS) are **processors**, not sovereign states.
- They own domain computation and their raw data files (files, MinIO buckets for volume).
- The **kernel (arifOS)** owns governance state, verdicts, seals, and the canonical view of "what exists right now".

### Layer Separation (Storage vs Patterns vs Action vs Governance)

Database / dataset / memory = stores reality (exact facts, relationships, history, receipts).
LLM = compresses statistical patterns from language (good at inference, summarisation, drafting — weak at exact truth or current state).
Agentic intelligence = uses models + memory + tools + goal + loop to pursue action.
Governed agent = the above under floors, evidence, authority, and F13 veto.

**Never conflate them.**

- Registries here are **Database/Memory layer** — structured state, not LLM-generated "knowledge".
- They answer "what is recorded?" not "what is most likely?".
- LLM pattern engines may help *interpret* registry content (inside domain organs), but never replace or author the canonical record.
- See also: /root/AAA/docs/AGI_VS.md (LLM Memory vs Agentic Memory matrix) and /root/arifOS/FEDERATION_MEMORY.md (full 6-layer + Arif taxonomy + authority bands + memory ladder + human reconstruction + institutions civilise + agentic intelligence flow). Registries are the bureaucratic/institutional layer in the ladder.

Metaphor:
Database = library shelves / sample catalogue.
Dataset = training examples / historical core logs.
Memory = notebook of events + receipts.
LLM = educated mind that infers and speaks.
Agent = worker with tools doing the task.
Governed agent (arifOS) = worker under law, audit, evidence protocol, and sovereign authority.

"Shared" does **not** mean "everything mixed in one bucket".
It means:
- One Postgres instance → schema-per-organ + Row Level Security / ACLs (aaa, wealth already exist; add geox, well, arifos).
- One Qdrant → collection-per-domain (arifos_*, aforge_*, arif_human_substrate etc.).
- One VAULT999 (immutable, append-only) — the only place for final SEALs.
- Separate object tier (MinIO) for high-volume raw data (GEOX SEGY/LAS volumes).
- Stricter isolation for WELL (F6 MARUAH — human signals deserve dedicated schema + tight ACLs).
- **One canonical write authority** per registry.

## The 9 Canonical Registries (from 00-master-index.yaml)

These are **Database / Memory layer** artifacts — structured, queryable, provable state. Not LLM "understanding".

See `/root/arifOS/registry/00-master-index.yaml` for the machine list. Governance rules below.

| # | Registry | Write Authority (Canonical) | Read Path (Single) | Provenance Required | Notes |
|---|----------|-----------------------------|--------------------|---------------------|-------|
| 01 | CONSTITUTION | arifOS kernel only | arifos://doctrine + 01-constitution.yaml | Full (kernel seal) | Immutable floors. DB of law. |
| 02 | IDENTITY (Agents) | AAA (primary) + arifOS kernel ratification | arifos://identity + AAA_AGENTS_REGISTRY.json + /.well-known/agent*.json via kernel | actor_id + timestamp + card hash | One source for active agents. Memory of who exists. |
| 03 | TOOLS / Capabilities | arifOS (constitutional_map.py + arifos_registry/mcp_tool_registry.py) | arifos://registry/toolregistry + arifos://tools (kernel aggregated) | organ, schema_hash, blast_radius, reversible, source_repo, signed | Structured capability state. LLM may use it; never authors it. |
| 04 | SCARS | arifOS + VAULT999 | arifos://scars | Seal chain ref | Immutable once sealed. |
| 05 | MODELS | arifOS | arifos://models | Model + forbidden actions | Registry of pattern engines (not the engines themselves). |
| 06 | PHILOSOPHY | arifOS | arifos://philosophy | | Structured doctrine memory. |
| 07 | MEMORY (L1-L5) | Shared substrate (namespaced) + arifOS governance | Qdrant collections + arifos://memory | actor + layer + timestamp | L6 is VAULT999. |
| 08 | VAULT | VAULT999 only (append) | outcomes.jsonl + seal_chain | Hash chain + actor | The ultimate durable memory. |
| 09 | WITNESS | arifOS + VAULT999 | arifos://witness | Tri-witness packet | Evidence packets as state. |

## Write Rules (Non-Negotiable) — Enforcement to make drift impossible

1. **Single canonical write path**: ONLY through arifOS kernel:
   - `arifos_registry/mcp_tool_registry.py:MCPToolRegistry.register(manifest: ToolManifest)`
   - Or governed MCP tool `arif_register_organ_surface` (to be wired).
   - This updates the live canonical (in-memory + Qdrant mcp_capabilities + Postgres aaa.mcp_surface).
   - AAA/docs/TOOLREGISTRY.json, per-organ registry.py, arifOS manifests, GEOX/WEALTH lists etc. are **DERIVED / read-only snapshots**. Direct edits are rejected by drift detectors + future hooks.

2. **Namespace allocation for plug-in**: New organ declares (via A2A or kernel call) → kernel (substrate_namespace_registry + namespace_guard) allocates prefix, updates master, creates necessary schema/collection entries. No manual wiring of manifests/schemas/sync.

3. **Manifest requirement + rejection hooks**: Every tool uses ToolManifest with full fields. register() enforces no duplicates, valid namespace (via NamespaceGuard), provenance. Non-canonical writes (hand @mcp.tool outside registration, direct JSON edits) are rejected at load/registration time and flagged for auto-HOLD.

4. **Propagation + auto validation**: Canonical write propagates to shared stores. On health/probe/drift_detector: compare (mcp_surface.tool_count + schema_hash vs Qdrant mcp_capabilities vs resource content). Mismatch → auto 888 HOLD + F11 log. No manual reconcile.

5. **Single read path**: All organs/agents/AAA/OpenClaw query ONLY arifos://registry/toolregistry (or kernel arif_get_registry tool). Per-organ lists for internal domain only. Kernel guarantees the number.

## Read Rules

- **One canonical read path**: Use arifos://* resources (federation_registry.py and siblings) or kernel tools (arif_retrieve_tools, arif_federation_state, etc.).
- All organs and edge agents MUST query the kernel-backed view for federation-wide questions ("what tools exist?", "active agents?", "which organ can do X?").
- Direct FS reads or per-organ lists are for internal domain use only and must not be treated as federation truth.

## Drift & Governance

- Drift detector (registry/drift_detector.py): DB says X, registry says Y, resource shows Z → VOID or auto-HOLD.
- Every registry entry carries provenance: who (actor_id/organ), when, from which write path, hash of content, optional seal ref.
- Cross-layer inconsistency on critical registries (tools, identity, constitution) triggers F11 + 888 path.
- New organ onboarding is "plug in": implement prefixed tools, provide manifest, call registration (future: at boot via kernel), done. No manual schema/ collection/ manifest sync.

## Special Cases (the 15%)

- **WELL privacy (F6 MARUAH)**: Use dedicated schema (well) + strict ACLs / RLS. Human substrate signals are dignity-sensitive.
- **GEOX volume**: Raw seismic/well logs → MinIO buckets with GEOX-specific policies (separate from governance state). Ingest metadata + evidence go to shared layers.
- **A-FORGE CouchDB**: Justified for ephemeral execution scratch (different lifetime from durable governance memory).
- **Registry duplication was governance, not infra**: Even with perfect DBs, without canonical write authority + rejection of non-canonical writes, drift happens. Fix is authority + hooks, not more clusters.

## Current Scaffolding (2026-07-05 reality)

- Namespaces + Guard: arifos_registry/substrate_namespace_registry.py + namespace_guard.py
- ToolManifest + CapabilityManifest: arifos_registry/
- Master Index: 00-master-index.yaml (9 registries)
- Kernel source for arifOS tools: constitutional_map.py + tools_canonical.py
- MCP resources: resources/federation_registry.py (arifos://registry/toolregistry etc.)
- Postgres aaa schema: mcp_surface, namespace_summary, unified_tool_calls
- Qdrant: mcp_capabilities collection + arifos_* memory collections
- VAULT999: single source for seals

## Payoff (Arif's "So What")

- Seals based on one reality → trivially auditable (F11).
- New organ = declare + plug in. No data migration hell.
- One number for active agents / tools / capabilities. No reconciliation meetings.
- Drift becomes impossible (rejected at write hook), not just unlikely.
- Federation-wide reasoning works reliably ("what overlaps?", "what is missing?").
- Effort shifts from "keep the registries in sync" (systems admin tax) to "F3 witness, F11 audit, F6 dignity, F8 genius" (constitutional court).

## Enforcement Plan (Next)

1. Make arifos:// resources the enforced single read (update all consumers).
2. Wire dynamic registration hook (organ surface → kernel canonical write with provenance).
3. Add full provenance envelope to all 9 registry entries.
4. Harden drift detector to auto-HOLD on critical mismatch.
5. MinIO policies + WELL schema ACLs.
6. Update per-organ AGENTS.md to mandate "read federation truth from kernel resources only".

When complete: every organ, every agent, every seal operates on the same truth at the same time.

**This is what makes the kernel sovereign — not intelligence, but being the only trustworthy source.**

*Sealed under F13. Update this file on any constitutional change to registry authority.*
