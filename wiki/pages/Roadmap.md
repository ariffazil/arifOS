---
type: Source
tags: [roadmap, engineering, strategy, valuation, horizons]
sources: [ROADMAP.md]
last_sync: 2026-04-08
confidence: 1.0
---

# arifOS Roadmap

> **Source:** `wiki/raw/ROADMAP.md` | Version: `2026.04.07-SOT-SEALED`
> **Authority:** Muhammad Arif bin Fazil (999_VALIDATOR)
> **Motto:** *Execution is the proof of Law.*

---

## Platform Agnosticism Strategy — 4 Paths (EMV/NPV Ranked)

arifOS is LLM-agnostic and platform-agnostic by design. Four execution paths ordered by Expected Monetary Value × Net Present Value:

| Path | Name | Effort | NPV (12–24mo) | Risk | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | Tool `platform=` Mode Parameter | 1–2 wks | ~$35k | Low | Foundation shipped, dispatch pending |
| **D** | ChatGPT Widget Phase 1 | 1–2 wks | ~$40k | Low–Med | Blocked on DNS + TLS (human action) |
| **B** | MCP Profile Gateway | 4–6 wks | ~$180k | Medium | H2 2026 |
| **C** | REST Constitutional API | 8–12 wks | ~$600k | High | 2027 |

**Total NPV trajectory over 24 months:** ~$855k (conservative). Enterprise CaaS licensing would 3–5× the long-term figure.

### Recommended Execution Order

```text
NOW (0–2 weeks):    D + A  →  Fix ChatGPT deployment + add platform= mode
MID (1–4 months):   B      →  MCP Profile Gateway
LONG (4–12 months): C      →  REST Constitutional API

```

---

## Drift Audit Summary (Apr 1 → Apr 6, 2026)

| Dimension | Apr 1 | Apr 6 | Δ |
| :--- | :--- | :--- | :--- |
| Constitutional Coverage | 80 | 96 | +16 |
| Injection Resistance | 70 | 92 | — |
| Determinism | 75 | 90 | — |
| Machine Verifiability | 60 | 90 | +30 |
| Documentation Coherence | 85 | 93 | +8 |
| Runtime Governance Integrity | 82 | 94 | +12 |
| Theory of Mind Integration | 0 | 95 | **+95** |
| **Overall Readiness** | **85** | **96** | **+11** |

**Band:** Early Institutional Grade → Governance Robustness + Cognitive Alignment.

---

## Horizons

### Horizon 1 — The Execution Engine *(Current)*

Goal: Solidify the 11 Mega-Tool Surface for Institutional Adoption.

Key completions (as of 2026.04.07):

- Unified MCP surface — dual transport (stdio/http/streamable-http)
- Constitutional Health Tooling — `get_constitutional_health`, `render_vault_seal`, `list_recent_verdicts`
- ChatGPT Apps Integration — Apps SDK manifest bound to `/mcp`
- Vault999 Blueprint — BLS+hash+Merkle log model
- Validator CLI + Telemetry — tri-witness/ΔS/Ω₀ telemetry surfaced
- Three-Layer Identity Binding — F11 hardened (model declares → system verifies → session binds)
- Vector Memory — Ollama `nomic-embed-text` for semantic search
- Weekly HF Sync Cron — Sunday 8AM MYT AAA dataset sync

### Horizon 2 — The Multi-Agent Swarm *(Mid-Term, H2 2026)*

Goal: Safe, Governed Autonomy.

- [x] Eigent Backend — multi-agent desktop automation deployed
- [ ] EvidenceBundle & A2A Protocols
- [ ] Governed Auto-Deploy (Terraform/Pulumi) gated by Vault999
- [ ] Real-time ΔS & psi_LE Gauges in `/dashboard`
- [ ] Cross-Platform MCP Adapters (OpenAI + ≥1 other)
- [ ] Qdrant Cross-Agent RAG

### Horizon 3 — The Universal Body *(Long-Term)*

Goal: Hardware-Anchored Sovereignty.

- [ ] Hardware BLS + HSM Integration (keys never leave physical enclave)
- [ ] WebMCP P2P Expansion (decentralized Vault999 trust layer)
- [ ] Hardware-Integrated Metabolic Loops (custom ASIC/FPGA)
- [ ] Latency Benchmark Suite

---

## Valuation Band (as of April 2026)

| Scenario | Valuation (USD) | Triggers |
| :--- | :--- | :--- |
| Core Fair Band | $2M – $8M | Working 16-container stack, early traction |
| Institutional De-risking | $10M – $15M | First paid pilots, signed LOIs |
| Maturity (3–5yr) | ~$27M (Median) | Monte Carlo median at full systemic de-risk |

**Civilizational Value** target: APEX Protocol adopted as global standard → $100M+ addressable.

**Next Milestone:** Trinity Swarm v2.0 (Dec 2026)

---

## Drift Risk Watch

- Over-indexing on OpenAI instead of keeping adapters symmetric.
- Letting ChatGPT UI drive floor changes (should remain canon-first).
- "Read-only health check" creeping into "remote authority" without F11/F13 review.

---

## Open Questions

- When will DNS/TLS be resolved for `mcp.af-forge.io`? (Path D blocker)
- What triggers the B→C transition decision?
- How is `platform=` dispatch implemented at the tool level (Path A remaining work)?

---

> [!NOTE]
> This page is a synthesis of `wiki/raw/ROADMAP.md`. For full EMV tables, infrastructure status, and constitutional quotes corpus, see the raw source.

**Related:** [[Changelog]] | [[What-is-arifOS]]
