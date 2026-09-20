# arifOS — Market Positioning, 2026-09

> **All external figures observed 2026-09-20T19:12Z.** Star/push source:
> `GET https://api.github.com/repos/{owner}/{repo}`, same run. Live probes
> (`arifos.arif-fazil.com/health`, `127.0.0.1:8081/health`) beat any static count. Items not
> re-observable are marked UNVERIFIED and must not be quoted in a sales context.

---

## 1. Market map

| Project | Stars | Last push |
|---|---:|---|
| crewAIInc/crewAI | 58,822 | 2026-09-20T17:11Z |
| langchain-ai/langgraph | 42,020 | 2026-09-20T16:19Z |
| microsoft/semantic-kernel | 28,581 | 2026-09-19T01:54Z |
| guardrails-ai/guardrails | 7,435 | 2026-09-18T01:48Z |
| NVIDIA/NeMo-Guardrails → `NVIDIA-NeMo/Guardrails` (301) | 7,172 | 2026-09-18T21:20Z |
| agiresearch/AIOS | 6,403 | 2026-07-20T14:43Z |
| **microsoft/agent-governance-toolkit** (MIT) | **6,299** | 2026-09-20T10:33Z |
| ariffazil/arifOS | 51 | 2026-09-20T17:49Z |

`agent-governance-toolkit` repo `created_at` **2026-03-02**, announced **2026-04-02**
([Microsoft Open Source blog](https://opensource.microsoft.com/blog/2026/04/02/introducing-the-agent-governance-toolkit-open-source-runtime-security-for-ai-agents/)).
It claims 10/10 OWASP Agentic Top 10 coverage and owns the literal phrase "AI agent governance
toolkit": ~6.3k stars in ~6.4 months, pushed same-day. arifOS has 51 stars — it is not in this
market as a vendor, it is a reference implementation of a position.

Gartner maintains an **"AI governance platforms"** market
([gartner.com](https://www.gartner.com/reviews/market/ai-governance-platforms), observed
2026-09-20). The vendor names in the brief (Credo AI, IBM watsonx.governance, OneTrust,
ServiceNow, Vijil, Zenity, Galileo, AWS Bedrock Guardrails) were **not individually re-verified** —
UNVERIFIED.

### Regulatory tailwind — with one correction

- **NIST AI Agent Standards Initiative**, announced **February 2026** by CAISI — agent
  authentication, authorization, interop ([nist.gov](https://www.nist.gov/news-events/news/2026/02/announcing-ai-agent-standards-initiative-interoperable-and-secure)).
- **EU AI Act**: in force 2024-08-01, generally applicable **2026-08-02**
  ([EC](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)). **Correction
  to the brief:** Art. 50 transparency obligations bind from 2026-08-02, but high-risk obligations
  under Art. 6(2)/Annex III are reported as applying **2027-12-02** after a deadline extension
  ([artificialintelligenceact.eu](https://artificialintelligenceact.eu/high-level-summary/),
  [lw.com](https://www.lw.com/en/insights/ai-act-update-eu-resolves-to-change-rules-and-extend-deadlines)).
  Do not build the pitch on a date a lawyer can falsify.
- **Press pressure:** Fortune, *"AI agents are going rogue. CIOs are racing to put guardrails
  around them"*, 2026-09-16; *OpenAI discloses six more incidents of agents going rogue*, 2026-09-17.

**arifOS today (observed 2026-09-20):** `/health` → `healthy`, `floors_active: 13/13`,
`vault999: healthy`, `exposed_tools: 8`, `deployment_drift_status: aligned`; `/tools.json` → exactly
8 verbs; PyPI `arifos` **1!2026.9.2**, 82 releases.

---

## 2. Differentiation thesis

**Do not compete on "governance toolkit". Compete on provable decisions in a real
high-consequence domain.**

1. **The moat is domain-grounded governance, not generic guardrails.** A policy engine is a
   container for rules; its quality is testable only against rules somebody cared enough to write.
   arifOS governs a live Earth-science organ: GEOX exposes **25 canonical MCP tools**
   (`geox_well_qc`, `geox_basin`, `geox_prospect`, `geox_seismic_interpret`, `geox_claim`,
   `geox_glof`…), `tools_loaded: 25`, `surface_drift.drift_count: 0`,
   `authority_ceiling: 555_COMPUTE_ONLY`, `domain_law: NATURAL_LAW`, physics manifest hash
   published — observed `http://127.0.0.1:8081/health`. GEOX computes evidence and never
   adjudicates; arifOS holds the gavel. The separation *is* the product.
2. **The buyer is a regulated, high-consequence technical organisation — not every startup.**
   Subsurface review, resource certification, geohazard assessment and safety-critical engineering
   already produce falsifiable numeric claims, are audited, and hand-write their QC gates. They are
   the only buyers for whom "typed provenance + sealed verdict" *replaces work they already do*.
3. **The proof is receipts, verdicts and post-mortems — not policy prose.** The verdict lattice is
   ordered and non-compensable (VOID < HOLD < SABAR < PARTIAL < SEAL; `kernel-sot.yaml`,
   F13-ratified 2026-09-16). Failures are published as canon: `kernel-sot.yaml`'s `observed_drift`
   block records a public-surface/runtime contract mismatch *with root cause*; commits `33792ab74`
   (G-02) and `e8e6f9335` (G-10) are public fixes. A competitor can show a policy that *would*
   block a bad action; arifOS can show the action it *did* stop, and the receipt.

### 2.1 Strongest counter-argument — and the answer

**Counter:** *The domain moat is not a moat, it is a liability.* GEOX is BSL-1.1 (production use
requires a licence), has **0 stars**, one maintainer, 25 tools. A generic toolkit is adoptable in an
afternoon by anyone; a governance product requiring the buyer to also trust a single-author
geoscience organ is adoptable by nobody. Energy subsurface buyers already own domain reasoning
(Petrel, Techlog, SLB/Halliburton assurance) and procure through them. What they lack is the
*authority* layer — precisely the generic product this thesis says not to build. "Domain-grounded
governance" may therefore persuade agents and not procurement.

**Answer, with one concession.**
- *Conceded:* the energy-major sale is out of reach today, and GEOX's 0-star/BSL state means the
  domain asset cannot carry the position **on trust**. The moat is **conditional, not established**;
  selling it as established is fabrication.
- *The argument survives* because the moat is not "we have a geoscience tool". It is that **a
  governance kernel can only be judged by the quality of decisions it actually intercepted** — and
  GEOX makes those decisions technical, falsifiable and checkable by an outsider, with observation,
  derivation and interpretation kept separate and the physics manifest hash published. Every
  project in §1 can demo a rule; none runs a live high-consequence reasoning domain to attach a real
  verdict to. That is a structural difference, not a scale difference.
- *So the wedge changes:* not energy majors, but the narrow technical team that already writes QC
  spreadsheets and hates it. There a 25-tool Earth engine beats the artefact it replaces, and
  receipts are a benefit rather than a project. The moat becomes real when (a) GEOX surface
  consistency holds, (b) one redacted decision receipt is public, (c) the BSL evaluation path is
  stated in one paragraph.

---

## 3. Buyer segments, ranked

| # | Segment | Why they buy | Why they hesitate |
|---|---|---|---|
| 1 | **Subsurface / basin & prospect review, resource certification, geohazard (GLOF)** — independents, data custodians, consultancies | Already produce falsifiable claims under audit; `geox_prospect` / `geox_claim` substitute for bespoke spreadsheets | BSL licence; single-maintainer risk; no named peer reference |
| 2 | **Agent-infrastructure builders needing an authority plane** | Adopt on the 8-verb MCP surface; GEOX is the worked example, not the SKU | MCP-native only, no hosted SaaS, 51 stars = no social proof |
| 3 | **Regulated safety-critical engineering** (process, industrial, civil geotech) | Art. 50 (2026-08-02) + NIST initiative create budget lines; need immutable evidence trails | Long procurement; will demand SOC 2 / independent attestation arifOS lacks |

Segment 1 is primary (best proof-per-effort). Segment 3 is deliberately third: real but slow.

---

## 4. Proof assets

**Exist.** 8-verb MCP surface live + `tools.json`; `/health` showing `floors_active 13/13`,
`vault999: healthy`, `deployment_drift_status: aligned`; ordered non-compensable verdict lattice;
7 CI gate workflows (conformance, vault-integrity, floor gate, governance gate, runtime drift,
external witness); PyPI `arifos` 1!2026.9.2 across 82 releases; GEOX live at 25 canonical tools,
drift 0, physics manifest hash published; public post-mortem canon plus named fix commits.

**Missing — these block the thesis:**
- **No public end-to-end decision receipt** (one proposed action, floors evaluated, verdict,
  VAULT999 hash, redacted) — the single artefact no competitor can fabricate. *Whether an existing
  case study serves this is another agent's scope; not assessed here.*
- **GEOX surface inconsistency:** `/root/GEOX/tools.json` advertises **31** public names (incl. 6
  `geox_glof_cascade_*`) while live `/health` reports **25** canonical tools and
  `CANONICAL_PUBLIC_SURFACE.json` lists 25 (observed 2026-09-20 by file read). Live health
  self-reports `drift_count: 0`, so the mismatch is in the static advertisement, not the wire.
- **BSL-1.1 evaluation path unstated** — GEOX README says production use requires a licence; no
  evaluation tier was found.
- **No published independent third-party attestation of VAULT999** (external-witness CI exists; no
  published witness artefact observed).
- **`kernel-sot.yaml` → `surface_projection.ratification_status: "PROPOSED"`** — the public/gated
  split of the 8 verbs is not yet F13-ratified. Do not state it as settled.
- **Graphiti is RETIRED_888 (2026-09-04); semantic floor off by choice (`ARIFOS_ML_FLOORS=0`)** —
  from the README SOT-MANIFEST. Any pitch implying a live temporal knowledge graph or semantic
  floor is false today.

---

## 5. Next 5 distribution actions (impact ÷ effort)

| # | Action | Effort | Impact | Rationale |
|---|---|---|---|---|
| 1 | Publish **one redacted decision receipt**: GEOX claim → `arif_judge` → verdict → VAULT999 hash, with trace_id chain | 1–2 d | **High** | Only proof class competitors cannot fabricate; converts §2 from claim to evidence |
| 2 | Publish the **GEOX evaluator path** (what a team may run under BSL-1.1) + a 15-min "subsurface claim under governance" walkthrough | 2 d | **High** | Unblocks segment 1, the primary buyer |
| 3 | **Fix GEOX surface consistency** (static 31 vs live 25) and publish the divergence + fix as a post-mortem | 1 d | Medium | Every gap published becomes proof of the receipts thesis |
| 4 | Register on **MCP registries / curated MCP lists** with the authority-plane one-liner, GEOX as worked example | 0.5 d | Medium | Cheap reach into segment 2, no new claims required |
| 5 | Publish **this market map as a dated public page** with re-observation instructions | 1 d | Medium | Demonstrates "we publish our own numbers, dated" instead of asserting it |

**Do not:** fight for the phrase "AI agent governance toolkit"; publish parity tables against
Microsoft; claim enterprise readiness without an attestation artefact.
