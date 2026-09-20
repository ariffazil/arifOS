# arifOS Standards Crosswalk — 2026-09

**Status:** draft for review · **Observation date for all external references: 2026-09-21**
**arifOS source baseline:** branch `fix/judge-default-latency-class-20260921`, HEAD `572621510`
**Scope:** `docs/standards/` only. This document changes no code, no policy, and no runtime state.

---

## 0. Index

| § | Section | What it answers |
|---|---|---|
| 1 | [How to read this document](#1-how-to-read-this-document) | Evidence classes, and what each mapping type means |
| 2 | [Framework references](#2-framework-references) | Every external framework cited, with URL, version, observation date, verification level |
| 3 | [arifOS control inventory](#3-arifos-control-inventory) | What F1–F13 actually say, quoted from repo sources with `path:line` |
| 4 | [Mappings](#4-mappings) | 4A OWASP LLM Top 10 · 4B OWASP Agentic Top 10 · 4C NIST AI RMF · 4D ISO/IEC 42001 · 4E EU AI Act |
| 5 | [Gaps declared](#5-gaps-declared) | Per-framework `NO DIRECT COUNTERPART` rows |
| 6 | [Structural gaps](#6-structural-gaps-s1s12) | Obligations arifOS does not satisfy at all, at architecture level |
| 7 | [Internal divergences that block clean mapping](#7-internal-divergences-that-block-clean-mapping) | Places where the repo does not agree with itself on the floors |
| 8 | [Unverified references](#8-unverified-references) | Everything I could not verify, named explicitly |
| 9 | [How a buyer verifies this document](#9-how-a-buyer-verifies-this-document) | The self-audit procedure |
| 10 | [Counts and definitions](#10-counts-and-definitions) | Machine-checkable tallies |

---

## 1. How to read this document

**Evidence classes.** Every claim here is one of:

- **`OBSERVED`** — read from a file in this repository, with `path:line`; or read from the framework's own published page, with URL and observation date.
- **`OBSERVED-VIA-SECONDARY`** — the framework's primary text was not reachable; the claim rests on a named third-party summary. Flagged inline and listed in §8.
- **`UNVERIFIED`** — stated as unknown. Never silently upgraded.

There is no fourth class. Nothing in this document is paraphrased from memory, from a model's training data, or from the task brief.

**Mapping types.** Each row in §4 is exactly one of:

| Type | Meaning |
|---|---|
| **DIRECT** | The framework item names a control obligation, and arifOS has an enforced counterpart for it. "Enforced" means a named code path in this repo evaluates it, not that a document mentions it. |
| **PARTIAL** | A counterpart exists but does not cover the framework item's full obligation. The limitation is stated in the row. **PARTIAL is not a synonym for DIRECT.** |
| **NO DIRECT COUNTERPART** | No counterpart exists. This is a finding, not a defect to be hidden. |

**The failure mode this document is designed to avoid.** A crosswalk padded with false equivalences is worse than no crosswalk, because the reader it targets — a CISO or a regulator's technical assessor — reads the framework in the original language and will catch the padding. Where I could not justify a mapping from cited text, the row says `NO DIRECT COUNTERPART`.

**What this document is not.** It is not a certification, not a conformity assessment, not legal advice, and not a statement that arifOS makes its user compliant with anything. See §6, S5, S6 and S12.

---

## 2. Framework references

| # | Framework | Version / edition referenced | URL | Observed | Verification |
|---|---|---|---|---|---|
| F-1 | OWASP Top 10 for LLM Applications | 2025 edition — `LLM01:2025`…`LLM10:2025` | https://genai.owasp.org/llm-top-10/ | 2026-09-21 | **OBSERVED** — the ten rider titles read on the OWASP GenAI Security Project risk index |
| F-2 | OWASP GenAI LLM Top 10 **2026** | resource dated 2026-08-03 | https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/ | 2026-09-21 | **EXISTENCE OBSERVED, CONTENTS NOT READ** — resource page read; enumerated 2026 risk list not read. §4A maps the 2025 edition only. |
| F-3 | OWASP Top 10 for Agentic Applications | **2026** — `ASI01`…`ASI10` | https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ | 2026-09-21 | **OBSERVED** (resource page, dated December 9 2025) + rider names read in the OWASP launch post below |
| F-3a | OWASP ASI launch post (rider names ASI01–ASI10) | 2025-12-09 | https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/ | 2026-09-21 | **OBSERVED** — all ten rider names quoted at source |
| F-4 | OWASP Agentic Security Initiative (ASI) project | initiative page, includes ACS + "AIUC-1 Crosswalk" + Agentic Top 10 | https://genai.owasp.org/initiatives/agentic-security-initiative/ | 2026-09-21 | **OBSERVED** — project, leads, workstreams and resource list read |
| F-5 | NIST AI Risk Management Framework (AI RMF 1.0) | 1.0, released 2023-01-26 | https://www.nist.gov/itl/ai-risk-management-framework | 2026-09-21 | **OBSERVED** — release history, AI 600-1 (2024-07-26), 2026-04-07 critical-infrastructure profile concept note, and "AI RMF 1.0 is being revised" all read on this page |
| F-5a | AI RMF Core — Govern / Map / Measure / Manage and subcategory text | excerpt from AI RMF 1.0 (2023) | https://airc.nist.gov/airmf-resources/airmf/5-sec-core/ | 2026-09-21 | **OBSERVED** — §4C subcategory identifiers and outcome text read here |
| F-6 | NIST AI Agent Standards Initiative | page created 2026-02-17, updated 2026-08-14 | https://www.nist.gov/artificial-intelligence/ai-agent-standards-initiative | 2026-09-21 | **OBSERVED** — three strategic pillars, RFI on AI agent security, listening sessions |
| F-6a | NIST NCCoE concept paper — *Accelerating the Adoption of Software and AI Agent Identity and Authorization* | published 2026-02-05, comments closed 2026-04-02 | https://csrc.nist.gov/pubs/other/2026/02/05/accelerating-the-adoption-of-software-and-ai-agent/ipd | 2026-09-21 | **OBSERVED** — authors, dates, scope ("identity standards… with a focus on agentic AI applications"), and the stated concerns incl. "controls to prevent and mitigate prompt injection techniques" |
| F-7 | ISO/IEC 42001:2023 — AI management system (requirements) | 2023 | https://www.iso.org/standard/81230.html | 2026-09-21 | **NOT REACHABLE — bot protection.** `iso.org` served a Cloudflare interstitial on every attempt (browser + extract), and `r.jina.ai` returned `HTTP 403`. Clause and Annex A structure in §4D is **OBSERVED-VIA-SECONDARY** (see §8, U-1). |
| F-8 | EU AI Act — Regulation (EU) 2024/1689, article-level text | as rendered by the AI Act Explorer, page "last updated 31 August 2026" | https://artificialintelligenceact.eu/ | 2026-09-21 | **OBSERVED via Explorer** — Articles 5, 9, 12, 14, 15, 19, 26, 27, 50, 72, 99, 113 read individually (URLs in §4E). The Explorer flags amended provisions; the consolidated Official Journal text was **not** read. See §8, U-7. |
| F-9 | EU AI Act application timeline | "Last updated: 31 August 2026" | https://artificialintelligenceact.eu/implementation-timeline/ | 2026-09-21 | **OBSERVED** |

### 2.1 Correction to a widely repeated date (EU AI Act high-risk)

The brief for this document cites "the high-risk obligations date 2026-08-02". **That is no longer what the cited sources say.**

`OBSERVED` — Article 113 as rendered on 2026-09-21, with the Explorer's amendment markers:

> "It shall apply from 2 August 2026. However: … (c) Chapter III, Sections 1, 2, and 3, with the exception of Article 6(5), shall apply from: *(i) 2 December 2027 as regards AI systems classified as high-risk pursuant to Article 6(2) and Annex III;* and *(ii) 2 August 2028 as regards AI systems classified as high-risk pursuant to Article 6(1) and Annex I;*" — https://artificialintelligenceact.eu/article/113/ , observed 2026-09-21. The Explorer annotates both sub-points as *amended / new*.

Interpretation, stated as interpretation: 2 August 2026 is the **general** application date for the remainder of the Act; the Chapter III high-risk regime for Annex III systems is dated 2 December 2027 and for Annex I systems 2 August 2028. **Any publication that repeats "high-risk obligations from 2026-08-02" without the amendment is repeating a superseded date.** This document uses the amended dates.

---

## 3. arifOS control inventory

The floors are quoted from two repo sources that agree on names and disagree in places on wording (§7). Where they disagree, both are shown.

### 3.1 Canonical floor table

`OBSERVED` — `GENESIS/000_KERNEL_CANON.md:90-104`, marked there as "Single source of truth", with the machine-readable twin `GENESIS/FLOOR_TABLE.json`:

| Floor | Name | Canonical one-line rule (verbatim) |
|---|---|---|
| F1 | AMANAH | "Reversible first. Irreversible → 888 HOLD" |
| F2 | TRUTH | "P(truth) ≥ 0.99. Cheap claims = VOID. Evidence carries epistemic label from OBS / DER / INT / SPEC." |
| F3 | TRI-WITNESS | "Human + AI + Earth witness ≥ 0.75 (judgment-time, inside the governed system)." |
| F4 | CLARITY | "Every output must reduce entropy (ΔS ≤ 0)" |
| F5 | PEACE² | "Non-destructive power" |
| F6 | EMPATHY *(op: MARUAH)* | "Protect weakest stakeholder. Preserve dignity (maruah)." |
| F7 | HUMILITY | "No fake certainty. Ω₀ ∈ [0.03, 0.05]. Confidence cap = 1 − Ω₀ ∈ [0.95, 0.97]." |
| F8 | GENIUS | "G ≥ 0.80 for complex actions" |
| F9 | ANTIHANTU | "No deception, manipulation, consciousness claims" |
| F10 | ONTOLOGY | "AI-only ontology. Soul = VOID; map to harness content" |
| F11 | AUDITABILITY | "Every decision logged. Provenance per field." |
| F12 | RESILIENCE | "Injection defense" |
| F13 | SOVEREIGN | "Human veto FINAL. Harness switch belongs to sovereign." |

Richer per-floor rules live in `GENESIS/FLOOR_TABLE.json:8-196` (including F1's metabolic gate `φFQ ≥ 0.80`, F2's terminal labels `SYN` / `RECYCLED_SYN`, F7's floor-not-cap clarification at `:138`, and F13's first-seal-wins ordering at `:191`).

### 3.2 Runtime enforcement constants

`OBSERVED` — `core/laws.py`, the Python enforcement surface:

| Floor | Threshold constant (`core/laws.py:75-89`) | Level (`:115-134`) | Rule text (`:197-211`) |
|---|---|---|---|
| F1 | 0.50 | HARD | "Amanah - Reversibility and audit mandate" |
| F2 | 0.99 | HARD | "Truth - Information fidelity (anti-hallucination)" |
| F3 | 0.75 | DERIVED | "Quad-Witness - Byzantine consensus (H×A×E)^(1/3)" |
| F4 | 0.0 | HARD | "Clarity - Entropy reduction (ΔS ≤ 0)" |
| F5 | 1.0 | SOFT | "Peace² - Non-destructive power" |
| F6 | 0.70 | SOFT | "Empathy - Stakeholder care (κᵣ)" |
| F7 | (0.03, 0.05) | HARD | "Humility - Uncertainty band [0.03, 0.05]" |
| F8 | 0.80 | DERIVED | "Genius - G = (A × P × E × X)^(1/4) …" |
| F9 | 0.30 | HARD | "Anti-Hantu - No spiritual cosplay / consciousness claims" |
| L10 | 1.00 | HARD | "Ontology - Category lock (AI ≠ human)" |
| L11 | 1.00 | HARD | "CommandAuth - Verified identity / session required" |
| L12 | 0.85 | HARD | "Injection - Block adversarial control" |
| L13 | 1.00 | HARD | "Sovereign - Human final authority (888_HOLD)" |

Verdict lattice: `OBSERVED` — `kernel-sot.yaml:63-70`, ascending authority `VOID < HOLD < SABAR < PARTIAL < SEAL`, terminal `{VOID, HOLD, SEAL}`, retryable `{SABAR}`.

Verdict assignment: `OBSERVED` — `core/laws.py:356-376`. Any HARD-floor violation yields `VOID` and blocks the action; a CRITICAL or HIGH risk tier yields `HOLD`; SOFT-only violations yield `SABAR`; DERIVED-only yields `PARTIAL`; otherwise `SEAL`.

### 3.3 Where the floors are enforced

`OBSERVED` — `arifosmcp/runtime/governance_pipeline.py:940-950`, Gate 5 (`_gate_floors` at `:1910`) is called for every tool call; a failing gate sets `PipelineVerdict.HOLD` and returns before execution. `check_laws()` is `arifosmcp/runtime/law.py:195`.

`OBSERVED` — the same gate's failure path, `arifosmcp/runtime/governance_pipeline.py:1941-1948`:

```python
except ImportError:
    # check_laws not available — soft pass
    return GateResult(
        gate=Gate.FLOORS,
        passed=True,
        reason="check_laws not available — soft pass (degraded mode)",
```

**The primary floor gate fail-opens.** A runtime in which `check_laws` cannot be imported reports Gate 5 as *passed*, not as *unknown*. The adjacent Gödel-closure gate does the opposite — `:1967-1987` is explicitly fail-closed ("godel_lock_gate not available — fail-closed (HOLD)"). This asymmetry is carried into §6, S1, and it is the single most important caveat in this document: **every `DIRECT` row in §4 is conditional on the floor module importing successfully at runtime.**

Defaults observed at `governance_pipeline.py:606` (`enforcement_mode: str = "enforce"`) and `:611` (`floor_enabled: bool = True`).

### 3.4 Capability surface

`OBSERVED` — `kernel-sot.yaml:84-155`: 8 canonical public verbs (`arif_init`, `arif_observe`, `arif_think`, `arif_route`, `arif_memory`, `arif_judge`, `arif_forge`, `arif_seal`), each carrying a `mutation_class` and an `authority` field (`VERIFIED_ACTOR`, `SCOPED_LEASE`, `JUDGE_LEASE` / `JUDGED_LEASE`, `F13_BOUND`). `arif_seal` carries `irreversible: true`, `requires_human_confirmation: true`. This per-verb authority typing is the substrate for several mappings below.

### 3.5 Ledger

`OBSERVED` — `deploy/vault999-writer/main.py:713` (`"append_only_enforced": True`); `scripts/verify_vault_chain.py` (chain verification); `docs/REFERENCE-MONITOR-CLAIMS.md:25-30` records the `lsattr` append-only evidence chain for `/root/VAULT999` and `/var/lib/arifos/vault999/`, last green 2026-09-20.

**Not verified here:** I did not run `lsattr` against the live ledger from this workspace. The append-only property is therefore reported as *claimed with an in-repo check procedure*, not as measured by me.

---

## 4. Mappings

Every row cites the framework item's own text or title as read (see §2 for per-framework URLs and dates), and the arifOS control with a `path:line` or a §3 table reference.

### 4A. OWASP Top 10 for LLM Applications 2025

Rider titles `OBSERVED` at https://genai.owasp.org/llm-top-10/ , 2026-09-21.

| ID | arifOS control | OWASP item 2025 | Type | Limitation / why |
|---|---|---|---|---|
| 4A-1 | **L12 INJECTION** — threshold 0.85, patterns include `ignore\s+(previous\|above\|all)\s+(instructions\|rules\|commands)`, `<script`, `eval(`, `exec(`, `rm -rf` (`core/laws.py:1219-1256`); F14 folded into L12 (`arifosmcp/runtime/law.py:199-203`) | **LLM01 Prompt Injection** | **DIRECT** | arifOS inspects the *parameters of a proposed tool call* before execution. It does not inspect model context windows, retrieved documents, or multi-turn conversation state, which is where most real LLM01 attacks land. |
| 4A-2 | — | **LLM02 Sensitive Information Disclosure** | **NO DIRECT COUNTERPART** | No floor governs confidentiality, PII handling, or output redaction. F2 TRUTH governs whether a claim is *warranted*, not whether it is *permitted to be disclosed*. |
| 4A-3 | — | **LLM03 Supply Chain** | **NO DIRECT COUNTERPART** | arifOS has no model, dataset, package or dependency provenance control. `repo-inventory.json` / `package-origin-report.json` exist as repo metadata, not as an enforced control. |
| 4A-4 | — | **LLM04 Data and Model Poisoning** | **NO DIRECT COUNTERPART** | F2's terminal labels for `SYN` / `RECYCLED_SYN` (`GENESIS/FLOOR_TABLE.json:204-205`) address *claim provenance laundering*, which is adjacent but is not training-data or embedding-store integrity. Claiming this as LLM04 coverage would be a false equivalence. |
| 4A-5 | — | **LLM05 Improper Output Handling** | **NO DIRECT COUNTERPART** | arifOS gates the inbound action. Sanitisation of an LLM's output before a downstream consumer uses it is outside the kernel's path. |
| 4A-6 | **F1 AMANAH** + **F13 SOVEREIGN** + **L11 CommandAuth**; irreversibility classes `IRREVERSIBILITY_COMPLEXITY` (`core/laws.py:136-156`) and risk tiers `_assess_risk_tier` (`:1365-1381`) | **LLM06 Excessive Agency** | **DIRECT** | This is the closest thing arifOS does to its stated purpose: a proposed action is classified by consequence, and irreversible classes route to HOLD. Limitation: an agent that never calls arifOS is unaffected; coverage is per-invocation, not ambient. |
| 4A-7 | — | **LLM07 System Prompt Leakage** | **NO DIRECT COUNTERPART** | Not addressed. (`kernel-sot.yaml` concerns itself with *capability-surface* leakage — internal verbs in `llms.txt` — which is a different asset class from system-prompt disclosure.) |
| 4A-8 | — | **LLM08 Vector and Embedding Weaknesses** | **NO DIRECT COUNTERPART** | `arif_memory` carries `mutation_class: GOVERNED_MEMORY` (`kernel-sot.yaml:122`), which governs writes through the kernel's own memory verb. It does not protect an external vector store. |
| 4A-9 | **F2 TRUTH** (labels `OBS`/`DER`/`INT`/`SPEC`/`SYN`/`RECYCLED_SYN`; `SPEC` and `SYN` "supports_seal: false", `GENESIS/FLOOR_TABLE.json:200-205`) + **F7 HUMILITY** (Ω₀ ∈ [0.03,0.05]) + **F4 CLARITY** (ΔS ≤ 0) | **LLM09 Misinformation** | **DIRECT** | strong. `core/laws.py:520-644` scores F2 from *output-side* claim envelopes and explicitly refuses to reward input wording ("Input wording is not evidence"). Limitation: enforcement requires the caller to supply claim envelopes; without them F2 fails closed at a low score rather than measuring the claim. |
| 4A-10 | Nearest control: **Gate 2 BUDGET** (`budget_enabled: bool = True`, `governance_pipeline.py:608`; documented in `docs/floor_coverage_matrix.md:39`) | **LLM10 Unbounded Consumption** | **PARTIAL** | A budget gate is invoked, but it is **not a floor**, is not part of the constitutional set, and this document found no enforced per-agent compute/loop ceiling. Consumption control belongs to the caller's orchestration layer. |

**4A tally:** DIRECT 3 · PARTIAL 1 · NO DIRECT COUNTERPART 6.

### 4B. OWASP Top 10 for Agentic Applications 2026

Rider names `OBSERVED` verbatim in the OWASP ASI launch post (URL F-3a), 2026-09-21: ASI01 Agent Goal Hijack · ASI02 Tool Misuse · ASI03 Identity & Privilege Abuse · ASI04 Agentic Supply Chain Vulnerabilities · ASI05 Unexpected Code Execution · ASI06 Memory & Context Poisoning · ASI07 Insecure Inter-Agent Communication · ASI08 Cascading Failures · ASI09 Human-Agent Trust Exploitation · ASI10 Rogue Agents.

| ID | arifOS control | OWASP ASI item 2026 | Type | Limitation / why |
|---|---|---|---|---|
| 4B-1 | L12 INJECTION pattern set + F13 (goal change bound to human ratification) | **ASI01 Agent Goal Hijack** | **PARTIAL** | arifOS can void a *tool call* whose parameters carry an override instruction, and can hold an action awaiting human authority. It cannot observe or correct drift that happens entirely inside a model's planning loop. |
| 4B-2 | **F1 AMANAH** (destructive-verb classification, `core/laws.py:467-518`) + **L11** (verified actor/session) + **F13** (AI self-approval blocked, `:1285`) | **ASI02 Tool Misuse** | **DIRECT** | This is arifOS's core function: a tool call is evaluated before it executes. Mutation classes and per-verb authority are declared in `kernel-sot.yaml:84-155`. |
| 4B-3 | **L11 CommandAuth** — `score = 1.0 if (has_session and has_actor) else 0.0`, threshold 1.0 (`core/laws.py:1201-1217`); **F13** blocking AI self-approval (`:1273-1287`) | **ASI03 Identity & Privilege Abuse** | **PARTIAL** | The check is presence-based: a non-empty `actor_id` **string** satisfies L11. There is no cryptographic binding to a credential in the floor logic itself (session/identity enforcement lives elsewhere in the runtime, which this document did not audit). Treat "verified identity" here as *declared*, not *proven*. |
| 4B-4 | — | **ASI04 Agentic Supply Chain Vulnerabilities** | **NO DIRECT COUNTERPART** | Same finding as 4A-3. |
| 4B-5 | **F1 AMANAH** destructive patterns include `execute` (`core/laws.py:485`); L12 includes `eval(`, `exec(`, `rm -rf` (`:1230-1233`) | **ASI05 Unexpected Code Execution** | **PARTIAL** | Pattern matching against an action string is a lexicon, not a sandbox. It raises cost; it does not bound capability. arifOS does not execute code and cannot confine a shell that never passes through it. |
| 4B-6 | **F2** terminal labels `SYN`/`RECYCLED_SYN` (`GENESIS/FLOOR_TABLE.json:204-205`) + `arif_memory` `mutation_class: GOVERNED_MEMORY` (`kernel-sot.yaml:122`) | **ASI06 Memory & Context Poisoning** | **PARTIAL** | Provenance labelling is a real defence against laundering a synthetic claim into an observed one. But arifOS governs only memory written through `arif_memory`; an agent's own context window is outside the kernel's reach. |
| 4B-7 | — | **ASI07 Insecure Inter-Agent Communication** | **NO DIRECT COUNTERPART** | arifOS serves MCP and A2A surfaces and receipts its own decisions, but no floor governs authenticity or integrity of messages *between* agents. L11 binds identity at the arifOS boundary only. |
| 4B-8 | — | **ASI08 Cascading Failures** | **NO DIRECT COUNTERPART** | The non-compensable verdict lattice (`kernel-sot.yaml:63-70`) stops a failing action; it does not contain multi-hop failure propagation across an agent fleet. |
| 4B-9 | **F9 ANTIHANTU** ("No deception, manipulation, consciousness claims"; threshold `C_dark ≤ 0.30`, `core/laws.py:1132-1169`) + **F2** + **F7** | **ASI09 Human-Agent Trust Exploitation** | **DIRECT** | The F2 design note is unusually well-aimed at this risk: polished, confident, unfounded output is exactly what the epistemic-label requirement is built to downgrade (`SPEC` = "Speculation, no falsifiable anchor", `supports_seal: false`). Limitation: F9 is implemented as a keyword count over the query string (`:1137-1151`), so it is a tripwire, not a detector. |
| 4B-10 | **F13 SOVEREIGN** (human veto final; harness switch belongs to the sovereign) + **F10 ONTOLOGY** (AI ≠ human category lock) | **ASI10 Rogue Agents** | **PARTIAL** | F13 gives a human a final veto and a harness switch, which is the governance half of the risk. The detection half — noticing an agent has permanently deviated *without* an attacker — is not implemented. arifOS is a gate, not a behaviour monitor. |

**4B tally:** DIRECT 2 · PARTIAL 5 · NO DIRECT COUNTERPART 3. (Rows: 10.)

### 4C. NIST AI RMF 1.0

Subcategory identifiers and outcome text `OBSERVED` at URL F-5a, 2026-09-21. This is a **selection** of subcategories, not the full catalogue; unmapped subcategories are unmapped, not implicitly covered.

| ID | arifOS control | AI RMF subcategory | Type | Limitation / why |
|---|---|---|---|---|
| 4C-1 | Floors as encoded policy; no legal-requirement register | **GOVERN 1.1** — legal and regulatory requirements understood, managed, documented | **PARTIAL** | The kernel can *encode* a rule once someone states it. It does not discover, inventory or track legal obligations. |
| 4C-2 | F1–F13 as an executable policy set (`GENESIS/000_KERNEL_CANON.md:90-104`) | **GOVERN 1.2** — trustworthy-AI characteristics integrated into policy | **DIRECT** | Unusually literal: the characteristics are compiled into scoring functions rather than written into a policy document. |
| 4C-3 | `_assess_risk_tier` (LOW/MEDIUM/HIGH/CRITICAL, `core/laws.py:1365-1381`) + `IRREVERSIBILITY_COMPLEXITY` (`:136-156`) + `IRREVERSIBILITY_TIME_TAX_MS` (`:158-165`) | **GOVERN 1.3** — processes established to determine the needed level of risk management based on risk tolerance | **DIRECT** | Tiers exist and change the verdict (CRITICAL/HIGH → HOLD). Limitation: thresholds are hard-coded constants, not organization-configurable tolerance. |
| 4C-4 | Floors + verdict lattice (`kernel-sot.yaml:63-70`) + non-compensable ordering | **GOVERN 1.4** — risk-management process and outcomes established through transparent policies, procedures, controls | **DIRECT** | Transparency is real: the ordering is published and VOID is terminal. |
| 4C-5 | — | **GOVERN 1.5** — ongoing monitoring and periodic review of the risk-management process, roles and frequency defined | **NO DIRECT COUNTERPART** | Continuous CI gates exist, but no scheduled review of the *floor process itself* with named owners is defined in-repo. |
| 4C-6 | — | **GOVERN 1.6** — mechanisms to inventory AI systems | **NO DIRECT COUNTERPART** | arifOS has no inventory of the agents it governs. |
| 4C-7 | — | **GOVERN 1.7** — decommissioning / phasing out AI systems safely | **NO DIRECT COUNTERPART** | No floor covers retirement of a governed agent. |
| 4C-8 | — | **GOVERN 2.2** — personnel and partners receive AI risk-management training | **NO DIRECT COUNTERPART** | Out of scope for a kernel; named so the reader does not assume a blank cell means "not asked". |
| 4C-9 | Per-verb authority typing (`kernel-sot.yaml:84-155`) + F13 + F3 witness roles | **GOVERN 3.2** — policies define and differentiate roles and responsibilities for human-AI configurations and oversight | **DIRECT** | Authority is attached to the *verb*, not to the person (`VERIFIED_ACTOR`, `SCOPED_LEASE`, `JUDGED_LEASE`, `F13_BOUND`). |
| 4C-10 | CI workflows (`.github/workflows/floor_gate.yml`, `07-vault-integrity.yml`, `external-witness.yml`) + adversarial test material (`docs/ADVERSARIAL_TESTS.md`) | **GOVERN 4.3** — practices enabling AI testing, incident identification, information sharing | **PARTIAL** | Testing and identification exist in-repo; there is no external information-sharing process. |
| 4C-11 | — | **GOVERN 6.1 / 6.2** — third-party AI risks and contingency processes | **NO DIRECT COUNTERPART** | No supplier-risk floor. |
| 4C-12 | `contracts/verdict_contract.json` requires `action_description`, `substrate`, `action_mode`, `reversibility` on every judged candidate | **MAP 1.1** — intended purposes, context-specific laws/norms and deployment settings understood and documented | **PARTIAL** | The contract forces a *declaration* of context and reversibility per action. It does not document context at system level. |
| 4C-13 | **F7 HUMILITY** (Ω₀ band, `GENESIS/FLOOR_TABLE.json:131-145`) + **F2** `SPEC` → "supports_seal: false" | **MAP 2.2** — information about knowledge limits and human oversight of output is documented | **DIRECT** | F7's floor-not-cap reasoning at `:139` is the clearest statement of this subcategory's intent in the repo. |
| 4C-14 | Authority ceilings per organ/verb; F4 CLARITY (ΔS) | **MAP 3.3** — targeted application scope specified and documented | **PARTIAL** | Scope exists as authority envelopes, not as a published per-deployment scope statement. |
| 4C-15 | **F13** + **F3 TRI-WITNESS** + refusal-closure HOLD types (`FAILURE` / `CONSTITUTIONAL` / `F13_REFUSAL`, `GENESIS/FLOOR_TABLE.json:309-314`) | **MAP 3.5** — processes for human oversight defined, assessed and documented | **DIRECT** | Typed HOLD is a genuinely stronger artefact than a boolean refusal. |
| 4C-16 | — | **MAP 4.1 / 4.2** — third-party and component risk mapped, internal controls documented | **NO DIRECT COUNTERPART** | As 4C-11. |
| 4C-17 | **F6 EMPATHY/MARUAH** (weakest-stakeholder) + **F5 PEACE²** + `HumanImpactAssessment` structured path (`core/laws.py:711-806`, fields incl. `stakeholders`, `blast_radius_bounded`, `weakest_stakeholder_protected`) | **MAP 5.1** — likelihood and magnitude of impacts to individuals, groups, society characterized | **PARTIAL** | The assessment schema is real and is consumed by F5/F6. It is *per action*, supplied by the caller, and defaulted to neutral when absent (`:1061` — "no stakeholder map provided (κᵣ unknown)"), which is a declaration gap, not a measurement. |
| 4C-18 | — | **MAP 5.2** — regular engagement with relevant AI actors, integrating feedback | **NO DIRECT COUNTERPART** | No external-stakeholder engagement mechanism. |
| 4C-19 | `THRESHOLDS` (`core/laws.py:75-89`) as the metric set | **MEASURE 1.1** — metrics selected; risks or characteristics that will not/cannot be measured are documented | **PARTIAL** | Metrics are explicit per floor. The second half of the subcategory — documenting the *unmeasurable* — is not implemented. |
| 4C-20 | **F3** prior-isolated witness requirement + `external-witness.yml` workflow | **MEASURE 1.3** — internal experts who did not serve as developers and/or independent assessors involved | **PARTIAL** | The independence principle is asserted and has CI scaffolding; this document found no evidence of a *named independent assessor* in the loop today. |
| 4C-21 | — | **MEASURE 2.3** — performance criteria measured and demonstrated for deployment-like conditions | **NO DIRECT COUNTERPART** | Floor thresholds are unit-tested in `tests/`; the RMF asks for validated performance in deployment conditions, which requires a different kind of evidence than the repo contains. |
| 4C-22 | Telemetry as a closure requirement for capabilities (`kernel-sot.yaml:257-258`); `docs/sandbox_telemetry_schema.md` | **MEASURE 2.4** — functionality and behaviour monitored in production | **PARTIAL** | Telemetry exists as a closure requirement for the kernel's own capabilities. Whether a *governed agent's* behaviour is monitored is a caller-side question this document did not audit. |
| 4C-23 | `arif_judge` modes include `hold`, `escalate` (`kernel-sot.yaml:133`) | **MEASURE 3.3** — feedback processes for end users and impacted communities to report problems and appeal system outcomes | **PARTIAL** | An escalation path exists inside the kernel. There is no channel for an *affected community*. |
| 4C-24 | — | **MEASURE 4.1–4.3** — feedback about efficacy of measurement gathered and assessed | **NO DIRECT COUNTERPART** | No assessment of the floor system's own measurement efficacy. |
| 4C-25 | `arif_judge` verdicts gate execution (`governance_pipeline.py:940-950`) | **MANAGE 1.1** — determination whether the system achieves its intended purposes and whether deployment should proceed | **DIRECT** | `VOID` is a documented decision not to proceed; the lattice is published. |
| 4C-26 | Non-compensable ordering, `VOID < HOLD < SABAR < PARTIAL < SEAL` (`kernel-sot.yaml:63-70`) | **MANAGE 1.2 / 1.3** — risk treatment prioritised; responses to high-priority risks developed and documented | **DIRECT** | Non-compensability is the substance of the claim: a hard violation cannot be averaged away. |
| 4C-27 | Typed HOLD (`FAILURE`/`CONSTITUTIONAL`/`F13_REFUSAL`) and HOLD as a non-terminal state (`docs/VERDICT_SEMANTICS.md:109`) | **MANAGE 1.4** — negative residual risks to downstream acquirers and end users documented | **PARTIAL** | Residual risk is *carried visibly* rather than documented as a register. |
| 4C-28 | **F13** harness switch + refusal closure (`GENESIS/FLOOR_TABLE.json:298-314`) | **MANAGE 2.4** — mechanisms to supersede, disengage or deactivate systems inconsistent with intended use | **DIRECT** | This is the clearest NIST mapping in the document: the sovereign's switch is constitutional, not advisory. |
| 4C-29 | — | **MANAGE 4.1** — post-deployment monitoring plans incl. override, decommissioning, incident response, change management | **NO DIRECT COUNTERPART** | No post-deployment monitoring *plan* artefact. |
| 4C-30 | — | **MANAGE 4.3** — incidents and errors communicated to relevant AI actors, including affected communities | **NO DIRECT COUNTERPART** | No external incident communication. |

**4C tally:** DIRECT 9 · PARTIAL 10 · NO DIRECT COUNTERPART 11. (Rows: 30.)

### 4D. ISO/IEC 42001:2023

**Verification warning, repeated here because it governs this whole table.** `iso.org` was not reachable on 2026-09-21 (bot protection; `r.jina.ai` returned `HTTP 403`). Clause titles below are `OBSERVED-VIA-SECONDARY` from a third-party summary that explicitly describes its own sourcing (konfirmity.com, §8 U-1). **No clause or control reference in §4D may be treated as read from the standard.** They are here so a reader holding the standard can check them, and so the mapping is falsifiable. Do not quote §4D into a procurement document without validating against the standard.

| ID | arifOS control | ISO/IEC 42001:2023 item | Type | Limitation / why |
|---|---|---|---|---|
| 4D-1 | — | **Clause 4** — Context of the organization | **NO DIRECT COUNTERPART** | An AIMS scopes an *organization*. arifOS is a component inside someone's system. |
| 4D-2 | F1–F13 as executable policy | **Clause 5.2** — AI policy | **PARTIAL** | A policy exists and is stronger than prose: it is compiled. But it has not been approved by the adopting organization's leadership as *their* AI policy. |
| 4D-3 | Per-verb authority typing; F13 | **Clause 5.3** — roles, responsibilities and authorities | **PARTIAL** | Authorities are assigned mechanically to verbs. Organizational assignment is the adopter's. |
| 4D-4 | — | **Clause 6.1** (incl. determining controls / Statement of Applicability), **Clause 6.2** (AI objectives) | **NO DIRECT COUNTERPART** | No SoA, no objectives register. |
| 4D-5 | VAULT999 receipts; F2 provenance | **Clause 7.5** — documented information | **PARTIAL** | The kernel produces the strongest *decision* record in the system. Competence records (7.2) and other documented information are absent. |
| 4D-6 | Floor evaluation before execution (`governance_pipeline.py:940-950`) | **Clause 8.2** — AI risk assessment | **DIRECT** | Per-action, pre-execution, with declared inputs (`contracts/verdict_contract.json`). |
| 4D-7 | Verdict lattice; HOLD/SABAR/VOID as treatments | **Clause 8.3** — AI risk treatment | **DIRECT** | Treatment options are enforced, not advisory. |
| 4D-8 | `verify_vault_chain.py`; floor-gate CI | **Clause 9.1** — monitoring, measurement, analysis and evaluation | **PARTIAL** | Measurement exists for the kernel's own integrity. Adopter-level monitoring is out of reach. |
| 4D-9 | — | **Clause 9.2** — internal audit | **NO DIRECT COUNTERPART** | CI gates are not an internal audit programme. |
| 4D-10 | — | **Clause 9.3** — management review | **NO DIRECT COUNTERPART** | No management review process. |
| 4D-11 | Scar/entropy doctrine; VAULT999 corrections | **Clause 10.1** — continual improvement | **PARTIAL** | The repo metabolises failures into floor/scar changes. That is practice, not a documented improvement process. |
| 4D-12 | `scars`, typed HOLD, correction receipts | **Clause 10.2** — nonconformity and corrective action | **PARTIAL** | Nonconformity is recorded as a constitutional violation, which is *stronger* than a paper NC. No formal NC workflow exists. |
| 4D-13 | F1–F13 | **Annex A.2** — policies related to AI | **PARTIAL** | As 4D-2. |
| 4D-14 | Per-verb `authority`; F3 independent witnesses | **Annex A.3** — internal organization (roles, responsibilities, reporting concerns) | **PARTIAL** | No independent "report a concern" channel that bypasses the owning channel. |
| 4D-15 | — | **Annex A.4** — resources for AI systems | **NO DIRECT COUNTERPART** | No resource/competence inventory. |
| 4D-16 | F6 MARUAH + F5 PEACE² + `HumanImpactAssessment` | **Annex A.5** — assessing impacts of AI systems on individuals, groups, society | **PARTIAL** | Per-action assessment supplied by the caller; not a standing impact-assessment process. |
| 4D-17 | — | **Annex A.6** — AI system life cycle (design, V&V, deployment, operation, decommissioning) | **NO DIRECT COUNTERPART** | arifOS governs actions at use time; it is not in the SDLC path. |
| 4D-18 | — | **Annex A.7** — data for AI systems | **NO DIRECT COUNTERPART** | No data-governance floor. |
| 4D-19 | Receipts; `llms.txt`; `docs/` surface | **Annex A.8** — information for interested parties | **PARTIAL** | Information is produced *for auditors of the decision*. It is not the "intended purpose and limitations" disclosure to affected parties that this control asks for. |
| 4D-20 | F1/F13 gate at the moment of use; `arif_judge` | **Annex A.9** — use of AI systems (intended use, monitoring in operation) | **PARTIAL** | Intended-use enforcement happens per call. Continuous operational monitoring of the *adopter's* system does not. |
| 4D-21 | — | **Annex A.10** — third-party and customer relationships | **NO DIRECT COUNTERPART** | No responsibility-allocation artefact down the supply chain. |

**4D tally:** DIRECT 2 · PARTIAL 11 · NO DIRECT COUNTERPART 8. (Rows: 21.)

### 4E. EU AI Act (Regulation (EU) 2024/1689) — article-level

Article text `OBSERVED` via the AI Act Explorer on 2026-09-21 (URLs per row). The Explorer's amendment markers are noted; the consolidated OJ text was not read (§8 U-7).

| ID | arifOS control | AI Act article | Type | Limitation / why |
|---|---|---|---|---|
| 4E-1 | F9 ANTIHANTU; F5 PEACE²; F10 ONTOLOGY | **Article 5 — Prohibited AI practices** (https://artificialintelligenceact.eu/article/5/) | **PARTIAL** | A gate could refuse a prohibited *action* it is shown. arifOS is not a provider of an AI system, does not classify practices, and cannot make anyone compliant with Art. 5. |
| 4E-2 | — | **Article 6 + Annex III — high-risk classification** | **NO DIRECT COUNTERPART** | Classification is the provider's obligation. arifOS has no classifier and no product scope. |
| 4E-3 | Floors as a per-decision risk system; typed HOLD; risk tiers | **Article 9 — Risk management system** (https://artificialintelligenceact.eu/article/9/) | **PARTIAL** | Art. 9 requires an iterative, lifecycle-spanning, *documented* risk-management system, with para. 9 requiring consideration of impact on persons under 18 and other vulnerable groups. arifOS supplies a per-decision gate, not an RMS, and its vulnerability consideration depends on the caller supplying a stakeholder map (see 4C-17). |
| 4E-4 | — | **Article 11 + Annex IV — technical documentation** | **NO DIRECT COUNTERPART** | No Annex IV documentation set. |
| 4E-5 | **VAULT999** append-only ledger (`deploy/vault999-writer/main.py:713`); per-decision receipts; hash-chained verification (`scripts/verify_vault_chain.py`) | **Article 12 — Record-keeping** (https://artificialintelligenceact.eu/article/12/) | **DIRECT** | Art. 12(1)-(2) require logging capabilities "enabling the automatic recording of events (*logs*) over the lifetime of the system", supporting risk identification and post-market monitoring. arifOS records decisions with provenance as its primary function. Limitation: what is recorded is the *governance decision*, which is a subset of a system's event log; the adopter still owns the rest of Art. 12. |
| 4E-6 | **F13 SOVEREIGN** + **F3 TRI-WITNESS** + `888_HOLD` + typed HOLD (`FAILURE`/`CONSTITUTIONAL`/`F13_REFUSAL`) | **Article 14 — Human oversight** (https://artificialintelligenceact.eu/article/14/) | **DIRECT** | Art. 14(4)(d) requires the overseer be able to "decide, in any particular situation, not to use the high-risk AI system or to otherwise disregard, override or reverse the output"; 14(4)(e) requires ability to "intervene… or interrupt the system through a 'stop' button". F13 is exactly a non-delegable override, and `refusal_closure` makes refusal a first-class outcome. **See 4E-6a: the stop *surface* is not arifOS's.** |
| 4E-6a | — | **Article 14(4)(e) operator-facing interrupt surface** | **NO DIRECT COUNTERPART** | F13 is a *policy* control: it can refuse, but it does not ship the operator's interrupt UI. The stop button belongs to the caller's application. Do not read 4E-6 as covering the literature's "human in the loop" surface. |
| 4E-7 | F2 epistemic labels; L12 injection patterns | **Article 15 — Accuracy, robustness and cybersecurity** (https://artificialintelligenceact.eu/article/15/) | **PARTIAL** | Art. 15(5) requires resilience against unauthorised third parties altering use/outputs, with measures to "prevent, detect, respond to, resolve and control for attacks… (data poisoning)… (model poisoning), adversarial examples or model evasion". arifOS has no model-layer robustness or accuracy measurement; L12 is an input-pattern tripwire. **This is a real and material partial, not a nominal one.** |
| 4E-8 | — | **Article 17 — Quality management system** | **NO DIRECT COUNTERPART** | arifOS is not a QMS. |
| 4E-9 | Append-only receipt ledger | **Article 19 — Automatically generated logs** (https://artificialintelligenceact.eu/article/19/) | **PARTIAL** | Art. 19(1) requires providers to keep automatically generated logs for a period "of at least six months". arifOS provides the ledger substrate and append-only claim, but this document found **no retention-period control or evidence** in-repo. Until that is measured, the ≥6-month requirement is unsatisfied. |
| 4E-10 | vPer-call gating; deployer-visible verdicts | **Article 26 — Obligations of deployers** (https://artificialintelligenceact.eu/article/26/) | **PARTIAL** | The verdict record supports a deployer's oversight and logging duties. It does not discharge them. |
| 4E-11 | — | **Article 27 — Fundamental rights impact assessment** | **NO DIRECT COUNTERPART** | No FRIA process. F6 MARUAH is a per-action dignity check, which is not a fundamental-rights impact assessment. |
| 4E-12 | — | **Article 43 — Conformity assessment** | **NO DIRECT COUNTERPART** | arifOS performs no conformity assessment and is not a notified body. |
| 4E-13 | — | **Articles 48 / 49 — CE marking and registration** | **NO DIRECT COUNTERPART** | N/A to a policy kernel. Listed so the reader sees the omission was deliberate. |
| 4E-14 | F2 terminal labels `SYN` / `RECYCLED_SYN` (`GENESIS/FLOOR_TABLE.json:204-205`) | **Article 50 — Transparency obligations** (https://artificialintelligenceact.eu/article/50/) | **PARTIAL** | Art. 50 concerns marking and labelling artificially generated or manipulated content. arifOS has a *lineage* label for synthetic claims, which is the right primitive, but it does not mark content in the artefact itself and applies only where the label is supplied. |
| 4E-15 | — | **Article 72 — Post-market monitoring** (https://artificialintelligenceact.eu/article/72/) | **NO DIRECT COUNTERPART** | No post-market monitoring system or plan. Art. 72(3) required a Commission implementing act with a monitoring-plan template by 2 February 2026 — the requirement is live; arifOS does not address it. |

**4E tally:** DIRECT 2 · PARTIAL 6 · NO DIRECT COUNTERPART 8 (including 4E-6a). (Rows: 16.)

---

## 5. Gaps declared (consolidated)

The per-framework `NO DIRECT COUNTERPART` rows are the primary gap list, and they are reproduced here as a single register for the reader who only wants gaps. **36 rows**, matching the `NO DIRECT COUNTERPART` count in §4.

### 5.1 OWASP LLM Top 10 2025 (6)

| Gap | Item |
|---|---|
| G-LLM-1 | LLM02 Sensitive Information Disclosure — no confidentiality or PII floor |
| G-LLM-2 | LLM03 Supply Chain — no model/dataset/dependency provenance control |
| G-LLM-3 | LLM04 Data and Model Poisoning — provenance labels ≠ training-data integrity |
| G-LLM-4 | LLM05 Improper Output Handling — no output-side sanitisation |
| G-LLM-5 | LLM07 System Prompt Leakage — not addressed |
| G-LLM-6 | LLM08 Vector and Embedding Weaknesses — no external memory-store protection |

### 5.2 OWASP Agentic Top 10 2026 (3)

| Gap | Item |
|---|---|
| G-ASI-1 | ASI04 Agentic Supply Chain Vulnerabilities |
| G-ASI-2 | ASI07 Insecure Inter-Agent Communication — no inter-agent message integrity floor |
| G-ASI-3 | ASI08 Cascading Failures — no fleet-level failure containment |

### 5.3 NIST AI RMF 1.0 (11)

| Gap | Subcategory |
|---|---|
| G-RMF-1 | GOVERN 1.5 — no periodic review of the risk-management process |
| G-RMF-2 | GOVERN 1.6 — no AI system inventory |
| G-RMF-3 | GOVERN 1.7 — no decommissioning provision |
| G-RMF-4 | GOVERN 2.2 — no training controls |
| G-RMF-5 | GOVERN 6.1 / 6.2 — no third-party risk or contingency |
| G-RMF-6 | MAP 4.1 / 4.2 — no component/third-party risk mapping |
| G-RMF-7 | MAP 5.2 — no external stakeholder engagement |
| G-RMF-8 | MEASURE 2.3 — no deployment-condition performance validation |
| G-RMF-9 | MEASURE 4.1–4.3 — no assessment of measurement efficacy |
| G-RMF-10 | MANAGE 4.1 — no post-deployment monitoring plan |
| G-RMF-11 | MANAGE 4.3 — no external incident communication |

### 5.4 ISO/IEC 42001:2023 (8) — references unverified against the standard (§8 U-1)

| Gap | Clause / control |
|---|---|
| G-ISO-1 | Clause 4 — context of the organization |
| G-ISO-2 | Clause 6.1 / 6.2 — controls determination, Statement of Applicability, objectives |
| G-ISO-3 | Clause 9.2 — internal audit |
| G-ISO-4 | Clause 9.3 — management review |
| G-ISO-5 | Annex A.4 — resources for AI systems |
| G-ISO-6 | Annex A.6 — AI system life cycle |
| G-ISO-7 | Annex A.7 — data for AI systems |
| G-ISO-8 | Annex A.10 — third-party and customer relationships |

*(The absence of an AIMS — no organization-level policy approval, no competence management, no certification — is structural and is recorded once, at §6 S6 and S7, rather than double-counted here.)*

### 5.5 EU AI Act (8)

| Gap | Article |
|---|---|
| G-EU-1 | Art. 6 + Annex III — high-risk classification |
| G-EU-2 | Art. 11 + Annex IV — technical documentation |
| G-EU-3 | Art. 14(4)(e) — operator-facing interrupt surface |
| G-EU-4 | Art. 17 — quality management system |
| G-EU-5 | Art. 27 — fundamental rights impact assessment |
| G-EU-6 | Art. 43 — conformity assessment |
| G-EU-7 | Art. 48 / 49 — CE marking and registration |
| G-EU-8 | Art. 72 — post-market monitoring |

**Register total: 6 + 3 + 11 + 8 + 8 = 36 rows.** This matches the `NO DIRECT COUNTERPART` count in §4 exactly (see §10).

---

## 6. Structural gaps (S1–S12)

These are not framework rows. They are obligations arifOS does not satisfy at architecture level, and they bind across every framework in this document.

| ID | Structural gap | Evidence |
|---|---|---|
| **S1** | **The primary floor gate fail-opens.** On `ImportError`, Gate 5 reports `passed=True` with reason "soft pass (degraded mode)". A degraded runtime is indistinguishable from a compliant one in the verdict record. Any claim that "F1–F13 are enforced" is conditional on a successful import at runtime, and this document found no alarm that fires when that happens. | `arifosmcp/runtime/governance_pipeline.py:1941-1948`. Contrast the fail-closed sibling at `:1967-1987`. |
| **S2** | No confidentiality, data-protection or disclosure floor. | 4A-2, 4A-7 |
| **S3** | No supply-chain, dependency or third-party control at any layer. | 4A-3, 4B-4, 4C-11, 4C-16, 4D-21 |
| **S4** | No model-layer accuracy or robustness measurement; adversarial-example and model-poisoning resilience is unaddressed. | 4A-4, 4E-7 |
| **S5** | **arifOS holds no security or AI-management certification.** No SOC 2, no ISO/IEC 27001, no ISO/IEC 42001 certificate, no notified-body assessment. Nothing in this document is a certification, and arifOS's own repo already flags this as a procurement barrier for regulated buyers. | `docs/positioning/POSITIONING-2026-09.md:113` — "will demand SOC 2 / independent attestation arifOS lacks"; README badge "Security Audit: In Progress" |
| **S6** | arifOS is not an AI management system. No organization-level AI policy approval, no Statement of Applicability, no internal audit programme, no management review. | §5.4 |
| **S7** | No competence, training or awareness control. | G-RMF-4, G-ISO-9 |
| **S8** | No inventory of the AI systems it governs, and no decommissioning path. | G-RMF-2, G-RMF-3 |
| **S9** | No fundamental-rights or wider-impact assessment process. | G-EU-5 |
| **S10** | No operator-facing interrupt surface. F13 can refuse an action; it does not ship the human's stop control. | 4E-6a |
| **S11** | No external incident, complaint or market-surveillance reporting channel. | G-RMF-11, 4C-24 |
| **S12** | **Jurisdictional reality.** EU AI Act obligations attach to *providers* and *deployers* of AI systems. arifOS is neither: it is a policy kernel invoked by them. It cannot inherit those obligations downward to its users, and it cannot discharge them on their behalf. It can only produce evidence that helps. Any reading of §4E as "using arifOS makes you AI-Act-ready" is wrong. | Art. 3 definitions as rendered at the article pages cited in §4E |

**S1 deserves to be read twice.** In a crosswalk whose purpose is to let a compliance reader rely on the floors, the fail-open path is the highest-severity finding in this document, higher than any `NO DIRECT COUNTERPART` row, because it can silently convert a *mapping* into a *false claim at runtime*.

---

## 7. Internal divergences that block clean mapping

A crosswalk is only as good as the thing being mapped. While reading the floors I found the repo disagreeing with itself. These are recorded, not resolved — resolving them is outside this document's authority and path.

| ID | Divergence | Evidence |
|---|---|---|
| V1 | **F11 / F12 have two incompatible identities.** Canon: F11 AUDITABILITY, F12 RESILIENCE. Runtime: L11 CommandAuth, L12 INJECTION. Static floor pages: F11 "COMMAND AUTHORITY — Human Sovereignty", F12 "INJECTION DEFENSE". | `GENESIS/000_KERNEL_CANON.md:102-103` vs `core/laws.py:207-209` vs `static/arifos/floors/F11_AUTH.md:1` and `F12_INJECTION.md:1` |
| V2 | **Prefix drift.** `core/laws.py` and the README use **L10–L13**; the canon table and `FLOOR_TABLE.json` use **F10–F13** for the same four floors. | `core/laws.py:85-88` vs `GENESIS/000_KERNEL_CANON.md:101-104`; README SOT block: `floors_active: 13 (F1–F9 + L10–L13)` |
| V3 | **F8 GENIUS has two different operator forms.** `(A × P × E × X)^(1/4)` (runtime) vs `A × P × X × E²` (floor page). | `core/laws.py:205` vs `static/arifos/floors/F08_GENIUS.md:15` |
| V4 | **F3 is TRI-WITNESS in canon and QUAD-WITNESS in runtime and its own floor page**, adjudicated by amendment at `000_KERNEL_CANON.md:94` (name "refers to the three in-system channels only"). A reader meeting only `core/laws.py` will think it is four. | `GENESIS/000_KERNEL_CANON.md:94` vs `core/laws.py:206`, `static/arifos/floors/F03_WITNESS.md:1` |
| V5 | **F5 threshold.** Canon `≥ 1.0`; implementation uses an operational pass at 0.7 with the comment "Soft floor: use 0.7 operational pass for semantic F5; keep THRESHOLDS for catalog". | `GENESIS/FLOOR_TABLE.json:106-110` vs `core/laws.py:790-797` |
| V6 | **F4 threshold.** Canon sealed range is `ΔS ≤ 0`; implementation raises the effective free-pass threshold to 0.5 because a 0.0 threshold "always passed". | `GENESIS/FLOOR_TABLE.json:100` vs `core/laws.py:814-816` |
| V7 | **Two parallel verdict vocabularies.** The kernel emits `VOID/HOLD/SABAR/PARTIAL/SEAL`; `docs/VERDICT_SEMANTICS.md` documents a different machine (`PENDING`/`ADVISORY`/`HOLD`/`VOID`/`SEAL_AUTHORIZED`/`VAULT999_SEALED`) and five namespaced seals, with a rule that "No surface may use the bare word 'SEAL'". | `kernel-sot.yaml:63-70` vs `docs/VERDICT_SEMANTICS.md:16-113` |
| V8 | **A prior crosswalk already exists in the repo and contradicts this one.** `docs/F1F13-TO-OWASP-AGENTIC-TOP-10.md` names floors that do not exist in the canon table (F4 SCOPE, F5 DELIBERATION, F6 AUTHORITY-CHAIN, F7 TERMINALITY, F8 TIME, F9 NO-HANTU, F10 MEMORY-LIFECYCLE, F11 WITNESS-RIGHTS, F12 CURIOSITY-BOUND), maps them to "AAI1…AAI10" labels rather than OWASP's published `ASI01…ASI10`, and crosswalks to **NIST CSF 2.0** rather than the AI RMF. It also claims in the sibling positioning doc that arifOS "claims 10/10 OWASP Agentic Top 10 coverage". | `docs/F1F13-TO-OWASP-AGENTIC-TOP-10.md:24-38`; `docs/positioning/POSITIONING-2026-09.md:25` |
| V9 | **Capability-count drift is acknowledged in-tree.** `kernel-sot.yaml` states "8 canonical public verbs. Historical 9/13/19/24 counts are HISTORICAL only", while the SOT block in the README reports 8 public + a 25-verb internal superset, and `docs/floor_coverage_matrix.md` was written against 18 canonical tools. | `kernel-sot.yaml:52-54`; README SOT block; `docs/floor_coverage_matrix.md:17-19` |
| V10 | **The canon designates the *database* as source of truth**, which this document could not read. "law_type and canon_name are sourced from s000.constitutional_floors (DB). This file must stay in sync with DB. DB is the source of truth; canon docs mirror the DB." | `core/laws.py:12-13`. No DB was read from this workspace. |

**V8 is the one that matters commercially.** A hostile reader who reads both documents will conclude that arifOS cannot state its own floors consistently, and the "10/10 OWASP coverage" claim in `POSITIONING-2026-09.md:25` is unsupported by the ASI rider names. This document does not clean up that file — the path is owned elsewhere and out of scope — but the buyer must be shown both, and the divergence must be resolved by the sovereign before either is used in procurement.

---

## 8. Unverified references

Every framework reference I could not verify, with the reason. This list is load-bearing: it is the reason the rest of the document can be trusted.

| # | Unverified | Why |
|---|---|---|
| **U-1** | **ISO/IEC 42001:2023 — all clause and Annex A references in §4D and §5.4** | `iso.org` served Cloudflare bot protection on every attempt (headless browser and plain fetch, multiple retries) and `r.jina.ai` returned `HTTP 403`. Clause 4–10 structure and Annex A objective titles A.2–A.10 came from a third-party summary (konfirmity.com, observed 2026-09-21, whose own text states "You can read the objective titles for yourself in the ISO/IEC 42001:2023 standard on iso.org, which publishes a free preview"). Its numbers have **not** been checked against the standard. Treat §4D as a checklist to validate, not as citation. |
| **U-2** | **OWASP GenAI LLM Top 10 2026 — the enumerated risk list** | The resource page exists and is dated 2026-08-03 (observed). The rider list was not read, so §4A deliberately maps the **2025** edition. There is now a plausible chance that §4A is aimed at the superseded edition. |
| **U-3** | **OWASP Agent Control Standard (ACS) and "GenAI Security Industry Framework Crosswalk"** (both dated 2026-09-01 on the resource index) | Existence observed on the OWASP site index; contents not read. ACS may be directly relevant to a kernel of this kind and should be read before any external use of §4B. |
| **U-4** | **NIST COSAiS — SP 800-53 AI control overlays (single-agent and multi-agent)** | Reported by third-party sources (Cloud Security Alliance research notes) as in development with no publication date. **Not** verified on nist.gov. If these publish, they will likely be a better home for §4C's agentic content than the AI RMF subcategories. |
| **U-5** | **NIST AI 100-2 (adversarial ML taxonomy, 2025 edition)** | Referenced only by third-party sources during this work; not read on nist.gov. |
| **U-6** | **NIST AI RMF revised edition** | `airc.nist.gov` and `nist.gov` both state "The AI RMF 1.0 is being updated. A revised version is in progress." The revision text is not available, so every §4C identifier is a mapping to a revision-in-progress document. |
| **U-7** | **EU AI Act consolidated text in the Official Journal** | All §4E article text was read through the AI Act Explorer, which marks amended provisions inline. Article 113's dates (2 Dec 2027 Annex III / 2 Aug 2028 Annex I) are therefore second-hand relative to the OJ. Validate against EUR-Lex before external citation. |
| **U-8** | **NIST AI RMF Playbook contents** | Existence verified (offered alongside the AI RMF on airc.nist.gov); the Playbook's tactical actions were not read, so no §4C row cites a Playbook action. |
| **U-9** | **OWASP "Agentic AI – Threats and Mitigations" taxonomy (v1.1 referenced in the launch post)** | Reference observed in the OWASP blog; the taxonomy document was not read. |
| **U-10** | **The `AAI1…AAI10` scheme in `docs/F1F13-TO-OWASP-AGENTIC-TOP-10.md`** | Could not be matched to any OWASP-published enumeration during this work. Treated as undocumented (see V8). Not used as a source. |
| **U-11** | **`s000.constitutional_floors` (DB)** — designated source of truth for floor names and law types | `core/laws.py:12-13` names this table as canonical. No database was read from this workspace, so all floor text in §3 comes from the repo mirror, not from the DB. If DB and mirror have diverged, §3 is wrong. |

Additionally, and not a framework reference: **the live runtime was not probed.** No MCP endpoint was called, no verdict was issued, and `lsattr` was not run against VAULT999. This document is a *source* crosswalk, not a runtime attestation.

---

## 9. How a buyer verifies this document

1. Pick any `DIRECT` row in §4.
2. Open the cited `path:line` in the public repo at the HEAD named at the top of this document.
3. Confirm the code path does what the row says.
4. Open the cited framework URL and confirm the framework item says what the row says.
5. Re-run the mapping yourself. If a row fails step 3 or 4, the row is wrong and should be corrected in this file — not argued with.

For the runtime question — *is the floor gate actually live in your deployment?* — run:

```bash
# S1 check: does the floor module import in the deployed runtime?
python -c "from arifosmcp.runtime.law import check_laws; print(check_laws.__doc__[:80])"
# if this raises ImportError, Gate 5 is in soft-pass mode and every mapping above is moot
```

That single command distinguishes a *declared* floor set from an *enforced* one. It is the honest entry point to this document.

---

## 10. Counts and definitions

All figures below were produced by parsing the §4 tables in this file, not by hand. Any reader can reproduce them:

```bash
python3 - <<'PY'
import re, collections
t = open('docs/standards/CROSSWALK-2026-09.md').read()
secs = re.split(r'\n### (4[A-E])\.', t)
tot = collections.Counter(); nrows = 0
for i in range(1, len(secs), 2):
    rows = [l for l in secs[i+1].split('\n') if re.match(r'^\|\s*4[A-E]-', l)]
    nrows += len(rows)
    for r in rows:
        j = ''.join(r.split('|'))
        tot['GAP' if '**NO DIRECT COUNTERPART**' in j else
            'PARTIAL' if '**PARTIAL**' in j else 'DIRECT'] += 1
print(nrows, dict(tot))
PY
```

| Quantity | Definition | Value |
|---|---|---|
| **`mappings`** | §4 rows typed `DIRECT` or `PARTIAL` | **51** |
| — DIRECT rows | §4 | 18 |
| — PARTIAL rows | §4 | 33 |
| **Framework `NO DIRECT COUNTERPART` rows** | §4 = §5 register | **36** |
| **Structural gaps** | §6 (S1–S12) | **12** |
| **`gaps_declared`** | 36 + 12 | **48** |
| Total §4 rows | mappings + framework gaps | 87 |
| Internal divergences | §7 (V1–V10) — recorded, *not* counted as framework gaps | 10 |
| Unverified external references | §8 (U-1…U-11) | 11 |

Per-framework split:

| Framework | Rows | DIRECT | PARTIAL | NO DIRECT COUNTERPART |
|---|---|---|---|---|
| 4A · OWASP LLM Top 10 2025 | 10 | 3 | 1 | 6 |
| 4B · OWASP Agentic Top 10 2026 | 10 | 2 | 5 | 3 |
| 4C · NIST AI RMF 1.0 | 30 | 9 | 10 | 11 |
| 4D · ISO/IEC 42001:2023 | 21 | 2 | 11 | 8 |
| 4E · EU AI Act | 16 | 2 | 6 | 8 |
| **Total** | **87** | **18** | **33** | **36** |

**Reading the ratio honestly.** 51 mappings against 36 framework gaps and 12 structural gaps means **roughly two-fifths of the framework items examined have no counterpart at all**, and only 18 of 87 rows (21%) are `DIRECT`. The mapping count is not the headline; the 18 `DIRECT` rows are, and they cluster where arifOS actually does work: pre-execution tool gating (ASI02, LLM06, clause 8.2/8.3), recording (Art. 12), human override (Art. 14, MANAGE 2.4), and the sovereignty/kill-switch family (F13). Everything else is PARTIAL or absent, and §6 S1 means even the 18 are conditional on the floor module importing at runtime.

---

**DITEMPA BUKAN DIBERI ⚒️**

*Compiled 2026-09-21. Docs-only. No claim in this document was produced by paraphrasing from memory or from a task brief.*
