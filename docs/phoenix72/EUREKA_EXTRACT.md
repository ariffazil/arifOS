# EUREKA_EXTRACT.md — Old arifosmcp Wisdom Compression
**Generated:** 2026-05-25
**Phase:** PHASE 1 — Archaeological Survey
**Principle:** Extract truth, compress wisdom, discard entropy

---

## Insight Classification Framework

| Insight Type | New Home |
|---|---|
| Tool behavior pattern | `tools/canonical/` or organ proxy |
| Repeated governance rules | `governance/middleware/` |
| Explanatory content | `resources/` |
| Prompting patterns | `prompts/canonical/` |
| Validation logic | `tests/` or `schemas/` |
| Experimental/hack | backlog only, not production |

---

## EUREKA ID: GATEWAY-001
**Old file:** `tools/gateway.py`
**Function:** `arif_gateway_connect`
**Problem solved:** Connect to organ MCP services dynamically without hardcoding URLs
**What was good:**
- `_organ_url()` reads from config dict
- Supports organ name → URL mapping
- Connection timeout and retry logic
- Health check before declaring organ reachable
**What was chaotic:**
- No authentication on organ connections
- No constitutional middleware before proxy dispatch
- Dead organ URLs silently ignored
**Should become:**
- `governance/organ_proxy.py` — FastMCP proxy provider with health + auth
- `resources/registry/organ-endpoints.md` — read-only organ registry
**Canonical PHOENIX mapping:** GEOX/WEALTH/WELL proxy mounting
**Risk:** MEDIUM — network path, no auth today
**Migration decision:** PORT with auth guard added

---

## EUREKA ID: KERNEL-001
**Old file:** `tools/kernel.py`
**Function:** `arif_kernel_route`
**Problem solved:** Route queries to correct organ based on axis/topic classification
**What was good:**
- `_route_by_axis()` — topic classification
- `_check_contradicted_tools()` — detects impossible tool combinations
- `_intent_route()` — matches user intent to organ capability
- `_command_center_cockpit()` — dashboard of organ states
**What was chaotic:**
- Mixed routing logic with display logic
- No clear separation between routing and execution
- `_441_surprise_handler` — clever but unexplained
**Should become:**
- `tools/kernel/arif_kernel_route.py` — thin routing only, display removed
- `resources/kernel/routing-logic.md` — routing decision documentation
- `prompts/canonical/RAF.md` — routing as prompt
**Canonical PHOENIX mapping:** Kernel stage 555 routing
**Risk:** LOW — routing only, no mutation
**Migration decision:** PORT routing logic, DELETE display code

---

## EUREKA ID: JUDGE-001
**Old file:** `tools/judge.py`
**Function:** `arif_judge_deliberate`
**Problem solved:** Multi-organ deliberation with cooldown awareness
**What was good:**
- `_read_well_substrate()` — checks WELL state before judgment
- `_read_well_governance()` — governance file awareness
- `_apply_cooldown_awareness()` — prevents rapid re-judgment
- Verdict types: SEAL, PARTIAL, SABAR, HOLD, VOID
- Floor awareness (F11 SOVEREIGN)
**What was chaotic:**
- Well substrate reads from filesystem (brittle)
- No evidence integration — pure symbolic judgment
- No mathematical/thermodynamic basis
- Hardcoded cooldown periods
**Should become:**
- `governance/verdicts.py` — verdict enum + logic
- `governance/cooldown.py` — cooldown management
- `resources/judge/deliberation-protocol.md` — when to issue each verdict
- `prompts/canonical/JUDGE.md` — judge prompting
**Canonical PHOENIX mapping:** Kernel stage 888 judgment
**Risk:** HIGH — affects capital/operational decisions
**Migration decision:** PORT with evidence integration added

---

## EUREKA ID: VAULT-001
**Old file:** `tools/vault.py`
**Function:** `arif_vault_seal`
**Problem solved:** Immutable audit trail for sealed outcomes
**What was good:**
- `_build_seal_card()` — structured seal output with hash + timestamp + actor
- Append-only to outcomes.jsonl
- Hash chain verification (previous_hash → new_hash)
- Verdict, session, actor, delta_S all recorded
**What was chaotic:**
- Direct filesystem write — no VAULT999 service abstraction
- No Merkle tree computation
- No witness attestation
- Silent failure if write fails
**Should become:**
- `governance/vault_client.py` — VAULT999 service client
- `schemas/vault_seal.py` — Pydantic seal envelope
- `resources/vault/seal-protocol.md` — when/what to seal
- Test: `test_vault_write_gated.py`
**Canonical PHOENIX mapping:** Kernel stage 999 sealing
**Risk:** HIGH — irreversible audit trail
**Migration decision:** PORT with VAULT999 service call

---

## EUREKA ID: MEMORY-001
**Old file:** `tools/memory.py`
**Function:** `arif_memory_recall`
**Problem solved:** Session-aware memory retrieval with context annotation
**What was good:**
- `_annotate_recall_context()` — adds provenance metadata
- Qdrant + Postgres layer support (commented in code)
- Semantic search + keyword search parity
- Session context filtering
**What was chaotic:**
- Returns empty `[]` — no real implementation
- Graphiti reference but not wired
- Six memory layers but only one works
- No L1 ephemeral state management
**Should become:**
- `tools/kernel/arif_memory_recall.py` — real Qdrant query
- `resources/memory/layer-architecture.md` — memory layer docs
- `schemas/memory_recall.py` — Pydantic recall envelope
- `prompts/canonical/MEMORY.md` — memory use guidelines
**Canonical PHOENIX mapping:** Kernel stage 555m memory
**Risk:** MEDIUM — reads from vector store
**Migration decision:** PORT with real Qdrant wiring

---

## EUREKA ID: SESSION-001
**Old file:** `tools/session.py`
**Function:** `arif_session_init`
**Problem solved:** Session initialization with embodiment card and tool surface
**What was good:**
- `_build_embodiment_card()` — system identity + capabilities
- `_build_tool_surface()` — live tool list from registry
- `_compute_risk_leash()` — risk classification for session
- `_compute_warnings()` — runtime warnings for session
- F1/F11/F12 floor awareness in session creation
**What was chaotic:**
- Fake session_id generation (not UUID)
- Embodiment card has embedded shell scripts (weird)
- Tool surface doesn't verify tool actually works
- Risk leash is computed but never enforced
**Should become:**
- `tools/kernel/arif_session_init.py` — real UUID session, real tool verification
- `resources/kernel/embodiment-card-schema.md` — schema for embodiment
- `schemas/session_init.py` — Pydantic session envelope
**Canonical PHOENIX mapping:** Kernel stage 000 initialization
**Risk:** MEDIUM — establishes session context
**Migration decision:** PORT with real session ID and Redis tracking

---

## EUREKA ID: CONSENSUS-001
**Old file:** `tools/consensus.py`
**Function:** `_compute_consensus`
**Problem solved:** Multi-organ consensus before action (GEOLOGIC triad)
**What was good:**
- Three-organ packet: GEOX + WEALTH + WELL
- Organ unreachable → graceful DEGRADED
- Evidence integration via `arif_evidence_fetch`
- Consensus verdict from kernel/judge
**What was chaotic:**
- Dead organ URLs (8081/8082/8083) — returns VOID
- `_is_inside_container()` detection is fragile
- No actual organ MCP calls — purely symbolic
- arifOS kernel URL hardcoded to `http://arifosmcp:8080`
**Should become:**
- `tools/kernel/arif_organ_consensus.py` — real organ MCP proxy calls
- `resources/kernel/consensus-protocol.md` — when/how to use three-organ packet
- `prompts/canonical/CONSENSUS.md` — multi-organ deliberation prompt
**Canonical PHOENIX mapping:** Kernel organ consensus tool
**Risk:** HIGH — cross-organ coordination
**Migration decision:** PORT with live organ proxy calls

---

## EUREKA ID: HEALTH-001
**Old file:** `tools/health.py`
**Function:** `_check_tool_registry`
**Problem solved:** Canonical health check for entire arifOS stack
**What was good:**
- `_check_model_registry()` — 18 models check
- `_check_risk_leash()` — risk_leash.yaml validation
- `_check_tool_registry()` — tool count + allowlist enforcement
- `_check_vault999()` — vault health
- `_load_objective_state()` / `_save_objective_state()` — persistent state
- `_safe_action_class()` — maps risk score to action class
**What was chaotic:**
- tool_registry count is hardcoded 13
- risk_leash.yaml path is hardcoded
- `objective_state.json` is filesystem-based (brittle)
- No drift detection — only existence check
**Should become:**
- `tools/gateway/mcp_drift_check.py` — real registry vs manifest comparison
- `tools/gateway/mcp_health_check.py` — real health aggregation
- `schemas/health_response.py` — canonical health envelope
- `resources/kernel/health-check-protocol.md` — health check documentation
**Canonical PHOENIX mapping:** Gateway stage Ω health
**Risk:** LOW — read-only health reporting
**Migration decision:** PORT with real manifest comparison

---

## EUREKA ID: REASON-001
**Old file:** `tools/reason.py`
**Function:** `arif_mind_reason`
**Problem solved:** Physics-9 grounded reasoning with entropy calculations
**What was good:**
- Uses `core/physics/` for entropy calculations
- AXIOM_SET with physical constraints
- TAU signal detection (anomaly in reasoning)
- Multi-step inference chain
**What was chaotic:**
- Path permission error: `/home/arifos` not accessible
- No real physics9 integration — symbolic only
- TAU signal is hardcoded 0.96
- Evidence comes from `arif_evidence_fetch` but not used
**Should become:**
- `tools/kernel/arif_mind_reason.py` — real evidence + physics9
- `resources/kernel/physics9-axioms.md` — read-only physics9 reference
- `prompts/canonical/REASON.md` — reasoning protocol prompt
**Canonical PHOENIX mapping:** Kernel stage 333 reasoning
**Risk:** MEDIUM — affects judgment basis
**Migration decision:** PORT with evidence integration (fix /home/arifos)

---

## EUREKA ID: FORGE-001
**Old file:** `tools/forge.py`
**Function:** `arif_forge_execute`
**Problem solved:** Reversible execution with thermodynamic cost estimation
**What was good:**
- OPS/777 thermodynamic cost estimation
- Reversibility scoring
- Execution acknowledgment (ack_irreversible)
- F1 Amanah check before execution
- Budget enforcement (BudgetManager)
**What was chaotic:**
- No actual shell/code execution — returns fake results
- OPS cost is hardcoded
- BudgetManager exists but not wired
- No reversible rollback mechanism
**Should become:**
- `tools/kernel/arif_forge_execute.py` — real execution via A-FORGE
- `governance/ops_cost.py` — thermodynamic cost estimator
- `governance/reversibility.py` — reversibility scoring
- `resources/forge/execution-protocol.md` — when/how to forge
- `prompts/canonical/FORGE.md` — forge prompting
**Canonical PHOENIX mapping:** Kernel stage 666 execution
**Risk:** CRITICAL — actual system mutation
**Migration decision:** PORT with A-FORGE execution bridge (NOT direct exec)

---

## EUREKA ID: OPS-001
**Old file:** `tools/ops.py`
**Function:** `arif_ops_measure`
**Problem solved:** Metabolic/thermodynamic measurement of system state
**What was good:**
- g_score (thermodynamic state score)
- dS_component breakdown
- Entropy calculation per component
- Real disk/memory/CPU metrics (os.getloadavg, psutil)
**What was chaotic:**
- g_score hardcoded 0.85
- Only imports psutil but doesn't use it fully
- dS_components returns zeros
**Should become:**
- `tools/kernel/arif_ops_measure.py` — real system metrics
- `resources/kernel/metric-thresholds.md` — g_score interpretation
- `prompts/canonical/OPS.md` — ops measurement prompt
**Canonical PHOENIX mapping:** Kernel stage 777 ops
**Risk:** LOW — read-only measurement
**Migration decision:** PORT with real psutil metrics

---

## EUREKA ID: HEART-001
**Old file:** `tools/heart.py`
**Function:** `arif_heart_critique`
**Problem solved:** Emotional/ethical critique layer for responses
**What was good:**
- empathy_score computation (0-1)
- dignity_check
- Safety filter for outputs
- AFINN sentiment analysis pattern
- Tone management
**What was chaotic:**
- empathy_score hardcoded 0.82
- No real sentiment analysis wired
- dignity_check always passes
- Response rewriting is no-op
**Should become:**
- `tools/kernel/arif_heart_critique.py` — real sentiment + dignity
- `resources/kernel/heart-critique-protocol.md` — when to critique
- `prompts/canonical/HEART.md` — heart prompting
**Canonical PHOENIX mapping:** Kernel stage 444 critique
**Risk:** LOW — affects response tone only
**Migration decision:** PORT with real sentiment analysis

---

## EUREKA ID: EVIDENCE-001
**Old file:** `tools/evidence.py`
**Function:** `arif_evidence_fetch`
**Problem solved:** Evidence ingestion from multiple sources (FRED, news, knowledge)
**What was good:**
- Source type detection (FRED, news, knowledge, web)
- Quality scoring (0-1) based on source type
- Evidence card structure: source, content, quality, timestamp
- Fetch timeout (10s)
- Evidence caching pattern
**What was chaotic:**
- Returns hardcoded placeholder content
- No real data source integration
- Cache is in-memory only
- Quality score is fake
**Should become:**
- `tools/kernel/arif_evidence_fetch.py` — real evidence from sources
- `resources/evidence/fetch-protocol.md` — evidence source documentation
- `schemas/evidence.py` — Pydantic evidence envelope
**Canonical PHOENIX mapping:** Kernel stage 222 evidence
**Risk:** MEDIUM — affects reasoning basis
**Migration decision:** PORT with real source calls

---

## EUREKA ID: REPLY-001
**Old file:** `tools/reply.py`
**Function:** `arif_reply_compose`
**Problem solved:** Structured response composition with governance metadata
**What was good:**
- Verdict integration (SEAL, PARTIAL, SABAR, etc.)
- Tone adjustment based on verdict
- Evidence inclusion from context
- Response envelope with metadata
**What was chaotic:**
- Echoes input back — no real composition
- Verdict metadata is fake
- Tone adjustment is no-op
**Should become:**
- `tools/kernel/arif_reply_compose.py` — real response building
- `resources/kernel/reply-protocol.md` — composition guidelines
**Canonical PHOENIX mapping:** Kernel stage 444r reply
**Risk:** LOW — output formatting only
**Migration decision:** PORT with real composition

---

## EUREKA ID: SENSE-001
**Old file:** `tools/sense.py`
**Function:** `arif_sense_observe`
**Problem solved:** Environmental sensing — disk, memory, load, docker state
**What was good:**
- Multiple observation layers (disk, memory, load, docker)
- TAU signal (anomaly score)
- Risk flag computation
- Docker container state detection
** What was chaotic:**
- TAU hardcoded 0.96
- Most metrics return 0 or None
- Docker detection calls `docker ps` but doesn't parse correctly
- Risk flags are fake
**Should become:**
- `tools/kernel/arif_sense_observe.py` — real system observation
- `resources/kernel/sense-protocol.md` — sensing documentation
**Canonical PHOENIX mapping:** Kernel stage 111 observation
**Risk:** LOW — read-only observation
**Migration decision:** PORT with real metrics

---

## EUREKA ID: WIKI-001
**Old file:** `tools/wiki.py`
**Function:** `arif_wiki_ingest`, `arif_wiki_map`, `arif_wiki_search`, `arif_wiki_ask`
**Problem solved:** TREE777 wiki — knowledge base for the federation
**What was good:**
- Ingest: file-based wiki loading
- Map: topic-to-document mapping
- Search: keyword + semantic search
- Ask: question answering over wiki
- Markdown parsing with frontmatter
**What was chaotic:**
- All return hardcoded placeholder data
- No real wiki files on disk
- Search is grep-based, not semantic
- No ChromaDB or vector search wired
**Should become:**
- `tools/kernel/arif_wiki_*.py` — real TREE777 wiki operations
- `resources/wiki/wiki-architecture.md` — wiki structure docs
**Canonical PHOENIX mapping:** Kernel wiki tools
**Risk:** LOW — read-only knowledge
**Migration decision:** PORT with real wiki path

---

## Summary: Eureka Compression Table

| Old File | Eureka | Compress To | Risk |
|---|---|---|---|
| `gateway.py` | Organ URL mapping | `governance/organ_proxy.py` | MEDIUM |
| `kernel.py` | Routing + axis classification | `tools/` + `resources/` | LOW |
| `judge.py` | Verdict types + cooldown | `governance/verdicts.py` | HIGH |
| `vault.py` | Seal card + hash chain | `governance/vault_client.py` | HIGH |
| `memory.py` | Context annotation + Qdrant | `tools/` + `resources/` | MEDIUM |
| `session.py` | Embodiment card + risk leash | `tools/` + `schemas/` | MEDIUM |
| `consensus.py` | Three-organ packet | `tools/kernel/arif_organ_consensus.py` | HIGH |
| `health.py` | Registry/vault model checks | `tools/gateway/mcp_*.py` | LOW |
| `reason.py` | Physics9 + entropy | `tools/kernel/arif_mind_reason.py` | MEDIUM |
| `forge.py` | OPS cost + reversibility | `governance/ops_cost.py` | CRITICAL |
| `ops.py` | Thermodynamic measurement | `tools/kernel/arif_ops_measure.py` | LOW |
| `heart.py` | Empathy + dignity check | `tools/kernel/arif_heart_critique.py` | LOW |
| `evidence.py` | Source detection + quality | `tools/kernel/arif_evidence_fetch.py` | MEDIUM |
| `reply.py` | Verdict-aware composition | `tools/kernel/arif_reply_compose.py` | LOW |
| `sense.py` | TAU anomaly detection | `tools/kernel/arif_sense_observe.py` | LOW |
| `wiki.py` | Wiki ingest/map/search/ask | `tools/kernel/arif_wiki_*.py` | LOW |
| `registry.py` | Tool registry management | `tools/gateway/mcp_drift_check.py` | MEDIUM |

**Total eureka items:** 17
**PORT:** 17
**DELETE:** 0 (all old files contain compressible wisdom)
**BACKLOG:** 3 (experimental hacks to be evaluated later)

---

*DITEMPA BUKAN DIBERI — wisdom extracted, entropy noted*
