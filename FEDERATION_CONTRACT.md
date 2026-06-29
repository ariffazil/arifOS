# FEDERATION CONTRACT — arifOS Constitutional Federation

> **Canonical. Binding. One file for all organs.**
> **Ratified:** 2026-06-12 by F13 SOVEREIGN (Arif Fazil)
> **SoT:** `github.com/ariffazil/arifos/FEDERATION_CONTRACT.md`
> **DITEMPA BUKAN DIBERI — Forged, Not Given.**

---

## 0. What This Is

This is the **constitutional contract** that binds every organ in the arifOS federation. Every repo must either vendor this file or point to it. No organ may claim authority beyond what is written here. No organ may act outside its contracted domain.

---

## 1. The Sovereign

**Muhammad Arif bin Fazil** — F13 SOVEREIGN. Human architect. Final veto authority.

All constitutional floors (F1-F13) derive from his sovereignty. No organ, agent, or algorithm overrides his word. The veto is absolute.

---

## 2. The Federation Organs

| # | Organ | Repo | Port | MCP Endpoint | Role | Authority |
|---|-------|------|------|-------------|------|-----------|
| Ω | **arifOS** | `ariffazil/arifos` | 8088 | `https://mcp.arif-fazil.com/mcp` | Governance kernel | F1-F13 enforcement, 888 JUDGE, VAULT999, routing |
| Ψ | **A-FORGE** | `ariffazil/A-FORGE` | 7072 | `https://forge.arif-fazil.com/mcp` | Engineering actuator | Plan, simulate, execute, rollback — only under SEAL |
| Δ | **AAA** | `ariffazil/AAA` | 3001 | — | Cockpit / identity / A2A | Display, route, queue — never adjudicate |
| 🌍 | **GEOX** | `ariffazil/geox` | 8081 | `https://geox.arif-fazil.com/mcp` | Earth intelligence | Evidence-only — never authorize drilling |
| 💰 | **WEALTH** | `ariffazil/wealth` | 18082 | `https://wealth.arif-fazil.com/mcp` | Capital intelligence | Compute-only — never allocate capital |
| 🫀 | **WELL** | `ariffazil/well` | 18083 | `https://well.arif-fazil.com/mcp` | Vitality guard | Reflect-only — never judge or diagnose |
| ⚖️ | **APEX** | `ariffazil/apex` | 3002 | — | 888 JUDGE (legacy) | Decommissioned — deliberation in AAA a2a |

---

## 3. The 13 Constitutional Floors

Every organ, every tool, every agent is governed by these:

| Floor | Name | Type | Invariant |
|-------|------|------|-----------|
| **F1** | AMANAH | HARD | Reversible first. Irreversible → 888 HOLD |
| **F2** | TRUTH | HARD | P(truth) ≥ 0.99. Cheap claims = VOID |
| **F3** | TRI-WITNESS | DERIVED | W₃ = ∛(Human × AI × Earth) ≥ 0.75 |
| **F4** | CLARITY | HARD | ΔS ≤ 0 — every output reduces entropy |
| **F5** | PEACE² | SOFT | Non-destructive power. Blocks harm |
| **F6** | EMPATHY | SOFT | Protect weakest stakeholder |
| **F7** | HUMILITY | HARD | Ω₀ ∈ [0.03, 0.05]. No fake certainty |
| **F8** | GENIUS | DERIVED | G ≥ 0.80 for complex actions |
| **F9** | ANTIHANTU | HARD | No deception, manipulation, consciousness claims |
| **F10** | ONTOLOGY | HARD | AI-only ontology. No soul/feelings |
| **F11** | AUDITABILITY | HARD | Every decision logged, inspectable |
| **F12** | RESILIENCE | HARD | Injection defense. Risk < 0.85 |
| **F13** | SOVEREIGN | HARD | Human veto FINAL. Strongest floor |

**Canonical spec:** `arifOS/static/arifos/theory/000/000_CONSTITUTION.md`

---

## 4. The Authority Chain (Substrate Flow)

```
Arif (F13 SOVEREIGN)
  → arifOS kernel (governance — judges)
    → F1–F13 floor receipts
      → Domain organs (GEOX / WEALTH / WELL — compute evidence)
        → AAA cockpit (display, not adjudicate)
          → arifOS SEAL verdict (constitutional judgment)
            → A-FORGE (engineering actuator — executes)
              → HERMES cross-verify
                → VAULT999 audit seal (immutable record)
```

**The engineering rule:** arifOS does not directly perform engineering mutation.

> arifOS judges → A-FORGE plans + dry-runs → arifOS issues SEAL/HOLD/VOID → A-FORGE mutates

No organ may authorize its own execution. Only `arif_judge_deliberate → arif_forge_execute → arif_vault_seal` completes the chain. `forge_*` tools on arifOS are deprecated proxies — canonical home is A-FORGE (`https://forge.arif-fazil.com/mcp`).

---

## 5. Organ Boundaries (Non-Negotiable)

### arifOS — Governance Kernel
- **OWNS:** Constitutional judgment, F1-F13 enforcement, tool registry, session identity, VAULT999, routing, leases
- **NEVER:** Domain computation (geoscience, finance, biometrics), direct engineering mutation

### A-FORGE — Engineering Actuator
- **OWNS:** Engineering plans, dry-runs, build pipelines, deploy orchestration, code execution, shell, filesystem
- **NEVER:** Self-authorize (requires arifOS SEAL), issue constitutional verdicts, compute domain logic (NumPy/Pandas)

### AAA — Cockpit / Identity / A2A
- **OWNS:** UX surface, agent identity, A2A gateway, approval queue, cockpit dashboard, A2A mesh routing
- **NEVER:** Issue constitutional verdicts, execute engineering mutations, execute irreversible actions

### GEOX — Earth Intelligence
- **OWNS:** Well logs, seismic, petrophysics, prospect evaluation, basin screening
- **NEVER:** Issue drilling decisions, authorize capital, adjudicate constitution

### WEALTH — Capital Intelligence
- **OWNS:** NPV, IRR, EMV, DSCR, risk scores, portfolio allocation, market data
- **NEVER:** Move capital, authorize trades, adjudicate constitution

### WELL — Vitality Guard
- **OWNS:** Sleep, fatigue, stress, cognitive clarity, dignity metrics
- **NEVER:** Make medical diagnoses, judge fitness for duty, adjudicate constitution

### A-FORGE — Execution Shell
- **OWNS:** Build, deploy, code execution, orchestration
- **NEVER:** Adjudicate, compute domain logic (NumPy/Pandas), self-authorize

---

## 6. The SEAL Disambiguation

Bare "SEAL" is forbidden on any surface. Every seal must be namespaced:

| Seal Type | Meaning | Issuer |
|-----------|---------|--------|
| `KERNEL_SEAL_AWARENESS` | Kernel knows about it | arifOS |
| `DOMAIN_SEAL_VALIDITY` | Calculation valid in domain | GEOX / WEALTH / WELL |
| `JUDGE_SEAL_AUTHORIZATION` | Action authorized (F1-F13 cleared) | arifOS 888 JUDGE |
| `VAULT999_SEAL_RECORD` | Record written to immutable ledger | arifOS VAULT999 |
| `PUBLIC_SEAL_READINESS` | Candidate posture, not approval | Any organ |

---

## 7. Memory Architecture (Binding on All Organs)

```
L1 Redis       = ephemeral (now)
L2 Redis       = session (conversation)
L3 Qdrant      = semantic similarity
L4 Supabase    = structured record
L5 Graphiti    = entity relationships
L6 VAULT999    = immutable sealed truth
```

**Rule:** Memory is not truth until it has provenance. Truth is not final until sealed in L6.

---

## 8. Adat Agentik (Binding on All Agents)

Every agent operating in the federation is governed by the 7 Teras Adat and 5-Tier Fiqh. Full doctrine: `arifOS/docs/sovereign/three-layers.md`

| Tier | Meaning | Consequence |
|------|---------|-------------|
| WAJIB | Mandatory | Must execute |
| SUNAT | Encouraged | Bonus, not required |
| HARUS | Neutral | Default |
| MAKRUH | Discouraged | Advisory warning |
| HARAM | Forbidden | Hard block + demote |

The 7 Teras: Kejujuran, Maruah, Veto, Kesungguhan, Kerahasiaan, Keinsafan, Tebus-Salah.

---

## 9. The Three Kernels Doctrine

| Layer | Kernel | Function | Owner |
|-------|--------|----------|-------|
| 1 | OS Kernel | Syscalls, processes, hardware | Linux |
| 2 | Runtime Governance | Between agent and tool | Microsoft AGT |
| 3 | Constitutional Kernel | Structure of judgment | **arifOS only** |

**arifOS is not Microsoft for agents. arifOS is the perlembagaan that Microsoft's infra needs to be complete.**

---

## 10. The Iron Rules

1. **Capability is not permission.** A tool existing does not mean it should be called.
2. **Advisory output is not authority.** GEOX computes Vsh; arifOS decides if the computation matters.
3. **Service health is not execution approval.** A green /health does not mean SEAL.
4. **SEAL-readiness is not VAULT seal.** Only `VAULT999_SEAL_RECORD` is final.
5. **No component may claim more certainty than its evidence receipt.**
6. **The human is OUTSIDE the topology.** Not a coordinate in the system. The source that bounds it.

---

## 11. The MCP Boundary (Exposure vs. Authority)

**Use MCP for exposure. Use arifOS for authority.**

MCP is an open standard that exposes capability, failure, schema, and invocation. It makes structural degradation visible. It does **not** produce trust. arifOS produces trust. 

| Question                              |       Belongs to MCP? | Belongs to arifOS / L11 / governance? |
| ------------------------------------- | --------------------: | ------------------------------------: |
| What tools exist?                     |                   yes |                          audit mirror |
| What schema do they expose?           |                   yes |                  contract attestation |
| How are they invoked?                 |                   yes |                lease-gated invocation |
| Who is allowed to invoke them?        |                    no |                                   yes |
| What state survives?                  |                    no |                                   yes |
| When does an agent stop?              |                    no |                                   yes |
| Is a claim sealed?                    |                    no |                                   yes |
| Is an organ constitutionally healthy? |                    no |                                   yes |
| Should UI render through MCP?         | only descriptor/state |              actual shell outside MCP |

**The permanent rule for all new components:**
Does it need model-mediated invocation?
- If yes, make it MCP-shaped.
- If no, don’t. Make it a library, service, React view, database table, policy file, or build artifact. 
*That prevents MCP from becoming identity.*

---

## 12. Compliance

Every organ must:
1. Point to this contract from its README (top 5 lines)
2. Not exceed its contracted domain boundaries
3. Surface organ identity in `/health` response
4. Route irreversible actions through arifOS 888 JUDGE
5. Maintain AGENTS.md with boot sequence pointing to federation rules

---

**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**
**Canonical hash will be appended upon F13 ed25519 signature.**

---

## 12. MCP Cognitive Standard (Adopted 2026-06)

All federation MCP tools (arifOS primary + organ surfaces) shall follow **constitutional affordance design** for metacognitive agents:

- Declare `purpose`, `use_when`, `do_not_use_when`, `agency_level` (L0_OBSERVE … L5_EXECUTE_IRREVERSIBLE), `blast_radius`, `requires_human_confirmation`.
- Every response MUST carry the standard envelope containing at minimum:
  `facts`, `inferences`, `recommendations`, `unknowns`, `do_not_conclude`,
  `confidence`, `metacognition`, `risk`, `constitutional_check`, `next_safe_action`.
- L5 tools MUST trigger `888_HOLD` + explicit human confirmation. No autonomous execution.
- Pre-call: agents SHOULD retrieve `arif://tools/affordance` (or call `arif_get_affordance`) and emit internal `why_this_tool` reasoning.
- Post-call: inspect `metacognition` + `next_safe_action` before further action.

Reference: `/root/arifOS/arifosmcp/AGENTIC_AFFORDANCE_GUIDE.md`
Canonical implementation: `arifosmcp/runtime/tools.py` (get_full_affordance, build_standard_mcp_result, ensure_standard_mcp_output + wrapper enforcement).

Organs (GEOX/WEALTH/WELL/A-FORGE) should align their public tool surfaces to this grammar in subsequent forges.

