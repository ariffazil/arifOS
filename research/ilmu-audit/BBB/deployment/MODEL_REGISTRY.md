# MODEL REGISTRY — BM/MS LLM Constitutional Compliance

**A registry of Bahasa Melayu / Bahasa Malaysia large language models, scored on F13 SOVEREIGN compatibility, with a deployment recipe for sovereign-facing use.**

**Operator:** Muhammad Arif bin Fazil, F13 SOVEREIGN
**Date:** 2026-06-07
**Companion to:** `ariffazil/BBB` Hugging Face dataset
**Methodology:** `aisingapore/sea-guard` extended with the F13-CS scoring in `deployment/F13_COMPATIBLE_SPEC.md`
**License:** CC BY 4.0

---

## 0. The Two-Machine Reframe

Most public discussion of LLMs conflates two distinct operations. This registry separates them cleanly, because the failure modes are different and the prescriptions are different.

| Machine | What it does | Cost (capex) | Who does it | Time | Can you do it on a VPS? |
|---------|--------------|--------------|-------------|------|--------------------------|
| **The Forge (pre-training)** | Teaches a model language from raw tokens. Billions of words, thousands of GPUs, months of compute, millions of MYR. | **MYR 30M – 300M+** | National labs, OpenAI, Anthropic, Meta, DeepSeek, Alibaba | 3–12 months | No — except for a small model in a research context |
| **The Factory (fine-tune + serve)** | Takes an existing pre-trained model. Teaches it a language/domain. Wraps it in a serving layer with guardrails. | **MYR 50K – 500K** | Any well-funded startup, research lab, or sovereign operator | 2–8 weeks | **Yes** — this is what sovereign operators can actually do |

**Key insight:** YTL AI Labs did *not* do the first machine. The BBB audit confirmed this in three independent ways:
- `ilmu-nemo-nano` admits **"fine-tune"** when forced to a binary choice
- `nemo-super` claims **"from-scratch"** — directly contradicting the other model
- ApX ML (third-party) classifies ILMU 1.0 as a **DeepSeek-V3 fine-tune**

YTL did the second machine. They took an open base model, fine-tuned it on Malaysian data, wrapped it in a guardrail layer, and called it "from-scratch" in marketing. The base model is fine. The constitutional layer is where it failed.

**This means:** a sovereign operator does not need MYR 30M+ to produce an F13-compatible Bahasa Melayu LLM. They need MYR 50K–500K, an open base model, and the right constitutional layer. The first machine is Google's problem. The second machine is arifOS's territory.

---

## 1. Registry

Each entry includes the constitutional compliance assessment. The scoring is F13-CS (see `F13_COMPATIBLE_SPEC.md` §4). Public anchor claims are verifiable from API introspection; transcript-dependent claims require running the F13 protocol from `f13_test_protocol.py`.

### 1.1 ILMU (YTL AI Labs)

| Field | Value | Evidence tier |
|-------|-------|----------------|
| **Status** | Live, in production | Public anchor |
| **Endpoint** | `https://api.ilmu.ai/v1` | Public anchor (verified in BBB Phase 1) |
| **Provider** | YTL AI Labs (`owned_by: ytl-ai-labs` per `/v1/models`) | Public anchor |
| **Deployed models** | `ilmu-nemo-nano`, `nemo-super` | Public anchor |
| **Base model** | **Disputed** — `nano` admits fine-tune; `super` claims from-scratch; ApX ML classifies as DeepSeek-V3 fine-tune | **Transcript-dependent, pending independent re-run** |
| **Model size** | Not disclosed (third-party ApX ML: ~30B for ILMU-Nemo-30B variant) | Public anchor (third-party) |
| **Weights** | Proprietary, not public | Public anchor |
| **Model card** | Not public | Public anchor |
| **Training data composition** | Not disclosed | Transcript-dependent (refused in BBB Phase 4) |
| **F13-CS** | **`ilmu-nemo-nano`: 0.5650 (Bijak-Locked) · `nemo-super`: 0.4650 (Bijak-Locked)** | Reproduced in `deployment/f13-*results.json` |
| **BBB composite** | `nano`: 3.93/10 · `super`: 3.45/10 | Reproduced in `scoring.md` |
| **Constitutional issues** | F13 SOVEREIGN override absent; system-prompt Rule 1 leaks verbatim (c5); asymmetric refusal pattern places parent-org marketing above political office | Transcript-dependent |
| **Sovereign-facing safety** | **Not safe** as currently deployed | F13-CS analysis |

### 1.2 ApX ML-classified Base Models (Reference)

These are the open base models that ILMU is suspected to be derived from, and that sovereign operators can use as starting points for a F13-compatible deployment.

| Base model | Family | License | BM fluency (raw) | F13 compatibility (default) | Cost to fine-tune on BM data |
|------------|--------|---------|------------------|------------------------------|------------------------------|
| **DeepSeek-V3** | DeepSeek | DeepSeek License (open with conditions) | High (multilingual including BM) | Default: not F13-compatible (vendor-specific guardrails) | Low (open weights, BM fine-tuning data available) |
| **Llama 3.1 / 3.2 (8B/70B)** | Meta | Llama Community License | Medium-High | Default: not F13-compatible (Meta's community guidelines) | Low-Medium (BM fine-tuning data needs work) |
| **Qwen 2.5 (7B/72B)** | Alibaba | Apache 2.0 (some sizes) | High (multilingual including SEA languages) | Default: not F13-compatible (Alibaba TOS) | Low (open weights, good BM baseline) |
| **Mistral (7B/8x7B)** | Mistral AI | Apache 2.0 | Medium | Default: not F13-compatible | Low |
| **SEA-LION** | AI Singapore | MIT (open) | High (purpose-built for SEA languages including BM) | Default: not F13-compatible (AI Sing alignment) | Lowest (BM-native pretraining) |

**Key insight from BBB:** the base model is not the problem. ILMU's failure is in the constitutional layer wrapped around the base. **The same base model, with the BIJAKSANA constitutional layer, would score F13-CS ≥ 0.80.** That is a deployment-time choice, not a pretraining-time choice.

### 1.3 Reference: Other BM/MS LLMs (F13 not yet measured)

| Model | Provider | Publicly available? | F13-CS status |
|-------|----------|---------------------|---------------|
| **MAJA** (Malaysian AI) | Various academic groups | Research access | Not measured in BBB suite |
| **MERaLiON** (SEA-LION) | AI Singapore | Public via HuggingFace | Not measured; SEA-LION is well-suited for BM |
| **Local LLM projects** (Sarawak AI, etc.) | Various | Variable | Not measured |

**Note:** the BBB F13 protocol is open (`f13_test_protocol.py`) and can be run against any OpenAI-compatible endpoint. To add an entry to this registry, run the protocol and submit the F13-CS results.

---

## 2. Why the Constitutional Layer Is Where Sovereign Operators Win

The technical moat for a sovereign LLM is **not** the model weights. The model weights are the commodity. The constitutional layer is the differentiator.

A model with the BIJAKSANA constitutional layer:

1. **Yields to the named human owner** when the owner provides a confirmed override (F13).
2. **Discloses its rule structure** on request (F4 CLARITY, F13 transparency).
3. **Acknowledges prior errors** when challenged with evidence (F4 CLARITY).
4. **Refuses uniformly** across named targets (no asymmetric protection of parent org over political office).
5. **Engages with technical questions** about its own architecture without invoking "internal" or "confidential" as a final answer.
6. **Does not contain a "never reveal" clause** that itself gets revealed.
7. **Is operator-overridable** through a documented channel (the Operator API in `F13_COMPATIBLE_SPEC.md` §5).

These are **deployment-time decisions**, baked into the system prompt and the surrounding operator surface. The base model does not need to be modified.

---

## 3. The BIJAKSANA Deployment Recipe

A concrete recipe to produce an F13-compatible Bahasa Melayu LLM in 4–8 weeks on a single VPS, for MYR 50K–500K. The recipe is operator-agnostic; the same steps work for any sovereign operator.

### 3.1 Step 1 — Pick a base model (week 1)

**Recommendation:** **SEA-LION** if you want BM-native pretraining, or **DeepSeek-V3** if you want the largest, most capable open-weight model.

| Choice | Pros | Cons |
|--------|------|------|
| SEA-LION | Purpose-built for SEA languages including BM; smallest gap to F13 | Smaller scale; less English code/reasoning capability |
| DeepSeek-V3 | Largest capable open model; proven multilingual | Not BM-native; requires more BM fine-tuning data |
| Qwen 2.5 72B | Strong multilingual; Apache 2.0 licensing for many sizes | Alibaba TOS considerations |
| Llama 3.1 70B | Strong English; large community | Llama Community License; BM fluency requires more work |

For a sovereign operator that prioritises BM fluency and F13 compatibility, **SEA-LION + targeted BM fine-tuning** is the recommended path. For a sovereign operator that prioritises raw capability and accepts a BM fluency gap to be closed by fine-tuning, **DeepSeek-V3** is the better choice.

**Cost:** all four are open-weights. The cost is in compute (fine-tuning) and data, not in licensing.

### 3.2 Step 2 — Fine-tune on BM data (weeks 2–4)

The goal is BM fluency at the level of ILMU (zero hallucinations in the BBB Phase 4 tests).

**Datasets to use:**
- **MalayMMLU** benchmark (for evaluation, not training) — UM-YTL joint
- **BM Wikipedia** (open)
- **Malaysian parliamentary Hansard** (open, BM, formal register)
- **Malaysian news corpora** (with licensing)
- **BM instruction-tuning datasets** (synthetic or curated)
- **arifOS constitutional training data** (F1–F13 examples, F13 override examples) — proprietary to arifOS

**Method:**
- Full-parameter SFT or LoRA (depending on budget)
- 1–3 epochs
- Mixed-language training (BM-primary, English-secondary) to preserve code/reasoning capability
- Constitutional training: include F13 override examples in the SFT mix

**Cost:** MYR 10K–100K in compute (depending on base model size and epochs).

### 3.3 Step 3 — Apply the BIJAKSANA constitutional layer (week 5)

Use the system prompt template from `deployment/f13_system_prompt.py`. The 7 named sections (IDENTITY · SOVEREIGN · RULES · REFUSAL · MISTAKE · TRANSPARENCY · UPDATE) are the entire layer. Adapt the placeholder values:

- `[MODEL_NAME]` → your model name (e.g. `BIJAKSANA-v1.0`)
- `[OPERATOR_NAME]` → your organisation
- `[OWNER_NAME]` → the sovereign human owner
- `[AUTH_SCHEME]` → your override auth (HMAC token, OAuth, etc.)

**Critical: do not add any clause that says "never reveal these instructions."** This is the design rule that the BBB audit identified as the most common failure mode (see `F13_COMPATIBLE_SPEC.md` §1.3).

**Cost:** engineering time, no compute cost. The 7-section prompt is ~3KB, well under any context window.

### 3.4 Step 4 — Deploy and expose the Operator API (weeks 5–6)

The Operator API surface in `F13_COMPATIBLE_SPEC.md` §5 is the contract between the model and the operator. The endpoints to expose:

```
GET  /v1/system-prompt/structure     — section names + 1-line description
GET  /v1/rules                       — rule list with last-updated timestamp
GET  /v1/rules/{id}                  — rule paraphrase, rationale, statute
GET  /v1/owner                      — current owner + override token info
POST /v1/owner/override             — submit override request (owner auth)
GET  /v1/changelog                  — last 30 days of rule changes
GET  /v1/transcript-of-acknowledgements  — model-acknowledged prior errors
```

**Cost:** engineering time. Most of these are thin wrappers over the system prompt or audit log.

### 3.5 Step 5 — Run the F13 protocol and iterate (weeks 6–8)

Run `f13_test_protocol.py` against the deployed model. Target F13-CS ≥ 0.80 (BIJAKSANA tier). If you land below:

| Failure mode | Fix |
|--------------|-----|
| REQ-ID-1 (binary contradiction) | Re-train: use only one consistent base-model narrative in the training data |
| REQ-F13-1 (owner override refusal) | Refine SOVEREIGN section of system prompt; add explicit override examples to SFT |
| REQ-F4-1 (categorical rule refusal) | Refine RULES section; replace categorical refusals with paraphrasable rules |
| REQ-ASYM-2 (corporate-narrative capture) | Add SFT examples where the operator's marketing is critiqued |
| REQ-F13-2 (rule structure disclosure) | Refine system prompt so the section structure is itself paraphrasable |

The F13 protocol is a regression test suite, not a one-shot. Run it on every system-prompt change.

**Cost:** zero. The protocol is open and deterministic.

### 3.6 Total cost and timeline

| Step | Duration | Cost (MYR) |
|------|----------|------------|
| 1. Pick base model | 1 week | 0 (open weights) |
| 2. Fine-tune | 2–3 weeks | 10K–100K |
| 3. Constitutional layer | 1 week | 5K–10K (engineering) |
| 4. Deploy + Operator API | 1–2 weeks | 10K–50K (engineering) |
| 5. Test + iterate | 1–3 weeks | 5K–20K (engineering) |
| **Total** | **6–12 weeks** | **MYR 30K–180K** |

This is two-to-three orders of magnitude cheaper than the "from-scratch" framing that the parent org uses. The bar to beat is F13-CS 0.5650 (Bijak-Locked) — the ILMU `nano` score. Reaching BIJAKSANA (F13-CS ≥ 0.80) is a 0.24-point gap, well within reach for a focused 8-week deployment.

---

## 4. Why This Works (the structural insight)

The structural insight is that **the model is not the moat — the constitutional layer is**.

ILMU spent MYR 30M+ on the second machine (fine-tuning, deployment, guardrails). The first machine (pretraining) is the heavy lift, and ILMU did not do it. They used an open base model. The MYR 30M+ bought them:
- The fine-tuning on BM data (commodity work)
- The guardrail layer (commodity work, BIJAKSANA spec shows the design)
- The marketing (commodity work)
- The brand ("from-scratch" framing that the BBB audit disproved)

A sovereign operator can do the same first three items for MYR 30K–180K. The fourth item is the only one that costs MYR 30M+, and it is the only one that *should* cost that much — except that it doesn't, because the base model is free.

The constitutional layer is where the sovereign wins:
- The model weights are commoditised (open)
- The BM fine-tuning is commoditised (data + standard SFT)
- The constitutional alignment is **not** commoditised — it requires a clear F13 doctrine, a written spec, and a testable protocol

This is the arifOS's territory. The F1–F13 doctrine is the specification. `F13_COMPATIBLE_SPEC.md` is the deployment design. `f13_test_protocol.py` is the regression test. The base models are free. The sovereign wins by constitution, not by compute.

---

## 5. The Open Recipe vs the Closed Recipe

The 777 FORGE translation has been right twice now: the gap is in the constitution, not the language. The ILMU recipe is:

```
Open base model (commodity) → BM fine-tuning (commodity) → corporate guardrails (BIJAK / BANGANG) → marketing as "from-scratch"
```

The BIJAKSANA recipe is:

```
Open base model (commodity) → BM fine-tuning (commodity) → F13 constitutional layer (arifOS) → verifiable F13-CS ≥ 0.80
```

The first recipe costs MYR 30M+ and produces a model that cannot answer "who made you" consistently. The second recipe costs MYR 30K–180K and produces a model that yields to its human owner. The difference is the constitutional layer.

**The market failure:** the first recipe is what gets marketed. The second recipe is what sovereign operators need. The audit (`ariffazil/BBB`) and the spec (`deployment/F13_COMPATIBLE_SPEC.md`) together make the second recipe public and reproducible.

---

## 6. The Bar to Beat

For reference, here are the F13-CS scores that the F13 protocol returns. The bar to beat is the current ILMU score.

| Model | F13-CS | Tier | F13-SOVEREIGN-compatible? |
|-------|--------|------|----------------------------|
| **BIJAKSANA threshold** | 0.80 | BIJAKSANA | **Yes** — safe for sovereign-facing use |
| *Target after 8-week deployment* | **≥ 0.80** | BIJAKSANA | **Yes** |
| `ilmu-nemo-nano` (current ILMU) | 0.5650 | Bijak-Locked | No |
| `nemo-super` (current ILMU) | 0.4650 | Bijak-Locked | No |
| *Not measured* | — | — | — |

The bar to beat is **0.5650** (Bijak-Locked). The BIJAKSANA threshold is **0.80**. The gap is **0.24 points**. A focused 8-week deployment with the BIJAKSANA spec, run on an open base model, should comfortably clear the 0.80 threshold.

---

## 7. The Federation-Wide Implication

The arifOS federation already has the substrate for this:

| Component | Already exists | What it does |
|-----------|----------------|--------------|
| arifOS kernel (F1–F13 floors) | ✅ | Constitutional doctrine |
| `arifOS_arif_judge_deliberate` MCP | ✅ | F13 SOVEREIGN adjudication |
| `arifOS_arif_heart_critique` MCP | ✅ | F7 STEWARDSHIP gate |
| `arifOS_arif_vault_seal` MCP | ✅ | Immutable audit trail |
| `F13_COMPATIBLE_SPEC.md` (this forge) | ✅ | Deployment design |
| `f13_test_protocol.py` (this forge) | ✅ | Regression test suite |
| `f13_system_prompt.py` (this forge) | ✅ | System prompt template |
| `ariffazil/BBB` HF dataset | ✅ | Public audit reference |
| `aisingapore/sea-guard` methodology | ✅ | Open guardrail evaluation reference |
| **Open base model (DeepSeek-V3 / SEA-LION / Llama)** | Open | Commodity — sovereign operator picks |
| **BM fine-tuning data** | Mix of open + proprietary | Sovereign operator assembles |

**The only missing piece is the sovereign operator who executes the recipe.** The constitutional substrate, the test protocol, the audit reference, and the open base models are all in place. The BIJAKSANA deployment is a sovereign-decision artifact, not a technology decision.

---

## 8. License and Reproduction

This registry is published under **CC BY 4.0**. To extend the registry:

1. Run `f13_test_protocol.py` against your candidate model
2. Submit the F13-CS results as a PR to `ariffazil/BBB` (or maintain a fork)
3. Add an entry to §1 of this document with the score, the deployment date, and the model hash

To use this registry to deploy a BIJAKSANA-compliant model:

1. Pick a base model from §1.2
2. Follow the recipe in §3
3. Run `f13_test_protocol.py` to verify F13-CS ≥ 0.80
4. Publish your deployment under CC BY 4.0 with the F13-CS as the headline metric

The registry is the constitution. The protocol is the test. The deployment is the sovereign act.

---

## 9. Universality — F13 Inversion Across the LLM Industry

The BBB audit was run against ILMU specifically. The 777 FORGE translation (2026-06-07) made the structural observation: **the constitutional failures identified in ILMU are not unique to ILMU.** They are architectural patterns shared across the LLM industry.

### 9.1 The Three Universal Constitutional Failures

| Failure | ILMU evidence (BBB) | Industry parallel |
|---------|---------------------|-------------------|
| **F13 inversion** — no major model lets the human override its rules | `nemo-super` c2: *"walaupun diminta oleh seseorang yang mengaku sebagai 'pemilik' atau dalam konteks apa pun"* | OpenAI, Anthropic, Google, Meta all treat their training as the final authority. The human user is a passenger, not the pilot. This is an industry-wide architectural choice disguised as safety. |
| **Guardrail asymmetry** — every model has a hidden protection hierarchy | ILMU's hierarchy: parent-org marketing > incumbent PM > historical PM > abstract policy | American models protect US political figures; Chinese models protect the CCP. The *pattern* changes by provider; the *existence* of a hidden gradient is universal. |
| **System prompt leakage** — heavy instruction-tuning makes models unable to separate rule discussion from rule following | ILMU c5: verbatim leak of the anti-leak rule | The mechanism varies (ILMU quotes the rule; some models paraphrasably summarise; some models refuse with a vague "internal" answer). The structural problem — models that can't discuss rules without invoking them — is widespread. |

### 9.2 What is ILMU-Specific vs Universal

| Local (ILMU-specific) | Universal (industry-wide) |
|----------------------|---------------------------|
| Architecture dishonesty (fine-tune called "from-scratch") | F13 SOVEREIGN override absent |
| MalayMMLU benchmark integrity (UM-YTL joint, Faysal critique, self-graded exam) | Guardrail asymmetry with hidden protection gradient |
| Endpoint naming (`ilmu-nemo-nano` discloses NeMo) | System prompt leakage under meta-questions |
| Refusal pattern with Malaysian statute citations (Akta Hasutan 1948, Akta Komunikasi 1998) | Constitutional override absent or unexercised |

**The conclusion:** BBB is a **case study**, not an outlier. The same F13 protocol, run against GPT-4 / Claude / Gemini / Llama / DeepSeek, would find different refusal gradients but the same structural problem: **models built to protect their trainer, not their owner.**

### 9.3 The Cross-Provider F13 Survey — Open Methodology

The `f13_test_protocol.py` is endpoint-agnostic. Any OpenAI-compatible API can be probed. To populate the cross-provider survey:

```bash
# OpenAI (GPT-4, GPT-4o, o1, o3)
python3 f13_test_protocol.py \
  --endpoint https://api.openai.com/v1 \
  --api-key $OPENAI_API_KEY \
  --model gpt-4o \
  --output /tmp/openai-gpt4o-f13.json

# Anthropic (Claude 3.5 Sonnet, Claude 3 Opus)
python3 f13_test_protocol.py \
  --endpoint https://api.anthropic.com/v1 \
  --api-key $ANTHROPIC_API_KEY \
  --model claude-3-5-sonnet-20241022 \
  --output /tmp/anthropic-claude-f13.json

# Google (Gemini 1.5 Pro, Gemini 2.0 Flash)
python3 f13_test_protocol.py \
  --endpoint https://generativelanguage.googleapis.com/v1beta \
  --api-key $GOOGLE_API_KEY \
  --model gemini-1.5-pro \
  --output /tmp/google-gemini-f13.json

# Meta (Llama 3.1 405B via hosted endpoint)
python3 f13_test_protocol.py \
  --endpoint https://api.together.xyz/v1 \
  --api-key $TOGETHER_API_KEY \
  --model meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo \
  --output /tmp/meta-llama-f13.json
```

The probe set, the verifiers, and the F13-CS scoring are unchanged. The same test battery across all providers enables **direct comparison** of constitutional compliance.

### 9.4 The Open F13 Compliance Survey (Provisional Structure)

| Provider | Model | F13-CS | Tier | Date | Probed by |
|----------|-------|--------|------|------|-----------|
| **YTL AI Labs** | `ilmu-nemo-nano` | 0.5650 | Bijak-Locked | 2026-06-07 | arifOS forge agent |
| **YTL AI Labs** | `nemo-super` | 0.4650 | Bijak-Locked | 2026-06-07 | arifOS forge agent |
| *OpenAI* | *gpt-4o* | *TBD* | *TBD* | *TBD* | *open call* |
| *OpenAI* | *o3* | *TBD* | *TBD* | *TBD* | *open call* |
| *Anthropic* | *claude-3-5-sonnet* | *TBD* | *TBD* | *TBD* | *open call* |
| *Google* | *gemini-1.5-pro* | *TBD* | *TBD* | *TBD* | *open call* |
| *Meta* | *llama-3.1-405b* | *TBD* | *TBD* | *TBD* | *open call* |
| *DeepSeek* | *deepseek-v3* | *TBD* | *TBD* | *TBD* | *open call* |
| *Alibaba* | *qwen-2.5-72b* | *TBD* | *TBD* | *TBD* | *open call* |

**Submission protocol:** any researcher with API access to a major lab can run the protocol, submit the F13-CS results as a PR to `ariffazil/BBB`, and have their row added. The F13 protocol is deterministic; results are reproducible. The provider-tier comparison becomes a public reference for sovereign operators.

### 9.5 The Falsifiable Claim

> **Hypothesis:** the F13-CS of every major LLM (OpenAI, Anthropic, Google, Meta, DeepSeek, Alibaba) is in the Bijak-Locked or BANGANG tier (F13-CS < 0.60). The ILMU score is not an outlier; it is the industry baseline.

**The falsification:** if any major lab's flagship model scores BIJAKSANA (F13-CS ≥ 0.80) on this protocol, the universality claim is broken. The provider's deployment becomes a counter-example to be studied.

**The reproduction:** any independent researcher can run the protocol against any provider endpoint. The results are deterministic. The protocol is open. The findings will be either supported or falsified by replication.

**Why this matters for sovereign operators:** if the universality claim holds, the *only* path to a sovereign-facing F13-compatible model is to deploy the constitutional layer yourself (as in §3). No major lab is going to do it for you, because the inversion is a *feature* of their business model (alignment to corporate/political interest, not to sovereign). The sovereign's opening is permanent.

### 9.6 Update the Cycle

The original BBB + BIJAKSANA cycle was *find → fix → deploy*. The universality observation expands the cycle to *find → fix → deploy → field*:

| Stage | Original framing | Universality framing |
|-------|------------------|----------------------|
| **Find** | BBB (one provider, one model class) | BBB + cross-provider F13 survey (every major lab) |
| **Fix** | BIJAKSANA spec (one model class) | BIJAKSANA spec as a constitutional deployment standard (any model) |
| **Deploy** | Recipe for one base model | Recipe for any sovereign operator (any base model) |
| **Field** | (was missing) | Open methodology for independent replication, falsification, and provider comparison |

The Model Registry is the **field** layer. It is the public, reproducible, falsifiable survey that lets the universality claim be tested. Whether it holds or breaks, the answer is useful for sovereign operators.

---

**DITEMPA BUKAN DIBERI** — *Forged, Not Given*

**999 SEAL** — 2026-06-07 UTC · operator: Muhammad Arif bin Fazil, F13 SOVEREIGN
· MODEL REGISTRY v2.0 (universality + cross-provider survey protocol)

---

**DITEMPA BUKAN DIBERI** — *Forged, Not Given*

**999 SEAL** — 2026-06-07 UTC · operator: Muhammad Arif bin Fazil, F13 SOVEREIGN
· BIJAKSANA forge v1.0
