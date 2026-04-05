# arifOS TODO — THE BODY (Execution & Engineering)

**Version:** 2026.04.03-SEALED  
**Authority:** Muhammad Arif bin Fazil (999_VALIDATOR)  
**Motto:** *Body starts where Stochastic ends.*

---

## 🏗️ TIER 1: THE EXECUTION SURFACE (Immediate)

*Goal: Solidify the 11 Mega-Tools and the 42 Modes for Institutional Grade.*

- [x] **AAA MCP Induction:** Unified arifOS repository, collapsed `AAA/` shadow workspace.
- [x] **Substrate Controller:** Implemented auto-risk detection and `888_HOLD` in `tools_hardened_dispatch.py`.
- [x] **000/ Kernel Induction:** Established the 13 Constitutional Floors as the root governing substrate.
- [x] **Agent Skills Resource:** Implement `arifos://agents/skills` URI.
- [x] **Unified DEPLOY:** Consolidated VPS deployment into a single, directive-style `DEPLOY.md`.
- [x] **A-RIF Framework:** Created `000_A-RIF.md` — Retrieval Augmented Generation with constitutional floors.
- [x] **Eigent Deployment:** Multi-agent desktop automation on VPS.
- [x] **MiniMax MCP:** `web_search` + `understand_image` tools in opencode.
- [x] **Vector Memory:** Ollama `nomic-embed-text` for semantic search.
- [x] **Weekly HF Sync:** Cron job for HuggingFace AAA dataset sync (Sunday 8AM MYT).
- [x] **13 Hardened Prompts (000–999):** Constitutional Guard embedded in each.
- [x] **ASF-1 Dual-Layer Protocol:** JSON for agents, narrative for humans.
- [x] **Machine-Verifiable Schema Enforcement:** Explicit thresholds, formal verdict mapping.
- [x] **Red-Team Stage (666_HEART):** Adversarial critique integrated.
- [x] **Great Unification:** Repo restructuring, documentation hierarchy, and package consolidation (2026.04.06).
- [ ] **Mode Stability:** Audit all 42 modes in `tools_internal.py` for input schema parity with `contracts.py`.
- [ ] **API Rotation:** Revoke legacy OpenCode keys and inject fresh secrets into the VPS runtime.
- [ ] **Lint Fix (Ruff):** Resolve pre-existing lint failures in the root `arifosmcp/` kernel.
- [ ] **Red-Team Proven Injection Resistance:** Automated adversarial fuzz testing suite with benchmark corpus.

---

## 🧬 TIER 2: MULTI-AGENT ORCHESTRATION (Mid-Term)

*Goal: Move from "Single Agent" to "Trinity Swarm (ΔΩΨ)."*

- [x] **Eigent Backend:** VPS-side agent orchestration framework deployed.
- [ ] **A2A Evidence Passing:** Implement `EvidenceBundle` as the native inter-agent lingua franca.
- [ ] **Role-Bound Tool Access:** Refine `auth_context` to restrict specific tools based on the Architect/Engineer/Auditor role.
- [ ] **Unified Dashboard:** Finalize the `/dashboard` UI for real-time Ω₀ (Uncertainty) and ΔS (Entropy) gauges.
- [ ] **Qdrant AAA Indexing:** Index HuggingFace AAA canon to Qdrant for cross-agent constitutional RAG.
- [ ] **Docker 2.0 (Swarm Mode):** Transition the 16-container stack to a Docker Swarm/Kubernetes sidecar pattern for enterprise high-availability.
- [ ] **psi_LE Formalization:** Document intelligence elevation metric computation formally with reproducibility proof.
- [ ] **Floor Weight Sensitivity Analysis:** Monte Carlo test for weight perturbation, stress-case simulation.

---

## ⚡ TIER 3: HARDWARE-LEVEL INTEGRATION (Long-Term)

*Goal: Establish the Physical Root of Trust.*

- [ ] **Hardware Enclave (HSM):** Implement `F11` (Identity) grounding to a physical Nitro or SGX hardware enclave.
- [ ] **Global MCP Connectivity:** Secure WebMCP 3.0 protocol bridge for P2P agent-to-agent collaboration without centralized brokers.
- [ ] **Metabolic Auto-Scaling:** Automatically scale VPS resources based on the Genius Index (G) and token-thermodynamics.
- [ ] **Latency Benchmark Suite:** QPS benchmarks, horizontal scaling notes, caching strategy, parallelization model.

---

## 📋 COMPLETED (2026.04.03 SEAL)

| Item | Status | Notes |
|------|--------|-------|
| OpenClaw + MiniMax-M2.7 | ✅ | Telegram @AGI_ASI_bot |
| OpenClaw memory → Ollama | ✅ | `nomic-embed-text` |
| Eigent deployment | ✅ | `https://eigent.vps.arif-fazil.com` |
| MiniMax MCP | ✅ | web_search + understand_image |
| A-RIF canon | ✅ | `000_A-RIF.md` published |
| Weekly HF sync cron | ✅ | Sunday 8AM MYT |
| Session cleanup | ✅ | 110 → 24 files |
| Config permissions | ✅ | 600 (was 644) |
| GitHub push | ✅ | A-RIF committed |
| 13 Hardened Prompts | ✅ | ASF-1 Protocol |
| Machine-Verifiable Schemas | ✅ | Explicit thresholds |
| Red-Team Stage (666_HEART) | ✅ | Adversarial critique |

---

## 🔮 NEXT ACTIONS (Priority Order)

1. **Red-Team Injection Suite** — Automated fuzz testing to prove 92% injection resistance claim
2. **psi_LE Formalization** — Document intelligence elevation metric with formal formula
3. **Floor Weight Sensitivity** — Monte Carlo test for weight perturbation
4. **Qdrant AAA Indexing** — Index 19 AAA canon files for cross-agent RAG
5. **Mode Audit** — Verify 42 tool modes for schema parity
6. **Latency Benchmark Suite** — QPS benchmarks, caching strategy
7. **Eigent Windows Client** — Connect Eigent desktop app to VPS backend
8. **API Key Rotation** — Fresh secrets for production

---

## 🌍 GEOX SPECIFIC (From Deep Research — April 2026)

### Forge 1 (CRITICAL — Do First)
- [ ] Verify `pip install -e .` works clean in GEOX
- [ ] Add GitHub Actions CI: `ruff`, `mypy`, `pytest`
- [ ] Update `smithery.yaml` with full tool list (follow `usgs-quakes-mcp`)
- [ ] Test Claude Desktop stdio integration

### Forge 2 (HIGH — Visualization Gap)
- [ ] **INTEGRATE CIGVIS** — Add to dependencies, implement `SeismicVisualizationTool`
- [ ] Add MCP tools: `geox_render_inline`, `geox_render_timeslice`, `geox_render_3d`
- [ ] Implement real `MacrostratTool` with API v2
- [ ] Add SEG-Y reader (segypy/segyio)

### Forge 3 (MEDIUM — ML Pipeline)
- [ ] Implement `SeismicMLTool` (fault detection, salt ID, facies)
- [ ] Design multi-task heads: DHR + RGT + Fault
- [ ] Avoid OpenVINO (deprecated) — use ONNX/TensorRT

### Forge 4 (MEDIUM — Memory)
- [ ] Implement `DualMemoryStore` (Discrete + Continuous)
- [ ] Add LEM bridge with pluggable backends (TerraFM/Prithvi)
- [ ] Production-harden Qdrant integration

### Integration Matrix Summary
| Repo | Decision | Use |
|------|----------|-----|
| `cigvis` | **ADOPT** | Visualization (HIGHEST PRIORITY) |
| `usgs-quakes-mcp` | **ADOPT** | MCP packaging |
| `withseismic-mcp` | **ADOPT** | Server architecture |
| `earthdata-mcp-server` | **BORROW** | Data discovery patterns |
| `microsoft/seismic-deeplearning` | **BORROW** | ML pipelines |
| `lanl/mtl` | **BORROW** | Task taxonomy |
| `intel/openseismic` | **IGNORE** | Deprecated |

---

## ⚠️ WHAT TO DROP (Reduce/Eliminate)

- ❌ Repeated sovereignty rhetoric in technical sections
- ❌ Overuse of symbolic language in README (reduce by ~15%)
- ❌ Redundant floor explanations
- ❌ The phrase "Sovereign" in engineering core (keep in branding only)

---

## ✅ WHAT TO MAINTAIN (Competitive Moat)

- ✅ Hard floors F1, F2, F9, F10, F13
- ✅ Dual-layer ASF-1 separation
- ✅ Machine-verifiable schema enforcement
- ✅ Immutable vault logging
- ✅ Explicit uncertainty band (Ω0)
- ✅ Red-team stage (666_HEART)
- ✅ Formal verdict mapping

---

**Last SEALed:** 2026.04.03-ARIF  
**Status:** INSTITUTIONAL GRADE · GOVERNANCE HARDENED  
*"Ditempa bukan diberi"* 🔥
