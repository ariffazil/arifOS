# External Witness Ledger

Status: WITNESSED & CLASSIFIED
Last Audit: 2026-10-22
Authority: DERIVED from Public External Observation
Maintainer: arifOS Federation

---

## Canon: Witness > Narrative

> **Governing Invariants:**
> - Claim ≠ Witness
> - Listing ≠ Endorsement
> - Indexing ≠ Validation
> - Reality remains the final judge.
>
> The maturity progression of a governed system:
> **Discover (W1/W2) → Observe (W3) → Analyze (W3) → Verify (W5) → Trust**  
> *(never Claim → Market → Believe)*

This ledger tracks references originating strictly outside arifOS-controlled surfaces.
External witnesses are classified into five distinct tiers based on evidentiary function, ensuring that mere discoverability is never confused with independent verification.

---

## Witness Classification State Lattice

A system that can only store "proof" inevitably degenerates into propaganda. 
A system that rigorously stores both "proof" and "disproof" remains a scientific audit engine.

Every reference in this ledger must evaluate to one of four mutually exclusive states:

| State | Definition | Epistemic Rule |
|:---|:---|:---|
| **Verified** | Directly observed, active, and reproducible via live external HTTP/API probe. | Promoted to live evidence table. |
| **Observed** | Externally authored by a third party, but awaiting continuous automated reconciliation. | Tracked as candidate witness; not yet proof of continuous health. |
| **Unknown** | Reported in secondary feeds or logs, but unconfirmed by direct probe. | Held under quarantine until probed. |
| **Rejected** | Previously reported, asserted, or assumed, but falsified upon direct inspection (inaccurate, dead link, or unverified assertion). | Persisted in public Disproof/Rejection Ledger. History is never erased. |

---

## 1. Disproof & Rejection Log (Anti-Cult Invariant)

To preserve epistemic honesty, the following claims have been tested and **REJECTED** or downgraded:

| Target Surface / Claim | Initial Assertion | Audit Finding (2026-10-22) | State |
|:---|:---|:---|:---|
| **Official Anthropic MCP Registry** | Asserted listing of `io.github.ariffazil/aaa-mcp` in upstream Anthropic registry. | Direct web and API search of official Anthropic registry found no active indexed entry. | ❌ **REJECTED / UNVERIFIED** (Namespace declared only) |
| **Independent Continuous Verifier** | Third-party continuous verification of claims.json. | No third-party runner is bound to the CI verification loop. | ❌ **REJECTED / OPEN GAP 4** |
| **Smithery.ai Indexing** | Indexing on Smithery directory. | Search for `arifos` on `smithery.ai` returned 0 indexed entries. | ❌ **REJECTED** (Not present) |
| **Academic Citations** | Formal peer-reviewed journal papers. | No active DOI, arXiv, or peer-reviewed publication exists. | ❌ **REJECTED** (Aspiration only) |

---

## 2. Witness Classification Model (W1 – W5)

### Tier W1 — Public Registries (Discoverability)
*Core question answered:* **"Can I find it and install it?"**

| Entity / Platform | Type | Purpose | Direct Reference | State |
|:---|:---|:---|:---|:---|
| **PyPI (`arifos`)** | Package Registry | Public Python distribution | `https://pypi.org/project/arifos/` | ✅ **Verified** |
| **PyPI (`arifosmcp`)** | Package Registry | Secondary MCP distribution | `https://pypi.org/project/arifosmcp/` | ✅ **Verified** |
| **GitHub (`ariffazil/arifOS`)** | Source Repository | Public AGPL-3.0 codebase & audit trail | `https://github.com/ariffazil/arifOS` | ✅ **Verified** |
| **MCP Registry Namespace** | Protocol Registry | Canonical namespace declaration | `io.github.ariffazil/aaa-mcp` | ⚠️ **Observed** (Self-declared) |

---

### Tier W2 — Independent Catalogs & Marketplaces (External Indexing)
*Core question answered:* **"Has third-party tooling ingested and indexed it?"**

| Catalog / Directory | Ingested Metadata | Purpose | State |
|:---|:---|:---|:---|
| **Glama.ai MCP Registry** | Server endpoint, schema, and floor descriptions | Tooling discovery | ✅ **Verified** (`glama.ai/mcp/servers/...`) |
| **LobeHub Plugin Directory** | Skills, prompts, and induction guides | Agent runtime indexing | ✅ **Verified** |
| **Model Context Protocol Client Directory** | Setup guides, transport config, and FAQ | Ecosystem listing | ✅ **Verified** |
| **Loomal MCP Marketplace** | Repository metadata, PyPI linkage | Marketplace discovery | ✅ **Verified** |
| **Skills Playground MCP Catalog** | Claude, Cursor, and VS Code integration snippets | Client config discovery | ✅ **Verified** |
| **G2 AI Marketplace** | Listed under *Responsible AI* & *AI Transparency* | Software directory | ✅ **Verified** |
| **MCPSift & MCP Changefeed** | Automated schema scraping and change tracking | Changefeed tracking | ✅ **Verified** |
| **Willow Control Plane (`withwillow.ai`)** | Governed MCP connector definition | Enterprise catalog | ✅ **Verified** |

---

### Tier W3 — Independent Analysis & Landscape Studies (External Interpretation)
*Core question answered:* **"Did someone outside the system examine and analyze the architecture?"**

| Source / Author | Type of Artifact | Core External Finding / Assessment | State |
|:---|:---|:---|:---|
| **Agentrust: Awesome AI Governance** | Curated Production AI Governance Index | Classified under production AI governance frameworks alongside Microsoft AGT, Bifrost, Allowly, Conarium: *"AGPL-3.0 governance kernel for MCP agents that evaluates proposed actions against policy floors F1-F13, answers one of seven wire verdicts, and keeps a hash-chained decision ledger."* | 🔍 **Observed** (`agentrust-io/awesome-ai-governance`) |
| **Tom Rochette: AI Control Planes Research** | Independent Architectural Deep-Dive & Feature Matrix | Evaluated: *"Its separation of powers is the design point: proposer, judge, executor, and witness are four different components... and the judge never consults a model... The self-audit culture is unlike anything else in this category: the project publishes its own failing floors, a caught false pass, and a zero-revenue statement, which makes every other claim falsifiable."* | 🔍 **Observed** (`agents/control-planes/arifos/`) |
| **Hapax Systems: Constitution Research** | Comparative Systems Analysis | Benchmarked against axiom-based agent architectures: *"arifOS (ariffazil/arifOS) — Closest match to our axiom governance system. Both implement constitutional constraints on agent behavior... arifOS is the only project attempting constitutional AI governance, and it's runtime enforcement..."* | 🔍 **Observed** (`research/comparable-projects.md`) |

---

### Tier W4 — Community Signals & Ecosystem Participation (Participation)
*Core question answered:* **"Are external developers engaging with or cloning the system?"**

| Signal Surface | Measured Indicator | Scope / Context | State |
|:---|:---|:---|:---|
| **GitHub External Forks** | 12 forks across distinct accounts | Forks include `rohan-tessl/arifOS`, `Secure-Code-Zyloch-Basic/arifOS`, `mseep-ai/arifos`, `McBorisson/arifOS`, `chrstphe/arifOS` | 🔍 **Observed** (2026-10-22) |
| **GitHub Stargazers** | 54 stars | Organic discovery signal | 🔍 **Observed** (2026-10-22) |
| **External Code Mentions** | 1,372 public repo file matches | Citations in digests, open source lists, and configuration trackers | 🔍 **Observed** (2026-10-22) |
| **PyPI Download Volume** | ~750 monthly downloads (`arifos`) | Public telemetry from PyPI mirrors | 🔍 **Observed** (2026-10-22) |
| **Developer Community Forums** | Reddit threads (`r/mcp`, `r/ClaudeCode`, `r/ChatGPTPromptGenius`) | Discussions regarding runtime AI governance and MCP brake systems | 🔍 **Observed** |

---

### Tier W5 — Independent Verification (Reproducibility & Audit)
*Core question answered:* **"Can an external auditor independently reproduce and continuously verify all claims?"**

| Verifier Type | Target Requirement | Current State |
|:---|:---|:---|
| **Independent Verifier Kit** | Standalone out-of-band CLI (`verify-arifos`) running without arifOS runtime | ❌ **Rejected / Open Gap 4** |
| **Continuous CI Third-Party Seal** | Automated cryptographic verification bound into public CI | ❌ **Rejected / Open Gap 4** |
| **Academic Peer-Reviewed Paper** | Published paper with Zenodo/arXiv/SSRN DOI | ❌ **Rejected / Not Found** |
| **Commercial Security Audit** | Formal external SOC2 or third-party penetration/correctness audit | ❌ **Rejected / Not Found** |

---

## 3. Summary Matrix: Measured Reality

```
W1 · Public Registries          ─── VERIFIED ✅
W2 · Independent Catalogs       ─── VERIFIED ✅
W3 · Independent Analysis       ─── OBSERVED & DOCUMENTED 🔍
W4 · Community Signals          ─── OBSERVED (Early Stage) ⚠️
W5 · Independent Verification   ─── OPEN GAP (Rejected until bound) ❌
```

This ledger is maintained under the constitutional requirement that evidence outranks narrative, and that discovering a project must never be equated with verifying it.
