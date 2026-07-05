# arifOS Federation Memory Architecture — Live Map
> **Canonical Source:** `ariffazil/arifOS:FEDERATION_MEMORY.md`
> **Authority:** arifOS F13 SOVEREIGN (Muhammad Arif bin Fazil)
> **Last Verified:** 2026-06-21 by arifOS kernel attestation (tool_count=0 bug found; static fallback deployed)
> **Valid From:** 2026-05-27
> **Rule:** SOT state. All agents must read this for memory layer ground truth. Stale summaries in other docs must point here.

---

## The 6-Layer Federation Memory Architecture (Atlas Compass)

**Core rule from Arif:** AI memory is not one thing. Six different systems wearing the same word. They behave differently, fail differently, and require different governance.

```
Layer  Name               Engine         Status   Role (what it actually is)
─────  ─────────────────  ────────────   ──────   ─────────────────────────────────────────────────
 L1    Ephemeral / working   Redis          ✅ Live  now / current context (working memory)
 L2    Session / personal    Redis          ✅ Live  thread + preference (personal + working)
 L3    Associative / retrieval Qdrant     ✅ Live  fuzzy similarity search (retrieval memory)
 L4    Relational / storage  Supabase     ⚠️ Hold  structured facts & relationships (storage memory)
 L5    Knowledge / retrieval Graphiti     ⚠️ Hold  graph relationships (retrieval + meaning)
 L6    Immutable / constitutional VAULT999 ✅ Live  sealed truth + authority (constitutional memory)
```

Model memory (the LLM weights themselves) lives outside these layers. It is pattern compression, not state.

### Memory Types (Arif taxonomy) mapped to layers

- **Storage memory**: L4 (Postgres schemas) + raw files/MinIO. Exact records, constraints, history.
- **Retrieval memory**: L3 + L5. Search over past. Can pull wrong/stale/partial.
- **Personal memory**: L2 + AAA identity. Preferences, continuity. Risk: caricature.
- **Working memory**: L1 + L2 context window. Temporary. Lost on reset.
- **Model memory**: Outside (LLM training weights). Hard to edit, statistical patterns only.
- **Constitutional memory**: L6 VAULT999 + kernel floors + registries. Authority, seals, what is allowed to influence action.

Each type needs different authority, expiry, provenance, and action boundary. Not all memory is equal.

### The Trilemma + Quantum Problem (governance disguised as convenience)

Usefulness ↔ Truth ↔ Safety. Optimise two, the third suffers.

- Useful + truthful = may remember too much (creepy, F6 MARUAH violation, legal risk).
- Useful + safe = summaries that distort ("tired of investors" becomes "dislikes investors").
- Truthful + safe = almost nothing persisted → every session starts from zero.

Memory is not passive. Once loaded into prompt or used by agent, it changes the future answer and can delegate authority.

" I remember you wanted X " or "based on previous, I did Y" is now input to decision. Therefore every memory write must carry:
- source (observed / inferred / user-declared)
- evidence tier (OBS / DER / INT)
- owner / actor
- expiry / TTL
- action boundary (style only? decision input? irreversible?)
- reversibility flag (F1)
- floor checks (especially F2 Truth, F6 Maruah, F11 Audit)

### Authority Bands (different memory, different rules)

| Band                  | Layer example | Risk if ungoverned          | Required authority                          | Floors that bite hardest |
|-----------------------|---------------|-----------------------------|---------------------------------------------|--------------------------|
| Preference memory     | L2            | Caricature of human         | Soft, user-editable, low blast              | F6, F7, F4               |
| Project / continuity  | L2 + L3       | Stale architecture          | Session + provenance                        | F2, F4                   |
| Evidence memory       | L3 + L4       | False certainty             | Source-backed only, high witness            | F2, F3, F11              |
| Decision / verdict    | L6            | Wrong authority delegated   | Seal only via 888 + VAULT999                | F1, F11, F13             |
| Identity memory       | L2 + AAA + L6 | Privacy / dignity           | Strictest ACL, F13 override, human veto     | F6, F13, F9              |
| Agent state / workflow| L1 + L2       | Unsafe action               | Audited, reversible or HOLD on irreversible | F1, F5, F11, F12         |

Constitutional memory (L6 + floors + registries) is the conscience. It decides what the other memories are allowed to do.

### Real Architecture Rule

Database / Memory layers store what is (facts, receipts, state).
LLM compresses patterns (never treat as record).
Agentic loops use them to act.
Governance (arifOS kernel) decides what may be remembered, trusted, acted upon, or forgotten.

Raw event → summary → evidence tier → permission → expiry → retrieval rule → action boundary → audit.

No memory enters the loop without provenance and floor check. Drift between layers = HOLD.

---

## Human Memory: Reconstruction, Not Storage (Foundation)

Human memory is **not a database**. It is a living, lossy, emotional, reconstructive system.

Brain process:

experience → attention → encoding → emotional tagging → consolidation → retrieval → reconstruction → re-storage.

Every recall rebuilds. Two honest people can remember the same event differently — different fragments, emotional tags, context.

Brain systems:
- Hippocampus: binds events, place, time, sequence.
- Neocortex: patterns, concepts, long-term knowledge.
- Amygdala: emotional salience (threat, reward).
- Prefrontal: working memory, control.
- Basal ganglia: habits, skills.
- Body/nervous: stress, trauma, felt sense.

Human memory prioritises survival and meaning (threat, food, social, love, pain, novelty, repetition) over audit-grade truth. Forgetting is compression — without it, no generalisation.

**Types of human memory:**
- Working: hold now (limited, hence external tools).
- Episodic: experienced events.
- Semantic: facts/concepts.
- Procedural: skills/habits.
- Emotional: feeling-tagged.
- Social: who did what, reputation.

Digital world is scaffolding: phone (pocket memory), calendar (future), database (structured), AI (interpreted). It makes memory searchable, persistent, networked — but also overwhelming, surveillant, hard to forget.

**The digital memory bargain:** Gains (never lose, search everything) vs costs (clutter, dependence, experience-as-archive, surveillance, personalisation drift, ownership ambiguity). Forgetting becomes difficult — a civilisation problem: what deserves to decay?

## Institutions Civilise Memory

Institutions turn messy human memory into durable public reality:

- Court: evidence, witness, procedure, admissible, appeal.
- Bank: transaction record, timestamp, identity, audit trail.
- University: curriculum, exam, certificate, transcript.
- State: title deed, registry, law, archive.

Adds: procedure, witness, record, standard, authority, appeal, audit, continuity.

But can distort: bureaucratic blindness, propaganda, cover-up, selective history, weaponised docs.

Good institutions need: appeal, transparency, independent audit, public record, whistleblower, archival integrity, time limits, right to correction.

## The Memory Ladder

Biological memory → spoken → ritual → written → bureaucratic → database → networked → AI-interpreted → **governed constitutional memory**.

Each layer increases power and risk.

| Layer | Strength | Failure |
|-------|----------|---------|
| Human | meaning, emotion, judgement | bias, forgetting |
| Oral | communal continuity | myth drift |
| Written | durability | selective |
| Bureaucratic | procedure | rigidity |
| Database | precision | context loss |
| Networked | connection | misinformation |
| AI | synthesis | hallucinated continuity |
| Governed constitutional | traceability + floors | over-ritualisation |

## arifOS: Memory Civilisation Project

arifOS is not just AI governance. It decides:

what counts as memory, evidence, decision, authority, irreversible, logged, forgotten, human veto.

**Mapping:**

| Human civilisation | arifOS equivalent |
|--------------------|-------------------|
| memory | state (L1-L6) |
| testimony | witness (F3, provenance) |
| archive | VAULT999 (L6) |
| law | F1–F13 |
| court | kernel adjudication (888) |
| officer | agent (organs) |
| registry | canonical paths (registries, mcp_surface) |
| audit | drift scanner + F11 |
| sovereign judgement | Arif / F13 |

Memory governance disguised as convenience. Human gives meaning. Digital gives persistence. Institutional gives authority. AI combines all three — without wisdom unless governed.

**The Agentic Intelligence Flow (wired):**

Human experience (biological reconstruction, emotional tag) 
→ attention/encoding in agent (L1/L2 working + personal) 
→ digital storage/retrieval (L3/L4/L5, with evidence tier OBS/DER/INT) 
→ institutionalise (kernel floors check, registries as procedure) 
→ constitutional memory (L6 VAULT + authority bands + provenance + expiry + action boundary) 
→ governed action (A-FORGE with SEAL only after 888, F13 veto).

Raw event → summary → tier → permission/expiry/boundary → floor check → seal if irreversible → agent act (with audit).

Every step in the flow must carry provenance. LLM (model memory) only compresses patterns inside organs — never authors the record. Agentic loops (GEOX/WEALTH/WELL/A-FORGE) use layers but cannot bypass constitutional gate. arifOS kernel is the conscience.

This is the wired flow. Drift at any layer = HOLD. No memory influences action without the ladder.

### Live Counts & Milestone 2 Gate (as of 2026-06-02)

| Layer | Store | Count | Phase 1 Verdict |
|-------|-------|-------|-----------------|
| L1/L2 | Redis | - | Live |
| L3 | Qdrant | 864 vectors | Live |
| L4 | Supabase Cloud | shelves exist | Shelves built. Workers not filing yet. |
| L5 | Graphiti | partial | - |
| L6 | VAULT999 | 16,859 lines | Active |

### Supabase Cloud — Phase 1 Domain (L4)

*Naming convention: `arifosmcp_*` not `s000.*` — same intent, different namespace.*
*See the full integration rule: [SUPABASE_MCP_CONTRACT.md](file:///root/arifOS/docs/contracts/SUPABASE_MCP_CONTRACT.md).*

**Structured Tables (Shelves Built):**
- `arifosmcp_tool_calls`
- `arifosmcp_approval_tickets`
- `arifosmcp_floor_rules`
- `arifosmcp_memory_policy`
- `arifosmcp_memory_contract`
- `arifosmcp_sessions`
- `arifosmcp_canon_records`
- `arifosmcp_daily_roots`
- `arifosmcp_portfolio_snapshots`
- `arifosmcp_transactions`
- `arifosmcp_well_states`
- `arifosmcp_agent_telemetry`
- `mcp_prompt_versions` (planned)
- `mcp_resources` (planned)
- `mcp_manifest_snapshots` (planned)

**VAULT L4/L6 FACET:**
- `vault_sealed_events` (1,338 rows — actual L6 mirror)
- `vault_outcomes` (12,269+ rows)
- `vault_seals` (61 rows — legacy)
- `vault_shim_hits` (2 rows)

> **Milestone 2 Integration Gap:** arifOS MCP and federation organs must write receipts via the shared organ adapter (fail-soft). Do not connect Supabase to MCPs as a router.

---

### Port Map

| Service | Address | Port | Access |
|---------|---------|------|--------|
| Qdrant | `127.0.0.1` | 6333 | localhost Docker proxy |
| PostgreSQL | `0.0.0.0` | 5432 | Docker-managed |
| Redis | `0.0.0.0` | 6379 | Docker-managed |
| Ollama | `127.0.0.1` | 11434 | localhost |
| Graphiti MCP | container net | 8080 | arifOS MCP bridge only |
| VAULT999 | `/root/arifOS/VAULT999/` | — | file system, all agents |

---

## Agent Access Map

```
Agent          L1/L2       L3 Qdrant    L4 Postgres  L5 Graphiti   L6 VAULT999
────────────   ─────────   ──────────   ──────────   ──────────   ──────────
arifOS MCP (Ω)  ✅ via     ✅ R/W       ❌ blocked   ✅ R/W via    ✅ R/W
                session              DB down        arifOS MCP    ack_irrevers
                                   ──────────────────────────────   ible write
Hermes ASI      ✅ native  ❌           ❌            ❌            ✅ seal
(Telegram)      L1/L2                                                         events only
AAA Cockpit     ✅ via     ❌           ❌            ✅ telemetry   ❌
                            A2A                       via broker
WELL            ✅ own     ✅           ❌            ❌            ✅ own
                state                                                         outcomes only
WEALTH          ✅         ✅           ❌            ❌            ✅ ledger
                                                                          append
GEOX            ✅         ✅           ❌            ❌            ❌
A-FORGE         ✅         ❌           ❌            ❌            ❌
OpenCode/       ✅ full    ✅ via       ❌            ✅ via        ✅ via
Kimi             L2        arifOS                  arifOS       arifOS
```

**Note:** `arifOS MCP` (port 8088) is the **ONLY** gateway. Direct Qdrant/Postgres/Redis/file writes from organs/agents = violation per AGENTIC_MEMORY_ROUTING.md. All must route through memory_store.py enforce_memory_routing + kernel gates. Bypass = auto HOLD.

---

## Hermes ASI Private Memory

Distinct from federation memory. Not shared across agents.

```
MEMORY.md   — 2,200 char bounded snapshot, prompt-injected, zero latency
USER.md     — user profile, preferences, corrections
state.db    — FTS5 full-text session transcript, 30-day auto-prune
```

---

## Federation Memory Broker Plugin

**Location:** `/root/.hermes/plugins/federation-memory-broker/`

- Polls Hermes `state.db` every 60s
- Writes telemetry to Redis key: `federation:hermes:session_telemetry`
- Exposes `federation_get_hermes_telemetry()` via A2A for AAA cockpit
- **Status:** Plugin installed but Redis keys not populating — broker loop may not be active. Telemetry only, not critical path.

---

## Known Discrepancies vs. Stale Docs

| Claim in old docs | Actual state | Corrected |
|-------------------|-------------|-----------|
| Qdrant "42 vectors" | 10 pts total (2 collections) | ✅ update doc |
| PostgreSQL "62 records" | Empty, nothing writing | ✅ correct |
| VAULT999 "14,786 entries" | 16,794 lines total | ✅ correct |
| L4 relational | DB up (33h) but schema inactive | ✅ note as DOWN |
| Graphiti | Running (35h, healthy) but not remotely queryable | ✅ clarify |

---

## DITEMPA BUKAN DIBERI

Memory ground truth comes from live probes, not from cached summaries.
Every agent must verify before acting on memory-layer claims.

**Version:** 1.0 | **Sealed:** 2026-05-27 | **Authority:** arifOS F13 SOVEREIGN
