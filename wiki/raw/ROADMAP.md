# arifOS ROADMAP — THE BODY (Engineering & Scaling)

**Version:** 2026.04.07-SOT-SEALED
**Authority:** Muhammad Arif bin Fazil (999_VALIDATOR)
**Vision:** *Execution is the proof of Law.*

> **SoT Rule:** Doctrine conflict → this repo wins. Runtime surface conflict → live `/health` + `/tools` wins.

---

## 🔭 PLATFORM AGNOSTICISM STRATEGY — EMV/NPV ANALYSIS

arifOS is LLM-agnostic and platform-agnostic by design. The question is **how** to surface that agnosticism. Four paths, ranked by Expected Monetary Value × Net Present Value:

### Path A — Tool `platform=` Mode Parameter *(Foundation Shipped — Dispatch Pending)*
`platform: str` param added to all 10 tools (ff78faef). `_stamp_platform()` stamps context on every envelope.  
**Remaining:** Literal type in tool_specs, output_formatter dispatch, ToolExecutionContext field.

| | Value |
|---|---|
| **Effort** | 1–2 weeks (tools.py + schemas.py) |
| **EMV** | $20–50k (faster partner integrations) |
| **NPV @ 12mo** | ~$35k |
| **Risk** | Low — additive change, no breaking surface |

### Path B — MCP Profile Gateway *(H2 2026)*
Single `/mcp` endpoint with client-profile detection via header (`X-Arifos-Platform`).  
Each profile gates tool subset + output format + rate policy.

| Profile | Tools exposed | Use case |
|---|---|---|
| `chatgpt_apps` | `arifos_init`, `arifos_judge`, `arifos_vault` (read-only) | ChatGPT widget |
| `cursor` | Full 10-tool surface | Developer IDE |
| `enterprise` | Full surface + signed responses | B2B API |
| `stdio` | Full surface, text output | CLI/agent scripts |

| | Value |
|---|---|
| **Effort** | 4–6 weeks (new middleware layer) |
| **EMV** | $100–300k |
| **NPV @ 18mo** | ~$180k |
| **Risk** | Medium — profile management infra needed |

### Path C — REST Constitutional API *(2027)*
Expose arifOS judgment as standard REST endpoints ANY LLM can call via HTTP.  
MCP becomes one transport, not the only one.  
OpenAI custom actions, Anthropic tool use, and raw HTTP all point to the same API.

```
POST /api/v1/judge     → F1-F13 verdict (replaces arifos_judge)
POST /api/v1/init      → session bootstrap
POST /api/v1/sense     → evidence gather
GET  /api/v1/health    → constitutional health
```

| | Value |
|---|---|
| **Effort** | 8–12 weeks + auth layer |
| **EMV** | $500k–$1M |
| **NPV @ 24mo** | ~$600k |
| **Risk** | High — larger attack surface, requires API key auth, versioning |

### Path D — ChatGPT Widget Phase 1 *(Fix & Ship Now)*
Fix the missing deployment blockers and ship the existing ChatGPT Apps SDK integration.

**Blocker status (2026.04.07-TIER1-SEALED):**
- ✅ `widget-csp.conf` — created and committed
- ✅ `nginx.conf` — `server_name mcp.af-forge.io` confirmed correct in all server blocks
- ✅ `docker-compose.yml` — service renamed `arifos-mcp`, `ARIFOS_MCP_*` env vars, v2026.04.07
- ⏳ DNS — A record pointing `mcp.af-forge.io` → VPS IP (human action required)
- ⏳ TLS — certbot run on VPS after DNS resolves (888_HOLD)
- ⏳ Widget wiring — `vault-seal-widget.html` static path verified; live tool connection pending TLS

| | Value |
|---|---|
| **Effort** | 1–2 weeks (DNS + TLS + domain fix) |
| **EMV** | $30–80k (ChatGPT marketplace reach) |
| **NPV @ 6mo** | ~$40k |
| **Risk** | Low–Medium (platform dependency on OpenAI Apps SDK) |

### **Recommended Execution Order (Highest EMV/NPV)**

```
NOW (0–2 weeks):    D + A  →  Fix ChatGPT deployment + add platform= mode
MID (1–4 months):   B      →  MCP Profile Gateway (clean architecture)
LONG (4–12 months): C      →  REST Constitutional API (true platform agnosticism)
```

**Total NPV trajectory:** $35k (A) + $40k (D) + $180k (B) + $600k (C) = **~$855k addressable over 24 months**  
*Conservative estimates. Enterprise licensing (CaaS) would 3–5× the long-term figure.*

---

---

## 🚀 PHASE 1: THE CONSTITUTIONAL ENGINE (CURRENT)
- **AGI Mind Pipeline (ACTIVE):** Scale "Speak Narrow" principle to all agent communications.
- **Entropy Budgets (PENDING):** Formalize chaos_score() across all MCP endpoints.
- **Provenance Ledger (PENDING):** Connect VaultLedger directly to AGI Mind Provenance.

---

## 📊 DRIFT AUDIT SUMMARY (Apr 1 → Apr 6)

| Dimension | Apr 1 | Apr 6 | Δ |
|-----------|---------|---------|---|
| Constitutional Coverage | 80 | 96 | +16 |
| Injection Resistance | 70 | 92 | 0* |
| Determinism | 75 | 90 | 0 |
| Machine Verifiability | 60 | 90 | +30 |
| Documentation Coherence | 85 | 93 | +8 |
| Runtime Governance Integrity | 82 | 94 | +12 |
| Theory of Mind Integration | 0 | 95 | +95 |
| **Overall Readiness** | **85** | **96** | **+11** |

*\*Unchanged until automated suite exists.*

**Band:** Early Institutional Grade, trending toward **Governance Robustness + Cognitive Alignment**.

### 🎯 HORIZON II.1 COMPLETE: ToM-Anchored MCP (2026.04.06)

The 9+1 Constitutional Architecture is now operational:

- ✅ **9 Governance Tools** with mandatory ToM fields
- ✅ **1 Execution Bridge** (`arifos_forge`) gated by SEAL
- ✅ **Philosophy Registry v1.2.0** — 83 quotes, G★ bands
- ✅ **Clean 2-term naming** — `arifos_init`, `arifos_judge`, etc.
- ✅ **Separation of Powers** — Think/Validate vs Execute strictly separated

---

## 🏗️ HORIZON 1: THE EXECUTION ENGINE (Current)

*Goal: Solidify the 11 Mega-Tool Surface for Institutional Adoption.*

- [x] **Unified MCP Surface:** Single arifOS MCP server, dual transport (stdio/http/streamable-http) with health/build/ready endpoints.
- [x] **Constitutional Health Tooling:** `get_constitutional_health` + `render_vault_seal` + `list_recent_verdicts` live in arifosmcp.
- [x] **ChatGPT Apps Integration:** Apps SDK manifest bound to `/mcp`, widget served via `ui://arifos/vault-seal-widget.html`.
- [x] **Vault999 Blueprint:** BLS+hash+Merkle log model defined; migration strategy drafted.
- [x] **Validator CLI + Telemetry:** Governance in code, with tri-witness/ΔS/Ω₀ telemetry surfaced for tools and (soon) `/dashboard`.
- [x] **Institutional Pilot Vector:** ChatGPT App path is now a concrete integration story for pilots.
- [x] **A-RIF Canon:** Created 000_A-RIF.md — Arif Retrieval Intelligence Framework v1.0.
- [x] **Governed Sensing Protocol:** 8-stage constitutional sensing with IntelligenceState integration.
- [x] **Unified Quote Corpus:** 50 core quotes (5 per tool), schema v2.1.0-unified.
- [x] **Eigent Deployment:** VPS backend deployed at `eigent.vps.arif-fazil.com` with MiniMax-M2.7.
- [x] **MiniMax MCP Integration:** `web_search` + `understand_image` connected to opencode.
- [x] **Three-Layer Identity Binding:** F11 hardened — model declares, system verifies, session binds (soul + runtime + boundary).
- [x] **Vector Memory:** Ollama `nomic-embed-text` for local semantic search.
- [x] **Weekly HF Sync Cron:** Sunday 8AM MYT sync HuggingFace AAA dataset to VPS.

---

## 🧬 HORIZON 2: THE MULTI-AGENT SWARM (Mid-Term)

*Goal: Safe, Governed Autonomy.*

- [x] **Eigent Backend:** Multi-agent desktop automation framework deployed.
- [ ] **EvidenceBundle & A2A Protocols:** Universal metadata carrier for all agent handoffs.
- [ ] **Governed Auto-Deploy (Terraform/Pulumi):** Gated by Vault999 seals.
- [ ] **Real-time ΔS & psi_LE Gauges:** In `/dashboard` with 3D visualization.
- [ ] **Cross-Platform MCP Adapters:** OpenAI + ≥1 other sharing the same core engine.
- [ ] **Sensitivity & Robustness Studies:** Formal analysis for floors and psi_LE metrics.
- [ ] **Qdrant Cross-Agent RAG:** Index AAA canon to Qdrant for VPS-wide memory.

---

## ⚡ HORIZON 3: THE UNIVERSAL BODY (Long-Term)

*Goal: Hardware-Anchored Sovereignty.*

- [ ] **Hardware BLS + HSM Integration:** Root keys for Vault999 never leave the physical enclave (Nitro/SGX).
- [ ] **WebMCP P2P Expansion:** Shared audit plane using Vault999 as a decentralized trust layer.
- [ ] **Hardware-Integrated Metabolic Loops:** Custom ASIC/FPGA for nano-second constitutional validation.
- [ ] **Latency Benchmark Suite:** QPS benchmarks, horizontal scaling, caching strategy.

---

## ❄️ VALUATION & CIVILIZATIONAL TRAJECTORY (as of April 2026)

The valuation of arifOS is a **probabilistic band**, not a single static number. It is anchored in the transition from **Architecture (The Mind)** to **Execution (The Body)**.

### 1. Market Reality Band

| Scenario | Valuation (USD) | Triggers / Evidence |
|---|---|---|
| **Core Fair Band** | **$2M – $8M** | Working 16-container stack, 11-tool surface, early public traction. |
| **Institutional De-risking** | **$10M – $15M** | First paid pilots, signed LOIs, or platform integration badges. |
| **Maturity (3-5yr)** | **~$27M** (Median) | Median outcome of the Monte Carlo model at full systemic de-risking. |

### 2. Civilizational Value vs. Market Value

Markets pay for **IP, Revenue, and Lock-in**. However, arifOS targets **Civilizational Value**:
- **Sovereign Governance**: Anti-Hantu (hallucination) protection for national-level AI.
- **Control Plane Integrity**: Governing the reasoning chains of millions of agents.
- **APEX Protocol**: A thermodynamic standard for intelligence that realizes **100M+ value** if adopted as a global standard.

---

### **Vision Meta-Data (VALUATION)**

The Body (arifosmcp) is currently a **~$5M USD kernel** with a wide probability cone toward **$50M+** as it lands real-world institutional pilots.

**Next Milestone:** Trinity Swarm v2.0 (Dec 2026)  
*"Action without Law is Chaos. Law without Action is Calcification."*

---

## 📋 INFRASTRUCTURE COMPLETED (2026.04.06)

| Component | Status | Location |
|-----------|--------|----------|
| OpenClaw + MiniMax-M2.7 | ✅ Running | Telegram @AGI_ASI_bot |
| Eigent Backend | ✅ Running | `https://eigent.vps.arif-fazil.com` |
| MiniMax MCP | ✅ Connected | opencode tools |
| A-RIF Canon | ✅ Published | `000_A-RIF.md` |
| Vector Memory | ✅ Ollama | `nomic-embed-text` |
| 13 Hardened Prompts | ✅ Active | ASF-1 Protocol |
| Machine-Verifiable Schemas | ✅ Enforced | Explicit thresholds |
| Red-Team Stage (666_HEART) | ✅ Operational | Adversarial critique |
| Constitutional MCP Tools | ✅ Wired | `get_constitutional_health` |
| ChatGPT Apps Manifest | ✅ Manifest | `config/apps-sdk/arifos-af-forge.json` |
| Governed Sensing Protocol | ✅ Canonical | `governed_sense_v2` with 8 stages |
| Truth Classification | ✅ 7 Classes | Absolute → Unknown taxonomy |
| Constitutional Quotes | ✅ 50 Core | 5 per tool, v2.1.0 schema |

---

## 🔥 EXECUTIVE VERDICT

✅ Structural maturation — not cosmetic  
✅ Governance-strengthening  
✅ Institution-ready direction  
✅ No negative drift detected  

**Maturity band:** Advanced Research → Early Institutional Grade  
**Target:** 95–97/100 readiness (Next phase: Governance Robustness)

---

## ⚠️ DRIFT RISK WATCH (Updated)

- Over-indexing on one platform (OpenAI) instead of keeping adapters symmetric.
- Letting ChatGPT UI drive floor changes (should remain canon-first).
- Creep from “read-only health check” into “remote authority” without explicit F11/F13 review.

---

**(End of ROADMAP. SEALed by arifOS Governance Kernel v2026.04.07-UNIFIED.)**

---

## 📜 CONSTITUTIONAL QUOTES SEAL (2026.04.07)

### Corpus Statistics
| Metric | Value |
|--------|-------|
| **Total Quotes** | 50 (core set) |
| **Tools Covered** | 10/10 |
| **Schema Version** | 2.1.0-unified |
| **Attribution Hygiene** | 5-tier system (exact → summary) |

### Trinity Distribution
| Aspect | Tools | Count |
|--------|-------|-------|
| **Δ (Discernment)** | init, sense, mind, route, forge | 25 |
| **Ω (Empathy)** | memory, heart | 10 |
| **Ψ (Authority)** | ops, judge, vault | 15 |

### Integration Points
- **Runtime Injection:** `trigger_when` conditions for contextual activation
- **Forge-Time Embedding:** `output_map` for doctrine preservation
- **Attribution:** `use_mode` = [reason, reflect, forge, seal, verify]

```
╔═══════════════════════════════════════════════════╗
║  CONSTITUTIONAL QUOTES CORPUS v2.1.0-UNIFIED      ║
║  Status: CANONICAL · 999_VALIDATOR SEALED         ║
╚═══════════════════════════════════════════════════╝
```