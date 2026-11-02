# External Footprint Register

Status: OBSERVED & CLASSIFIED
Last Audit: 2026-10-22
Authority: Public Web Audit & Direct External Probes
Maintainer: arifOS Federation

---

## Purpose

This register tracks independently observable public references to arifOS outside first-party domains.

Discoverability is not validation.  
Listing ≠ Endorsement.  
Mention ≠ Adoption.  
Indexing ≠ Verification.

---

## Witness Classification State Lattice

A system that can only store "proof" inevitably degenerates into propaganda. 
A system that rigorously stores both "proof" and "disproof" remains a scientific audit engine.

- **Verified:** Directly observed, active, and reproducible.
- **Observed:** Mentioned externally by third parties, but awaiting continuous audit reconciliation.
- **Unknown:** Reported in secondary logs or feeds, but unconfirmed by direct probe.
- **Rejected:** Previously reported, asserted, or assumed, but falsified upon direct inspection (inaccurate, dead link, or unverified assertion).

---

## 1. Verified Surfaces (Direct Observation)

Confirmed active via live external probes:
- **GitHub Public Repository:** `github.com/ariffazil/arifOS` (AGPL-3.0 codebase, commit audit trail)
- **PyPI Packages:** `pypi.org/project/arifos/` and `pypi.org/project/arifosmcp/`
- **MCP Client Directory:** `model-context-protocol.com`
- **Loomal MCP Marketplace:** Profile and metadata ingested
- **Skills Playground MCP Directory:** Client configs (Claude, Cursor, VS Code)
- **Glama.ai MCP Registry:** Profile and schema index

---

## 2. Candidate Independent References (Observed Claims)

Reported by external sources; tracked as candidate witness objects:
- **Agentrust:** *Awesome AI Governance* (Curated production AI governance frameworks)
- **Tom Rochette:** *AI Control Planes Research* (Technical evaluation on separation of powers and self-audit culture)
- **Hapax Systems:** *Constitution Research* (Comparative benchmark on runtime axiom enforcement)
- **G2 AI Marketplace:** Indexed under *Responsible AI* & *AI Transparency*
- **Willow Control Plane:** Enterprise MCP connector definition
- **LobeHub Plugins Directory:** Agent skills and induction guides

---

## 3. Disproof & Rejection Log (Anti-Cult Invariant)

Re-probed 2026-11-01 against live sources. Two entries below were WRONG when first
written and are corrected here rather than deleted — a rejection log that cannot
record its own errors is a press release.

- **MCP Registry (`io.github.ariffazil/arifos`):** live query of the official
  community registry (registry.modelcontextprotocol.io, 2026-11-01) returned status
  **active**, published 2026-10-16T08:08:29Z, version `1!2026.10.11`, remote
  `https://mcp.arif-fazil.com/mcp`. The earlier entry here ("no active indexing —
  REJECTED") was a failed search, not an absence. Corrected to **VERIFIED ACTIVE**.
- **Legacy registry entry (`io.github.ariffazil/aaa-mcp`):** ALSO active in the same
  registry at version `60.0.0`, with a PyPI 60.0.0 package reference and an OCI tag
  `docker.io/ariffazil/arifos:60.0.0` -> `aaamcp.arif-fazil.com/sse`. Two entries now
  exist for one server. The newer `arifos` entry is canonical; `aaa-mcp` is
  **STALE, NOT RETIRED**. State: **DRIFT, OWNED - withdraw or update**.
- **Smithery.ai Directory:** NOT LOCATED in a query of 100 registry results for
  "arifos" on 2026-11-01 (`registry.smithery.ai/servers?q=arifos`, 2 pages). A dated
  negative observation, not proof of permanent absence - Smithery closed its MCP
  proxy on 2026-10-31, so the surface itself is in motion. State: **NOT LOCATED (dated)**.
- **Independent CI Automated Verifier:** No external verifier is bound to the CI
  verification loop. State: **REJECTED / OPEN GAP 4**.
- **Academic Peer-Reviewed Paper:** No published journal article or active DOI
  exists. State: **REJECTED / NOT FOUND**.

### 3b. Re-probe corrections, 2026-11-01 (measured, not asserted)

| Claim previously stated here | Measured 2026-11-01 | Verdict |
|---|---|---|
| PyPI `arifosmcp` is a redirect to `arifos` | `pypi.org/pypi/arifosmcp/json` -> name `arifosmcp`, version `1!2026.10.15` | **separate project, no redirect** |
| Hapax reference cannot be located | `hapax-systems/hapax-constitution` public; `research/comparable-projects.md:108` and `research/axiom-governance-evaluation.md:115` both assess arifOS | **exists; citation is critical, not promotional** |
| AgenTrust listing pending | `api.github.com/repos/agentrust-io/awesome-ai-governance/pulls/148` -> merged, "Add arifOS and A-FORGE to Governance Frameworks", opened 2026-10-14 by `ariffazil` | **merged; self-submitted = W2 index, not endorsement** |
| "12 forks" | `api.github.com/repos/ariffazil/arifOS` -> `forks_count: 9`, `stargazers_count: 54` | **drifted; 9** |
| "~750 monthly PyPI downloads" (unverified) | `pypistats.org/api/packages/arifos/recent` -> `last_month: 758`, `last_week: 137`, `last_day: 18` | **confirmed, dated; downloads are not users** |
| Tom Rochette = independent review | page meta: `agent-curated`, `fully-ai-generated`, `llm=glm-5.3-flash` | **AI-authored external interpretation (W3)** |

Hapax on arifOS, quoted in full because only the flattering half would be marketing:
"more ambitious in scope (13 floors vs 4 axioms, claims mathematical provability) but
much less mature in implementation ... The approaches share the 'constitutional'
metaphor but diverge sharply in engineering rigor."

---

## 4. Current Measured Reality

- **Discoverable:** YES ✅
- **Installable:** YES ✅ (`pip install arifos`)
- **Inspectable & Forkable:** YES ✅
- **Independent Validation:** NOT YET ESTABLISHED ❌

---

## Canonical Witness Ledger
For complete evidentiary matrices, citations, and the W1–W5 classification model, see:  
[`docs/EXTERNAL_WITNESS_LEDGER.md`](./EXTERNAL_WITNESS_LEDGER.md)
