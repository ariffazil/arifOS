<!-- SOT-MANIFEST
owner: Arif
last_verified: 2026-06-05
valid_from: 2026-06-05
valid_until: 2026-07-05
confidence: high
scope: /root/geox
epistemic_status: CLAIM
-->

# 🪨 GEOX — Earth Intelligence Engine

> **GEOX is the earth intelligence organ of the arifOS federation.** It connects AI agents to subsurface evidence — well logs, petrophysics, seismic data, and prospect evaluation — and enforces constitutional rules that prevent the AI from overstating confidence, skipping evidence, or making irreversible drilling decisions without human approval. It observes. It computes. It never decides alone.

***

## What GEOX Is

GEOX is the **Earth Evidence Layer** in the arifOS federation. It prepares, computes, and governs subsurface evidence — well logs, petrophysics, stratigraphy, geomechanics, seismic, and prospect risk — and exposes that evidence through a canonical FastMCP surface.

Every output passes through the **F3 WITNESS floor** before reaching the reasoning kernel.

**GEOX computes. MCP exposes. Resources guide. Artifacts remember. Agent reasons. Arif judges.**

> GEOX owns the **FIELD** — the empirical grounding layer for earth sciences.
> GEOX does **not** own constitutional judgment (arifOS) or economic logic (WEALTH).

***

## Architecture — Three Layers

```
┌─────────────────────────────────────────────────────────┐
│  GEOX repo                                              │
│                                                         │
│  src/geox_core/    ← Truth Engine. Computes.           │
│                       Never exposed to agents directly. │
│                                                         │
│  src/geox_mcp/     ← MCP Surface. The only surface    │
│                       AI agents touch. Governed by      │
│                       CANON-9, ToAC, F1–F13.           │
│                                                         │
│  resources/        ← Agent Knowledge Pack.              │
│                       Playbooks, ontology, prompts,      │
│                       toolcards, schemas, examples.      │
└─────────────────────────────────────────────────────────┘
```

### Epistemic Tier Separation

| Tier | Layer | Capability |
|------|-------|-----------|
| 0 | Observed | Raw witness — depth, GR, RT, RHOB, NPHI, DTC |
| 1 | Derived | Deterministic transforms — Vsh, φ, Sw, AI, pore pressure |
| 2 | Interpreted (Local) | Pattern — facies motif, lithology, single-well |
| 3 | Process Hypothesis | Abduction — transgression, forced regression, sequence |
| 4 | Contradiction Scan | Red-team — cross-evidence conflict, 888HOLD trigger |
| 5 | Prospect Risk | ACRisk, ToAC, basin charge, sovereign verdict |

**The LLM is the structured language interface — not the geologist. Arif judges.**

***

## MCP Surface (Live — 2026-06-05)

```
# HTTP mode (systemd, Cloudflare Tunnel):
PYTHONPATH=src python -m geox_mcp.server --host 127.0.0.1 --port 8081

# Stdio mode (local agents — Claude Code, OpenCode, Continue CLI):
PYTHONPATH=src python -m geox_mcp.server --transport stdio

→ 33 canonical tools across 3 domains (witness, paleoscan, claims)
→ Universal output envelope v0.5 (cross_modal_stability, attention_equivalence)
→ Version v2026.05.27
→ Contract epoch: 2026-05-12-GEOX-13TOOLS-v0.7
```

### The 33 canonical tools

The canonical list lives at `src/geox_mcp/server.py` → `CANONICAL_PUBLIC_TOOLS` and is served live by `geox_system_registry_status`. **Always trust the live registry, not this table.**

| Domain | Tools |
|--------|-------|
| **Data intake** | `geox_data_ingest_bundle`, `geox_data_qc_bundle`, `geox_dst_ingest_test` |
| **Inspect / Evidence (pre-ingest)** | `geox_las_inspect`, `geox_seismic_inspect`, `geox_seismic_segy_inspect`, `geox_header_inspect`, `geox_evidence_discover`, `geox_report_to_workflow` |
| **Subsurface (petrophysics + integrity)** | `geox_subsurface_generate_candidates`, `geox_subsurface_verify_integrity` |
| **Seismic physics** | `geox_seismic_compute` (modes: synthetic, well_tie, time_depth_anchor, anomalous_contrast, attribute) — now carries AVO class I-IV + attention residual + softmax hallucination risk per anomaly |
| **Horizon interpretation** | `geox_horizon_contrast_surface` — 6-step ToAC-as-Attention pipeline: background model → multi-attribute contrast → attention-weighted fusion → candidates → governance → audit |
| **Sequence stratigraphy** | `geox_sequence_interpret` (modes: single_well, project, section_correlation) |
| **Evidence reasoning** | `geox_evidence_reason` (phases: synthesize, abduct, contradict, full) |
| **Prospect** | `geox_prospect_evaluate` (modes: screen, appraise, develop) |
| **Map context** | `geox_map_context_scene` |
| **Claim governance** | `geox_claim_create`, `geox_claim_challenge`, `geox_evidence_attach`, `geox_claim_seal` |
| **Registry / system** | `geox_system_registry_status` |

> **F13 honored** — every capability lives in an existing tool's modes/params, not a new tool. Eureka forges (E1 multi-method T-D fitters, E7 cascade demotion) add depth inside `geox_seismic_compute` and `geox_claim_*` without expanding the surface.

### Universal Output Envelope (v0.5)

Every tool returns the same outer contract — now with **cross-modal stability** fields forged 2026-06-05:

```json
{
  "execution_status": "SUCCESS | HOLD | VOID",
  "tool_class": "well_stratigraphy",
  "claim_state": "SEAL | QUALIFY | HOLD | VOID",
  "observed": {},
  "derived": {},
  "interpreted": {},
  "artifact_refs": {},
  "evidence_refs": [],
  "missing_inputs_schema": [],
  "claim_limits": [],
  "next_best_actions": [],
  "audit_receipt": {},
  "human_final_authority": "Arif",
  "cross_modal_stability": 0.95,
  "semantic_density_score": 0.35,
  "dim_spot_flag": false
}
```

> **Cross-Modal Fidelity Theorem (2026-06-05):** Physical and schematic constraint reduces the admissible solution space, improving inter-modal fidelity. `cross_modal_stability` scores how well this output will survive transmission to another modality (image, audio, protocol). `dim_spot_flag` warns when negative constraints (VOID, absence) risk being lost in cross-modal transfer — the hardest failure mode, confirmed in the literature (Kolmogorov, Solomonoff 1964; Semantic Hub, Wu et al. ICLR 2025). See `GENESIS/003_CONSTITUTIONAL_ALIGNMENT.md` and `docs/GEOX_NOBEL_EUREKA_CATALOGUE.md`.

***

## Repository Structure

```
geox/
├── src/
│   ├── geox_core/              # Truth Engine (not agent-facing)
│   │   ├── engines/
│   │   │   ├── petrophysics/  # Archie, Sw ensemble, Vsh, cutoffs
│   │   │   ├── stratigraphy/  # Recursive ToAC, GR motif, parasequence
│   │   │   ├── geomechanics/  # Eaton pore pressure, mechanical strat
│   │   │   ├── seismic/       # Well tie, attribute preparation
│   │   │   ├── map_context/   # Geospatial grounding
│   │   │   └── prospect/      # Basin charge, ACRisk math
│   │   ├── io/                # LAS, SEG-Y, tops, checkshot readers
│   │   ├── governance/         # physics_guard.py, ac_risk.py, judge.py
│   │   ├── artifacts/          # store.py, refs.py, exporter.py
│   │   └── schemas/            # Pydantic models — well, seismic, prospect
│   │
│   └── geox_mcp/              # MCP Surface (agent-facing)
│       ├── server.py           # THE canonical FastMCP entrypoint
│       ├── registry.py         # Single tool registry — one source of truth
│       ├── contracts/          # MCP protocol contracts
│       └── tools/             # 20 canonical tools (one module per domain)
│
├── resources/                  # Agent Knowledge Pack
│   ├── capabilities/
│   │   └── geox_capabilities.json    # THE canonical registry source
│   ├── toolcards/                     # YAML — intent, limits, failure modes
│   ├── playbooks/                     # Workflow guides for agents
│   ├── prompts/                       # Claim discipline, failure policy, etc.
│   ├── ontology/                      # curve_aliases, lithology, depositional env
│   ├── schemas/                      # Exported JSON schemas
│   └── examples/                     # Golden examples (danum1, etc.)
│
├── tests/                       # 693 passing
│   ├── unit/
│   ├── integration/
│   └── golden/                 # Agent behavior anchor tests
├── docs/                        # Architecture, deployment, changelog
├── scripts/                     # generate_live_sot.py, seed_evidence.py
├── deploy/                      # Dockerfiles, systemd, Caddy
├── archive/                     # Legacy (read-only, never runtime)
│   ├── WELL/                   # Archived WELL integration
│   └── arifos/                # Archived legacy domain logic
├── .mcpignore                  # Prevents agent ingestion of archive/vault/raw
└── server.py                   # Legacy entrypoint (points to src/geox_mcp/server.py)
```

***

## Getting Started

```bash
# Install
pip install -e ".[dev]"

# Run canonical MCP server (HTTP — systemd default)
PYTHONPATH=src python -m geox_mcp.server --host 127.0.0.1 --port 8081

# Run as stdio (local agents — Claude Code, OpenCode, Continue CLI)
PYTHONPATH=src python -m geox_mcp.server --transport stdio

# Run tests
PYTHONPATH=src python -m pytest tests/ -q

# Lint
ruff check src/
ruff format src/
mypy src/geox_mcp/server.py
```

### Connect via FastMCP CLI / Agent Config

```bash
# List all 33 tools
fastmcp run src/geox_mcp/server.py --transport stdio

# Call a tool
fastmcp call src/geox_mcp/server.py geox_system_registry_status
```

### Stdio — Claude Code / OpenCode / Continue CLI

GEOX is dual-mode. Use `--transport stdio` for any agent on the same machine:

```json
{
  "mcpServers": {
    "geox": {
      "command": "python3",
      "args": ["-m", "geox_mcp.server", "--transport", "stdio"],
      "cwd": "/root/geox"
    }
  }
}
```

No token needed — F1 stdio bypass for local use. All 33 tools available.

### Remote (VPS)

```bash
# Health check
curl https://geox.arif-fazil.com/health

# MCP endpoint
# wss://geox.arif-fazil.com/mcp
```

***

## The Agent Operating Loop

An AI agent should experience GEOX in this sequence:

```
1. list_resources → read geox://resources/index
2. read relevant playbook (e.g., geox://resources/playbooks/well_sequence_stratigraphy.yaml)
3. call geox_data_ingest_bundle (artifact_ref returned)
4. call geox_data_qc_bundle (claim_state verified)
5. call domain computation tool (well, petro, strat, seismic)
6. call geox_process_abduction (ranked process hypotheses)
7. call geox_evidence_contradiction_scan (red-team the hypotheses)
8. call geox_evidence_summarize_cross (governed narrative)
9. agent writes explanation with claim_limits
10. Arif renders final judgment (F13 sovereign veto)
```

> The agent does **not** search source files. It reads the governed operating manual (`resources/`), then calls governed tools.

***

## Governance Model

All tools enforce the **arifOS F1–F13 constitutional floors**:

| Floor | Principle | GEOX Implementation |
|-------|-----------|---------------------|
| F1 | Reversible | All operations non-destructive; artifact_refs are immutable |
| F2 | ≥99% truth or declare band | `claim_state` with explicit uncertainty band |
| F3 | Human-AI-Evidence align | Tri-witness on every output |
| F5 | Peace ≥ 1.0 | 888HOLD before irreversible subsurface decisions |
| F7 | Humility band 0.03–0.15 | ACRisk declared on every claim |
| F9 | Anti-Hantu | No hallucinated geology — missing inputs trigger HOLD |
| F13 | Sovereign human veto | `human_final_authority: "Arif"` on every envelope |

### 888HOLD Protocol

When ACRisk exceeds threshold or evidence is contradicted:

```python
# Automatic hold — never silently proceeds
if acrisk > 0.60 or contradiction_detected:
    return envelope(
        execution_status="HOLD",
        verdict="888HOLD",
        hold_reason="...",
        human_final_authority="Arif"
    )
```

***

## ACRisk — Theory of Anomalous Contrast

Every claim carries a risk score:

```
ACRisk = U_phys × D_transform × B_cog
```

Where:
- **U_phys** — physical uncertainty of the raw signal
- **D_transform** — distortion introduced by visual/computational transforms
- **B_cog** — cognitive bias from display seduction (VLM/human)

| ACRisk | Verdict | Action |
|--------|---------|--------|
| < 0.25 | SEAL | Auto-proceed |
| 0.25–0.50 | QUALIFY | Proceed with declared caveats |
| 0.50–0.75 | HOLD | Human review required |
| > 0.75 | VOID | Unsafe — do not use |

### Anomalous Contrast Detection (Hardened 2026-06-05)

`geox_seismic_compute(mode="anomalous_contrast")` now returns governed outputs — not raw physics. Each detected anomaly is classified via the **contradiction ontology** (INTERPRETATION_OBSERVATION_MISMATCH), gated through `888_HOLD` when severity is HIGH, and scored for cross-modal stability. The bridge: **AVO fluid factor (Smith & Gidlow 1987) = transformer attention (Vaswani 2017) = constitutional governance deviation.** Same math. Different domain. See `docs/TOAC_CANON.md` and `docs/GEOX_NOBEL_EUREKA_CATALOGUE.md`.

***

## Artifact Reference Protocol

Stable cross-tool evidence transport. No raw file paths.

```
geox://artifact/DATA-LAS-DANUM1-QIDB2025
geox://artifact/PETRO-SW-DANUM1-INT001
geox://artifact/STRAT-TOAC-DANUM1-Z1
```

Artifact refs are immutable, auditable, and federation-portable (arifOS ↔ WEALTH ↔ GEOX).

***


## Roadmap

| Horizon | Status | Description |
|---------|--------|-------------|
| H1 — Clean Surface | ✅ SEALED | One server, one registry, strict `.mcpignore` |
| H2 — `geox_process_abduction` | ✅ SEALED | Earth abduction engine — pattern → process hypothesis |
| H3 — Async Tasks (`task=True`) | 🔧 Next | Long-running batch LAS ingest, basin metabolize (FastMCP 3.0 unblocked) |
| H4 — MCP Resources | ✅ SEALED | playbooks + prompts wired as MCP resources |
| H5 — MCP Elicitation (888HOLD UI) | 🔧 Next | Multi-select elicitation via SEP-1330 — partial unblock in FastMCP 2.14 |
| H6 — Server Card + Registry | ✅ SEALED | `server-card.json` published |
| H7 — MCP Skills | ❌ Blocked | Awaiting MCP Skills WG finalization |
| PINN Layer | ✅ FORGED | Physics-informed neural net for Vsh/φ/Sw — violates Archie → auto-fail (`engines/petrophysics/pinn.py`, 389 lines) |
| AC Risk Hardening | ✅ FORGED | Governed anomalous contrast detection — AVO class I-IV, attention residual, Essay #13 softmax hallucination risk (`seismic_compute.py`, `anomalous_contrast.py`) |
| Cross-Modal Fidelity | ✅ FORGED | `cross_modal_stability`, `semantic_density_score`, `dim_spot_flag` on every envelope — 7 files hardened (2026-06-05) |
| ToAC-Attention Pipeline | ✅ FORGED | `geox_horizon_contrast_surface` — 6-step multi-attribute contrast fusion pipeline with ABKSS stratigraphic query templates (2026-06-05) |
| Essay #13 Lock-In | ✅ FORGED | Mathematical derivation encoded: softmax hallucination risk, approximation tier, boundary condition flags, trilogy reference — every anomaly output carries the proof |
| Stdio Transport | ✅ FORGED | Dual-mode MCP: `--transport stdio` for local agents, `--transport http` for systemd (2026-06-05) |
| DRP Synthetic Core | 🔧 Future | GAN super-resolution for micro-CT training data |
| WLFM Backbone | 🔧 Future | Well-log foundation model — cross-well invariant geological token embeddings |

***

## Test Suite

```
264 passed, 1 skipped, 0 failures
*Includes: anomalous contrast (15/15), horizon contrast pipeline (8/8), seismic compute, 
envelope integrity, contradiction ontology, AVO-attention equivalence, 
Essay #13 softmax hallucination risk, Nobel-grade locks (33/33).
Golden tests anchor agent behavior — tool output shape, claim_state correctness, 
failure mode coverage, no secret/path leaks.*

***

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTHONPATH` | `src` | Required — must include `src/` for imports |
| `GEOX_HOST` | `127.0.0.1` | HTTP bind host (systemd) |
| `GEOX_PORT` | `8081` | HTTP bind port (geox-mcp.service) |
| `--transport` | `http` | Transport mode: `http` (uvicorn) or `stdio` (local agents) |
| `GEOX_LOG_LEVEL` | `INFO` | Logging level |
| `GEOX_SECRET_TOKEN` | `stdio-bypass` | Fail-closed auth for HTTP transport (auto-bypassed on stdio) |

***


---

## TREE777 Wiki

Full federation knowledge base — architecture decisions, earth-intelligence theory, agent documentation:
→ **https://wiki.arif-fazil.com**

## 🏛️ Federation

| Organ | Repository | Role | Port |
|-------|-----------|------|------|
| **arifOS** | [ariffazil/arifOS](https://github.com/ariffazil/arifOS) | Constitutional Kernel · F1-F13 | 8088 |
| **AAA** | [ariffazil/AAA](https://github.com/ariffazil/AAA) | Reality Console · A2A Gateway | 3001 |
| **A-FORGE** | [ariffazil/A-FORGE](https://github.com/ariffazil/A-FORGE) | Execution Shell | 7071 |
| **GEOX** | [ariffazil/geox](https://github.com/ariffazil/geox) | Earth Intelligence | 8081 |
| **WEALTH** | [ariffazil/wealth](https://github.com/ariffazil/wealth) | Capital Intelligence | 18082 |
| **WELL** | [ariffazil/well](https://github.com/ariffazil/well) | Human Readiness | 18083 |
| **arif-sites** | [ariffazil/arif-sites](https://github.com/ariffazil/arif-sites) | Public Surfaces | 443 |

> **Constitutional authority:** F1-F13 floors, 888_JUDGE, and VAULT999 live in `ariffazil/arifOS`.  
> **Live federation status:** See `ariffazil/arifOS/FEDERATION_STATUS.md`.
## 📄 Contributing

This repository operates under the arifOS Federation constitution (F1–F13).  
See [AGENTS.md](AGENTS.md) for the canonical boot sequence and agent operating rules.

## 📜 License

AGPL-3.0. See [LICENSE](LICENSE).

---

**DITEMPA BUKAN DIBERI** — Forged, Not Given.



> **Evidence Contract.** This organ emits the standard envelope (epistemic_tag, evidence_quality, source_attribution, uncertainty_band, delta_S) per [arifOS 000_CONSTITUTION.md](../../arifOS/static/arifos/theory/000/000_CONSTITUTION.md) Appendix B. arifOS reads the envelope and applies L01–L13. This organ does not self-judge.


## Changelog

- **v2026.06.06-LAW-SEAL** (2026-06-06): Constitution unified. arifOS canonical 000_CONSTITUTION.md. 13 Laws (L01-L13) live in arifOS only. Evidence Contract line added. AGENTS.md updated.
